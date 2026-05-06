"""
Bundle Pricing Agent for SPARC.

Wraps the deterministic pricing engine with bundle-level analysis:
market benchmarking, coverage density scoring, slim-tier comparison,
and a structured summary for the recommendation output stage.

Public API
----------
price_bundle(profile, scores, bundle, recommendations=None) -> dict
    Returns ``bundle_quote`` (full pricing engine output) and
    ``bundle_analysis`` (market benchmarks, coverage density, alt tiers).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pricing_engine import (
    COVER_SPECS,
    GST_RATE,
    _float,
    _select_covers,
    infer_underwriting_inputs,
    normalize_cover_key,
    price_output_stage,
)

BUNDLE_AGENT_VERSION = "bundle-agent-2026.05"

# Market mid-rates for Indian SME/startup segment, Q1 2026.
# Used only for benchmark comparison — not for premium calculation.
# Sources:
#   Cyber      — Mitigata Cyber Insurance India 2026 study
#   D&O / PI   — Liberty General / IFFCO Tokio market quotes; IRDAI PI Guidelines 2021
#   Property   — BusinessStandard Dec 2024 fire premium analysis; Trust Risk Control Jan 2025
#   EEI        — WTIB Electronic Equipment Tariff (de-notified reference)
#   Employees  — NivaaBupa / Pazcare group health data 2025-26
#   Group PA   — Bajaj Finserv group PA range
#   Marine     — Pazago domestic marine cargo rates
#   Trade Cred — Allianz Trade cost guide
#   Engineering— Riskbirbal CAR/EAR rate guide
#   Surety     — IRDAI Surety Insurance Guidelines 2022
MARKET_MID_RATES: Dict[str, Dict[str, Any]] = {
    "cyber_liability":               {"rate_pct": 2.00, "unit": "% of limit",          "source": "Mitigata Cyber Insurance India 2026"},
    "dno_liability":                 {"rate_pct": 0.85, "unit": "% of limit",          "source": "Liberty General / IFFCO Tokio market"},
    "professional_indemnity":        {"rate_pct": 0.80, "unit": "% of limit",          "source": "IRDAI PI Guidelines 2021 + broker quotes"},
    "comprehensive_general_liability": {"rate_pct": 0.45, "unit": "% of limit",        "source": "HDFC ERGO CGL market range"},
    "public_liability":              {"rate_pct": 0.35, "unit": "% of limit",          "source": "Bajaj Allianz PL market range"},
    "product_liability":             {"rate_pct": 0.60, "unit": "% of limit",          "source": "Market estimate (D2C / Healthtech)"},
    "property_fire":                 {"rate_pct": 0.40, "unit": "% of SI",             "source": "BusinessStandard Dec 2024: +60% rise in 2025"},
    "property_all_risk":             {"rate_pct": 0.60, "unit": "% of SI",             "source": "Market convention ~1.5x fire rate"},
    "business_interruption":         {"rate_pct": 0.25, "unit": "% of BI SI",          "source": "Trust Risk Control Jan 2025 standardisation"},
    "burglary":                      {"rate_pct": 0.20, "unit": "% of stock value",    "source": "Market estimate 0.18–0.25%"},
    "electronic_equipment":          {"rate_pct": 0.90, "unit": "% of equipment value","source": "WTIB EEI tariff (de-notified); market 0.8–1.2%"},
    "machinery_breakdown":           {"rate_pct": 0.65, "unit": "% of plant value",    "source": "HDFC ERGO / Liberty General range"},
    "employees_comp":                {"rate_pct": 0.50, "unit": "% of payroll",        "source": "IRDAI WC; office-class ~0.5% of payroll"},
    "employee_health":               {"rate_pct": None, "unit": "Rs.15,000 / employee",  "source": "NivaaBupa / Pazcare group health 2025-26"},
    "group_pa":                      {"rate_pct": None, "unit": "Rs.10,000 / employee",  "source": "Bajaj Finserv group PA range"},
    "marine_transit":                {"rate_pct": 0.45, "unit": "% of cargo turnover", "source": "Pazago domestic marine cargo 0.3–0.8%"},
    "trade_credit":                  {"rate_pct": 0.40, "unit": "% of receivables",    "source": "Allianz Trade: 0.1–0.4% of annual sales"},
    "engineering":                   {"rate_pct": 0.25, "unit": "% of project value",  "source": "Riskbirbal CAR/EAR guide 0.1–0.5%"},
    "surety":                        {"rate_pct": 0.55, "unit": "% of contract value", "source": "IRDAI Surety Insurance Guidelines 2022"},
    "parametric":                    {"rate_pct": 0.28, "unit": "% of exposed value",  "source": "Emerging product; limited market data"},
    "money_insurance":               {"rate_pct": 0.40, "unit": "% of cash limit",     "source": "Market estimate"},
    "crime_fidelity":                {"rate_pct": 0.40, "unit": "% of limit",          "source": "Market estimate"},
    "drone_insurance":               {"rate_pct": 0.50, "unit": "% of hull SI",        "source": "Limited market data"},
}

# Risk category buckets for coverage density scoring.
_RISK_CATEGORIES: Dict[str, set] = {
    "liability":  {"cyber_liability", "dno_liability", "professional_indemnity",
                   "comprehensive_general_liability", "public_liability", "product_liability"},
    "property":   {"property_fire", "property_all_risk", "business_interruption",
                   "burglary", "electronic_equipment", "machinery_breakdown"},
    "people":     {"employees_comp", "employee_health", "group_pa"},
    "financial":  {"trade_credit", "crime_fidelity", "money_insurance", "surety"},
    "specialty":  {"marine_transit", "engineering", "parametric", "drone_insurance"},
}


def _bundle_to_dict(bundle: Any) -> Dict[str, Any]:
    """Coerce BundleRecommendation, plain dataclass, or dict to a plain dict."""
    if bundle is None:
        return {}
    if isinstance(bundle, dict):
        return bundle
    if hasattr(bundle, "to_dict"):
        return bundle.to_dict()
    if hasattr(bundle, "__dataclass_fields__"):
        import dataclasses
        return dataclasses.asdict(bundle)
    return dict(bundle)


def _market_benchmark(cover_key: str, premium_lakh: float, exposure: float) -> Dict[str, Any]:
    """Compare the engine premium against the published market mid-rate."""
    bench = MARKET_MID_RATES.get(cover_key)
    if not bench:
        return {}
    if bench["rate_pct"] is None:
        return {"market_note": bench["unit"], "market_source": bench["source"]}
    # rate_pct is expressed as percentage of exposure (SI / limit / payroll / etc.)
    market_lakh = round(exposure * bench["rate_pct"] / 100 * 100, 2)
    delta_pct = (
        round((premium_lakh - market_lakh) / market_lakh * 100, 1)
        if market_lakh > 0 else None
    )
    return {
        "market_mid_rate": f"{bench['rate_pct']}% ({bench['unit']})",
        "market_mid_premium_lakh": market_lakh,
        "vs_market_delta_pct": delta_pct,
        "market_source": bench["source"],
    }


def _coverage_density(covers: List[str]) -> Dict[str, Any]:
    """Score coverage breadth across the five risk categories."""
    cover_set = set(covers)
    by_cat: Dict[str, Any] = {}
    for cat, members in _RISK_CATEGORIES.items():
        covered = sorted(cover_set & members)
        missing = sorted(members - cover_set)
        by_cat[cat] = {
            "covered": covered,
            "missing": missing,
            "score": round(len(covered) / len(members), 2),
        }
    overall = round(sum(d["score"] for d in by_cat.values()) / len(_RISK_CATEGORIES), 2)
    return {"by_category": by_cat, "overall_breadth_score": overall}


def _slim_tier_quote(
    profile: Dict[str, Any],
    scores: Dict[str, Any],
    bundle_dict: Dict[str, Any],
    recommendations: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Price a slim version of the bundle containing only mandatory covers
    (or the first 3 covers if no mandatory list is defined).
    """
    mandatory_raw = bundle_dict.get("mandatory_covers") or []
    slim_bundle = {
        "name": f"{bundle_dict.get('name', 'Bundle')} — Mandatory Only",
        "mandatory_covers": mandatory_raw or bundle_dict.get("optional_covers", [])[:3],
        "optional_covers": [],
    }
    slim_profile = {**profile, "quote_requested": True}
    quote = price_output_stage(slim_profile, scores, recommendations, slim_bundle)
    if quote.get("quote_type") != "indicative_underwriting_quote":
        return {"available": False, "reason": quote.get("quote_type")}
    return {
        "available": True,
        "covers": [c["cover_key"] for c in quote["covers_priced"]],
        "cover_count": quote["cover_count"],
        "gross_premium_lakh": quote["gross_premium_lakh"],
        "gross_premium_inr": quote["gross_premium_inr"],
    }


def price_bundle(
    profile: Dict[str, Any],
    scores: Dict[str, Any],
    bundle: Any,
    recommendations: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Price a recommended bundle and return an enriched quote with market
    benchmarks, coverage density scoring, slim-tier comparison, and
    bundle-level value metrics.

    Parameters
    ----------
    profile         : Startup intake profile dict.
    scores          : Risk dimension scores dict (keyed by risk category name).
    bundle          : BundleRecommendation object, plain dataclass, or dict with
                      keys ``name``, ``mandatory_covers``, ``optional_covers``.
    recommendations : Optional standalone product recommendations list.

    Returns
    -------
    dict
        ``bundle_agent_version``, ``bundle_name``, ``bundle_quote`` (full
        pricing engine output with per-cover market benchmarks injected),
        ``bundle_analysis`` (coverage density, value metrics, slim tier,
        market benchmarks index).
    """
    bundle_dict = _bundle_to_dict(bundle)
    recommendations = recommendations or []
    bundle_name = bundle_dict.get("name") or bundle_dict.get("product_name") or "Unnamed Bundle"

    quote = price_output_stage(profile, scores, recommendations, bundle_dict)

    if quote["quote_type"] != "indicative_underwriting_quote":
        return {
            "bundle_agent_version": BUNDLE_AGENT_VERSION,
            "bundle_name": bundle_name,
            "bundle_quote": quote,
            "bundle_analysis": None,
        }

    covers = _select_covers(recommendations, bundle_dict)
    priced_items = quote["covers_priced"]

    # Inject market benchmark comparison into each priced cover.
    benchmarked_covers = [
        {
            **item,
            "market_benchmark": _market_benchmark(
                item["cover_key"], item["premium_lakh"], item["exposure_value"]
            ),
        }
        for item in priced_items
    ]

    # Value metrics.
    gross = quote["gross_premium_lakh"]
    total_si = quote["total_sum_insured_cr"]
    n_covers = len(priced_items)
    n_headcount = sum(
        1 for i in priced_items
        if COVER_SPECS[i["cover_key"]].pricing_unit == "per_employee"
    )

    # Slim-tier alternative (mandatory covers only, no bundle discount).
    slim = _slim_tier_quote(profile, scores, bundle_dict, recommendations)
    slim_savings = (
        round(gross - slim["gross_premium_lakh"], 2)
        if slim.get("available") else None
    )

    return {
        "bundle_agent_version": BUNDLE_AGENT_VERSION,
        "bundle_name": bundle_name,
        "bundle_quote": {**quote, "covers_priced": benchmarked_covers},
        "bundle_analysis": {
            "value_metrics": {
                "gross_premium_lakh": gross,
                "gross_premium_inr": quote["gross_premium_inr"],
                "cover_count": n_covers,
                "per_cover_avg_lakh": round(gross / max(n_covers, 1), 2),
                "total_si_cr": total_si,
                "si_to_annual_premium_ratio": (
                    round(total_si / gross, 1) if gross > 0 and total_si > 0 else None
                ),
                "headcount_covers_count": n_headcount,
                "bundle_discount_pct": round(quote["bundle_discount_rate"] * 100, 1),
                "bundle_discount_lakh": quote["bundle_discount_lakh"],
            },
            "coverage_density": _coverage_density(covers),
            "slim_mandatory_tier": {
                **slim,
                "savings_vs_full_bundle_lakh": slim_savings,
            },
            "market_benchmarks": {
                k: v for k, v in MARKET_MID_RATES.items() if k in covers
            },
        },
    }
