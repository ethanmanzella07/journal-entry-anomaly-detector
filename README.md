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
  driven by the large
