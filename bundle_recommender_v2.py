"""
bundle_recommender_v2.py — Multi-bundle recommendation engine (v2).

Public API
----------
recommend_bundles_v2(inp: BundleInputV2) -> BundleOutput
    Returns primary_bundles (top 3) and secondary_bundles (next 2),
    each enriched with score, confidence, reasons, missing_inputs, and paired_with.

Design
------
1. For each canonical family, compute a z-score using FAMILY_SCORING_PARAMS.
2. Apply hard gates per eligible product within the family.
3. Select the best eligible product variant in each family.
4. Apply PAIR_RULES to boost correlated families.
5. Re-rank after pair boosting.
6. Emit top 3 as primary, next 2 as secondary.

This module does NOT modify the existing standalone product recommender
(risk_engine.recommend_products).  It is invoked independently.
"""

from __future__ import annotations

import logging
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from bundle_scoring_utils import (
    BundleInputV2,
    BundleMeta,
    Config,
    check_hard_gates,
    compute_bundle_score,
    compute_confidence,
    compute_z_score,
    extract_exposure_features,
    load_config,
)

log = logging.getLogger(__name__)
from product_catalogue_v2 import (
    FAMILY_SCORING_PARAMS,
    PAIR_RULES,
    PRODUCTS,
    PRODUCT_CATALOGUE_V2,
    TREND_PRIORS,
)


# ---------------------------------------------------------------------------
# OUTPUT DATA STRUCTURES
# ---------------------------------------------------------------------------

@dataclass
class BundleRecommendation:
    product_name: str
    canonical_family: str
    product_key: str
    score: float
    confidence: str
    reasons: List[str] = field(default_factory=list)
    missing_inputs: List[str] = field(default_factory=list)
    paired_with: List[str] = field(default_factory=list)
    hard_gate_blocks: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "product_name": self.product_name,
            "canonical_family": self.canonical_family,
            "product_key": self.product_key,
            "score": self.score,
            "confidence": self.confidence,
            "reasons": self.reasons,
            "missing_inputs": self.missing_inputs,
            "paired_with": self.paired_with,
        }


@dataclass
class BundleOutput:
    primary_bundles: List[BundleRecommendation] = field(default_factory=list)
    secondary_bundles: List[BundleRecommendation] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary_bundles": [b.to_dict() for b in self.primary_bundles],
            "secondary_bundles": [b.to_dict() for b in self.secondary_bundles],
        }


@dataclass
class Recommendation:
    bundle: str
    final: float
    premium_inr: int
    risk_mult: float
    revenue_score: float
    rationale: Dict[str, str]
    regulatory_triggers_fired: List[Dict[str, Any]] = field(default_factory=list)
    graduation_next: Any = None
    compliance_flags: List[Dict[str, Any]] = field(default_factory=list)
    components: List[str] = field(default_factory=list)
    config_version: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bundle": self.bundle,
            "final": self.final,
            "premium_inr": self.premium_inr,
            "risk_mult": self.risk_mult,
            "revenue_score": self.revenue_score,
            "rationale": self.rationale,
            "regulatory_triggers_fired": self.regulatory_triggers_fired,
            "graduation_next": self.graduation_next,
            "compliance_flags": self.compliance_flags,
            "components": self.components,
            "config_version": self.config_version,
        }


_PROFILE_RISK_KEY = {
    "Cyber Technical Risk": "cyber_technical",
    "Data Privacy Risk": "data_privacy",
    "Liability Risk": "liability",
    "IP Infringement Risk": "ip_infringement",
    "Key Person Risk": "key_person",
    "Governance & Fraud Risk": "governance_fraud",
    "Property Risk": "property",
    "Regulatory Compliance Risk": "regulatory_compliance",
    "ESG & Climate Risk": "esg_climate",
    "Geopolitical Risk": "geopolitical",
    "Gig & Labour Risk": "gig_labour",
    "Policy Velocity Risk": "policy_velocity",
    "Reputation Risk": "reputation",
}

_SECTOR_KEY = {
    "Fintech": "fintech",
    "Healthtech": "healthtech",
    "Edtech": "edtech",
    "Deeptech / AI / Robotics": "deeptech",
    "Cleantech / Climatetech": "climatetech",
    "D2C / Consumer Brands": "d2c",
    "Foodtech / Cloud Kitchen": "d2c",
    "Logistics / Mobility": "d2c",
    "SaaS / Enterprise Software": "saas_b2b",
    "Legaltech": "saas_b2b",
    "HRtech": "saas_b2b",
    "Gaming / Media / Content": "saas_b2b",
    "Agritech": "trading",
}

_STAGE_KEY = {
    "Pre-seed": "seed",
    "Seed": "seed",
    "Series A": "series_a",
    "Series B+": "series_b",
    "Growth": "growth",
}


def _profile_stage(profile: Dict[str, Any]) -> str:
    return _STAGE_KEY.get(profile.get("stage") or profile.get("funding_stage"), profile.get("stage", "seed"))


def _profile_sector(profile: Dict[str, Any]) -> str:
    return _SECTOR_KEY.get(profile.get("sector", ""), profile.get("sector", ""))


def _asset_band(profile: Dict[str, Any]) -> str:
    assets = set(profile.get("physical_assets") or [])
    split = float(profile.get("hardware_software_split") or 0.0)
    if split > 0.6 or "Manufacturing plant / factory" in assets:
        return "fab_or_plant"
    if split > 0.3 or "Lab / R&D equipment" in assets or "Drones / UAV equipment" in assets:
        return "lab_equipment"
    if "Warehouse / fulfilment centre" in assets or "Retail stores / kiosks" in assets:
        return "warehouse"
    return "asset_light"


def _risk_scores(profile: Dict[str, Any], cfg: Config) -> Dict[str, float]:
    raw_scores = profile.get("scores") or {}
    out = {key: 0.0 for key in cfg.risk_weights.as_dict()}
    for key, value in raw_scores.items():
        out[_PROFILE_RISK_KEY.get(key, key)] = float(value)
    return out


def composite_multiplier(profile: Dict[str, Any], cfg: Config) -> Dict[str, float]:
    mults = {key: 1.0 for key in cfg.risk_weights.as_dict()}
    sector = _profile_sector(profile)
    stage = _profile_stage(profile)
    asset = _asset_band(profile)
    for source_name, source, selected in (
        ("sector", cfg.sector_multipliers.values, sector),
        ("stage", cfg.stage_multipliers.values, stage),
        ("asset", cfg.asset_multipliers.values, asset),
    ):
        for risk_key, mult in source.get(selected, {}).items():
            mults[risk_key] = mults.get(risk_key, 1.0) * float(mult)
            log.debug(
                "multiplier applied config=%s source=%s selected=%s risk=%s mult=%.3f",
                cfg.config_version, source_name, selected, risk_key, float(mult),
            )
    return mults


def eligible(bm: BundleMeta, profile: Dict[str, Any]) -> bool:
    sector = _profile_sector(profile)
    stage = _profile_stage(profile)
    asset = _asset_band(profile)
    if "any" not in bm.eligible_sectors and sector not in bm.eligible_sectors:
        return False
    if stage not in bm.eligible_stages:
        return False
    if "any" not in bm.asset_band and asset not in bm.asset_band:
        return False
    if bm.si_cap_inr is not None and float(profile.get("asset_value_inr") or 0.0) > bm.si_cap_inr:
        return False
    return True


def _trigger_matches(trigger: Dict[str, Any], profile: Dict[str, Any]) -> bool:
    signal = trigger.get("signal")
    regulatory = set(profile.get("regulatory") or [])
    data = set(profile.get("data_handled") or [])
    if signal == "drone_ops":
        return bool(profile.get("drone_ops") or profile.get("drone_operations") or "DGCA / drone operations" in regulatory)
    if signal == "handles_pii":
        return bool(
            profile.get("sdf_probability", 0) > 0
            or profile.get("data_sensitivity") in ("Medium", "High")
            or "Sensitive personal data (DPDP Act)" in data
            or "Personal identity data (KYC / Aadhaar)" in data
        )
    if signal == "aggregator_schedule_7":
        return bool(profile.get("gig_headcount_pct", 0) > 0.2 or "Labour Codes / gig worker regulations" in regulatory)
    if signal == "top_1000_listed":
        return bool(profile.get("listed_customer_brsr_dependency"))
    if signal == "rbi_licensed":
        return bool(profile.get("rbi_registration") or "RBI / SEBI / IRDAI licensed" in regulatory)
    if signal == "d2c_ecommerce":
        return profile.get("sector") == "D2C / Consumer Brands"
    return False


def fired_triggers(profile: Dict[str, Any], cfg: Config) -> List[Dict[str, Any]]:
    fired = []
    for trigger in cfg.regulatory_triggers:
        item = {
            "signal": trigger.signal,
            "regulation": trigger.regulation,
            "product": trigger.product,
            "mandatory": trigger.mandatory,
            "citation_url": trigger.citation_url,
        }
        if _trigger_matches(item, profile):
            fired.append(item)
    return fired


def compliance_flags(bm: BundleMeta, profile: Dict[str, Any], cfg: Config) -> List[Dict[str, Any]]:
    flags = []
    components = set(bm.components)
    for trigger in fired_triggers(profile, cfg):
        if trigger["mandatory"] and trigger["product"] not in components:
            flags.append({
                "bundle": bm.name,
                "signal": trigger["signal"],
                "regulation": trigger["regulation"],
                "required_product": trigger["product"],
                "message": f"{bm.name} lacks mandatory {trigger['product']} for {trigger['signal']}",
            })
    if bm.si_cap_inr is not None and float(profile.get("asset_value_inr") or 0.0) > bm.si_cap_inr:
        flags.append({
            "bundle": bm.name,
            "signal": "si_cap",
            "regulation": "Bharat Sookshma SI cap",
            "required_product": "BHARAT_SOOKSHMA",
            "message": f"{bm.name} rejected because SI exceeds INR {bm.si_cap_inr:,.0f}",
        })
    return flags


def violates_compliance(bm: BundleMeta, profile: Dict[str, Any], cfg: Config) -> bool:
    return bool(compliance_flags(bm, profile, cfg))


def coverage_score(profile: Dict[str, Any], bm: BundleMeta, cfg: Config) -> float:
    scores = _risk_scores(profile, cfg)
    weights = cfg.risk_weights.as_dict()
    covered = bm.covered_risks or tuple(weights)
    return sum((scores.get(risk, 0.0) / 100.0) * weights.get(risk, 0.0) for risk in covered)


def premium_potential(bm: BundleMeta, profile: Dict[str, Any], mults: Dict[str, float], products=PRODUCTS) -> float:
    stage = _profile_stage(profile)
    product_premium = 0.0
    for component in bm.components:
        product = next((p for p in products.values() if p.uin == component), None)
        if not product:
            continue
        band = product.premium_seriesb_inr_range if stage in ("series_b", "growth") else product.premium_seed_inr_range
        product_premium += sum(band) / 2.0
    blended = sum(mults.values()) / max(1, len(mults))
    return max(bm.base_premium, product_premium) * blended


def revenue_score(bm: BundleMeta) -> float:
    trajectory = {"up": 1.0, "flat": 0.55, "down": 0.2}.get(bm.trajectory, 0.55)
    tam_component = min(bm.tam_cr / 16250.0, 1.0)
    unit_component = min(bm.adoption * bm.margin * 40.0, 1.0)
    return round(100.0 * (0.4 * tam_component + 0.3 * unit_component + 0.3 * trajectory), 2)


def explain(bm: BundleMeta, cov: float, rev: float, rm: float, mults: Dict[str, float], profile: Dict[str, Any]) -> Dict[str, str]:
    top_risks = sorted(_risk_scores(profile, load_config()).items(), key=lambda item: item[1], reverse=True)
    covered_top = sum(1 for risk, _score in top_risks[:11] if risk in set(bm.covered_risks))
    addressable = bm.tam_cr * bm.adoption * bm.margin
    avg_mult = sum(mults.values()) / max(1, len(mults))
    return {
        "coverage": f"This bundle covers {covered_top} of your top 11 risks; weighted coverage = {cov:.2f}.",
        "revenue": f"Bundle TAM INR {bm.tam_cr:,.0f} cr x adoption {bm.adoption:.0%} x margin {bm.margin:.0%} = INR {addressable:,.0f} cr addressable.",
        "risk_multiplier": f"{rm:.2f}x bundle risk multiplier with blended profile multiplier {avg_mult:.2f}x under config {load_config().config_version}.",
    }


def risk_multiplier_breakdown(profile: Dict[str, Any], cfg: Optional[Config] = None) -> Dict[str, float]:
    cfg = cfg or load_config()
    scores = _risk_scores(profile, cfg)
    bundle_values = list(cfg.bundle_meta.values())
    avg_adoption = sum(bm.adoption for bm in bundle_values) / max(1, len(bundle_values))
    return {
        "claims_frequency": round((scores.get("property", 0.0) + scores.get("liability", 0.0)) / 200.0, 4),
        "settlement": round((scores.get("governance_fraud", 0.0) + scores.get("regulatory_compliance", 0.0)) / 200.0, 4),
        "regulatory_volatility": round((scores.get("policy_velocity", 0.0) + scores.get("regulatory_compliance", 0.0)) / 200.0, 4),
        "market_saturation": round(1.0 - avg_adoption, 4),
    }


def rank(profile: Dict[str, Any], cfg: Optional[Config] = None) -> List[Recommendation]:
    cfg = cfg or load_config()
    mults = composite_multiplier(profile, cfg)
    results: List[Recommendation] = []
    stage = _profile_stage(profile)

    for bm in cfg.bundle_meta.values():
        if not eligible(bm, profile):
            continue
        if violates_compliance(bm, profile, cfg):
            continue
        cov = coverage_score(profile, bm, cfg)
        weights = cfg.risk_weights.as_dict()
        covered = bm.covered_risks or tuple(weights)
        max_cov = sum(weights.get(r, 0.0) for r in covered)
        cov_norm = (cov / max_cov) if max_cov > 0 else cov
        prem = premium_potential(bm, profile, mults, PRODUCTS)
        rev = revenue_score(bm)
        rm = bm.risk_mult
        final = (0.50 * cov_norm + 0.30 * (rev / 100.0) + 0.20 * bm.adoption) * rm
        results.append(Recommendation(
            bundle=bm.name,
            final=round(final, 3),
            premium_inr=round(prem),
            risk_mult=rm,
            revenue_score=rev,
            rationale=explain(bm, cov, rev, rm, mults, profile),
            regulatory_triggers_fired=fired_triggers(profile, cfg),
            graduation_next=cfg.graduation_map.get(stage),
            compliance_flags=compliance_flags(bm, profile, cfg),
            components=list(bm.components),
            config_version=cfg.config_version,
        ))

    return sorted(results, key=lambda rec: -rec.final)[:3]


# ---------------------------------------------------------------------------
# VARIANT SELECTION WITHIN A FAMILY
# ---------------------------------------------------------------------------

def _select_best_variant(
    family: str,
    inp: BundleInputV2,
    exposure_feats: Dict[str, float],
    family_params: Dict[str, Any],
) -> Tuple[Optional[str], Optional[Dict[str, Any]], float, List[str]]:
    """
    Within a family, pick the single most appropriate product variant by:
      1. Filtering on hard gates (ineligible products are discarded).
      2. Computing a variant-adjusted z-score (family params + product overrides).
      3. Applying selectivity:
           - Prefer the most specific eligible product.
           - Break ties by: eligibility fit > sector match > broader package.

    Returns (product_key, product_meta, z_score, gate_block_messages).
    """
    family_products = [
        (k, v) for k, v in PRODUCT_CATALOGUE_V2.items()
        if v["canonical_family"] == family and v.get("active_status", True)
    ]

    candidates: List[Tuple[str, Dict, float, List[str]]] = []
    all_block_messages: List[str] = []

    for pk, pm in family_products:
        eligible, block_reason = check_hard_gates(pm.get("hard_gates", {}), inp)
        if not eligible:
            all_block_messages.append(f"{pm['product_name']}: {block_reason}")
            continue

        # Build merged params: family base + product-level overrides
        merged = deepcopy(family_params)

        # Merge product-level exposure_weights on top of family
        prod_ew = pm.get("exposure_weights", {})
        for feat_key, weight in prod_ew.items():
            merged["exposure_weights"][feat_key] = (
                merged["exposure_weights"].get(feat_key, 0.0) + weight
            )

        # Merge product-level penalties
        prod_penalties = pm.get("penalties", {})
        for feat_key, weight in prod_penalties.items():
            merged["penalty_weights"][feat_key] = (
                merged.get("penalty_weights", {}).get(feat_key, 0.0) + weight
            )

        # Sector match bonus
        sector_bonus = 0.2 if inp.industry in pm.get("sector_tags", []) else 0.0
        z = compute_z_score(merged, inp.risk_scores, exposure_feats)
        z += float(pm.get("trend_priors", 0.0)) + sector_bonus

        # Asset-tier specificity bonus: IRDAI-designed tier products (Bharat Udyam,
        # IAR, etc.) carry binding asset-range gates. When a product is eligible
        # because it fits the range exactly, prefer it over generic alternatives.
        asset_range_gates = {
            k for k in pm.get("hard_gates", {})
            if k in ("max_total_insurable_value", "min_total_insurable_value")
        }
        if asset_range_gates:
            z += 2.0  # strong preference for range-specific products

        candidates.append((pk, pm, z, []))

    if not candidates:
        return None, None, -99.0, all_block_messages

    # Sort by z descending; among ties prefer more specific (fewer sector_tags = more niche)
    candidates.sort(key=lambda c: (c[2], -len(c[1].get("sector_tags", []))), reverse=True)
    best_pk, best_pm, best_z, _ = candidates[0]
    return best_pk, best_pm, best_z, all_block_messages


# ---------------------------------------------------------------------------
# FAMILY-LEVEL SCORING
# ---------------------------------------------------------------------------

def _score_all_families(
    inp: BundleInputV2,
    exposure_feats: Dict[str, float],
) -> Dict[str, Dict[str, Any]]:
    """
    Score every canonical family and return a dict keyed by family name.
    Each value contains: product_key, product_meta, z, score, confidence, gate_blocks.
    """
    results: Dict[str, Dict[str, Any]] = {}

    for family, fparams in FAMILY_SCORING_PARAMS.items():
        # Add global trend prior for this family to the params' own trend_prior
        combined_params = deepcopy(fparams)
        combined_params["trend_prior"] = (
            fparams.get("trend_prior", 0.0) + TREND_PRIORS.get(family, 0.0)
        )

        pk, pm, z, gate_blocks = _select_best_variant(
            family, inp, exposure_feats, combined_params
        )

        if pk is None:
            results[family] = {
                "product_key": None,
                "product_meta": None,
                "z": -99.0,
                "score": 0.0,
                "confidence": "very_low",
                "gate_blocks": gate_blocks,
            }
            continue

        score = compute_bundle_score(z)
        min_score = fparams.get("min_score", 20)
        if score < min_score:
            score = 0.0

        results[family] = {
            "product_key": pk,
            "product_meta": pm,
            "z": z,
            "score": score,
            "confidence": compute_confidence(score),
            "gate_blocks": gate_blocks,
        }

    return results


# ---------------------------------------------------------------------------
# PAIR RULE APPLICATION
# ---------------------------------------------------------------------------

def _apply_pair_rules(
    family_scores: Dict[str, Dict[str, Any]],
    exposure_feats: Dict[str, float],
    threshold: float = 50.0,
) -> Dict[str, Dict[str, Any]]:
    """
    Apply PAIR_RULES: if a trigger family scores above threshold and the
    condition feature is present, boost the z-score of the paired family.
    Returns updated family_scores with a note added to reasons.
    """
    boosted = deepcopy(family_scores)

    for rule in PAIR_RULES:
        trig = rule["trigger_family"]
        boost_fam = rule["boost_family"]
        cond = rule["condition_key"]
        delta = rule["delta_z"]
        reason = rule["reason"]

        trig_score = boosted.get(trig, {}).get("score", 0.0)
        cond_val = exposure_feats.get(cond, 0.0)

        if trig_score >= threshold and cond_val > 0:
            target = boosted.get(boost_fam)
            if target and target["product_key"] is not None:
                old_z = target["z"]
                new_z = old_z + delta
                new_score = compute_bundle_score(new_z)
                target["z"] = new_z
                target["score"] = new_score
                target["confidence"] = compute_confidence(new_score)
                target.setdefault("pair_reasons", []).append(
                    f"Boosted by {trig} pair rule: {reason}"
                )

    return boosted


# ---------------------------------------------------------------------------
# REASON GENERATION
# ---------------------------------------------------------------------------

_RISK_DISPLAY = {
    "Cyber Technical Risk": "high cyber technical risk",
    "Data Privacy Risk": "significant data privacy exposure",
    "Liability Risk": "elevated liability exposure",
    "IP Infringement Risk": "IP infringement risk",
    "Key Person Risk": "key person dependency",
    "Governance & Fraud Risk": "governance and fraud risk",
    "Property Risk": "physical asset exposure",
    "Regulatory Compliance Risk": "regulatory compliance obligations",
    "ESG & Climate Risk": "ESG / climate risk",
    "Geopolitical Risk": "geopolitical / cross-border risk",
    "Gig & Labour Risk": "gig / labour workforce exposure",
    "Policy Velocity Risk": "regulatory velocity risk",
    "Reputation Risk": "reputation risk",
}

_EXPOSURE_DISPLAY = {
    "has_factory": "factory / manufacturing operations",
    "has_warehouse": "warehouse / storage presence",
    "has_store": "retail store presence",
    "has_lab": "laboratory / R&D operations",
    "has_office": "office premises",
    "asset_tier": "significant physical asset value",
    "stock_tier": "substantial stock / inventory",
    "machinery_tier": "machinery / plant exposure",
    "headcount_tier": "workforce size",
    "blue_collar_tier": "blue-collar / field workforce",
    "gig_tier": "gig / contractor workforce",
    "has_domestic_shipments": "domestic goods transit",
    "has_export_shipments": "export / cross-border shipments",
    "receivables_tier": "trade receivables on credit",
    "vehicle_tier": "owned / operated vehicle fleet",
    "goods_vehicle_tier": "goods-carrying vehicle fleet",
    "has_project": "active construction / installation project",
    "capex_tier": "significant capital project value",
    "handles_personal_data": "personal data handling",
    "handles_financial_data": "financial data handling",
    "handles_medical_data": "medical / health data handling",
    "uptime_dependency": "revenue-critical uptime dependency",
    "transaction_tier": "high online transaction volume",
    "payment_card_program": "card / payment instrument programme",
    "healthcare_ops": "healthcare / clinical operations",
    "food_pharma_mfg": "food / pharma manufacturing",
    "warranty_obligation": "warranty / service contract obligations",
    "event_production_ops": "event / media production operations",
    "drone_ops": "commercial drone / RPA operations",
    "jewellery_inventory": "jewellery inventory",
    "fuel_forecourt": "fuel / forecourt operations",
    "port_maritime": "maritime / port operations",
    "telecom_network": "telecom network assets",
    "real_estate_dev": "real-estate development activity",
    "ma_transaction": "M&A / secondary transaction",
    "surety_bond_need": "contract / performance bond requirement",
    "is_funded": "funded-stage business",
    "regulatory_intensity_tier": "elevated regulatory intensity",
}


def _generate_reasons(
    family: str,
    product_meta: Dict[str, Any],
    family_params: Dict[str, Any],
    inp: BundleInputV2,
    exposure_feats: Dict[str, float],
    pair_reasons: List[str],
) -> List[str]:
    """
    Produce up to 5 human-readable reason strings for a recommendation.
    Priority: (1) high-weight risk scores, (2) triggered exposure features, (3) pair rules.
    """
    reasons: List[str] = []

    # Top risk drivers
    risk_weights = family_params.get("risk_weights", {})
    scored_risks = [
        (rk, inp.risk_scores.get(rk, 0.0) * rw)
        for rk, rw in risk_weights.items()
    ]
    scored_risks.sort(key=lambda x: x[1], reverse=True)
    for rk, contrib in scored_risks[:2]:
        raw = inp.risk_scores.get(rk, 0.0)
        if raw >= 40:
            label = _RISK_DISPLAY.get(rk, rk)
            reasons.append(f"Risk engine flags {label} (score {raw:.0f}/100).")

    # Top exposure drivers
    exposure_weights = family_params.get("exposure_weights", {})
    prod_ew = product_meta.get("exposure_weights", {})
    merged_ew = {**exposure_weights, **prod_ew}
    scored_exposures = [
        (fk, exposure_feats.get(fk, 0.0) * w)
        for fk, w in merged_ew.items()
    ]
    scored_exposures.sort(key=lambda x: x[1], reverse=True)
    for fk, contrib in scored_exposures[:3]:
        val = exposure_feats.get(fk, 0.0)
        if val > 0.05 and fk in _EXPOSURE_DISPLAY:
            reasons.append(f"Intake signals {_EXPOSURE_DISPLAY[fk]}.")
            if len(reasons) >= 4:
                break

    # Pair rule boosts
    for pr in pair_reasons[:1]:
        reasons.append(pr)

    # Sector-specific reason
    if inp.industry in product_meta.get("sector_tags", []):
        reasons.append(
            f"Product is specifically rated for the {inp.industry} sector."
        )

    return reasons[:5] if reasons else ["Recommended based on overall risk and exposure profile."]


def _generate_missing_inputs(
    family: str,
    inp: BundleInputV2,
) -> List[str]:
    """
    Identify intake fields that, if provided, could change or sharpen the recommendation.
    """
    missing = []

    if family in ("property_fire", "core_business_package") and inp.owned_assets_value == 0:
        missing.append("owned_assets_value: providing total asset value would select the correct product tier (Sookshma / Laghu / IAR).")

    if family == "employee_health" and inp.headcount_total == 0:
        missing.append("headcount_total: team size is required to determine group health eligibility and premium band.")

    if family == "employers_liability" and inp.headcount_blue_collar == 0 and inp.headcount_field == 0:
        missing.append("headcount_blue_collar / headcount_field: blue-collar and field headcount drives WC sum insured.")

    if family == "cyber" and not inp.handles_personal_data and not inp.handles_financial_data:
        missing.append("handles_personal_data / handles_financial_data: data type handled significantly affects cyber score.")

    if family == "marine_logistics_credit" and inp.receivables_on_credit == 0:
        missing.append("receivables_on_credit: outstanding trade receivables are needed to size Trade Credit Insurance.")

    if family == "engineering_project" and inp.capex_project_value == 0 and inp.project_under_construction:
        missing.append("capex_project_value: project value determines the correct CAR / EAR sum insured.")

    if family == "commercial_motor_fleet" and inp.total_vehicle_count == 0:
        missing.append("owned_vehicle_count / goods_vehicle_count: fleet size is the primary rating factor for motor insurance.")

    return missing


def _generate_paired_with(
    family: str,
    product_meta: Dict[str, Any],
    family_scores: Dict[str, Dict[str, Any]],
    threshold: float = 40.0,
) -> List[str]:
    """
    Return list of product names from product-level pair_rules and PAIR_RULES
    that also have non-trivial scores (>= threshold).
    """
    paired: List[str] = []

    # From product-level pair_rules
    for pair_family in product_meta.get("pair_rules", []):
        entry = family_scores.get(pair_family)
        if entry and entry["score"] >= threshold and entry["product_meta"]:
            paired.append(entry["product_meta"]["product_name"])

    # From PAIR_RULES where this family is the trigger
    for rule in PAIR_RULES:
        if rule["trigger_family"] == family:
            bf = rule["boost_family"]
            entry = family_scores.get(bf)
            if entry and entry["score"] >= threshold and entry["product_meta"]:
                name = entry["product_meta"]["product_name"]
                if name not in paired:
                    paired.append(name)

    return paired[:4]


# ---------------------------------------------------------------------------
# MAIN ENTRY POINT
# ---------------------------------------------------------------------------

def recommend_bundles_v2(inp: BundleInputV2) -> BundleOutput:
    """
    Core bundle recommendation function.

    Steps
    -----
    1. Extract normalised exposure features.
    2. Score every canonical family + select best variant within each.
    3. Apply pair rules (post-scoring boosts).
    4. Rank families by score descending.
    5. Build BundleRecommendation objects with reasons, missing inputs, and paired_with.
    6. Return top 3 as primary_bundles, next 2 as secondary_bundles.
    """
    exposure_feats = extract_exposure_features(inp)

    # Step 1: score all families
    raw_scores = _score_all_families(inp, exposure_feats)

    # Step 2: apply pair rules
    boosted_scores = _apply_pair_rules(raw_scores, exposure_feats)

    # Step 3: rank by score descending, only include families with score > 0
    ranked = sorted(
        [
            (fam, data)
            for fam, data in boosted_scores.items()
            if data["score"] > 0 and data["product_key"] is not None
        ],
        key=lambda x: x[1]["score"],
        reverse=True,
    )

    # Step 4: build recommendation objects
    recs: List[BundleRecommendation] = []
    for family, data in ranked:
        pk = data["product_key"]
        pm = data["product_meta"]
        pair_reasons = data.get("pair_reasons", [])

        family_params = FAMILY_SCORING_PARAMS.get(family, {})
        reasons = _generate_reasons(
            family, pm, family_params, inp, exposure_feats, pair_reasons
        )
        missing = _generate_missing_inputs(family, inp)
        paired = _generate_paired_with(family, pm, boosted_scores)

        rec = BundleRecommendation(
            product_name=pm["product_name"],
            canonical_family=family,
            product_key=pk,
            score=data["score"],
            confidence=data["confidence"],
            reasons=reasons,
            missing_inputs=missing,
            paired_with=paired,
            hard_gate_blocks=data.get("gate_blocks", []),
        )
        recs.append(rec)

    return BundleOutput(
        primary_bundles=recs[:3],
        secondary_bundles=recs[3:5],
    )


# ---------------------------------------------------------------------------
# CONVENIENCE: bridge from the existing server.py / analyze() flow
# ---------------------------------------------------------------------------

def get_bundle_recommendations_v2(
    sector: str,
    stage: str,
    risk_scores: Dict[str, float],
    inp_legacy,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Drop-in supplement for server.py analyze().
    Accepts the legacy StartupInput object + existing risk_scores dict,
    returns a JSON-serialisable dict.

    Usage in server.py::

        from bundle_recommender_v2 import get_bundle_recommendations_v2
        bundles_v2 = get_bundle_recommendations_v2(sector, stage, scores, inp, extra={...})
        result["bundles_v2"] = bundles_v2

    This does NOT replace match_bundle(); both can coexist in the response.
    """
    v2_inp = BundleInputV2.from_startup_input(inp_legacy, risk_scores=risk_scores, extra=extra)
    output = recommend_bundles_v2(v2_inp)
    return output.to_dict()
