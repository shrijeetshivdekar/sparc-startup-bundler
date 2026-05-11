STARTUP_SIZE_BUCKETS = {
    "micro": {"stages": ["Pre-seed", "Seed"], "team_max": 25},
    "small": {"stages": ["Series A"], "team_max": 100},
    "growth": {"stages": ["Series B+"], "team_max": 500},
}

PREMIUM_RANGES = {
    "cyber_liability": {
        "micro": {"min_lakh": 0.5, "max_lakh": 2.5, "basis": "INR 1cr SI, digital-only, basic controls"},
        "small": {"min_lakh": 2.5, "max_lakh": 9.0, "basis": "INR 5cr SI, Series A, DPDPA compliance"},
        "growth": {"min_lakh": 9.0, "max_lakh": 30.0, "basis": "INR 25cr SI, Series B+, SDF-likely"},
    },
    "dno_liability": {
        "micro": {"min_lakh": 0.8, "max_lakh": 2.0, "basis": "INR 2cr SI, seed-stage founders"},
        "small": {"min_lakh": 2.0, "max_lakh": 6.0, "basis": "INR 5cr SI, Series A, institutional investors"},
        "growth": {"min_lakh": 6.0, "max_lakh": 20.0, "basis": "INR 25cr SI, Series B+, listed-company exposure"},
    },
    "professional_indemnity": {
        "micro": {"min_lakh": 0.3, "max_lakh": 1.5, "basis": "INR 1cr SI, small client base"},
        "small": {"min_lakh": 1.5, "max_lakh": 5.0, "basis": "INR 5cr SI, enterprise B2B contracts"},
        "growth": {"min_lakh": 5.0, "max_lakh": 18.0, "basis": "INR 25cr SI, large-enterprise contracts"},
    },
    "employee_health": {
        "micro": {"min_lakh": 0.5, "max_lakh": 2.0, "basis": "INR 3L floater, 10 employees"},
        "small": {"min_lakh": 2.0, "max_lakh": 8.0, "basis": "INR 5L floater, 50 employees"},
        "growth": {"min_lakh": 8.0, "max_lakh": 25.0, "basis": "INR 5L floater, 150 employees"},
    },
    "group_pa": {
        "micro": {"min_lakh": 0.1, "max_lakh": 0.4, "basis": "INR 10L cover, 10 employees"},
        "small": {"min_lakh": 0.4, "max_lakh": 1.5, "basis": "INR 10L cover, 50 employees"},
        "growth": {"min_lakh": 1.5, "max_lakh": 5.0, "basis": "INR 10L cover, 150 employees"},
    },
    "group_criti_shield": {
        "micro": {"min_lakh": 0.05, "max_lakh": 0.30, "basis": "INR 5L critical illness cover, 10 employees"},
        "small": {"min_lakh": 0.30, "max_lakh": 1.20, "basis": "INR 5L cover, 50 employees"},
        "growth": {"min_lakh": 1.20, "max_lakh": 4.00, "basis": "INR 10L cover, 150 employees"},
    },
    "group_hospishield": {
        "micro": {"min_lakh": 0.06, "max_lakh": 0.40, "basis": "INR 1,000/day hospital cash, 10 employees"},
        "small": {"min_lakh": 0.40, "max_lakh": 1.50, "basis": "INR 1,000/day, 50 employees"},
        "growth": {"min_lakh": 1.50, "max_lakh": 5.00, "basis": "INR 2,000/day, 150 employees"},
    },
    "employees_comp": {
        "micro": {"min_lakh": 0.2, "max_lakh": 0.8, "basis": "Small team, limited hazardous ops"},
        "small": {"min_lakh": 0.8, "max_lakh": 2.5, "basis": "Mid-size team, moderate hazardous ops"},
        "growth": {"min_lakh": 2.5, "max_lakh": 8.0, "basis": "Large team, warehouse/logistics ops"},
    },
    "property_fire": {
        "micro": {"min_lakh": 0.50, "max_lakh": 2.00, "basis": "INR 2Cr property; post-IRDAI de-tariff Apr 2024"},
        "small": {"min_lakh": 2.00, "max_lakh": 6.50, "basis": "INR 10Cr property; non-tariff SME market rate"},
        "growth": {"min_lakh": 6.50, "max_lakh": 22.00, "basis": "INR 50Cr property; market range post-de-notification"},
    },
    "business_edge": {
        "micro": {"min_lakh": 0.4, "max_lakh": 1.5, "basis": "Package: fire+burglary+PL, SME"},
        "small": {"min_lakh": 1.5, "max_lakh": 5.0, "basis": "Package: comprehensive, mid-size"},
        "growth": {"min_lakh": 5.0, "max_lakh": 15.0, "basis": "Package: full suite, growth"},
    },
    "public_liability": {
        "micro": {"min_lakh": 0.2, "max_lakh": 0.8, "basis": "INR 1cr limit, small premises"},
        "small": {"min_lakh": 0.8, "max_lakh": 2.5, "basis": "INR 2cr limit, medium operations"},
        "growth": {"min_lakh": 2.5, "max_lakh": 8.0, "basis": "INR 5cr limit, multi-site ops"},
    },
    "product_liability": {
        "micro": {"min_lakh": 0.4, "max_lakh": 1.5, "basis": "INR 2cr SI, single product line"},
        "small": {"min_lakh": 1.5, "max_lakh": 5.0, "basis": "INR 5cr SI, multiple product lines"},
        "growth": {"min_lakh": 5.0, "max_lakh": 18.0, "basis": "INR 20cr SI, large production volume"},
    },
    "marine_transit": {
        "micro": {"min_lakh": 0.2, "max_lakh": 1.0, "basis": "Open cover, INR 50L goods per month"},
        "small": {"min_lakh": 1.0, "max_lakh": 3.5, "basis": "Open cover, INR 2cr goods per month"},
        "growth": {"min_lakh": 3.5, "max_lakh": 12.0, "basis": "Open cover, INR 10cr goods per month"},
    },
    "key_person": {
        "micro": {"min_lakh": 0.5, "max_lakh": 1.5, "basis": "INR 2cr cover, 1 founder"},
        "small": {"min_lakh": 1.5, "max_lakh": 4.0, "basis": "INR 5cr cover, 2 key persons"},
        "growth": {"min_lakh": 4.0, "max_lakh": 12.0, "basis": "INR 15cr cover, leadership team"},
    },
    "employment_practices": {
        "micro": {"min_lakh": 0.40, "max_lakh": 1.20, "basis": "INR 1Cr limit, team < 25, low POSH exposure"},
        "small": {"min_lakh": 1.20, "max_lakh": 3.50, "basis": "INR 3Cr limit, Series A, 50 employees"},
        "growth": {"min_lakh": 3.50, "max_lakh": 10.00, "basis": "INR 10Cr limit, Series B+, 150+ employees"},
    },
    "crime_fidelity": {
        "micro": {"min_lakh": 0.3, "max_lakh": 1.0, "basis": "INR 50L coverage, small finance ops"},
        "small": {"min_lakh": 1.0, "max_lakh": 3.5, "basis": "INR 2cr coverage, mid-size finance"},
        "growth": {"min_lakh": 3.5, "max_lakh": 12.0, "basis": "INR 10cr coverage, large payment ops"},
    },
    "gadget_equipment": {
        "micro": {"min_lakh": 0.1, "max_lakh": 0.5, "basis": "10 devices, INR 30L cover"},
        "small": {"min_lakh": 0.5, "max_lakh": 1.5, "basis": "50 devices, INR 1.5cr cover"},
        "growth": {"min_lakh": 1.5, "max_lakh": 5.0, "basis": "150 devices, INR 5cr cover"},
    },
    "clinical_trials": {
        "micro": {"min_lakh": 1.0, "max_lakh": 4.0, "basis": "Phase 1 trial, INR 5cr liability"},
        "small": {"min_lakh": 4.0, "max_lakh": 12.0, "basis": "Phase 2 trial, INR 20cr liability"},
        "growth": {"min_lakh": 12.0, "max_lakh": 40.0, "basis": "Phase 3 trial, INR 100cr liability"},
    },
    "comprehensive_general_liability": {
        "micro": {"min_lakh": 0.3, "max_lakh": 1.2, "basis": "INR 1cr limit, small B2B"},
        "small": {"min_lakh": 1.2, "max_lakh": 4.0, "basis": "INR 3cr limit, enterprise contracts"},
        "growth": {"min_lakh": 4.0, "max_lakh": 12.0, "basis": "INR 10cr limit, large-enterprise"},
    },
    "business_interruption": {
        "micro": {"min_lakh": 0.3, "max_lakh": 1.0, "basis": "INR 50L BI cover, 90 days indemnity"},
        "small": {"min_lakh": 1.0, "max_lakh": 4.0, "basis": "INR 2cr BI cover, 180 days indemnity"},
        "growth": {"min_lakh": 4.0, "max_lakh": 15.0, "basis": "INR 10cr BI cover, 365 days indemnity"},
    },
    "property_all_risk": {
        "micro": {"min_lakh": 0.5, "max_lakh": 2.0, "basis": "INR 3cr property, lab/equipment"},
        "small": {"min_lakh": 2.0, "max_lakh": 7.0, "basis": "INR 15cr property, pilot plant"},
        "growth": {"min_lakh": 7.0, "max_lakh": 25.0, "basis": "INR 75cr property, full facility"},
    },
    "electronic_equipment": {
        "micro": {"min_lakh": 0.3, "max_lakh": 1.2, "basis": "INR 1cr EEI SI, GPU/servers"},
        "small": {"min_lakh": 1.2, "max_lakh": 4.0, "basis": "INR 5cr EEI SI, data centre"},
        "growth": {"min_lakh": 4.0, "max_lakh": 15.0, "basis": "INR 25cr EEI SI, large infra"},
    },
    "machinery_breakdown": {
        "micro": {"min_lakh": 0.2, "max_lakh": 0.8, "basis": "INR 1cr machinery, small plant"},
        "small": {"min_lakh": 0.8, "max_lakh": 3.0, "basis": "INR 5cr machinery, mid plant"},
        "growth": {"min_lakh": 3.0, "max_lakh": 10.0, "basis": "INR 25cr machinery, large plant"},
    },
    "motor_fleet": {
        "micro": {"min_lakh": 0.5, "max_lakh": 2.0, "basis": "5-vehicle fleet"},
        "small": {"min_lakh": 2.0, "max_lakh": 7.0, "basis": "20-vehicle fleet"},
        "growth": {"min_lakh": 7.0, "max_lakh": 25.0, "basis": "100-vehicle fleet"},
    },
    "healthcare_pi": {
        "micro": {"min_lakh": 0.8, "max_lakh": 2.5, "basis": "Small clinic/diagnostic exposure, INR 1-2cr PI limit"},
        "small": {"min_lakh": 2.5, "max_lakh": 9.0, "basis": "Multi-location healthtech, INR 5cr PI limit"},
        "growth": {"min_lakh": 9.0, "max_lakh": 30.0, "basis": "Scaled clinical operations, INR 20cr+ PI limit"},
    },
    "financial_services_pi": {
        "micro": {"min_lakh": 1.0, "max_lakh": 3.5, "basis": "Small regulated fintech, INR 2cr FI PI limit"},
        "small": {"min_lakh": 3.5, "max_lakh": 12.0, "basis": "NBFC/payment profile, INR 5-10cr FI PI limit"},
        "growth": {"min_lakh": 12.0, "max_lakh": 40.0, "basis": "Growth fintech, INR 25cr+ FI PI limit"},
    },
    "payment_protection": {
        "micro": {"min_lakh": 0.5, "max_lakh": 1.8, "basis": "Low-volume card/payment programme"},
        "small": {"min_lakh": 1.8, "max_lakh": 6.0, "basis": "Series A payment/embedded finance exposure"},
        "growth": {"min_lakh": 6.0, "max_lakh": 20.0, "basis": "Large payment programme and customer compensation exposure"},
    },
    "product_recall": {
        "micro": {"min_lakh": 0.7, "max_lakh": 2.5, "basis": "Small batch production and basic recall limit"},
        "small": {"min_lakh": 2.5, "max_lakh": 8.0, "basis": "D2C/FSSAI production, INR 5cr recall limit"},
        "growth": {"min_lakh": 8.0, "max_lakh": 28.0, "basis": "Scaled FMCG/pharma/hardware recall exposure"},
    },
    "event_production": {
        "micro": {"min_lakh": 0.4, "max_lakh": 1.2, "basis": "Small event or production budget"},
        "small": {"min_lakh": 1.2, "max_lakh": 5.0, "basis": "Series A production/event slate"},
        "growth": {"min_lakh": 5.0, "max_lakh": 18.0, "basis": "Large production schedule and venue/equipment exposure"},
    },
    "surety": {
        "micro": {"min_lakh": 0.8, "max_lakh": 2.5, "basis": "Small bid/performance bond need"},
        "small": {"min_lakh": 2.5, "max_lakh": 10.0, "basis": "EPC/solar project, INR 10cr contract value"},
        "growth": {"min_lakh": 10.0, "max_lakh": 35.0, "basis": "Large contract performance exposure"},
    },
    "trade_credit": {
        "micro": {"min_lakh": 0.4, "max_lakh": 1.5, "basis": "INR 2cr receivables"},
        "small": {"min_lakh": 1.5, "max_lakh": 5.0, "basis": "INR 10cr receivables"},
        "growth": {"min_lakh": 5.0, "max_lakh": 18.0, "basis": "INR 50cr receivables"},
    },
    "money_insurance": {
        "micro": {"min_lakh": 0.1, "max_lakh": 0.4, "basis": "INR 5L cash limit"},
        "small": {"min_lakh": 0.4, "max_lakh": 1.2, "basis": "INR 20L cash limit"},
        "growth": {"min_lakh": 1.2, "max_lakh": 4.0, "basis": "INR 1cr cash limit"},
    },
    "contractors_all_risk": {
        "micro": {"min_lakh": 0.5, "max_lakh": 2.0, "basis": "INR 2cr project value"},
        "small": {"min_lakh": 2.0, "max_lakh": 8.0, "basis": "INR 10cr project value"},
        "growth": {"min_lakh": 8.0, "max_lakh": 30.0, "basis": "INR 50cr project value"},
    },
    "drone_insurance": {
        "micro": {"min_lakh": 0.3, "max_lakh": 1.0, "basis": "2 drones, INR 50L hull"},
        "small": {"min_lakh": 1.0, "max_lakh": 3.5, "basis": "10 drones, INR 2cr hull"},
        "growth": {"min_lakh": 3.5, "max_lakh": 12.0, "basis": "50 drones, INR 10cr hull"},
    },
    "msme_suraksha": {
        "micro": {"min_lakh": 0.3, "max_lakh": 1.0, "basis": "INR 50L insurable value, all perils"},
        "small": {"min_lakh": 1.0, "max_lakh": 3.5, "basis": "INR 2cr insurable value"},
        "growth": {"min_lakh": 3.5, "max_lakh": 10.0, "basis": "INR 10cr insurable value"},
    },
    "enterprise_secure": {
        "micro": {"min_lakh": 0.8, "max_lakh": 2.5, "basis": "Package: property+BI+PL"},
        "small": {"min_lakh": 2.5, "max_lakh": 8.0, "basis": "Package: full suite, Series A"},
        "growth": {"min_lakh": 8.0, "max_lakh": 25.0, "basis": "Package: enterprise suite"},
    },
}

PREMIUM_FOOTNOTE = (
    "Indicative estimates only. Actual premium is subject to underwriting, "
    "sum insured selection, risk controls, and claims history. Base rates reflect "
    "post-IRDAI fire de-tariff (April 2024) market and Indian startup segment "
    "benchmarks as of Q1 2026. Sources: Mitigata Cyber Insurance India 2026; "
    "BimaKavach D&O startup benchmarks; BusinessStandard fire premium analysis "
    "Dec 2024; NivaaBupa/Pazcare group health data; IRDAI Annual Report 2023-24. "
    "Products recommended are individual ICICI Lombard policies or curated "
    "co-cover sets - not all bundle names are single named policies."
)


def get_size_bucket(funding_stage: str, team_size: int) -> str:
    if funding_stage in STARTUP_SIZE_BUCKETS["micro"]["stages"] and team_size <= 25:
        return "micro"
    if funding_stage in STARTUP_SIZE_BUCKETS["growth"]["stages"]:
        return "growth"
    return "small"


def estimate_premium(product_key: str, size_bucket: str) -> dict | None:
    return PREMIUM_RANGES.get(product_key, {}).get(size_bucket)


def format_premium(min_lakh: float, max_lakh: float) -> str:
    return f"INR {min_lakh:.1f} - {max_lakh:.1f} lakhs"
