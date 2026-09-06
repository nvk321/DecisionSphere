# DecisionSphere: Research Paper — Chapter 13: Reproducibility & Open Artifacts

**Section:** 12. Reproducibility, Open Code & Artifact Registries  
**Context:** Verification Protocols, Cryptographic Signatures, and Artifact Repositories

---

### 12.1 Open Science & Artifact Availability
To ensure complete academic reproducibility, all code, benchmark dataset loaders, serialized model artifacts, Jupyter research notebooks, and configuration files are maintained in the open repository:
- **Repository Core:** `https://github.com/DecisionSphere/DecisionSphere`
- **TRL Level:** Technology Readiness Level 4 (Laboratory Validated System Prototype)
- **Primary Runtime:** Python 3.13.5 (CPython) / Node.js 20.x / Windows 11 / Linux (Ubuntu 22.04 LTS).

---

### 12.2 Frozen Analytical Core Guarantee
In accordance with research protocol, the analytical core of DecisionSphere is frozen and invariant. Evaluators can verify that no code changes occurred during notebook execution or frontend evaluation:
```bash
git diff --stat src models
# Output: 0 files changed, 0 insertions, 0 deletions
```

---

### 12.3 Cryptographic Integrity Verification (Gate H)
Every serialized machine learning model bundle (`.joblib`) is verified using SHA-256 cryptographic hashing prior to execution:

| Artifact Path | SHA-256 Cryptographic Checksum | Verified Integrity Status |
|:---|:---|:---:|
| `models/demand/demand_model.joblib` | `029671d44fdba6b81561578f77395015e5109bcf7efb2dbe2c448fe9c15ffc11` | Cryptographically Verified |
| `models/supply_chain/supply_chain_model.joblib`| `54b9d3b36484e5264b3fe3f37b19ce8a514d88e63784197f2beadcf752c009d1` | Cryptographically Verified |
| `models/workforce/workforce_model.joblib` | `8c4746f345df74ceb3ef5d22f6da0684f22ae391bf39cff281a95e263d91cf33` | Cryptographically Verified |

At server startup and during every simulation pass, `ScenarioEngine.get_artifact_fingerprints()` computes the runtime digest of the disk artifacts. If any model file is altered by even one bit, Gate H terminates execution with an `IntegrityError`.

---

### 12.4 Executable Jupyter Research Suite
The 16-part Jupyter Research Suite (`notebooks/00_*.ipynb` through `15_*.ipynb`) provides fully executable documentation of the data pipelines, model evaluations, cross-domain propagation, and financial calculations:
- Fully automated deterministic batch runner: `python scripts/execute_notebook_suite.py`.
- Automated regression suite: `pytest tests/test_research_suite.py`.
- Publication figures (300 DPI) generated deterministically in `artifacts/figures/`.
