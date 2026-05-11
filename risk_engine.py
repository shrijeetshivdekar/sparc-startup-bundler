"""
risk_engine.py — SPARC core logic (v2 — regulatory audit rebuild)
All sector profiles, product catalog, risk scoring, and recommendation logic lives here.
Import this module in startup_risk_app.py and retest.py.

v2 changes: 5 → 13 risk categories, StartupInput dataclass, sub-sector taxonomy,
20 new scoring variables, 8 new recommendation triggers, hard-decline logic,
REGULATORY_CITATIONS dict for explainability.
"""
import math
import decimal
import warnings
from dataclasses import dataclass, field
from typing import Optional, List


# =============================================================================
# STARTUP INPUT DATACLASS
# =============================================================================
@dataclass
class StartupInput:
    # ── EXISTING (preserved) ──────────────────────────────────────────────────
    sector: str
    funding_stage: str                      # "Pre-seed" | "Seed" | "Series A" | "Series B+"
    team_size: int
    operations: str                         # "Digital-only" | "Physical-only" | "Hybrid"
    data_sensitivity: str                   # "Low" | "Medium" | "High"

    # ── NEW: Sub-sector ───────────────────────────────────────────────────────
    sub_sector: Optional[str] = None        # e.g. "Fintech.NBFC_Digital_Lending"

    # ── NEW: Revenue & market mix ─────────────────────────────────────────────
    export_eu_pct: float = 0.0              # % revenue from EU — CBAM trigger
    export_us_pct: float = 0.0
    export_china_pct: float = 0.0
    b2b_pct: float = 0.5                    # 0-1; B2B elevates PI / CGL

    # ── NEW: Workforce ────────────────────────────────────────────────────────
    gig_headcount_pct: float = 0.0          # gig/contractor % of total workforce
    posh_ic_constituted: bool = False       # POSH Act 2013 §4 IC formed?
    cert_in_poc_designated: bool = False    # CERT-In 2022 POC designated?

    # ── NEW: Capital & governance ─────────────────────────────────────────────
    investor_cn_hk_pct: float = 0.0         # BO % from China/HK — PN3 flag
    cumulative_fundraising_inr_cr: float = 0.0  # DVT ₹2,000cr Competition Act flag
    holdco_domicile: str = "India"          # "India" | "DE" | "SG" | "Cayman" | "Flip_pending"
    founder_concentration_index: float = 0.5    # (founder_equity_pct) × (1 − indep_director_pct)

    # ── NEW: Data & product ───────────────────────────────────────────────────
    sdf_probability: float = 0.0            # 0-1; DPDPA §10 SDF designation likelihood
    data_localisation_status: str = "Unknown"  # "Full_onshore"|"Hybrid"|"Offshore"|"Unknown"
    ai_in_product: bool = False             # MeitY AI Advisory + SGI Rules trigger
    hardware_software_split: float = 0.0    # % of revenue from physical hardware/product

    # ── NEW: Regulatory registration ─────────────────────────────────────────
    rbi_registration: Optional[str] = None  # "NBFC"|"PA"|"PPI"|"RIA"|"AA"|None
    dpiit_recognition: bool = False

    # ── NEW: Geographic & supply chain ────────────────────────────────────────
    state_footprint: List[str] = field(default_factory=list)
    chinese_supplier_pct_cogs: float = 0.0
    listed_customer_brsr_dependency: bool = False  # SEBI BRSR value-chain push-through

    # ── NEW: Environment ──────────────────────────────────────────────────────
    facility_climate_risk_zone: str = "Low"     # "Low"|"Medium"|"High"|"Extreme"


# =============================================================================
# SECTOR PROFILES — 13 sectors × 13 scoring dimensions + emoji + description
# =============================================================================
SECTOR_PROFILES = {
    "SaaS / Enterprise Software": {
        "cyber_technical": 8, "data_privacy": 8,
        "liability": 8, "ip_infringement": 7,
        "key_person": 5, "governance_fraud": 5,
        "property": 2, "regulatory_compliance": 8,
        "esg_climate": 2, "geopolitical": 6,
        "gig_labour": 2, "policy_velocity": 6,
        "reputation": 6, "tax_tp": 5,
        "emoji": "💻",
        "description": "Digital-first, enterprise contracts, SDF-likely, CERT-In exposure.",
    },
    "Fintech": {
        "cyber_technical": 10, "data_privacy": 10,
        "liability": 9, "ip_infringement": 5,
        "key_person": 8, "governance_fraud": 9,
        "property": 3, "regulatory_compliance": 10,
        "esg_climate": 3, "geopolitical": 8,
        "gig_labour": 5, "policy_velocity": 9,
        "reputation": 9, "tax_tp": 8,
        "emoji": "💳",
        "description": "RBI/SEBI regulated, high cyber+governance exposure, PN3 sensitive.",
    },
    "Healthtech": {
        "cyber_technical": 10, "data_privacy": 9,
        "liability": 9, "ip_infringement": 8,
        "key_person": 6, "governance_fraud": 7,
        "property": 5, "regulatory_compliance": 9,
        "esg_climate": 4, "geopolitical": 6,
        "gig_labour": 5, "policy_velocity": 8,
        "reputation": 8, "tax_tp": 5,
        "emoji": "🏥",
        "description": "Patient data, SaMD classification risk, DPDPA + CDSCO + NMC exposure.",
    },
    "D2C / Consumer Brands": {
        "cyber_technical": 7, "data_privacy": 6,
        "liability": 8, "ip_infringement": 6,
        "key_person": 4, "governance_fraud": 7,
        "property": 8, "regulatory_compliance": 9,
        "esg_climate": 6, "geopolitical": 9,
        "gig_labour": 6, "policy_velocity": 5,
        "reputation": 8, "tax_tp": 6,
        "emoji": "🛍️",
        "description": "BIS QCO, LMPC, EPR, CBAM EU-export, CCPA dark-patterns exposure.",
    },
    "Deeptech / AI / Robotics": {
        "cyber_technical": 7, "data_privacy": 7,
        "liability": 7, "ip_infringement": 10,
        "key_person": 8, "governance_fraud": 5,
        "property": 7, "regulatory_compliance": 8,
        "esg_climate": 7, "geopolitical": 10,
        "gig_labour": 2, "policy_velocity": 7,
        "reputation": 6, "tax_tp": 6,
        "emoji": "🤖",
        "description": "IP-heavy, dual-use export controls, EU AI Act extraterritorial, drone-reg.",
    },
    "Edtech": {
        "cyber_technical": 7, "data_privacy": 8,
        "liability": 8, "ip_infringement": 6,
        "key_person": 7, "governance_fraud": 10,
        "property": 3, "regulatory_compliance": 9,
        "esg_climate": 2, "geopolitical": 6,
        "gig_labour": 4, "policy_velocity": 7,
        "reputation": 9, "tax_tp": 5,
        "emoji": "📚",
        "description": "CCPA consumer complaints, MoE Coaching Guidelines, DPDPA §9 minor-data, governance crisis.",
    },
    "Agritech": {
        "cyber_technical": 4, "data_privacy": 5,
        "liability": 6, "ip_infringement": 4,
        "key_person": 5, "governance_fraud": 6,
        "property": 8, "regulatory_compliance": 8,
        "esg_climate": 9, "geopolitical": 5,
        "gig_labour": 5, "policy_velocity": 5,
        "reputation": 4, "tax_tp": 4,
        "emoji": "🌾",
        "description": "APMC/EC-Act patchwork, drone dual-reg, highest physical-climate risk.",
    },
    "Cleantech / Climatetech": {
        "cyber_technical": 5, "data_privacy": 4,
        "liability": 7, "ip_infringement": 7,
        "key_person": 6, "governance_fraud": 6,
        "property": 9, "regulatory_compliance": 9,
        "esg_climate": 10, "geopolitical": 7,
        "gig_labour": 3, "policy_velocity": 5,
        "reputation": 6, "tax_tp": 6,
        "emoji": "🌱",
        "description": "ALMM supply-risk, CCTS carbon-market, CBAM EU-export, Battery Waste EPR.",
    },
    "Logistics / Mobility": {
        "cyber_technical": 6, "data_privacy": 6,
        "liability": 10, "ip_infringement": 3,
        "key_person": 4, "governance_fraud": 5,
        "property": 8, "regulatory_compliance": 10,
        "esg_climate": 8, "geopolitical": 6,
        "gig_labour": 10, "policy_velocity": 4,
        "reputation": 7, "tax_tp": 5,
        "emoji": "🚚",
        "description": "MV Act unlimited TP, Aggregator Guidelines 2025, gig-worker Acts, EV Battery-EPR.",
    },
    "Legaltech": {
        "cyber_technical": 7, "data_privacy": 8,
        "liability": 9, "ip_infringement": 7,
        "key_person": 5, "governance_fraud": 4,
        "property": 2, "regulatory_compliance": 9,
        "esg_climate": 1, "geopolitical": 3,
        "gig_labour": 3, "policy_velocity": 7,
        "reputation": 8, "tax_tp": 4,
        "emoji": "⚖️",
        "description": "AI-legal liability, Advocates Act unauthorised practice, privileged-data DPDPA.",
    },
    "HRtech": {
        "cyber_technical": 8, "data_privacy": 9,
        "liability": 6, "ip_infringement": 4,
        "key_person": 5, "governance_fraud": 5,
        "property": 2, "regulatory_compliance": 9,
        "esg_climate": 2, "geopolitical": 4,
        "gig_labour": 8, "policy_velocity": 6,
        "reputation": 7, "tax_tp": 6,
        "emoji": "👥",
        "description": "Labour Codes 2025, SS Code aggregator levy, payroll-PII DPDPA exposure.",
    },
    "Gaming / Media / Content": {
        "cyber_technical": 6, "data_privacy": 7,
        "liability": 9, "ip_infringement": 8,
        "key_person": 5, "governance_fraud": 8,
        "property": 3, "regulatory_compliance": 10,
        "esg_climate": 2, "geopolitical": 7,
        "gig_labour": 2, "policy_velocity": 10,
        "reputation": 9, "tax_tp": 9,
        "emoji": "🎮",
        "description": "Online Gaming Act 2025, 28% GST face-value, IP risk, RMG prohibition exposure.",
    },
    "Foodtech / Cloud Kitchen": {
        "cyber_technical": 6, "data_privacy": 6,
        "liability": 9, "ip_infringement": 4,
        "key_person": 4, "governance_fraud": 6,
        "property": 8, "regulatory_compliance": 10,
        "esg_climate": 7, "geopolitical": 5,
        "gig_labour": 10, "policy_velocity": 6,
        "reputation": 10, "tax_tp": 6,
        "emoji": "🍔",
        "description": "FSSAI per-location, MV Aggregator 2025, gig Acts, food-safety reputation risk.",
    },
}


# =============================================================================
# SUB-SECTOR PROFILES — weight overrides for high-heterogeneity sub-sectors
# Values are absolute (not deltas), capped at 10.
# Keys starting with "_" are metadata, not scoring dimensions.
# =============================================================================
SUB_SECTOR_PROFILES = {
    # ── FINTECH ───────────────────────────────────────────────────────────────
    "Fintech.NBFC_Digital_Lending": {
        "regulatory_compliance": 10, "governance_fraud": 10, "liability": 10,
        "data_privacy": 10, "policy_velocity": 10,
        "_note": "RBI Digital Lending Directions 8-May-2025; DLG cap; CIMS reporting 15-Jun-2025",
    },
    "Fintech.PA_PG": {
        "regulatory_compliance": 10, "geopolitical": 9, "governance_fraud": 9,
        "_note": "PA Directions 15-Sep-2025; PA-CB 31-Oct-2023; FIU-IND AML",
    },
    "Fintech.PA_Cross_Border": {
        "regulatory_compliance": 10, "geopolitical": 10, "governance_fraud": 9, "policy_velocity": 9,
        "_note": "PA-CB 31-Oct-2023; PMLA reporting entity; FEMA cross-border settlement",
    },
    "Fintech.WealthTech_EOP": {
        "regulatory_compliance": 9, "liability": 9, "governance_fraud": 8,
        "_note": "SEBI EOP Framework 13-Jun-2023; SEBI Investment Adviser Regulations",
    },
    "Fintech.Neobank_PPI": {
        "regulatory_compliance": 9, "data_privacy": 9, "cyber_technical": 9,
        "_note": "RBI PPI Master Directions 2021; interoperability mandate",
    },
    "Fintech.InsurTech": {
        "regulatory_compliance": 9, "liability": 8, "policy_velocity": 8,
        "_note": "IRDAI Bima Sugam Regs 20-Mar-2024; Bima Vistaar; Use-&-File",
    },
    "Fintech.Account_Aggregator": {
        "regulatory_compliance": 10, "data_privacy": 10, "cyber_technical": 10,
        "_note": "NBFC-AA MD 2016; DPDPA §8 consent-manager obligations",
    },
    # ── HEALTHTECH ────────────────────────────────────────────────────────────
    "Healthtech.Telemedicine": {
        "liability": 10, "regulatory_compliance": 10,
        "_note": "NMC Telemedicine Guidelines 2020 + 2025 Amendment; DPDPA health-data",
    },
    "Healthtech.Diagnostics": {
        "liability": 9, "regulatory_compliance": 9, "ip_infringement": 7,
        "_note": "NABL accreditation; MDR 2017 IVD classification",
    },
    "Healthtech.PharmaTech_ePharmacy": {
        "regulatory_compliance": 10, "liability": 9, "reputation": 9,
        "_note": "Drugs & Cosmetics Act; Drugs Rules 1945; e-pharmacy draft rules",
    },
    "Healthtech.MedDevice_SaMD": {
        "regulatory_compliance": 10, "liability": 10, "ip_infringement": 9, "policy_velocity": 9,
        "_note": "CDSCO SaMD Draft Guidance 21-Oct-2025; Class B/C/D; S.O. 648(E) 11-Feb-2020",
        "_auto_include": ["clinical_trials", "product_liability"],
        "_decline_without_cdsco_licence": True,
    },
    "Healthtech.Clinical_Trials_SaaS": {
        "regulatory_compliance": 10, "liability": 10,
        "_note": "CDSCO NDCT Rules 2019; ICH-GCP; mandatory coverage pre-trial",
        "_auto_include": ["clinical_trials"],
    },
    # ── GAMING ────────────────────────────────────────────────────────────────
    "Gaming.Real_Money": {
        "_hard_decline": True,
        "_reason": (
            "Promotion & Regulation of Online Gaming Act 2025 (assented 22-Aug-2025) "
            "§5 blanket prohibition; §7 criminal liability for PSPs/banks. "
            "Revisit post-SC ruling."
        ),
    },
    "Gaming.Casual_Esports": {
        "policy_velocity": 7, "regulatory_compliance": 8,
        "_note": "Not caught by Online Gaming Act §2(k) definition; lower GST exposure",
    },
    "Gaming.OTT": {
        "regulatory_compliance": 8, "liability": 7, "ip_infringement": 9,
        "_note": "IT Rules 2021 Rule 9; content certification; copyright clearance",
    },
    "Gaming.Creator_Economy": {
        "liability": 7, "ip_infringement": 8, "reputation": 9,
        "_note": "ASCI influencer guidelines; copyright on derivative works",
    },
    # ── LOGISTICS ─────────────────────────────────────────────────────────────
    "Logistics.Last_Mile_Delivery": {
        "gig_labour": 10, "regulatory_compliance": 10, "liability": 10,
        "_note": "MV Aggregator Guidelines 2025; Karnataka/Rajasthan/Bihar gig Acts",
        "_auto_include": ["motor_fleet", "group_pa", "employees_comp"],
    },
    "Logistics.B2B_Freight": {
        "property": 9, "liability": 9,
        "_note": "Carriage by Road Act 2007; transit liability",
    },
    "Logistics.EV_OEM": {
        "regulatory_compliance": 10, "esg_climate": 9, "property": 8,
        "_note": "BWM Rules 2022 EPR; PM E-DRIVE Sep-2024; AIS-156 battery safety",
    },
    # ── D2C ───────────────────────────────────────────────────────────────────
    "D2C.Hardware_Electronics": {
        "regulatory_compliance": 10, "liability": 9, "geopolitical": 10,
        "_note": "BIS QCO + LMPC + PWM EPR; Chinese component exposure (PN3)",
        "_auto_include": ["product_liability"],
    },
    "D2C.Food_Beverage": {
        "regulatory_compliance": 10, "liability": 10, "reputation": 10,
        "_note": "FSSAI LRS Regulations 2011; FSSAI Organic Standards; recall risk",
        "_auto_include": ["product_liability"],
    },
    "D2C.Apparel_Footwear": {
        "regulatory_compliance": 9, "esg_climate": 7,
        "_note": "BIS IS 17043/15844 QCO 1-Aug-2024; LMPC; EPR plastic",
    },
    # ── DEEPTECH ──────────────────────────────────────────────────────────────
    "Deeptech.AI_Software": {
        "regulatory_compliance": 9, "policy_velocity": 9, "ip_infringement": 10,
        "_note": "MeitY AI Advisory; EU AI Act Art 2(1)(c); SGI Rules 10-Feb-2026",
        "_auto_include": ["professional_indemnity"],
    },
    "Deeptech.Hardware_Robotics": {
        "property": 9, "ip_infringement": 9, "esg_climate": 7,
        "_note": "Import-dependency; dual-use export controls DGFT; SEMI standards",
    },
    # ── EDTECH ────────────────────────────────────────────────────────────────
    "Edtech.K12_Children": {
        "regulatory_compliance": 10, "data_privacy": 10, "reputation": 10,
        "_note": "DPDPA §9 ₹200cr verifiable-parental-consent penalty; NCPCR; POCSO §13",
        "_auto_include": ["cyber_liability"],
    },
    "Edtech.Test_Prep_Adult": {
        "regulatory_compliance": 9, "liability": 9, "governance_fraud": 9,
        "_note": "MoE Coaching Guidelines 16-Jan-2024; CCPA refund mandate; Byju's precedent",
    },
}


# =============================================================================
# PRODUCT CATALOG — 28 ICICI Lombard products (unchanged)
# =============================================================================
PRODUCT_CATALOG = {
    "cyber_liability": {
        "name": "Cyber Liability Insurance",
        "il_product": "Commercial Cyber Liability / I-Elite Group Cyber Liability Insurance",
        "what_it_covers": (
            "Pays for costs when your systems get hacked, customer data leaks, "
            "or a ransomware attack hits your servers. Covers forensic investigation, "
            "legal defence, customer notification, regulatory fines, and business "
            "interruption losses."
        ),
        "nudge": (
            "If a hacker steals your customer data tomorrow, you could face lawsuits, "
            "DPDP Act penalties, and months of downtime — this policy is what keeps "
            "your startup from shutting down."
        ),
        "best_for": "SaaS, fintech, healthtech, edtech, D2C with customer data.",
    },
    "dno_liability": {
        "name": "Directors & Officers (D&O) Liability",
        "il_product": "Directors and Officers Liability",
        "what_it_covers": (
            "Protects founders, directors, and senior managers personally if they "
            "get sued over business decisions — by investors, employees, regulators, "
            "or competitors. Covers legal defence and settlements."
        ),
        "nudge": (
            "The moment you take VC money, investors often require this. If a deal "
            "goes wrong or an employee sues the company, your personal savings and "
            "home are on the line without it."
        ),
        "best_for": "Any funded startup, especially post-Seed with institutional investors.",
    },
    "professional_indemnity": {
        "name": "Professional Indemnity / E&O Insurance",
        "il_product": "Professional Indemnity (Technology) Insurance",
        "what_it_covers": (
            "Covers claims from clients who say your software, service, or advice "
            "caused them financial loss — due to a bug, outage, wrong recommendation, "
            "or missed deadline. Pays legal costs and damages."
        ),
        "nudge": (
            "If your app has a bug that causes a client to lose money, they can sue "
            "you. Enterprise customers now demand this before signing contracts."
        ),
        "best_for": "SaaS, IT services, consultancies, fintech platforms, AI/ML products.",
    },
    "employee_health": {
        "name": "Group Health Insurance",
        "il_product": "Group Health Insurance / Group Health (Floater) Insurance",
        "what_it_covers": (
            "Medical cover for your employees and their families — hospitalization, "
            "day-care procedures, maternity, and more. Builds trust and helps you "
            "hire and retain talent."
        ),
        "nudge": (
            "Top engineers compare health benefits before joining. A ₹5 lakh family "
            "floater often costs less than one month's salary and dramatically "
            "improves retention."
        ),
        "best_for": "Every startup with 5+ employees.",
    },
    "group_pa": {
        "name": "Group Personal Accident",
        "il_product": "Group Personal Accident",
        "what_it_covers": (
            "One-time payout to the employee or family if there is an accidental "
            "injury, disability, or death — even outside working hours. Very "
            "affordable per head."
        ),
        "nudge": (
            "Field staff, delivery riders, sales teams travel constantly. For the "
            "price of a coffee per employee per month, you show them you care."
        ),
        "best_for": "Logistics, field-sales, agritech, manufacturing, any startup with travel.",
    },
    "employees_comp": {
        "name": "Workmen's Compensation / Employee's Compensation",
        "il_product": "Employer's Liability / Workmen's Compensation Insurance",
        "what_it_covers": (
            "Legally mandated under the Employees' Compensation Act for many "
            "categories of workers. Pays compensation if an employee is injured or "
            "dies while doing their job."
        ),
        "nudge": (
            "If a warehouse worker or delivery partner is injured on duty, the law "
            "holds you liable. This converts an unpredictable lawsuit into a fixed, "
            "small premium."
        ),
        "best_for": "Logistics, cleantech, D2C with warehouses, agritech, any physical ops.",
    },
    "property_fire": {
        "name": "Fire & Allied Perils / Property Insurance",
        "il_product": "ICICI Lombard Fire & Allied Perils Insurance Policy / MSME Suraksha Kavach",
        "what_it_covers": (
            "Covers your office, warehouse, equipment, and inventory against fire, "
            "lightning, floods, earthquakes, and burglary. Includes rebuilding costs "
            "and lost business income while you recover."
        ),
        "nudge": (
            "One warehouse fire can wipe out six months of inventory. If you stock "
            "physical goods or run a lab, this is non-negotiable."
        ),
        "best_for": "D2C brands, cleantech, manufacturing, deeptech labs, agritech.",
    },
    "business_edge": {
        "name": "Business Edge (Comprehensive Business Package)",
        "il_product": "Business Edge Policy / Business Prime Policy",
        "what_it_covers": (
            "A single package combining fire, burglary, money-in-transit, machinery "
            "breakdown, and public liability — designed for small and medium "
            "businesses. Simpler to manage than buying each separately."
        ),
        "nudge": (
            "One policy, one premium, one renewal date. Perfect for a growing "
            "startup that wants real cover without juggling five insurance documents."
        ),
        "best_for": "Growth-stage startups with physical offices or light manufacturing.",
    },
    "public_liability": {
        "name": "Public Liability Insurance",
        "il_product": "Commercial General Liability / Public Liability (Industrial or Non-Industrial)",
        "what_it_covers": (
            "Pays if a third party — customer, visitor, supplier — is injured on "
            "your premises, or if your product or operation damages someone's "
            "property. Covers legal costs and court-awarded damages."
        ),
        "nudge": (
            "If a delivery customer slips in your warehouse or your product causes "
            "property damage, lawsuits can run into crores. This is the shield."
        ),
        "best_for": "D2C, logistics, cleantech, events, hospitality-tech, physical retail.",
    },
    "product_liability": {
        "name": "Product Liability Insurance",
        "il_product": "Product Liability (Commercial or Retail)",
        "what_it_covers": (
            "Covers you if your manufactured product causes injury, illness, or "
            "damage after a customer buys it. Includes product recall, legal defence, "
            "and settlement costs."
        ),
        "nudge": (
            "If a batch of your D2C wellness gummies makes customers sick, the "
            "recall and lawsuits can finish the company. This is your survival kit."
        ),
        "best_for": "D2C brands, healthtech devices, food-tech, cleantech hardware.",
    },
    "marine_transit": {
        "name": "Marine Transit / Inland Transit Insurance",
        "il_product": "Marine Inland Transit Insurance / Marine Export-Import",
        "what_it_covers": (
            "Covers goods while they move — by road, rail, sea, or air. Protects "
            "against theft, accidents, and damage in transit, whether it's raw "
            "material coming in or products going out."
        ),
        "nudge": (
            "Every truckload is exposed. One accident can mean lakhs in lost "
            "inventory — this is standard for anyone who ships physical goods."
        ),
        "best_for": "D2C, logistics, agritech, cleantech, manufacturing startups.",
    },
    "key_person": {
        "name": "Key Person Insurance",
        "il_product": "Mapped via Group Personal Accident + term-life partnerships",
        "what_it_covers": (
            "Financial cushion for the company if a founder or critical team member "
            "dies or is permanently disabled. Helps the business survive the "
            "transition, pay off debt, or find a replacement."
        ),
        "nudge": (
            "Investors increasingly ask for this. If your sole technical founder is "
            "hit by a bus, this cash keeps the lights on while you rebuild."
        ),
        "best_for": "Founder-dependent startups, deeptech, single-CTO companies.",
    },
    "employment_practices": {
        "name": "Employment Practices Liability (EPL)",
        "il_product": "Employment Practices Liability (Commercial or Retail)",
        "what_it_covers": (
            "Covers lawsuits from employees alleging wrongful termination, "
            "harassment, discrimination, or unfair pay. Pays legal defence and "
            "settlements."
        ),
        "nudge": (
            "With POSH Act and labour codes, HR complaints are rising fast. One "
            "tribunal case can drain ₹20–50 lakhs in fees alone."
        ),
        "best_for": "Any startup with 10+ employees, especially post-Series A.",
    },
    "crime_fidelity": {
        "name": "Crime / Fidelity Insurance",
        "il_product": "Fidelity Insurance / Employee Dishonesty Liability",
        "what_it_covers": (
            "Covers financial loss if an employee commits fraud, theft, or "
            "embezzlement. Also covers external crime like vendor impersonation "
            "scams and fraudulent fund transfers."
        ),
        "nudge": (
            "UPI frauds and insider theft are the fastest-growing startup losses. "
            "One rogue finance hire can empty your runway."
        ),
        "best_for": "Fintech, D2C, any startup handling cash or payments.",
    },
    "gadget_equipment": {
        "name": "Gadget & Electronic Equipment Insurance",
        "il_product": "Gadget Insurance / Electronic Equipment Insurance",
        "what_it_covers": (
            "Covers laptops, phones, servers, specialized electronics against "
            "accidental damage, theft, and breakdown. Useful for distributed or "
            "remote teams."
        ),
        "nudge": (
            "A remote team of 30 means 30 laptops in 30 homes. Replacing even 10% "
            "per year adds up — this converts it into a small predictable premium."
        ),
        "best_for": "Remote-first SaaS, deeptech with specialised equipment.",
    },
    "clinical_trials": {
        "name": "Clinical Trials Liability",
        "il_product": "Clinical Trials Liability (Commercial or Retail)",
        "what_it_covers": (
            "Mandatory for human clinical trials in India. Covers liability if "
            "trial participants are injured or suffer adverse effects."
        ),
        "nudge": (
            "You cannot legally run a trial without it. CDSCO will not approve your "
            "protocol if this is missing."
        ),
        "best_for": "Healthtech, biotech, pharma, medical device startups.",
    },
    "comprehensive_general_liability": {
        "name": "Comprehensive General Liability (CGL)",
        "il_product": "Commercial General Liability Insurance",
        "what_it_covers": (
            "Broad umbrella cover for bodily injury, property damage, and personal "
            "injury claims made against your business by third parties — customers, "
            "vendors, or the public. Wider scope than standard public liability."
        ),
        "nudge": (
            "Enterprise B2B clients and international contracts increasingly require "
            "CGL as a vendor prerequisite. Without it, you can lose deals before they start."
        ),
        "best_for": "B2B SaaS, IT services, consulting, any startup with enterprise clients.",
    },
    "business_interruption": {
        "name": "Business Interruption Insurance",
        "il_product": "Consequential Loss (Fire) / Business Interruption Policy",
        "what_it_covers": (
            "Replaces lost revenue and pays fixed costs (rent, salaries) if your "
            "business is forced to shut down or slow down due to a covered event — "
            "fire, flood, or a major cyber incident. Bridges the gap while you rebuild."
        ),
        "nudge": (
            "Post-Series A, your monthly burn is high enough that even 30 days of "
            "downtime can permanently damage the business. This is your revenue safety net."
        ),
        "best_for": "Series A+ startups, physical ops, cloud infra-dependent SaaS.",
    },
    "property_all_risk": {
        "name": "Property All Risk Insurance",
        "il_product": "Industrial All Risk Insurance / Property All Risk",
        "what_it_covers": (
            "Broadest property cover available — protects all physical assets against "
            "any accidental loss or damage not explicitly excluded. Goes beyond standard "
            "fire policies to cover accidental damage, equipment failure, and more."
        ),
        "nudge": (
            "If you have a lab, server room, or manufacturing line, standard fire "
            "insurance leaves big gaps. All-risk is the upgrade that actually covers "
            "real-world accidents."
        ),
        "best_for": "Deeptech, cleantech hardware, medical device startups, labs.",
    },
    "electronic_equipment": {
        "name": "Electronic Equipment Insurance",
        "il_product": "Electronic Equipment Insurance (EEI)",
        "what_it_covers": (
            "Covers sudden and accidental damage to computers, servers, telecom "
            "equipment, medical devices, and other electronic machinery — including "
            "electrical burnout, short circuit, and accidental operator error."
        ),
        "nudge": (
            "A server rack failure or GPU cluster burnout can cost Rs 50L+ and set "
            "your product back by months. Standard property policies exclude electrical "
            "damage — this one doesn't."
        ),
        "best_for": "Deeptech / AI, healthtech with medical devices, cloud hardware operators.",
    },
    "machinery_breakdown": {
        "name": "Machinery Breakdown Insurance",
        "il_product": "Machinery Breakdown Insurance / Boiler & Pressure Plant Insurance",
        "what_it_covers": (
            "Covers sudden mechanical or electrical breakdown of machinery and plant "
            "equipment. Pays for repair or replacement costs and consequential "
            "business loss from the breakdown."
        ),
        "nudge": (
            "If a critical machine breaks in your production line, downtime costs "
            "compound daily. This converts an unpredictable capital hit into a "
            "small, predictable premium."
        ),
        "best_for": "Cleantech / manufacturing, agritech with processing equipment, foodtech.",
    },
    "motor_fleet": {
        "name": "Motor Fleet / Goods Vehicle Insurance",
        "il_product": "Goods Carrying Vehicle Insurance / Passenger Carrying Vehicle Insurance",
        "what_it_covers": (
            "Covers your entire vehicle fleet — own damage, third-party liability, "
            "and personal accident cover for drivers. Single fleet policy is cheaper "
            "and simpler than insuring each vehicle separately."
        ),
        "nudge": (
            "Every uninsured delivery vehicle is a liability bomb. One accident "
            "without commercial vehicle cover exposes you personally to third-party "
            "claims that can run into crores."
        ),
        "best_for": "Logistics / mobility startups, agritech with farm vehicles, D2C with own fleet.",
    },
    "trade_credit": {
        "name": "Trade Credit Insurance",
        "il_product": "Trade Credit Insurance / Credit Insurance",
        "what_it_covers": (
            "Protects your accounts receivable if a B2B customer fails to pay due "
            "to insolvency, default, or political risk. Lets you extend credit "
            "confidently and protect cash flow."
        ),
        "nudge": (
            "If your top 3 customers account for 60%+ of revenue, one default "
            "can wipe out your runway. Essential for any B2B startup "
            "with payment terms of 30-90 days."
        ),
        "best_for": "B2B SaaS, logistics, D2C with wholesale channels, fintech lending platforms.",
    },
    "money_insurance": {
        "name": "Money Insurance",
        "il_product": "Money Insurance Policy",
        "what_it_covers": (
            "Covers physical cash, cheques, and negotiable instruments against "
            "loss by theft, robbery, or accident — whether in transit, in a safe, "
            "or at the premises."
        ),
        "nudge": (
            "Retail ops, cash-handling kitchens, and event businesses handle "
            "significant daily cash. One robbery without this policy means "
            "the loss comes straight out of your working capital."
        ),
        "best_for": "Foodtech / cloud kitchen, D2C retail, events, logistics cash-on-delivery ops.",
    },
    "contractors_all_risk": {
        "name": "Contractors All Risk (CAR) / Erection All Risk (EAR)",
        "il_product": "Contractors All Risk Insurance / Erection All Risk Insurance",
        "what_it_covers": (
            "Covers construction and installation projects against accidental damage, "
            "fire, flood, and third-party liability during the project period. "
            "EAR specifically covers machinery and equipment being erected or installed."
        ),
        "nudge": (
            "If you're building infrastructure, installing solar panels, or "
            "erecting hardware at a client site, your standard policies provide "
            "zero cover. CAR/EAR is the mandatory gap-filler."
        ),
        "best_for": "Cleantech, deeptech hardware, agritech with infrastructure, construction-adjacent startups.",
    },
    "drone_insurance": {
        "name": "Remotely Piloted Aircraft (Drone) Insurance",
        "il_product": "Remotely Piloted Aircraft Insurance",
        "what_it_covers": (
            "Covers drones against accidental damage, third-party liability for "
            "bodily injury or property damage, and hull loss. Required under DGCA "
            "regulations for commercial drone operations in India."
        ),
        "nudge": (
            "DGCA mandates insurance for all commercial drone operations. Flying "
            "without it is illegal, and one crash in a populated area without "
            "liability cover is a company-ending event."
        ),
        "best_for": "Agritech with drone ops, logistics / drone delivery, survey and mapping startups.",
    },
    "msme_suraksha": {
        "name": "MSME Suraksha Kavach (Complete Package)",
        "il_product": "MSME Suraksha Kavach / Complete Fire & Package Policy",
        "what_it_covers": (
            "All-in-one package for small businesses — combines fire, burglary, "
            "money, personal accident, public liability, and business interruption "
            "in a single affordable policy. IRDAI-designed for MSMEs."
        ),
        "nudge": (
            "If you're pre-Series A with physical ops, this single policy gives "
            "you 6 covers at the price of 2. It's the most capital-efficient "
            "insurance purchase a small startup can make."
        ),
        "best_for": "Pre-seed to Seed startups with physical operations, retail, food, light manufacturing.",
    },
    "enterprise_secure": {
        "name": "Enterprise Secure Package Policy",
        "il_product": "Enterprise Secure Package Policy / Business Shield",
        "what_it_covers": (
            "Comprehensive business package for mid-to-large enterprises — combines "
            "property all risk, machinery breakdown, business interruption, "
            "public liability, and fidelity in a single policy."
        ),
        "nudge": (
            "Post-Series A, managing 6 separate policies means 6 renewal dates, "
            "6 claims processes, and 6 chances for a coverage gap. One enterprise "
            "package eliminates all of that."
        ),
        "best_for": "Series A+ startups with physical assets, manufacturing, complex multi-site ops.",
    },
}


# =============================================================================
# PRODUCT RISK MAP — 28 entries, updated to 13-category score keys
# =============================================================================
PRODUCT_RISK_MAP = {
    "cyber_liability": {
        "Cyber Technical Risk": 1.0, "Data Privacy Risk": 0.7,
        "Regulatory Compliance Risk": 0.3,
    },
    "dno_liability": {
        "Liability Risk": 0.7, "Governance & Fraud Risk": 0.6,
        "Regulatory Compliance Risk": 0.5,
    },
    "professional_indemnity": {
        "Liability Risk": 1.0, "Cyber Technical Risk": 0.2,
        "IP Infringement Risk": 0.3,
    },
    "employee_health": {
        "Key Person Risk": 0.5, "Liability Risk": 0.2, "Gig & Labour Risk": 0.3,
    },
    "group_pa": {
        "Key Person Risk": 0.6, "Liability Risk": 0.2, "Gig & Labour Risk": 0.4,
    },
    "employees_comp": {
        "Liability Risk": 0.6, "Regulatory Compliance Risk": 0.6,
        "Property Risk": 0.2, "Gig & Labour Risk": 0.5,
    },
    "property_fire": {
        "Property Risk": 1.0, "ESG & Climate Risk": 0.3,
    },
    "business_edge": {
        "Property Risk": 0.7, "Liability Risk": 0.4,
    },
    "public_liability": {
        "Liability Risk": 0.8, "Property Risk": 0.3,
    },
    "product_liability": {
        "Liability Risk": 0.9, "Regulatory Compliance Risk": 0.3,
        "IP Infringement Risk": 0.2,
    },
    "marine_transit": {
        "Property Risk": 0.8, "Geopolitical Risk": 0.3,
    },
    "key_person": {
        "Key Person Risk": 1.0, "Governance & Fraud Risk": 0.3,
    },
    "employment_practices": {
        "Liability Risk": 0.6, "Regulatory Compliance Risk": 0.6,
        "Gig & Labour Risk": 0.5,
    },
    "crime_fidelity": {
        "Cyber Technical Risk": 0.3, "Liability Risk": 0.4,
        "Governance & Fraud Risk": 0.6, "Regulatory Compliance Risk": 0.3,
    },
    "gadget_equipment": {
        "Property Risk": 0.5, "Cyber Technical Risk": 0.2,
    },
    "clinical_trials": {
        "Regulatory Compliance Risk": 0.8, "Liability Risk": 0.6,
    },
    "comprehensive_general_liability": {
        "Liability Risk": 0.9, "Regulatory Compliance Risk": 0.3,
    },
    "business_interruption": {
        "Property Risk": 0.5, "Cyber Technical Risk": 0.3,
        "Liability Risk": 0.2, "Policy Velocity Risk": 0.3,
    },
    "property_all_risk": {
        "Property Risk": 1.0, "Liability Risk": 0.2, "ESG & Climate Risk": 0.3,
    },
    "electronic_equipment": {
        "Property Risk": 0.7, "Cyber Technical Risk": 0.2,
    },
    "machinery_breakdown": {
        "Property Risk": 0.8, "Regulatory Compliance Risk": 0.1,
    },
    "motor_fleet": {
        "Liability Risk": 0.8, "Property Risk": 0.6, "Gig & Labour Risk": 0.4,
    },
    "trade_credit": {
        "Regulatory Compliance Risk": 0.4, "Liability Risk": 0.5,
        "Geopolitical Risk": 0.3,
    },
    "money_insurance": {
        "Property Risk": 0.4, "Liability Risk": 0.3,
    },
    "contractors_all_risk": {
        "Property Risk": 0.9, "Liability Risk": 0.5,
    },
    "drone_insurance": {
        "Liability Risk": 0.7, "Property Risk": 0.5,
        "Regulatory Compliance Risk": 0.4,
    },
    "msme_suraksha": {
        "Property Risk": 0.6, "Liability Risk": 0.4,
    },
    "enterprise_secure": {
        "Property Risk": 0.8, "Liability Risk": 0.4,
        "Regulatory Compliance Risk": 0.2, "ESG & Climate Risk": 0.2,
    },
}


# =============================================================================
# SECTOR OVERRIDES & EXCLUSIONS
# =============================================================================
SECTOR_OVERRIDES = {
    "Healthtech":               ["clinical_trials", "electronic_equipment"],
    "Logistics / Mobility":     ["marine_transit", "public_liability", "motor_fleet"],
    "D2C / Consumer Brands":    ["product_liability", "marine_transit", "msme_suraksha"],
    "Foodtech / Cloud Kitchen": ["product_liability", "public_liability", "money_insurance"],
    "Fintech":                  ["crime_fidelity", "dno_liability", "trade_credit"],
    "Cleantech / Climatetech":  ["property_fire", "public_liability", "contractors_all_risk"],
    "Agritech":                 ["marine_transit", "drone_insurance", "motor_fleet"],
    "Deeptech / AI / Robotics": ["electronic_equipment", "property_all_risk", "key_person"],
    "SaaS / Enterprise Software": [
        "cyber_liability", "professional_indemnity", "comprehensive_general_liability",
    ],
    "Edtech":                   ["cyber_liability", "employee_health"],
    "HRtech":                   ["cyber_liability", "employment_practices"],
    "Legaltech":                ["professional_indemnity", "dno_liability"],
    "Gaming / Media / Content": ["cyber_liability", "professional_indemnity"],
}

SECTOR_EXCLUSIONS = {
    "SaaS / Enterprise Software": [
        "clinical_trials", "product_liability", "marine_transit",
        "motor_fleet", "drone_insurance", "contractors_all_risk",
        "machinery_breakdown", "msme_suraksha", "money_insurance",
    ],
    "Fintech": [
        "clinical_trials", "product_liability", "marine_transit",
        "motor_fleet", "drone_insurance", "contractors_all_risk",
        "machinery_breakdown", "msme_suraksha", "money_insurance",
    ],
    "Edtech": [
        "clinical_trials", "product_liability", "marine_transit",
        "motor_fleet", "drone_insurance", "contractors_all_risk",
        "machinery_breakdown", "money_insurance",
    ],
    "HRtech": [
        "clinical_trials", "product_liability", "marine_transit",
        "motor_fleet", "drone_insurance", "contractors_all_risk",
        "machinery_breakdown", "msme_suraksha", "money_insurance",
    ],
    "Legaltech": [
        "clinical_trials", "product_liability", "marine_transit",
        "motor_fleet", "drone_insurance", "contractors_all_risk",
        "machinery_breakdown", "msme_suraksha", "money_insurance",
    ],
    "Gaming / Media / Content": [
        "clinical_trials", "marine_transit", "motor_fleet",
        "drone_insurance", "contractors_all_risk",
        "machinery_breakdown", "msme_suraksha", "money_insurance",
    ],
    "D2C / Consumer Brands": [
        "clinical_trials", "drone_insurance", "contractors_all_risk",
        "electronic_equipment", "motor_fleet",
    ],
    "Healthtech": [
        "motor_fleet", "drone_insurance", "msme_suraksha",
        "contractors_all_risk", "money_insurance",
    ],
    "Deeptech / AI / Robotics": [
        "clinical_trials", "marine_transit", "motor_fleet",
        "drone_insurance", "msme_suraksha", "money_insurance",
    ],
    "Agritech":                 ["clinical_trials", "enterprise_secure"],
    "Cleantech / Climatetech":  [
        "clinical_trials", "drone_insurance", "money_insurance",
        "trade_credit", "msme_suraksha",
    ],
    "Logistics / Mobility": [
        "clinical_trials", "product_liability",
        "electronic_equipment", "machinery_breakdown", "enterprise_secure",
    ],
    "Foodtech / Cloud Kitchen": [
        "clinical_trials", "marine_transit", "motor_fleet",
        "drone_insurance", "contractors_all_risk",
        "electronic_equipment", "enterprise_secure",
    ],
    # Hard-decline sub-sector: all products excluded
    "Gaming.Real_Money": [
        "cyber_liability", "dno_liability", "professional_indemnity", "employee_health",
        "group_pa", "employees_comp", "property_fire", "business_edge",
        "public_liability", "product_liability", "marine_transit", "key_person",
        "employment_practices", "crime_fidelity", "gadget_equipment",
        "comprehensive_general_liability", "business_interruption", "property_all_risk",
        "electronic_equipment", "trade_credit", "money_insurance", "enterprise_secure",
    ],
}


# =============================================================================
# RISK CATEGORY STATISTICS — current scenario + forecast backing each weight
# Sources: CERT-In 2025, RBI 2024-25, NITI Aayog 2024, FSSAI 2024,
#          Delhi HC judgments 2024, DGGI FY24, Economic Survey 2024.
# =============================================================================
RISK_CATEGORY_STATS = {
    "Cyber Technical Risk": {
        "headline": (
            "CERT-In recorded 29.44 lakh (2.94 million) cyber incidents in 2025. "
            "India suffered 265 million cyber attacks in 2025 — financial services and "
            "healthcare are the hardest-hit sectors. Star Health breach (Sep 2024) "
            "exposed 31 million Indians' medical records on Telegram."
        ),
        "source": "CERT-In Annual Report 2025; PIB; BFSI Digital Threat Report 2024",
        "forecast": (
            "Ransomware and malware are the fastest-growing threat vectors. "
            "42% of Indian companies identify them as their top concern. "
            "SaaS and cloud assets are primary targets through 2026."
        ),
        "sector_notes": {
            "Fintech": "BFSI is the #1 targeted sector in India; card/internet fraud quadrupled in FY24 (29,082 cases, +334% YoY).",
            "Healthtech": "Star Health (Sep 2024): 31M health records leaked; Dec 2024: 1.59M insurance records breached.",
            "SaaS / Enterprise Software": "boAt (7.5M records), Hathway (41.5M records), BSNL SIM details — all in 2024.",
            "HRtech": "HRtech platforms hold payroll, biometric, and health data — all DPDPA Sensitive Personal Data; 72-hr breach notification mandatory.",
        },
    },
    "Data Privacy Risk": {
        "headline": (
            "DPDPA 2023 imposes penalties up to ₹250 crore per breach. "
            "Average cost of a data breach in India reached ₹19.5 crore in 2024 "
            "(9% YoY increase). India ranks 5th globally for volume of data breaches."
        ),
        "source": "DPDPA 2023; IBM Cost of a Data Breach India 2024; Surfshark 2024",
        "forecast": (
            "DPDP Rules (notified Nov 2025) enter full enforcement by May 2027. "
            "Significant Data Fiduciary designation (§10) will trigger algorithmic audits "
            "and mandatory data localisation for affected platforms."
        ),
        "sector_notes": {
            "Fintech": "Fintech classified as likely SDF; ₹200cr penalty for failing 72-hr breach notification.",
            "Healthtech": "31M health records exposed in 2024; draft rules (Jan 2025) revealed no special health-data protections.",
            "HRtech": "Payroll + biometric + health data = triple DPDPA Sensitive Personal Data exposure.",
            "Edtech": "DPDPA §9: ₹200cr penalty for processing minor data without verifiable parental consent.",
        },
    },
    "Liability Risk": {
        "headline": (
            "National highways (2% of India's road network) account for 30% of all "
            "road accidents and 36% of deaths. India has 5.2 million medical negligence "
            "cases filed annually — a 110% jump in recent years. Consumer Protection "
            "Act 2019 imposes strict product liability on manufacturers and platforms."
        ),
        "source": "TRIP Centre IIT Delhi Road Safety Report 2024; Medical Journal Dr. D.Y. Patil Vidyapeeth 2024; ICLG 2025",
        "forecast": (
            "MV Act enforcement via electronic surveillance devices increasing. "
            "Telemedicine market growing at 21.2% CAGR through 2030 — creating new "
            "medical liability vectors. D2C strict liability doctrine expanding."
        ),
        "sector_notes": {
            "Logistics / Mobility": "28.4M vehicles produced FY24; highways = 36% of all road deaths; MV Act §149 unlimited third-party liability.",
            "Healthtech": "5.2M negligence cases/year; surgical procedures = 80% of negligence-related deaths.",
            "Edtech": "CCPA penalty ₹3L for misleading ads (2024); Hooghly court ordered Byju's to refund ₹65K + ₹5K compensation.",
            "D2C / Consumer Brands": "NCDRC Honda judgment (2024) — strict liability for product defects; burden of proof on manufacturer.",
        },
    },
    "IP Infringement Risk": {
        "headline": (
            "ANI v. OpenAI (Delhi HC, 2024): court admitted copyright infringement suit "
            "against AI training on news content — India's first landmark AI copyright case. "
            "Jackie Shroff v. Peppy Store (2024): court restrained AI chatbot from using "
            "personality rights without consent. DPIIT clarified AI developers must seek "
            "authorisation for copyrighted training data."
        ),
        "source": "Delhi High Court 2024; Khurrana & Khurana IP Analysis 2024; DPIIT mid-2024",
        "forecast": (
            "AI copyright litigation is escalating. Fair use exemption for commercial "
            "AI training is unlikely in India. Esports IP disputes expected to rise "
            "as the Online Gaming Act 2025 formalises the sector."
        ),
        "sector_notes": {
            "Deeptech / AI / Robotics": "ANI v. OpenAI is the precedent-setting case; personality rights protection expanding to AI-generated content.",
            "Gaming / Media / Content": "Online Gaming Act 2025 creates formal IP frameworks for esports content; copyright enforcement rising.",
            "Healthtech": "Pharma and medical device patents litigated under Patents Act 1970; AI diagnostics creating new patent disputes.",
        },
    },
    "Key Person Risk": {
        "headline": (
            "RBI Fit & Proper criteria require regulator approval for all fintech "
            "MD/CEO appointments. Paytm Payments Bank leadership was restructured "
            "following RBI enforcement action (Jan 2024). Deep tech sector has extreme "
            "founder/scientist concentration with no succession frameworks."
        ),
        "source": "RBI Fit & Proper Framework 2024; Paytm enforcement action Jan 2024",
        "forecast": (
            "RBI Fit & Proper scrutiny is increasing across all regulated fintech entities. "
            "Deep tech talent concentration will remain high-risk as the sector scales "
            "and global talent competition intensifies."
        ),
        "sector_notes": {
            "Fintech": "RBI can suspend/replace CEO of regulated entity; Paytm precedent shows regulatory key-person risk is real.",
            "Deeptech / AI / Robotics": "Deep tech companies are typically built around 1-2 founding scientists; no substitutes in the market.",
        },
    },
    "Governance & Fraud Risk": {
        "headline": (
            "Fraud losses in India grew 8x in H1 FY24-25 to ₹21,367 crore (~$2.56B). "
            "Digital payment fraud surged 5x to ₹14.57B. Byju's — once valued at $22B — "
            "collapsed due to governance lapses; MCA probe found opaque acquisitions and "
            "weak board controls. BharatPe EOW FIR: ₹81.3 crore fake-vendor fraud."
        ),
        "source": "RBI / BioCatch Fraud Trends 2025; Business Today 2024; EOW Mumbai 2023",
        "forecast": (
            "Fraud losses projected to keep rising. RBI's MuleHunter.ai deployed in "
            "23 banks (Dec 2025) to detect mule accounts. Governance compliance "
            "will tighten for high-growth startups post-Byju's."
        ),
        "sector_notes": {
            "Fintech": "Card/internet fraud = 66.8% of all cases; social engineering = 33%; digital arrest scams alone = ₹2,000 crore (2024).",
            "Edtech": "Byju's: Prosus wrote off $500M stake; 3 major investors left board over governance disputes in 2024.",
            "Gaming / Media / Content": "DGGI detected ₹81,875 crore GST evasion in online gaming FY24; 118 domestic operators issued show-cause notices.",
        },
    },
    "Property Risk": {
        "headline": (
            "Fire insurance gross direct premiums reached ₹256B in FY24. "
            "Between 2015–2021, India lost 35M hectares to drought and 33.9M "
            "hectares to excess rainfall. 3.2M hectares affected by extreme weather "
            "events in 2024 alone; 10,000+ livestock killed."
        ),
        "source": "Statista Fire Insurance FY24; Economic Survey 2024; RBI Bulletin Aug 2024",
        "forecast": (
            "Climate-driven property losses are escalating. Warehouse fire/flood risk "
            "is concentrated in Gujarat, Maharashtra, Tamil Nadu, and Delhi — "
            "India's fastest-growing logistics and D2C corridors."
        ),
        "sector_notes": {
            "D2C / Consumer Brands": "Logistics costs = 10–18% of revenue; warehouse fires/floods in industrial clusters growing with D2C CAGR of 8%.",
            "Agritech": "65% of Indian farmland is rainfed; crop/equipment loss is endemic and escalating.",
            "Logistics / Mobility": "Fleet damage exposed to MV Act strict penalties; cargo loss liability rising with e-commerce scaling.",
        },
    },
    "Regulatory Compliance Risk": {
        "headline": (
            "RBI issued 8+ major circulars in 2024 and restricted Paytm Payments Bank. "
            "DGGI detected ₹81,875 crore GST evasion in online gaming FY24. "
            "FSSAI conducted 18,000+ enforcement actions in 2024 (20% rise YoY). "
            "Paytm Payments Bank halted customer onboarding for KYC violations (Jan 2024)."
        ),
        "source": "RBI Circular Index 2024; DGGI Annual Report FY24; FSSAI Enforcement Data 2024",
        "forecast": (
            "RBI policy cycle is accelerating — expect major circular updates quarterly. "
            "Online Gaming Act 2025 enforcement begins May 2026. "
            "FSSAI deploying AI-based FoSCoS inspections with expanded scope."
        ),
        "sector_notes": {
            "Fintech": "8+ major RBI circulars in 2024; SRO framework introduced May 2024 for ongoing compliance monitoring.",
            "Gaming / Media / Content": "118 operators issued show-cause notices; 658 offshore entities under investigation for GST non-compliance.",
            "Foodtech / Cloud Kitchen": "18,000+ FSSAI enforcement actions; penalties ₹25K–₹10L per violation; traceability mandate expanding.",
            "Healthtech": "CDSCO National Single Window System (Jan 2024); risk-based device surveillance (Sep 2024); SaMD Class B/C/D mandatory.",
        },
    },
    "ESG & Climate Risk": {
        "headline": (
            "India is the 20th most climate-vulnerable nation (ND-GAIN Index). "
            "CBAM (EU Carbon Border Adjustment Mechanism) enters definitive phase Jan 2026 "
            "— India is among the largest payers alongside China and Russia. "
            "ALMM mandate for solar modules revived Apr 2024; SEBI BRSR value-chain "
            "push-through (Mar 2025) extends ESG obligations to supplier startups."
        ),
        "source": "ND-GAIN Index 2024; India-Briefing CBAM 2025; MNRE ALMM 2024; SEBI BRSR Circular Mar 2025",
        "forecast": (
            "EPR obligations expanding through FY2027-28. CBAM compliance costs rising "
            "for carbon-intensive manufacturers. Agri food inflation expected to remain "
            "endemic; RBI flagged erratic monsoon as a structural inflation driver."
        ),
        "sector_notes": {
            "Cleantech / Climatetech": "ALMM List-II for solar cells from Jun 2026; EPR phased through FY2028; CCTS carbon market live.",
            "Agritech": "35M hectares lost to drought (2015-21); 33.9M to excess rain; food inflation doubled from 2.9% to 6.3% in 2020s.",
            "Logistics / Mobility": "EV Battery EPR (BWM Rules 2022); PM E-DRIVE Sep-2024; emissions compliance costs rising for fleet operators.",
        },
    },
    "Geopolitical Risk": {
        "headline": (
            "DPIIT Press Note 3 (Apr 2020) requires government-route approval for FDI "
            "from 7 land-border countries including China. Mar 2026 amendments raised "
            "beneficial ownership threshold to 10% for automatic-route approval. "
            "D2C sector raised only $757M in 2024 — 54% below its 2022 peak — partly "
            "due to Chinese supply-chain and investor restrictions."
        ),
        "source": "PMO Press Release Mar 2026; India-Briefing PN3 2026; Tracxn D2C Report Apr 2025",
        "forecast": (
            "PN3 restrictions continuing to tighten selectively. CBAM compliance "
            "costs rising for exporters to EU. Cross-border payment corridors expanding "
            "but subject to RBI localisation requirements and sudden policy reversals."
        ),
        "sector_notes": {
            "Deeptech / AI / Robotics": "Dual-use export controls + PN3 = dual geopolitical exposure; capital goods/electronics manufacturing incentivised but scrutinised.",
            "D2C / Consumer Brands": "Indian D2C funding down 54% from 2022 peak; Chinese supplier dependency creates CBAM and supply disruption risk.",
            "Fintech": "RBI data localisation + PN3 investor restrictions + cross-border settlement rules create layered geopolitical exposure.",
        },
    },
    "Gig & Labour Risk": {
        "headline": (
            "India has 7.7 million gig workers (2024), projected to reach 23.5 million "
            "by 2029-30 (NITI Aayog). 24% of delivery drivers reported road accidents "
            "as their primary safety concern. Zomato delivery worker death (Aug 2024) "
            "with no company compensation — triggering worker unionisation demands. "
            "Social Security Code §113-114 aggregator levy now in force."
        ),
        "source": "NITI Aayog 2024; IDinsight Delivery Platform Research 2024; SS Code 2020",
        "forecast": (
            "Gig worker population expected to 3x by 2030. Karnataka, Rajasthan, Bihar, "
            "Jharkhand, and Telangana have the most aggressive state gig Acts. "
            "MV Aggregator Guidelines 2025 mandate ₹5L health + ₹10L term cover per driver."
        ),
        "sector_notes": {
            "Logistics / Mobility": "5M+ delivery workers; 24% accident rate; Karnataka/Rajasthan gig Acts impose levy + mandatory benefits.",
            "Foodtech / Cloud Kitchen": "Zomato/Swiggy rider deaths documented 2024; gig workforce = majority of headcount; accident liability unresolved.",
            "HRtech": "HRtech platforms managing gig payrolls face aggregator levy exposure under SS Code §113-114.",
        },
    },
    "Policy Velocity Risk": {
        "headline": (
            "Online Gaming Act 2025 (assented 22-Aug-2025) disrupted an entire sector "
            "within months of enactment — the clearest Indian precedent for policy velocity. "
            "RBI issued 8+ major circulars in 2024. MeitY issued and revised its AI Advisory "
            "twice within 15 days (Mar 2024). Competition Act DVT (₹2,000cr threshold) "
            "went live Sep 2024 with no phase-in period."
        ),
        "source": "MeitY Online Gaming Act 2025; RBI Circular Index 2024; Competition (Amendment) Act 2023",
        "forecast": (
            "India is adopting sector-based AI regulation — no standalone AI law, "
            "but sectoral rules accelerating (SGI Rules Feb 2026, MeitY AI Advisory). "
            "Digital Competition Bill ex-ante obligations expected for SSDs. "
            "Income-Tax Act 2025 effective Apr 2026."
        ),
        "sector_notes": {
            "Gaming / Media / Content": "Online Gaming Act enforcement from May 2026; OGAI oversight body being established; 28-40% GST applicable.",
            "Fintech": "8+ RBI circulars (2024); SRO framework (May 2024); CIMS reporting (Jun 2025) — highest circular frequency of any sector.",
            "Deeptech / AI / Robotics": "MeitY AI Advisory revised twice in 15 days; EU AI Act Art 2(1)(c) extraterritorial reach on Indian AI products sold to EU.",
        },
    },
    "Reputation Risk": {
        "headline": (
            "FSSAI trended on social media (Jan 2026) after food adulteration outrage. "
            "MDH/Everest spices banned in Hong Kong and Singapore (2024) for carcinogenic "
            "substances. Zepto customer found a human finger in ice cream (2024). "
            "Byju's governance collapse destroyed investor confidence in all edtech — "
            "60% of parents now seek refunds from edtech platforms."
        ),
        "source": "MEDIANAMA 2024-26; Consumer court data 2024; IBTimes India 2024",
        "forecast": (
            "Viral social media campaigns are structurally increasing reputation risk for "
            "foodtech, edtech, and gaming. Consumer trust in FSSAI at historic low (Apr 2024 "
            "survey). Edtech reputation expected to remain low through 2025-26."
        ),
        "sector_notes": {
            "Foodtech / Cloud Kitchen": "Multiple viral food safety incidents in 2024 (Zepto, Blinkit, Zomato Hyperpure); April 2024 survey: majority have low/no confidence in FSSAI.",
            "Edtech": "Byju's collapse + CCPA penalties + 60% refund-seeking parents = sector-wide brand damage.",
            "Gaming / Media / Content": "₹81,875 crore GST evasion, 1.6B illegal gaming site visits — legitimacy crisis until Online Gaming Act normalises sector.",
        },
    },
}

# =============================================================================
# REGULATORY CITATIONS — for explainability panel
# =============================================================================
REGULATORY_CITATIONS = {
    "Cyber Technical Risk": [
        "CERT-In Directions 28-Apr-2022 (No. 20(3)/2022-CERT-In) — 6-hr breach, 180-day log retention",
        "IT Act 2000 §§43A, 66F; IT (Amendment) Act 2008",
    ],
    "Data Privacy Risk": [
        "DPDPA 2023 §33 — ₹250 cr maximum penalty per breach",
        "DPDP Rules G.S.R. 846(E) notified 13-Nov-2025 — phased enforcement",
        "DPDP Rules §13 — SDF algorithmic audit obligations",
    ],
    "Regulatory Compliance Risk": [
        "RBI Digital Lending Directions 8-May-2025 — RE vicarious liability for LSP/DLA",
        "PA Directions 15-Sep-2025 — Payment Aggregator compliance",
        "CDSCO SaMD Draft Guidance 21-Oct-2025 — AI diagnostics Class B/C/D",
        "MoE Coaching Guidelines 16-Jan-2024 — 10-day pro-rata refund mandate",
        "Online Gaming Act 2025 (22-Aug-2025) — RMG blanket prohibition",
    ],
    "Gig & Labour Risk": [
        "Social Security Code 2020 §§113-114 — gig aggregator levy",
        "Four Labour Codes effective 21-Nov-2025 (MoLE corrigendum 19-Dec-2025)",
        "Karnataka Platform Gig Workers Bill 2025",
        "Rajasthan Platform-Based Gig Workers Act 2023",
        "Bihar & Jharkhand Gig Worker Acts (Aug 2025)",
        "MV Aggregator Guidelines 2025 — ₹5L health + ₹10L term per driver mandatory",
    ],
    "Geopolitical Risk": [
        "DPIIT Press Note 3 (17-Apr-2020) — government route for land-border country FDI",
        "PN 2 (2026 series) 15-Mar-2026 — liberalisation of PN3 for select sectors",
        "FEMA OI Rules 22-Aug-2022 — overseas investment reporting",
        "CBAM Reg 2023/956 — definitive phase 1-Jan-2026 (EU carbon border levy)",
    ],
    "ESG & Climate Risk": [
        "SEBI BRSR Core Circular 12-Jul-2023; Revised 28-Mar-2025 (value-chain)",
        "Carbon Credit Trading Scheme S.O. 2825(E) 28-Jun-2023",
        "MNRE ALMM List-I 1-Apr-2024; List-II (cells) 1-Jun-2026",
        "Battery Waste Management Rules 2022 GSR 1030(E) — EPR obligation",
        "PWM Amendment Rules 2024 GSR 201(E) — plastic packaging EPR",
    ],
    "Policy Velocity Risk": [
        "Online Gaming Act 2025 assented 22-Aug-2025 — sector-level disruption precedent",
        "MeitY AI Advisory 15-Mar-2024; SGI Rules 10-Feb-2026",
        "Digital Competition Bill draft 12-Mar-2024 — SSDE ex-ante obligations",
        "Competition (Amendment) Act 2023 — Deal Value Threshold ₹2,000cr live 10-Sep-2024",
        "Income-Tax Act 2025 (Act 18 of 2025) effective 1-Apr-2026",
    ],
    "Governance & Fraud Risk": [
        "BharatPe EOW FIR May-2023 — ₹81.3 cr fake-vendor fraud",
        "Paytm Payments Bank Sec 35A halt 31-Jan-2024 (RBI press release prid=57345)",
        "Byju's NCLT admission 16-Jul-2024; US Bankruptcy Court $1.07bn judgment 20-Nov-2025",
        "Companies Act 2013 §2(60) — officer-in-default personal liability",
    ],
    "IP Infringement Risk": [
        "ANI v OpenAI Delhi HC (pending) — AI training data copyright",
        "Patents Act 1970 §48; Trade Marks Act 1999 §29",
        "IT Act 2000 §§65, 66B — source code theft",
    ],
    "Liability Risk": [
        "MV Act 1988 §149 — unlimited third-party liability",
        "Consumer Protection Act 2019 §84 — product liability",
        "IPC §304A — death by negligence (criminal exposure)",
    ],
    "Key Person Risk": [
        "RBI Fit & Proper criteria — MD/CEO approval required",
        "SEBI Listing Regulations Reg 17 — board composition",
    ],
    "Property Risk": [
        "IMD Climate Hazard Atlas — flood/cyclone/heat zones",
        "NDMA Guidelines — natural disaster risk classification",
    ],
    "Reputation Risk": [
        "ASCI Education Sector Guidelines — misleading success-rate ads",
        "Consumer Protection Act 2019 §2(28) — misleading advertisements",
        "IT Rules 2021 Rule 4(1)(d) — takedown obligations for platforms",
    ],
}


# =============================================================================
# RISK SCORING ENGINE — v2 (13 categories, StartupInput dataclass)
# =============================================================================
def compute_risk_scores(inp: StartupInput) -> dict:
    """
    13-category risk engine. Accepts StartupInput dataclass.
    Returns dict of 13 risk category scores (0-100).
    """
    # ── Input validation ──────────────────────────────────────────────────────
    if inp.sector not in SECTOR_PROFILES:
        raise ValueError(f"Unknown sector: {inp.sector!r}")
    if inp.sub_sector and inp.sub_sector in SUB_SECTOR_PROFILES:
        if SUB_SECTOR_PROFILES[inp.sub_sector].get("_hard_decline"):
            raise ValueError(
                f"Hard decline: {inp.sub_sector} — "
                f"{SUB_SECTOR_PROFILES[inp.sub_sector].get('_reason', 'Regulatory prohibition')}"
            )
    if inp.funding_stage not in ("Pre-seed", "Seed", "Series A", "Series B+"):
        raise ValueError(f"Unknown funding stage: {inp.funding_stage!r}")
    if not isinstance(inp.team_size, int) or inp.team_size < 1:
        raise ValueError(f"team_size must be positive int, got {inp.team_size!r}")
    if inp.operations not in ("Digital-only", "Physical-only", "Hybrid"):
        raise ValueError(f"Unknown operations: {inp.operations!r}")
    if inp.data_sensitivity not in ("Low", "Medium", "High"):
        raise ValueError(f"Unknown data_sensitivity: {inp.data_sensitivity!r}")

    # ── Base weights: mutable copy of sector profile ──────────────────────────
    base = dict(SECTOR_PROFILES[inp.sector])

    # ── Sub-sector overrides (absolute values, not deltas) ────────────────────
    if inp.sub_sector and inp.sub_sector in SUB_SECTOR_PROFILES:
        for k, v in SUB_SECTOR_PROFILES[inp.sub_sector].items():
            if not k.startswith("_") and k in base:
                base[k] = min(10, v)

    # ── Stage multipliers (category-specific) ─────────────────────────────────
    default_stage_mult = {
        "Pre-seed": 0.70, "Seed": 0.90, "Series A": 1.10, "Series B+": 1.30,
    }[inp.funding_stage]

    # governance_fraud: U-shaped (high at pre-seed & B+, dips at Seed/A)
    gov_stage_mult = {
        "Pre-seed": 0.90, "Seed": 0.85, "Series A": 1.00, "Series B+": 1.30,
    }[inp.funding_stage]

    # policy_velocity: inverse (mature companies have lobbying/legal buffers)
    policy_stage_mult = {
        "Pre-seed": 1.10, "Seed": 1.00, "Series A": 0.95, "Series B+": 1.00,
    }[inp.funding_stage]

    # ── Team-size multipliers ─────────────────────────────────────────────────
    if inp.team_size <= 5:      team_mult = 0.8;   kp_mult = 1.5
    elif inp.team_size <= 10:   team_mult = 1.0;   kp_mult = 1.4
    elif inp.team_size <= 20:   team_mult = 1.0;   kp_mult = 1.2
    elif inp.team_size <= 50:   team_mult = 1.15;  kp_mult = 1.0
    elif inp.team_size <= 150:  team_mult = 1.30;  kp_mult = 0.85
    else:                       team_mult = 1.50;  kp_mult = 0.7

    # ── Operations multipliers ────────────────────────────────────────────────
    ops_mult = {
        "Digital-only":  {"property": 0.4, "liability": 0.8, "cyber_technical": 1.2, "gig_labour": 0.6},
        "Physical-only": {"property": 1.4, "liability": 1.2, "cyber_technical": 0.7, "gig_labour": 1.3},
        "Hybrid":        {"property": 1.0, "liability": 1.0, "cyber_technical": 1.0, "gig_labour": 1.0},
    }[inp.operations]

    # ── Data sensitivity multipliers ──────────────────────────────────────────
    data_mult = {
        "Low":    {"cyber_technical": 0.6, "data_privacy": 0.5, "regulatory_compliance": 0.8},
        "Medium": {"cyber_technical": 1.0, "data_privacy": 1.0, "regulatory_compliance": 1.0},
        "High":   {"cyber_technical": 1.4, "data_privacy": 1.5, "regulatory_compliance": 1.3},
    }[inp.data_sensitivity]

    # ── Dynamic adjusters from new inputs ─────────────────────────────────────
    # SDF probability → elevates data_privacy (DPDPA §33 ₹250cr)
    sdf_adj = 1.0 + (inp.sdf_probability * 0.5)

    # PN3 / Chinese investor + supply chain → geopolitical elevation
    geo_adj = 1.0 + (inp.investor_cn_hk_pct * 0.8) + (inp.chinese_supplier_pct_cogs * 0.4)

    # Gig headcount → gig_labour elevation
    gig_adj = 1.0 + (inp.gig_headcount_pct * 1.2)

    # Gig Acts in state footprint (KA/RJ/BR/JH/TG most aggressive)
    gig_state_risk = {"Karnataka", "Rajasthan", "Bihar", "Jharkhand", "Telangana"}
    if set(inp.state_footprint) & gig_state_risk and inp.gig_headcount_pct > 0.1:
        gig_adj = min(gig_adj * 1.25, 2.0)

    # Hardware split → property + compliance (BIS QCO, BEE)
    hw_adj = 1.0 + (inp.hardware_software_split * 0.6)

    # Export to EU → esg_climate + geopolitical (CBAM)
    cbam_adj = 1.0 + (inp.export_eu_pct * 1.5)

    # AI in product → policy_velocity + compliance (MeitY + EU AI Act)
    ai_adj = 1.3 if inp.ai_in_product else 1.0

    # Governance: founder concentration + fundraising scale
    gov_adj = (
        1.0
        + (inp.founder_concentration_index * 0.5)
        + (0.3 if inp.cumulative_fundraising_inr_cr > 2000 else 0.0)
    )

    # BRSR push-through: elevates esg_climate
    brsr_adj = 1.2 if inp.listed_customer_brsr_dependency else 1.0

    # Climate risk zone: elevates esg_climate + property
    climate_adj = {"Low": 1.0, "Medium": 1.2, "High": 1.5, "Extreme": 1.8}.get(
        inp.facility_climate_risk_zone, 1.0
    )

    # B2B split: elevates liability (PI contractual exposure)
    b2b_adj = 1.0 + (inp.b2b_pct * 0.4)

    # ── Score computation ─────────────────────────────────────────────────────
    def to_100(x: float) -> float:
        d = decimal.Decimal(str(x * 7.5)).quantize(
            decimal.Decimal("0.1"), rounding=decimal.ROUND_HALF_UP
        )
        return float(max(decimal.Decimal("0"), min(decimal.Decimal("100"), d)))

    team_liability_factor = 0.85 + 0.08 * math.log1p(inp.team_size / 10)

    return {
        "Cyber Technical Risk": to_100(
            base["cyber_technical"]
            * default_stage_mult
            * ops_mult["cyber_technical"]
            * data_mult["cyber_technical"]
        ),
        "Data Privacy Risk": to_100(
            base["data_privacy"]
            * default_stage_mult
            * data_mult["data_privacy"]
            * sdf_adj
        ),
        "Liability Risk": to_100(
            base["liability"]
            * default_stage_mult
            * ops_mult["liability"]
            * team_liability_factor
            * b2b_adj
        ),
        "IP Infringement Risk": to_100(
            base["ip_infringement"]
            * default_stage_mult
        ),
        "Key Person Risk": to_100(
            base["key_person"]
            * kp_mult
            * default_stage_mult
        ),
        "Governance & Fraud Risk": to_100(
            base["governance_fraud"]
            * gov_stage_mult
            * gov_adj
        ),
        "Property Risk": to_100(
            base["property"]
            * ops_mult["property"]
            * team_mult
            * hw_adj
            * climate_adj
        ),
        "Regulatory Compliance Risk": to_100(
            base["regulatory_compliance"]
            * default_stage_mult
            * data_mult["regulatory_compliance"]
            * ai_adj
        ),
        "ESG & Climate Risk": to_100(
            base["esg_climate"]
            * cbam_adj
            * brsr_adj
            * climate_adj
        ),
        "Geopolitical Risk": to_100(
            base["geopolitical"]
            * geo_adj
        ),
        "Gig & Labour Risk": to_100(
            base.get("gig_labour", 3)
            * gig_adj
            * ops_mult["gig_labour"]
            * default_stage_mult
        ),
        "Policy Velocity Risk": to_100(
            base.get("policy_velocity", 5)
            * policy_stage_mult
            * ai_adj
        ),
        "Reputation Risk": to_100(
            base.get("reputation", 5)
            * default_stage_mult
            * team_liability_factor
        ),
    }


def compute_risk_scores_legacy(sector: str, funding_stage: str, team_size: int,
                                operations: str, data_sensitivity: str) -> dict:
    """
    Backward-compatible wrapper. Accepts old positional args, returns original 5 keys.
    Cyber Risk = max(Cyber Technical, Data Privacy)
    Compliance Risk = max(Regulatory Compliance, Policy Velocity)
    """
    inp = StartupInput(
        sector=sector,
        funding_stage=funding_stage,
        team_size=team_size,
        operations=operations,
        data_sensitivity=data_sensitivity,
    )
    s = compute_risk_scores(inp)
    return {
        "Cyber Risk":       max(s["Cyber Technical Risk"], s["Data Privacy Risk"]),
        "Liability Risk":   s["Liability Risk"],
        "Key Person Risk":  s["Key Person Risk"],
        "Property Risk":    s["Property Risk"],
        "Compliance Risk":  max(s["Regulatory Compliance Risk"], s["Policy Velocity Risk"]),
    }


def priority_label(score: float) -> str:
    if score >= 70: return "Critical"
    if score >= 40: return "Recommended"
    return "Optional"


# =============================================================================
# HARD DECLINE CHECKS
# =============================================================================
def check_hard_decline_by_subsector(sub_sector: str) -> Optional[str]:
    """Quick check by sub-sector string alone (for UI pre-validation)."""
    if not sub_sector:
        return None
    profile = SUB_SECTOR_PROFILES.get(sub_sector, {})
    if profile.get("_hard_decline"):
        return profile.get("_reason", "Regulatory prohibition — coverage cannot be bound.")
    return None


def check_hard_decline(inp: StartupInput) -> Optional[str]:
    """Full check including field-level rules. Returns decline reason or None."""
    if inp.sub_sector:
        reason = check_hard_decline_by_subsector(inp.sub_sector)
        if reason:
            return reason
        if (
            inp.sub_sector == "Healthtech.MedDevice_SaMD"
            and SUB_SECTOR_PROFILES["Healthtech.MedDevice_SaMD"].get("_decline_without_cdsco_licence")
        ):
            return (
                "CDSCO SaMD Guidance 21-Oct-2025 requires MD-13/MD-17 licence for "
                "Class B/C/D AI diagnostics. Verify licence before binding coverage."
            )
    if inp.investor_cn_hk_pct > 0.50:
        return (
            "DPIIT Press Note 3 (2020): BO > 50% from land-bordering country. "
            "Regulatory status unclear. Refer to underwriting committee."
        )
    return None


# =============================================================================
# PRODUCT RECOMMENDER
# =============================================================================
def _proportional_boost(score: float, pct: float, floor: float) -> float:
    """Lift score proportionally, capped at 100, guaranteed at least floor."""
    return min(100.0, max(score * (1.0 + pct), floor))


def recommend_products(risk_scores: dict, sector: str, team_size: int,
                       funding_stage: str, inp: Optional[StartupInput] = None) -> list:
    """
    Returns top 5 by fit score, then appends mandatory products not in top 5.
    Pass inp (StartupInput) to activate the new regulatory triggers.
    """
    scored = []
    excluded = set(SECTOR_EXCLUSIONS.get(sector, []))

    for key, weights in PRODUCT_RISK_MAP.items():
        if key in excluded:
            continue
        raw = sum(risk_scores[cat] * w for cat, w in weights.items())
        score = raw / sum(weights.values())
        scored.append((key, score))

    # Proportional sector override boosts
    for key in SECTOR_OVERRIDES.get(sector, []):
        scored = [
            (k, _proportional_boost(s, pct=0.40, floor=50.0)) if k == key else (k, s)
            for k, s in scored
        ]

    # D&O boost: stage-aware AND compliance-aware
    if funding_stage in ("Series A", "Series B+"):
        compliance_factor = 1.0 + (risk_scores["Regulatory Compliance Risk"] / 200.0)
        scored = [
            (k, _proportional_boost(s, pct=0.45 * compliance_factor, floor=55.0))
            if k == "dno_liability" else (k, s)
            for k, s in scored
        ]

    # Team-size boosts
    if team_size >= 10:
        scored = [
            (k, _proportional_boost(s, pct=0.20, floor=40.0)) if k == "employee_health" else (k, s)
            for k, s in scored
        ]
    if team_size >= 25:
        scored = [
            (k, _proportional_boost(s, pct=0.15, floor=38.0)) if k == "employment_practices" else (k, s)
            for k, s in scored
        ]

    # ── New regulatory triggers (modify scored list before sort) ─────────────
    if inp is not None:
        # Gig worker exposure → employees_comp + employment_practices + group_pa
        # Basis: CoSS 2020 §114; MV Aggregator Guidelines 2025; state gig Acts
        if inp.gig_headcount_pct > 0.30:
            for key in ["employees_comp", "employment_practices", "group_pa"]:
                scored = [
                    (k, _proportional_boost(s, pct=0.45, floor=55.0)) if k == key else (k, s)
                    for k, s in scored
                ]

        # Hardware / BIS QCO → product_liability auto-surface
        # Basis: CPA 2019 §84; BIS QCO 2024 IS 17043/15844
        if inp.hardware_software_split > 0.30:
            scored = [
                (k, _proportional_boost(s, pct=0.50, floor=60.0)) if k == "product_liability" else (k, s)
                for k, s in scored
            ]

        # CBAM / EU export → trade_credit + marine_transit
        # Basis: CBAM Reg 2023/956 definitive phase 1-Jan-2026
        if inp.export_eu_pct > 0.10:
            for key in ["trade_credit", "marine_transit"]:
                scored = [
                    (k, _proportional_boost(s, pct=0.35, floor=50.0)) if k == key else (k, s)
                    for k, s in scored
                ]

        # PN3 / Chinese BO or DVT → D&O + crime_fidelity
        # Basis: DPIIT Press Note 3 (2020); Competition DVT 10-Sep-2024 (₹2,000cr)
        if inp.investor_cn_hk_pct > 0.10 or inp.cumulative_fundraising_inr_cr > 2000:
            for key in ["dno_liability", "crime_fidelity"]:
                scored = [
                    (k, _proportional_boost(s, pct=0.40, floor=55.0)) if k == key else (k, s)
                    for k, s in scored
                ]

        # AI in product → professional_indemnity (affirmative-AI PI)
        # Basis: MeitY Advisory 15-Mar-2024; SGI Rules 10-Feb-2026; EU AI Act Art 2(1)(c)
        if inp.ai_in_product:
            scored = [
                (k, _proportional_boost(s, pct=0.40, floor=55.0)) if k == "professional_indemnity" else (k, s)
                for k, s in scored
            ]

        # RBI registration → dno_liability + business_interruption
        # Basis: RBI Sec 35A precedent — Paytm PB 31-Jan-2024, Kotak 24-Apr-2024
        if inp.rbi_registration is not None:
            for key in ["dno_liability", "business_interruption"]:
                scored = [
                    (k, _proportional_boost(s, pct=0.45, floor=60.0)) if k == key else (k, s)
                    for k, s in scored
                ]

        # BRSR value-chain dependency → enterprise_secure advisory
        # Basis: SEBI BRSR Core + Value-Chain Circular 28-Mar-2025
        if inp.listed_customer_brsr_dependency:
            scored = [
                (k, _proportional_boost(s, pct=0.25, floor=45.0)) if k == "enterprise_secure" else (k, s)
                for k, s in scored
            ]

    scored = [(k, min(100.0, s)) for k, s in scored]
    scored.sort(key=lambda x: x[1], reverse=True)
    scored_lookup = dict(scored)

    if len(scored) < 5:
        warnings.warn(
            f"Only {len(scored)} eligible products for sector '{sector}'. "
            "Consider reviewing SECTOR_EXCLUSIONS.",
            stacklevel=2,
        )

    top5 = scored[:5]
    top5_keys = {k for k, _ in top5}

    results = []
    result_keys = set()
    for key, score in top5:
        product = PRODUCT_CATALOG[key].copy()
        product["key"] = key
        product["score"] = round(score, 1)
        product["priority"] = priority_label(product["score"])
        product["mandatory"] = False
        results.append(product)
        result_keys.add(key)

    def append_mandatory(key: str, fallback_score: float = 0.0) -> None:
        if key in excluded or key in result_keys or key not in PRODUCT_CATALOG:
            return
        score = round(scored_lookup.get(key, fallback_score), 1)
        product = PRODUCT_CATALOG[key].copy()
        product["key"] = key
        product["score"] = score
        product["priority"] = priority_label(score)
        product["mandatory"] = True
        results.append(product)
        result_keys.add(key)

    for key in SECTOR_OVERRIDES.get(sector, []):
        if key not in top5_keys:
            append_mandatory(key)

    if funding_stage in ("Series A", "Series B+") and "dno_liability" not in top5_keys:
        append_mandatory("dno_liability")

    # ── New mandatory triggers (require append_mandatory to be defined) ───────
    if inp is not None:
        # SaMD → clinical_trials + product_liability mandatory
        # Basis: CDSCO SaMD Draft Guidance 21-Oct-2025; MDR 2017
        if inp.sub_sector == "Healthtech.MedDevice_SaMD":
            append_mandatory("clinical_trials")
            append_mandatory("product_liability")

        # MV Aggregator Guidelines 2025 → group_pa + employees_comp mandatory
        # Basis: MoRTH Aggregator Guidelines Jul-2025 (₹5L health + ₹10L term per driver)
        if (
            sector in ("Logistics / Mobility", "Foodtech / Cloud Kitchen")
            and inp.gig_headcount_pct > 0.20
        ):
            append_mandatory("group_pa")
            append_mandatory("employees_comp")

    append_mandatory("employee_health", fallback_score=40.0)

    return results


# =============================================================================
# CONFIG VALIDATOR — runs at import time
# =============================================================================
def validate_config() -> None:
    """
    Raises ValueError if:
    - Any product key is in both OVERRIDES and EXCLUSIONS for the same sector
    - Any override/exclusion key doesn't exist in PRODUCT_CATALOG
    Sub-sector keys in SECTOR_EXCLUSIONS (contain '.') are validated for product
    key existence but skipped for override-conflict checks.
    """
    errors = []
    all_keys = set(PRODUCT_CATALOG.keys())

    for sector, overrides in SECTOR_OVERRIDES.items():
        exclusions = set(SECTOR_EXCLUSIONS.get(sector, []))
        conflicts = [k for k in overrides if k in exclusions]
        if conflicts:
            errors.append(
                f"  CONFLICT in '{sector}': {conflicts} are in both OVERRIDES and EXCLUSIONS."
            )
        for k in overrides:
            if k not in all_keys:
                errors.append(f"  OVERRIDE key '{k}' in '{sector}' missing from PRODUCT_CATALOG.")

    for sector, excl_keys in SECTOR_EXCLUSIONS.items():
        for k in excl_keys:
            if k not in all_keys:
                errors.append(f"  EXCLUSION key '{k}' in '{sector}' missing from PRODUCT_CATALOG.")

    if errors:
        raise ValueError("Risk engine config errors found:\n" + "\n".join(errors))


validate_config()  # runs once at import — catches config bugs immediately
