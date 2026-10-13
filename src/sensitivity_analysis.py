from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "simulation_results.csv"
RESULTS_DIR = BASE_DIR / "results"

STAFFING = ["CheckIn", "Security", "Passport", "Gate"]

METRICS = [
    "WaitingTime",
    "TotalCost",
    "CompletedPassengers"
]


def main():

    RESULTS_DIR.mkdir(exist_ok=True)

    data = pd.read_csv(DATA_FILE)

    print("\nAIRPORT DIGITAL TWIN — SENSITIVITY ANALYSIS")
    print("=" * 55)

    # -----------------------------------------
    # 1. Average performance by staffing level
    # -----------------------------------------

    level_results = []

    for station in STAFFING:

        summary = (
            data.groupby(station)[METRICS]
            .mean()
            .reset_index()
        )

        summary["Station"] = station
        summary = summary.rename(columns={station: "StaffingLevel"})

        level_results.append(summary)

    level_summary = pd.concat(level_results, ignore_index=True)

    level_summary.to_csv(
        RESULTS_DIR / "sensitivity_levels.csv",
        index=False
    )

    print("\nAVERAGE PERFORMANCE BY STAFFING LEVEL")
    print("-" * 55)
    print(level_summary.round(2).to_string(index=False))

    # -----------------------------------------
    # 2. Marginal effects of adding one employee
    # -----------------------------------------

    # Average replications within each staffing configuration.
    config_means = (
        data.groupby(STAFFING, as_index=False)[METRICS]
        .mean()
    )

    effects = []

    for station in STAFFING:

        other_stations = [s for s in STAFFING if s != station]

        for _, current in config_means.iterrows():

            next_level = current[station] + 1

            matching = config_means[
                (config_means[station] == next_level)
            ]

            for other in other_stations:
                matching = matching[
                    matching[other] == current[other]
                ]

            if matching.empty:
                continue

            next_config = matching.iloc[0]

            result = {
                "Station": station,
                "FromLevel": int(current[station]),
                "ToLevel": int(next_level)
            }

            for metric in METRICS:
                result[f"Change_{metric}"] = (
                    next_config[metric] - current[metric]
                )

            effects.append(result)

    effects_df = pd.DataFrame(effects)

    effects_df.to_csv(
        RESULTS_DIR / "sensitivity_effects.csv",
        index=False
    )

    # -----------------------------------------
    # 3. Rank stations by impact
    # -----------------------------------------

    impact_summary = (
        effects_df.groupby("Station")
        .agg(
            Average_WaitingTime_Change=("Change_WaitingTime", "mean"),
            Average_TotalCost_Change=("Change_TotalCost", "mean"),
            Average_CompletedPassengers_Change=(
                "Change_CompletedPassengers", "mean"
            )
        )
        .reset_index()
    )

    impact_summary["Absolute_WaitingTime_Impact"] = (
        impact_summary["Average_WaitingTime_Change"].abs()
    )

    impact_summary = impact_summary.sort_values(
        "Absolute_WaitingTime_Impact",
        ascending=False
    )

    impact_summary.to_csv(
        RESULTS_DIR / "sensitivity_ranking.csv",
        index=False
    )

    print("\nSTAFFING SENSITIVITY RANKING")
    print("-" * 55)
    print(
        impact_summary[
            [
                "Station",
                "Average_WaitingTime_Change",
                "Average_TotalCost_Change",
                "Average_CompletedPassengers_Change"
            ]
        ].round(2).to_string(index=False)
    )

    print("\nResults saved to:")
    print(" - results/sensitivity_levels.csv")
    print(" - results/sensitivity_effects.csv")
    print(" - results/sensitivity_ranking.csv")

    print("\nSensitivity analysis completed successfully!")


if __name__ == "__main__":
    main()