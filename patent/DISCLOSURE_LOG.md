# DecisionSphere — Intellectual Property Disclosure & Pre-Filing Log

**Confidentiality Level:** RESTRICTED / INTERNAL IPR RECORD  
**Purpose:** Formal tracking of technical disclosures, contributor conception events, and publication status to safeguard absolute novelty under Indian Patent Law (Sections 29–34, Patents Act 1970) and international patent statutes.  
**Authoritative Protocol:** [AGENTS.md](file:///d:/Projects/DecisionSphere/AGENTS.md)  

---

## 1. Statutory Notice on Prior Disclosure

Under the Patents Act, 1970 (India), public demonstration, publication, or commercial exploitation of an invention prior to the filing date of a patent application generally destroys patentable novelty. While Section 31 provides limited grace periods for paper presentations before learned societies or government exhibitions, **safe legal practice requires filing a Provisional Patent Application BEFORE any public manuscript, presentation, or code repository release**.

---

## 2. Master Intellectual Property Disclosure Log

| Date | Version | Contributors / Inventors | Technical Change / Disclosure Event | Enabling Evidence | Publicly Disclosed? | Where Disclosed | IP Relevance & Novelty Impact |
|---|---|---|---|---|---|---|---|
| **2026-07-29** | v0.1.0 | P N V Kushal, P M K Tejas, J R Sagabala, Dr. Suresh A | Review 1: Project concept formulation and literature survey. | Review 1 Presentation Slides (`docs/`) | Academic Only (Internal to VIT Faculty) | Internal University Review Panel | TRL 2 formulated. No enabling mathematical state-space or calibration code disclosed. |
| **2026-09-15** | v0.2.0 | Lead Research Engineer, Technical Contributors | Implementation of baseline predictive models across Rossmann, DataCo, and IBM HR datasets. | `models/demand/`, `models/supply_chain/`, `models/workforce/` | No (Private Repository) | N/A | Established offline ML baselines. Known algorithms (XGBoost) not patentable in isolation. |
| **2026-10-10** | v0.3.0 | Lead Systems Architect, Research Contributors | Review 2: End-to-end prototype with 13-stage deterministic accounting and 6-tier epistemic hierarchy. | Review 2 Report (`university_reviews/REVIEW_2/`) | Academic Only (Internal to VIT Committee) | VIT BCSE497J Evaluation Committee | TRL 4 achieved. Functional demonstration of coupling; conceptual architecture presented. |
| **2026-10-24** | v0.4.0 | Lead Research Engineer & Systems Architect | Formulation of 24-dimensional continuous state vector in $\mathbb{R}^{24}$, 11-node DAG propagation operator, and Platt probability-to-penalty error bounding. | `src/scenario/state.py`, `src/scenario/graph.py`, `src/scenario/propagation.py`, `tests/test_patent_core.py` | **NO (STRICT CONFIDENTIALITY)** | Internal Workspace Only | **CORE PATENTABLE EMBODIMENT CONCEIVED & IMPLEMENTED**. Must NOT be disclosed publicly prior to provisional filing. |
| **2026-10-24** | v0.4.1 | Autonomous Research Verification Agent | Independent verification audit of all 11 quantitative claims; generation of EXP-P01 through EXP-P07 and formal technical evidence. | `research/VERIFICATION_AUDIT.md`, `patent/TECHNICAL_EFFECT_EVIDENCE.md` | **NO (CONFIDENTIAL)** | Internal Workspace Only | Provides empirical evidence of technical effect ($72.7\%$ ECE drop, $\$27\text{k}+$ penalty distortion elimination, $\$642\text{k}+$ capital misallocation avoided). |
| **2026-10-24** | v0.5.0 | Complete Project Team | Authoring of Conference Manuscript (`paper/DecisionSphere_Conference_Paper.tex`) and Journal Manuscript (`paper/DecisionSphere_Journal_Paper.tex`). | `paper/` directory | **NO (PENDING IP CLEARANCE)** | Drafted for venue submission | Manuscripts drafted. **MANDATORY HOLD:** Formal submission to IEEE/ACM conferences or Scopus journals must occur ONLY AFTER provisional patent filing or explicit written IP waiver. |

---

## 3. Contributor & Conception Record

The technical concepts embodied in the candidate patent claims (the 24-dimensional continuous state vector, 11-node DAG propagation operator, and Platt probability-to-penalty error bounding) were formulated and reduced to practice within the DecisionSphere project team at VIT SCOPE under project code `BCSE497J`.

- **Primary Student Researchers & Co-Inventors:**
  1. P Naga Venkata Kushal (Reg No: 23BDS0133)
  2. P Manjunatha Kumar Tejas (Reg No: 23BCE0584)
  3. Jeswanth Reddy Sagabala (Reg No: 23BCE0203)
- **Faculty Guide / Mentor:**
  - Dr. Suresh A (School of Computer Science and Engineering, VIT)

---

## 4. IP Precedence & Release Directive

1. **Pre-Filing Secrecy:** All code in `src/scenario/propagation.py`, `src/scenario/state.py`, and `src/scenario/graph.py`, as well as the documents in `patent/`, must remain in a private, access-restricted repository.
2. **Institutional Routing:** This complete IP package (`patent/`) must be submitted to the **VIT Center for Intellectual Property Rights (CIPR) / IPR Cell** for formal patentability screening and provisional application drafting.
3. **Academic Submission Synchronization:**
   - If CIPR approves provisional patent filing: File Form 1, Form 2 (Provisional Specification), and Form 5 with the Indian Patent Office Chennai branch. Once the official Filing Receipt / Application Number is secured (typically 24–48 hours), academic manuscripts in `paper/` may be submitted to conferences or journals without risk to patent priority.
   - If CIPR determines that patent filing is unviable or declines to proceed: Immediately release manuscripts in `paper/` to Tier A peer-reviewed venues (IEEE TEMSCON / IEEE SMC / IEEE TEM) under the publication track.
