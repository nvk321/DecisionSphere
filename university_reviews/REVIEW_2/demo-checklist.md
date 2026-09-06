# Review 2 — Live Software Demonstration Runbook & Checklist

**Project Title:** `DecisionSphere: A Scenario-Based Strategic Planning and Risk Evaluation Platform`  
**Purpose:** Standard Operating Procedure for the live viva software demonstration before the faculty panel.  
**Target Duration:** 5 to 7 minutes.  
**Authoritative Canonical Scenario Target:** Demand Shock $+15\%$, Promo Active, Lead Time SLA Offset $0\text{d}$, Shipping Standard Class, Overtime $40\%$, Salary Hike None. Expected Net Profit Delta: $-\$642,716.18$, CRS: $37.48$, Recommendation: `[RULE-04] ACT-FIN-001 Margin Erosion Warning`.

---

## 1. Pre-Demo Environment Verification (Execute 15 Mins Before Viva)

- [ ] **Backend Server Check:**
  - Verify FastAPI backend is active and listening on port 8000:
    ```bash
    curl http://127.0.0.1:8000/health
    ```
    *Expected Response:* `{"status":"healthy","version":"1.0.0",...}`
- [ ] **Frontend Server Check:**
  - Open browser and navigate to `http://localhost:3000`.
  - Verify page loads with zero console errors.
- [ ] **Database & Model Check:**
  - Navigate to `http://localhost:3000/system/health` and verify all 3 models display **ONLINE** with matching SHA-256 hashes.

---

## 2. Step-by-Step Live Demonstration Sequence

### Step 1: System Health & Cryptographic Integrity (1 Minute)
1. **Screen:** `http://localhost:3000/system/health` and `/system/models`.
2. **Action:** Show the panel the three predictive models (Rossmann Demand, DataCo Supply Chain, IBM HR Attrition).
3. **Narration to Panel:**
   > "We begin by showing our system governance layer. All three domain models are loaded into memory and validated cryptographically via SHA-256 digests (Gate H). Notice that probabilistic calibration (Gate G) is verified, with calibration error compressed under 0.05. No mock data is used; every inference runs against these frozen artifacts."

### Step 2: Scenario Creation & Lever Adjustment (1.5 Minutes)
1. **Screen:** `http://localhost:3000/simulate`.
2. **Action:**
   - In **Scenario Details**, enter Name: `Review 2 Canonical Stress Test`.
   - In **Commercial Levers**, set **Demand Shock** slider to `+15.0%`.
   - Toggle **Promotional Campaign** to `Active` (Checked).
   - In **Logistics Levers**, leave **Lead Time SLA Offset** at `0 days`.
   - Verify **Shipping Mode** is set to `Standard Class`.
   - In **Workforce Levers**, set **Mandatory Overtime** slider to `40.0%`.
   - Leave **Salary Adjustment** at `0.0%` (None).
3. **Narration to Panel:**
   > "Here is our Scenario Builder. We are simulating a standard corporate dilemma: marketing launches an aggressive promotional push expected to generate +15% demand, but operations plans to absorb the surge using 40% mandatory overtime without expanding headcount or logistics capacity."
4. **Action:** Click the primary blue button: **`Execute Cross-Domain Simulation`**.

### Step 3: Simulation Results & Domain Disruption Analysis (1.5 Minutes)
1. **Screen:** `http://localhost:3000/simulations/[id]` (Automatic redirect).
2. **Action:** Point out the three Domain Metric Cards:
   - **Demand Card:** Base `55,666.31` $\to$ Scenario `84,217.35` ($\Delta = +28,551.04$ units, $+51.29\%$).
   - **Supply Chain Card:** Late Delivery Risk shifts from $49.24\%$ baseline to $47.11\%$ scenario.
   - **Workforce Card:** Attrition Risk spikes from $16.51\%$ to $18.85\%$ ($\Delta = +2.34\text{ pp}$).
3. **Narration to Panel:**
   > "The simulation completes in under 200 milliseconds. The Demand model forecasts an additional 28,551 units. However, looking at Workforce, mandatory overtime immediately pushes employee turnover probability from 16.5% up to 18.85%."

### Step 4: Explainable AI & TreeSHAP Attribution (1 Minute)
1. **Screen:** Click **`Explain Prediction`** button on the Workforce card.
2. **Action:** Open the **TreeSHAP Waterfall Modal**.
3. **Narration to Panel:**
   > "To ensure complete transparency, we inspect the TreeSHAP attribution. The waterfall chart proves that the `OverTime` indicator provides the dominant positive Shapley attribution (+0.445), statistically driving employee attrition risk upward."

### Step 5: Financial Impact & The Bottom-Line Margin Collapse (1.5 Minutes)
1. **Screen:** Scroll down to the **Financial Waterfall & Decision Hero** section.
2. **Action:** Hover over the financial waterfall steps:
   - Realized Revenue Delta: `+$26,710.78`
   - Cost of Goods Sold (COGS): `+$16,026.47`
   - Logistics Disruption Cost: `+$469,188.49`
   - Workforce Overtime & Turnover Cost: `+$184,212.00`
   - **Net Operating Profit Delta: `-$642,716.18`**
3. **Action:** Highlight the **Decision Hero**:
   - **Decision Category:** `REJECT_RESTRUCTURE` (Red Badge).
   - **Composite Risk Score:** `37.48 / 100` (`MODERATE RISK`).
   - **Triggered Strategic Action:** `[RULE-04] ACT-FIN-001: Margin Erosion Warning: Rescale Promotional Intensity`.
4. **Narration to Panel:**
   > "Here is the critical strategic finding: While top-line realized revenue expanded by \$26,710, the volume surge triggered \$469,188 in carrier disruption and \$184,212 in labor costs. The enterprise loses \$642,716! DecisionSphere automatically rejects the scenario under Rule 4, preventing a catastrophic commercial misstep."

### Step 6: Sensitivity Sweeps & Policy Simplex (Optional 1 Minute)
1. **Screen:** `http://localhost:3000/sensitivity`.
2. **Action:** Select parameter `asm_001_delay_penalty` and sweep between \$10 and \$60.
3. **Narration to Panel:**
   > "Finally, our sensitivity sweep engine allows leadership to test how resilient this decision is against varying delay penalty contracts, demonstrating that the strategy remains net-negative across all realistic cost regimes."

---

## 3. Emergency Fallback Procedure

If the local network drops or a browser port fails:
1. Open terminal: `python scripts/get_canonical_run_metrics.py`.
2. The terminal script executes the exact same underlying backend pipeline and prints all verified numbers, proving that the Python analytical core is 100% operational offline.
