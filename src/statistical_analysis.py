from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "simulation_results.csv"
RESULTS_DIR = BASE_DIR / "results"

STAFFING = ["CheckIn", "Security", "Passport", "Gate"]
METRICS = ["WaitingTime", "AirportTime", "TotalCost", "CompletedPassengers"]


def main():
    RESULTS_DIR.mkdir(exist_ok=True)

    data = pd.read_csv(DATA_FILE)

    # Calculate 95% confidence intervals for every staffing configuration.
    records = []

    for configuration, group in data.groupby(STAFFING):
        record = dict(zip(STAFFING, configuration))
        n = len(group)

        for metric in METRICS:
            values = group[metric].to_numpy(dtype=float)
            mean = np.mean(values)
            standard_error = stats.sem(values)

            margin = stats.t.ppf(0.975, df=n - 1) * standard_error

            record[f"{metric}_Mean"] = mean
            record[f"{metric}_CI_Lower"] = mean - margin
            record[f"{metric}_CI_Upper"] = mean + margin

        records.append(record)

    summary = pd.DataFrame(records)
    summary.to_csv(RESULTS_DIR / "confidence_intervals.csv", index=False)

    print("\nAIRPORT DIGITAL TWIN — STATISTICAL VALIDATION")
    print("=" * 55)
    print(f"Configurations analyzed: {len(summary)}")
    print("Confidence level: 95%")

    # Compare the two best configurations.
    first = data[
        (data[STAFFING] == [7, 2, 2, 1]).all(axis=1)
    ]

    second = data[
        (data[STAFFING] == [7, 2, 2, 2]).all(axis=1)
    ]

    print("\nCOMPARISON: 7-2-2-1 vs 7-2-2-2")
    print("-" * 55)

    for metric in ["WaitingTime", "TotalCost"]:
        result = stats.ttest_ind(
            first[metric],
            second[metric],
            equal_var=False
        )

        print(f"\n{metric}")
        print(f"7-2-2-1 mean: {first[metric].mean():.2f}")
        print(f"7-2-2-2 mean: {second[metric].mean():.2f}")
        print(f"Welch t-test p-value: {result.pvalue:.4f}")

        if result.pvalue < 0.05:
            print("Statistically significant difference (p < 0.05)")
        else:
            print("No statistically significant difference detected (p >= 0.05)")

    print("\nResults saved to: results/confidence_intervals.csv")


if __name__ == "__main__":
    main()