# Journal Entry Anomaly Detector

Python tool that applies standard audit analytical procedures to a real,
public government payment dataset — the [Texas Education Agency's Check
Register (FY2025)](https://tea.texas.gov/about-tea/agency-finances/check-register/tea-check-register),
covering 61,775 valid transactions paid to school districts and vendors
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

## Results

- **Total transactions analyzed:** 61,775
- **Potential duplicate payment pairs flagged:** 62
- **Round-dollar transactions:** 1,780 (2.9% of total)
- **Weekend postings:** 0 (0.00% of total)
- **Benford's Law chi-square p-value:** < 0.0001 (statistically significant deviation)

### Duplicate payment triage

The 62 flagged pairs were manually reviewed and triaged into three tiers
based on dollar amount and timing:

- **Red flag** (large dollar amount — roughly $50,000+ — OR same/next-day
  repetition regardless of size): 8 pairs, including a $1,249,104.08
  payment to Texas Tech University repeated within 6 days, and a
  $420,685.65 payment to the State Office of Administrative Hearings
  repeated the very next day.
- **Yellow** (moderate, specific amounts with a several-day gap — worth a
  note, not urgent): includes payments like Deer Oaks EAP Services
  ($1,551.25, 2 days apart) and Lewisville ISD ($10,640, 7 days apart).
- **Green** (small, recurring, or clearly routine): the majority of flagged
  pairs — small individual reimbursements and standing recurring vendor
  fees (e.g., Texas Comptroller of Public Accounts' repeated $50/$435
  charges) that repeat by design, not by error.

**Note on data limitations:** this dataset only contains vendor name,
date, and gross amount — no invoice numbers, PO numbers, or department
codes. The triage above reflects which transactions *warrant follow-up
with underlying documentation*, not confirmed errors. A real audit team
would pull invoice-level backup on the red-flagged items next.

### Interpreting the other checks

- **Round-dollar (2.9%):** unremarkable — a small share of transactions
  landing on round numbers is normal and not itself a red flag.
- **Weekend postings (0%):** indicates a well-controlled, business-day-only
  payment processing system — a positive control signal, not a gap.
- **Benford's Law deviation:** the significant deviation is most likely
  driven by the large number of *recurring, fixed-amount* payments in this
  dataset (e.g., the Texas Comptroller's repeated $50 and $435 charges
  visible in the duplicate-payment data above). Government payment
  registers containing many standing/recurring charges naturally deviate
  from Benford's expected distribution, which assumes organically varied
  transaction amounts — this is a structural characteristic of the
  dataset, not evidence of manipulation.

## How to run it

1. Clone this repo and install dependencies:
```bash
   pip install -r requirements.txt
```
2. Download the dataset from TEA's website (not included in this repo due
   to file size):
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
- **Duplicate triage rule:** flagged as high priority if the amount is
  roughly $50,000 or greater, OR if the repeat occurred within 1-2 days
  regardless of amount — since same-day repetition is itself a control-
  failure signal independent of dollar size.
- **Benford's Law caveat:** this test works best on naturally occurring,
  unconstrained transaction amounts. Government payments include many
  recurring fixed amounts, which is a legitimate, explainable limitation
  of applying this test to this type of dataset.
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
