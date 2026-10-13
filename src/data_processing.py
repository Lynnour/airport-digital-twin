from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


# --------------------------------------------------
# PROJECT DIRECTORIES
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "simulation_results.csv"
RESULTS_DIR = BASE_DIR / "results"

RESULTS_DIR.mkdir(exist_ok=True)


# --------------------------------------------------
# DATASET STRUCTURE
# --------------------------------------------------

STAFFING_COLUMNS = [
    "CheckIn",
    "Security",
    "Passport",
    "Gate"
]

PASSENGER_COLUMNS = [
    "TotalArrivals",
    "CompletedPassengers",
    "RemainingPassengers"
]

METRICS = [
    "AirportTime",
    "WaitingTime",
    "StaffingCost",
    "WaitingCost",
    "TotalCost",
    "TotalArrivals",
    "CompletedPassengers",
    "RemainingPassengers",
    "CompletionRate"
]

EXPECTED_COLUMNS = (
    STAFFING_COLUMNS
    + [metric for metric in METRICS if metric != "CompletionRate"]
)


# --------------------------------------------------
# LOAD AND VALIDATE DATA
# --------------------------------------------------

def load_and_validate_data():
    """Load simulation results and validate their structure."""

    data = pd.read_csv(DATA_FILE)

    # Check required columns
    missing_columns = set(EXPECTED_COLUMNS) - set(data.columns)

    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}")

    # Keep required columns
    data = data[EXPECTED_COLUMNS].copy()

    # Convert columns to numeric values
    for column in EXPECTED_COLUMNS:
        data[column] = pd.to_numeric(
            data[column],
            errors="raise"
        )

    # Check missing and infinite values
    if data.isna().any().any():
        raise ValueError("Dataset contains missing values.")

    if not np.isfinite(data.to_numpy()).all():
        raise ValueError("Dataset contains infinite values.")

    # Validate staffing values
    for column in STAFFING_COLUMNS:

        if (data[column] < 1).any():
            raise ValueError(
                f"Invalid staffing values in {column}."
            )

        if (data[column] % 1 != 0).any():
            raise ValueError(
                f"Non-integer staffing values in {column}."
            )

    # Validate passenger counts
    for column in PASSENGER_COLUMNS:

        if (data[column] < 0).any():
            raise ValueError(
                f"Negative passenger counts in {column}."
            )

        if (data[column] % 1 != 0).any():
            raise ValueError(
                f"Non-integer passenger counts in {column}."
            )

    # Validate passenger-flow balance
    if not (
        data["TotalArrivals"]
        == data["CompletedPassengers"] + data["RemainingPassengers"]
    ).all():

        raise ValueError(
            "Passenger-flow inconsistency: "
            "arrivals != completed + remaining."
        )

    # Validate cost calculation
    cost_difference = (
        data["StaffingCost"]
        + data["WaitingCost"]
        - data["TotalCost"]
    )

    if not np.allclose(cost_difference, 0, atol=1e-6):
        raise ValueError(
            "TotalCost does not match its components."
        )

    # Calculate completion rate for each simulation
    if (data["TotalArrivals"] <= 0).any():
        raise ValueError(
            "Completion rate requires positive total arrivals."
        )

    data["CompletionRate"] = (
        data["CompletedPassengers"]
        / data["TotalArrivals"]
    ) * 100

    return data


# --------------------------------------------------
# STATISTICAL ANALYSIS
# --------------------------------------------------

def summarize_configurations(data):
    """Calculate statistics for every staffing configuration."""

    grouped = data.groupby(
        STAFFING_COLUMNS,
        sort=True
    )

    summary = grouped.size().rename(
        "Replications"
    ).to_frame()

    for metric in METRICS:

        summary[f"Mean_{metric}"] = grouped[metric].mean()

        summary[f"SD_{metric}"] = grouped[metric].std()

        # 95% confidence interval using Student's t-distribution
        n = summary["Replications"]

        t_critical = stats.t.ppf(
            0.975,
            df=n - 1
        )

        margin = (
            t_critical
            * summary[f"SD_{metric}"]
            / np.sqrt(n)
        )

        summary[f"CI_Lower_{metric}"] = (
            summary[f"Mean_{metric}"] - margin
        )

        summary[f"CI_Upper_{metric}"] = (
            summary[f"Mean_{metric}"] + margin
        )

    summary = summary.reset_index()

    # Rank configurations by average total cost
    summary = summary.sort_values(
        by="Mean_TotalCost",
        ascending=True
    ).reset_index(drop=True)

    summary.insert(
        0,
        "CostRank",
        np.arange(1, len(summary) + 1)
    )

    return summary


# --------------------------------------------------
# MAIN AUTOMATED ANALYSIS
# --------------------------------------------------

def main():

    print("\nAIRPORT DIGITAL TWIN — AUTOMATED ANALYSIS")
    print("=" * 55)

    data = load_and_validate_data()

    print(f"Simulation runs loaded: {len(data)}")

    summary = summarize_configurations(data)

    print(f"Staffing configurations: {len(summary)}")

    print(
        f"Replications per configuration: "
        f"{sorted(summary['Replications'].unique())}"
    )

    # Export processed results
    output_file = RESULTS_DIR / "staffing_summary.csv"

    summary.to_csv(
        output_file,
        index=False
    )

    print(f"\nResults saved to: {output_file}")

    # Display five lowest-cost configurations
    display_columns = [
        "CheckIn",
        "Security",
        "Passport",
        "Gate",
        "Mean_AirportTime",
        "Mean_WaitingTime",
        "Mean_TotalArrivals",
        "Mean_CompletedPassengers",
        "Mean_RemainingPassengers",
        "Mean_CompletionRate",
        "Mean_TotalCost"
    ]

    print("\nTOP 5 CONFIGURATIONS BY AVERAGE TOTAL COST")
    print("-" * 55)

    print(
        summary[display_columns]
        .head(5)
        .round(2)
        .to_string(index=False)
    )

    print("\nAnalysis completed successfully!")


if __name__ == "__main__":
    main()