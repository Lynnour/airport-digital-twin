from pathlib import Path
import pandas as pd
import plotly.express as px

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"
SUMMARY_FILE = RESULTS_DIR / "staffing_summary.csv"

CHARTS_DIR = RESULTS_DIR / "charts"
CHARTS_DIR.mkdir(parents=True, exist_ok=True)


def generate_charts():
    df = pd.read_csv(SUMMARY_FILE)

    # Create readable staffing labels
    df["Configuration"] = (
        df["CheckIn"].astype(str) + "-"
        + df["Security"].astype(str) + "-"
        + df["Passport"].astype(str) + "-"
        + df["Gate"].astype(str)
    )

    # Chart 1: Waiting time across configurations
    fig1 = px.bar(
        df.sort_values("Mean_WaitingTime"),
        x="Configuration",
        y="Mean_WaitingTime",
        title="Passenger Waiting Time by Staffing Configuration",
        labels={"Mean_WaitingTime": "Average Waiting Time (minutes)"},
        hover_data=["Mean_AirportTime", "Mean_TotalCost"],
    )

    fig1.update_layout(xaxis_tickangle=-45)

    fig1.write_html(CHARTS_DIR / "waiting_time.html")

    # Chart 2: Operating cost across configurations
    fig2 = px.bar(
        df.sort_values("Mean_TotalCost"),
        x="Configuration",
        y="Mean_TotalCost",
        title="Operating Cost by Staffing Configuration",
        labels={"Mean_TotalCost": "Average Total Operating Cost"},
        hover_data=["Mean_WaitingTime", "Mean_StaffingCost"],
    )

    fig2.update_layout(xaxis_tickangle=-45)

    fig2.write_html(CHARTS_DIR / "operating_cost.html")

    # Chart 3: Cost-service trade-off
    fig3 = px.scatter(
        df,
        x="Mean_WaitingTime",
        y="Mean_TotalCost",
        color="CheckIn",
        size="Mean_StaffingCost",
        hover_name="Configuration",
        hover_data=["Mean_AirportTime", "Replications"],
        title="Airport Staffing: Cost vs. Passenger Waiting Time",
        labels={
            "Mean_WaitingTime": "Average Waiting Time (minutes)",
            "Mean_TotalCost": "Average Total Operating Cost",
        },
    )

    fig3.write_html(CHARTS_DIR / "cost_service_tradeoff.html")

    print("\nINTERACTIVE VISUALIZATIONS GENERATED")
    print("=" * 45)
    print(f"Charts saved to: {CHARTS_DIR}")


if __name__ == "__main__":
    generate_charts()