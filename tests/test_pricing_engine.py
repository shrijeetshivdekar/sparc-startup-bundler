import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pricing_engine import infer_underwriting_inputs, price_output_stage
from startup_shield_web import server


BASE_SCORES = {
    "Cyber Technical Risk": 82,
    "Data Privacy Risk": 78,
    "Liability Risk": 64,
    "IP Infringement Risk": 58,
    "Key Person Risk": 55,
    "Governance & Fraud Risk": 72,
    "Property Risk": 45,
    "Regulatory Compliance Risk": 75,
    "ESG & Climate Risk": 30,
    "Geopolitical Risk": 45,
    "Gig & Labour Risk": 30,
    "Policy Velocity Risk": 66,
    "Reputation Risk": 61,
}


def test_pricing_engine_prices_bundle_components_with_gst():
    profile = {
        "sector": "Fintech",
        "funding_stage": "Series A",
        "team_size": 60,
        "data_sensitivity": "High",
        "has_investors": "Yes",
        "physical_assets": ["Office / coworking space"],
        "data_handled": ["Payments / financial transactions"],
        "b2b_pct": 0.9,
        "quote_requested": True,
        "cyber_limit_cr": 7.5,
        "dno_limit_cr": 5.0,
        "pi_limit_cr": 5.0,
    }
    bundle = {
        "name": "Startup Shield Pack",
        "mandatory_covers": ["CYBER", "D_AND_O", "PI_TECH_EO"],
        "optional_covers": [],
    }

    quote = price_output_stage(profile, BASE_SCORES, [], bundle)

    assert quote["gross_premium_lakh"] > quote["net_premium_lakh"] > 0
    assert quote["gst_lakh"] > 0
    assert quote["cover_count"] == 3
    assert {item["cover_key"] for item in quote["covers_priced"]} == {
        "cyber_liability",
        "dno_liability",
        "professional_indemnity",
    }
    assert quote["missing_inputs"] == []


def test_pricing_engine_does_not_quote_without_user_request():
    profile = {
        "sector": "Fintech",
        "funding_stage": "Series A",
        "team_size": 60,
        "data_sensitivity": "High",
        "has_investors": "Yes",
    }
    bundle = {
        "name": "Startup Shield Pack",
        "mandatory_covers": ["CYBER", "D_AND_O", "PI_TECH_EO"],
        "optional_covers": [],
    }

    quote = price_output_stage(profile, BASE_SCORES, [], bundle)

    assert quote["quote_type"] == "input_required"
    assert quote["status"] == "not_requested"
    assert "gross_premium_lakh" not in quote
    assert {row["key"] for row in quote["missing_required_inputs"]} == {
        "cyber_limit_cr",
        "dno_limit_cr",
        "pi_limit_cr",
    }


def test_explicit_asset_value_drives_property_sum_insured():
    low = infer_underwriting_inputs({
        "sector": "D2C / Consumer Brands",
        "funding_stage": "Seed",
        "team_size": 10,
        "physical_assets": ["Warehouse / fulfilment centre"],
        "asset_value_inr": 10_000_000,
    })
    high = infer_underwriting_inputs({
        "sector": "D2C / Consumer Brands",
        "funding_stage": "Seed",
        "team_size": 10,
        "physical_assets": ["Warehouse / fulfilment centre"],
        "asset_value_inr": 50_000_000,
    })

    assert low["property_sum_insured_cr"] == 1.0
    assert high["property_sum_insured_cr"] == 5.0


def test_analyze_response_asks_for_pricing_inputs_by_default():
    payload = server._v2_score({
        "startup_name": "Pricing Test",
        "sector": "Fintech",
        "funding_stage": "Series A",
        "team_size": 55,
        "operations": "Digital-only",
        "data_sensitivity": "High",
        "data_handled": ["Payments / financial transactions", "Personal identity data (KYC / Aadhaar)"],
        "regulatory": ["RBI / SEBI / IRDAI licensed", "DPDP Act obligations"],
        "physical_assets": ["Office / coworking space"],
        "has_investors": "Yes",
    })

    quote = payload["pricing_engine_quote"]
    assert quote["quote_type"] == "input_required"
    assert quote["status"] == "not_requested"
    assert "gross_premium_inr" not in quote
    assert quote["required_inputs"]


def test_analyze_response_quotes_after_user_supplies_inputs():
    payload = server._v2_score({
        "startup_name": "Pricing Test",
        "sector": "Fintech",
        "funding_stage": "Series A",
        "team_size": 55,
        "operations": "Digital-only",
        "data_sensitivity": "High",
        "data_handled": ["Payments / financial transactions", "Personal identity data (KYC / Aadhaar)"],
        "regulatory": ["RBI / SEBI / IRDAI licensed", "DPDP Act obligations"],
        "physical_assets": ["Office / coworking space"],
        "has_investors": "Yes",
        "quote_requested": True,
        "cyber_limit_cr": 7.5,
        "dno_limit_cr": 5.0,
        "pi_limit_cr": 5.0,
        "crime_limit_cr": 1.0,
        "receivables_on_credit_cr": 2.0,
        "public_liability_limit_cr": 2.0,
    })

    quote = payload["pricing_engine_quote"]
    assert quote["quote_type"] == "indicative_underwriting_quote"
    assert quote["gross_premium_inr"] > 0
    assert quote["covers_priced"]
