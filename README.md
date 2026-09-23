# Journal Entry Anomaly Detector

Python tool that applies standard audit analytical procedures to a real,
public government payment dataset — the [Texas Education Agency's Check
Register (FY2025)](https://tea.texas.gov/about-tea/agency-finances/check-register/tea-check-register),
covering 100,000+ transactions paid to school districts and vendors
statewide.

## What it does

This project runs four analytical procedures commonly used in audit
fieldwork to identify transactions warranting further review:

| Check | What it flags | Why auditors run it |
|---|---|---|
| **Duplicate payment detection** | Same vendor, same amount, paid within 7 days | Classic double-payment / control failure test |
| **Round-dollar analysis** | Payments that are suspiciously round ($X,000 or $X00) | Round numbers can indicate estimates or manual overrides rather than invoiced amounts |
| **Weekend posting check** | Transactions dated on a Saturday or Sunday | Unusual timing can indicate manual entries outside normal processing controls |
| **Benford's Law analysis** | Statistical deviation in the distribution of leading digits | A widely used fraud-detection heuristic — naturally occurring financial data follows a predictable digit pattern; large deviations warrant investigation |

## Sample Results

*(Fill this in after running the script on your own machine — replace with
your real numbers before pushing to GitHub)*

- **Total transactions analyzed:** `[X]`
- **Potential duplicate payment pairs flagged:** `[X]`
- **Round-dollar transactions:** `[X]` (`[X]%` of total)
- **Weekend postings:** `[X]` (`[X]%` of total)
- **Benford's Law chi-square p-value:** `[X]`

## How to run it

1. Clone this repo and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Download the dataset from TEA's website (not included in this repo due
   to file size):
   ```
   https://tea.texas.gov/about-tea/agency-finances/check-register/25-cr-report.csv
   ```
   Save it in the project root as `25-cr-report.csv`.
3. Run the analysis:
   ```bash
   python anomaly_detector.py
   ```
4. Outputs:
   - `anomaly_summary.csv` — headline results table
   - `flagged_duplicates.csv` — detail of flagged potential duplicate payments
   - `benford_chart.png` — observed vs. expected leading-digit distribution

## Methodology notes

- **Duplicate detection window:** 7 days was chosen as a reasonable
  materiality threshold for "near-duplicate" timing — adjustable in the
  script.
- **Benford's Law caveat:** this test works best on naturally occurring,
  unconstrained transaction amounts. Some deviation is expected here since
  government payments include recurring fixed amounts (e.g., standard
  monthly allotments), which is a legitimate limitation worth noting in
  discussion of the results, not a flaw to hide.
- **Data source limitation:** the TEA register only contains vendor name,
  date, and gross amount — no invoice numbers, GL account codes, or
  approver info, so this analysis is necessarily narrower than a real
  audit team's access to underlying ERP data.

## Why this project

Built to demonstrate practical application of Python and data analytics
to audit-style analytical procedures — the same category of testing
performed in real Big 4 audit engagements (journal entry testing,
duplicate payment testing, and fraud-risk analytics like Benford's Law),
applied here to a real, publicly available government financial dataset.

## Tech stack

Python, pandas, NumPy, SciPy (statistical testing), Matplotlib
