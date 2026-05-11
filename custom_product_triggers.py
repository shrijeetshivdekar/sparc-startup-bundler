CUSTOM_PRODUCT_TRIGGERS = {
    "ai_model_performance_parametric": {
        "trigger_conditions": {
            "ai_tier": ["Foundational", "Applied"],
            "min_score": {"IP Infringement Risk": 75, "Liability Risk": 70},
        },
        "description": "Parametric AI model performance warranty that pays on measurable accuracy degradation, hallucination liability, training-data IP claims, or algorithmic bias claims.",
        "global_precedent": "Armilla AI Warranty (Lloyd's) / Munich Re aiSure",
        "irdai_path": "IRDAI Sandbox or Lloyd's India placement",
        "estimated_market_size": "INR 200-500 cr TAM by 2027",
        "sectors": ["Deeptech / AI / Robotics", "SaaS / Enterprise Software", "Healthtech", "Fintech"],
    },
    "quantum_cryptographic_liability": {
        "trigger_conditions": {
            "min_score": {"Cyber Technical Risk": 80, "IP Infringement Risk": 75},
            "ai_tier": ["Foundational"],
        },
        "description": "Covers cryptographic obsolescence and harvest-now-decrypt-later liability once quantum computing weakens current encryption.",
        "global_precedent": "IBM Quantum Risk Advisory / UK NCSC post-quantum guidance",
        "irdai_path": "Lloyd's India or IRDAI Sandbox",
        "estimated_market_size": "INR 50-150 cr TAM by 2028",
        "sectors": ["Fintech", "Healthtech", "Deeptech / AI / Robotics", "SaaS / Enterprise Software"],
    },
    "cbam_carbon_levy_parametric": {
        "trigger_conditions": {
            "min_score": {"ESG & Climate Risk": 70, "Geopolitical Risk": 65},
            "export_eu_pct_min": 0.10,
        },
        "description": "Parametric cover paying when EU CBAM levies materially exceed projected rates.",
        "global_precedent": "Kita Carbon Insurance / Oka carbon credit covers",
        "irdai_path": "IRDAI Sandbox parametric structure",
        "estimated_market_size": "INR 100-300 cr TAM by 2027",
        "sectors": ["Cleantech / Climatetech", "D2C / Consumer Brands", "Agritech", "Logistics / Mobility"],
    },
    "gig_platform_wage_protection": {
        "trigger_conditions": {
            "min_score": {"Gig & Labour Risk": 75, "Regulatory Compliance Risk": 70},
            "gig_headcount_pct_min": 0.30,
        },
        "description": "Income replacement cover for gig/platform workers when illness, accident, or platform suspension prevents work.",
        "global_precedent": "Deliveroo x Zurich / Uber x AXA / Stride Health",
        "irdai_path": "IRDAI Sandbox or micro-insurance route",
        "estimated_market_size": "INR 300-800 cr TAM by 2027",
        "sectors": ["Logistics / Mobility", "Foodtech / Cloud Kitchen", "HRtech", "Agritech"],
    },
    "carbon_credit_invalidation": {
        "trigger_conditions": {
            "min_score": {"ESG & Climate Risk": 75},
            "export_eu_pct_min": 0.05,
        },
        "description": "Covers carbon-credit invalidation from additionality failures, double-counting, registry fraud, or retroactive decertification.",
        "global_precedent": "Kita Carbon Credit Invalidation Cover / Oka Re",
        "irdai_path": "Lloyd's India syndicate placement or IRDAI Sandbox",
        "estimated_market_size": "INR 50-200 cr TAM by 2027",
        "sectors": ["Cleantech / Climatetech", "Agritech"],
    },
    "large_industrial_property": {
        "trigger_conditions": {
            "min_score": {"Property Risk": 70},
            "min_attr": {"total_insurable_asset_value_cr": 50},
        },
        "description": "Industrial All Risk / Large Property bundle referral for high-SI property, machinery, business interruption, and equipment breakdown exposure.",
        "global_precedent": "Industrial All Risk / Property All Risk package wording",
        "irdai_path": "Commercial property package underwriting",
        "estimated_market_size": "INR 1,000-1,800 cr TAM",
        "sectors": ["D2C / Consumer Brands", "Deeptech / AI / Robotics", "Cleantech / Climatetech", "Logistics / Mobility"],
    },
    "fleet_commercial_motor": {
        "trigger_conditions": {
            "min_score": {"Liability Risk": 65, "Gig & Labour Risk": 55},
            "min_attr": {"fleet_count": 1},
        },
        "description": "Mobility / Delivery Fleet bundle trigger for owned or operated vehicles, rider fleets, field service vehicles, goods carriers, or trailers.",
        "global_precedent": "Commercial motor package and fleet policies",
        "irdai_path": "Motor package underwriting",
        "estimated_market_size": "INR 1,500-2,500 cr TAM",
        "sectors": ["Logistics / Mobility", "D2C / Consumer Brands", "Foodtech / Cloud Kitchen"],
    },
    "healthcare_medical_liability": {
        "trigger_conditions": {
            "min_score": {"Liability Risk": 70, "Regulatory Compliance Risk": 70},
            "bool_attr": ["healthcare_operations"],
        },
        "description": "Healthcare / Medical Liability bundle trigger for clinics, diagnostics, telemedicine, medtech delivery, and patient-facing healthcare operations.",
        "global_precedent": "Professional Indemnity for Doctors / Healthcare PI",
        "irdai_path": "Professional liability underwriting",
        "estimated_market_size": "INR 750-1,250 cr TAM",
        "sectors": ["Healthtech"],
    },
    "fintech_payment_protection": {
        "trigger_conditions": {
            "min_score": {"Cyber Technical Risk": 75, "Regulatory Compliance Risk": 75, "Governance & Fraud Risk": 70},
            "bool_attr": ["payment_or_card_program"],
        },
        "description": "Fintech / FI Liability bundle trigger for RBI-regulated lending, payments, card programs, KYC data, payment protection, crime, and FI PI exposure.",
        "global_precedent": "Financial institution PI / card and payment protection policies",
        "irdai_path": "Financial lines underwriting",
        "estimated_market_size": "INR 900-1,500 cr TAM",
        "sectors": ["Fintech"],
    },
    "product_recall_contamination": {
        "trigger_conditions": {
            "min_score": {"Liability Risk": 70, "Reputation Risk": 70},
            "bool_attr_any": ["product_recall_exposure", "food_or_pharma_manufacturing"],
        },
        "description": "Product Recall / Contamination bundle trigger for batch manufacturing, FSSAI, food/pharma, nutraceutical, cosmetics, hardware, or consumer goods recall exposure.",
        "global_precedent": "Total Recall / product recall and contamination policies",
        "irdai_path": "Commercial liability underwriting",
        "estimated_market_size": "INR 650-1,000 cr TAM",
        "sectors": ["D2C / Consumer Brands", "Healthtech", "Agritech / Foodtech", "Foodtech / Cloud Kitchen"],
    },
    "surety_contract_performance": {
        "trigger_conditions": {
            "min_score": {"Governance & Fraud Risk": 60, "Regulatory Compliance Risk": 60},
            "bool_attr_any": ["contract_bid_or_performance_bond_need"],
            "min_attr_any": {"project_value_cr": 1, "capex_project_value_cr": 1},
        },
        "description": "Surety / Contract Performance bundle referral for bid bonds, performance bonds, EPC projects, solar projects, or government/PSU contracts.",
        "global_precedent": "IRDAI surety insurance guidelines and contract guarantee products",
        "irdai_path": "Surety underwriter referral",
        "estimated_market_size": "INR 500-900 cr TAM",
        "sectors": ["Cleantech / Climatetech", "Deeptech / AI / Robotics", "D2C / Consumer Brands"],
    },
    "event_production_package": {
        "trigger_conditions": {
            "min_score": {"Liability Risk": 60, "Reputation Risk": 60},
            "bool_attr": ["event_or_production_operations"],
        },
        "description": "Media / Entertainment Production bundle trigger for active event, film, ad, creator-economy, venue, equipment, and production interruption exposure.",
        "global_precedent": "Entertainment Production Package policies",
        "irdai_path": "Commercial package underwriting",
        "estimated_market_size": "INR 250-450 cr TAM",
        "sectors": ["Gaming / Media / Content"],
    },
}


def _name_from_key(key: str) -> str:
    return key.replace("_", " ").title()


def _get(source, key, default=None):
    if isinstance(source, dict):
        return source.get(key, default)
    return getattr(source, key, default)


def _flag(context, key: str) -> bool:
    value = _get(context, key, False)
    if isinstance(value, str):
        return value.strip().lower() in ("yes", "true", "1", "y")
    return bool(value)


def check_custom_triggers(scores: dict, inp, profile: dict | None = None) -> list[dict]:
    triggered = []
    context = profile or inp
    for key, trigger in CUSTOM_PRODUCT_TRIGGERS.items():
        cond = trigger["trigger_conditions"]
        reasons = []
        if _get(context, "sector") not in trigger.get("sectors", []):
            continue
        if not all(scores.get(cat, 0) >= minimum for cat, minimum in cond.get("min_score", {}).items()):
            continue
        for cat, minimum in cond.get("min_score", {}).items():
            reasons.append(f"{cat}: {scores.get(cat, 0):.0f} >= trigger threshold {minimum}")
        if "ai_tier" in cond and _get(context, "ai_tier", "None") not in cond["ai_tier"]:
            continue
        if "export_eu_pct_min" in cond:
            if _get(context, "export_eu_pct", 0.0) < cond["export_eu_pct_min"]:
                continue
            reasons.append(f"EU revenue {_get(context, 'export_eu_pct', 0.0) * 100:.0f}% >= threshold {cond['export_eu_pct_min'] * 100:.0f}%")
        if "gig_headcount_pct_min" in cond:
            if _get(context, "gig_headcount_pct", 0.0) < cond["gig_headcount_pct_min"]:
                continue
            reasons.append(f"Gig workforce {_get(context, 'gig_headcount_pct', 0.0) * 100:.0f}% >= threshold {cond['gig_headcount_pct_min'] * 100:.0f}%")
        if "bool_attr" in cond:
            missing = [attr for attr in cond["bool_attr"] if not _flag(context, attr)]
            if missing:
                continue
            reasons.extend(f"{attr} is true" for attr in cond["bool_attr"])
        if "bool_attr_any" in cond and "min_attr_any" in cond:
            matched_any = [f"{attr} is true" for attr in cond["bool_attr_any"] if _flag(context, attr)]
            for attr, minimum in cond["min_attr_any"].items():
                value = float(_get(context, attr, 0.0) or 0.0)
                if value >= minimum:
                    matched_any.append(f"{attr} {value:.1f} >= threshold {minimum}")
            if not matched_any:
                continue
            reasons.extend(matched_any)
        elif "bool_attr_any" in cond:
            if not any(_flag(context, attr) for attr in cond["bool_attr_any"]):
                continue
            reasons.extend(f"{attr} is true" for attr in cond["bool_attr_any"] if _flag(context, attr))
        if "min_attr" in cond:
            blocked = False
            for attr, minimum in cond["min_attr"].items():
                value = float(_get(context, attr, 0.0) or 0.0)
                if value < minimum:
                    blocked = True
                    break
                reasons.append(f"{attr} {value:.1f} >= threshold {minimum}")
            if blocked:
                continue
        if "min_attr_any" in cond and "bool_attr_any" not in cond:
            matched = []
            for attr, minimum in cond["min_attr_any"].items():
                value = float(_get(context, attr, 0.0) or 0.0)
                if value >= minimum:
                    matched.append(f"{attr} {value:.1f} >= threshold {minimum}")
            if not matched:
                continue
            reasons.extend(matched)
        triggered.append({
            "key": key,
            "name": _name_from_key(key),
            "description": trigger["description"],
            "global_precedent": trigger["global_precedent"],
            "irdai_path": trigger["irdai_path"],
            "estimated_market_size": trigger["estimated_market_size"],
            "triggered_by": reasons,
        })
    return triggered
