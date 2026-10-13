from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "simulation_results.csv"
RESULTS_DIR = BASE_DIR / "results"

STAFFING = ["CheckIn", "Security", "Passport", "Gate"]

SCENARIOS = {
    "Baseline": (1, 1),
    "Higher Staffing Cost": (5, 1),
    "Higher Waiting Cost": (1, 2),
    "Balanced Cost": (5, 0.5),
    "Very High Staffing Cost": (20, 1),
}


def main():
    RESULTS_DIR.mkdir(exist_ok=True)

    data = pd.read_csv(DATA_FILE)

    results = []

    for scenario, (staff_rate, waiting_rate) in SCENARIOS.items():

        scenario_data = data.copy()

        # Recalculate staffing cost using the 8-hour simulation horizon.
        scenario_data["AdjustedStaffingCost"] = (
            scenario_data[STAFFING].sum(axis=1)
            * 8
            * staff_rate
        )

        # Original waiting cost uses a rate of 1 cost unit/minute.
        scenario_data["AdjustedWaitingCost"] = (
            scenario_data["WaitingCost"] * waiting_rate
        )

        scenario_data["AdjustedTotalCost"] = (
            scenario_data["AdjustedStaffingCost"]
            + scenario_data["AdjustedWaitingCost"]
        )

        summary = (
            scenario_data.groupby(STAFFING, as_index=False)
            .agg(
                Mean_TotalCost=("AdjustedTotalCost", "mean"),
                Mean_StaffingCost=("AdjustedStaffingCost", "mean"),
                Mean_WaitingCost=("AdjustedWaitingCost", "mean"),
                Mean_WaitingTime=("WaitingTime", "mean"),
                Mean_AirportTime=("AirportTime", "mean"),
            )
        )

        summary["Scenario"] = scenario
        summary["StaffCostRate"] = staff_rate
        summary["WaitingCostRate"] = waiting_rate

        results.append(summary)

    all_results = pd.concat(results, ignore_index=True)

    all_results.to_csv(
        RESULTS_DIR / "economic_sensitivity.csv",
        index=False
    )

    print("\nAIRPORT DIGITAL TWIN — ECONOMIC SENSITIVITY")
    print("=" * 60)

    for scenario in SCENARIOS:

        subset = all_results[
            all_results["Scenario"] == scenario
        ]

        best = subset.loc[subset["Mean_TotalCost"].idxmin()]

        configuration = "-".join(
            str(int(best[col])) for col in STAFFING
        )

        print(f"\nScenario: {scenario}")
        print(f"Lowest-cost configuration: {configuration}")
        print(f"Average total cost: {best['Mean_TotalCost']:.2f}")
        print(f"Average waiting time: {best['Mean_WaitingTime']:.2f} min")

    print("\nResults saved to: results/economic_sensitivity.csv")


if __name__ == "__main__":
    main()