/* ═══════════════════════════════════════════════════════════════
   SPARC 3.0 — Redesigned frontend
   ═══════════════════════════════════════════════════════════════ */

/* ─── CONSTANTS ──────────────────────────────────────────────── */
const SECTIONS = [
  { id: "identity",  label: "Identity",  icon: "◎" },
  { id: "shape",     label: "Shape",     icon: "⬡" },
  { id: "exposure",  label: "Exposure",  icon: "⚡" },
  { id: "advanced",  label: "Advanced",  icon: "⚙" },
];

const SECTOR_ICONS = {
  "Fintech":                     "💳",
  "Healthtech":                  "🏥",
  "SaaS / Enterprise Software":  "💻",
  "Deeptech / AI / Robotics":    "🤖",
  "Edtech":                      "🎓",
  "D2C / Consumer Brands":       "🛍",
  "Logistics / Mobility":        "🚚",
  "Agritech / Foodtech":         "🌱",
  "Cleantech / Climatetech":     "🌿",
  "Gaming / Media / Content":    "🎮",
  "HRtech":                      "👥",
  "Legaltech":                   "⚖",
  "Proptech":                    "🏠",
  "Spacetech":                   "🚀",
  "Insurtech":                   "🛡",
  "Other":                       "✦",
};

const OPS_ICONS = {
  "Digital-only":         "🌐",
  "Hybrid (online+offline)": "⟳",
  "Offline / Physical":   "🏢",
  "Hardware / IoT":       "📦",
  "Marketplace":          "🔀",
};

const FUNDING_ICONS = {
  "Pre-seed":  "🌱",
  "Seed":      "🌿",
  "Series A":  "🌳",
  "Series B+": "🌲",
};

/* ─── STATE ──────────────────────────────────────────────────── */
const state = {
  meta: null,
  view: "role",
  section: 0,   // 0..3
  profile: {},
  customerProfile: {},
};

/* ─── UTILS ──────────────────────────────────────────────────── */
const $ = (id) => document.getElementById(id);
const esc = (v) => String(v).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#039;");
const labelize = (k) => k.replace(/_/g," ").replace(/\b\w/g,c=>c.toUpperCase());

const PRODUCT_BLURBS = {
  "CYBER":                            "Covers data breach response, ransomware recovery, and regulatory penalties — directly required by CERT-In Directions 2022 and the DPDP Act.",
  "D_AND_O":                          "Protects founders and directors personally if investors, regulators, or employees file suit over decisions made on the company's behalf.",
  "PI_TECH_EO":                       "Pays legal defence and client claims if your software, API, or professional services cause a customer a financial loss or system failure.",
  "CRIME_FIDELITY":                   "Reimburses losses from employee fraud, theft, or forgery — critical once you have a finance team, vendor access, or payment flows.",
  "GROUP_HEALTH":                     "Medical cover for your entire team — a key hiring benefit and an IRDAI-regulated expectation once your headcount crosses 20.",
  "GROUP_PA":                         "Accidental death and disability cover for your workforce, and mandatory for aggregator platforms under the Code on Social Security 2020.",
  "EMPLOYERS_COMP":                   "Statutory payout if an employee is injured or dies at work — required under the Employees' Compensation Act 1923.",
  "PRODUCT_LIABILITY":                "Covers legal defence and settlements if your physical product causes injury or property damage to a customer or third party.",
  "PUBLIC_LIABILITY":                 "Covers third-party bodily injury or property damage claims arising from your premises, events, or day-to-day operations.",
  "BHARAT_SOOKSHMA":                  "Government-backed property bundle protecting your office, equipment, and stock against fire, flood, and theft — up to ₹5 Cr sum insured.",
  "MARINE_CARGO":                     "Covers goods in transit against loss or damage while your products move between warehouses, ports, or last-mile customers.",
  "TRADE_CREDIT":                     "Pays you when a B2B buyer defaults on an invoice — essential for startups extending credit terms to distributors or enterprise clients.",
  "ENGINEERING_CAR_EAR_CPM_MBD_EEI": "Covers physical damage to machinery, equipment under erection, and electronics — essential for hardware, robotics, and manufacturing startups.",
  "SURETY":                           "A performance bond required for government contracts, guaranteeing project completion and protecting against contractor default.",
  "PRAKRITIK_PARAMETRIC":             "Pays out automatically when a climate trigger — flood index, wind speed — is breached. No claims investigation; instant liquidity for climate-exposed ops.",
  "Drone_RPAS":                       "DGCA-mandated insurance for drone operations, covering hull damage and third-party liability arising from aerial activities under Drone Rules 2021.",
  "CGL_I_ELITE":                      "Comprehensive general liability for bodily injury, property damage, and personal injury claims from any third party — the corporate liability cornerstone.",
};
const formatVal = (v) => {
  if (Array.isArray(v)) return v.length ? v.join(", ") : "None";
  if (v === null || v === undefined || v === "") return "None";
  if (typeof v === "boolean") return v ? "Yes" : "No";
  return String(v);
};

/* ─── INIT ───────────────────────────────────────────────────── */
async function init() {
  renderApp();
  const stub = buildStubMeta();
  try {
    const res = await fetch("/api/meta");
    if (!res.ok) throw new Error("no meta");
    const ct = res.headers.get("content-type") || "";
    if (!ct.includes("json")) throw new Error("not json");
    const serverMeta = await res.json();
    // Merge: server values take priority, stub fills any missing fields
    state.meta = { ...stub, ...serverMeta };
    state.profile = structuredClone(state.meta.defaults);
  } catch (e) {
    state.meta = stub;
    state.profile = structuredClone(state.meta.defaults);
  }
  resetCustomerProfile();
  renderRoleSelection();
}

function buildStubMeta() {
  return {
    defaults: {
      startup_name: "",
      sector: "SaaS / Enterprise Software",
      sub_sector: null,
      funding_stage: "Series A",
      team_size: 20,
      operations: "Digital-only",
      data_sensitivity: "Medium",
      ai_in_product: false,
      ai_tier: "None",
      customer_type: [],
      has_investors: "No",
      product_description: "",
      data_handled: [],
      regulatory: [],
      physical_assets: [],
      biggest_fear: "",
      investor_cn_hk_pct: 0,
      cumulative_fundraising_inr_cr: 0,
      holdco_domicile: "India",
      founder_concentration_index: 0.5,
      dpiit_recognition: false,
      rbi_registration: null,
      gig_headcount_pct: 0,
      posh_ic_constituted: false,
      state_footprint: [],
      cert_in_poc_designated: false,
      sdf_probability: 0.5,
      data_localisation_status: "Unknown",
      hardware_software_split: 0,
      b2b_pct: 0.5,
      export_eu_pct: 0,
      export_us_pct: 0,
      export_china_pct: 0,
      chinese_supplier_pct_cogs: 0,
      listed_customer_brsr_dependency: false,
      facility_climate_risk_zone: "Low",
    },
    sectors: [
      "Fintech","Healthtech","SaaS / Enterprise Software","Deeptech / AI / Robotics",
      "Edtech","D2C / Consumer Brands","Logistics / Mobility","Agritech / Foodtech",
      "Cleantech / Climatetech","Gaming / Media / Content","HRtech","Legaltech",
      "Proptech","Spacetech","Insurtech","Other",
    ].map(n=>({name:n})),
    subSectorOptions: {},
    fundingStages: ["Pre-seed","Seed","Series A","Series B+"],
    operations: ["Digital-only","Hybrid (online+offline)","Offline / Physical","Hardware / IoT","Marketplace"],
    dataSensitivity: ["Low","Medium","High","Very High"],
    customerTypeOptions: ["B2B Enterprise","B2B SMB","B2C Consumers","Government / PSU","D2C"],
    dataHandledOptions: [
      "Employee / HR data (payroll, biometrics)",
      "Customer behavioural / usage data",
      "Financial / payment data",
      "Health / medical records",
      "Children's data",
      "Biometric data",
      "None / minimal",
    ],
    regulatoryOptions: [
      "DPDP Act obligations","RBI / NBFC licensing","SEBI regulations","FSSAI licensing",
      "IRDAI regulations","CERT-In compliance","Telecom / DoT licensing","None known",
    ],
    physicalAssetOptions: [
      "Office / coworking space","Owned warehouse / factory","Lab / R&D equipment",
      "Fleet / vehicles","Retail outlets","None",
    ],
    states: ["Maharashtra","Karnataka","Delhi NCR","Tamil Nadu","Telangana","Gujarat","Rajasthan","Others"],
    holdcoDomiciles: ["India","Singapore","USA (Delaware)","Cayman Islands","Mauritius","UK","UAE","Netherlands"],
    rbiRegistrations: ["None","PA (Payment Aggregator)","PG (Payment Gateway)","NBFC","NBFC-AA","Prepaid Instruments"],
    aiTiers: ["None","Applied","Autonomous","Frontier"],
    climateZones: ["Low","Medium","High","Very High"],
  };
}

/* ─── TOP BAR ────────────────────────────────────────────────── */
function renderApp() {
  document.getElementById("app").innerHTML = `
    <div class="app-wrap">
      <header class="topbar">
        <div class="topbar-brand">
          <div class="brand-mark">S</div>
          <span class="topbar-name">SPARC</span>
        </div>
        <div class="topbar-sep"></div>
        <span class="topbar-sub">ICICI Lombard · Startup Risk Intelligence</span>
      </header>
      <div id="main-content"></div>
    </div>`;
}

/* ─── FORM RENDER ────────────────────────────────────────────── */
function resetCustomerProfile() {
  state.customerProfile = {
    business_name: "",
    persona: "SaaS founder",
    industry: state.meta?.defaults?.sector || "SaaS / Enterprise Software",
    revenue_range: "INR 1-5 Cr",
    team_range: "11-50",
    funding_status: "Seed",
    main_concern: "Customer contracts",
    handles: ["customer_data", "contracts"],
  };
}

function renderRoleSelection() {
  state.view = "role";
  $("main-content").innerHTML = `
    <main class="role-shell">
      <section class="role-panel">
        <div class="role-copy">
          <div class="intake-eyebrow">Choose experience</div>
          <h1>Start with the input view that fits your role</h1>
          <p>Select the customer route for a short, persona-led recommendation. Select the underwriter route for the full SPARC intake and risk report.</p>
        </div>
        <div class="role-options">
          <button class="role-card role-card-primary" type="button" id="customer-role-btn">
            <span class="role-card-kicker">Customer End Input</span>
            <strong>Quick recommendation</strong>
            <span>Short profile questions, simple language, and an RM-ready recommendation screen.</span>
          </button>
          <button class="role-card" type="button" id="underwriter-role-btn">
            <span class="role-card-kicker">Underwriter End Input</span>
            <strong>Full underwriting analysis</strong>
            <span>Use the existing detailed intake, scoring model, pricing views, and report output.</span>
          </button>
        </div>
      </section>
    </main>`;

  $("customer-role-btn").onclick = () => {
    if (!state.customerProfile?.persona) resetCustomerProfile();
    renderCustomerInput();
  };
  $("underwriter-role-btn").onclick = () => renderForm();
}

function renderCustomerInput() {
  state.view = "customer";
  const meta = state.meta;
  const p = state.customerProfile;
  const sectors = (meta.sectors || []).map(s => s.name);
  const handleOptions = [
    ["customer_data", "Customer data"],
    ["payments", "Online payments"],
    ["contracts", "B2B contracts"],
    ["employees", "Employees"],
    ["physical_ops", "Office, stock, or equipment"],
  ];

  $("main-content").innerHTML = `
    <main class="customer-shell">
      <section class="customer-form-panel">
        <button class="link-button" type="button" id="customer-back-role">Back to role selection</button>
        <div class="customer-head">
          <div class="intake-eyebrow">Customer input</div>
          <h1>Get a startup insurance recommendation in under two minutes</h1>
          <p>Answer a few business-friendly questions. We will translate them into the SPARC risk model and keep the output concise.</p>
        </div>

        <div class="customer-grid">
          <div class="field-group">
            <label>Business name</label>
            <input class="f-input" type="text" value="${esc(p.business_name)}" placeholder="e.g. BrightPay" data-customer-key="business_name" />
          </div>
          <div class="field-group">
            <label>Which sounds closest to you?</label>
            <select class="f-select" data-customer-key="persona">
              ${["SaaS founder","Fintech operator","D2C brand","Healthtech builder","Marketplace platform","Hardware or IoT startup","AI product company"].map(v => `<option ${p.persona===v?"selected":""}>${esc(v)}</option>`).join("")}
            </select>
          </div>
          <div class="field-group">
            <label>Industry</label>
            <select class="f-select" data-customer-key="industry">
              ${sectors.map(v => `<option ${p.industry===v?"selected":""}>${esc(v)}</option>`).join("")}
            </select>
          </div>
          <div class="field-group">
            <label>Annual revenue range</label>
            <select class="f-select" data-customer-key="revenue_range">
              ${["Pre-revenue","Below INR 1 Cr","INR 1-5 Cr","INR 5-25 Cr","INR 25 Cr+"].map(v => `<option ${p.revenue_range===v?"selected":""}>${esc(v)}</option>`).join("")}
            </select>
          </div>
          <div class="field-group">
            <label>Team size</label>
            <select class="f-select" data-customer-key="team_range">
              ${["1-10","11-50","51-200","200+"].map(v => `<option ${p.team_range===v?"selected":""}>${esc(v)}</option>`).join("")}
            </select>
          </div>
          <div class="field-group">
            <label>Funding status</label>
            <select class="f-select" data-customer-key="funding_status">
              ${(meta.fundingStages || ["Pre-seed","Seed","Series A","Series B+"]).map(v => `<option ${p.funding_status===v?"selected":""}>${esc(v)}</option>`).join("")}
            </select>
          </div>
        </div>

        <div class="field-group">
          <label>Main concern right now</label>
          <div class="customer-choice-row" id="customer-concerns">
            ${["Customer contracts","Data breach","Investor or board risk","Employee benefits","Product or service claims","Property or equipment loss"].map(v => `
              <button class="customer-chip ${p.main_concern===v?"active":""}" type="button" data-concern="${esc(v)}">${esc(v)}</button>`).join("")}
          </div>
        </div>

        <div class="field-group">
          <label>What applies to your business?</label>
          <div class="customer-check-grid">
            ${handleOptions.map(([key, label]) => `
              <label class="customer-check">
                <input type="checkbox" value="${key}" ${(p.handles || []).includes(key) ? "checked" : ""} />
                <span>${esc(label)}</span>
              </label>`).join("")}
          </div>
        </div>

        <div class="customer-actions">
          <button class="btn btn-ghost" type="button" id="customer-reset-btn">Reset</button>
          <button class="btn btn-primary btn-lg" type="button" id="customer-submit-btn">Show my recommendation</button>
        </div>
      </section>

      <aside class="customer-side">
        <div class="customer-side-card">
          <div class="sidebar-card-label">What you will see</div>
          <div class="info-list">
            <div class="info-row"><div class="info-dot"></div><span>Best-fit bundle for your stage</span></div>
            <div class="info-row"><div class="info-dot"></div><span>Top 3 products to discuss first</span></div>
            <div class="info-row"><div class="info-dot"></div><span>Baseline cover to start with</span></div>
            <div class="info-row"><div class="info-dot"></div><span>Plain-language RM nudge</span></div>
          </div>
        </div>
      </aside>
    </main>`;

  bindCustomerInput();
}

function bindCustomerInput() {
  $("customer-back-role").onclick = () => renderRoleSelection();
  $("customer-reset-btn").onclick = () => {
    resetCustomerProfile();
    renderCustomerInput();
  };
  document.querySelectorAll("[data-customer-key]").forEach(el => {
    const update = () => { state.customerProfile[el.dataset.customerKey] = el.value; };
    el.addEventListener("input", update);
    el.addEventListener("change", update);
  });
  document.querySelectorAll("[data-concern]").forEach(btn => {
    btn.addEventListener("click", () => {
      state.customerProfile.main_concern = btn.dataset.concern;
      document.querySelectorAll("[data-concern]").forEach(x => x.classList.toggle("active", x === btn));
    });
  });
  document.querySelectorAll(".customer-check input").forEach(el => {
    el.addEventListener("change", () => {
      state.customerProfile.handles = [...document.querySelectorAll(".customer-check input:checked")].map(x => x.value);
    });
  });
  $("customer-submit-btn").onclick = () => runCustomerAnalysis();
}

function teamRangeToNumber(range) {
  return { "1-10": 8, "11-50": 25, "51-200": 90, "200+": 250 }[range] || 20;
}

function mapCustomerToUnderwritingProfile(customer) {
  const handles = new Set(customer.handles || []);
  const profile = structuredClone(state.meta.defaults);
  profile.startup_name = customer.business_name?.trim() || "Your startup";
  profile.sector = customer.industry || profile.sector;
  profile.funding_stage = customer.funding_status || profile.funding_stage;
  profile.team_size = teamRangeToNumber(customer.team_range);
  profile.product_description = `${customer.persona}. Main concern: ${customer.main_concern}. Revenue range: ${customer.revenue_range}.`;
  profile.has_investors = ["Seed", "Series A", "Series B+"].includes(profile.funding_stage) ? "Yes" : "No";
  profile.customer_type = handles.has("contracts") ? ["B2B Enterprise"] : ["B2C Consumers"];
  profile.operations = handles.has("physical_ops") ? "Hybrid" : "Digital-only";
  profile.data_sensitivity = handles.has("payments") || handles.has("customer_data") ? "High" : "Medium";
  profile.data_handled = [];
  profile.regulatory = [];
  profile.physical_assets = [];

  if (handles.has("customer_data")) {
    profile.data_handled.push("Customer behavioural / usage data");
    profile.regulatory.push("DPDP Act obligations");
  }
  if (handles.has("payments")) {
    profile.data_handled.push("Payments / financial transactions");
    profile.regulatory.push("IT Act / CERT-In obligations");
  }
  if (handles.has("employees")) {
    profile.data_handled.push("Employee / HR data (payroll, biometrics)");
  }
  if (handles.has("physical_ops")) {
    profile.physical_assets.push("Office / coworking space");
  }
  if (customer.main_concern === "Data breach" && !profile.regulatory.includes("IT Act / CERT-In obligations")) {
    profile.regulatory.push("IT Act / CERT-In obligations");
  }
  if (customer.main_concern === "Employee benefits" && !handles.has("employees")) {
    profile.data_handled.push("Employee / HR data (payroll, biometrics)");
  }

  profile.biggest_fear = customer.main_concern || "";
  profile.b2b_pct = handles.has("contracts") ? 0.75 : 0.25;
  return profile;
}

async function runCustomerAnalysis() {
  renderCustomerLoading();
  const mappedProfile = mapCustomerToUnderwritingProfile(state.customerProfile);
  try {
    const res = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(mappedProfile),
    });
    const result = await res.json();
    if (!res.ok || result.error) throw new Error(result.error || "Analysis failed");
    renderCustomerResults(result);
  } catch (err) {
    $("main-content").innerHTML = `
      <div style="padding:100px 40px;max-width:640px;margin:0 auto;">
        <div class="error-box">${esc(err.message)}</div>
        <button class="btn btn-ghost" style="margin-top:16px;" onclick="renderCustomerInput()">Back to customer inputs</button>
      </div>`;
  }
}

function renderCustomerLoading() {
  $("main-content").innerHTML = `
    <div class="loading-screen customer-loading">
      <div class="loading-ring"></div>
      <div class="loading-text">Building your recommendation</div>
      <div class="loading-sub">Translating your profile into a simple bundle and product shortlist.</div>
    </div>`;
}

function getBaselineProduct(result) {
  const recs = result.recommendations || [];
  return recs.find(p => p.mandatory) || recs.find(p => p.priority === "Critical") || recs[0] || null;
}

function customerProductReason(product) {
  if (!product) return "";
  return product.nudge || PRODUCT_BLURBS[product.key] || "Relevant for the risks most likely to affect your business at this stage.";
}

function customerExplanation(result) {
  const p = result.profile || {};
  const topRisk = (result.top_risks || [])[0]?.name?.replace(" Risk", "").toLowerCase() || "business continuity";
  const bundle = result.bundle_match?.name || "the recommended bundle";
  return `For a ${p.funding_stage || "growing"} ${p.sector || "startup"} with about ${p.team_size || "your current"} people, ${bundle} is the clearest starting point. It prioritises ${topRisk} and keeps the first discussion focused on covers that protect contracts, data, people, and day-to-day operations.`;
}

function customerNudge(result) {
  const p = result.profile || {};
  if ((p.customer_type || []).includes("B2B Enterprise")) {
    return "This is commonly selected by businesses at your stage before signing larger customer contracts.";
  }
  if ((p.data_handled || []).length) {
    return "Founders with similar data exposure often review this cover early to avoid expensive surprises after a breach or customer complaint.";
  }
  return "Teams at this stage often start with baseline protection now, then expand the cover as revenue and operations scale.";
}

function renderCustomerResults(result) {
  const p = result.profile || {};
  const bundle = result.bundle_match || {};
  const topProducts = (result.recommendations || []).slice(0, 3);
  const baseline = getBaselineProduct(result);

  $("main-content").innerHTML = `
    <main class="customer-results">
      <section class="customer-results-hero">
        <button class="link-button light" type="button" onclick="renderCustomerInput()">Edit customer inputs</button>
        <div class="customer-results-top">
          <div>
            <div class="customer-results-kicker">Your startup shield recommendation</div>
            <h1>${esc(bundle.name || "Recommended startup protection")}</h1>
            <p>${esc(customerExplanation(result))}</p>
          </div>
          <div class="customer-fit">
            <strong>${bundle.fit_pct || Math.round(100 - Math.min(70, result.overall || 0) / 2)}%</strong>
            <span>profile fit</span>
          </div>
        </div>
      </section>

      <section class="customer-result-grid">
        <article class="customer-result-card customer-bundle-card">
          <div class="card-label">Recommended bundle</div>
          <h2>${esc(bundle.name || "Bundle recommendation")}</h2>
          <p>${esc(bundle.description || "A practical set of covers matched to your current business profile.")}</p>
          ${result.bundle_only_pricing_quote?.gross_premium_lakh ? `<div class="customer-price">Indicative bundle premium: INR ${esc(result.bundle_only_pricing_quote.gross_premium_lakh)}L incl. GST</div>` : ""}
        </article>

        <article class="customer-result-card">
          <div class="card-label">Baseline product</div>
          ${baseline ? `
            <h2>${esc(baseline.name || labelize(baseline.key))}</h2>
            <p>${esc(customerProductReason(baseline))}</p>
          ` : `<p>No baseline product was returned for this profile.</p>`}
        </article>
      </section>

      <section class="customer-products-section">
        <div class="result-section-head">
          <div class="result-section-bar"></div>
          <div class="result-section-title">Top 3 products to discuss first</div>
        </div>
        <div class="customer-product-grid">
          ${topProducts.map((product, i) => `
            <article class="customer-product-card">
              <div class="customer-product-rank">#${i + 1}</div>
              <h3>${esc(product.name || labelize(product.key))}</h3>
              <p>${esc(customerProductReason(product))}</p>
              <div class="customer-product-tags">
                <span>${esc(product.priority || "Recommended")}</span>
                ${product.mandatory ? "<span>Baseline</span>" : ""}
              </div>
            </article>`).join("") || `<div class="r-card">${emptyState("i", "No products returned", "Try changing the customer profile inputs.")}</div>`}
        </div>
      </section>

      <section class="customer-rm-banner">
        <div>
          <div class="customer-rm-label">Next best action</div>
          <h2>Talk with your RM</h2>
          <p>${esc(customerNudge(result))}</p>
        </div>
        <button class="btn btn-primary btn-lg" type="button">Talk with RM</button>
      </section>

      <div class="customer-result-actions">
        <button class="btn btn-ghost" type="button" onclick="renderRoleSelection()">Back to role selection</button>
        <button class="btn btn-ghost" type="button" onclick="renderForm()">Open underwriter view</button>
      </div>
    </main>`;

  state.profile = structuredClone(p);
  window.__customerResult = result;
}

function renderForm() {
  state.view = "underwriter";
  state.section = 0;
  const mc = $("main-content");
  mc.innerHTML = `
    <div class="intake-shell">
      <main class="intake-main">
        <div class="intake-hero">
          <div class="intake-eyebrow">Risk Analysis</div>
          <h1>Tell us about<br/>your startup</h1>
          <p>We'll map your risk exposure across 13 categories and recommend the exact insurance covers you need.</p>
        </div>

        <div class="progress-row" id="progress-row"></div>

        <div id="form-sections">
          ${renderSectionIdentity()}
          ${renderSectionShape()}
          ${renderSectionExposure()}
          ${renderSectionAdvanced()}
        </div>

        <div class="intake-nav">
          <button class="btn btn-ghost" id="back-btn" type="button" disabled>← Back</button>
          <div class="nav-spacer"></div>
          <button class="btn btn-primary btn-lg" id="next-btn" type="button">Continue →</button>
        </div>
      </main>

      <aside class="intake-sidebar">
        <div class="sidebar-card">
          <div class="sidebar-card-label">Your profile so far</div>
          <div id="profile-summary"></div>
        </div>
        <div class="sidebar-card">
          <div class="sidebar-card-label">We'll calculate</div>
          <div class="info-list">
            ${[
              "Risk score across 13 categories",
              "Overall exposure rating out of 100",
              "Personalised ICICI Lombard products",
              "Premium cost estimates",
              "Non-insurance mitigation actions",
            ].map(t=>`<div class="info-row"><div class="info-dot"></div><span>${t}</span></div>`).join("")}
          </div>
        </div>
      </aside>
    </div>`;

  bindForm();
  updateProgress();
  showSection(0);
  updateProfileSummary();
}

/* ── Section 0: Identity ──────────────────────────────────── */
function renderSectionIdentity() {
  const meta = state.meta;
  const sectors = meta.sectors.map(s=>s.name);
  const p = state.profile;

  const sectorCards = sectors.map(s => `
    <button class="choice-card ${p.sector===s?"active":""}" type="button" data-key="sector" data-value="${esc(s)}" onclick="chooseCard(this,'sector',false)">
      <div class="cc-icon">${SECTOR_ICONS[s]||"✦"}</div>
      <div class="cc-label">${esc(s)}</div>
    </button>`).join("");

  const stageCards = meta.fundingStages.map(s => `
    <button class="choice-card ${p.funding_stage===s?"active":""}" type="button" data-key="funding_stage" data-value="${esc(s)}" onclick="chooseCard(this,'funding_stage',false)">
      <div class="cc-icon">${FUNDING_ICONS[s]||"●"}</div>
      <div class="cc-label">${esc(s)}</div>
    </button>`).join("");

  return `
    <div class="form-section" id="section-identity">
      <div class="section-label">01 — Identity</div>

      <div class="field-group">
        <label>Startup name</label>
        <input class="f-input" id="f-name" type="text" placeholder="e.g. Acme Labs" value="${esc(p.startup_name||"")}" oninput="setVal('startup_name',this.value)" />
      </div>

      <div class="field-group">
        <label>Sector</label>
        <div class="card-grid">${sectorCards}</div>
      </div>

      <div class="field-group">
        <label>Funding stage</label>
        <div class="card-grid">${stageCards}</div>
      </div>

      <div class="field-row">
        <div class="field-group">
          <label>Team size (full-time)</label>
          <div class="range-wrap">
            <input type="range" min="1" max="500" step="1"
              value="${p.team_size||20}"
              oninput="setVal('team_size',Number(this.value)); this.nextElementSibling.textContent=this.value" />
            <div class="range-bubble">${p.team_size||20}</div>
          </div>
        </div>
        <div class="field-group">
          <label>Institutional investors?</label>
          <div class="pill-grid">
            ${["Yes","No"].map(v=>`<button class="pill ${p.has_investors===v?"active":""}" type="button" data-key="has_investors" data-value="${esc(v)}" onclick="chooseVal('has_investors','${v}',false)">${v}</button>`).join("")}
          </div>
        </div>
      </div>
    </div>`;
}

/* ── Section 1: Shape ─────────────────────────────────────── */
function renderSectionShape() {
  const meta = state.meta;
  const p = state.profile;

  const opsCards = meta.operations.map(s => `
    <button class="choice-card ${p.operations===s?"active":""}" type="button" data-key="operations" data-value="${esc(s)}" onclick="chooseCard(this,'operations',false)">
      <div class="cc-icon">${OPS_ICONS[s]||"●"}</div>
      <div class="cc-label">${esc(s)}</div>
    </button>`).join("");

  const sensitivityPills = meta.dataSensitivity.map(v=>`
    <button class="pill ${p.data_sensitivity===v?"active":""}" type="button" data-key="data_sensitivity" data-value="${esc(v)}" onclick="chooseVal('data_sensitivity','${v}',false)">${v}</button>`).join("");

  const custPills = meta.customerTypeOptions.map(v=>`
    <button class="pill ${(p.customer_type||[]).includes(v)?"active":""}" type="button" data-key="customer_type" data-value="${esc(v)}" onclick="chooseVal('customer_type','${esc(v)}',true)">${esc(v)}</button>`).join("");

  return `
    <div class="form-section" id="section-shape">
      <div class="section-label">02 — Shape</div>

      <div class="field-group">
        <label>Operating model</label>
        <div class="card-grid">${opsCards}</div>
      </div>

      <div class="field-row">
        <div class="field-group">
          <label>Data sensitivity</label>
          <div class="pill-grid">${sensitivityPills}</div>
        </div>
        <div class="field-group">
          <label>AI / ML in core product?</label>
          <div class="pill-grid">
            ${["No","Yes"].map(v=>`<button class="pill ${(p.ai_in_product?(v==="Yes"):(v==="No"))?"active":""}" type="button" data-key="ai_toggle" data-value="${v}" onclick="setAI('${v}')">${v}</button>`).join("")}
          </div>
        </div>
      </div>

      <div class="field-group">
        <label>Customers <span style="font-weight:400;color:var(--ink-faint)">(select all that apply)</span></label>
        <div class="pill-grid">${custPills}</div>
      </div>

      <div class="field-group">
        <label>What does your product do? <span style="font-weight:400;color:var(--ink-faint)">(optional)</span></label>
        <textarea class="f-textarea" placeholder="e.g. We build a UPI payment gateway for SMBs…" oninput="setVal('product_description',this.value)">${esc(p.product_description||"")}</textarea>
      </div>
    </div>`;
}

/* ── Section 2: Exposure ──────────────────────────────────── */
function mkPillsGrouped(groups, profileKey) {
  return groups.map(({heading, items, rule}) => [
    rule ? `<span class="pill-divider-rule"></span>` : "",
    heading ? `<span class="pill-divider">${esc(heading)}</span>` : "",
    ...items.map(v =>
      `<button class="pill ${(state.profile[profileKey]||[]).includes(v)?"active":""}" type="button" data-key="${profileKey}" data-value="${esc(v)}" onclick="chooseVal('${profileKey}','${esc(v)}',true)">${esc(v)}</button>`
    )
  ].join("")).join("");
}

function renderSectionExposure() {
  const dataGroups = [
    { heading: "Personal & financial",
      items: ["Payments / financial transactions", "Personal identity data (KYC / Aadhaar)", "Health / medical records", "Minors' / children's data", "Sensitive personal data (DPDP Act)"] },
    { heading: "Business & IP",
      items: ["Employee / HR data (payroll, biometrics)", "Intellectual property / source code", "Customer behavioural / usage data"] },
    { heading: "Operational",
      items: ["Location / GPS tracking data", "Physical inventory / goods"] },
    { rule: true, heading: "",
      items: ["None of the above"] },
  ];

  const regGroups = [
    { heading: "Financial & data",
      items: ["RBI / SEBI / IRDAI licensed", "DPDP Act obligations", "IT Act / CERT-In obligations"] },
    { heading: "Health & life sciences",
      items: ["FSSAI / food safety", "CDSCO / medical devices", "NMC / telemedicine regulations"] },
    { heading: "Operations & transport",
      items: ["DGCA / drone operations", "MV Act / transport regulations", "Labour Codes / gig worker regulations"] },
    { heading: "Product & environment",
      items: ["BIS / QCO product certification", "EPR / environmental compliance", "SEBI BRSR / ESG reporting", "Competition Act / CCI"] },
    { rule: true, heading: "",
      items: ["None / minimal"] },
  ];

  const assetGroups = [
    { heading: "Premises & retail",
      items: ["Office / coworking space", "Warehouse / fulfilment centre", "Retail stores / kiosks"] },
    { heading: "Production & lab",
      items: ["Manufacturing plant / factory", "Lab / R&D equipment", "Kitchen / food processing", "Cold chain / refrigeration"] },
    { heading: "Specialist equipment",
      items: ["Medical devices / diagnostic equipment", "Drones / UAV equipment", "Solar / clean energy infrastructure"] },
    { heading: "Transport & tech",
      items: ["Vehicles / delivery fleet", "Data centre / server room"] },
    { rule: true, heading: "",
      items: ["None - fully cloud"] },
  ];

  const p = state.profile;
  return `
    <div class="form-section" id="section-exposure">
      <div class="section-label">03 — Exposure</div>

      <div class="field-group">
        <label>Sensitive data you handle <span style="font-weight:400;color:var(--ink-faint)">(select all)</span></label>
        <div class="pill-grid">${mkPillsGrouped(dataGroups, "data_handled")}</div>
      </div>

      <div class="field-group">
        <label>Regulatory exposure <span style="font-weight:400;color:var(--ink-faint)">(select all)</span></label>
        <div class="pill-grid">${mkPillsGrouped(regGroups, "regulatory")}</div>
      </div>

      <div class="field-group">
        <label>Physical assets <span style="font-weight:400;color:var(--ink-faint)">(select all)</span></label>
        <div class="pill-grid">${mkPillsGrouped(assetGroups, "physical_assets")}</div>
      </div>

      <div class="field-group">
        <label>Biggest risk concern <span style="font-weight:400;color:var(--ink-faint)">(optional)</span></label>
        <textarea class="f-textarea" placeholder="e.g. A data breach that damages customer trust…" oninput="setVal('biggest_fear',this.value)">${esc(p.biggest_fear||"")}</textarea>
      </div>
    </div>`;
}

/* ── Section 3: Advanced ──────────────────────────────────── */
function renderSectionAdvanced() {
  const meta = state.meta;
  const p = state.profile;

  const mkSlider = (key, label, min, max, step, decimals=2) => {
    const val = Number(p[key] ?? 0);
    return `
      <div class="adv-slider-row">
        <span class="adv-slider-label">${label}</span>
        <input type="range" class="adv-range" min="${min}" max="${max}" step="${step}" value="${val}"
          oninput="setVal('${key}',Number(this.value)); this.nextElementSibling.textContent=Number(this.value).toFixed(${decimals})" />
        <span class="adv-slider-val">${val.toFixed(decimals)}</span>
      </div>`;
  };

  const mkSelect = (key, label, opts, nullLabel="") => {
    const cur = p[key];
    return `
      <div class="adv-select-item">
        <label class="adv-select-label">${label}</label>
        <select class="f-select" style="height:38px;font-size:13px;" onchange="setVal('${key}',this.value||null)">
          ${nullLabel?`<option value="">${esc(nullLabel)}</option>`:""}
          ${opts.map(o=>`<option value="${esc(o)}" ${cur===o?"selected":""}>${esc(o)}</option>`).join("")}
        </select>
      </div>`;
  };

  const mkCheck = (key, label) => `
    <label class="adv-check">
      <input type="checkbox" id="chk-${key}" ${p[key]?"checked":""} onchange="setVal('${key}',this.checked)" />
      <span>${label}</span>
    </label>`;

  const statePills = meta.states.map(s=>`
    <button class="pill ${(p.state_footprint||[]).includes(s)?"active":""}" type="button" data-key="state_footprint" data-value="${esc(s)}" onclick="chooseVal('state_footprint','${esc(s)}',true)">${esc(s)}</button>`).join("");

  return `
    <div class="form-section" id="section-advanced">
      <div class="section-label">04 — Advanced <span style="font-weight:500;color:var(--ink-faint);text-transform:none;letter-spacing:0;">(optional)</span></div>

      <div class="adv-group">
        <div class="adv-group-title">Governance &amp; capital</div>
        <div class="adv-sliders">
          ${mkSlider("investor_cn_hk_pct","China / HK investor BO",0,1,.01)}
          ${mkSlider("cumulative_fundraising_inr_cr","Total fundraising (INR Cr)",0,10000,10,0)}
          ${mkSlider("founder_concentration_index","Founder concentration index",0,1,.01)}
        </div>
        <div class="adv-selects">
          ${mkSelect("holdco_domicile","Holdco domicile",meta.holdcoDomiciles)}
          ${mkSelect("rbi_registration","RBI registration",meta.rbiRegistrations,"None")}
        </div>
        <div class="adv-checks">${mkCheck("dpiit_recognition","DPIIT recognised startup")}</div>
      </div>

      <div class="adv-group">
        <div class="adv-group-title">Workforce &amp; gig risk</div>
        <div class="adv-sliders">
          ${mkSlider("gig_headcount_pct","Gig / contractor workforce %",0,1,.01)}
        </div>
        <div class="adv-checks">
          ${mkCheck("posh_ic_constituted","POSH IC constituted")}
          ${mkCheck("cert_in_poc_designated","CERT-In POC designated")}
        </div>
        <div class="adv-state-wrap">
          <div class="adv-state-label">State footprint <span style="font-weight:400;color:var(--ink-faint)">(select all that apply)</span></div>
          <div class="pill-grid">${statePills}</div>
        </div>
      </div>

      <div class="adv-group">
        <div class="adv-group-title">Data &amp; AI</div>
        <div class="adv-sliders">
          ${mkSlider("sdf_probability","SDF likelihood",0,1,.01)}
          ${mkSlider("hardware_software_split","Hardware revenue share",0,1,.01)}
        </div>
        <div class="adv-selects">
          ${mkSelect("data_localisation_status","Data localisation",["Unknown","Full_onshore","Hybrid","Offshore"])}
          ${mkSelect("ai_tier","AI tier",meta.aiTiers)}
        </div>
      </div>

      <div class="adv-group">
        <div class="adv-group-title">Market &amp; supply chain</div>
        <div class="adv-sliders">
          ${mkSlider("b2b_pct","B2B revenue",0,1,.01)}
          ${mkSlider("export_eu_pct","EU revenue",0,1,.01)}
          ${mkSlider("export_us_pct","US revenue",0,1,.01)}
          ${mkSlider("export_china_pct","China revenue",0,1,.01)}
          ${mkSlider("chinese_supplier_pct_cogs","Chinese supplier COGS",0,1,.01)}
        </div>
        <div class="adv-checks">${mkCheck("listed_customer_brsr_dependency","Listed customers require BRSR")}</div>
      </div>

      <div class="adv-group">
        <div class="adv-group-title">Physical &amp; environmental</div>
        <div class="adv-selects" style="max-width:360px;">
          ${mkSelect("facility_climate_risk_zone","Facility climate risk zone",meta.climateZones)}
        </div>
      </div>
    </div>`;
}

/* ─── FORM BIND / INTERACTIONS ──────────────────────────────── */
function bindForm() {
  $("back-btn").onclick = () => {
    if (state.section > 0) { state.section--; showSection(state.section); }
  };
  $("next-btn").onclick = () => {
    if (state.section < SECTIONS.length - 1) {
      state.section++;
      showSection(state.section);
    } else {
      runAnalysis();
    }
  };
}

function showSection(idx) {
  document.querySelectorAll(".form-section").forEach(el => el.classList.remove("visible"));
  const ids = ["section-identity","section-shape","section-exposure","section-advanced"];
  const el = $(ids[idx]);
  if (el) el.classList.add("visible");

  $("back-btn").disabled = idx === 0;
  $("next-btn").textContent = idx === SECTIONS.length - 1 ? "Analyse my startup →" : "Continue →";
  updateProgress();
  updateProfileSummary();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function updateProgress() {
  const row = $("progress-row");
  if (!row) return;
  row.innerHTML = SECTIONS.map((s, i) => {
    const cls = i < state.section ? "done" : i === state.section ? "active" : "";
    const line = i < SECTIONS.length - 1 ? `<div class="progress-line"></div>` : "";
    return `<div class="progress-step ${cls}"><div class="progress-dot"></div>${s.label}</div>${line}`;
  }).join("");
}

// Global helpers called from onclick attributes
window.setVal = (key, val) => {
  state.profile[key] = val;
  updateProfileSummary();
};

window.setAI = (v) => {
  state.profile.ai_in_product = v === "Yes";
  state.profile.ai_tier = v === "Yes" ? "Applied" : "None";
  document.querySelectorAll(`.pill[data-key="ai_toggle"]`).forEach(btn => {
    btn.classList.toggle("active", btn.dataset.value === v);
  });
  updateProfileSummary();
};

window.chooseCard = (el, key, multi) => {
  const val = el.dataset.value;
  if (!multi) {
    document.querySelectorAll(`.choice-card[data-key="${key}"]`).forEach(b => b.classList.remove("active"));
    el.classList.add("active");
    state.profile[key] = val;
    if (key === "sector") state.profile.sub_sector = null;
  } else {
    el.classList.toggle("active");
    const cur = new Set(state.profile[key] || []);
    cur.has(val) ? cur.delete(val) : cur.add(val);
    state.profile[key] = [...cur];
  }
  updateProfileSummary();
};

window.chooseVal = (key, val, multi) => {
  if (!multi) {
    state.profile[key] = val;
    document.querySelectorAll(`.pill[data-key="${key}"]`).forEach(b => {
      b.classList.toggle("active", b.dataset.value === val);
    });
  } else {
    const cur = new Set(state.profile[key] || []);
    cur.has(val) ? cur.delete(val) : cur.add(val);
    state.profile[key] = [...cur];
    document.querySelectorAll(`.pill[data-key="${key}"]`).forEach(b => {
      b.classList.toggle("active", cur.has(b.dataset.value));
    });
  }
  updateProfileSummary();
};

function updateProfileSummary() {
  const el = $("profile-summary");
  if (!el) return;
  const p = state.profile;
  const items = [
    ["Name",       p.startup_name || "—"],
    ["Sector",     p.sector       || "—"],
    ["Stage",      p.funding_stage|| "—"],
    ["Team",       p.team_size ? `${p.team_size} FTEs` : "—"],
    ["Model",      p.operations   || "—"],
    ["Customers",  (p.customer_type||[]).join(", ") || "—"],
  ];
  el.innerHTML = items.map(([k,v]) => `
    <div class="profile-item">
      <span class="profile-item-key">${k}</span>
      <span class="profile-item-val">${esc(String(v))}</span>
    </div>`).join("");
}

/* ─── ANALYSIS ───────────────────────────────────────────────── */
async function runAnalysis() {
  renderLoading();
  try {
    const res = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(state.profile),
    });
    const ct = res.headers.get("content-type") || "";
    if (!ct.includes("json")) throw new Error("no-backend");
    const result = await res.json();
    if (!res.ok || result.error) throw new Error(result.error || "Analysis failed");
    renderResults(result);
  } catch (err) {
    // Fall back to demo response when no backend is connected
    try {
      const demoRes = await fetch("./demo-response.json");
      const demo = await demoRes.json();
      // Patch the demo profile with what the user actually entered
      if (state.profile.startup_name) demo.profile.startup_name = state.profile.startup_name;
      if (state.profile.sector) demo.profile.sector = state.profile.sector;
      if (state.profile.funding_stage) demo.profile.funding_stage = state.profile.funding_stage;
      if (state.profile.team_size) demo.profile.team_size = state.profile.team_size;
      if (state.profile.operations) demo.profile.operations = state.profile.operations;
      renderResults(demo);
    } catch {
      $("main-content").innerHTML = `
        <div style="padding:80px 40px;padding-top:100px;max-width:600px;margin:0 auto;">
          <div class="error-box">${esc(err.message)}</div>
          <button class="btn btn-ghost" style="margin-top:16px;" onclick="renderForm()">← Edit inputs</button>
        </div>`;
    }
  }
}

function renderLoading() {
  $("main-content").innerHTML = `
    <div class="loading-screen">
      <div class="loading-ring"></div>
      <div class="loading-text">Analysing your startup</div>
      <div class="loading-sub">Running 13 risk models against your profile</div>
      <div class="loading-steps">
        <div class="loading-step"><div class="loading-step-dot"></div>Scoring digital &amp; data exposure…</div>
        <div class="loading-step"><div class="loading-step-dot"></div>Mapping regulatory triggers…</div>
        <div class="loading-step"><div class="loading-step-dot"></div>Matching ICICI Lombard products…</div>
        <div class="loading-step"><div class="loading-step-dot"></div>Estimating premium ranges…</div>
      </div>
    </div>`;
}

/* ─── RESULTS RENDER ─────────────────────────────────────────── */
function renderResults(result) {
  state.profile = structuredClone(result.profile || state.profile);
  const p = result.profile;

  const gaugeClass = result.overall >= 70 ? "gauge-critical" : result.overall >= 45 ? "gauge-moderate" : "gauge-low";
  const gaugeColor = result.overall >= 70 ? "var(--red)" : result.overall >= 45 ? "var(--amber)" : "var(--green)";

  $("main-content").innerHTML = `
    <div class="results-wrap">

      <!-- Hero -->
      <div class="results-hero">
        <div>
          <div class="hero-eyebrow">Risk Report</div>
          <div class="hero-title">${esc(p.startup_name)} — ${result.overall}/100 overall risk</div>
          <div class="hero-meta">
            <span>${esc(p.sector)}</span>
            <span>${esc(p.funding_stage)}</span>
            <span>${p.team_size} people</span>
            <span>${esc(p.operations)}</span>
          </div>
        </div>
        <div class="hero-actions">
          <button class="btn-hero-primary" onclick="downloadReport(window.__result)">Download report</button>
          <button class="btn-hero-ghost" onclick="renderForm()">Edit inputs</button>
        </div>
      </div>

      <!-- Section nav -->
      <nav class="section-nav">
        ${[["#bundle","Bundle"],["#products","Products"],["#risk","Risk scores"],["#timeline","Timeline"],["#triggers","Actions"],["#outreach","Outreach"]].map(([h,l])=>`<a class="snav-pill" href="${h}">${l}</a>`).join("")}
      </nav>

      <!-- KPI strip -->
      <div class="kpi-row">
        ${renderKPI("Overall risk", `${result.overall}/100`)}
        ${renderKPI("Top risk", (result.top_risks||[])[0]?.name?.replace(" Risk","") || "—")}
        ${renderKPI("Critical covers", (result.recommendations||[]).filter(r=>r.priority==="Critical").length + " products")}
        ${renderKPI("Bundle quote", result.bundle_only_pricing_quote?.gross_premium_lakh ? `INR ${result.bundle_only_pricing_quote.gross_premium_lakh}L` : "Input needed")}
        ${renderKPI("Premium range", result.premium_summary ? `₹${result.premium_summary.min_lakh}–${result.premium_summary.max_lakh}L` : "—")}
        ${renderKPI("Risk clusters", Object.keys(result.clusters||{}).length + " analysed")}
      </div>

      <!-- Premium summary -->
      ${renderDualPricingPanel(result)}
      ${result.premium_summary ? `
      <div class="premium-card">
        <div class="premium-card-label">Total premium potential</div>
        <div class="premium-card-value">₹${result.premium_summary.min_lakh} – ${result.premium_summary.max_lakh} lakhs</div>
        <div class="premium-card-note">Across ${result.premium_summary.count} products · ${esc(result.premium_footnote||"Indicative estimates only.")}</div>
      </div>` : ""}

      <!-- Action banner -->
      ${renderActionBanner(result.recommendations)}

      <!-- BUNDLE — primary focus -->
      <div class="result-section" id="bundle">
        <div class="result-section-head">
          <div class="result-section-bar"></div>
          <div class="result-section-title">Bundle recommendation</div>
        </div>
        ${renderBundleHero(result.bundle_match, result.recommendations)}
        ${renderBundleAlternatives(result.bundle_alternatives)}
        ${renderV2Insights(result)}
      </div>

      <!-- Recommended products — secondary -->
      <div class="result-section" id="products">
        <div class="result-section-head">
          <div class="result-section-bar"></div>
          <div class="result-section-title">Additional recommended products</div>
        </div>
        <div class="products-list">
          ${(() => {
            const bundleKeys = new Set([
              ...(result.bundle_match?.mandatory_covers || []),
              ...(result.bundle_match?.optional_covers || []),
            ]);
            const additionalRecs = (result.recommendations || []).filter(r => !bundleKeys.has(r.key));
            if (!additionalRecs.length) {
              return `<div class="r-card">${emptyState("✓", "All recommended products are in your bundle", "The engine has no additional products to recommend outside the selected bundle.")}</div>`;
            }
            return renderProductRows(additionalRecs, result.product_mapping);
          })()}
        </div>
        ${renderBadProducts(result.not_preferred_recommendations)}
      </div>

      <!-- Risk scores -->
      <div class="result-section" id="risk">
        <div class="result-section-head">
          <div class="result-section-bar"></div>
          <div class="result-section-title">Risk overview</div>
        </div>
        <div class="score-grid">
          <div class="r-card" style="display:flex;flex-direction:column;">
            <div class="card-label">Overall risk score</div>
            <div class="gauge-wrap" style="flex:1;">
              <div class="gauge-ring" style="--score:${Math.min(100,result.overall)};background:radial-gradient(circle at center,white 0 57%,transparent 58%),conic-gradient(${gaugeColor} calc(${Math.min(100,result.overall)} * 1%),var(--surface) 0);">
                <div class="gauge-ring-inner">
                  <strong>${result.overall}</strong>
                  <span>/100</span>
                </div>
              </div>
              <div class="gauge-label">${overallLabel(result.overall)}</div>
            </div>
          </div>
          <div class="r-card">
            <div class="card-label">Risk categories</div>
            <div id="score-bars-wrap">${renderScoreBars(result.scores)}</div>
          </div>
          <div class="r-card">
            <div class="card-label">Spider graph</div>
            <canvas id="risk-radar" class="radar-canvas" width="340" height="300"></canvas>
          </div>
        </div>
      </div>

      <!-- Top risk drivers -->
      <div class="result-section">
        <div class="result-section-head">
          <div class="result-section-bar"></div>
          <div class="result-section-title">Top risk drivers</div>
        </div>
        <div class="drivers-grid">
          ${renderDriverCards((result.top_risks||[]).slice(0,3))}
        </div>
      </div>

      <!-- Timeline -->
      <div class="result-section" id="timeline">
        <div class="result-section-head">
          <div class="result-section-bar"></div>
          <div class="result-section-title">Coverage timeline</div>
        </div>
        <div class="r-card">
          <div class="timeline">${renderTimeline(result.bundles)}</div>
        </div>
      </div>

      <!-- Regulatory triggers + Mitigations -->
      <div class="result-section two-col" id="triggers">
        <div class="r-card">
          <div class="card-label">Regulatory triggers</div>
          ${renderTriggers(result.regulatory_triggers)}
        </div>
        <div class="r-card">
          <div class="card-label">Non-insurance actions</div>
          ${renderMitigations(result.mitigations)}
        </div>
      </div>

      <!-- Assumptions -->
      <details class="expander-card" style="margin-bottom:24px;">
        <summary>Assumptions used</summary>
        <div class="expander-body">
          <div class="kv-grid">${renderAssumptions(result.assumptions)}</div>
        </div>
      </details>

      <!-- Refine panel -->
      <details class="refine-panel-wrap" style="margin-bottom:24px;">
        <summary>⚙ Refine profile — adjust to sharpen scores</summary>
        <div class="refine-body" id="refine-body">
          ${renderRefineBody()}
        </div>
      </details>

      <!-- Outreach -->
      ${renderOutreach(result.outreach_prompts, result.outreach_source, result.outreach_error)}

      <!-- Downstream -->
      ${renderDownstream(result.downstream_opportunities)}

      <!-- Expanders -->
      <details class="expander-card" style="margin-bottom:14px;">
        <summary>Global products — how SPARC compares</summary>
        <div class="expander-body">
          <div class="products-grid">${renderGlobalProducts(result.global_products)}</div>
        </div>
      </details>

      <details class="expander-card" style="margin-bottom:14px;">
        <summary>Score breakdown — multipliers applied</summary>
        <div class="expander-body">${renderBreakdown(result.multiplier_breakdown)}</div>
      </details>

      <details class="expander-card" style="margin-bottom:14px;">
        <summary>Product comparison table</summary>
        <div class="expander-body">${renderComparisonTable(result.recommendations)}</div>
      </details>

      ${renderCustomTriggers(result.custom_triggers)}

    </div>`;

  // Store result globally for download
  window.__result = result;
  window.__refineResult = result;

  // Bind product row expand/collapse
  window.toggleProductRow = (i) => {
    const row = document.getElementById(`prow-${i}`);
    if (row) row.classList.toggle('expanded');
  };

  // Bind refine
  bindRefine();

  // Bind outreach copy buttons
  document.querySelectorAll("[data-copy]").forEach(btn => {
    btn.addEventListener("click", async () => {
      await navigator.clipboard?.writeText(btn.dataset.copy || "");
      const orig = btn.textContent;
      btn.textContent = "Copied ✓";
      setTimeout(() => btn.textContent = orig, 1800);
    });
  });

  // Draw radar
  setTimeout(() => drawRadar("risk-radar", result.scores, { maxLabelLength: 16 }), 100);
}

/* ─── RESULT HELPERS ─────────────────────────────────────────── */
function renderKPI(label, value) {
  return `
    <div class="kpi-card">
      <div class="kpi-label">${esc(label)}</div>
      <div class="kpi-value">${esc(String(value))}</div>
    </div>`;
}

function isQuoted(q) {
  return q?.covers_priced?.length > 0;
}

function renderPricePanel(quote, tagLabel, tagClass, subtitle) {
  if (!quote || !isQuoted(quote)) return "";
  const covers = quote.covers_priced || [];
  const flags  = quote.underwriter_referral_flags || [];
  return `
    <div class="pricing-card">
      <span class="pricing-panel-tag ${tagClass}">${esc(tagLabel)}</span>
      <div class="pricing-head">
        <div>
          <div class="pricing-title">INR ${esc(quote.gross_premium_lakh)} lakhs</div>
          <div class="premium-card-note">${esc(subtitle)} &nbsp;·&nbsp; incl. 18% GST</div>
        </div>
        <div class="pricing-totals">
          <div class="kv-row"><span class="kv-key">Net premium</span><span class="kv-val">INR ${esc(quote.net_premium_lakh)}L</span></div>
          <div class="kv-row"><span class="kv-key">GST (18%)</span><span class="kv-val">INR ${esc(quote.gst_lakh)}L</span></div>
          <div class="kv-row"><span class="kv-key">${quote.cover_count} cover${quote.cover_count !== 1 ? "s" : ""}</span><span class="kv-val">INR ${esc(quote.total_sum_insured_cr)}Cr SI</span></div>
          ${quote.bundle_discount_lakh > 0 ? `<div class="kv-row"><span class="kv-key">Bundle discount</span><span class="kv-val" style="color:var(--green,#2e7d32)">−INR ${esc(quote.bundle_discount_lakh)}L</span></div>` : ""}
        </div>
      </div>
      <div class="pricing-cover-grid">
        ${covers.map(c => `
          <div class="pricing-cover">
            <div class="pricing-cover-name">${esc(c.cover_name || labelize(c.cover_key))}</div>
            <div class="pricing-cover-premium">INR ${esc(c.premium_lakh)}L</div>
            <div class="pricing-cover-basis">${esc(c.exposure_label || "")} | risk ${esc(c.average_risk_score ?? "n/a")}/100</div>
          </div>`).join("")}
      </div>
      ${flags.length ? `
        <div class="pricing-notes" style="grid-template-columns:1fr;">
          <div><div class="card-label">Underwriter checks</div>${flags.map(f => `<div class="callout-item compact"><span>${esc(f)}</span></div>`).join("")}</div>
        </div>` : ""}
    </div>`;
}

function reviseQuoteInputs() {
  state.quotePanelMode = "edit";
  renderResults(window.__result);
}

function renderDualPricingPanel(result) {
  const bundleQ = result.bundle_only_pricing_quote;
  const fullQ   = result.pricing_engine_quote;
  const bundleName = result.bundle_match?.name || "Recommended bundle";
  const fullCount  = fullQ?.covers_to_price?.length || fullQ?.cover_count || "";

  if ((!isQuoted(bundleQ) && !isQuoted(fullQ)) || state.quotePanelMode === "edit") {
    state.quotePanelMode = null;
    return renderQuoteInputPanel(fullQ || bundleQ);
  }

  return `
    <div class="pricing-split">
      ${renderPricePanel(bundleQ, "Bundle price", "bundle", bundleName)}
      ${renderPricePanel(fullQ,   "Full recommended cover", "full", `${fullCount ? fullCount + " covers — " : ""}bundle + critical products`)}
    </div>
    <div style="margin-top:10px;text-align:right;">
      <button class="btn btn-ghost" type="button" onclick="reviseQuoteInputs()">Edit underwriting inputs</button>
    </div>`;
}

function renderPricingQuote(quote) {
  if (!quote) return "";
  if (quote.quote_type === "input_required" || !quote?.covers_priced?.length) {
    return renderQuoteInputPanel(quote);
  }
  const covers = quote.covers_priced || [];
  const flags = quote.underwriter_referral_flags || [];
  const missing = quote.missing_inputs || [];
  const assumptions = quote.assumptions || [];
  return `
    <div class="pricing-card">
      <div class="pricing-head">
        <div>
          <div class="premium-card-label">Pricing engine quote</div>
          <div class="pricing-title">INR ${esc(quote.gross_premium_lakh)} lakhs incl. GST</div>
          <div class="premium-card-note">${esc(quote.method || "Base rate x sum insured x risk loadings.")}</div>
        </div>
        <div class="pricing-totals">
          <div class="kv-row"><span class="kv-key">Net premium</span><span class="kv-val">INR ${esc(quote.net_premium_lakh)}L</span></div>
          <div class="kv-row"><span class="kv-key">GST</span><span class="kv-val">INR ${esc(quote.gst_lakh)}L</span></div>
          <div class="kv-row"><span class="kv-key">Total SI</span><span class="kv-val">INR ${esc(quote.total_sum_insured_cr)}Cr</span></div>
        </div>
      </div>
      <div class="pricing-cover-grid">
        ${covers.slice(0, 8).map(c => `
          <div class="pricing-cover">
            <div class="pricing-cover-name">${esc(c.cover_name || labelize(c.cover_key))}</div>
            <div class="pricing-cover-premium">INR ${esc(c.premium_lakh)}L</div>
            <div class="pricing-cover-basis">${esc(c.exposure_label || "")} | risk ${esc(c.average_risk_score ?? "n/a")}/100</div>
          </div>`).join("")}
      </div>
      ${flags.length || missing.length || assumptions.length ? `
        <div class="pricing-notes">
          ${flags.length ? `<div><div class="card-label">Underwriter checks</div>${flags.map(f => `<div class="callout-item compact"><span>${esc(f)}</span></div>`).join("")}</div>` : ""}
          ${missing.length ? `<div><div class="card-label">Inputs to confirm</div>${missing.map(m => `<div class="callout-item compact"><span>${esc(m)}</span></div>`).join("")}</div>` : ""}
          ${assumptions.length ? `<div><div class="card-label">Assumptions</div>${assumptions.map(a => `<div class="callout-item compact"><span>${esc(a)}</span></div>`).join("")}</div>` : ""}
        </div>` : ""}
    </div>`;
}

function quoteFieldValue(row) {
  for (const key of (row.aliases || [row.key])) {
    const val = state.profile[key];
    if (val !== undefined && val !== null && val !== "") return val;
  }
  return "";
}

function renderQuoteInputPanel(quote) {
  const fields = quote.required_inputs || [];
  const missing = quote.missing_required_inputs || [];
  const covers = quote.covers_to_price || [];
  // Pre-set boolean fields to false so the default "No" counts as provided
  // without requiring the user to interact with the select first.
  fields.filter(f => f.unit === "yes/no").forEach(f => {
    if (state.profile[f.key] === undefined || state.profile[f.key] === null) {
      state.profile[f.key] = false;
    }
  });
  return `
    <div class="pricing-card">
      <div class="pricing-head">
        <div>
          <div class="premium-card-label">Estimated quote</div>
          <div class="pricing-title">Want to see an estimated quote?</div>
          <div class="premium-card-note">No premium is calculated until you provide the underwriting inputs below. The estimate will use only these submitted values plus the risk assessment already shown.</div>
        </div>
        <div class="pricing-totals">
          <div class="kv-row"><span class="kv-key">Status</span><span class="kv-val">${quote.status === "awaiting_inputs" ? "Waiting for inputs" : "Not requested"}</span></div>
          <div class="kv-row"><span class="kv-key">Covers</span><span class="kv-val">${covers.length}</span></div>
        </div>
      </div>
      ${covers.length ? `
        <div class="cover-pills" style="margin-bottom:14px;">
          ${covers.slice(0, 10).map(c => `<span class="cover-pill">${esc(c.cover_name || labelize(c.cover_key))}</span>`).join("")}
        </div>` : ""}
      <div class="quote-input-grid">
        ${fields.map(row => {
          const val = quoteFieldValue(row);
          const inputHtml = row.unit === "yes/no"
            ? `<select class="f-select" style="height:36px;font-size:13px;"
                 onchange="setVal('${esc(row.key)}', this.value === 'yes')">
                 <option value="no" ${!val ? "selected" : ""}>No</option>
                 <option value="yes" ${val ? "selected" : ""}>Yes</option>
               </select>`
            : `<input class="f-input" type="number" min="0" step="${row.unit === "count" ? "1" : "0.01"}"
                 value="${esc(String(val))}"
                 oninput="setVal('${esc(row.key)}', Number(this.value))" />`;
          return `
          <label class="quote-input-field">
            <span>${esc(row.label)} ${row.unit && row.unit !== "yes/no" ? `<em>${esc(row.unit)}</em>` : ""}</span>
            ${inputHtml}
            ${row.help ? `<small>${esc(row.help)}</small>` : ""}
          </label>`;
        }).join("")}
      </div>
      ${missing.length ? `<div class="notice" style="margin-top:12px;">Please fill ${missing.length} required input${missing.length > 1 ? "s" : ""} before estimating.</div>` : ""}
      <div style="display:flex;gap:10px;align-items:center;margin-top:16px;flex-wrap:wrap;">
        <button class="btn btn-primary" type="button" onclick="generatePricingEstimate()">Generate estimated quote</button>
        <span id="pricing-estimate-status" style="font-size:12px;color:var(--ink-muted);"></span>
      </div>
    </div>`;
}

async function generatePricingEstimate() {
  const status = $("pricing-estimate-status");
  if (status) status.textContent = "Calculating from submitted inputs...";
  state.profile.quote_requested = true;
  try {
    const res = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(state.profile),
    });
    const result = await res.json();
    if (!res.ok || result.error) throw new Error(result.error || "Failed");
    renderResults(result);
  } catch (err) {
    if (status) status.textContent = `Error: ${err.message}`;
  }
}

function overallLabel(score) {
  if (score >= 70) return "High exposure — prioritise critical covers and governance actions now.";
  if (score >= 45) return "Moderate exposure — buy essentials first and review quarterly.";
  return "Lower exposure — start with baseline covers and revisit as you scale.";
}

function renderActionBanner(recs) {
  if (!recs?.length) return "";
  const critical = recs.filter(r => r.priority === "Critical").slice(0, 3);
  if (!critical.length) return "";
  return `
    <div class="action-banner">
      <div class="action-banner-title">Buy now — ${critical.length} critical cover${critical.length>1?"s":""} for your profile</div>
      ${critical.map(r => `
        <div class="action-item-row">
          <span class="action-item-name">${esc(r.name||r.key)}</span>
          ${r.premium ? `<span class="action-price-tag">₹${r.premium.min_lakh.toFixed(1)}–${r.premium.max_lakh.toFixed(1)}L</span>` : ""}
          <span class="action-why">${esc(r.nudge||"")}</span>
        </div>`).join("")}
    </div>`;
}

function renderScoreBars(scores) {
  return Object.entries(scores)
    .sort((a,b) => b[1]-a[1])
    .map(([name, score]) => {
      const lvl = score >= 70 ? "critical" : score >= 40 ? "watch" : "low";
      const badgeLabel = score >= 70 ? "Critical" : score >= 40 ? "Watch" : "Low";
      return `
        <div class="score-bar-item">
          <div class="sbi-head">
            <span class="sbi-name">${esc(name)}</span>
            <div class="sbi-right">
              <span class="sbi-score">${score}</span>
              <span class="badge badge-${lvl}">${badgeLabel}</span>
            </div>
          </div>
          <div class="sbi-bar">
            <div class="sbi-fill ${lvl}" style="width:${Math.min(100,score)}%"></div>
          </div>
        </div>`;
    }).join("");
}

const emptyState = (icon, title, sub="") => `
  <div class="empty-state">
    <div class="empty-state-icon">${icon}</div>
    <div class="empty-state-title">${title}</div>
    ${sub ? `<div class="empty-state-sub">${sub}</div>` : ""}
  </div>`;

function renderDriverCards(risks) {
  if (!risks?.length) return emptyState("📊", "No risk drivers available", "Run the analysis to see your top risk drivers.");
  const explanations = {
    "Cyber Technical Risk": "Digital footprint, data sensitivity and cloud posture create breach and continuity exposure.",
    "Data Privacy Risk": "Personal or sensitive data creates consent, fiduciary, retention and breach-notification obligations.",
    "Regulatory Compliance Risk": "Sector or selected exposure carries licensing, audit, reporting or statutory compliance pressure.",
    "Governance & Fraud Risk": "Investors, controls, fraud exposure and board accountability drive D&O and crime coverage needs.",
    "Liability Risk": "Customer contracts, product failures and negligence claims create third-party loss exposure.",
    "IP Infringement Risk": "AI training data, copyrights and patent landscape create escalating IP litigation risk.",
  };
  return risks.map((r, i) => `
    <div class="driver-card">
      <div class="driver-rank">#${i+1} Driver</div>
      <div class="driver-name">${esc(r.name)}</div>
      <div class="driver-score-row">
        <div class="driver-score-num">${r.score}</div>
        <div class="sbi-bar" style="flex:1;"><div class="sbi-fill critical" style="width:${Math.min(100,r.score)}%"></div></div>
      </div>
      <div class="driver-desc">${explanations[r.name] || "This category is above the rest of your profile and should be reviewed with controls and coverage."}</div>
    </div>`).join("");
}

function renderProductCards(recs, mapping) {
  const byKey = Object.fromEntries((mapping||[]).map(r=>[r.key, r]));
  if (!recs?.length) return `<p style="color:var(--ink-muted)">No recommended products.</p>`;
  const appetiteLabels = { good:"Good risk", moderate:"Moderate", bad:"Not preferred", tbd:"Under review" };
  return recs.map(p => {
    const prio = p.priority || "Optional";
    const prioClass = prio === "Critical" ? "critical" : prio === "Recommended" ? "recommended" : "";
    const prioFlag = prio !== "Optional" ? `<div class="product-card-flag flag-${prio.toLowerCase()}">${esc(prio)} cover</div>` : "";
    return `
      <div class="product-card ${prioClass}">
        ${prioFlag}
        <div class="product-card-name">${esc(p.name||p.key)}</div>
        <div class="product-card-tags">
          <span class="product-tag score">${p.score}/100 fit</span>
          <span class="product-tag appetite-${p.appetite||"tbd"}">${appetiteLabels[p.appetite||"tbd"]}</span>
          ${p.mandatory ? `<span class="product-tag baseline">Baseline</span>` : ""}
        </div>
        <div class="product-card-il"><strong>ICICI Lombard:</strong> ${esc(p.il_product||"")}</div>
        <div class="product-card-nudge">${esc(p.nudge||"")}</div>
        ${p.premium ? `
          <div class="product-premium">
            <div class="product-premium-amount">₹${p.premium.min_lakh.toFixed(1)} – ${p.premium.max_lakh.toFixed(1)}L</div>
            <div class="product-premium-basis">${esc(p.premium.basis)}</div>
          </div>` : ""}
      </div>`;
  }).join("");
}

function renderBadProducts(products) {
  if (!products?.length) return "";
  return `
    <details style="margin-top:16px;">
      <summary style="cursor:pointer;font-size:13px;font-weight:700;color:var(--ink-muted);padding:4px 0;">
        Available but not preferred (${products.length})
      </summary>
      <div class="products-grid" style="margin-top:12px;">${products.map(p=>`
        <div class="product-card">
          <div class="product-card-flag" style="color:var(--ink-faint);">Not preferred</div>
          <div class="product-card-name">${esc(p.name||p.key)}</div>
          <div class="product-card-desc" style="font-style:italic;">${esc(p.bad_reason||"Not preferred for this sector.")}</div>
        </div>`).join("")}
      </div>
    </details>`;
}

function renderBundleHero(bundle, recs) {
  if (!bundle?.name) return `<div class="r-card">${emptyState("📦", "No bundle matched", "No packaged bundle was a strong enough fit for this profile. Recommended products are listed individually below.")}</div>`;

  const mandatory = bundle.mandatory_covers || [];
  const optional  = bundle.optional_covers  || [];
  const recKeys   = new Set((recs||[]).map(r => r.key));
  const eyebrow   = bundle.nearest_fallback ? "Closest package fit" : "Recommended package";

  const coverItems = [
    ...mandatory.map(c => ({ key: c, type: "mandatory" })),
    ...optional.map(c  => ({ key: c, type: "optional"  })),
  ];

  return `
    <div class="bundle-hero">
      <div class="bundle-hero-top">
        <div>
          <div class="bundle-hero-eyebrow">${eyebrow}</div>
          <div class="bundle-hero-name">${esc(bundle.name)}</div>
          <div class="bundle-hero-il">${esc(bundle.il_product_name || "")}</div>
        </div>
        <div style="display:flex;flex-direction:column;align-items:flex-end;gap:8px;flex-shrink:0;">
          <div class="bundle-fit-badge">
            <div class="bundle-fit-dot"></div>
            ${bundle.fit_pct || 0}% profile fit
          </div>
          <span style="background:rgba(173,30,35,.7);color:white;border-radius:999px;padding:4px 14px;font-size:11px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;">${esc(bundle.criticality || "High")}</span>
        </div>
      </div>

      <div class="bundle-hero-desc">${esc(bundle.description || "")}</div>

      <div class="bundle-covers-label">Covers included — ${mandatory.length} mandatory · ${optional.length} optional</div>
      <div class="bundle-cover-grid">
        ${coverItems.slice(0, 12).map(({ key, type }) => {
          const blurb = PRODUCT_BLURBS[key] || "";
          return `
            <div class="bundle-cover-item">
              <div class="bundle-cover-dot ${type}"></div>
              <div>
                <div class="bundle-cover-name">${esc(labelize(key))}</div>
                ${blurb ? `<div class="bundle-cover-blurb">${esc(blurb)}</div>` : ""}
              </div>
            </div>`;
        }).join("")}
      </div>

      ${(bundle.prerequisite_notes || []).map(n => `
        <div style="margin-top:14px;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.12);border-radius:var(--r-sm);padding:10px 14px;font-size:12px;color:rgba(255,255,255,.6);">${esc(n)}</div>`).join("")}
    </div>`;
}

function renderBundleAlternatives(bundles) {
  if (!bundles?.length) return "";
  const statusLabel = (b) => b.alternative_status === "tied" ? "Tied with top pick" : "Lesser relevant";
  return `
    <details class="expander-card" style="margin-top:14px;">
      <summary>Other bundle options (${bundles.length})</summary>
      <div class="expander-body">
        <div class="products-grid-2col">
          ${bundles.map(b => `
            <div class="product-card">
              <div class="product-card-flag">${statusLabel(b)} · Rank ${b.rank}</div>
              <div class="product-card-name">${esc(b.name)} <span class="product-tag score">${b.fit_pct || 0}% fit</span></div>
              <div class="product-card-desc">${esc(b.description || "")}</div>
              <div class="product-card-il">${esc(b.il_product_name || "")}</div>
              <div class="cover-pills" style="margin-top:8px;">
                ${(b.mandatory_covers || []).slice(0, 4).map(c => `<span class="cover-pill">${esc(labelize(c))}</span>`).join("")}
              </div>
            </div>`).join("")}
        </div>
      </div>
    </details>`;
}

function pct(v) {
  if (v === null || v === undefined || v === "") return "n/a";
  const n = Number(v);
  if (!Number.isFinite(n)) return esc(v);
  return `${Math.round(n * 100)}%`;
}

const SIGNAL_LABELS = {
  handles_pii:          "Handles personal data",
  rbi_licensed:         "RBI-licensed business",
  sebi_regulated:       "SEBI-regulated entity",
  healthtech:           "Health data processed",
  fintech:              "Financial services product",
  has_investors:        "Has institutional investors",
  ai_in_product:        "AI used in product",
  b2b_contracts:        "B2B contracts in place",
  physical_assets:      "Owns physical assets",
  gig_workers:          "Employs gig / contract workers",
  export_operations:    "Operates internationally",
  cert_in_obligations:  "CERT-In reporting obligations",
};

const RISK_FACTOR_LABELS = {
  claims_frequency: "How often claims occur in this sector",
  claims_freq:      "How often claims occur in this sector",
  settlement:       "Typical time to resolve a claim",
  settlement_time:  "Typical time to resolve a claim",
  regulatory_volatility: "How fast regulations are changing",
  market_saturation:     "Competition in this cover segment",
};

function renderV2Insights(result) {
  const isV2 = Boolean(result?.config_version || result?.graduation_map || result?.compliance_flags);
  if (!isV2) return "";
  const revenue = result.revenue_breakdown || [];
  const risk = result.risk_multiplier_breakdown || {};
  const graduation = result.graduation_map || {};
  const stageKey = (result.profile?.funding_stage || "Seed")
    .toLowerCase().replace("+", "").replace(/\s+/g, "_").replace("pre-seed", "seed");
  const path = Array.isArray(graduation) ? graduation : (graduation[stageKey] || graduation.seed || []);
  const triggers = result.regulatory_triggers_fired || [];

  const riskItems = Object.entries(risk)
    .filter(([k, v]) => RISK_FACTOR_LABELS[k] != null && v != null)
    .map(([k, v]) => [RISK_FACTOR_LABELS[k], v]);

  const trajectoryLabel = (t) => ({ up: "Growing market", down: "Declining market", stable: "Stable market" }[t] || t || "");

  return `
    <details class="expander-card" style="margin-top:14px;">
      <summary>Why this was recommended</summary>
      <div class="expander-body">
        <div class="two-col">
          <div>
            <div class="card-label">Bundle fit for your profile</div>
            ${revenue.length ? revenue.slice(0, 3).map(r => `
              <div class="callout-item">
                <strong>${esc(r.bundle || "Bundle")}</strong>
                <span>${r.why ? esc(r.why) : `About ${pct(r.adoption)} of businesses at your stage carry this bundle.`}${r.trajectory ? ` ${esc(trajectoryLabel(r.trajectory))}.` : ""}</span>
              </div>`).join("") : emptyState("—", "No fit data available")}
          </div>
          <div>
            <div class="card-label">Market risk factors for this cover</div>
            ${riskItems.length ? riskItems.map(([label, value]) => `
              <div class="kv-row">
                <span class="kv-key">${esc(label)}</span>
                <span class="kv-val">${pct(value)}</span>
              </div>`).join("") : `<div style="color:var(--ink-faint);font-size:13px;">No risk factor data.</div>`}
          </div>
        </div>
        ${path.length ? `
          <div style="margin-top:18px;">
            <div class="card-label">Your coverage roadmap as you grow</div>
            <div class="timeline">${path.map((p, i) => `
              <div class="timeline-item">
                <div class="tl-dot">${i + 1}</div>
                <div class="tl-time">${esc(p.stage || `Step ${i + 1}`)}</div>
                <div class="tl-name">${esc(p.bundle || p.recommendation || "")}</div>
              </div>`).join("")}</div>
          </div>` : ""}
        ${triggers.length ? `
          <div style="margin-top:18px;">
            <div class="card-label">Why certain covers were flagged for you</div>
            <div class="two-col">
              ${triggers.map(t => `
                <div class="callout-item">
                  <strong>${esc(SIGNAL_LABELS[t.signal] || t.signal || "Trigger")} → ${esc(t.product || "")}</strong>
                  <span>${t.citation_url
                    ? `<a href="${esc(t.citation_url)}" target="_blank" rel="noopener noreferrer">${esc(t.regulation || t.reg || "")}</a>`
                    : esc(t.regulation || t.reg || "")}</span>
                </div>`).join("")}
            </div>
          </div>` : ""}
      </div>
    </details>`;
}

function renderProductRows(recs, mapping) {
  const byKey = Object.fromEntries((mapping || []).map(r => [r.key, r]));
  if (!recs?.length) return emptyState("🛡️", "No products recommended", "The engine found no matching ICICI Lombard products for this profile. Try adjusting your inputs.");
  const appetiteLabels = { good: "Good risk", moderate: "Moderate", bad: "Not preferred", tbd: "Under review" };

  return recs.map((p, i) => {
    const prio      = p.priority || "Optional";
    const prioClass = prio === "Critical" ? "critical" : prio === "Recommended" ? "recommended" : "";

    return `
      <div class="product-row ${prioClass}" id="prow-${i}">
        <div class="product-row-left">
          <div class="product-row-name">${esc(p.name || p.key)}</div>
          <div class="product-row-il">${esc(p.il_product || "")}</div>
          <div style="display:flex;gap:5px;margin-top:4px;flex-wrap:wrap;">
            <span class="product-tag score">${p.score}/100 fit</span>
            <span class="product-tag appetite-${p.appetite || "tbd"}">${appetiteLabels[p.appetite || "tbd"]}</span>
            ${p.mandatory ? `<span class="product-tag baseline">Baseline</span>` : ""}
            <span class="badge badge-${prio === "Critical" ? "critical" : prio === "Recommended" ? "watch" : "low"}" style="font-size:10px;">${esc(prio)}</span>
          </div>
        </div>
        <div class="product-row-nudge">${esc(p.nudge || "")}</div>
        <div class="product-row-right">
          ${p.premium ? `<div class="product-row-premium">₹${p.premium.min_lakh.toFixed(1)}–${p.premium.max_lakh.toFixed(1)}L</div>
          <div style="font-size:11px;color:var(--ink-faint);text-align:right;">${esc(p.premium.basis)}</div>` : ""}
          <button class="product-row-expand" onclick="toggleProductRow(${i})" title="Expand">›</button>
        </div>
      </div>`;
  }).join("");
}

function renderTimeline(bundles) {
  if (!bundles?.length) return emptyState("📅", "No timeline data", "Coverage timeline will appear once products are recommended.");
  return bundles.map((b,i) => `
    <div class="timeline-item">
      <div class="tl-dot">${i+1}</div>
      <div class="tl-time">${esc(b.timeline)}</div>
      <div class="tl-name">${esc(b.name)}</div>
      <div class="tl-count">${b.products.length} product${b.products.length!==1?"s":""}</div>
    </div>`).join("");
}

function renderTriggers(triggers) {
  if (!triggers?.length) return emptyState("✅", "No regulatory triggers", "No major regulatory flags were detected for this profile.");
  return triggers.map(t=>`
    <div class="callout-item">
      <strong>${esc(t.name)}</strong>
      <span>${esc(t.detail)}</span>
    </div>`).join("");
}

function renderMitigations(items) {
  if (!items?.length) return emptyState("✅", "No actions required", "No non-insurance mitigation actions were flagged for this profile.");
  return items.map(t=>`
    <div class="callout-item">
      <strong>${esc(t.risk)}</strong>
      <span>${esc(t.action)}</span>
    </div>`).join("");
}

function renderAssumptions(assumptions) {
  const entries = Object.entries(assumptions||{});
  if (!entries.length) return `<p style="color:var(--ink-muted);font-size:13px;">No assumptions recorded.</p>`;
  return entries.map(([k,v])=>`
    <div class="kv-row">
      <span class="kv-key">${esc(labelize(k))}</span>
      <span class="kv-val">${esc(formatVal(v))}</span>
    </div>`).join("");
}

function renderOutreach(prompts, source, error) {
  const entries = Object.entries(prompts||{});
  if (!entries.length) return "";
  const sourceText = source === "gemini"
    ? "AI-generated outreach drafts active."
    : "Using local fallback drafts. Add GEMINI_API_KEY to enable AI-generated drafts.";
  return `
    <div class="result-section" id="outreach">
      <div class="result-section-head">
        <div class="result-section-bar"></div>
        <div class="result-section-title">Outreach kit</div>
      </div>
      <div class="r-card">
        <p style="font-size:12px;color:var(--ink-muted);margin-bottom:14px;">${esc(sourceText)}</p>
        ${error ? `<p class="notice" style="margin-bottom:12px;">${esc(error)}</p>` : ""}
        ${entries.map(([key, item], i) => {
          const email = `${item.email_subject}\n\n${item.email_body}`;
          return `
            <details class="outreach-item" ${i===0?"open":""}>
              <summary>${esc(labelize(key))}</summary>
              <div class="outreach-body">
                <div>
                  <div class="outreach-col-label">Email</div>
                  <pre>${esc(email)}</pre>
                  <button class="btn btn-ghost" style="height:36px;padding:0 14px;font-size:12px;margin-top:8px;" data-copy="${esc(email)}">Copy email</button>
                </div>
                <div>
                  <div class="outreach-col-label">WhatsApp</div>
                  <pre>${esc(item.whatsapp||"")}</pre>
                  <button class="btn btn-ghost" style="height:36px;padding:0 14px;font-size:12px;margin-top:8px;" data-copy="${esc(item.whatsapp||"")}">Copy WhatsApp</button>
                </div>
              </div>
            </details>`;
        }).join("")}
      </div>
    </div>`;
}

function renderDownstream(opps) {
  if (!opps?.length) return "";
  return `
    <div class="result-section">
      <div class="result-section-head">
        <div class="result-section-bar"></div>
        <div class="result-section-title">Downstream opportunities</div>
      </div>
      <div class="downstream-grid">
        ${opps.map(o=>`
          <div class="r-card">
            <div class="card-label">${esc(o.customer_type)} customers</div>
            <div style="font-family:var(--font-head);font-size:16px;font-weight:700;margin-bottom:8px;letter-spacing:-.02em;">${esc(o.product)}</div>
            <p style="font-size:13px;color:var(--ink-muted);line-height:1.55;">${esc(o.rationale)}</p>
            ${o.total_opportunity_lakhs_min !== undefined ? `
              <div class="notice" style="margin-top:10px;">
                Estimated potential: INR ${o.total_opportunity_lakhs_min} – ${o.total_opportunity_lakhs_max} lakhs
              </div>` : ""}
          </div>`).join("")}
      </div>
    </div>`;
}

function renderGlobalProducts(products) {
  if (!products?.length) return emptyState("🌍", "No global benchmarks", "No global product comparisons matched this profile.");
  const statusLabels = { icici:"ICICI Lombard", india_competitor:"Indian market", not_in_india:"Global only" };
  return products.map(p=>`
    <div class="product-card ${p.label==='not_in_india'?'innovation-card':''}">
      <div class="product-card-flag" style="color:var(--ink-faint);">${p.match_basis==='nearest_risk' ? "Nearest benchmark" : (statusLabels[p.label]||"Global")}</div>
      <div class="product-card-name">${esc(p.name)} <span class="product-tag score">${p.relevance_score}/100</span></div>
      <div class="product-card-desc">${esc(p.what_it_covers||"")}</div>
      <div style="font-size:12px;color:var(--ink-muted);">Providers: ${esc(p.providers||"")}</div>
      ${p.label==='not_in_india'?`<p class="notice" style="margin-top:8px;">Product innovation opportunity — flag to product team.</p>`:""}
    </div>`).join("");
}

function renderBreakdown(items) {
  if (!items?.length) return emptyState("⚙️", "No multipliers applied", "No dynamic score multipliers were material for this profile.");
  return items.map(i=>`
    <div class="callout-item">
      <strong>${esc(labelize(i.key))}</strong>
      <span>${esc(i.applied||"")}</span>
      <span style="font-size:11px;color:var(--ink-faint);display:block;margin-top:3px;">${esc(i.stat||"")}</span>
    </div>`).join("");
}

function renderComparisonTable(recs) {
  return `
    <div class="table-wrap">
      <table>
        <thead><tr><th>Product</th><th>Priority</th><th>Fit</th><th>Baseline</th></tr></thead>
        <tbody>
          ${(recs||[]).map(p=>`
            <tr>
              <td>${esc(p.name||p.key)}</td>
              <td>${esc(p.priority||"Optional")}</td>
              <td>${p.score}</td>
              <td>${p.mandatory?"Yes":"No"}</td>
            </tr>`).join("")}
        </tbody>
      </table>
    </div>`;
}

function renderCustomTriggers(triggers) {
  if (!triggers?.length) return "";
  return `
    <div class="r-card innovation-card" style="margin-bottom:24px;">
      <div class="card-label">Product innovation opportunities</div>
      ${triggers.map(t=>`
        <div class="callout-item" style="margin-bottom:10px;">
          <strong>${esc(t.name||labelize(t.key))}</strong>
          <span>${esc(t.description)}</span>
          <div style="font-size:12px;color:var(--ink-faint);margin-top:4px;">IRDAI path: ${esc(t.irdai_path||"")} · Market: ${esc(t.estimated_market_size||"")}</div>
        </div>`).join("")}
    </div>`;
}

/* ─── REFINE PANEL ───────────────────────────────────────────── */
function renderRefineBody() {
  if (!state.meta) return "";
  const meta = state.meta;
  const p = state.profile;

  const mkSlider = (key, label, min, max, step, decimals=2) => {
    const val = Number(p[key] ?? 0);
    return `
      <div class="adv-slider-row">
        <span class="adv-slider-label">${label}</span>
        <input type="range" class="adv-range" min="${min}" max="${max}" step="${step}" value="${val}" data-rkey="${key}" data-dec="${decimals}"
          oninput="this.nextElementSibling.textContent=Number(this.value).toFixed(${decimals})" />
        <span class="adv-slider-val">${val.toFixed(decimals)}</span>
      </div>`;
  };

  const mkSelect = (key, label, opts, nullLabel="") => {
    const cur = p[key];
    return `
      <div class="adv-select-item">
        <label class="adv-select-label">${label}</label>
        <select class="f-select" style="height:38px;font-size:13px;" data-rkey="${key}">
          ${nullLabel?`<option value="">${esc(nullLabel)}</option>`:""}
          ${opts.map(o=>`<option value="${esc(o)}" ${cur===o?"selected":""}>${esc(o)}</option>`).join("")}
        </select>
      </div>`;
  };

  const mkCheck = (key, label) => `
    <label class="adv-check">
      <input type="checkbox" data-rkey="${key}" ${p[key]?"checked":""} />
      <span>${label}</span>
    </label>`;

  return `
    <div class="adv-group">
      <div class="adv-group-title">Governance &amp; capital</div>
      <div class="adv-sliders">
        ${mkSlider("investor_cn_hk_pct","China / HK investor BO",0,1,.01)}
        ${mkSlider("cumulative_fundraising_inr_cr","Total fundraising (INR Cr)",0,10000,10,0)}
        ${mkSlider("founder_concentration_index","Founder concentration",0,1,.01)}
      </div>
      <div class="adv-selects">
        ${mkSelect("holdco_domicile","Holdco domicile",meta.holdcoDomiciles)}
        ${mkSelect("rbi_registration","RBI registration",meta.rbiRegistrations,"None")}
      </div>
      <div class="adv-checks">${mkCheck("dpiit_recognition","DPIIT recognised startup")}</div>
    </div>
    <div class="adv-group">
      <div class="adv-group-title">Data &amp; AI</div>
      <div class="adv-sliders">
        ${mkSlider("sdf_probability","SDF likelihood",0,1,.01)}
        ${mkSlider("hardware_software_split","Hardware revenue share",0,1,.01)}
      </div>
      <div class="adv-selects">
        ${mkSelect("data_localisation_status","Data localisation",["Unknown","Full_onshore","Hybrid","Offshore"])}
        ${mkSelect("ai_tier","AI tier",meta.aiTiers)}
      </div>
    </div>
    <div class="adv-group" style="border-bottom:none;margin-bottom:0;padding-bottom:0;">
      <div class="adv-group-title">Market &amp; supply chain</div>
      <div class="adv-sliders">
        ${mkSlider("b2b_pct","B2B revenue",0,1,.01)}
        ${mkSlider("export_eu_pct","EU revenue",0,1,.01)}
        ${mkSlider("export_us_pct","US revenue",0,1,.01)}
        ${mkSlider("export_china_pct","China revenue",0,1,.01)}
        ${mkSlider("chinese_supplier_pct_cogs","Chinese supplier COGS",0,1,.01)}
      </div>
      <div class="adv-checks">${mkCheck("listed_customer_brsr_dependency","Listed customers require BRSR")}</div>
    </div>
    <div style="margin-top:20px;padding-top:16px;border-top:1px solid var(--border);display:flex;gap:10px;align-items:center;">
      <button class="btn btn-primary" id="refine-run-btn" type="button">Recalculate scores</button>
      <span id="refine-status" style="font-size:12px;color:var(--ink-muted);"></span>
    </div>`;
}

function bindRefine() {
  const body = $("refine-body");
  if (!body) return;
  let timer = null;

  // Sliders auto-update profile
  body.querySelectorAll("input[type='range'][data-rkey]").forEach(el => {
    el.addEventListener("input", () => {
      state.profile[el.dataset.rkey] = Number(el.value);
    });
  });

  body.querySelectorAll("select[data-rkey]").forEach(el => {
    el.addEventListener("change", () => {
      const val = el.value || null;
      state.profile[el.dataset.rkey] = val;
      if (el.dataset.rkey === "ai_tier") state.profile.ai_in_product = val !== "None";
    });
  });

  body.querySelectorAll("input[type='checkbox'][data-rkey]").forEach(el => {
    el.addEventListener("change", () => {
      state.profile[el.dataset.rkey] = el.checked;
    });
  });

  const runBtn = $("refine-run-btn");
  const status = $("refine-status");

  if (runBtn) {
    runBtn.addEventListener("click", async () => {
      runBtn.disabled = true;
      runBtn.textContent = "Recalculating…";
      if (status) status.textContent = "";
      try {
        const res = await fetch("/api/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(state.profile),
        });
        const result = await res.json();
        if (!res.ok || result.error) throw new Error(result.error || "Failed");
        renderResults(result);
      } catch (err) {
        if (status) status.textContent = `Error: ${err.message}`;
      } finally {
        if (runBtn) { runBtn.disabled = false; runBtn.textContent = "Recalculate scores"; }
      }
    });
  }
}

/* ─── DOWNLOAD ───────────────────────────────────────────────── */
window.downloadReport = function(result) {
  if (!result) return;
  const lines = [
    `SPARC Risk Report — ${result.profile.startup_name}`,
    `Generated: ${new Date().toLocaleDateString("en-IN")}`,
    "",
    `Sector: ${result.profile.sector}`,
    `Stage: ${result.profile.funding_stage}`,
    `Team size: ${result.profile.team_size}`,
    `Overall risk: ${result.overall}/100`,
    result.bundle_only_pricing_quote?.gross_premium_lakh ? `Bundle price: INR ${result.bundle_only_pricing_quote.gross_premium_lakh} lakhs incl. GST` : "Bundle price: not requested",
    result.pricing_engine_quote?.gross_premium_lakh ? `Full cover price: INR ${result.pricing_engine_quote.gross_premium_lakh} lakhs incl. GST` : "Full cover price: not requested",
    "",
    "TOP RISKS:",
    ...(result.top_risks||[]).map(r => `  · ${r.name}: ${r.score}/100`),
    "",
    "RECOMMENDATIONS:",
    ...(result.recommendations||[]).map(p => `  · ${p.name||p.key}: ${p.priority} (${p.score}/100)`),
    "",
    "MITIGATION ACTIONS:",
    ...(result.mitigations||[]).map(m => `  · ${m.risk}: ${m.action}`),
  ];
  const blob = new Blob([lines.join("\n")], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = `${(result.profile.startup_name||"startup").replace(/\s+/g,"-")}-sparc-report.txt`;
  a.click();
  URL.revokeObjectURL(url);
};

/* ─── RADAR CHART ────────────────────────────────────────────── */
function drawRadar(canvasId, data, opts = {}) {
  const canvas = $(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const entries = Object.entries(data || {});
  if (!entries.length) return;

  const W = canvas.width, H = canvas.height;
  const cx = W / 2, cy = H / 2;
  const R = Math.min(W, H) * 0.3;
  const maxLen = opts.maxLabelLength || 14;

  ctx.clearRect(0, 0, W, H);

  // Grid rings
  for (let ring = 1; ring <= 4; ring++) {
    ctx.beginPath();
    entries.forEach((_, i) => {
      const angle = -Math.PI/2 + i * 2*Math.PI / entries.length;
      const r = R * ring / 4;
      const x = cx + Math.cos(angle)*r, y = cy + Math.sin(angle)*r;
      i === 0 ? ctx.moveTo(x,y) : ctx.lineTo(x,y);
    });
    ctx.closePath();
    ctx.strokeStyle = "#E2E2DC";
    ctx.lineWidth = 1;
    ctx.stroke();
  }

  // Axis lines + labels
  ctx.font = "10px 'Inter', sans-serif";
  ctx.textAlign = "center"; ctx.textBaseline = "middle";
  entries.forEach(([label], i) => {
    const angle = -Math.PI/2 + i * 2*Math.PI / entries.length;
    const x = cx + Math.cos(angle)*R, y = cy + Math.sin(angle)*R;
    ctx.beginPath(); ctx.moveTo(cx,cy); ctx.lineTo(x,y);
    ctx.strokeStyle = "#E2E2DC"; ctx.lineWidth = 1; ctx.stroke();
    const lx = cx + Math.cos(angle)*(R+28), ly = cy + Math.sin(angle)*(R+28);
    ctx.fillStyle = "#94A3B8";
    const short = label.length > maxLen ? label.slice(0, maxLen-1)+"…" : label;
    ctx.fillText(short, lx, ly);
  });

  // Data polygon
  ctx.beginPath();
  entries.forEach(([_, score], i) => {
    const angle = -Math.PI/2 + i * 2*Math.PI / entries.length;
    const r = R * Math.min(100, Number(score)) / 100;
    const x = cx + Math.cos(angle)*r, y = cy + Math.sin(angle)*r;
    i === 0 ? ctx.moveTo(x,y) : ctx.lineTo(x,y);
  });
  ctx.closePath();
  ctx.fillStyle = "rgba(173,30,35,.14)";
  ctx.strokeStyle = "#AD1E23";
  ctx.lineWidth = 2;
  ctx.fill(); ctx.stroke();

  // Dots on vertices
  entries.forEach(([_, score], i) => {
    const angle = -Math.PI/2 + i * 2*Math.PI / entries.length;
    const r = R * Math.min(100, Number(score)) / 100;
    const x = cx + Math.cos(angle)*r, y = cy + Math.sin(angle)*r;
    ctx.beginPath(); ctx.arc(x,y,3,0,2*Math.PI);
    ctx.fillStyle = "#AD1E23"; ctx.fill();
  });
}

/* ─── KICK OFF ───────────────────────────────────────────────── */
window.renderForm = renderForm;
init();
