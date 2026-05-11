"""
product_catalogue_v2.py — Master ICICI Lombard commercial/group/specialty product catalogue.

Structure
---------
FAMILY_SCORING_PARAMS   dict[family_key -> scoring params]
    Each entry defines intercept, risk_weights, exposure_weights,
    trend_prior, wording_weights, and penalty_weights for the family.

PRODUCT_CATALOGUE_V2    dict[product_key -> product metadata]
    Each product carries canonical_family, variant metadata,
    hard_gates, sector_tags, and optional per-product scoring overrides.

PAIR_RULES              list of (trigger_family, boost_family, condition, delta_z, reason)
    Post-scoring pair-boost rules applied by bundle_recommender_v2.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Any, Tuple


@dataclass(frozen=True)
class Product:
    name: str
    uin: str
    startup_relevance: int
    premium_seed_inr_range: Tuple[int, int]
    premium_seriesb_inr_range: Tuple[int, int]
    risk_mult: float
    top_bundle_pairs: List[str]
    regulatory_complexity: str
    regulation_anchors: List[str]
    exclusions: List[str]
    decision_rationale: str
    route_to_life_insurer: bool = False


PRODUCTS: Dict[str, Product] = {
    "group_health": Product(
        name="Group Health",
        uin="GROUP_HEALTH",
        startup_relevance=9,
        premium_seed_inr_range=(120000, 450000),
        premium_seriesb_inr_range=(800000, 3200000),
        risk_mult=1.05,
        top_bundle_pairs=["Group_PA", "Employers_Compensation"],
        regulatory_complexity="low",
        regulation_anchors=["IRDAI Health Insurance Regulations"],
        exclusions=["Non-employee dependants without endorsement"],
        decision_rationale="Baseline employee welfare cover for hiring and retention.",
    ),
    "group_pa": Product(
        name="Group Personal Accident",
        uin="GROUP_PA",
        startup_relevance=8,
        premium_seed_inr_range=(35000, 150000),
        premium_seriesb_inr_range=(250000, 900000),
        risk_mult=0.95,
        top_bundle_pairs=["GROUP_HEALTH", "EMPLOYERS_COMP"],
        regulatory_complexity="low",
        regulation_anchors=["IRDAI Personal Accident product norms"],
        exclusions=["Non-occupational exclusions as per policy wording"],
        decision_rationale="Low-cost accident cover paired with health and workforce products.",
    ),
    "employers_comp": Product(
        name="Employers Compensation",
        uin="EMPLOYERS_COMP",
        startup_relevance=9,
        premium_seed_inr_range=(50000, 250000),
        premium_seriesb_inr_range=(450000, 1800000),
        risk_mult=0.9,
        top_bundle_pairs=["GROUP_PA", "PUBLIC_LIABILITY"],
        regulatory_complexity="medium",
        regulation_anchors=["Employees' Compensation Act 1923"],
        exclusions=["Non-work-related injury"],
        decision_rationale="Statutory and contractual workforce injury liability cover.",
    ),
    "employment_practices": Product(
        name="Employment Practices Liability",
        uin="EMPLOYMENT_PRACTICES",
        startup_relevance=7,
        premium_seed_inr_range=(40000, 120000),
        premium_seriesb_inr_range=(350000, 1000000),
        risk_mult=1.1,
        top_bundle_pairs=["EMPLOYERS_COMP", "GROUP_PA", "D_AND_O"],
        regulatory_complexity="medium",
        regulation_anchors=["POSH Act 2013", "Code on Social Security 2020"],
        exclusions=["Known disputes, deliberate unlawful acts, and prior claims as worded"],
        decision_rationale="Wrongful termination, discrimination, harassment, and workplace-practices liability for scaling teams.",
    ),
    "cgl_i_elite": Product(
        name="CGL / I-Elite",
        uin="CGL_I_ELITE",
        startup_relevance=8,
        premium_seed_inr_range=(90000, 350000),
        premium_seriesb_inr_range=(600000, 2500000),
        risk_mult=1.1,
        top_bundle_pairs=["PUBLIC_LIABILITY", "PRODUCT_LIABILITY", "PI_TECH_EO"],
        regulatory_complexity="medium",
        regulation_anchors=["Commercial General Liability wording"],
        exclusions=["Professional services unless endorsed"],
        decision_rationale="Broad third-party bodily injury, property damage, and contractual liability foundation.",
    ),
    "public_liability": Product(
        name="Public Liability",
        uin="PUBLIC_LIABILITY",
        startup_relevance=7,
        premium_seed_inr_range=(40000, 175000),
        premium_seriesb_inr_range=(250000, 1200000),
        risk_mult=0.95,
        top_bundle_pairs=["EMPLOYERS_COMP", "PROPERTY_FIRE"],
        regulatory_complexity="medium",
        regulation_anchors=["Public Liability Insurance Act 1991 where applicable"],
        exclusions=["Product defects unless product liability is bought"],
        decision_rationale="Premises and public interaction liability cover.",
    ),
    "product_liability": Product(
        name="Product Liability",
        uin="PRODUCT_LIABILITY",
        startup_relevance=8,
        premium_seed_inr_range=(75000, 300000),
        premium_seriesb_inr_range=(500000, 2200000),
        risk_mult=1.2,
        top_bundle_pairs=["CGL_I_ELITE", "CYBER"],
        regulatory_complexity="medium",
        regulation_anchors=["Consumer Protection Act 2019"],
        exclusions=["Known defects and recall unless endorsed"],
        decision_rationale="Physical product defect and injury exposure for D2C, hardware, food, and devices.",
    ),
    "pi_tech_eo": Product(
        name="Professional Indemnity / Tech E&O",
        uin="PI_TECH_EO",
        startup_relevance=9,
        premium_seed_inr_range=(100000, 450000),
        premium_seriesb_inr_range=(700000, 3000000),
        risk_mult=1.15,
        top_bundle_pairs=["CYBER", "D_AND_O"],
        regulatory_complexity="medium",
        regulation_anchors=["Professional Indemnity commercial wording"],
        exclusions=["Fraud, deliberate non-performance, and uninsured warranties"],
        decision_rationale="Core E&O protection for SaaS, fintech, healthtech, and services contracts.",
    ),
    "d_and_o": Product(
        name="Directors and Officers Liability",
        uin="D_AND_O",
        startup_relevance=9,
        premium_seed_inr_range=(125000, 600000),
        premium_seriesb_inr_range=(900000, 4500000),
        risk_mult=1.2,
        top_bundle_pairs=["PI_TECH_EO", "CRIME_FIDELITY"],
        regulatory_complexity="high",
        regulation_anchors=["Companies Act 2013", "SEBI LODR where applicable"],
        exclusions=["Insured versus insured and prior acts as worded"],
        decision_rationale="Board, investor, and management liability protection for funded companies.",
    ),
    "cyber": Product(
        name="Cyber",
        uin="CYBER",
        startup_relevance=10,
        premium_seed_inr_range=(75000, 400000),
        premium_seriesb_inr_range=(600000, 3500000),
        risk_mult=1.3,
        top_bundle_pairs=["PI_TECH_EO", "CRIME_FIDELITY"],
        regulatory_complexity="high",
        regulation_anchors=["DPDP Act 2023", "CERT-In Directions 2022"],
        exclusions=["Unpatched known vulnerabilities as worded"],
        decision_rationale="Breach response, privacy liability, ransomware, and cyber interruption cover.",
    ),
    "bharat_sookshma": Product(
        name="Bharat Sookshma",
        uin="BHARAT_SOOKSHMA",
        startup_relevance=7,
        premium_seed_inr_range=(8000, 50000),
        premium_seriesb_inr_range=(0, 0),
        risk_mult=0.9,
        top_bundle_pairs=["PUBLIC_LIABILITY", "EMPLOYERS_COMP"],
        regulatory_complexity="low",
        regulation_anchors=["Bharat Sookshma Udyam Suraksha product wording"],
        exclusions=["Sum insured above INR 5 crore"],
        decision_rationale="Standardised fire/property route for small enterprises under the SI cap.",
    ),
    "property_fire": Product(
        name="Property Fire",
        uin="PROPERTY_FIRE",
        startup_relevance=8,
        premium_seed_inr_range=(50000, 200000),
        premium_seriesb_inr_range=(650000, 2200000),
        risk_mult=1.05,
        top_bundle_pairs=["BUSINESS_INTERRUPTION", "PUBLIC_LIABILITY", "EMPLOYERS_COMP"],
        regulatory_complexity="low",
        regulation_anchors=["Standard Fire and Special Perils / Bharat Laghu and Sookshma property wording"],
        exclusions=["Uninsured perils, underinsurance, and excluded catastrophe extensions as worded"],
        decision_rationale="Core premises, stock, machinery, and business asset protection for physical SME operations.",
    ),
    "business_interruption": Product(
        name="Business Interruption",
        uin="BUSINESS_INTERRUPTION",
        startup_relevance=8,
        premium_seed_inr_range=(30000, 100000),
        premium_seriesb_inr_range=(400000, 1500000),
        risk_mult=1.1,
        top_bundle_pairs=["BHARAT_SOOKSHMA", "PROPERTY_ALL_RISK"],
        regulatory_complexity="medium",
        regulation_anchors=["Business interruption section wording"],
        exclusions=["Uninsured physical damage trigger and uninsured standing charges as worded"],
        decision_rationale="Cash-flow protection after insured physical damage.",
    ),
    "property_all_risk": Product(
        name="Property All Risk",
        uin="PROPERTY_ALL_RISK",
        startup_relevance=8,
        premium_seed_inr_range=(50000, 200000),
        premium_seriesb_inr_range=(700000, 2500000),
        risk_mult=1.15,
        top_bundle_pairs=["BUSINESS_INTERRUPTION", "PUBLIC_LIABILITY"],
        regulatory_complexity="medium",
        regulation_anchors=["Property all risk wording"],
        exclusions=["Named exclusions and catastrophe deductibles as worded"],
        decision_rationale="Broader property protection for labs, warehouses, plants, and equipment-heavy startups.",
    ),
    "electronic_equipment": Product(
        name="Electronic Equipment Insurance",
        uin="ELECTRONIC_EQUIPMENT",
        startup_relevance=7,
        premium_seed_inr_range=(30000, 120000),
        premium_seriesb_inr_range=(400000, 1500000),
        risk_mult=1.1,
        top_bundle_pairs=["PROPERTY_ALL_RISK", "CYBER"],
        regulatory_complexity="low",
        regulation_anchors=["Electronic equipment insurance wording"],
        exclusions=["Wear and tear, gradual deterioration, and unapproved modifications as worded"],
        decision_rationale="Affirmative cover for servers, diagnostic equipment, lab electronics, and control systems.",
    ),
    "machinery_breakdown": Product(
        name="Machinery Breakdown",
        uin="MACHINERY_BREAKDOWN",
        startup_relevance=7,
        premium_seed_inr_range=(20000, 80000),
        premium_seriesb_inr_range=(300000, 1000000),
        risk_mult=1.15,
        top_bundle_pairs=["PROPERTY_ALL_RISK", "BUSINESS_INTERRUPTION"],
        regulatory_complexity="low",
        regulation_anchors=["Machinery breakdown wording"],
        exclusions=["Maintenance failures, wear and tear, and excluded machinery as worded"],
        decision_rationale="Breakdown cover for plant, production, and mission-critical machinery.",
    ),
    "marine_cargo": Product(
        name="Marine Cargo",
        uin="MARINE_CARGO",
        startup_relevance=7,
        premium_seed_inr_range=(40000, 200000),
        premium_seriesb_inr_range=(350000, 1600000),
        risk_mult=1.0,
        top_bundle_pairs=["TRADE_CREDIT", "COMMERCIAL_MOTOR"],
        regulatory_complexity="medium",
        regulation_anchors=["Marine Cargo policy wording", "Institute Cargo Clauses"],
        exclusions=["Delay and trade credit unless separately insured"],
        decision_rationale="Transit cover for domestic and export goods movement.",
    ),
    "crime_fidelity": Product(
        name="Crime / Fidelity",
        uin="CRIME_FIDELITY",
        startup_relevance=8,
        premium_seed_inr_range=(75000, 300000),
        premium_seriesb_inr_range=(450000, 1800000),
        risk_mult=1.15,
        top_bundle_pairs=["CYBER", "D_AND_O"],
        regulatory_complexity="medium",
        regulation_anchors=["Commercial Crime / Fidelity wording"],
        exclusions=["Known prior fraud and weak controls as worded"],
        decision_rationale="Employee dishonesty, social engineering, and financial crime protection.",
    ),
    "drone_rpas": Product(
        name="Drone RPAS",
        uin="Drone_RPAS",
        startup_relevance=8,
        premium_seed_inr_range=(90000, 350000),
        premium_seriesb_inr_range=(500000, 2200000),
        risk_mult=1.35,
        top_bundle_pairs=["PUBLIC_LIABILITY", "PRODUCT_LIABILITY"],
        regulatory_complexity="high",
        regulation_anchors=["Drone Rules 2021 Rule 44", "DGCA UAS guidance"],
        exclusions=["Non-compliant operations and unauthorised flight zones"],
        decision_rationale="Mandatory specialty liability/property route for commercial drone operations.",
    ),
    "engineering": Product(
        name="Engineering CAR / EAR / CPM / MBD / EEI",
        uin="ENGINEERING_CAR_EAR_CPM_MBD_EEI",
        startup_relevance=7,
        premium_seed_inr_range=(150000, 700000),
        premium_seriesb_inr_range=(900000, 5000000),
        risk_mult=1.25,
        top_bundle_pairs=["MARINE_CARGO", "SURETY"],
        regulatory_complexity="medium",
        regulation_anchors=["Engineering Insurance policy wordings"],
        exclusions=["Operational wear and tear unless machinery breakdown applies"],
        decision_rationale="Project, plant, machinery, and electronic equipment protection.",
    ),
    "trade_credit": Product(
        name="Trade Credit",
        uin="TRADE_CREDIT",
        startup_relevance=6,
        premium_seed_inr_range=(100000, 450000),
        premium_seriesb_inr_range=(800000, 3500000),
        risk_mult=1.2,
        top_bundle_pairs=["MARINE_CARGO"],
        regulatory_complexity="medium",
        regulation_anchors=["Trade Credit Insurance wording"],
        exclusions=["Disputed receivables and related-party debt"],
        decision_rationale="Buyer default and receivables concentration protection.",
    ),
    "surety": Product(
        name="Surety",
        uin="SURETY",
        startup_relevance=5,
        premium_seed_inr_range=(125000, 600000),
        premium_seriesb_inr_range=(1000000, 6000000),
        risk_mult=1.3,
        top_bundle_pairs=["ENGINEERING_CAR_EAR_CPM_MBD_EEI"],
        regulatory_complexity="high",
        regulation_anchors=["IRDAI Surety Insurance Guidelines"],
        exclusions=["Weak financials and non-bondable contracts"],
        decision_rationale="Bid, performance, and contract bond support for project businesses.",
    ),
    "prakritik_parametric": Product(
        name="Prakritik Vishamta Bima Parametric",
        uin="PRAKRITIK_PARAMETRIC",
        startup_relevance=5,
        premium_seed_inr_range=(50000, 250000),
        premium_seriesb_inr_range=(400000, 2000000),
        risk_mult=1.1,
        top_bundle_pairs=["BHARAT_SOOKSHMA", "MARINE_CARGO"],
        regulatory_complexity="medium",
        regulation_anchors=["Parametric climate product filings"],
        exclusions=["Basis risk outside defined index triggers"],
        decision_rationale="Climate index payout route for weather-sensitive operations.",
    ),
    "motor_fleet": Product(
        name="Commercial Motor Fleet",
        uin="MOTOR_FLEET",
        startup_relevance=8,
        premium_seed_inr_range=(50000, 200000),
        premium_seriesb_inr_range=(700000, 2500000),
        risk_mult=1.2,
        top_bundle_pairs=["EMPLOYERS_COMP", "MARINE_CARGO"],
        regulatory_complexity="medium",
        regulation_anchors=["Motor Vehicles Act 1988"],
        exclusions=["Unregistered vehicles, non-permitted use, and driver exclusions as worded"],
        decision_rationale="Fleet cover for owned or operated delivery, goods, field-service, and industrial vehicles.",
    ),
    "healthcare_pi": Product(
        name="Healthcare and Medical Professional Liability",
        uin="HEALTHCARE_PI",
        startup_relevance=8,
        premium_seed_inr_range=(150000, 600000),
        premium_seriesb_inr_range=(900000, 4500000),
        risk_mult=1.25,
        top_bundle_pairs=["CYBER", "CGL_I_ELITE", "GROUP_HEALTH"],
        regulatory_complexity="high",
        regulation_anchors=["Healthcare professional liability wording", "NMC / telemedicine guidance where applicable"],
        exclusions=["Known incidents, criminal acts, and unlicensed clinical practice as worded"],
        decision_rationale="Clinical negligence and patient injury exposure for healthcare operations.",
    ),
    "financial_services_pi": Product(
        name="Financial Services / Institutions Professional Indemnity",
        uin="FINANCIAL_SERVICES_PI",
        startup_relevance=9,
        premium_seed_inr_range=(200000, 850000),
        premium_seriesb_inr_range=(1200000, 6000000),
        risk_mult=1.35,
        top_bundle_pairs=["CYBER", "CRIME_FIDELITY", "D_AND_O"],
        regulatory_complexity="high",
        regulation_anchors=["RBI / SEBI / IRDAI regulatory framework where applicable"],
        exclusions=["Deliberate regulatory breach, insolvency, and uninsured investment losses as worded"],
        decision_rationale="Regulated financial-service errors, omissions, and investigation defence for fintechs.",
    ),
    "payment_protection": Product(
        name="Payment / Card Protection",
        uin="PAYMENT_PROTECTION",
        startup_relevance=8,
        premium_seed_inr_range=(125000, 550000),
        premium_seriesb_inr_range=(800000, 3500000),
        risk_mult=1.25,
        top_bundle_pairs=["CYBER", "CRIME_FIDELITY"],
        regulatory_complexity="high",
        regulation_anchors=["Payment card / consumer payment protection wording"],
        exclusions=["Unauthorised payment flows outside programme wording"],
        decision_rationale="Fraud, skimming, counterfeit, and unauthorised-transaction protection for payment programmes.",
    ),
    "product_recall_cover": Product(
        name="Product Recall / Contamination",
        uin="PRODUCT_RECALL",
        startup_relevance=8,
        premium_seed_inr_range=(150000, 700000),
        premium_seriesb_inr_range=(900000, 5000000),
        risk_mult=1.3,
        top_bundle_pairs=["PRODUCT_LIABILITY", "CGL_I_ELITE", "PROPERTY_FIRE"],
        regulatory_complexity="high",
        regulation_anchors=["Product recall / contamination policy wording", "FSSAI rules where applicable"],
        exclusions=["Known defects, deliberate contamination, and recall outside covered territories as worded"],
        decision_rationale="Recall cost, contamination, financial loss, and brand rehabilitation cover for product-led businesses.",
    ),
    "event_production": Product(
        name="Entertainment Production Package",
        uin="EVENT_PRODUCTION",
        startup_relevance=6,
        premium_seed_inr_range=(100000, 450000),
        premium_seriesb_inr_range=(700000, 2800000),
        risk_mult=1.2,
        top_bundle_pairs=["PUBLIC_LIABILITY", "EMPLOYERS_COMP"],
        regulatory_complexity="medium",
        regulation_anchors=["Entertainment production package wording"],
        exclusions=["Unlicensed venues, excluded cast risks, and weather exclusions as worded"],
        decision_rationale="Production interruption, cast/equipment, venue, and event liability cover.",
    ),
    "group_term_life": Product(
        name="Group Term Life",
        uin="GROUP_TERM_LIFE",
        startup_relevance=6,
        premium_seed_inr_range=(60000, 250000),
        premium_seriesb_inr_range=(500000, 2200000),
        risk_mult=0.95,
        top_bundle_pairs=["GROUP_HEALTH", "GROUP_PA"],
        regulatory_complexity="low",
        regulation_anchors=["Life insurance routed outside ICICI Lombard"],
        exclusions=["Not a general insurance composite component"],
        decision_rationale="Life cover routed to ICICI Prudential Life, not an ICICI Lombard bundle component.",
        route_to_life_insurer=True,
    ),
    "key_person_life": Product(
        name="Key Person",
        uin="KEY_PERSON_LIFE",
        startup_relevance=7,
        premium_seed_inr_range=(75000, 300000),
        premium_seriesb_inr_range=(450000, 1800000),
        risk_mult=1.0,
        top_bundle_pairs=["D_AND_O"],
        regulatory_complexity="low",
        regulation_anchors=["Life insurance routed outside ICICI Lombard"],
        exclusions=["Not a general insurance composite component"],
        decision_rationale="Founder dependency life route via ICICI Prudential Life.",
        route_to_life_insurer=True,
    ),
}


# ============================================================================
# FAMILY-LEVEL SCORING PARAMETERS
# ============================================================================
# intercept      : baseline z-score before any evidence
# risk_weights   : {risk_category_name: weight}  — risk scores are 0-100, normalised to 0-1
# exposure_weights: {feature_key: weight}         — features are 0-1 normalised
# trend_prior    : additive constant reflecting macro trend signal
# wording_weights: {feature_key: weight}           — policy wording alignment bonuses
# penalty_weights: {feature_key: weight}           — negative adjustments for contraindications
# min_score      : minimum score to appear in recommendations at all
# ============================================================================

FAMILY_SCORING_PARAMS: Dict[str, Dict[str, Any]] = {

    "core_business_package": {
        "intercept": -2.5,
        "risk_weights": {
            "Property Risk": 1.2,
            "Liability Risk": 0.8,
            "Reputation Risk": 0.5,
            "Regulatory Compliance Risk": 0.4,
        },
        "exposure_weights": {
            "any_physical":      0.5,
            "has_warehouse":     0.5,
            "has_store":         0.6,
            "has_factory":       0.4,
            "asset_tier":        0.8,
            "headcount_tier":    0.4,
            "is_funded":         0.3,
            "event_production_ops": 1.5,
            "jewellery_inventory":  2.0,
            "fuel_forecourt":       2.0,
            "port_maritime":        1.2,
            "revenue_tier":         0.4,
        },
        "trend_prior": 0.1,
        "wording_weights": {},
        "penalty_weights": {},
        "min_score": 25,
    },

    "property_fire": {
        "intercept": -2.5,
        "risk_weights": {
            "Property Risk": 2.5,
            "ESG & Climate Risk": 0.4,
            "Regulatory Compliance Risk": 0.2,
        },
        "exposure_weights": {
            "has_factory":   1.2,
            "has_warehouse": 1.0,
            "has_store":     0.7,
            "has_lab":       0.4,
            "has_office":    0.2,
            "asset_tier":    1.2,
            "stock_tier":    0.8,
            "machinery_tier": 1.0,
            "any_physical":  0.3,
        },
        "trend_prior": 0.1,
        "wording_weights": {},
        "penalty_weights": {},
        "min_score": 20,
    },

    "employee_health": {
        "intercept": -2.5,
        "risk_weights": {
            "Key Person Risk": 0.8,
            "Gig & Labour Risk": 0.6,
            "Regulatory Compliance Risk": 0.4,
        },
        "exposure_weights": {
            "headcount_tier":  2.0,
            "has_workforce":   0.5,
            "is_funded":       0.4,
            "regulatory_intensity_tier": 0.3,
            "revenue_tier":    0.3,
        },
        "trend_prior": 0.25,
        "wording_weights": {},
        "penalty_weights": {},
        "min_score": 25,
    },

    "employers_liability": {
        "intercept": -2.5,
        "risk_weights": {
            "Liability Risk": 1.5,
            "Gig & Labour Risk": 1.2,
            "Regulatory Compliance Risk": 0.5,
        },
        "exposure_weights": {
            "blue_collar_tier":  1.0,
            "gig_tier":          0.8,
            "headcount_tier":    0.5,
            "has_factory":       0.3,
            "has_warehouse":     0.2,
            "has_workforce":     0.3,
        },
        "trend_prior": 0.1,
        "wording_weights": {},
        "penalty_weights": {},
        "min_score": 20,
    },

    "general_or_modular_liability": {
        "intercept": -2.0,
        "risk_weights": {
            "Liability Risk": 2.0,
            "Reputation Risk": 0.7,
            "Regulatory Compliance Risk": 0.5,
        },
        "exposure_weights": {
            "has_factory":    0.6,
            "has_warehouse":  0.4,
            "has_store":      0.5,
            "any_physical":   0.3,
            "headcount_tier": 0.3,
            "locations_tier": 0.5,
        },
        "trend_prior": 0.1,
        "wording_weights": {},
        "penalty_weights": {},
        "min_score": 25,
    },

    "cyber": {
        "intercept": -2.5,
        "risk_weights": {
            "Cyber Technical Risk": 2.0,
            "Data Privacy Risk": 1.5,
            "Regulatory Compliance Risk": 0.5,
        },
        "exposure_weights": {
            "handles_personal_data":  0.5,
            "handles_financial_data": 0.8,
            "handles_medical_data":   0.8,
            "uptime_dependency":      0.4,
            "transaction_tier":       0.6,
            "stores_docs":            0.3,
            "regulatory_intensity_tier": 0.4,
        },
        "trend_prior": 0.3,
        "wording_weights": {},
        "penalty_weights": {},
        "min_score": 20,
    },

    "professional_or_sector_liability": {
        "intercept": -2.5,
        "risk_weights": {
            "Liability Risk": 1.5,
            "Regulatory Compliance Risk": 1.0,
            "Reputation Risk": 0.6,
            "IP Infringement Risk": 0.3,
        },
        "exposure_weights": {
            "healthcare_ops":           1.5,
            "food_pharma_mfg":          1.0,
            "warranty_obligation":      0.8,
            "drone_ops":                1.2,
            "real_estate_dev":          1.5,
            "ma_transaction":           1.5,
            "surety_bond_need":         1.2,
            "regulatory_intensity_tier": 0.8,
            "handles_financial_data":   0.5,
        },
        "trend_prior": 0.1,
        "wording_weights": {},
        "penalty_weights": {},
        "min_score": 20,
    },

    "healthcare_liability": {
        "intercept": -3.0,
        "risk_weights": {
            "Liability Risk": 1.8,
            "Regulatory Compliance Risk": 1.2,
            "Reputation Risk": 0.8,
            "Data Privacy Risk": 0.5,
        },
        "exposure_weights": {
            "healthcare_ops": 2.8,
            "handles_medical_data": 0.8,
            "has_lab": 0.4,
            "asset_tier": 0.3,
            "regulatory_intensity_tier": 0.8,
        },
        "trend_prior": 0.15,
        "wording_weights": {},
        "penalty_weights": {"is_early": 0.1},
        "min_score": 25,
    },

    "fintech_fi_liability": {
        "intercept": -3.0,
        "risk_weights": {
            "Cyber Technical Risk": 1.2,
            "Data Privacy Risk": 1.0,
            "Governance & Fraud Risk": 1.2,
            "Regulatory Compliance Risk": 1.5,
            "Reputation Risk": 0.6,
        },
        "exposure_weights": {
            "handles_financial_data": 1.2,
            "payment_card_program": 1.4,
            "transaction_tier": 0.7,
            "regulatory_intensity_tier": 1.0,
            "is_funded": 0.4,
        },
        "trend_prior": 0.2,
        "wording_weights": {},
        "penalty_weights": {},
        "min_score": 25,
    },

    "product_recall_contamination": {
        "intercept": -3.2,
        "risk_weights": {
            "Liability Risk": 1.5,
            "Reputation Risk": 1.2,
            "Regulatory Compliance Risk": 1.0,
            "Property Risk": 0.4,
        },
        "exposure_weights": {
            "food_pharma_mfg": 2.5,
            "warranty_obligation": 1.0,
            "has_factory": 0.5,
            "stock_tier": 0.6,
            "revenue_tier": 0.3,
        },
        "trend_prior": 0.1,
        "wording_weights": {},
        "penalty_weights": {},
        "min_score": 25,
    },

    "surety_contract": {
        "intercept": -3.4,
        "risk_weights": {
            "Governance & Fraud Risk": 1.0,
            "Regulatory Compliance Risk": 1.0,
            "Property Risk": 0.5,
            "Liability Risk": 0.5,
        },
        "exposure_weights": {
            "surety_bond_need": 3.0,
            "has_project": 0.8,
            "capex_tier": 0.8,
            "revenue_tier": 0.3,
        },
        "trend_prior": 0.1,
        "wording_weights": {},
        "penalty_weights": {},
        "min_score": 30,
    },

    "media_production": {
        "intercept": -3.2,
        "risk_weights": {
            "Liability Risk": 1.2,
            "Reputation Risk": 1.0,
            "Property Risk": 0.5,
            "Gig & Labour Risk": 0.5,
        },
        "exposure_weights": {
            "event_production_ops": 3.0,
            "headcount_tier": 0.4,
            "asset_tier": 0.3,
        },
        "trend_prior": 0.05,
        "wording_weights": {},
        "penalty_weights": {},
        "min_score": 30,
    },

    "engineering_project": {
        "intercept": -3.5,
        "risk_weights": {
            "Property Risk": 1.5,
            "Liability Risk": 1.0,
            "ESG & Climate Risk": 0.3,
        },
        "exposure_weights": {
            "has_project": 3.0,
            "capex_tier":  1.5,
        },
        "trend_prior": 0.05,
        "wording_weights": {},
        "penalty_weights": {},
        "min_score": 25,
    },

    "marine_logistics_credit": {
        "intercept": -2.0,
        "risk_weights": {
            "Geopolitical Risk": 0.8,
            "Reputation Risk": 0.5,
            "Governance & Fraud Risk": 0.6,
        },
        "exposure_weights": {
            "has_domestic_shipments": 1.0,
            "has_export_shipments":   1.5,
            "has_import_dependency":  0.8,
            "receivables_tier":       1.0,
            "goods_vehicle_tier":     0.5,
            "port_maritime":          1.5,
            "surety_bond_need":       1.5,
            "invoice_cycle_tier":     0.5,
        },
        "trend_prior": 0.1,
        "wording_weights": {},
        "penalty_weights": {},
        "min_score": 20,
    },

    "commercial_motor_fleet": {
        "intercept": -3.0,
        "risk_weights": {
            "Liability Risk": 1.5,
            "Property Risk": 0.7,
            "Gig & Labour Risk": 0.5,
        },
        "exposure_weights": {
            "vehicle_tier":       2.0,
            "goods_vehicle_tier": 0.8,
            "has_trailer":        0.5,
            "has_two_wheeler":    0.3,
        },
        "trend_prior": 0.05,
        "wording_weights": {},
        "penalty_weights": {},
        "min_score": 25,
    },

    "payment_card_network_specialty": {
        "intercept": -4.0,
        "risk_weights": {
            "Cyber Technical Risk": 1.5,
            "Governance & Fraud Risk": 1.5,
            "Data Privacy Risk": 0.8,
            "Regulatory Compliance Risk": 0.5,
        },
        "exposure_weights": {
            "payment_card_program":     3.0,
            "handles_financial_data":   0.8,
            "transaction_tier":         0.6,
            "telecom_network":          2.0,
            "regulatory_intensity_tier": 0.5,
        },
        "trend_prior": 0.1,
        "wording_weights": {},
        "penalty_weights": {},
        "min_score": 30,
    },
}


# ============================================================================
# PRODUCT CATALOGUE
# ============================================================================
# Fields per product:
#   canonical_family      : family key from FAMILY_SCORING_PARAMS
#   product_name          : exact marketing name
#   variant_type          : "standard"|"commercial"|"laghu"|"sookshma"|"advance"|"micro"|"plus"|...
#   active_status         : True = currently available
#   sector_tags           : list of sector names this product is well-suited to
#   required_exposures    : human-readable list of exposures that trigger fit
#   forbidden_exposures   : exposures that make this product inappropriate
#   hard_gates            : dict passed to check_hard_gates()
#   exposure_weights      : product-specific override / supplement to family weights
#   trend_priors          : product-specific trend adjustment (float added to family trend_prior)
#   wording_features      : list of key policy wording features
#   penalties             : dict of feature → penalty weight (supplement to family penalties)
#   pair_rules            : list of families that should be boosted when this product is chosen
#   explanation_templates : list of f-string-style templates for generating reasons
# ============================================================================

PRODUCT_CATALOGUE_V2: Dict[str, Dict[str, Any]] = {

    # -------------------------------------------------------------------------
    # FAMILY: core_business_package
    # -------------------------------------------------------------------------

    "business_edge": {
        "canonical_family": "core_business_package",
        "product_name": "Business Edge Policy",
        "variant_type": "standard",
        "active_status": True,
        "sector_tags": [
            "SaaS / Enterprise Software", "D2C / Consumer Brands", "Logistics / Mobility",
            "HRtech", "Legaltech", "Foodtech / Cloud Kitchen",
        ],
        "required_exposures": ["office_presence", "any_physical_presence"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_any_physical_presence": True},
        "exposure_weights": {"has_office": 0.3, "is_funded": 0.3},
        "trend_priors": 0.0,
        "wording_features": ["property_and_liability_combined", "optional_covers_menu"],
        "penalties": {},
        "pair_rules": ["employee_health", "cyber"],
        "explanation_templates": [
            "Business Edge provides combined property and liability in a single package, simplifying SME risk management.",
            "Physical office / premises presence makes Business Edge a natural anchor policy.",
        ],
    },

    "business_prime": {
        "canonical_family": "core_business_package",
        "product_name": "Business Prime Policy",
        "variant_type": "premium",
        "active_status": True,
        "sector_tags": [
            "SaaS / Enterprise Software", "Fintech", "Healthtech", "D2C / Consumer Brands",
            "Logistics / Mobility", "HRtech", "Legaltech",
        ],
        "required_exposures": ["office_presence", "any_physical_presence"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_any_physical_presence": True},
        "exposure_weights": {"has_office": 0.3, "is_funded": 0.4, "is_growth": 0.3},
        "trend_priors": 0.05,
        "wording_features": ["broader_property_scope", "higher_liability_limits", "optional_covers_menu"],
        "penalties": {},
        "pair_rules": ["employee_health", "cyber", "professional_or_sector_liability"],
        "explanation_templates": [
            "Business Prime offers higher limits and broader cover than Business Edge, suitable for funded or growth-stage businesses.",
        ],
    },

    "msme_suraksha_kavach_advance": {
        "canonical_family": "core_business_package",
        "product_name": "ICICI Lombard MSME Suraksha Kavach Package Policy – Advance",
        "variant_type": "advance",
        "active_status": True,
        "sector_tags": [
            "D2C / Consumer Brands", "Logistics / Mobility", "Foodtech / Cloud Kitchen",
            "Agritech", "Cleantech / Climatetech", "Deeptech / AI / Robotics",
        ],
        "required_exposures": ["office_presence", "warehouse_presence", "factory_presence"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_any_physical_presence": True},
        "exposure_weights": {
            "has_warehouse": 0.5,
            "has_factory":   0.5,
            "stock_tier":    0.5,
            "headcount_tier": 0.3,
        },
        "trend_priors": 0.0,
        "wording_features": [
            "fire_burglary_bi_package", "optional_cyber", "optional_product_liability",
            "optional_public_liability", "optional_employees_comp",
        ],
        "penalties": {},
        "pair_rules": ["employers_liability", "cyber", "marine_logistics_credit"],
        "explanation_templates": [
            "MSME Suraksha Kavach Advance is designed for startups with physical ops — warehouse, inventory, and delivery exposure.",
            "Bundles fire, burglary, and business interruption as mandatory covers with optional add-ons.",
        ],
    },

    "enterprise_secure": {
        "canonical_family": "core_business_package",
        "product_name": "Enterprise Secure Package Policy",
        "variant_type": "standard",
        "active_status": True,
        "sector_tags": [
            "SaaS / Enterprise Software", "Fintech", "Healthtech", "Logistics / Mobility",
            "Deeptech / AI / Robotics", "HRtech", "Legaltech",
        ],
        "required_exposures": ["office_presence", "any_physical_presence"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_any_physical_presence": True, "min_headcount": 10},
        "exposure_weights": {"is_funded": 0.5, "is_growth": 0.3, "headcount_tier": 0.3},
        "trend_priors": 0.1,
        "wording_features": ["property_liability_crime_combined", "optional_financial_lines"],
        "penalties": {},
        "pair_rules": ["cyber", "employee_health", "professional_or_sector_liability"],
        "explanation_templates": [
            "Enterprise Secure combines property, liability, and crime covers in a single enterprise-grade package.",
        ],
    },

    "enterprise_secure_commercial": {
        "canonical_family": "core_business_package",
        "product_name": "Enterprise Secure Package Policy – Commercial",
        "variant_type": "commercial",
        "active_status": True,
        "sector_tags": [
            "SaaS / Enterprise Software", "Fintech", "Healthtech", "Logistics / Mobility",
        ],
        "required_exposures": ["office_presence"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_any_physical_presence": True, "min_headcount": 25},
        "exposure_weights": {"is_growth": 0.5, "headcount_tier": 0.3, "revenue_tier": 0.4},
        "trend_priors": 0.1,
        "wording_features": ["commercial_property_scope", "liability_crime_combined"],
        "penalties": {},
        "pair_rules": ["cyber", "professional_or_sector_liability"],
        "explanation_templates": [
            "Commercial version of Enterprise Secure for larger businesses with higher sum-insured requirements.",
        ],
    },

    "merchants_cover_iii": {
        "canonical_family": "core_business_package",
        "product_name": "Merchants Cover III",
        "variant_type": "standard",
        "active_status": True,
        "sector_tags": ["D2C / Consumer Brands", "Foodtech / Cloud Kitchen", "Agritech"],
        "required_exposures": ["store_presence", "warehouse_presence"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_any_physical_presence": True},
        "exposure_weights": {"has_store": 0.8, "has_warehouse": 0.5, "stock_tier": 0.6},
        "trend_priors": 0.0,
        "wording_features": ["stock_burglary_fire_money", "public_liability"],
        "penalties": {},
        "pair_rules": ["employers_liability", "general_or_modular_liability"],
        "explanation_templates": [
            "Merchants Cover III is designed for retail and trading businesses with stock and burglary exposure.",
        ],
    },

    "merchants_cover_iii_commercial": {
        "canonical_family": "core_business_package",
        "product_name": "Merchants Cover III – Commercial",
        "variant_type": "commercial",
        "active_status": True,
        "sector_tags": ["D2C / Consumer Brands", "Foodtech / Cloud Kitchen"],
        "required_exposures": ["store_presence"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_any_physical_presence": True},
        "exposure_weights": {"has_store": 0.9, "stock_tier": 0.7, "is_funded": 0.2},
        "trend_priors": 0.0,
        "wording_features": ["commercial_stock_limits", "burglary_fire"],
        "penalties": {},
        "pair_rules": ["employers_liability"],
        "explanation_templates": [
            "Commercial variant of Merchants Cover with higher limits for larger retail or trading operations.",
        ],
    },

    "corporate_cover_ii": {
        "canonical_family": "core_business_package",
        "product_name": "Corporate Cover II",
        "variant_type": "standard",
        "active_status": True,
        "sector_tags": [
            "SaaS / Enterprise Software", "Fintech", "Healthtech", "Legaltech",
            "HRtech", "D2C / Consumer Brands", "Logistics / Mobility",
            "Cleantech / Climatetech", "Deeptech / AI / Robotics",
        ],
        "required_exposures": ["office_presence"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_any_physical_presence": True, "min_headcount": 10},
        "exposure_weights": {
            "has_warehouse": 0.3, "has_office": 0.3, "is_funded": 0.6,
            "headcount_tier": 0.4,
        },
        "trend_priors": 0.15,
        "wording_features": [
            "fire_bi_public_liability_workers_comp", "optional_cyber", "optional_dno",
            "optional_pi", "optional_marine", "optional_trade_credit",
        ],
        "penalties": {},
        "pair_rules": ["cyber", "professional_or_sector_liability", "employee_health"],
        "explanation_templates": [
            "Corporate Cover II is the go-to growth-stage commercial package with BI, public liability, and employees' compensation.",
            "Institutional investors and enterprise clients often require the liability covers bundled in Corporate Cover II.",
        ],
    },

    "corporate_cover_ii_commercial": {
        "canonical_family": "core_business_package",
        "product_name": "Corporate Cover II – Commercial",
        "variant_type": "commercial",
        "active_status": True,
        "sector_tags": [
            "SaaS / Enterprise Software", "Fintech", "Healthtech", "Logistics / Mobility",
        ],
        "required_exposures": ["office_presence"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_any_physical_presence": True, "min_headcount": 25},
        "exposure_weights": {"is_growth": 0.6, "headcount_tier": 0.4, "revenue_tier": 0.5},
        "trend_priors": 0.15,
        "wording_features": ["commercial_property_bi_liability"],
        "penalties": {},
        "pair_rules": ["cyber", "professional_or_sector_liability"],
        "explanation_templates": [
            "Corporate Cover II Commercial offers higher limits and broader commercial property scope for Series B+ businesses.",
        ],
    },

    "petrol_station": {
        "canonical_family": "core_business_package",
        "product_name": "Petrol Station Package Policy",
        "variant_type": "standard",
        "active_status": True,
        "sector_tags": ["Logistics / Mobility", "Cleantech / Climatetech"],
        "required_exposures": ["fuel_or_forecourt_operations"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_fuel_forecourt": True},
        "exposure_weights": {"fuel_forecourt": 3.0},
        "trend_priors": 0.0,
        "wording_features": ["fuel_fire_explosion_public_liability", "pollution_liability"],
        "penalties": {},
        "pair_rules": ["employers_liability", "commercial_motor_fleet"],
        "explanation_templates": [
            "Petrol Station Package bundles fire/explosion, pollution liability, and public liability for forecourt operations.",
        ],
    },

    "petrol_station_commercial": {
        "canonical_family": "core_business_package",
        "product_name": "Petrol Station Package Policy – Commercial",
        "variant_type": "commercial",
        "active_status": True,
        "sector_tags": ["Logistics / Mobility"],
        "required_exposures": ["fuel_or_forecourt_operations"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_fuel_forecourt": True},
        "exposure_weights": {"fuel_forecourt": 3.0, "revenue_tier": 0.3},
        "trend_priors": 0.0,
        "wording_features": ["commercial_fuel_limits"],
        "penalties": {},
        "pair_rules": ["employers_liability", "commercial_motor_fleet"],
        "explanation_templates": [
            "Commercial version for multi-site or high-throughput petrol station operators.",
        ],
    },

    "jewellers_package": {
        "canonical_family": "core_business_package",
        "product_name": "Jeweller's Package Policy",
        "variant_type": "standard",
        "active_status": True,
        "sector_tags": ["D2C / Consumer Brands"],
        "required_exposures": ["jewellery_inventory"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_jewellery_inventory": True},
        "exposure_weights": {"jewellery_inventory": 3.0, "has_store": 0.5},
        "trend_priors": 0.0,
        "wording_features": ["jewellery_floater_transit_burglary_fire"],
        "penalties": {},
        "pair_rules": ["employers_liability", "general_or_modular_liability"],
        "explanation_templates": [
            "Jeweller's Package provides all-risk cover for stock, transit, and burglary of jewellery inventory.",
        ],
    },

    "jewellers_package_laghu": {
        "canonical_family": "core_business_package",
        "product_name": "Jeweller's Package Policy Laghu",
        "variant_type": "laghu",
        "active_status": True,
        "sector_tags": ["D2C / Consumer Brands"],
        "required_exposures": ["jewellery_inventory"],
        "forbidden_exposures": [],
        "hard_gates": {
            "requires_jewellery_inventory": True,
            "min_total_insurable_value": 5.0,
            "max_total_insurable_value": 50.0,
        },
        "exposure_weights": {"jewellery_inventory": 3.0},
        "trend_priors": 0.0,
        "wording_features": ["laghu_jewellery_floater"],
        "penalties": {},
        "pair_rules": ["employers_liability"],
        "explanation_templates": [
            "Laghu variant for jewellers with asset value between ₹5Cr and ₹50Cr.",
        ],
    },

    "jewellers_package_sookshma": {
        "canonical_family": "core_business_package",
        "product_name": "Jeweller's Package Policy Sookshma",
        "variant_type": "sookshma",
        "active_status": True,
        "sector_tags": ["D2C / Consumer Brands"],
        "required_exposures": ["jewellery_inventory"],
        "forbidden_exposures": [],
        "hard_gates": {
            "requires_jewellery_inventory": True,
            "max_total_insurable_value": 5.0,
        },
        "exposure_weights": {"jewellery_inventory": 3.0},
        "trend_priors": 0.0,
        "wording_features": ["micro_jewellery_floater"],
        "penalties": {},
        "pair_rules": [],
        "explanation_templates": [
            "Sookshma variant for micro jewellers with total insurable assets up to ₹5Cr.",
        ],
    },

    "energy_package": {
        "canonical_family": "core_business_package",
        "product_name": "Energy Package Insurance",
        "variant_type": "specialty",
        "active_status": True,
        "sector_tags": ["Cleantech / Climatetech", "Deeptech / AI / Robotics"],
        "required_exposures": ["factory_presence", "machinery_value"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_any_physical_presence": True},
        "exposure_weights": {
            "has_factory": 1.0, "machinery_tier": 0.8, "asset_tier": 0.7,
            "capex_tier": 0.5,
        },
        "trend_priors": 0.15,
        "wording_features": ["energy_property_machinery_BI_combined"],
        "penalties": {},
        "pair_rules": ["engineering_project", "employers_liability"],
        "explanation_templates": [
            "Energy Package bundles property, machinery breakdown, and business interruption for power and energy operations.",
        ],
    },

    "port_package": {
        "canonical_family": "core_business_package",
        "product_name": "Port Package Insurance",
        "variant_type": "specialty",
        "active_status": True,
        "sector_tags": ["Logistics / Mobility"],
        "required_exposures": ["port_or_maritime_operations"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_port_maritime": True},
        "exposure_weights": {"port_maritime": 3.5, "machinery_tier": 0.5},
        "trend_priors": 0.0,
        "wording_features": ["port_property_machinery_cargo_liability"],
        "penalties": {},
        "pair_rules": ["marine_logistics_credit", "employers_liability"],
        "explanation_templates": [
            "Port Package covers port property, machinery, cargo handling, and liability in a single policy.",
        ],
    },

    "entertainment_production_package": {
        "canonical_family": "media_production",
        "product_name": "Entertainment Production Package Policy",
        "variant_type": "package",
        "active_status": True,
        "sector_tags": ["Gaming / Media / Content"],
        "required_exposures": ["event_or_production_operations"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_event_production": True},
        "exposure_weights": {"event_production_ops": 3.5, "headcount_tier": 0.3},
        "trend_priors": 0.05,
        "wording_features": ["production_property_cast_abandonment_liability"],
        "penalties": {},
        "pair_rules": ["general_or_modular_liability", "employers_liability"],
        "explanation_templates": [
            "Entertainment Production Package covers cast, equipment, abandonment, and liability for film/event productions.",
        ],
    },

    "entertainment_production": {
        "canonical_family": "media_production",
        "product_name": "Entertainment Production Policy",
        "variant_type": "standalone",
        "active_status": True,
        "sector_tags": ["Gaming / Media / Content"],
        "required_exposures": ["event_or_production_operations"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_event_production": True},
        "exposure_weights": {"event_production_ops": 3.0},
        "trend_priors": 0.05,
        "wording_features": ["production_equipment_abandonment"],
        "penalties": {},
        "pair_rules": ["general_or_modular_liability"],
        "explanation_templates": [
            "Standalone production policy for event operators not requiring the full package.",
        ],
    },

    "business_guard": {
        "canonical_family": "core_business_package",
        "product_name": "Business Guard",
        "variant_type": "standard",
        "active_status": True,
        "sector_tags": [
            "SaaS / Enterprise Software", "Fintech", "HRtech", "Legaltech",
            "Edtech", "Gaming / Media / Content",
        ],
        "required_exposures": [],
        "forbidden_exposures": [],
        "hard_gates": {},
        "exposure_weights": {"is_funded": 0.4, "regulatory_intensity_tier": 0.3},
        "trend_priors": 0.1,
        "wording_features": ["property_liability_crime_optional"],
        "penalties": {},
        "pair_rules": ["cyber", "professional_or_sector_liability"],
        "explanation_templates": [
            "Business Guard is a flexible base policy covering property, liability, and optional financial lines.",
        ],
    },

    "business_guard_plus": {
        "canonical_family": "core_business_package",
        "product_name": "Business Guard Plus",
        "variant_type": "plus",
        "active_status": True,
        "sector_tags": [
            "SaaS / Enterprise Software", "Fintech", "Healthtech", "HRtech", "Legaltech",
        ],
        "required_exposures": [],
        "forbidden_exposures": [],
        "hard_gates": {},
        "exposure_weights": {"is_funded": 0.5, "is_growth": 0.3, "regulatory_intensity_tier": 0.4},
        "trend_priors": 0.15,
        "wording_features": ["broader_property", "higher_liability_limits", "crime_optional"],
        "penalties": {},
        "pair_rules": ["cyber", "professional_or_sector_liability", "employee_health"],
        "explanation_templates": [
            "Business Guard Plus offers enhanced limits and broader wording than Business Guard.",
        ],
    },

    "business_shield": {
        "canonical_family": "core_business_package",
        "product_name": "Business Shield",
        "variant_type": "standard",
        "active_status": True,
        "sector_tags": [
            "SaaS / Enterprise Software", "Fintech", "Healthtech", "Edtech",
            "Legaltech", "HRtech", "Gaming / Media / Content",
        ],
        "required_exposures": [],
        "forbidden_exposures": [],
        "hard_gates": {},
        "exposure_weights": {"is_funded": 0.4, "handles_personal_data": 0.3},
        "trend_priors": 0.1,
        "wording_features": ["digital_first_package", "cyber_pi_combined"],
        "penalties": {},
        "pair_rules": ["cyber", "professional_or_sector_liability"],
        "explanation_templates": [
            "Business Shield combines cyber liability, professional indemnity, and property for digital-first businesses.",
        ],
    },

    "business_shield_sme": {
        "canonical_family": "core_business_package",
        "product_name": "Business Shield SME",
        "variant_type": "sme",
        "active_status": True,
        "sector_tags": [
            "SaaS / Enterprise Software", "Fintech", "Healthtech", "HRtech", "Legaltech",
        ],
        "required_exposures": [],
        "forbidden_exposures": [],
        "hard_gates": {},
        "exposure_weights": {"is_early": 0.3, "is_funded": 0.4, "regulatory_intensity_tier": 0.3},
        "trend_priors": 0.1,
        "wording_features": ["sme_cyber_pi_package"],
        "penalties": {},
        "pair_rules": ["cyber", "employee_health"],
        "explanation_templates": [
            "Business Shield SME is sized for earlier-stage digital SMEs needing cyber + PI in a packaged form.",
        ],
    },

    # -------------------------------------------------------------------------
    # FAMILY: property_fire
    # -------------------------------------------------------------------------

    "bharat_sookshma": {
        "canonical_family": "property_fire",
        "product_name": "ICICI Bharat Sookshma Udyam Suraksha Policy",
        "variant_type": "sookshma",
        "active_status": True,
        "sector_tags": [
            "Agritech", "Foodtech / Cloud Kitchen", "D2C / Consumer Brands",
            "Cleantech / Climatetech", "Logistics / Mobility",
        ],
        "required_exposures": ["any_physical_presence"],
        "forbidden_exposures": [],
        "hard_gates": {
            "requires_any_physical_presence": True,
            "max_total_insurable_value": 5.0,
        },
        "exposure_weights": {"has_factory": 0.4, "has_warehouse": 0.3, "stock_tier": 0.3},
        "trend_priors": 0.0,
        "wording_features": ["standard_fire_perils", "optional_burglary", "optional_wc"],
        "penalties": {},
        "pair_rules": ["employers_liability", "general_or_modular_liability"],
        "explanation_templates": [
            "Bharat Sookshma is the most affordable entry-level fire policy for micro-enterprises with total assets ≤ ₹5Cr.",
        ],
    },

    "bharat_laghu": {
        "canonical_family": "property_fire",
        "product_name": "ICICI Bharat Laghu Udyam Suraksha Policy",
        "variant_type": "laghu",
        "active_status": True,
        "sector_tags": [
            "Agritech", "Foodtech / Cloud Kitchen", "D2C / Consumer Brands",
            "Cleantech / Climatetech", "Logistics / Mobility",
        ],
        "required_exposures": ["any_physical_presence"],
        "forbidden_exposures": [],
        "hard_gates": {
            "requires_any_physical_presence": True,
            "min_total_insurable_value": 5.0,
            "max_total_insurable_value": 50.0,
        },
        "exposure_weights": {"has_factory": 0.5, "has_warehouse": 0.4, "asset_tier": 0.4},
        "trend_priors": 0.0,
        "wording_features": ["standard_fire_perils", "optional_covers_menu"],
        "penalties": {},
        "pair_rules": ["employers_liability", "general_or_modular_liability"],
        "explanation_templates": [
            "Bharat Laghu is the small-business fire policy for asset values between ₹5Cr and ₹50Cr.",
        ],
    },

    "msme_suraksha_kavach_fire": {
        "canonical_family": "property_fire",
        "product_name": "ICICI Lombard MSME Suraksha Kavach (Complete Fire Insurance)",
        "variant_type": "fire_only",
        "active_status": True,
        "sector_tags": [
            "D2C / Consumer Brands", "Logistics / Mobility", "Foodtech / Cloud Kitchen",
            "Agritech",
        ],
        "required_exposures": ["any_physical_presence"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_any_physical_presence": True},
        "exposure_weights": {"has_warehouse": 0.5, "has_factory": 0.5, "stock_tier": 0.4},
        "trend_priors": 0.0,
        "wording_features": ["comprehensive_fire_perils_msme"],
        "penalties": {},
        "pair_rules": ["employers_liability", "general_or_modular_liability"],
        "explanation_templates": [
            "MSME Suraksha Kavach Complete Fire Insurance provides comprehensive fire cover for MSME premises and stock.",
        ],
    },

    "iar_policy": {
        "canonical_family": "property_fire",
        "product_name": "ICICI Lombard IAR Policy / Industrial All Risk Policy",
        "variant_type": "industrial_all_risk",
        "active_status": True,
        "sector_tags": [
            "Cleantech / Climatetech", "Deeptech / AI / Robotics", "Agritech",
            "Logistics / Mobility", "D2C / Consumer Brands",
        ],
        "required_exposures": ["factory_presence", "machinery_value"],
        "forbidden_exposures": [],
        "hard_gates": {
            "requires_any_physical_presence": True,
            "min_total_insurable_value": 50.0,
        },
        "exposure_weights": {
            "has_factory": 1.0, "machinery_tier": 1.0, "asset_tier": 0.8,
        },
        "trend_priors": 0.05,
        "wording_features": ["all_risk_industrial_property", "machinery_breakdown_included", "business_interruption"],
        "penalties": {},
        "pair_rules": ["engineering_project", "employers_liability"],
        "explanation_templates": [
            "IAR (Industrial All Risk) provides the broadest property cover for manufacturing/industrial sites with sum insured ≥ ₹50Cr.",
        ],
    },

    "property_all_risk": {
        "canonical_family": "property_fire",
        "product_name": "ICICI Lombard Property All Risk Insurance Policy",
        "variant_type": "all_risk",
        "active_status": True,
        "sector_tags": [
            "SaaS / Enterprise Software", "Fintech", "Healthtech", "Deeptech / AI / Robotics",
            "Cleantech / Climatetech", "Logistics / Mobility",
        ],
        "required_exposures": ["any_physical_presence"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_any_physical_presence": True},
        "exposure_weights": {
            "asset_tier": 0.8, "electronics_tier": 0.6, "has_lab": 0.5, "has_office": 0.3,
        },
        "trend_priors": 0.05,
        "wording_features": ["all_risk_accidental_damage", "broader_than_standard_fire"],
        "penalties": {},
        "pair_rules": ["engineering_project", "employee_health"],
        "explanation_templates": [
            "Property All Risk covers accidental damage in addition to named perils, making it suitable for R&D, lab, and data centre assets.",
        ],
    },

    "iar_commercial": {
        "canonical_family": "property_fire",
        "product_name": "Industrial All Risk Insurance Policy – Commercial",
        "variant_type": "commercial",
        "active_status": True,
        "sector_tags": [
            "Cleantech / Climatetech", "Deeptech / AI / Robotics", "Logistics / Mobility",
        ],
        "required_exposures": ["factory_presence"],
        "forbidden_exposures": [],
        "hard_gates": {
            "requires_any_physical_presence": True,
            "min_total_insurable_value": 50.0,
        },
        "exposure_weights": {"has_factory": 1.2, "machinery_tier": 1.0},
        "trend_priors": 0.05,
        "wording_features": ["commercial_all_risk_industrial", "bi_optional"],
        "penalties": {},
        "pair_rules": ["engineering_project", "employers_liability"],
        "explanation_templates": [
            "Commercial IAR variant with broader limits for large industrial operations.",
        ],
    },

    "fire_mega_risk": {
        "canonical_family": "property_fire",
        "product_name": "Fire Mega Risk",
        "variant_type": "mega",
        "active_status": True,
        "sector_tags": [
            "Cleantech / Climatetech", "Logistics / Mobility", "Deeptech / AI / Robotics",
        ],
        "required_exposures": ["factory_presence"],
        "forbidden_exposures": [],
        "hard_gates": {
            "requires_any_physical_presence": True,
            "min_total_insurable_value": 100.0,
        },
        "exposure_weights": {"has_factory": 1.5, "asset_tier": 1.0, "machinery_tier": 0.8},
        "trend_priors": 0.0,
        "wording_features": ["mega_fire_risk_cover", "catastrophe_perils"],
        "penalties": {},
        "pair_rules": ["engineering_project", "employers_liability"],
        "explanation_templates": [
            "Fire Mega Risk is for large industrial complexes with sum insured above ₹100Cr requiring catastrophe-grade cover.",
        ],
    },

    # -------------------------------------------------------------------------
    # FAMILY: employee_health
    # -------------------------------------------------------------------------

    "group_health": {
        "canonical_family": "employee_health",
        "product_name": "Group Health Insurance",
        "variant_type": "standard",
        "active_status": True,
        "sector_tags": [
            "SaaS / Enterprise Software", "Fintech", "Healthtech", "Edtech",
            "HRtech", "Legaltech", "Gaming / Media / Content", "D2C / Consumer Brands",
            "Logistics / Mobility", "Deeptech / AI / Robotics",
        ],
        "required_exposures": ["headcount_total >= 5"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_workforce": True, "min_headcount": 5},
        "exposure_weights": {"headcount_tier": 1.0, "is_funded": 0.4},
        "trend_priors": 0.2,
        "wording_features": ["hospitalisation_cover", "network_cashless"],
        "penalties": {},
        "pair_rules": ["employers_liability"],
        "explanation_templates": [
            "Group Health is a foundational employee benefit — required by talent retention standards in funded startups.",
            "Headcount of {headcount_total} meets the threshold for group health placement.",
        ],
    },

    "group_health_floater": {
        "canonical_family": "employee_health",
        "product_name": "Group Health / Group Health Floater / Health Shield 360 Group",
        "variant_type": "floater",
        "active_status": True,
        "sector_tags": [
            "SaaS / Enterprise Software", "Fintech", "Healthtech", "HRtech", "Legaltech",
        ],
        "required_exposures": ["headcount_total >= 5"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_workforce": True, "min_headcount": 5},
        "exposure_weights": {"headcount_tier": 1.0, "is_funded": 0.5, "is_growth": 0.3},
        "trend_priors": 0.2,
        "wording_features": ["family_floater_cover", "dependants_included"],
        "penalties": {},
        "pair_rules": ["employers_liability"],
        "explanation_templates": [
            "Group Health Floater / Health Shield 360 extends cover to employee dependants, important for talent-competitive sectors.",
        ],
    },

    "corporate_advantage_top_up": {
        "canonical_family": "employee_health",
        "product_name": "Corporate Advantage Super Top Up / Group Health Assure Super Top Up",
        "variant_type": "super_top_up",
        "active_status": True,
        "sector_tags": [
            "SaaS / Enterprise Software", "Fintech", "Healthtech",
        ],
        "required_exposures": ["headcount_total >= 10"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_workforce": True, "min_headcount": 10},
        "exposure_weights": {"headcount_tier": 0.8, "is_growth": 0.5, "revenue_tier": 0.3},
        "trend_priors": 0.15,
        "wording_features": ["super_top_up_above_base_cover"],
        "penalties": {},
        "pair_rules": [],
        "explanation_templates": [
            "Super Top Up supplements a base group health policy to bridge high hospitalisation costs.",
        ],
    },

    "group_hospital_cash": {
        "canonical_family": "employee_health",
        "product_name": "Group Hospital Cash",
        "variant_type": "hospital_cash",
        "active_status": True,
        "sector_tags": [
            "Logistics / Mobility", "D2C / Consumer Brands", "Agritech",
            "Foodtech / Cloud Kitchen",
        ],
        "required_exposures": ["headcount_total >= 5"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_workforce": True, "min_headcount": 5},
        "exposure_weights": {"blue_collar_tier": 0.6, "headcount_tier": 0.6},
        "trend_priors": 0.1,
        "wording_features": ["daily_hospital_cash_benefit"],
        "penalties": {},
        "pair_rules": ["employers_liability"],
        "explanation_templates": [
            "Group Hospital Cash provides daily cash benefit during hospitalisation, valuable for blue-collar and field workforce.",
        ],
    },

    "group_hospishield_plus": {
        "canonical_family": "employee_health",
        "product_name": "Group HospiShield Plus",
        "variant_type": "plus",
        "active_status": True,
        "sector_tags": [
            "SaaS / Enterprise Software", "Fintech", "Healthtech",
            "D2C / Consumer Brands", "HRtech",
        ],
        "required_exposures": ["headcount_total >= 5"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_workforce": True, "min_headcount": 5},
        "exposure_weights": {"headcount_tier": 0.9, "is_funded": 0.3},
        "trend_priors": 0.15,
        "wording_features": ["enhanced_hospitalisation", "day_care_procedures"],
        "penalties": {},
        "pair_rules": ["employers_liability"],
        "explanation_templates": [
            "HospiShield Plus provides enhanced hospitalisation cover with broader day-care and OPD benefits.",
        ],
    },

    "group_criti_shield_plus": {
        "canonical_family": "employee_health",
        "product_name": "Group Criti Shield Plus",
        "variant_type": "critical_illness",
        "active_status": True,
        "sector_tags": [
            "SaaS / Enterprise Software", "Fintech", "Healthtech", "HRtech",
        ],
        "required_exposures": ["headcount_total >= 10"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_workforce": True, "min_headcount": 10},
        "exposure_weights": {"headcount_tier": 0.7, "is_funded": 0.5},
        "trend_priors": 0.1,
        "wording_features": ["critical_illness_lump_sum"],
        "penalties": {},
        "pair_rules": [],
        "explanation_templates": [
            "Criti Shield Plus provides lump-sum critical illness benefit, important for retaining senior employees.",
        ],
    },

    "universal_protection": {
        "canonical_family": "employee_health",
        "product_name": "Universal Protection Insurance Policy",
        "variant_type": "universal",
        "active_status": True,
        "sector_tags": [
            "Logistics / Mobility", "Agritech", "Foodtech / Cloud Kitchen",
            "D2C / Consumer Brands",
        ],
        "required_exposures": ["headcount_total >= 5"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_workforce": True, "min_headcount": 5},
        "exposure_weights": {"blue_collar_tier": 0.7, "gig_tier": 0.5, "headcount_tier": 0.6},
        "trend_priors": 0.1,
        "wording_features": ["multi_benefit_group_cover"],
        "penalties": {},
        "pair_rules": ["employers_liability"],
        "explanation_templates": [
            "Universal Protection bundles health, accident, and life benefits into a single group product.",
        ],
    },

    "group_safeguard": {
        "canonical_family": "employee_health",
        "product_name": "Group Safeguard Insurance Policy",
        "variant_type": "standard",
        "active_status": True,
        "sector_tags": [
            "Logistics / Mobility", "D2C / Consumer Brands", "Agritech",
        ],
        "required_exposures": ["headcount_total >= 5"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_workforce": True, "min_headcount": 5},
        "exposure_weights": {"blue_collar_tier": 0.8, "headcount_tier": 0.6},
        "trend_priors": 0.1,
        "wording_features": ["group_life_accident_health"],
        "penalties": {},
        "pair_rules": ["employers_liability"],
        "explanation_templates": [
            "Group Safeguard combines life, accident, and health cover for blue-collar and field workforce.",
        ],
    },

    "group_safeguard_micro": {
        "canonical_family": "employee_health",
        "product_name": "Group Safeguard Micro Insurance Policy",
        "variant_type": "micro",
        "active_status": True,
        "sector_tags": ["Agritech", "Logistics / Mobility", "Foodtech / Cloud Kitchen"],
        "required_exposures": ["headcount_total >= 5"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_workforce": True, "min_headcount": 5},
        "exposure_weights": {"blue_collar_tier": 0.9, "gig_tier": 0.6, "is_early": 0.3},
        "trend_priors": 0.1,
        "wording_features": ["micro_group_life_accident"],
        "penalties": {},
        "pair_rules": ["employers_liability"],
        "explanation_templates": [
            "Group Safeguard Micro is a cost-effective option for small teams in low-formalisation sectors.",
        ],
    },

    # -------------------------------------------------------------------------
    # FAMILY: employers_liability
    # -------------------------------------------------------------------------

    "employers_liability_ec": {
        "canonical_family": "employers_liability",
        "product_name": "Employer's Liability / Workmen's Compensation / Employee's Compensation",
        "variant_type": "wc_ec",
        "active_status": True,
        "sector_tags": [
            "Logistics / Mobility", "D2C / Consumer Brands", "Foodtech / Cloud Kitchen",
            "Agritech", "Cleantech / Climatetech", "Deeptech / AI / Robotics",
        ],
        "required_exposures": ["headcount_total", "blue_collar_workers"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_workforce": True},
        "exposure_weights": {
            "blue_collar_tier": 1.5,
            "gig_tier": 1.0,
            "has_factory": 0.5,
            "has_warehouse": 0.3,
        },
        "trend_priors": 0.1,
        "wording_features": ["statutory_wc_cover", "occupational_disease", "medical_expenses"],
        "penalties": {},
        "pair_rules": ["employee_health", "general_or_modular_liability"],
        "explanation_templates": [
            "Employee's Compensation is mandatory under the Employee's Compensation Act 1923 for most physical workers.",
            "Field / blue-collar headcount of {headcount_blue_collar}+ creates direct WC obligation.",
        ],
    },

    "group_personal_accident": {
        "canonical_family": "employers_liability",
        "product_name": "Group Personal Accident",
        "variant_type": "gpa",
        "active_status": True,
        "sector_tags": [
            "SaaS / Enterprise Software", "Fintech", "Healthtech", "Logistics / Mobility",
            "D2C / Consumer Brands", "Agritech", "Cleantech / Climatetech",
        ],
        "required_exposures": ["headcount_total"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_workforce": True},
        "exposure_weights": {
            "headcount_tier": 0.8,
            "blue_collar_tier": 0.6,
            "has_factory": 0.3,
        },
        "trend_priors": 0.15,
        "wording_features": ["accidental_death_and_disability", "24hr_worldwide_cover"],
        "penalties": {},
        "pair_rules": ["employee_health"],
        "explanation_templates": [
            "Group PA provides low-cost accidental death and disability benefit — highly cost-effective for field and travelling workforce.",
        ],
    },

    # -------------------------------------------------------------------------
    # FAMILY: general_or_modular_liability
    # -------------------------------------------------------------------------

    "public_liability": {
        "canonical_family": "general_or_modular_liability",
        "product_name": "Public Liability Insurance",
        "variant_type": "standard",
        "active_status": True,
        "sector_tags": [
            "D2C / Consumer Brands", "Foodtech / Cloud Kitchen", "Logistics / Mobility",
            "Healthtech", "Agritech", "Cleantech / Climatetech",
        ],
        "required_exposures": ["any_physical_presence", "locations_count"],
        "forbidden_exposures": [],
        "hard_gates": {},
        "exposure_weights": {"any_physical": 0.5, "has_store": 0.4, "has_factory": 0.4, "locations_tier": 0.4},
        "trend_priors": 0.0,
        "wording_features": ["third_party_bi_pd", "premises_operations"],
        "penalties": {},
        "pair_rules": ["employers_liability", "property_fire"],
        "explanation_templates": [
            "Public Liability covers third-party bodily injury and property damage arising from premises or operations.",
        ],
    },

    "cgl_commercial": {
        "canonical_family": "general_or_modular_liability",
        "product_name": "Commercial General Liability Insurance",
        "variant_type": "commercial",
        "active_status": True,
        "sector_tags": [
            "SaaS / Enterprise Software", "Fintech", "Healthtech",
            "D2C / Consumer Brands", "Logistics / Mobility",
        ],
        "required_exposures": [],
        "forbidden_exposures": [],
        "hard_gates": {},
        "exposure_weights": {"any_physical": 0.3, "is_funded": 0.3, "headcount_tier": 0.2},
        "trend_priors": 0.1,
        "wording_features": ["products_completed_ops", "personal_advertising_injury", "medical_payments"],
        "penalties": {},
        "pair_rules": ["employers_liability", "professional_or_sector_liability"],
        "explanation_templates": [
            "Commercial General Liability is a broad-form policy covering products, completed operations, and advertising injury.",
        ],
    },

    "cgl_claims_basis": {
        "canonical_family": "general_or_modular_liability",
        "product_name": "Comprehensive General Liability claim basis",
        "variant_type": "claims_made",
        "active_status": True,
        "sector_tags": [
            "Fintech", "Healthtech", "SaaS / Enterprise Software", "Legaltech",
        ],
        "required_exposures": [],
        "forbidden_exposures": [],
        "hard_gates": {},
        "exposure_weights": {"is_funded": 0.4, "regulatory_intensity_tier": 0.3},
        "trend_priors": 0.1,
        "wording_features": ["claims_made_trigger", "retroactive_date", "extended_reporting"],
        "penalties": {},
        "pair_rules": ["professional_or_sector_liability"],
        "explanation_templates": [
            "Claims-made CGL is suited to professional services businesses — trigger date is when claim is made, not when incident occurs.",
        ],
    },

    "cgl_occurrence_basis": {
        "canonical_family": "general_or_modular_liability",
        "product_name": "Comprehensive General Liability occurrence basis",
        "variant_type": "occurrence",
        "active_status": True,
        "sector_tags": [
            "D2C / Consumer Brands", "Logistics / Mobility", "Agritech",
            "Foodtech / Cloud Kitchen",
        ],
        "required_exposures": [],
        "forbidden_exposures": [],
        "hard_gates": {},
        "exposure_weights": {"any_physical": 0.4, "has_factory": 0.3},
        "trend_priors": 0.1,
        "wording_features": ["occurrence_trigger", "long_tail_products_cover"],
        "penalties": {},
        "pair_rules": ["employers_liability"],
        "explanation_templates": [
            "Occurrence-basis CGL covers liability arising from incidents during the policy period, regardless of when the claim is filed.",
        ],
    },

    "i_elite_cgl_claims": {
        "canonical_family": "general_or_modular_liability",
        "product_name": "I-Elite Comprehensive General Liability claims based",
        "variant_type": "elite_claims_made",
        "active_status": True,
        "sector_tags": [
            "Fintech", "Healthtech", "SaaS / Enterprise Software",
        ],
        "required_exposures": [],
        "forbidden_exposures": [],
        "hard_gates": {"min_headcount": 25},
        "exposure_weights": {"is_funded": 0.5, "is_growth": 0.4, "regulatory_intensity_tier": 0.4},
        "trend_priors": 0.15,
        "wording_features": ["elite_limits", "claims_made", "defense_costs_included"],
        "penalties": {},
        "pair_rules": ["professional_or_sector_liability", "cyber"],
        "explanation_templates": [
            "I-Elite CGL (claims-made) offers higher limits and broader cover for larger organisations.",
        ],
    },

    "i_elite_cgl_occurrence": {
        "canonical_family": "general_or_modular_liability",
        "product_name": "I-Elite Comprehensive General Liability occurrence based",
        "variant_type": "elite_occurrence",
        "active_status": True,
        "sector_tags": [
            "D2C / Consumer Brands", "Logistics / Mobility", "Deeptech / AI / Robotics",
        ],
        "required_exposures": [],
        "forbidden_exposures": [],
        "hard_gates": {"min_headcount": 25},
        "exposure_weights": {"is_funded": 0.5, "has_factory": 0.3},
        "trend_priors": 0.15,
        "wording_features": ["elite_limits", "occurrence_trigger"],
        "penalties": {},
        "pair_rules": ["employers_liability"],
        "explanation_templates": [
            "I-Elite CGL (occurrence) provides premium limits for operations with long-tail product liability.",
        ],
    },

    "i_select_liability": {
        "canonical_family": "general_or_modular_liability",
        "product_name": "I-Select Liability Insurance",
        "variant_type": "modular",
        "active_status": True,
        "sector_tags": [
            "SaaS / Enterprise Software", "Fintech", "Healthtech", "HRtech", "Legaltech",
        ],
        "required_exposures": [],
        "forbidden_exposures": [],
        "hard_gates": {},
        "exposure_weights": {"is_funded": 0.4, "regulatory_intensity_tier": 0.4},
        "trend_priors": 0.1,
        "wording_features": ["modular_liability_pick_and_choose"],
        "penalties": {},
        "pair_rules": ["cyber", "professional_or_sector_liability"],
        "explanation_templates": [
            "I-Select allows bespoke combination of liability sections, useful for startups with mixed exposure profiles.",
        ],
    },

    # -------------------------------------------------------------------------
    # FAMILY: cyber
    # -------------------------------------------------------------------------

    "i_elite_cyber": {
        "canonical_family": "cyber",
        "product_name": "I-Elite Group Cyber Liability Insurance",
        "variant_type": "elite_group",
        "active_status": True,
        "sector_tags": [
            "Fintech", "Healthtech", "SaaS / Enterprise Software", "HRtech", "Legaltech",
        ],
        "required_exposures": ["handles_personal_data", "handles_financial_data"],
        "forbidden_exposures": [],
        "hard_gates": {"min_headcount": 50},
        "exposure_weights": {
            "handles_financial_data": 0.8, "handles_medical_data": 0.8,
            "transaction_tier": 0.6, "regulatory_intensity_tier": 0.5,
        },
        "trend_priors": 0.1,
        "wording_features": ["elite_cyber_limits", "breach_response", "regulatory_defense", "crisis_management"],
        "penalties": {},
        "pair_rules": ["professional_or_sector_liability", "general_or_modular_liability"],
        "explanation_templates": [
            "I-Elite Cyber offers the highest limits and broadest cyber wording for large data-intensive organisations.",
        ],
    },

    "cyber_secure": {
        "canonical_family": "cyber",
        "product_name": "Cyber Secure",
        "variant_type": "standard",
        "active_status": True,
        "sector_tags": [
            "SaaS / Enterprise Software", "Fintech", "Healthtech", "Edtech",
            "HRtech", "Legaltech", "Gaming / Media / Content",
        ],
        "required_exposures": ["handles_personal_data"],
        "forbidden_exposures": [],
        "hard_gates": {},
        "exposure_weights": {
            "handles_personal_data": 0.5, "handles_financial_data": 0.7,
            "uptime_dependency": 0.4, "stores_docs": 0.3,
        },
        "trend_priors": 0.2,
        "wording_features": ["breach_response", "ransomware_extortion", "network_security_liability"],
        "penalties": {},
        "pair_rules": ["professional_or_sector_liability"],
        "explanation_templates": [
            "Cyber Secure is the standard cyber liability product covering breach response, ransomware, and network security liability.",
            "Data handling ({data_types}) creates direct DPDPA and CERT-In regulatory exposure.",
        ],
    },

    "cyber_liability_commercial": {
        "canonical_family": "cyber",
        "product_name": "Cyber Liability / Commercial Cyber",
        "variant_type": "commercial",
        "active_status": True,
        "sector_tags": [
            "SaaS / Enterprise Software", "Fintech", "Healthtech", "D2C / Consumer Brands",
        ],
        "required_exposures": ["handles_personal_data"],
        "forbidden_exposures": [],
        "hard_gates": {},
        "exposure_weights": {
            "handles_personal_data": 0.5, "handles_medical_data": 0.7,
            "transaction_tier": 0.5, "regulatory_intensity_tier": 0.4,
        },
        "trend_priors": 0.2,
        "wording_features": ["commercial_cyber_limits", "media_liability_optional"],
        "penalties": {},
        "pair_rules": ["professional_or_sector_liability"],
        "explanation_templates": [
            "Commercial Cyber is a broader form with higher limits for businesses with significant third-party data obligations.",
        ],
    },

    # -------------------------------------------------------------------------
    # FAMILY: professional_or_sector_liability
    # -------------------------------------------------------------------------

    "healthcare_pi": {
        "canonical_family": "healthcare_liability",
        "product_name": "Healthcare and Medical Professional Liability",
        "variant_type": "healthcare_pi",
        "active_status": True,
        "sector_tags": ["Healthtech"],
        "required_exposures": ["healthcare_operations"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_healthcare_ops": True},
        "exposure_weights": {"healthcare_ops": 2.5, "regulatory_intensity_tier": 0.6},
        "trend_priors": 0.1,
        "wording_features": ["clinical_malpractice", "misdiagnosis_cover", "nmc_defense"],
        "penalties": {},
        "pair_rules": ["cyber", "employee_health"],
        "explanation_templates": [
            "Healthcare Professional Liability is essential for any clinic, hospital, diagnostic centre, or telemedicine provider.",
        ],
    },

    "financial_services_pi": {
        "canonical_family": "fintech_fi_liability",
        "product_name": "Financial Services / Institutions Professional Indemnity",
        "variant_type": "fs_pi",
        "active_status": True,
        "sector_tags": ["Fintech"],
        "required_exposures": ["handles_financial_data"],
        "forbidden_exposures": [],
        "hard_gates": {},
        "exposure_weights": {
            "handles_financial_data": 1.5, "regulatory_intensity_tier": 1.0, "is_funded": 0.3,
        },
        "trend_priors": 0.15,
        "wording_features": ["rbi_sebi_regulatory_defense", "investment_advice_cover", "custodian_liability"],
        "penalties": {},
        "pair_rules": ["cyber", "general_or_modular_liability"],
        "explanation_templates": [
            "Financial Services PI covers regulatory investigations, investment advice errors, and custodian liability for fintechs.",
        ],
    },

    "total_recall": {
        "canonical_family": "product_recall_contamination",
        "product_name": "Total Recall Contamination / Brand Protection Liability",
        "variant_type": "product_recall_contamination",
        "active_status": True,
        "sector_tags": ["Foodtech / Cloud Kitchen", "D2C / Consumer Brands", "Agritech"],
        "required_exposures": ["food_or_pharma_manufacturing"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_food_pharma": True},
        "exposure_weights": {"food_pharma_mfg": 2.5, "has_factory": 0.5},
        "trend_priors": 0.05,
        "wording_features": ["contamination_recall_costs", "brand_rehabilitation", "third_party_recall"],
        "penalties": {},
        "pair_rules": ["general_or_modular_liability", "property_fire"],
        "explanation_templates": [
            "Total Recall covers costs of product recall, contamination incidents, and brand rehabilitation for food/pharma manufacturers.",
        ],
    },

    "product_recall": {
        "canonical_family": "product_recall_contamination",
        "product_name": "Product Recall Guarantee and Financial Loss Liability",
        "variant_type": "product_recall",
        "active_status": True,
        "sector_tags": [
            "D2C / Consumer Brands", "Foodtech / Cloud Kitchen", "Deeptech / AI / Robotics",
        ],
        "required_exposures": ["food_or_pharma_manufacturing", "warranty_or_service_contract_obligation"],
        "forbidden_exposures": [],
        "hard_gates": {},
        "exposure_weights": {
            "food_pharma_mfg": 1.5, "warranty_obligation": 1.0, "has_factory": 0.4,
        },
        "trend_priors": 0.05,
        "wording_features": ["recall_costs", "financial_loss", "guarantee_obligations"],
        "penalties": {},
        "pair_rules": ["general_or_modular_liability"],
        "explanation_templates": [
            "Product Recall covers the cost of recalling defective products and associated financial loss.",
        ],
    },

    "representation_warranty": {
        "canonical_family": "professional_or_sector_liability",
        "product_name": "Representation and Warranty Insurance",
        "variant_type": "rw",
        "active_status": True,
        "sector_tags": [
            "SaaS / Enterprise Software", "Fintech", "Healthtech",
        ],
        "required_exposures": ["M_and_A_or_secondary_transaction"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_ma_transaction": True},
        "exposure_weights": {"ma_transaction": 3.5, "is_growth": 0.5},
        "trend_priors": 0.05,
        "wording_features": ["warranty_breach_indemnity", "seller_side_rw", "buyer_side_rw"],
        "penalties": {},
        "pair_rules": ["professional_or_sector_liability"],
        "explanation_templates": [
            "R&W Insurance bridges indemnity gaps in M&A transactions, increasingly required in PE-backed deals.",
        ],
    },

    "title_insurance": {
        "canonical_family": "professional_or_sector_liability",
        "product_name": "Title Insurance for Developers",
        "variant_type": "title",
        "active_status": True,
        "sector_tags": ["Cleantech / Climatetech"],
        "required_exposures": ["real_estate_development"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_real_estate_development": True},
        "exposure_weights": {"real_estate_dev": 3.5},
        "trend_priors": 0.0,
        "wording_features": ["title_defect_indemnity", "lender_protection"],
        "penalties": {},
        "pair_rules": ["engineering_project"],
        "explanation_templates": [
            "Title Insurance protects developers and lenders against title defects discovered after property acquisition.",
        ],
    },

    "service_contract_liability": {
        "canonical_family": "professional_or_sector_liability",
        "product_name": "Service Contract Liability Policy",
        "variant_type": "service_warranty",
        "active_status": True,
        "sector_tags": [
            "SaaS / Enterprise Software", "Deeptech / AI / Robotics", "D2C / Consumer Brands",
        ],
        "required_exposures": ["warranty_or_service_contract_obligation"],
        "forbidden_exposures": [],
        "hard_gates": {},
        "exposure_weights": {"warranty_obligation": 2.0, "is_funded": 0.3},
        "trend_priors": 0.05,
        "wording_features": ["service_warranty_obligations", "financial_loss_from_service_failure"],
        "penalties": {},
        "pair_rules": ["general_or_modular_liability"],
        "explanation_templates": [
            "Service Contract Liability covers financial loss from failure to meet warranty or service contract obligations.",
        ],
    },

    "surety_conditional": {
        "canonical_family": "surety_contract",
        "product_name": "Surety Insurance Conditional",
        "variant_type": "surety",
        "active_status": True,
        "sector_tags": [
            "Cleantech / Climatetech", "Deeptech / AI / Robotics", "Logistics / Mobility",
        ],
        "required_exposures": ["contract_bid_or_performance_bond_need"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_surety_or_construction": True},
        "exposure_weights": {"surety_bond_need": 3.0, "has_project": 0.5},
        "trend_priors": 0.1,
        "wording_features": ["bid_bond", "performance_bond", "advance_payment_bond"],
        "penalties": {},
        "pair_rules": ["engineering_project", "marine_logistics_credit"],
        "explanation_templates": [
            "Surety Insurance replaces cash security deposits for construction contracts, infrastructure bids, and government tenders.",
        ],
    },

    "drone_rpa": {
        "canonical_family": "professional_or_sector_liability",
        "product_name": "Remotely Piloted Aircraft Insurance",
        "variant_type": "drone",
        "active_status": True,
        "sector_tags": [
            "Agritech", "Logistics / Mobility", "Deeptech / AI / Robotics",
            "Cleantech / Climatetech",
        ],
        "required_exposures": ["drone_operations"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_drone_ops": True},
        "exposure_weights": {"drone_ops": 4.0},
        "trend_priors": 0.2,
        "wording_features": ["hull_cover", "third_party_liability_drone", "dgca_compliance"],
        "penalties": {},
        "pair_rules": ["employers_liability", "general_or_modular_liability"],
        "explanation_templates": [
            "DGCA mandates third-party liability cover for commercial drone operations — RPA Insurance satisfies this requirement.",
        ],
    },

    "art_insurance": {
        "canonical_family": "professional_or_sector_liability",
        "product_name": "Art Insurance – Commercial",
        "variant_type": "commercial",
        "active_status": True,
        "sector_tags": ["Gaming / Media / Content"],
        "required_exposures": [],
        "forbidden_exposures": [],
        "hard_gates": {},
        "exposure_weights": {"event_production_ops": 0.8, "is_funded": 0.2},
        "trend_priors": 0.0,
        "wording_features": ["fine_art_all_risk", "transit_cover"],
        "penalties": {},
        "pair_rules": [],
        "explanation_templates": [
            "Art Insurance – Commercial covers fine art and collectibles for media, entertainment, and creative organisations.",
        ],
    },

    "aviation": {
        "canonical_family": "professional_or_sector_liability",
        "product_name": "Aviation Insurance",
        "variant_type": "aviation",
        "active_status": True,
        "sector_tags": ["Logistics / Mobility", "Deeptech / AI / Robotics"],
        "required_exposures": ["drone_operations"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_aviation": True},
        "exposure_weights": {"drone_ops": 3.0},
        "trend_priors": 0.1,
        "wording_features": ["aircraft_hull", "aviation_liability", "passenger_liability"],
        "penalties": {},
        "pair_rules": ["general_or_modular_liability"],
        "explanation_templates": [
            "Aviation Insurance provides hull and liability cover for aviation and drone fleet operators.",
        ],
    },

    # -------------------------------------------------------------------------
    # FAMILY: engineering_project
    # -------------------------------------------------------------------------

    "car_standard": {
        "canonical_family": "engineering_project",
        "product_name": "Contractor's All Risk",
        "variant_type": "standard",
        "active_status": True,
        "sector_tags": [
            "Cleantech / Climatetech", "Deeptech / AI / Robotics", "Agritech",
            "Logistics / Mobility",
        ],
        "required_exposures": ["project_under_construction"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_project_or_installation": True},
        "exposure_weights": {"has_project": 2.0, "capex_tier": 1.0},
        "trend_priors": 0.0,
        "wording_features": ["construction_all_risk", "third_party_liability_section"],
        "penalties": {},
        "pair_rules": ["employers_liability", "marine_logistics_credit"],
        "explanation_templates": [
            "CAR covers damage to works under construction and third-party liability during the construction period.",
        ],
    },

    "car_commercial": {
        "canonical_family": "engineering_project",
        "product_name": "Contractor's All Risk – Commercial",
        "variant_type": "commercial",
        "active_status": True,
        "sector_tags": [
            "Cleantech / Climatetech", "Deeptech / AI / Robotics",
        ],
        "required_exposures": ["project_under_construction"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_project_or_installation": True},
        "exposure_weights": {"has_project": 2.0, "capex_tier": 1.2, "is_growth": 0.3},
        "trend_priors": 0.0,
        "wording_features": ["commercial_car_higher_limits"],
        "penalties": {},
        "pair_rules": ["employers_liability", "surety_contract"],
        "explanation_templates": [
            "Commercial CAR with higher limits for large construction projects.",
        ],
    },

    "ear_commercial": {
        "canonical_family": "engineering_project",
        "product_name": "Erection All Risks – Commercial",
        "variant_type": "commercial",
        "active_status": True,
        "sector_tags": [
            "Cleantech / Climatetech", "Deeptech / AI / Robotics",
        ],
        "required_exposures": ["installation_or_commissioning"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_project_or_installation": True},
        "exposure_weights": {"has_project": 2.5, "capex_tier": 1.2, "machinery_tier": 0.5},
        "trend_priors": 0.1,
        "wording_features": ["erection_machinery_all_risk", "testing_commissioning_cover"],
        "penalties": {},
        "pair_rules": ["employers_liability"],
        "explanation_templates": [
            "EAR covers machinery and plant erection, including testing and commissioning phase.",
        ],
    },

    "cecr_commercial": {
        "canonical_family": "engineering_project",
        "product_name": "Civil Engineering Completed Risks – Commercial",
        "variant_type": "commercial",
        "active_status": True,
        "sector_tags": ["Cleantech / Climatetech", "Logistics / Mobility"],
        "required_exposures": ["project_under_construction"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_project_or_installation": True},
        "exposure_weights": {"has_project": 2.0, "capex_tier": 0.8},
        "trend_priors": 0.0,
        "wording_features": ["completed_civil_works_cover"],
        "penalties": {},
        "pair_rules": [],
        "explanation_templates": [
            "CECR covers civil works (dams, tunnels, bridges) after completion against damage during maintenance period.",
        ],
    },

    "ear_car_alop": {
        "canonical_family": "engineering_project",
        "product_name": "EAR/CAR Advance Loss of Profit",
        "variant_type": "alop",
        "active_status": True,
        "sector_tags": [
            "Cleantech / Climatetech", "Deeptech / AI / Robotics",
        ],
        "required_exposures": ["project_under_construction", "capex_project_value"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_project_or_installation": True},
        # Lower has_project weight so base CAR/EAR products are preferred over ALOP.
        # ALOP is a supplementary cover; its edge comes from high capex (delay economics).
        "exposure_weights": {"has_project": 0.8, "capex_tier": 1.5, "is_growth": 0.4},
        "trend_priors": 0.1,
        "wording_features": ["delay_in_startup_business_interruption", "alop_cover"],
        "penalties": {},
        "pair_rules": ["marine_logistics_credit"],
        "explanation_templates": [
            "ALOP covers business interruption losses if a project delay causes deferred revenue start.",
        ],
    },

    "delay_startup_marine": {
        "canonical_family": "engineering_project",
        "product_name": "Delay in Start-up (Marine)",
        "variant_type": "marine_dst",
        "active_status": True,
        "sector_tags": [
            "Cleantech / Climatetech", "Logistics / Mobility",
        ],
        "required_exposures": ["project_under_construction"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_project_or_installation": True},
        # Reduced has_project weight: this product is a marine-delay supplement,
        # not the primary CAR/EAR cover. It wins only when shipment exposure is strong.
        "exposure_weights": {
            "has_project": 0.5, "capex_tier": 0.5,
            "has_export_shipments": 1.0, "has_import_dependency": 1.0,
        },
        "trend_priors": 0.05,
        "wording_features": ["marine_delay_startup_losses"],
        "penalties": {},
        "pair_rules": ["marine_logistics_credit"],
        "explanation_templates": [
            "Delay in Start-up (Marine) covers financial losses from project delays caused by marine cargo incidents.",
        ],
    },

    # -------------------------------------------------------------------------
    # FAMILY: marine_logistics_credit
    # -------------------------------------------------------------------------

    "marine_export_import": {
        "canonical_family": "marine_logistics_credit",
        "product_name": "Marine Export Import Insurance / Open",
        "variant_type": "open_cover",
        "active_status": True,
        "sector_tags": [
            "D2C / Consumer Brands", "Logistics / Mobility", "Agritech",
            "Cleantech / Climatetech", "Deeptech / AI / Robotics",
        ],
        "required_exposures": ["export_shipments", "import_dependency"],
        "forbidden_exposures": [],
        "hard_gates": {},
        "exposure_weights": {
            "has_export_shipments": 1.5, "has_import_dependency": 1.0,
            "has_domestic_shipments": 0.5,
        },
        "trend_priors": 0.1,
        "wording_features": ["open_marine_policy", "all_risk_cargo", "icc_a_conditions"],
        "penalties": {},
        "pair_rules": ["marine_logistics_credit"],
        "explanation_templates": [
            "Marine Export/Import Open Cover provides automatic cover for all cargo shipments under an annual policy.",
        ],
    },

    "marine_transit_inland": {
        "canonical_family": "marine_logistics_credit",
        "product_name": "Marine Transit Insurance (Inland)",
        "variant_type": "inland_transit",
        "active_status": True,
        "sector_tags": [
            "Logistics / Mobility", "D2C / Consumer Brands", "Agritech",
            "Foodtech / Cloud Kitchen",
        ],
        "required_exposures": ["domestic_shipments"],
        "forbidden_exposures": [],
        "hard_gates": {},
        "exposure_weights": {"has_domestic_shipments": 1.5, "goods_vehicle_tier": 0.6},
        "trend_priors": 0.05,
        "wording_features": ["inland_transit_all_risk", "road_rail_cover"],
        "penalties": {},
        "pair_rules": ["commercial_motor_fleet"],
        "explanation_templates": [
            "Marine Inland Transit covers goods in transit by road, rail, or inland waterway.",
        ],
    },

    "marine_hull": {
        "canonical_family": "marine_logistics_credit",
        "product_name": "Marine Hull Policy",
        "variant_type": "hull",
        "active_status": True,
        "sector_tags": ["Logistics / Mobility"],
        "required_exposures": ["port_or_maritime_operations"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_port_maritime": True},
        "exposure_weights": {"port_maritime": 3.0},
        "trend_priors": 0.0,
        "wording_features": ["vessel_hull_machinery", "collision_liability"],
        "penalties": {},
        "pair_rules": ["marine_logistics_credit"],
        "explanation_templates": [
            "Marine Hull covers loss or damage to owned vessels.",
        ],
    },

    "marine_hull_los": {
        "canonical_family": "marine_logistics_credit",
        "product_name": "Marine Hull Loss of Earnings / Hire",
        "variant_type": "loss_of_hire",
        "active_status": True,
        "sector_tags": ["Logistics / Mobility"],
        "required_exposures": ["port_or_maritime_operations"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_port_maritime": True},
        "exposure_weights": {"port_maritime": 2.5, "revenue_tier": 0.4},
        "trend_priors": 0.0,
        "wording_features": ["loss_of_hire_from_vessel_damage"],
        "penalties": {},
        "pair_rules": ["marine_hull"],
        "explanation_templates": [
            "Loss of Earnings / Hire covers revenue lost when a vessel is off-hire due to an insured damage event.",
        ],
    },

    "protection_indemnity": {
        "canonical_family": "marine_logistics_credit",
        "product_name": "Protection & Indemnity",
        "variant_type": "pi_marine",
        "active_status": True,
        "sector_tags": ["Logistics / Mobility"],
        "required_exposures": ["port_or_maritime_operations"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_port_maritime": True},
        "exposure_weights": {"port_maritime": 3.0, "headcount_tier": 0.3},
        "trend_priors": 0.0,
        "wording_features": ["crew_liability", "cargo_liability_marine", "pollution_maritime"],
        "penalties": {},
        "pair_rules": ["marine_hull"],
        "explanation_templates": [
            "P&I covers shipowners' liabilities to crew, cargo claimants, and pollution regulators.",
        ],
    },

    "trade_credit": {
        "canonical_family": "marine_logistics_credit",
        "product_name": "Trade Credit Insurance",
        "variant_type": "trade_credit",
        "active_status": True,
        "sector_tags": [
            "SaaS / Enterprise Software", "Fintech", "D2C / Consumer Brands",
            "Logistics / Mobility", "Agritech",
        ],
        "required_exposures": ["receivables_on_credit"],
        "forbidden_exposures": [],
        "hard_gates": {},
        "exposure_weights": {
            "receivables_tier": 2.0, "invoice_cycle_tier": 0.6,
            "has_export_shipments": 0.4,
        },
        "trend_priors": 0.15,
        "wording_features": ["buyer_insolvency", "protracted_default", "political_risk_included"],
        "penalties": {},
        "pair_rules": ["marine_export_import"],
        "explanation_templates": [
            "Trade Credit protects against buyer insolvency and protracted non-payment on B2B receivables.",
        ],
    },

    "political_risk": {
        "canonical_family": "marine_logistics_credit",
        "product_name": "Political Risk Insurance",
        "variant_type": "political_risk",
        "active_status": True,
        "sector_tags": [
            "Fintech", "SaaS / Enterprise Software", "Logistics / Mobility",
        ],
        "required_exposures": ["export_shipments"],
        "forbidden_exposures": [],
        "hard_gates": {},
        "exposure_weights": {
            "has_export_shipments": 1.5, "regulatory_intensity_tier": 0.5,
        },
        "trend_priors": 0.1,
        "wording_features": ["confiscation_expropriation", "currency_inconvertibility"],
        "penalties": {},
        "pair_rules": ["trade_credit"],
        "explanation_templates": [
            "Political Risk Insurance covers expropriation, currency inconvertibility, and political violence for cross-border exposures.",
        ],
    },

    "credit_fi": {
        "canonical_family": "marine_logistics_credit",
        "product_name": "Credit Insurance – Financial Institutions",
        "variant_type": "fi_credit",
        "active_status": True,
        "sector_tags": ["Fintech"],
        "required_exposures": ["handles_financial_data"],
        "forbidden_exposures": [],
        "hard_gates": {},
        "exposure_weights": {
            "handles_financial_data": 1.5, "receivables_tier": 1.0, "regulatory_intensity_tier": 0.6,
        },
        "trend_priors": 0.1,
        "wording_features": ["loan_portfolio_credit_risk", "bank_guarantees"],
        "penalties": {},
        "pair_rules": ["professional_or_sector_liability"],
        "explanation_templates": [
            "Credit Insurance for Financial Institutions protects loan portfolios and financial guarantees against default.",
        ],
    },

    # -------------------------------------------------------------------------
    # FAMILY: commercial_motor_fleet
    # -------------------------------------------------------------------------

    "goods_carrying_vehicle": {
        "canonical_family": "commercial_motor_fleet",
        "product_name": "Goods Carrying Vehicle Package Policy",
        "variant_type": "gcv",
        "active_status": True,
        "sector_tags": ["Logistics / Mobility", "D2C / Consumer Brands", "Agritech"],
        "required_exposures": ["goods_vehicle_count"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_vehicles": True},
        "exposure_weights": {"goods_vehicle_tier": 2.5, "vehicle_tier": 0.5},
        "trend_priors": 0.05,
        "wording_features": ["gcv_act_liability", "own_damage_optional", "transit_cargo_optional"],
        "penalties": {},
        "pair_rules": ["employers_liability", "marine_transit_inland"],
        "explanation_templates": [
            "GCV Policy covers goods-carrying vehicles for Act Liability (mandatory) and optional own damage.",
        ],
    },

    "miscellaneous_vehicle": {
        "canonical_family": "commercial_motor_fleet",
        "product_name": "Miscellaneous Vehicle Package Policy",
        "variant_type": "misc_vehicle",
        "active_status": True,
        "sector_tags": ["Logistics / Mobility", "Cleantech / Climatetech"],
        "required_exposures": ["miscellaneous_vehicle_count"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_vehicles": True},
        "exposure_weights": {"vehicle_tier": 1.5},
        "trend_priors": 0.0,
        "wording_features": ["miscellaneous_motor_cover"],
        "penalties": {},
        "pair_rules": ["employers_liability"],
        "explanation_templates": [
            "Miscellaneous Vehicle Package covers non-standard vehicles such as construction equipment and agri-machinery.",
        ],
    },

    "trailer_package": {
        "canonical_family": "commercial_motor_fleet",
        "product_name": "Trailer Package Policy",
        "variant_type": "trailer",
        "active_status": True,
        "sector_tags": ["Logistics / Mobility"],
        "required_exposures": ["trailer_count"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_vehicles": True},
        "exposure_weights": {"has_trailer": 3.0, "vehicle_tier": 0.5},
        "trend_priors": 0.0,
        "wording_features": ["trailer_own_damage_liability"],
        "penalties": {},
        "pair_rules": ["goods_carrying_vehicle"],
        "explanation_templates": [
            "Trailer Package provides cover for trailers and semi-trailers including own damage and third-party liability.",
        ],
    },

    "bundled_two_wheeler": {
        "canonical_family": "commercial_motor_fleet",
        "product_name": "Bundled Two Wheeler Policy",
        "variant_type": "two_wheeler_bundled",
        "active_status": True,
        "sector_tags": ["Logistics / Mobility", "D2C / Consumer Brands", "Foodtech / Cloud Kitchen"],
        "required_exposures": ["two_wheeler_count"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_vehicles": True},
        "exposure_weights": {"has_two_wheeler": 3.0},
        "trend_priors": 0.0,
        "wording_features": ["two_wheeler_od_tp_combined"],
        "penalties": {},
        "pair_rules": ["employers_liability"],
        "explanation_templates": [
            "Bundled Two Wheeler Policy (5-year TP + 1-year OD) for delivery and field two-wheeler fleets.",
        ],
    },

    "two_wheeler_package": {
        "canonical_family": "commercial_motor_fleet",
        "product_name": "Two Wheeler Vehicle Package Policy",
        "variant_type": "two_wheeler_package",
        "active_status": True,
        "sector_tags": ["Logistics / Mobility", "Foodtech / Cloud Kitchen"],
        "required_exposures": ["two_wheeler_count"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_vehicles": True},
        "exposure_weights": {"has_two_wheeler": 3.0},
        "trend_priors": 0.0,
        "wording_features": ["two_wheeler_package_cover"],
        "penalties": {},
        "pair_rules": ["employers_liability"],
        "explanation_templates": [
            "Two Wheeler Package Policy for individual two-wheelers in delivery / gig operations.",
        ],
    },

    # -------------------------------------------------------------------------
    # FAMILY: payment_card_network_specialty
    # -------------------------------------------------------------------------

    "card_package_commercial": {
        "canonical_family": "payment_card_network_specialty",
        "product_name": "Credit/Debit/ATM Card Package Insurance Policy – Commercial",
        "variant_type": "card_commercial",
        "active_status": True,
        "sector_tags": ["Fintech"],
        "required_exposures": ["payment_or_card_program"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_payment_or_card_program": True},
        "exposure_weights": {"payment_card_program": 3.0, "transaction_tier": 0.8},
        "trend_priors": 0.1,
        "wording_features": ["card_fraud_counterfeit", "atm_robbery", "skimming"],
        "penalties": {},
        "pair_rules": ["cyber"],
        "explanation_templates": [
            "Card Package Commercial covers fraud, counterfeit, ATM robbery, and skimming for card programme operators.",
        ],
    },

    "consumer_payment_protection_commercial": {
        "canonical_family": "payment_card_network_specialty",
        "product_name": "Consumer Payment Protection Policy – Commercial",
        "variant_type": "payment_protection_commercial",
        "active_status": True,
        "sector_tags": ["Fintech"],
        "required_exposures": ["payment_or_card_program"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_payment_or_card_program": True},
        "exposure_weights": {"payment_card_program": 3.0, "handles_financial_data": 0.6},
        "trend_priors": 0.1,
        "wording_features": ["consumer_payment_protection", "unauthorized_transactions"],
        "penalties": {},
        "pair_rules": ["cyber"],
        "explanation_templates": [
            "Consumer Payment Protection Commercial covers losses from unauthorised transactions and payment fraud.",
        ],
    },

    "consumer_payment_protection_package": {
        "canonical_family": "payment_card_network_specialty",
        "product_name": "Consumer Payment Protection Package Policy",
        "variant_type": "payment_protection_package",
        "active_status": True,
        "sector_tags": ["Fintech"],
        "required_exposures": ["payment_or_card_program"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_payment_or_card_program": True},
        "exposure_weights": {"payment_card_program": 3.0, "transaction_tier": 0.6},
        "trend_priors": 0.1,
        "wording_features": ["bundled_payment_protection"],
        "penalties": {},
        "pair_rules": ["cyber"],
        "explanation_templates": [
            "Consumer Payment Protection Package bundles multiple payment fraud covers in a single product.",
        ],
    },

    "cellular_network": {
        "canonical_family": "payment_card_network_specialty",
        "product_name": "Cellular Network Insurance Policy",
        "variant_type": "telecom",
        "active_status": True,
        "sector_tags": ["SaaS / Enterprise Software"],
        "required_exposures": ["telecom_network_assets"],
        "forbidden_exposures": [],
        "hard_gates": {"requires_telecom_network": True},
        "exposure_weights": {"telecom_network": 4.0},
        "trend_priors": 0.0,
        "wording_features": ["telecom_network_property_liability"],
        "penalties": {},
        "pair_rules": ["cyber"],
        "explanation_templates": [
            "Cellular Network Insurance covers telecom infrastructure including towers, cable, and network equipment.",
        ],
    },
}


# ============================================================================
# PAIR RULES
# ============================================================================
# Format: (trigger_family, boost_family, condition_key, delta_z, reason)
#   trigger_family  : if this family scores >= threshold
#   boost_family    : add delta_z to this family's z-score
#   condition_key   : exposure feature that must be > 0 to activate the rule
#   delta_z         : additive boost to z-score of boost_family
#   reason          : human-readable explanation for why the pair is recommended
# ============================================================================

PAIR_RULES: List[Dict[str, Any]] = [
    {
        "trigger_family": "general_or_modular_liability",
        "boost_family": "employers_liability",
        "condition_key": "has_workforce",
        "delta_z": 0.6,
        "reason": "CGL does not replace Employer's Liability; separate EC cover is needed for workforce injury claims.",
    },
    {
        "trigger_family": "general_or_modular_liability",
        "boost_family": "property_fire",
        "condition_key": "asset_tier",
        "delta_z": 0.4,
        "reason": "Public liability exposure from premises suggests significant insurable physical assets worth protecting.",
    },
    {
        "trigger_family": "engineering_project",
        "boost_family": "marine_logistics_credit",
        "condition_key": "has_project",
        "delta_z": 0.9,
        "reason": "Construction projects with imported machinery create marine transit and ALOP delay exposure.",
    },
    {
        "trigger_family": "employee_health",
        "boost_family": "employers_liability",
        "condition_key": "blue_collar_tier",
        "delta_z": 0.5,
        "reason": "Group Health does not satisfy EC Act obligations for blue-collar workers; both covers are needed.",
    },
    {
        "trigger_family": "marine_logistics_credit",
        "boost_family": "commercial_motor_fleet",
        "condition_key": "goods_vehicle_tier",
        "delta_z": 0.4,
        "reason": "Goods-in-transit exposure from shipments is often paired with a fleet motor policy for end-to-end cover.",
    },
    {
        "trigger_family": "cyber",
        "boost_family": "fintech_fi_liability",
        "condition_key": "regulatory_intensity_tier",
        "delta_z": 0.5,
        "reason": "High cyber risk in a regulated sector usually co-exists with regulatory defense and PI exposure.",
    },
    {
        "trigger_family": "cyber",
        "boost_family": "healthcare_liability",
        "condition_key": "handles_medical_data",
        "delta_z": 0.5,
        "reason": "Medical data exposure usually co-exists with clinical liability and patient-care obligations.",
    },
    {
        "trigger_family": "marine_logistics_credit",
        "boost_family": "marine_logistics_credit",
        "condition_key": "receivables_tier",
        "delta_z": 0.4,
        "reason": "High export receivables signal simultaneous Trade Credit + Marine Insurance need.",
    },
    {
        "trigger_family": "engineering_project",
        "boost_family": "surety_contract",
        "condition_key": "surety_bond_need",
        "delta_z": 0.6,
        "reason": "EPC/contractor projects frequently require both CAR and Surety Insurance for bid and performance bonds.",
    },
    {
        "trigger_family": "employers_liability",
        "boost_family": "employee_health",
        "condition_key": "headcount_tier",
        "delta_z": 0.4,
        "reason": "Employee's Compensation covers statutory liability; Group Health addresses employee welfare — both are typically placed together.",
    },
    {
        "trigger_family": "commercial_motor_fleet",
        "boost_family": "employers_liability",
        "condition_key": "has_workforce",
        "delta_z": 0.3,
        "reason": "Fleet operators with drivers have direct Workmen's Compensation obligations under the EC Act.",
    },
]


# ============================================================================
# TREND PRIORS  (family-level baseline adjustments beyond product priors)
# ============================================================================
# Encode macro risk trends as small non-overriding additive constants.

TREND_PRIORS: Dict[str, float] = {
    "cyber":                        0.30,   # rising breach frequency in India (CERT-In 2022+)
    "employee_health":              0.20,   # talent retention benchmark for funded startups
    "general_or_modular_liability": 0.10,   # increasing contract liability requirements
    "marine_logistics_credit":      0.10,   # trade credit adoption growing in B2B India
    "professional_or_sector_liability": 0.10,
    "engineering_project":          0.05,
    "property_fire":                0.10,   # climate zone losses driving take-up
    "employers_liability":          0.10,
    "core_business_package":        0.10,
    "commercial_motor_fleet":       0.05,
    "payment_card_network_specialty": 0.10,
    "healthcare_liability":         0.15,
    "fintech_fi_liability":         0.20,
    "product_recall_contamination": 0.10,
    "surety_contract":              0.10,
    "media_production":             0.05,
}
