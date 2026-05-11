"""
Deterministic premium pricing engine for SPARC.

The engine deliberately keeps premium math outside GenAI. It accepts the
recommended bundle/output profile, normalises covers, infers missing sum insured
values from the intake profile, and returns an auditable quote object.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

from risk_appetite import get_appetite


CRORE_INR = 10_000_000
GST_RATE = 0.18
ENGINE_VERSION = "pricing-2026.05.r1"

# Maximum multiplier any cover's combined loading can reach.
# Prevents pathological compounding (risk×stage×sector×climate×claims can
# theoretically reach 7x; 4x is the auditable ceiling).
MAX_COMBINED_LOADING = 4.0

BAD_RISK_REASONS_SHORT = {
    "cyber_liability": {
        "Fintech": "High claim frequency; elevated deductible likely required.",
        "Gaming / Media / Content": "Ransomware/extortion exposure disproportionately high.",
    },
    "product_liability": {
        "SaaS / Enterprise Software": "Software failures are PI/E&O claims, not product liability.",
        "Fintech": "Financial service failures handled through PI/E&O, not product liability.",
    },
    "marine_transit": {
        "Fintech": "No physical goods; no cargo exposure.",
        "SaaS / Enterprise Software": "Digital-only; no cargo exposure.",
    },
}


COVER_ALIASES = {
    "CYBER": "cyber_liability",
    "cyber": "cyber_liability",
    "cyber_liability": "cyber_liability",
    "D_AND_O": "dno_liability",
    "d_and_o": "dno_liability",
    "dno_liability": "dno_liability",
    "PI_TECH_EO": "professional_indemnity",
    "pi_tech_eo": "professional_indemnity",
    "professional_indemnity": "professional_indemnity",
    "CGL_I_ELITE": "comprehensive_general_liability",
    "cgl_i_elite": "comprehensive_general_liability",
    "comprehensive_general_liability": "comprehensive_general_liability",
    "PUBLIC_LIABILITY": "public_liability",
    "public_liability": "public_liability",
    "PRODUCT_LIABILITY": "product_liability",
    "product_liability": "product_liability",
    "EMPLOYERS_COMP": "employees_comp",
    "employees_comp": "employees_comp",
    "GROUP_HEALTH": "employee_health",
    "group_health": "employee_health",
    "employee_health": "employee_health",
    "GROUP_PA": "group_pa",
    "group_pa": "group_pa",
    "BHARAT_SOOKSHMA": "property_fire",
    "bharat_sookshma": "property_fire",
    "property_fire": "property_fire",
    "PROPERTY_FIRE": "property_fire",
    "BUSINESS_INTERRUPTION": "business_interruption",
    "business_interruption": "business_interruption",
    "PROPERTY_ALL_RISK": "property_all_risk",
    "property_all_risk": "property_all_risk",
    "ELECTRONIC_EQUIPMENT": "electronic_equipment",
    "electronic_equipment": "electronic_equipment",
    "MACHINERY_BREAKDOWN": "machinery_breakdown",
    "ENGINEERING_CAR_EAR_CPM_MBD_EEI": "engineering",
    "engineering": "engineering",
    "contractors_all_risk": "engineering",
    "CONTRACTORS_ALL_RISK": "engineering",
    "SURETY": "surety",
    "surety": "surety",
    "MARINE_CARGO": "marine_transit",
    "marine_cargo": "marine_transit",
    "marine_transit": "marine_transit",
    "TRADE_CREDIT": "trade_credit",
    "trade_credit": "trade_credit",
    "PRAKRITIK_PARAMETRIC": "parametric",
    "prakritik_parametric": "parametric",
    "parametric": "parametric",
    "burglary": "burglary",
    "money_insurance": "money_insurance",
    "CRIME_FIDELITY": "crime_fidelity",
    "crime_fidelity": "crime_fidelity",
    "Drone_RPAS": "drone_insurance",
    "drone_rpas": "drone_insurance",
    "drone_insurance": "drone_insurance",
    "employment_practices": "employment_practices",
    "EMPLOYMENT_PRACTICES": "employment_practices",
    "epl": "employment_practices",
    "EPL": "employment_practices",
    "epli": "employment_practices",
    "EPLI": "employment_practices",
    "machinery_breakdown": "machinery_breakdown",
    "MOTOR_FLEET": "motor_fleet",
    "motor_fleet": "motor_fleet",
    "commercial_motor_fleet": "motor_fleet",
    "HEALTHCARE_PI": "healthcare_pi",
    "healthcare_pi": "healthcare_pi",
    "FINANCIAL_SERVICES_PI": "financial_services_pi",
    "financial_services_pi": "financial_services_pi",
    "PAYMENT_PROTECTION": "payment_protection",
    "payment_protection": "payment_protection",
    "PRODUCT_RECALL": "product_recall",
    "TOTAL_RECALL": "product_recall",
    "product_recall": "product_recall",
    "EVENT_PRODUCTION": "event_production",
    "event_production": "event_production",
    "ENTERTAINMENT_PRODUCTION": "event_production",
}


@dataclass(frozen=True)
class CoverSpec:
    label: str
    exposure_field: str
    rate_lakh_per_cr: float
    min_lakh: float
    risk_keys: tuple[str, ...]
    pricing_unit: str = "sum_insured"


# Base rates below are calibrated to Indian SME/startup market mid-points as of Q1 2026.
# Sources: Mitigata Cyber Insurance India 2026; NivaaBupa/Pazcare group health data;
# Pazago marine cargo rates; Allianz Trade credit data; Riskbirbal CAR/EAR guide;
# IRDAI Surety Guidelines 2022; BusinessStandard fire premium analysis Dec 2024;
# WTIB EEI tariff; HDFC ERGO / Liberty General machinery breakdown quotes.
# All covers are non-tariff (market-based) post IRDAI de-notification Apr 2024,
# except Employees Compensation (IIB-based) and Electronic Equipment (ex-tariff reference).
COVER_SPECS: Dict[str, CoverSpec] = {
    # rate 1.75 → effective ~2.0% of limit at mid-loading; market 2–2.5L/Cr (Mitigata 2026)
    "cyber_liability": CoverSpec(
        "Cyber Liability", "cyber_limit_cr", 1.75, 1.50,
        ("Cyber Technical Risk", "Data Privacy Risk", "Regulatory Compliance Risk"),
    ),
    # rate 0.75 → effective ~0.85% of limit; market 0.5–1.5% (Liberty/IFFCO Tokio); floor raised to 2.00L (institutional round trigger)
    "dno_liability": CoverSpec(
        "Directors and Officers Liability", "dno_limit_cr", 0.75, 2.00,
        ("Governance & Fraud Risk", "Regulatory Compliance Risk", "Reputation Risk"),
    ),
    # rate 0.70 → effective ~0.80% of limit; market 0.6–1.2% (IRDAI PI Guidelines 2021)
    "professional_indemnity": CoverSpec(
        "Professional Indemnity / Tech E&O", "pi_limit_cr", 0.70, 1.00,
        ("Liability Risk", "IP Infringement Risk", "Reputation Risk"),
    ),
    # rate 0.40 → effective ~0.45% of limit; HDFC ERGO CGL market range
    "comprehensive_general_liability": CoverSpec(
        "Comprehensive General Liability", "public_liability_limit_cr", 0.40, 0.55,
        ("Liability Risk", "Reputation Risk", "Regulatory Compliance Risk"),
    ),
    # rate 0.30 → effective ~0.34% of limit; Bajaj Allianz PL range
    "public_liability": CoverSpec(
        "Public Liability", "public_liability_limit_cr", 0.30, 0.35,
        ("Liability Risk", "Property Risk"),
    ),
    # rate 0.52 → effective ~0.59% of limit; market for D2C/Healthtech sectors
    "product_liability": CoverSpec(
        "Product Liability", "product_liability_limit_cr", 0.52, 0.60,
        ("Liability Risk", "Reputation Risk", "Regulatory Compliance Risk"),
    ),
    # rate 0.50 → effective ~0.57% of SI; IRDAI de-tariff Apr 2024 drove market rates up 60–80% (BusinessStandard Dec 2024)
    "property_fire": CoverSpec(
        "Property Fire", "property_sum_insured_cr", 0.50, 0.45,
        ("Property Risk", "ESG & Climate Risk"),
    ),
    # rate 0.52 → effective ~0.59% of SI; ~1.5x fire rate per market convention
    "property_all_risk": CoverSpec(
        "Property All Risk", "property_sum_insured_cr", 0.52, 0.55,
        ("Property Risk", "ESG & Climate Risk", "Liability Risk"),
    ),
    # rate 0.22 → effective ~0.25% of BI SI; Trust Risk Control Jan 2025 standardisation
    "business_interruption": CoverSpec(
        "Business Interruption", "gross_profit_si_cr", 0.22, 0.25,
        ("Property Risk", "Liability Risk", "Reputation Risk"),
    ),
    # rate 0.18 → effective ~0.20% of stock; market 0.18–0.25%
    "burglary": CoverSpec(
        "Burglary", "stock_sum_insured_cr", 0.18, 0.15,
        ("Property Risk", "Gig & Labour Risk"),
    ),
    # rate 0.80 → effective ~0.91% of equipment value; ex-tariff 1.25% (WTIB); market 0.8–1.2%
    "electronic_equipment": CoverSpec(
        "Electronic Equipment", "equipment_sum_insured_cr", 0.80, 0.50,
        ("Property Risk", "Cyber Technical Risk"),
    ),
    # rate 0.55 → effective ~0.62% of plant value; HDFC ERGO / Liberty General range
    "machinery_breakdown": CoverSpec(
        "Machinery Breakdown", "equipment_sum_insured_cr", 0.55, 0.40,
        ("Property Risk", "ESG & Climate Risk"),
    ),
    # rate 0.40 → effective ~0.45% of payroll; IRDAI WC office class ~0.5%
    "employees_comp": CoverSpec(
        "Employees Compensation", "payroll_cr", 0.40, 0.30,
        ("Gig & Labour Risk", "Liability Risk", "Regulatory Compliance Risk"),
    ),
    # rate 0.13 lakh/employee → effective ~₹14,700/emp at mid-loading; NivaaBupa/Pazcare ₹10–25K
    "employee_health": CoverSpec(
        "Group Health", "employee_count", 0.13, 1.20,
        ("Key Person Risk", "Gig & Labour Risk"),
        pricing_unit="per_employee",
    ),
    # rate 0.09 lakh/employee → effective ~₹10,200/emp at mid-loading; Bajaj Finserv ₹8–15K
    "group_pa": CoverSpec(
        "Group Personal Accident", "employee_count", 0.09, 0.50,
        ("Gig & Labour Risk", "Key Person Risk"),
        pricing_unit="per_employee",
    ),
    # rate 0.40 → effective ~0.45% of cargo turnover; Pazago domestic marine 0.3–0.8%
    "marine_transit": CoverSpec(
        "Marine Cargo", "cargo_turnover_cr", 0.40, 0.35,
        ("Geopolitical Risk", "Property Risk", "Reputation Risk"),
    ),
    # rate 0.40 → effective ~0.45% of receivables; Allianz Trade 0.1–0.4% of sales
    "trade_credit": CoverSpec(
        "Trade Credit", "receivables_on_credit_cr", 0.40, 0.45,
        ("Governance & Fraud Risk", "Geopolitical Risk", "Reputation Risk"),
    ),
    # rate 0.22 → effective ~0.25% of project value; Riskbirbal CAR/EAR 0.1–0.5%
    "engineering": CoverSpec(
        "Engineering CAR / EAR", "project_value_cr", 0.22, 0.55,
        ("Property Risk", "Liability Risk", "ESG & Climate Risk"),
    ),
    # rate 0.45 → effective ~0.51% of bond value; IRDAI Surety Guidelines 2022
    "surety": CoverSpec(
        "Surety", "project_value_cr", 0.45, 0.65,
        ("Governance & Fraud Risk", "Regulatory Compliance Risk"),
    ),
    # rate 0.22; emerging product in India — limited market data
    "parametric": CoverSpec(
        "Climate Parametric", "weather_exposed_si_cr", 0.22, 0.35,
        ("ESG & Climate Risk", "Property Risk", "Geopolitical Risk"),
    ),
    # rate 0.35; market estimate — no change
    "money_insurance": CoverSpec(
        "Money Insurance", "cash_limit_cr", 0.35, 0.08,
        ("Governance & Fraud Risk", "Property Risk"),
    ),
    # rate 0.35; market estimate — no change
    "crime_fidelity": CoverSpec(
        "Crime / Fidelity", "crime_limit_cr", 0.35, 0.30,
        ("Governance & Fraud Risk", "Cyber Technical Risk"),
    ),
    # rate 0.42; limited public market data — no change
    "drone_insurance": CoverSpec(
        "Drone RPAS", "drone_hull_si_cr", 0.42, 0.30,
        ("Liability Risk", "Property Risk", "Regulatory Compliance Risk"),
    ),
    "motor_fleet": CoverSpec(
        "Commercial Motor Fleet", "fleet_count", 0.18, 0.50,
        ("Liability Risk", "Property Risk", "Gig & Labour Risk"),
        pricing_unit="per_vehicle",
    ),
    "healthcare_pi": CoverSpec(
        "Healthcare / Medical Professional Liability", "healthcare_pi_limit_cr", 0.95, 1.25,
        ("Liability Risk", "Regulatory Compliance Risk", "Reputation Risk"),
    ),
    "financial_services_pi": CoverSpec(
        "Financial Services Professional Indemnity", "fi_pi_limit_cr", 1.05, 1.50,
        ("Liability Risk", "Governance & Fraud Risk", "Regulatory Compliance Risk"),
    ),
    "payment_protection": CoverSpec(
        "Payment / Card Protection", "payment_protection_limit_cr", 0.65, 0.80,
        ("Cyber Technical Risk", "Governance & Fraud Risk", "Data Privacy Risk"),
    ),
    "product_recall": CoverSpec(
        "Product Recall / Contamination", "recall_limit_cr", 0.85, 1.00,
        ("Liability Risk", "Reputation Risk", "Regulatory Compliance Risk"),
    ),
    "event_production": CoverSpec(
        "Entertainment Production Package", "production_budget_cr", 0.60, 0.60,
        ("Liability Risk", "Reputation Risk", "Property Risk"),
    ),
    # rate 0.45 → effective ~0.51% of limit; emerging EPLI market in India (Marsh/AON EPL data 2025)
    "employment_practices": CoverSpec(
        "Employment Practices Liability", "pi_limit_cr", 0.45, 1.00,
        ("Gig & Labour Risk", "Governance & Fraud Risk", "Reputation Risk"),
    ),
}

INPUT_FIELD_LABELS = {
    "property_sum_insured_cr": ("Property sum insured", "INR Cr", "Building, fitout, stock, and other insurable property value."),
    "total_insurable_asset_value_cr": ("Total insurable asset value", "INR Cr", "Total building, fitout, stock, equipment, and other insured property value."),
    "asset_value_inr": ("Property asset value", "INR", "Alternative to property SI if available in rupees."),
    "stock_sum_insured_cr": ("Stock sum insured", "INR Cr", "Inventory value to insure against fire/theft."),
    "equipment_sum_insured_cr": ("Equipment sum insured", "INR Cr", "Electronics, machinery, lab, server, or plant equipment value."),
    "gross_profit_si_cr": ("Gross profit / BI sum insured", "INR Cr", "Gross profit or standing charges basis for business interruption."),
    "cyber_limit_cr": ("Cyber limit", "INR Cr", "Cyber liability limit requested."),
    "dno_limit_cr": ("D&O limit", "INR Cr", "Directors and officers liability limit requested."),
    "pi_limit_cr": ("Professional indemnity limit", "INR Cr", "E&O / PI limit requested."),
    "public_liability_limit_cr": ("Public liability limit", "INR Cr", "Third-party bodily injury/property damage limit."),
    "product_liability_limit_cr": ("Product liability limit", "INR Cr", "Physical product liability limit."),
    "payroll_cr": ("Annual payroll", "INR Cr", "Annual payroll/wage roll for employees compensation."),
    "cargo_annual_turnover_cr": ("Annual cargo turnover", "INR Cr", "Annual value of goods moved domestically or internationally."),
    "receivables_on_credit_cr": ("Receivables on credit", "INR Cr", "Outstanding B2B receivables under credit terms."),
    "project_value_cr": ("Project value", "INR Cr", "Contract/project value for engineering or surety covers."),
    "weather_exposed_si_cr": ("Weather-exposed value", "INR Cr", "Assets or revenue exposed to parametric weather events."),
    "cash_limit_cr": ("Cash limit", "INR Cr", "Cash-in-safe/transit limit."),
    "crime_limit_cr": ("Crime / fidelity limit", "INR Cr", "Employee dishonesty/social engineering limit."),
    "drone_hull_si_cr": ("Drone hull SI", "INR Cr", "Drone hull/equipment value."),
    "fleet_count": ("Fleet count", "vehicles", "Owned or operated commercial vehicles, delivery two-wheelers, trailers, or field-service vehicles."),
    "healthcare_pi_limit_cr": ("Healthcare PI limit", "INR Cr", "Medical professional liability limit requested."),
    "fi_pi_limit_cr": ("FI PI limit", "INR Cr", "Financial institution professional indemnity limit requested."),
    "payment_protection_limit_cr": ("Payment protection limit", "INR Cr", "Card/payment protection or unauthorised transaction limit."),
    "recall_limit_cr": ("Recall / contamination limit", "INR Cr", "Product recall, contamination, and brand rehabilitation limit."),
    "production_budget_cr": ("Production budget", "INR Cr", "Insurable event/production budget or equipment-at-risk value."),
    "employment_practices_limit_cr": ("EPL limit", "INR Cr", "Employment practices liability limit - wrongful termination, harassment, discrimination claims."),
    "employee_count": ("Employee count", "count", "Employees to be covered."),
    "team_size": ("Team size", "count", "Existing intake team size used for employee covers."),
    "annual_revenue_cr": ("Annual revenue", "INR Cr", "Annual revenue / ARR — scales Cyber and PI/Tech E&O premium."),
    "data_records_lakhs": ("Data records", "lakhs", "Customer/user records held in lakhs (1 lakh = 100,000). Drives Cyber exposure."),
    "claims_last_3_years": ("Prior claims", "yes/no", "Any insurance claims filed in the last 3 years? Adds a loading if yes."),
}


REQUIRED_INPUTS_BY_COVER = {
    "cyber_liability": (
        ("cyber_limit_cr",),
        ("annual_revenue_cr", "revenue_cr"),
        ("data_records_lakhs",),
        ("claims_last_3_years",),
    ),
    "dno_liability": (
        ("dno_limit_cr",),
        ("claims_last_3_years",),
    ),
    "professional_indemnity": (
        ("pi_limit_cr", "professional_indemnity_limit_cr"),
        ("annual_revenue_cr", "revenue_cr"),
        ("claims_last_3_years",),
    ),
    "crime_fidelity": (
        ("crime_limit_cr",),
        ("claims_last_3_years",),
    ),
    "comprehensive_general_liability": (("public_liability_limit_cr",),),
    "public_liability": (("public_liability_limit_cr",),),
    "product_liability": (("product_liability_limit_cr",),),
    "property_fire": (("property_sum_insured_cr", "total_insurable_asset_value_cr", "asset_value_inr"),),
    "property_all_risk": (("property_sum_insured_cr", "total_insurable_asset_value_cr", "asset_value_inr"),),
    "business_interruption": (("gross_profit_si_cr", "gross_profit_cr"),),
    "burglary": (("stock_sum_insured_cr",),),
    "electronic_equipment": (("equipment_sum_insured_cr",),),
    "machinery_breakdown": (("equipment_sum_insured_cr",),),
    "employees_comp": (("payroll_cr",),),
    "employee_health": (("employee_count", "team_size", "headcount_total"),),
    "group_pa": (("employee_count", "team_size", "headcount_total"),),
    "marine_transit": (("cargo_annual_turnover_cr", "cargo_turnover_cr"),),
    "trade_credit": (("receivables_on_credit_cr",),),
    "engineering": (("project_value_cr", "capex_project_value_cr"),),
    "surety": (("project_value_cr", "capex_project_value_cr"),),
    "parametric": (("weather_exposed_si_cr",),),
    "money_insurance": (("cash_limit_cr",),),
    "drone_insurance": (("drone_hull_si_cr",),),
    "motor_fleet": (("fleet_count",),),
    "healthcare_pi": (("healthcare_pi_limit_cr",), ("claims_last_3_years",)),
    "financial_services_pi": (("fi_pi_limit_cr",), ("annual_revenue_cr", "revenue_cr"), ("claims_last_3_years",)),
    "payment_protection": (("payment_protection_limit_cr",), ("annual_revenue_cr", "revenue_cr"), ("claims_last_3_years",)),
    "product_recall": (("recall_limit_cr",), ("annual_revenue_cr", "revenue_cr"), ("claims_last_3_years",)),
    "event_production": (("production_budget_cr",), ("claims_last_3_years",)),
    "employment_practices": (("pi_limit_cr", "employment_practices_limit_cr"), ("claims_last_3_years",)),
}


def _float(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _positive(value: Any) -> Optional[float]:
    number = _float(value)
    return number if number > 0 else None


def _asset_value_in_cr(profile: Dict[str, Any]) -> Optional[float]:
    explicit = _explicit_cr(profile, "total_insurable_asset_value_cr", "property_sum_insured_cr")
    if explicit is not None:
        return explicit
    for key in ("asset_value_inr", "total_asset_value_inr", "sum_insured_inr"):
        value = _positive(profile.get(key))
        if value is not None:
            return value / CRORE_INR
    return None


def _explicit_cr(profile: Dict[str, Any], *keys: str) -> Optional[float]:
    for key in keys:
        value = _positive(profile.get(key))
        if value is not None:
            return value
    return None


def _stage(profile: Dict[str, Any]) -> str:
    return str(profile.get("funding_stage") or profile.get("stage") or "Seed")


def _team_size(profile: Dict[str, Any]) -> int:
    return max(1, int(_float(profile.get("team_size") or profile.get("headcount_total"), 10)))


def _has_any(items: Iterable[str], *needles: str) -> bool:
    item_set = set(items or [])
    return any(needle in item_set for needle in needles)


def _infer_property_si(profile: Dict[str, Any]) -> tuple[float, List[str]]:
    explicit = _explicit_cr(profile, "property_sum_insured_cr", "total_insurable_asset_value_cr")
    asset_inr = _asset_value_in_cr(profile)
    if explicit is not None:
        return explicit, ["Property SI taken from property_sum_insured_cr."]
    if asset_inr is not None:
        return asset_inr, ["Property SI taken from asset_value_inr."]

    stage_base = {"Pre-seed": 0.50, "Seed": 1.50, "Series A": 6.00, "Series B+": 20.00}
    assets = profile.get("physical_assets") or []
    inferred = stage_base.get(_stage(profile), 1.50)
    asset_notes = []
    asset_adders = {
        "Office / coworking space": (0.50, "office/coworking fitout"),
        "Warehouse / fulfilment centre": (2.00, "warehouse and stock concentration"),
        "Manufacturing plant / factory": (8.00, "manufacturing plant"),
        "Lab / R&D equipment": (3.00, "lab/R&D equipment"),
        "Medical devices / diagnostic equipment": (3.00, "medical/diagnostic equipment"),
        "Vehicles / delivery fleet": (1.00, "fleet assets"),
        "Drones / UAV equipment": (1.00, "drone hardware"),
        "Kitchen / food processing": (1.50, "kitchen/processing assets"),
        "Cold chain / refrigeration": (2.00, "cold-chain equipment"),
        "Solar / clean energy infrastructure": (6.00, "clean-energy infrastructure"),
        "Retail stores / kiosks": (1.00, "retail/kiosk fitout"),
        "Data centre / server room": (2.50, "server room equipment"),
    }
    for asset in assets:
        add, note = asset_adders.get(asset, (0.0, ""))
        inferred += add
        if note:
            asset_notes.append(note)

    hardware_split = _float(profile.get("hardware_software_split"))
    if hardware_split > 0:
        inferred *= 1.0 + min(hardware_split, 1.0) * 0.35
    if not assets or "None - fully cloud" in assets:
        inferred = min(inferred, 1.0)

    notes = [f"Property SI inferred from stage, team size, and physical assets ({', '.join(asset_notes) or 'asset-light profile'})."]
    return round(max(0.25, inferred), 2), notes


def infer_underwriting_inputs(profile: Dict[str, Any]) -> Dict[str, Any]:
    property_si, notes = _infer_property_si(profile)
    stage = _stage(profile)
    team = _team_size(profile)
    # Bug fix: read explicit employee_count before falling back to team_size/headcount_total.
    # REQUIRED_INPUTS_BY_COVER lists employee_count as a valid alias; it must be honoured.
    employee_count = max(1, int(_float(
        profile.get("employee_count") or profile.get("team_size") or profile.get("headcount_total"),
        10,
    )))
    sector = str(profile.get("sector") or "")
    data_sensitivity = str(profile.get("data_sensitivity") or "Medium")
    physical_assets = profile.get("physical_assets") or []
    data_handled = profile.get("data_handled") or []

    revenue_base = {"Pre-seed": 0.75, "Seed": 3.0, "Series A": 20.0, "Series B+": 100.0}
    annual_revenue = _explicit_cr(profile, "annual_revenue_cr", "revenue_cr") or revenue_base.get(stage, 3.0)
    annual_revenue *= max(1.0, team / 50.0)

    cyber_base = {"Pre-seed": 1.0, "Seed": 2.0, "Series A": 5.0, "Series B+": 20.0}.get(stage, 2.0)
    if data_sensitivity == "High":
        cyber_base *= 1.5
    if sector in ("Fintech", "Healthtech"):
        cyber_base *= 1.3

    dno_base = {"Pre-seed": 1.0, "Seed": 2.0, "Series A": 5.0, "Series B+": 25.0}.get(stage, 2.0)
    if profile.get("has_investors") == "Yes":
        dno_base *= 1.2

    pi_base = {"Pre-seed": 1.0, "Seed": 2.0, "Series A": 5.0, "Series B+": 15.0}.get(stage, 2.0)
    pi_base *= 1.0 + min(1.0, _float(profile.get("b2b_pct"), 0.5)) * 0.25

    stock_default = property_si * 0.35 if _has_any(
        physical_assets,
        "Warehouse / fulfilment centre", "Retail stores / kiosks", "Kitchen / food processing",
    ) or "Physical inventory / goods" in data_handled else property_si * 0.12
    equipment_default = property_si * 0.45 if _has_any(
        physical_assets,
        "Manufacturing plant / factory", "Lab / R&D equipment", "Solar / clean energy infrastructure",
        "Data centre / server room", "Medical devices / diagnostic equipment",
    ) else property_si * 0.18

    export_share = _float(profile.get("export_eu_pct")) + _float(profile.get("export_us_pct")) + _float(profile.get("export_china_pct"))
    has_trade = "Physical inventory / goods" in data_handled or export_share > 0 or _has_any(physical_assets, "Warehouse / fulfilment centre")
    cargo_turnover = annual_revenue * (0.55 if has_trade else 0.10) * (1.0 + min(export_share, 1.0) * 0.5)
    receivables = annual_revenue * max(0.10, min(1.0, _float(profile.get("b2b_pct"), 0.5))) * 0.18
    project_value = property_si * (1.7 if _has_any(physical_assets, "Manufacturing plant / factory", "Solar / clean energy infrastructure") else 0.5)
    fleet_count = int(_float(profile.get("fleet_count"), 0))
    if fleet_count <= 0 and _has_any(physical_assets, "Vehicles / delivery fleet"):
        fleet_count = max(3, int(team * max(0.1, _float(profile.get("gig_headcount_pct"), 0.2))))
    healthcare_limit = max(1.0, annual_revenue * 0.20)
    fi_limit = max(2.0, annual_revenue * 0.25)
    payment_limit = max(1.0, annual_revenue * 0.12)
    recall_limit = max(1.0, annual_revenue * 0.20)
    production_budget = max(0.5, annual_revenue * 0.15)
    if stage in ("Pre-seed", "Seed"):
        gross_profit_default = max(0.25, annual_revenue * 0.25)
    elif stage == "Series A":
        gross_profit_default = max(0.50, annual_revenue * 0.30)
    else:
        gross_profit_default = max(1.00, annual_revenue * 0.35)

    inputs = {
        "property_sum_insured_cr": _explicit_cr(profile, "property_sum_insured_cr") or property_si,
        "stock_sum_insured_cr": _explicit_cr(profile, "stock_sum_insured_cr") or round(max(0.10, stock_default), 2),
        "equipment_sum_insured_cr": _explicit_cr(profile, "equipment_sum_insured_cr") or round(max(0.10, equipment_default), 2),
        "gross_profit_si_cr": _explicit_cr(profile, "gross_profit_si_cr", "gross_profit_cr") or round(gross_profit_default, 2),
        "cyber_limit_cr": _explicit_cr(profile, "cyber_limit_cr") or round(cyber_base, 2),
        "dno_limit_cr": _explicit_cr(profile, "dno_limit_cr") or round(dno_base, 2),
        "pi_limit_cr": _explicit_cr(profile, "pi_limit_cr", "professional_indemnity_limit_cr") or round(pi_base, 2),
        "public_liability_limit_cr": _explicit_cr(profile, "public_liability_limit_cr") or round(max(1.0, property_si * 0.75), 2),
        "product_liability_limit_cr": _explicit_cr(profile, "product_liability_limit_cr") or round(max(1.0, annual_revenue * 0.20), 2),
        "payroll_cr": _explicit_cr(profile, "payroll_cr") or round(max(0.25, team * 0.12), 2),
        "employee_count": employee_count,
        "cargo_turnover_cr": _explicit_cr(profile, "cargo_annual_turnover_cr", "cargo_turnover_cr") or round(max(0.25, cargo_turnover), 2),
        "receivables_on_credit_cr": _explicit_cr(profile, "receivables_on_credit_cr") or round(max(0.25, receivables), 2),
        "project_value_cr": _explicit_cr(profile, "project_value_cr", "capex_project_value_cr") or round(max(0.50, project_value), 2),
        "weather_exposed_si_cr": _explicit_cr(profile, "weather_exposed_si_cr") or round(max(0.50, property_si + stock_default), 2),
        "cash_limit_cr": _explicit_cr(profile, "cash_limit_cr") or 0.10,
        "crime_limit_cr": _explicit_cr(profile, "crime_limit_cr") or round(max(0.50, annual_revenue * 0.10), 2),
        "drone_hull_si_cr": _explicit_cr(profile, "drone_hull_si_cr") or (1.00 if _has_any(physical_assets, "Drones / UAV equipment") else 0.25),
        "fleet_count": int(_explicit_cr(profile, "fleet_count") or fleet_count or 1),
        "healthcare_pi_limit_cr": _explicit_cr(profile, "healthcare_pi_limit_cr") or round(healthcare_limit, 2),
        "fi_pi_limit_cr": _explicit_cr(profile, "fi_pi_limit_cr") or round(fi_limit, 2),
        "payment_protection_limit_cr": _explicit_cr(profile, "payment_protection_limit_cr") or round(payment_limit, 2),
        "recall_limit_cr": _explicit_cr(profile, "recall_limit_cr") or round(recall_limit, 2),
        "production_budget_cr": _explicit_cr(profile, "production_budget_cr") or round(production_budget, 2),
        "employment_practices_limit_cr": _explicit_cr(profile, "employment_practices_limit_cr", "epli_limit_cr") or round(max(1.0, annual_revenue * 0.15), 2),
        "_assumption_notes": notes,
    }
    return inputs


def normalize_cover_key(key: Any) -> Optional[str]:
    if key is None:
        return None
    text = str(key).strip()
    if not text:
        return None
    return COVER_ALIASES.get(text) or COVER_ALIASES.get(text.lower()) or text.lower()


def _select_covers(
    recommendations: List[Dict[str, Any]],
    bundle: Optional[Dict[str, Any]],
    max_covers: int = 8,
) -> List[str]:
    # Accumulate raw keys in priority order; deduplication and cap applied after normalization.
    raw: List[str] = []
    for key in (bundle or {}).get("mandatory_covers", []):
        raw.append(key)
    for key in (bundle or {}).get("optional_covers", []):
        raw.append(key)
    for product in recommendations or []:
        raw.append(product.get("key"))

    # Normalise, deduplicate, and enforce the cap across the full combined list.
    normalized: List[str] = []
    seen: set = set()
    for key in raw:
        if len(normalized) >= max_covers:
            break
        cover = normalize_cover_key(key)
        if cover in COVER_SPECS and cover not in seen:
            normalized.append(cover)
            seen.add(cover)
    if "business_interruption" in normalized:
        has_property = any(c in normalized for c in ("property_fire", "property_all_risk"))
        if not has_property and "property_fire" not in seen:
            normalized.insert(normalized.index("business_interruption"), "property_fire")
            seen.add("property_fire")
    return normalized


def _avg_risk(scores: Dict[str, Any], keys: Iterable[str]) -> float:
    values = [_float(scores.get(key), 0.0) for key in keys if key in scores]
    if not values:
        return 45.0
    return sum(values) / len(values)


def _stage_loading(stage: str) -> float:
    return {
        "Pre-seed": 0.90,
        "Seed": 1.00,
        "Series A": 1.12,
        "Series B+": 1.28,
    }.get(stage, 1.00)


def _sector_loading(cover: str, profile: Dict[str, Any]) -> float:
    sector = profile.get("sector")
    if cover == "cyber_liability" and sector in ("Fintech", "Healthtech"):
        return 1.20
    if cover in ("property_fire", "property_all_risk", "business_interruption") and sector in (
        "D2C / Consumer Brands", "Logistics / Mobility", "Foodtech / Cloud Kitchen", "Cleantech / Climatetech",
    ):
        return 1.15
    if cover == "product_liability" and sector in ("D2C / Consumer Brands", "Healthtech", "Deeptech / AI / Robotics"):
        return 1.20
    if cover in ("engineering", "surety") and sector in ("Cleantech / Climatetech", "Deeptech / AI / Robotics"):
        return 1.15
    if cover == "motor_fleet" and sector in ("Logistics / Mobility", "D2C / Consumer Brands", "Foodtech / Cloud Kitchen"):
        return 1.15
    if cover == "healthcare_pi" and sector == "Healthtech":
        return 1.20
    if cover in ("financial_services_pi", "payment_protection") and sector == "Fintech":
        return 1.25
    if cover == "product_recall" and sector in ("D2C / Consumer Brands", "Foodtech / Cloud Kitchen", "Healthtech"):
        return 1.20
    if cover == "event_production" and sector == "Gaming / Media / Content":
        return 1.20
    return 1.00


def _control_loading(cover: str, profile: Dict[str, Any]) -> float:
    loading = 1.0
    if cover == "cyber_liability" and profile.get("cert_in_poc_designated"):
        loading *= 0.92
    if cover in ("employees_comp", "employee_health", "group_pa") and profile.get("posh_ic_constituted"):
        loading *= 0.97
    if profile.get("data_localisation_status") == "Full_onshore" and cover == "cyber_liability":
        loading *= 0.96
    return loading


def _climate_loading(cover: str, profile: Dict[str, Any]) -> float:
    if cover not in ("property_fire", "property_all_risk", "business_interruption", "parametric", "marine_transit"):
        return 1.0
    return {
        "Low": 1.00,
        "Medium": 1.08,
        "High": 1.18,
        "Extreme": 1.32,
        "Very High": 1.32,
    }.get(profile.get("facility_climate_risk_zone"), 1.00)


def _claims_loading(profile: Dict[str, Any]) -> float:
    raw = profile.get("claims_last_3_years")
    # Intake may pass a boolean (True/False) or a string ("Yes"/"1"); treat those as 1 claim.
    if isinstance(raw, bool):
        claims = 1.0 if raw else 0.0
    elif isinstance(raw, str):
        claims = 1.0 if raw.strip().lower() in ("yes", "true", "1") else _float(raw, 0.0)
    else:
        claims = max(0.0, _float(raw, 0.0))
    return min(1.75, 1.0 + claims * 0.15)


def _risk_loading(avg_risk: float) -> float:
    return round(0.75 + (max(0.0, min(avg_risk, 100.0)) / 100.0) * 0.85, 3)


def _revenue_loading(cover: str, profile: Dict[str, Any]) -> float:
    """Scale Cyber and PI premiums by annual revenue band.
    Sub-5Cr startups get a slight discount; 50Cr+ attract up to +20%.
    Only applies when annual_revenue_cr is explicitly provided."""
    if cover not in (
        "cyber_liability", "professional_indemnity", "financial_services_pi",
        "payment_protection", "healthcare_pi", "product_recall",
    ):
        return 1.0
    revenue = _explicit_cr(profile, "annual_revenue_cr", "revenue_cr")
    if revenue is None:
        return 1.0
    if revenue < 5:
        return 0.92
    if revenue < 20:
        return 1.00
    if revenue < 50:
        return 1.08
    if revenue < 100:
        return 1.15
    return 1.20


def _records_loading(cover: str, profile: Dict[str, Any]) -> float:
    """Scale Cyber premium by data records held (in lakhs).
    10M+ records (100 lakhs) is the DPDP significant-data-fiduciary threshold."""
    if cover != "cyber_liability":
        return 1.0
    records = _float(profile.get("data_records_lakhs"), 0)
    if records <= 0:
        return 1.0
    if records < 1:
        return 0.95
    if records < 10:
        return 1.00
    if records < 50:
        return 1.10
    if records < 100:
        return 1.20
    return 1.30


def _price_cover(
    cover_key: str,
    spec: CoverSpec,
    inputs: Dict[str, Any],
    scores: Dict[str, Any],
    profile: Dict[str, Any],
) -> Dict[str, Any]:
    exposure = _float(inputs.get(spec.exposure_field), 0.0)
    avg_risk = _avg_risk(scores, spec.risk_keys)
    loadings = {
        "risk": _risk_loading(avg_risk),
        "stage": _stage_loading(_stage(profile)),
        "sector": _sector_loading(cover_key, profile),
        "climate": _climate_loading(cover_key, profile),
        "controls": _control_loading(cover_key, profile),
        "claims": _claims_loading(profile),
        "revenue": _revenue_loading(cover_key, profile),
        "records": _records_loading(cover_key, profile),
    }
    raw_combined = 1.0
    for value in loadings.values():
        raw_combined *= value
    # Cap prevents pathological compounding (theoretical max without cap ≈ 7×).
    cap_applied = raw_combined > MAX_COMBINED_LOADING
    combined_loading = min(raw_combined, MAX_COMBINED_LOADING)

    if spec.pricing_unit == "per_employee":
        technical = exposure * spec.rate_lakh_per_cr * combined_loading
        exposure_label = f"{int(exposure)} employees"
        # per_employee covers have no sum-insured denomination; intentionally 0 so
        # they don't inflate the aggregate SI used in underwriter referral checks.
        sum_insured_cr = 0.0
    elif spec.pricing_unit == "per_vehicle":
        technical = exposure * spec.rate_lakh_per_cr * combined_loading
        exposure_label = f"{int(exposure)} vehicles"
        sum_insured_cr = 0.0
    else:
        technical = exposure * spec.rate_lakh_per_cr * combined_loading
        exposure_label = f"INR {exposure:.2f} Cr"
        sum_insured_cr = exposure

    if cover_key == "dno_liability" and _stage(profile) in ("Series A", "Series B+"):
        spec_min = max(spec.min_lakh, 2.50)
    else:
        spec_min = spec.min_lakh
    premium_lakh = round(max(spec_min, technical), 2)
    return {
        "cover_key": cover_key,
        "cover_name": spec.label,
        "exposure_field": spec.exposure_field,
        "exposure_value": round(exposure, 2),
        "exposure_label": exposure_label,
        "sum_insured_cr": round(sum_insured_cr, 2),
        "base_rate_lakh_per_cr": spec.rate_lakh_per_cr,
        "average_risk_score": round(avg_risk, 1),
        "loadings": {key: round(value, 3) for key, value in loadings.items()},
        "raw_combined_loading": round(raw_combined, 3),
        "loading_cap_applied": cap_applied,
        "premium_lakh": premium_lakh,
        "basis": f"{spec.label}: {exposure_label} x base rate {spec.rate_lakh_per_cr:.3f}L/unit x loadings.",
    }


def _missing_inputs(profile: Dict[str, Any], covers: List[str]) -> List[str]:
    prompts = []
    if any(c in covers for c in ("property_fire", "property_all_risk", "business_interruption", "burglary")):
        if _asset_value_in_cr(profile) is None and _explicit_cr(profile, "property_sum_insured_cr") is None:
            prompts.append("Confirm property/stock/equipment sum insured for a bindable quote.")
    if "cyber_liability" in covers and _explicit_cr(profile, "cyber_limit_cr") is None:
        prompts.append("Confirm cyber policy limit and deductible preference.")
    if "dno_liability" in covers and _explicit_cr(profile, "dno_limit_cr") is None:
        prompts.append("Confirm D&O limit, latest fundraise amount, and investor board rights.")
    if "professional_indemnity" in covers and _explicit_cr(profile, "pi_limit_cr") is None:
        prompts.append("Confirm professional indemnity limit and largest customer contract value.")
    if any(c in covers for c in ("marine_transit", "trade_credit")):
        prompts.append("Confirm annual transit turnover, top buyer concentration, and credit terms.")
    if any(c in covers for c in ("engineering", "surety")):
        prompts.append("Confirm project value, contract period, and defect liability period.")
    if "motor_fleet" in covers:
        prompts.append("Confirm vehicle count, vehicle classes, driver controls, and claims history.")
    if "healthcare_pi" in covers:
        prompts.append("Confirm clinical services, practitioner credentials, patient volume, and prior malpractice claims.")
    if any(c in covers for c in ("financial_services_pi", "payment_protection")):
        prompts.append("Confirm licence type, transaction volume, fraud controls, and customer compensation obligations.")
    if "product_recall" in covers:
        prompts.append("Confirm batch volumes, recall plan, quality controls, and prior recall/contamination events.")
    if "event_production" in covers:
        prompts.append("Confirm production budget, venue controls, cast/equipment schedule, and cancellation exposure.")
    return prompts


def _input_present(profile: Dict[str, Any], aliases: Iterable[str]) -> bool:
    for alias in aliases:
        if alias == "claims_last_3_years" and alias in profile:
            return True
        val = profile.get(alias)
        if isinstance(val, bool):
            return True  # False is a valid explicit answer (e.g. claims_last_3_years=False)
        if _positive(val) is not None:
            return True
    return False


def _required_input_specs(profile: Dict[str, Any], covers: List[str]) -> List[Dict[str, Any]]:
    """Return deduplicated user inputs required to quote the selected covers."""
    rows: List[Dict[str, Any]] = []
    seen = set()
    for cover in covers:
        for aliases in REQUIRED_INPUTS_BY_COVER.get(cover, ()):
            key = aliases[0]
            if key in seen:
                continue
            seen.add(key)
            label, unit, help_text = INPUT_FIELD_LABELS.get(key, (key.replace("_", " ").title(), "", ""))
            rows.append({
                "key": key,
                "aliases": list(aliases),
                "label": label,
                "unit": unit,
                "help": help_text,
                "required_for": cover,
                "provided": _input_present(profile, aliases),
            })
    return rows


def _missing_required_inputs(profile: Dict[str, Any], covers: List[str]) -> List[Dict[str, Any]]:
    return [row for row in _required_input_specs(profile, covers) if not row["provided"]]


def pricing_input_request(
    profile: Dict[str, Any],
    recommendations: Optional[List[Dict[str, Any]]] = None,
    bundle: Optional[Dict[str, Any]] = None,
    status: str = "not_requested",
) -> Dict[str, Any]:
    recommendations = recommendations or []
    covers = _select_covers(recommendations, bundle)
    return {
        "engine_version": ENGINE_VERSION,
        "quote_type": "input_required",
        "status": status,
        "currency": "INR",
        "bundle_name": (bundle or {}).get("name"),
        "covers_to_price": [
            {"cover_key": cover, "cover_name": COVER_SPECS[cover].label}
            for cover in covers
        ],
        "required_inputs": _required_input_specs(profile, covers),
        "missing_required_inputs": _missing_required_inputs(profile, covers),
        "message": "Quote is not calculated automatically. Confirm the underwriting inputs to generate an estimated quote.",
    }


def _referral_flags(
    profile: Dict[str, Any],
    scores: Dict[str, Any],
    inputs: Dict[str, Any],
    covers: List[str],
) -> List[str]:
    flags = []
    aggregate_si = sum(_float(inputs.get(field)) for field in (
        "property_sum_insured_cr", "stock_sum_insured_cr", "equipment_sum_insured_cr",
        "cyber_limit_cr", "dno_limit_cr", "pi_limit_cr", "public_liability_limit_cr",
    ))
    if aggregate_si > 50:
        flags.append("Aggregate selected SI exceeds INR 50 Cr; route to underwriter approval.")
    if "cyber_liability" in covers and _float(scores.get("Cyber Technical Risk")) >= 85:
        flags.append("Cyber risk score is 85+; require control questionnaire before firm pricing.")
    if "cyber_liability" in covers and _float(profile.get("data_records_lakhs"), 0) >= 100:
        flags.append("Data records exceed 10M (100 lakhs); DPDP significant-data-fiduciary rules apply — confirm compliance documentation.")
    if any(c in covers for c in ("property_fire", "property_all_risk")) and _float(inputs.get("property_sum_insured_cr")) > 25:
        flags.append("Property SI exceeds INR 25 Cr; validate occupancy, protection, and catastrophe exposure.")
    if profile.get("facility_climate_risk_zone") in ("High", "Extreme", "Very High"):
        flags.append("High climate zone; check flood/cyclone exposure and deductibles.")
    if profile.get("claims_last_3_years"):
        flags.append("Prior claims disclosed; validate loss runs before binding.")
    if "motor_fleet" in covers and _float(inputs.get("fleet_count")) >= 50:
        flags.append("Fleet count is 50+; validate driver vetting, telematics, route controls, and motor loss history.")
    if "healthcare_pi" in covers and profile.get("healthcare_operations"):
        flags.append("Healthcare operations disclosed; require practitioner credential and incident history before firm pricing.")
    if any(c in covers for c in ("financial_services_pi", "payment_protection")) and profile.get("rbi_registration"):
        flags.append("Regulated financial-services exposure; confirm licence scope, outsourcing controls, and regulator correspondence.")
    if "product_recall" in covers and profile.get("product_recall_exposure"):
        flags.append("Recall/contamination exposure disclosed; require QA controls, traceability, and recall plan.")
    if "surety" in covers and profile.get("contract_bid_or_performance_bond_need"):
        flags.append("Surety need disclosed; route to surety underwriter for financial strength and contract wording review.")
    if "event_production" in covers and profile.get("event_or_production_operations"):
        flags.append("Production/event exposure disclosed; validate venue, cancellation, cast, and equipment schedule.")
    sector = profile.get("sector", "")
    for cover in covers:
        appetite = get_appetite(cover, sector)
        if appetite == "bad":
            reason = BAD_RISK_REASONS_SHORT.get(cover, {}).get(sector, "")
            label = COVER_SPECS[cover].label if cover in COVER_SPECS else cover
            flags.append(
                f"{label}: adverse underwriting appetite for {sector} - refer to underwriter "
                f"before presenting quote. {reason}"
            )
    return flags


def price_output_stage(
    profile: Dict[str, Any],
    scores: Dict[str, Any],
    recommendations: Optional[List[Dict[str, Any]]] = None,
    bundle: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Return an auditable quote for the current recommendation output."""
    recommendations = recommendations or []
    covers = _select_covers(recommendations, bundle)

    if not profile.get("quote_requested"):
        return pricing_input_request(profile, recommendations, bundle, "not_requested")

    missing_required = _missing_required_inputs(profile, covers)
    if missing_required:
        return pricing_input_request(profile, recommendations, bundle, "awaiting_inputs")

    inputs = infer_underwriting_inputs(profile)
    priced = [
        _price_cover(cover, COVER_SPECS[cover], inputs, scores, profile)
        for cover in covers
    ]
    flags = _referral_flags(profile, scores, inputs, covers)
    if any(item.get("loading_cap_applied") for item in priced):
        flags.append(
            "Combined risk loading was capped at 4.0x on one or more covers - "
            "actual technical rate may be higher. Route to senior underwriter."
        )

    subtotal = round(sum(item["premium_lakh"] for item in priced), 2)
    discount_rate = 0.0
    if bundle and bundle.get("name") and len(priced) >= 3:
        discount_rate = 0.08 if len(priced) >= 5 else 0.05
    discount = round(subtotal * discount_rate, 2)
    net = round(max(0.0, subtotal - discount), 2)
    gst = round(net * GST_RATE, 2)
    gross = round(net + gst, 2)

    return {
        "engine_version": ENGINE_VERSION,
        "quote_type": "indicative_underwriting_quote",
        "currency": "INR",
        "method": f"Base rate x sum insured/exposure x risk, stage, sector, climate, control, and claims loadings. Combined loading capped at {MAX_COMBINED_LOADING}x per cover.",
        "bundle_name": (bundle or {}).get("name"),
        "covers_priced": priced,
        "cover_count": len(priced),
        "total_sum_insured_cr": round(sum(item["sum_insured_cr"] for item in priced), 2),
        "subtotal_premium_lakh": subtotal,
        "bundle_discount_rate": discount_rate,
        "bundle_discount_lakh": discount,
        "net_premium_lakh": net,
        "gst_rate": GST_RATE,
        "gst_lakh": gst,
        "gross_premium_lakh": gross,
        "gross_premium_inr": int(round(gross * 100_000)),
        "underwriting_inputs": {key: value for key, value in inputs.items() if not key.startswith("_")},
        "assumptions": inputs.get("_assumption_notes", []),
        "missing_inputs": _missing_inputs(profile, covers),
        "underwriter_referral_flags": flags,
    }
