import json
from bundle_pricing_agent import price_bundle

profile = {
    "startup_name":       "LogiTrack India",
    "sector":             "Logistics / Mobility",
    "funding_stage":      "Series A",
    "team_size":          80,
    "employee_count":     72,

    "operations":         "Physical + Digital",
    "physical_assets":    ["Warehouse / fulfilment centre", "Vehicles / delivery fleet"],
    "data_handled":       ["Physical inventory / goods", "Personal identity data (KYC / Aadhaar)"],
    "data_sensitivity":   "Medium",

    "annual_revenue_cr":  18.0,
    "b2b_pct":            0.75,

    "has_investors":      "Yes",

    "facility_climate_risk_zone": "High",

    "claims_last_3_years": "Yes",

    "quote_requested":            True,
    "cyber_limit_cr":             3.0,
    "dno_limit_cr":               3.0,
    "pi_limit_cr":                2.0,
    "public_liability_limit_cr":  5.0,
    "property_sum_insured_cr":    12.0,
    "payroll_cr":                 4.2,
    "cargo_annual_turnover_cr":   8.5,   # marine_transit makes it into slot 7 after dedup
}

scores = {
    "Cyber Technical Risk":       58,
    "Data Privacy Risk":          55,
    "Liability Risk":             72,
    "Property Risk":              78,
    "Gig & Labour Risk":          68,
    "ESG & Climate Risk":         74,
    "Geopolitical Risk":          52,
    "Governance & Fraud Risk":    65,
    "Regulatory Compliance Risk": 70,
    "Reputation Risk":            60,
    "Key Person Risk":            45,
    "IP Infringement Risk":       30,
}

bundle = {
    "name": "Logistics & Mobility Shield",
    "mandatory_covers": [
        "CYBER",
        "PUBLIC_LIABILITY",
        "EMPLOYERS_COMP",
        "GROUP_HEALTH",
        "PROPERTY_FIRE",
    ],
    "optional_covers": [
        "D_AND_O",
        "MARINE_CARGO",
        "BHARAT_SOOKSHMA",
        "GROUP_PA",
        "ELECTRONIC_EQUIPMENT",
        "CRIME_FIDELITY",
        "TRADE_CREDIT",
        "BURGLARY",
        "PROPERTY_ALL_RISK",
        "SURETY",
    ],
}

result = price_bundle(profile, scores, bundle)

q = result["bundle_quote"]
a = result["bundle_analysis"]

print()
print("=" * 62)
print(f"  {result['bundle_name']}")
print("=" * 62)
print(f"  Covers priced  : {q['cover_count']}  (cap=8, dedup applied)")
print(f"  Gross premium  : INR {q['gross_premium_inr']:,}  ({q['gross_premium_lakh']}L)")
print(f"  Bundle discount: {a['value_metrics']['bundle_discount_pct']}%  (-{q['bundle_discount_lakh']}L)")
print(f"  SI/prem ratio  : {a['value_metrics']['si_to_annual_premium_ratio']}x")
print()

print("  PER-COVER BREAKDOWN + MARKET BENCHMARKS")
print(f"  {'Cover':<38} {'Engine':>8} {'Market':>8} {'Delta':>7}  claims-load")
print("  " + "-" * 72)
for c in q["covers_priced"]:
    b = c["market_benchmark"]
    market = f"{b['market_mid_premium_lakh']}L" if b.get("market_mid_premium_lakh") is not None else b.get("market_note", "N/A")
    delta  = f"{b['vs_market_delta_pct']:+.0f}%" if b.get("vs_market_delta_pct") is not None else "N/A"
    cl = c["loadings"]["claims"]
    print(f"  {c['cover_name']:<38} {c['premium_lakh']:>7.2f}L {market:>8} {delta:>7}  {cl:.2f}")

print()
print("  COVERAGE DENSITY")
density = a["coverage_density"]["by_category"]
for cat, d in density.items():
    filled = round(d["score"] * 10)
    bar = "#" * filled + "." * (10 - filled)
    gaps = ", ".join(d["missing"][:2]) or "none"
    print(f"  {cat:<12} [{bar}] {int(d['score']*100):>3}%  gaps: {gaps}")
print(f"  Overall breadth: {int(a['coverage_density']['overall_breadth_score']*100)}%")

print()
slim = a["slim_mandatory_tier"]
print(f"  SLIM TIER (mandatory only, {slim.get('cover_count', '?')} covers): {slim.get('gross_premium_lakh', '?')}L")
print(f"  Savings vs full bundle: {slim.get('savings_vs_full_bundle_lakh', '?')}L")

print()
print("  FIX VERIFICATION")
emp = q["underwriting_inputs"]["employee_count"]
print(f"  employee_count used in pricing : {emp}  (profile=72, team_size=80 -> fix #2: {emp == 72})")
claims_loads = set(round(c["loadings"]["claims"], 2) for c in q["covers_priced"])
print(f"  claims loading for 'Yes' string: {claims_loads}  (expected {{1.15}} -> fix #4: {claims_loads == {1.15}})")
print(f"  cover count <= 8               : {q['cover_count'] <= 8}  (fix #1: cap enforced)")
print()
