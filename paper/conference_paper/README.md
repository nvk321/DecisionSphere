# DecisionSphere — Official IEEE Conference Paper

This directory contains the self-contained, publication-ready research manuscript formatted in strict accordance with the official **IEEE Conference Template (06/28/2024)**.

---

## Directory Contents

- `IEEEtran.cls`: Official IEEE conference class file (self-contained, no external installation required).
- `DecisionSphere_Conference_Paper.tex`: Main IEEE conference manuscript encompassing all 9 empirical experiments, mathematical derivations, tables, and figures.
- `main.tex`: Standard entrypoint for Overleaf.
- `references.bib`: BibTeX bibliography containing all 13 peer-reviewed citations.
- `figures/`: High-resolution 300 DPI publication figures.
- `tables/`: Modular LaTeX tables.

---

## How to Compile

### Option 1: Overleaf Cloud (Recommended)
1. Zip the contents of this `conference_paper/` folder.
2. Log in to [Overleaf](https://www.overleaf.com/).
3. Click **New Project** $\to$ **Upload Project** and upload the zip file.
4. Set compiler to **pdfLaTeX** and click **Recompile**.

### Option 2: Local Compilation (TeX Live / MiKTeX)
```bash
pdflatex DecisionSphere_Conference_Paper.tex
bibtex DecisionSphere_Conference_Paper
pdflatex DecisionSphere_Conference_Paper.tex
pdflatex DecisionSphere_Conference_Paper.tex
```

---

## Empirical Verification Summary
- **Demand Forecasting:** XGBoost achieved **8.12% WAPE** on chronological holdout vs. 33.32% naive baseline.
- **Logistics Delivery Risk:** Platt-calibrated XGBoost achieved **0.7795 ROC-AUC** and reduced Expected Calibration Error (ECE) to **0.0142** (-72.7%).
- **Workforce Attrition Risk:** Calibrated XGBoost achieved **0.8045 ROC-AUC** and **0.0537 ECE**.
- **Margin Tipping Point:** Empirically identified at **+18.4% demand growth**.
- **Canonical Scenario Deficit:** **-$642,716.18 USD** net operating profit collapse under unbuffered +15% demand surge and 40% overtime.
- **Monte Carlo Stability:** **100.0% REJECT_RESTRUCTURE** recommendation stability across N=200 stochastic runs with asymptotic standard error convergence ($\text{SE} = \$3,955.49$).
