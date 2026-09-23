"""
Journal Entry Anomaly Detector
--------------------------------
Applies common audit analytical procedures to a public government
check register dataset (Texas Education Agency, FY2025):

  1. Duplicate payment detection (same vendor, same amount, near dates)
  2. Round-dollar amount flagging
  3. Weekend posting detection
  4. Benford's Law analysis (first-digit distribution test)

Input:  25-cr-report.csv  (download from TEA's website - see README)
Output: anomaly_summary.csv, flagged_duplicates.csv, benford_chart.png

HOW TO RUN:
  pip install pandas matplotlib scipy
  python anomaly_detector.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from collections import Counter

INPUT_FILE = "25-cr-report.csv"

def load_data(path):
    """Load and clean the TEA check register CSV."""
    df = pd.read_csv(
        path,
        header=None,
        names=["Vendor", "Date", "Amount"],
        skiprows=1  # first row is a header artifact in TEA's export
    )
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    df = df.dropna(subset=["Date", "Amount", "Vendor"])
    df = df[df["Amount"] > 0]  # drop zero/negative amounts (reversals, credits)
    print(f"Loaded {len(df):,} valid transactions.")
    return df

def flag_duplicates(df):
    """
    Flag potential duplicate payments: same vendor + same amount,
    posted within 7 days of each other. This mirrors the classic
    audit test for double-paid invoices.
    """
    df_sorted = df.sort_values(["Vendor", "Amount", "Date"])
    dup_flags = []

    for (vendor, amount), group in df_sorted.groupby(["Vendor", "Amount"]):
        if len(group) < 2:
            continue
        dates = group["Date"].sort_values().tolist()
        for i in range(1, len(dates)):
            gap = (dates[i] - dates[i-1]).days
            if gap <= 7:
                dup_flags.append({
                    "Vendor": vendor,
                    "Amount": amount,
                    "Date1": dates[i-1].date(),
                    "Date2": dates[i].date(),
                    "DaysApart": gap
                })

    dup_df = pd.DataFrame(dup_flags)
    print(f"\nDuplicate payment check: {len(dup_df)} potential duplicate pairs flagged "
          f"(same vendor, same amount, within 7 days).")
    return dup_df

def flag_round_dollar(df):
    """Flag transactions that are suspiciously round (end in 000 or 00)."""
    round_thousand = df[df["Amount"] % 1000 == 0]
    round_hundred = df[(df["Amount"] % 100 == 0) & (df["Amount"] % 1000 != 0)]
    print(f"\nRound-dollar check:")
    print(f"  {len(round_thousand):,} transactions are round to the nearest $1,000")
    print(f"  {len(round_hundred):,} more are round to the nearest $100")
    print(f"  ({len(round_thousand) + len(round_hundred):,} of {len(df):,} total "
          f"= {(len(round_thousand)+len(round_hundred))/len(df):.1%} of all transactions)")
    return round_thousand

def flag_weekend_postings(df):
    """Flag transactions posted on a Saturday or Sunday - unusual for routine processing."""
    df = df.copy()
    df["Weekday"] = df["Date"].dt.dayofweek  # Monday=0 ... Sunday=6
    weekend = df[df["Weekday"] >= 5]
    print(f"\nWeekend posting check: {len(weekend):,} of {len(df):,} transactions "
          f"({len(weekend)/len(df):.2%}) were posted on a Saturday or Sunday.")
    return weekend

def benford_analysis(df):
    """
    Benford's Law: in naturally occurring financial datasets, the leading
    digit 1 appears ~30% of the time, 2 appears ~18%, etc. Significant
    deviation can indicate manipulated or fabricated numbers.
    """
    leading_digits = df["Amount"].apply(
        lambda x: int(str(abs(x)).lstrip("0.")[0]) if str(abs(x)).lstrip("0.") else None
    ).dropna()
    leading_digits = leading_digits[(leading_digits >= 1) & (leading_digits <= 9)]

    observed_counts = Counter(leading_digits)
    total = sum(observed_counts.values())
    observed_pct = [observed_counts.get(d, 0) / total for d in range(1, 10)]

    # Benford's expected distribution
    expected_pct = [np.log10(1 + 1/d) for d in range(1, 10)]

    # Chi-square goodness of fit test
    observed_freq = [observed_counts.get(d, 0) for d in range(1, 10)]
    expected_freq = [p * total for p in expected_pct]
    chi2, p_value = stats.chisquare(observed_freq, expected_freq)

    print(f"\nBenford's Law analysis:")
    print(f"  Chi-square statistic: {chi2:.2f}, p-value: {p_value:.4f}")
    if p_value < 0.05:
        print("  Result: Statistically significant deviation from Benford's "
              "distribution (p < 0.05) - worth investigating further.")
    else:
        print("  Result: No statistically significant deviation from Benford's "
              "distribution - consistent with naturally occurring transaction data.")

    # Chart
    digits = list(range(1, 10))
    fig, ax = plt.subplots(figsize=(8, 5))
    width = 0.35
    ax.bar([d - width/2 for d in digits], observed_pct, width, label="Observed", color="#2E86AB")
    ax.bar([d + width/2 for d in digits], expected_pct, width, label="Benford's Expected", color="#A23B72")
    ax.set_xlabel("Leading Digit")
    ax.set_ylabel("Proportion")
    ax.set_title("Benford's Law: Observed vs. Expected Leading Digit Distribution")
    ax.set_xticks(digits)
    ax.legend()
    plt.tight_layout()
    plt.savefig("benford_chart.png", dpi=150)
    print("  Saved chart to benford_chart.png")

    return chi2, p_value

def main():
    df = load_data(INPUT_FILE)

    dup_df = flag_duplicates(df)
    round_df = flag_round_dollar(df)
    weekend_df = flag_weekend_postings(df)
    chi2, p_value = benford_analysis(df)

    # Save outputs
    if not dup_df.empty:
        dup_df.to_csv("flagged_duplicates.csv", index=False)

    summary = pd.DataFrame([{
        "TotalTransactions": len(df),
        "PotentialDuplicatePairs": len(dup_df),
        "RoundThousandDollarTxns": len(round_df),
        "WeekendPostings": len(weekend_df),
        "BenfordChiSquare": round(chi2, 2),
        "BenfordPValue": round(p_value, 4),
    }])
    summary.to_csv("anomaly_summary.csv", index=False)
    print("\nSaved anomaly_summary.csv - this is your headline results table.")
    print("Done. Review flagged_duplicates.csv and benford_chart.png next.")

if __name__ == "__main__":
    main()
