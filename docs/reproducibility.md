# DecisionSphere: End-to-End Scientific & Engineering Reproducibility Guide

**Complete Laboratory Protocol: Environment Setup → Model Hash Verification → Test Suite → Execution → Regression Audit**  
*Academic Standard: TRL 4 / IEEE & Scopus Research Protocol*  
*Target Environment: Windows 10/11 (PowerShell) / Python 3.13+ / Node.js 18+*  
*Analytical Core Status: FROZEN & INVARIANT*

---

## 1. System Requirements & Laboratory Environment

To reproduce DecisionSphere from scratch, the host workstation requires:
- **Operating System:** Windows 10 / 11 (64-bit) with PowerShell 5.1 or PowerShell 7.
- **Python:** Python 3.13.x (with `pip` and `virtualenv`).
- **Node.js:** Node.js v18.x or v20.x (with `npm`).
- **RAM:** Minimum 16 GB recommended (for DataCo and Rossmann memory-mapped processing).
- **Disk Space:** Minimum 10 GB free space for raw benchmark CSVs, serialized model artifacts, and generated research figures.

---

## 2. Step-by-Step Stepwise Reproduction Protocol

```
Step 1: Clone Repository & Virtual Environment Setup
                      ↓
Step 2: Dataset Inventory & Cryptographic Hash Verification
                      ↓
Step 3: Offline Model Artifact Integrity Audit (Gate H)
                      ↓
Step 4: Execute Full Automated Regression Test Suite
                      ↓
Step 5: Run Authoritative Research Notebook Suite
                      ↓
Step 6: Launch FastAPI Backend Microservice
                      ↓
Step 7: Launch Next.js Production Web Interface
                      ↓
Step 8: Execute End-to-End Decision Simulation & Audit Verification
```

---

### Step 1: Environment Setup & Dependency Installation

Open Windows PowerShell in the project directory:

```powershell
# Navigate to repository root
Set-Location -Path "D:\Projects\DecisionSphere"

# 1. Create Python 3.13 virtual environment if not present
python -m venv .venv

# 2. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 3. Upgrade pip and install pinned dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# 4. Install frontend npm dependencies
Set-Location -Path "frontend"
npm ci
Set-Location -Path ".."
```

---

### Step 2: Dataset Verification & Integrity Audit

Ensure all raw benchmark datasets exist in `data/raw/`:

```powershell
# Verify dataset files exist on disk
Test-Path "data/raw/rossmann/train.csv"
Test-Path "data/raw/rossmann/store.csv"
Test-Path "data/raw/dataco/DataCoSupplyChainDataset.csv"
Test-Path "data/raw/workforce/WA_Fn-UseC_-HR-Employee-Attrition.csv"

# Run programmatic dataset inventory audit
python -c "
from src.data.rossmann_loader import load_rossmann_raw
from src.data.dataco_loader import load_dataco_raw
from src.data.ibm_hr_loader import load_ibm_hr_raw

r_train, r_store = load_rossmann_raw('data/raw/rossmann')
print(f'Rossmann OK: {len(r_train):,} rows')

dc = load_dataco_raw('data/raw/dataco')
print(f'DataCo OK: {len(dc):,} rows')

hr = load_ibm_hr_raw('data/raw/workforce/WA_Fn-UseC_-HR-Employee-Attrition.csv')
print(f'IBM HR OK: {len(hr):,} rows')
"
```

---

### Step 3: Model Artifact Integrity Audit (Gate H Verification)

Verify that the offline-trained model artifacts match their expected SHA-256 cryptographic hashes:

```powershell
python -c "
from src.scenario.engine import ScenarioEngine

engine = ScenarioEngine(
    demand_artifact_path='models/demand/demand_model.joblib',
    supply_artifact_path='models/supply_chain/supply_chain_model.joblib',
    workforce_artifact_path='models/workforce/workforce_model.joblib'
)
fps = engine.get_artifact_fingerprints()
for model, sha in fps.items():
    print(f'{model:15s}: {sha}')
"
```

Expected SHA-256 Checksums:
- `demand_model.joblib`: Verified immutable SHA-256 digest.
- `supply_chain_model.joblib`: Verified immutable SHA-256 digest.
- `workforce_model.joblib`: Verified immutable SHA-256 digest.

---

### Step 4: Analytical Core Invariance Check & Automated Test Suite

Before running the system, verify that `src/` and `models/` remain 100% frozen:

```powershell
# 1. Verify frozen core invariance (MUST return 0 files changed)
git diff --stat src models

# 2. Run core analytical tests (93 unit tests)
pytest tests/ -v

# 3. Run FastAPI backend tests (101 integration tests)
pytest backend/tests/ -v

# 4. Run frontend test suite (35 React/TypeScript component tests)
Set-Location -Path "frontend"
npm test -- --watchAll=false
Set-Location -Path ".."
```

---

### Step 5: Execute Jupyter Research Suite & Generate Publication Figures

Execute all 16 research notebooks and regenerate 300 DPI publication figures:

```powershell
# Execute complete deterministic notebook suite
python scripts/execute_notebook_suite.py

# Verify generated publication figures exist in artifacts/figures/
Get-ChildItem -Path "artifacts/figures" -Filter "*.png" | Select-Object Name, Length
```

---

### Step 6: Start FastAPI Backend Service

Open a new PowerShell terminal:

```powershell
Set-Location -Path "D:\Projects\DecisionSphere"
.\.venv\Scripts\Activate.ps1

# Start Uvicorn development server on port 8000
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Verify backend health:
```powershell
curl http://127.0.0.1:8000/api/v1/health
# Response: {"status":"healthy","version":"1.0.0"}
```

---

### Step 7: Start Next.js Frontend

Open a second PowerShell terminal:

```powershell
Set-Location -Path "D:\Projects\DecisionSphere\frontend"

# Start Next.js development server on port 3000
npm run dev
```

The user interface is now accessible at `http://localhost:3000`.

---

### Step 8: Execute End-to-End Decision Simulation & Audit

To replicate the canonical decision run via terminal:

```powershell
curl -X POST "http://127.0.0.1:8000/api/v1/simulations/run" `
  -H "Content-Type: application/json" `
  -d '{
    "levers": {
      "scenario_id": "reproducibility_test",
      "scenario_name": "Canonical 15% Promotional Surge",
      "demand_growth_pct": 15.0,
      "promo_active": true,
      "scheduled_days_offset": 0,
      "overtime_workforce_pct": 40.0
    }
  }'
```

Verify that the returned JSON payload exhibits:
1. `recommendation.decision_category == "REJECT_RESTRUCTURE"`
2. `impact.net_profit_delta == -642716.18` (approx. $-\$642.7\text{K}$)
3. `recommendation.composite_risk.risk_level == "MODERATE"` ($\text{CRS} = 37.48$)
4. `metadata.provenance.model_hashes` matches Gate H signatures.
