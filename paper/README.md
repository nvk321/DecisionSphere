# DecisionSphere — IEEE-Formatted Research Manuscript

This directory contains the formal academic research paper manuscript for the DecisionSphere project, formatted in accordance with the official IEEE conference proceedings template (\texttt{IEEEtran.cls}).

> [!NOTE]
> **Status:**  
> This manuscript represents an **IEEE-formatted research manuscript** prepared for academic review and university deliverables. Venue submission depends on targeting specific peer-reviewed tracks (e.g., IEEE/ACM conferences in decision support or enterprise intelligence).

---

## Directory Structure

```
paper/
├── DecisionSphere_Conference_Paper.tex # IEEEtran Conference Manuscript (6-8 pages)
├── DecisionSphere_Journal_Paper.tex    # IEEEtran Journal Manuscript (14-18 pages)
├── VENUE_SHORTLIST.md                 # Verified Scopus/IEEE venue selection strategy
├── references.bib                     # Verified BibTeX bibliography (20+ citations)
├── figures/                           # 300 DPI publication figures (fig1-fig6, etc.)
├── tables/                            # LaTeX table modular sources
└── README.md                          # Documentation and compilation instructions
```

---

## Compilation Instructions

### Option 1: Compiling Locally via TeX Live / MiKTeX
If you have a local LaTeX distribution installed:
```bash
cd paper
pdflatex DecisionSphere_Research_Paper.tex
bibtex DecisionSphere_Research_Paper
pdflatex DecisionSphere_Research_Paper.tex
pdflatex DecisionSphere_Research_Paper.tex
```

### Option 2: Overleaf Cloud Compilation (Recommended)
1. Zip the entire `paper/` directory:
   - Include `DecisionSphere_Research_Paper.tex`, `references.bib`, and the `figures/` directory.
2. Log in to [Overleaf](https://www.overleaf.com/).
3. Click **New Project** $\to$ **Upload Project** and select the zip file.
4. Set compiler to **pdfLaTeX** and click **Recompile**.

---

## Authoritative Canonical Scenario Reference

All experimental results, financial accounting waterfalls, and risk evaluations reported in Section X correspond to the verified live backend canonical scenario:
- **Commercial Shock:** Demand $+15.0\%$, Active Promotional Campaign.
- **Logistics Setting:** Standard Class Shipping, $0\text{d}$ Lead Time SLA Offset.
- **Workforce Setting:** $40.0\%$ Mandatory Overtime, Baseline Compensation.
- **Verified Net Operating Profit Delta:** $-\$642,716.18$ USD.
- **Composite Risk Score (CRS):** $37.48 / 100$ (\texttt{MODERATE RISK}).
- **Decision Category:** \texttt{REJECT\_RESTRUCTURE} (\texttt{RULE-04: Margin Erosion Warning}).
