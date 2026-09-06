"""Containerized live stack verification script for DecisionSphere Milestone 9.7.

Verifies:
1. GET /api/v1/health (database connected, models verified)
2. GET /api/v1/models/status (all 3 models loaded and hash verified)
3. POST /api/v1/scenarios/ (create a scenario)
4. POST /api/v1/scenarios/{id}/run (execute full cross-domain simulation)
5. Validates 3 domain predictions, financial impact, recommendations, and Gate H provenance.
"""

import sys
import json
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000/api/v1"

AUTHORITATIVE_HASHES = {
    "demand": "fb438c03a742202657bb4ef9196ff17e004bc090e99218f02985dc7720f41941",
    "supply_chain": "0052e641cf355257abb332703c3e6a46c65e9ab10a975227d83cf77d7e689b59",
    "workforce": "4b195c7bee3ab8f4afe75ccd0c75fff0c8e18b9fca88a00305e165a010109918",
}


def http_request(method: str, path: str, data: dict | None = None) -> tuple[int, dict]:
    url = f"{BASE_URL}{path}"
    body = json.dumps(data).encode("utf-8") if data else None
    headers = {"Content-Type": "application/json"} if data else {}
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            resp_body = resp.read().decode("utf-8")
            return resp.status, json.loads(resp_body) if resp_body else {}
    except urllib.error.HTTPError as e:
        resp_body = e.read().decode("utf-8")
        try:
            parsed = json.loads(resp_body)
        except Exception:
            parsed = {"raw": resp_body}
        return e.code, parsed


def main():
    print("=" * 70)
    print("DecisionSphere Container Stack Live Verification")
    print("=" * 70)

    # 1. Health Probe
    print("\n[Step 1] Probing /api/v1/health ...")
    status, body = http_request("GET", "/health")
    print(f"Status: {status}")
    print(f"Response: {json.dumps(body, indent=2)}")
    assert status == 200, f"Expected 200, got {status}"
    assert body.get("status") == "healthy", f"Expected 'healthy', got {body.get('status')}"
    assert body.get("database") == "connected", f"Expected db 'connected', got {body.get('database')}"
    assert body.get("models_verified") is True, f"Expected models_verified=True, got {body.get('models_verified')}"
    print("--> Step 1 PASSED: Container is healthy, DB connected, models verified.")

    # 2. Model Status Probe
    print("\n[Step 2] Probing /api/v1/models/status ...")
    status, body = http_request("GET", "/models/status")
    print(f"Status: {status}")
    print(f"Response: {json.dumps(body, indent=2)}")
    assert status == 200, f"Expected 200, got {status}"
    assert body.get("all_verified") is True, "Expected all_verified=True"
    models = body.get("models", {})
    for domain, expected_hash in AUTHORITATIVE_HASHES.items():
        assert domain in models, f"Missing model domain '{domain}' in response"
        m_info = models[domain]
        assert m_info.get("exists") is True, f"Model '{domain}' does not exist"
        assert m_info.get("verified") is True, f"Model '{domain}' hash not verified"
        computed_hash = (m_info.get("actual_sha256") or m_info.get("computed_hash", "")).lower()
        assert computed_hash == expected_hash, (
            f"Hash mismatch for {domain}: got {computed_hash}, expected {expected_hash}"
        )
    print("--> Step 2 PASSED: All 3 models loaded and byte-identical to frozen SHA-256 fingerprints.")

    # 3. Create Scenario
    print("\n[Step 3] POST /api/v1/scenarios/ ...")
    scenario_payload = {
        "name": "Live Container E2E Test Scenario",
        "description": "Verification of containerized DecisionSphere simulation pipeline",
        "initial_levers": {
            "demand_growth_pct": 15.0,
            "promo_active": True,
            "scheduled_days_offset": 1,
            "shipping_mode_override": "Standard Class",
            "overtime_workforce_pct": 25.0,
            "salary_hike_override": 5.0,
        },
    }
    status, body = http_request("POST", "/scenarios/", scenario_payload)
    print(f"Status: {status}")
    print(f"Response: {json.dumps(body, indent=2)}")
    assert status == 201, f"Expected 201 Created, got {status}"
    scenario_id = body.get("id")
    assert scenario_id, "Missing scenario id in response"
    print(f"--> Step 3 PASSED: Created scenario {scenario_id}")

    # 4. Run Simulation
    print(f"\n[Step 4] POST /api/v1/scenarios/{scenario_id}/run ...")
    status, body = http_request("POST", f"/scenarios/{scenario_id}/run")
    print(f"Status: {status}")
    print(f"Response: {json.dumps(body, indent=2)}")
    assert status == 201, f"Expected 201 Created, got {status}"

    # 5. Deep Validation of Simulation Outputs
    print("\n[Step 5] Validating Simulation Outputs & Gate H Provenance ...")
    run_id = body.get("id")
    scenario_version_ref = body.get("scenario_version_id")
    domain_preds = body.get("domain_predictions") or []
    financial_res = body.get("financial_result") or {}
    recommendation_res = body.get("recommendation_result") or {}
    audit_rec = body.get("audit_record") or {}

    print(f"Run ID: {run_id}")
    print(f"Scenario Version ID: {scenario_version_ref}")
    print(f"Execution Status: {body.get('execution_status')}")
    print(f"Domain Predictions Count: {len(domain_preds)}")

    assert body.get("execution_status") == "SUCCESS", f"Expected SUCCESS, got {body.get('execution_status')}"

    # Domain predictions check (assert all 3 domains present)
    domains_predicted = {p.get("domain") for p in domain_preds}
    print(f"Domains Predicted: {domains_predicted}")
    for expected_domain in ["DEMAND", "SUPPLY_CHAIN", "WORKFORCE"]:
        assert expected_domain in domains_predicted, f"Missing prediction for domain {expected_domain}"

    # Financial impact check
    print(f"Financial Result: Net Profit Delta = {financial_res.get('net_profit_delta')}, Realized Revenue Delta = {financial_res.get('realized_revenue_delta')}")
    assert "net_profit_delta" in financial_res, "Missing net_profit_delta in financial result"
    assert "realized_revenue_delta" in financial_res, "Missing realized_revenue_delta in financial result"

    # Recommendations check
    print(f"Recommendation Result: Decision = {recommendation_res.get('decision_category')}, Risk Level = {recommendation_res.get('risk_level')}, CRS = {recommendation_res.get('composite_risk_score')}")
    assert "decision_category" in recommendation_res, "Missing decision_category"
    assert "composite_risk_score" in recommendation_res, "Missing composite_risk_score"
    assert len(recommendation_res.get("strategic_actions", [])) > 0, "Expected at least 1 strategic action"

    # Gate H Provenance check
    prov = audit_rec.get("provenance_tuple", {})
    print(f"Gate H Audit Provenance Tuple: {json.dumps(prov, indent=2)}")
    assert audit_rec.get("model_hashes"), "Missing model_hashes in audit record"
    for domain, exp_hash in AUTHORITATIVE_HASHES.items():
        recorded_hash = audit_rec["model_hashes"].get(domain, "").lower()
        assert recorded_hash == exp_hash, (
            f"Gate H hash mismatch for {domain}: got {recorded_hash}, expected {exp_hash}"
        )

    print("\n--> Step 5 PASSED: Full E2E simulation verified successfully inside container!")
    print("    - 3 Domain Predictions (DEMAND, SUPPLY_CHAIN, WORKFORCE)")
    print("    - Managerial Financial Accounting Result")
    print(f"    - Strategic Recommendation ({recommendation_res.get('decision_category')})")
    print("    - Gate H Cryptographic Provenance Record")
    print("\n" + "=" * 70)
    print("ALL LIVE CONTAINER VERIFICATION CHECKS PASSED!")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"\nFAILED with error: {exc}", file=sys.stderr)
        sys.exit(1)
