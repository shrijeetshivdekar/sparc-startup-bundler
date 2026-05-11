"""
bundle_scoring_utils.py — Scoring primitives for bundle_recommender_v2.

Provides:
  - BundleInputV2 dataclass  (superset of StartupInput + full intake fields)
  - sigmoid / z-score helpers
  - exposure feature normalisation
  - hard gate evaluation
"""

from __future__ import annotations
import json
import math
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple


@dataclass(frozen=True)
class RiskWeights:
    cyber_technical: float
    data_privacy: float
    liability: float
    ip_infringement: float
    key_person: float
    governance_fraud: float
    property: float
    regulatory_compliance: float
    esg_climate: float
    geopolitical: float
    gig_labour: float
    policy_velocity: float
    reputation: float

    def as_dict(self) -> Dict[str, float]:
        return {
            "cyber_technical": self.cyber_technical,
            "data_privacy": self.data_privacy,
            "liability": self.liability,
            "ip_infringement": self.ip_infringement,
            "key_person": self.key_person,
            "governance_fraud": self.governance_fraud,
            "property": self.property,
            "regulatory_compliance": self.regulatory_compliance,
            "esg_climate": self.esg_climate,
            "geopolitical": self.geopolitical,
            "gig_labour": self.gig_labour,
            "policy_velocity": self.policy_velocity,
            "reputation": self.reputation,
        }


@dataclass(frozen=True)
class SectorMultipliers:
    values: Dict[str, Dict[str, float]]


@dataclass(frozen=True)
class StageMultipliers:
    values: Dict[str, Dict[str, float]]


@dataclass(frozen=True)
class AssetMultipliers:
    values: Dict[str, Dict[str, float]]


@dataclass(frozen=True)
class BundleMeta:
    name: str
    tam_cr: float
    base_premium: float
    adoption: float
    margin: float
    trajectory: str
    risk_mult: float
    eligible_sectors: Tuple[str, ...]
    eligible_stages: Tuple[str, ...]
    asset_band: Tuple[str, ...]
    components: Tuple[str, ...]
    si_cap_inr: Optional[float] = None
    regulatory_anchors: Tuple[str, ...] = ()
    covered_risks: Tuple[str, ...] = ()


@dataclass(frozen=True)
class ComplianceTrigger:
    signal: str
    regulation: str
    product: str
    mandatory: bool
    citation_url: str = ""


@dataclass(frozen=True)
class Config:
    config_version: str
    risk_weights: RiskWeights
    sector_multipliers: SectorMultipliers
    stage_multipliers: StageMultipliers
    asset_multipliers: AssetMultipliers
    bundle_meta: Dict[str, BundleMeta]
    regulatory_triggers: Tuple[ComplianceTrigger, ...]
    graduation_map: Dict[str, Any]
    raw: Dict[str, Any]


def _config_path(path: str) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return Path(__file__).resolve().parent / candidate


def _normalise_trigger(item: Dict[str, Any]) -> ComplianceTrigger:
    return ComplianceTrigger(
        signal=str(item.get("signal", "")),
        regulation=str(item.get("regulation") or item.get("reg", "")),
        product=str(item.get("product", "")),
        mandatory=bool(item.get("mandatory", False)),
        citation_url=str(item.get("citation_url", "")),
    )


def _validate_config(raw: Dict[str, Any]) -> None:
    from product_catalogue_v2 import PRODUCTS

    valid_uins = {product.uin for product in PRODUCTS.values()}
    valid_products = valid_uins | set(PRODUCTS.keys())
    life_uins = {
        product.uin
        for product in PRODUCTS.values()
        if product.route_to_life_insurer
    }

    weights = raw.get("risk_weights", {})
    total = sum(float(v) for v in weights.values())
    if abs(total - 1.0) > 1e-6:
        raise ValueError(f"risk_weights must sum to 1.0; got {total:.12f}")

    for bundle_key, meta in raw.get("bundle_meta", {}).items():
        components = meta.get("components", [])
        for component in components:
            if component not in valid_uins:
                raise ValueError(
                    f"bundle_meta.{bundle_key}.components references unknown product UIN {component!r}"
                )
            if component in life_uins:
                raise ValueError(
                    f"bundle_meta.{bundle_key}.components includes life-routed product {component!r}"
                )

    for trigger in raw.get("regulatory_triggers", []):
        product = str(trigger.get("product", ""))
        if product not in valid_products:
            raise ValueError(
                f"regulatory trigger {trigger.get('signal')!r} references unknown product {product!r}"
            )


def load_config(path: str = "research_config.json") -> Config:
    """Load and validate research_config.json into frozen typed dataclasses."""
    cfg_path = _config_path(path)
    with cfg_path.open(encoding="utf-8") as fh:
        raw = json.load(fh)
    _validate_config(raw)

    weights = RiskWeights(**raw["risk_weights"])
    bundles = {
        key: BundleMeta(
            name=str(meta.get("name", key.replace("_", " "))),
            tam_cr=float(meta["tam_cr"]),
            base_premium=float(meta["base_premium"]),
            adoption=float(meta["adoption"]),
            margin=float(meta["margin"]),
            trajectory=str(meta["trajectory"]),
            risk_mult=float(meta["risk_mult"]),
            eligible_sectors=tuple(meta.get("eligible_sectors", ())),
            eligible_stages=tuple(meta.get("eligible_stages", ())),
            asset_band=tuple(meta.get("asset_band", ())),
            components=tuple(meta.get("components", ())),
            si_cap_inr=meta.get("si_cap_inr"),
            regulatory_anchors=tuple(meta.get("regulatory_anchors", ())),
            covered_risks=tuple(meta.get("covered_risks", ())),
        )
        for key, meta in raw.get("bundle_meta", {}).items()
    }

    return Config(
        config_version=str(raw.get("config_version") or raw.get("version", "")),
        risk_weights=weights,
        sector_multipliers=SectorMultipliers(raw.get("sector_multipliers", {})),
        stage_multipliers=StageMultipliers(raw.get("stage_multipliers", {})),
        asset_multipliers=AssetMultipliers(raw.get("asset_multipliers", {})),
        bundle_meta=bundles,
        regulatory_triggers=tuple(_normalise_trigger(t) for t in raw.get("regulatory_triggers", ())),
        graduation_map=raw.get("graduation_map", {}),
        raw=raw,
    )


# ---------------------------------------------------------------------------
# INTAKE DATACLASS
# ---------------------------------------------------------------------------

@dataclass
class BundleInputV2:
    # Identity & Sector
    industry: str = "SaaS / Enterprise Software"
    sub_industry: Optional[str] = None
    business_model: str = "B2B"          # B2B | B2C | B2B2C | D2C | Marketplace
    development_stage: str = "Seed"
    funding_stage: str = "Seed"          # Pre-seed | Seed | Series A | Series B+
    annual_revenue: float = 0.0          # ₹ crores

    # Workforce
    headcount_total: int = 0
    headcount_field: int = 0             # field / sales / delivery workers
    headcount_blue_collar: int = 0       # factory / warehouse / manual labour
    contractors_count: int = 0
    gig_workers_count: int = 0

    # Physical Presence
    locations_count: int = 0
    office_presence: bool = False
    warehouse_presence: bool = False
    store_presence: bool = False
    lab_presence: bool = False
    factory_presence: bool = False

    # Asset Values (₹ crores)
    owned_assets_value: float = 0.0
    stock_value: float = 0.0
    machinery_value: float = 0.0
    electronics_value: float = 0.0

    # Logistics & Trade
    domestic_shipments: bool = False
    export_shipments: bool = False
    import_dependency: bool = False
    receivables_on_credit: float = 0.0   # ₹ crores on credit terms
    average_invoice_cycle_days: int = 0

    # Fleet
    owned_vehicle_count: int = 0
    goods_vehicle_count: int = 0
    miscellaneous_vehicle_count: int = 0
    two_wheeler_count: int = 0
    trailer_count: int = 0

    # Construction / Engineering
    project_under_construction: bool = False
    installation_or_commissioning: bool = False
    capex_project_value: float = 0.0     # ₹ crores

    # Cyber / Data
    handles_personal_data: bool = False
    handles_financial_data: bool = False
    handles_medical_data: bool = False
    stores_customer_documents: bool = False
    uptime_dependency: bool = False      # revenue-critical uptime SLA
    online_transaction_volume: int = 0   # transactions / month

    # Specialty Triggers
    payment_or_card_program: bool = False    # issues cards / payment instruments
    healthcare_operations: bool = False      # clinic / hospital / diagnostic centre
    food_or_pharma_manufacturing: bool = False
    warranty_or_service_contract_obligation: bool = False
    event_or_production_operations: bool = False
    drone_operations: bool = False
    jewellery_inventory: bool = False
    fuel_or_forecourt_operations: bool = False
    port_or_maritime_operations: bool = False
    telecom_network_assets: bool = False
    real_estate_development: bool = False
    M_and_A_or_secondary_transaction: bool = False
    contract_bid_or_performance_bond_need: bool = False

    # Risk Context
    regulatory_intensity: int = 0        # 0–5; 0 = minimal, 5 = highly regulated
    pincode: Optional[str] = None

    # Risk Engine Scores (0-100), injected after compute_risk_scores()
    risk_scores: Dict[str, float] = field(default_factory=dict)

    # -----------------------------------------------------------------------
    # Derived properties
    # -----------------------------------------------------------------------
    @property
    def total_insurable_asset_value(self) -> float:
        return (
            self.owned_assets_value
            + self.stock_value
            + self.machinery_value
            + self.electronics_value
        )

    @property
    def total_vehicle_count(self) -> int:
        return (
            self.owned_vehicle_count
            + self.goods_vehicle_count
            + self.miscellaneous_vehicle_count
            + self.two_wheeler_count
            + self.trailer_count
        )

    @property
    def any_physical_presence(self) -> bool:
        return any([
            self.office_presence, self.warehouse_presence, self.store_presence,
            self.lab_presence, self.factory_presence,
        ])

    @property
    def has_workforce(self) -> bool:
        return (
            self.headcount_total > 0
            or self.headcount_blue_collar > 0
            or self.headcount_field > 0
            or self.contractors_count > 0
            or self.gig_workers_count > 0
        )

    # -----------------------------------------------------------------------
    # Bridge from legacy StartupInput
    # -----------------------------------------------------------------------
    @classmethod
    def from_startup_input(
        cls,
        si,
        risk_scores: Optional[Dict[str, float]] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> "BundleInputV2":
        """
        Construct BundleInputV2 from the legacy StartupInput dataclass.
        Fields absent in StartupInput default to zero / False.
        Pass ``extra`` dict to override individual fields.
        """
        physical = getattr(si, "operations", "Digital-only")
        is_physical = physical in ("Physical-only", "Hybrid")
        sector = getattr(si, "sector", "SaaS / Enterprise Software")
        physical_assets = set(getattr(si, "physical_assets", []) or [])
        data_handled = set(getattr(si, "data_handled", []) or [])
        regulatory = set(getattr(si, "regulatory", []) or [])
        team_size = int(getattr(si, "team_size", 0) or 0)

        has_office = is_physical or "Office / coworking space" in physical_assets
        has_warehouse = "Warehouse / fulfilment centre" in physical_assets
        has_store = "Retail stores / kiosks" in physical_assets
        has_lab = any(asset in physical_assets for asset in (
            "Lab / R&D equipment", "Medical devices / diagnostic equipment", "Data centre / server room",
        ))
        has_factory = any(asset in physical_assets for asset in (
            "Manufacturing plant / factory", "Kitchen / food processing", "Solar / clean energy infrastructure",
        ))
        fleet_count = int((extra or {}).get("fleet_count", 0) or 0)
        if fleet_count <= 0 and "Vehicles / delivery fleet" in physical_assets:
            gig_pct = float(getattr(si, "gig_headcount_pct", 0.0) or 0.0)
            fleet_count = max(1, int(team_size * max(0.10, gig_pct or 0.20)))
        project_value = float((extra or {}).get("project_value_cr", 0.0) or (extra or {}).get("capex_project_value", 0.0) or 0.0)
        asset_value = float((extra or {}).get("total_insurable_asset_value_cr", 0.0) or (extra or {}).get("owned_assets_value", 0.0) or 0.0)
        annual_revenue = float((extra or {}).get("annual_revenue_cr", 0.0) or (extra or {}).get("annual_revenue", 0.0) or 0.0)

        inst = cls(
            industry=sector,
            sub_industry=getattr(si, "sub_sector", None),
            funding_stage=getattr(si, "funding_stage", "Seed"),
            development_stage=getattr(si, "funding_stage", "Seed"),
            annual_revenue=annual_revenue,
            headcount_total=team_size,
            headcount_field=max(0, int(team_size * float(getattr(si, "gig_headcount_pct", 0.0) or 0.0))),
            office_presence=has_office,
            warehouse_presence=has_warehouse,
            store_presence=has_store,
            lab_presence=has_lab,
            factory_presence=has_factory,
            owned_assets_value=asset_value,
            stock_value=asset_value * (0.35 if has_warehouse or has_store else 0.12),
            machinery_value=asset_value * (0.45 if has_factory else 0.0),
            electronics_value=asset_value * (0.25 if has_lab else 0.0),
            domestic_shipments=bool(physical_assets & {"Warehouse / fulfilment centre", "Vehicles / delivery fleet"}),
            export_shipments=bool(getattr(si, "export_eu_pct", 0.0) or getattr(si, "export_us_pct", 0.0) or getattr(si, "export_china_pct", 0.0)),
            owned_vehicle_count=fleet_count,
            two_wheeler_count=fleet_count if sector in ("Logistics / Mobility", "Foodtech / Cloud Kitchen") else 0,
            project_under_construction=project_value > 0,
            capex_project_value=project_value,
            regulatory_intensity=_infer_reg_intensity(sector),
            handles_personal_data=getattr(si, "data_sensitivity", "Low") in ("Medium", "High"),
            handles_financial_data=sector in ("Fintech",) or "Payments / financial transactions" in data_handled,
            handles_medical_data=sector in ("Healthtech",) or "Health / medical records" in data_handled,
            uptime_dependency=getattr(si, "data_sensitivity", "Low") == "High",
            payment_or_card_program=bool((extra or {}).get("payment_or_card_program") or sector == "Fintech" and (
                getattr(si, "rbi_registration", None) or "RBI / SEBI / IRDAI licensed" in regulatory or "Payments / financial transactions" in data_handled
            )),
            healthcare_operations=bool((extra or {}).get("healthcare_operations") or sector == "Healthtech" and (
                "Health / medical records" in data_handled or "Medical devices / diagnostic equipment" in physical_assets
            )),
            food_or_pharma_manufacturing=bool((extra or {}).get("food_or_pharma_manufacturing") or (
                "FSSAI / food safety" in regulatory or "Kitchen / food processing" in physical_assets
            )),
            event_or_production_operations=bool((extra or {}).get("event_or_production_operations")),
            drone_operations="Drones / UAV equipment" in physical_assets or "DGCA / drone operations" in regulatory,
            contract_bid_or_performance_bond_need=bool((extra or {}).get("contract_bid_or_performance_bond_need")),
            risk_scores=risk_scores or {},
        )
        if extra:
            for k, v in extra.items():
                if hasattr(inst, k):
                    setattr(inst, k, v)
        return inst


def _infer_reg_intensity(sector: str) -> int:
    high = {"Fintech", "Healthtech", "Gaming / Media / Content"}
    medium = {"SaaS / Enterprise Software", "Legaltech", "HRtech", "Logistics / Mobility", "Edtech"}
    if sector in high:
        return 4
    if sector in medium:
        return 2
    return 1


# ---------------------------------------------------------------------------
# MATH HELPERS
# ---------------------------------------------------------------------------

def sigmoid(x: float) -> float:
    """Numerically stable sigmoid: 1 / (1 + e^-x)."""
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    ex = math.exp(x)
    return ex / (1.0 + ex)


def _log_scale(value: float, max_value: float) -> float:
    """Compress a large-range positive value to 0–1 using log scale."""
    if value <= 0:
        return 0.0
    return min(1.0, math.log1p(value) / math.log1p(max_value))


# ---------------------------------------------------------------------------
# EXPOSURE FEATURE EXTRACTION  (BundleInputV2 → normalised feature dict)
# ---------------------------------------------------------------------------

def extract_exposure_features(inp: BundleInputV2) -> Dict[str, float]:
    """
    Derive a normalised (0–1) feature vector from intake.
    These map to exposure_weights in the z-score formula.
    """
    field_blue = inp.headcount_field + inp.headcount_blue_collar

    return {
        # Physical presence
        "has_office":      float(inp.office_presence),
        "has_warehouse":   float(inp.warehouse_presence),
        "has_store":       float(inp.store_presence),
        "has_lab":         float(inp.lab_presence),
        "has_factory":     float(inp.factory_presence),
        "any_physical":    float(inp.any_physical_presence),
        "locations_tier":  _log_scale(inp.locations_count, 20),

        # Asset values (log-compressed, max ₹200Cr for general assets)
        "asset_tier":      _log_scale(inp.total_insurable_asset_value, 200),
        "stock_tier":      _log_scale(inp.stock_value, 50),
        "machinery_tier":  _log_scale(inp.machinery_value, 100),
        "electronics_tier": _log_scale(inp.electronics_value, 50),

        # Workforce
        "headcount_tier":   _log_scale(inp.headcount_total, 500),
        "blue_collar_tier": _log_scale(field_blue, 200),
        "gig_tier":         _log_scale(inp.gig_workers_count + inp.contractors_count, 100),
        "has_workforce":    float(inp.has_workforce),

        # Logistics & trade
        "has_domestic_shipments": float(inp.domestic_shipments),
        "has_export_shipments":   float(inp.export_shipments),
        "has_import_dependency":  float(inp.import_dependency),
        "receivables_tier":  _log_scale(inp.receivables_on_credit, 100),
        "invoice_cycle_tier": min(1.0, inp.average_invoice_cycle_days / 90.0),

        # Fleet
        "vehicle_tier":        _log_scale(inp.total_vehicle_count, 50),
        "goods_vehicle_tier":  _log_scale(inp.goods_vehicle_count, 30),
        "has_trailer":         float(inp.trailer_count > 0),
        "has_two_wheeler":     float(inp.two_wheeler_count > 0),

        # Engineering / construction
        "has_project":  float(inp.project_under_construction or inp.installation_or_commissioning),
        "capex_tier":   _log_scale(inp.capex_project_value, 500),

        # Cyber / data
        "handles_personal_data":  float(inp.handles_personal_data),
        "handles_financial_data": float(inp.handles_financial_data),
        "handles_medical_data":   float(inp.handles_medical_data),
        "stores_docs":            float(inp.stores_customer_documents),
        "uptime_dependency":      float(inp.uptime_dependency),
        "transaction_tier":       _log_scale(inp.online_transaction_volume, 1_000_000),

        # Specialty triggers
        "payment_card_program":     float(inp.payment_or_card_program),
        "healthcare_ops":           float(inp.healthcare_operations),
        "food_pharma_mfg":          float(inp.food_or_pharma_manufacturing),
        "warranty_obligation":      float(inp.warranty_or_service_contract_obligation),
        "event_production_ops":     float(inp.event_or_production_operations),
        "drone_ops":                float(inp.drone_operations),
        "jewellery_inventory":      float(inp.jewellery_inventory),
        "fuel_forecourt":           float(inp.fuel_or_forecourt_operations),
        "port_maritime":            float(inp.port_or_maritime_operations),
        "telecom_network":          float(inp.telecom_network_assets),
        "real_estate_dev":          float(inp.real_estate_development),
        "ma_transaction":           float(inp.M_and_A_or_secondary_transaction),
        "surety_bond_need":         float(inp.contract_bid_or_performance_bond_need),
        "regulatory_intensity_tier": min(1.0, inp.regulatory_intensity / 5.0),

        # Stage / size proxy
        "is_funded":    float(inp.funding_stage in ("Series A", "Series B+")),
        "is_growth":    float(inp.funding_stage == "Series B+"),
        "is_early":     float(inp.funding_stage in ("Pre-seed", "Seed")),
        "revenue_tier": _log_scale(inp.annual_revenue, 500),
    }


# ---------------------------------------------------------------------------
# HARD GATE EVALUATION
# ---------------------------------------------------------------------------

def check_hard_gates(
    gates: Dict[str, Any],
    inp: BundleInputV2,
) -> Tuple[bool, Optional[str]]:
    """
    Returns (eligible, block_reason_or_None).
    First failing gate terminates evaluation.
    """
    total_assets = inp.total_insurable_asset_value

    _checks: Dict[str, Any] = {
        "max_total_insurable_value": lambda v: (
            total_assets <= v,
            f"Asset value ₹{total_assets:.1f}Cr exceeds ₹{v}Cr ceiling for this product"
        ),
        "min_total_insurable_value": lambda v: (
            total_assets >= v,
            f"Asset value ₹{total_assets:.1f}Cr below ₹{v}Cr floor for this product"
        ),
        "min_headcount": lambda v: (
            inp.headcount_total >= v,
            f"Team size {inp.headcount_total} below minimum {v} for this product"
        ),
        "requires_drone_ops": lambda v: (
            (inp.drone_operations if v else True),
            "Requires active drone / RPA operations"
        ),
        "requires_payment_or_card_program": lambda v: (
            (inp.payment_or_card_program if v else True),
            "Requires a card-issuing or payment-instrument programme"
        ),
        "requires_real_estate_development": lambda v: (
            (inp.real_estate_development if v else True),
            "Title insurance requires real-estate development activity"
        ),
        "requires_ma_transaction": lambda v: (
            (inp.M_and_A_or_secondary_transaction if v else True),
            "R&W insurance requires an M&A / secondary transaction context"
        ),
        "requires_port_maritime": lambda v: (
            (inp.port_or_maritime_operations if v else True),
            "Port Package requires active maritime / port operations"
        ),
        "requires_telecom_network": lambda v: (
            (inp.telecom_network_assets if v else True),
            "Cellular Network insurance requires telecom network assets"
        ),
        "requires_jewellery_inventory": lambda v: (
            (inp.jewellery_inventory if v else True),
            "Jeweller's Package requires jewellery inventory"
        ),
        "requires_fuel_forecourt": lambda v: (
            (inp.fuel_or_forecourt_operations if v else True),
            "Petrol Station Package requires fuel / forecourt operations"
        ),
        "requires_project_or_installation": lambda v: (
            ((inp.project_under_construction or inp.installation_or_commissioning) if v else True),
            "Engineering product requires active construction or commissioning project"
        ),
        "requires_vehicles": lambda v: (
            (inp.total_vehicle_count > 0 if v else True),
            "Motor policy requires at least one owned / operated vehicle"
        ),
        "requires_healthcare_ops": lambda v: (
            (inp.healthcare_operations if v else True),
            "Healthcare Professional Indemnity requires healthcare operations"
        ),
        "requires_event_production": lambda v: (
            (inp.event_or_production_operations if v else True),
            "Entertainment Production package requires event / production operations"
        ),
        "requires_any_physical_presence": lambda v: (
            (inp.any_physical_presence if v else True),
            "Product requires physical premises or on-site assets"
        ),
        "requires_workforce": lambda v: (
            (inp.has_workforce if v else True),
            "Employee / workforce product requires active headcount"
        ),
        "requires_food_pharma": lambda v: (
            (inp.food_or_pharma_manufacturing if v else True),
            "Contamination / recall insurance requires food or pharma manufacturing"
        ),
        "requires_aviation": lambda v: (
            ((inp.drone_operations or getattr(inp, "_aviation_ops", False)) if v else True),
            "Aviation insurance requires aviation or drone operations"
        ),
        "requires_surety_or_construction": lambda v: (
            ((inp.contract_bid_or_performance_bond_need or inp.project_under_construction) if v else True),
            "Surety insurance requires a bid bond, performance bond, or construction project"
        ),
        "max_industrial_sum_insured": lambda v: (
            total_assets < v,
            f"IAR / industrial covers are not available below ₹{v}Cr sum insured"
        ),
    }

    for gate_key, gate_value in gates.items():
        if gate_key in _checks:
            result = _checks[gate_key](gate_value)
            ok, reason = result
            if not ok:
                return False, reason

    return True, None


# ---------------------------------------------------------------------------
# Z-SCORE AND BUNDLE SCORE COMPUTATION
# ---------------------------------------------------------------------------

def compute_z_score(
    params: Dict[str, Any],
    risk_scores: Dict[str, float],
    exposure_feats: Dict[str, float],
) -> float:
    """
    z_b = intercept
        + Σ(risk_scores_normalised * risk_weights)
        + Σ(exposure_feats * exposure_weights)
        + trend_prior
        + Σ(exposure_feats * wording_weights)
        - Σ(exposure_feats * penalty_weights)
    """
    z = float(params.get("intercept", -2.0))

    # Risk engine contribution (scores 0-100 → normalise to 0-1)
    for risk_key, weight in params.get("risk_weights", {}).items():
        score = risk_scores.get(risk_key, 0.0) / 100.0
        z += score * weight

    # Exposure feature contribution
    for feat_key, weight in params.get("exposure_weights", {}).items():
        z += exposure_feats.get(feat_key, 0.0) * weight

    # Trend priors (additive constant)
    z += float(params.get("trend_prior", 0.0))

    # Wording features (additional additive when present)
    for feat_key, weight in params.get("wording_weights", {}).items():
        z += exposure_feats.get(feat_key, 0.0) * weight

    # Penalties (subtracted)
    for feat_key, weight in params.get("penalty_weights", {}).items():
        z -= exposure_feats.get(feat_key, 0.0) * weight

    return z


def compute_bundle_score(z: float) -> float:
    """Convert z-score to 0–100 score via sigmoid."""
    return round(100.0 * sigmoid(z), 2)


def compute_confidence(score: float) -> str:
    if score >= 70:
        return "high"
    if score >= 50:
        return "medium"
    if score >= 30:
        return "low"
    return "very_low"
