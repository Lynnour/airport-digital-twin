from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Airport Digital Twin",
    page_icon="✈️",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "results" / "staffing_summary.csv"


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():
    return pd.read_csv(DATA_FILE)


df = load_data()

required_columns = [
    "Mean_TotalArrivals",
    "Mean_CompletedPassengers",
    "Mean_RemainingPassengers",
    "Mean_CompletionRate",
    "CI_Lower_CompletionRate"
]

missing = set(required_columns) - set(df.columns)

if missing:
    st.error(
        "Missing passenger-flow statistics. "
        "Run data_processing.py again."
    )
    st.stop()


st.title("✈️ Airport Digital Twin")
st.subheader("Passenger Flow & Staffing Optimization")

st.caption(
    "Simulation-based decision-support system | "
    "Peak arrival rate: 1.3 passengers/minute | "
    "Simulation horizon: 480 minutes"
)

st.divider()


# --------------------------------------------------
# SIDEBAR — USER CONSTRAINTS
# --------------------------------------------------

st.sidebar.header("⚙️ Optimization Settings")

max_waiting = st.sidebar.slider(
    "Maximum average waiting time (min)",
    min_value=1,
    max_value=100,
    value=10
)

max_airport = st.sidebar.slider(
    "Maximum average airport time (min)",
    min_value=10,
    max_value=150,
    value=35
)

use_completion_constraint = st.sidebar.checkbox(
    "Require minimum passenger completion rate",
    value=False
)

min_completion = st.sidebar.slider(
    "Minimum completion rate (%)",
    min_value=50,
    max_value=100,
    value=90,
    disabled=not use_completion_constraint
)

st.sidebar.caption(
    "When enabled, the completion-rate requirement "
    "uses the lower bound of its 95% confidence interval."
)

st.sidebar.subheader("Maximum Available Staff")

max_checkin = st.sidebar.slider(
    "Check-in agents",
    min_value=4,
    max_value=7,
    value=7
)

max_security = st.sidebar.slider(
    "Security officers",
    min_value=1,
    max_value=2,
    value=2
)

max_passport = st.sidebar.slider(
    "Passport officers",
    min_value=1,
    max_value=2,
    value=2
)

max_gate = st.sidebar.slider(
    "Gate agents",
    min_value=1,
    max_value=2,
    value=2
)


# --------------------------------------------------
# FILTER FEASIBLE CONFIGURATIONS
# --------------------------------------------------

df["Configuration"] = (
    df["CheckIn"].astype(str) + "-"
    + df["Security"].astype(str) + "-"
    + df["Passport"].astype(str) + "-"
    + df["Gate"].astype(str)
)

df["Feasible"] = (
    (df["CI_Upper_WaitingTime"] <= max_waiting)
    & (df["CI_Upper_AirportTime"] <= max_airport)
    & (df["CheckIn"] <= max_checkin)
    & (df["Security"] <= max_security)
    & (df["Passport"] <= max_passport)
    & (df["Gate"] <= max_gate)
)

if use_completion_constraint:
    df["Feasible"] = (
        df["Feasible"]
        & (df["CI_Lower_CompletionRate"] >= min_completion)
    )

feasible = df[df["Feasible"]].sort_values(
    "Mean_TotalCost"
)


# --------------------------------------------------
# OVERVIEW METRICS
# --------------------------------------------------

st.header("📊 Optimization Overview")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Configurations Evaluated",
    len(df)
)

col2.metric(
    "Feasible Configurations",
    len(feasible)
)

col3.metric(
    "Simulation Replications",
    int(df["Replications"].sum())
)

st.divider()


# --------------------------------------------------
# OPTIMAL CONFIGURATION
# --------------------------------------------------

st.header("🏆 Recommended Staffing Configuration")

if not feasible.empty:

    best = feasible.iloc[0]

    st.success(
        f"Recommended configuration: {best['Configuration']}"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Check-in Agents", int(best["CheckIn"]))
    c2.metric("Security Officers", int(best["Security"]))
    c3.metric("Passport Officers", int(best["Passport"]))
    c4.metric("Gate Agents", int(best["Gate"]))

    st.subheader("Expected Performance")

    p1, p2, p3 = st.columns(3)

    p1.metric(
        "Average Waiting Time",
        f"{best['Mean_WaitingTime']:.2f} min"
    )

    p2.metric(
        "Average Airport Time",
        f"{best['Mean_AirportTime']:.2f} min"
    )

    p3.metric(
        "Average Total Cost",
        f"{best['Mean_TotalCost']:,.2f}"
    )

    st.subheader("Passenger Flow Performance")

    f1, f2, f3, f4 = st.columns(4)

    f1.metric(
        "Average Arrivals",
        f"{best['Mean_TotalArrivals']:.0f}"
    )

    f2.metric(
        "Average Completed",
        f"{best['Mean_CompletedPassengers']:.0f}"
    )

    f3.metric(
        "Average Remaining",
        f"{best['Mean_RemainingPassengers']:.0f}"
    )

    f4.metric(
        "Completion Rate",
        f"{best['Mean_CompletionRate']:.1f}%"
    )

    st.caption(
        "Passenger counts and completion rate are averages "
        "across simulation replications. Remaining passengers "
        "have not completed their journey at the 480-minute cutoff."
    )

else:

    st.warning(
        "No simulated staffing configuration satisfies "
        "the selected constraints."
    )

st.divider()


# --------------------------------------------------
# COST-SERVICE TRADE-OFF
# --------------------------------------------------

st.header("📈 Cost vs. Passenger Waiting Time")

fig = px.scatter(
    df,
    x="Mean_WaitingTime",
    y="Mean_TotalCost",
    color="Feasible",
    hover_name="Configuration",
    hover_data=[
        "Mean_AirportTime",
        "Mean_StaffingCost",
        "Mean_WaitingCost",
        "Mean_CompletionRate",
        "Mean_RemainingPassengers"
    ],
    title="Staffing Configurations: Cost-Service Trade-off",
    labels={
        "Mean_WaitingTime": "Average Waiting Time (minutes)",
        "Mean_TotalCost": "Average Total Cost (model units)"
    }
)

fig.add_vline(
    x=max_waiting,
    line_dash="dash",
    annotation_text="Waiting-Time Target"
)

st.plotly_chart(fig, width="stretch")


# --------------------------------------------------
# PASSENGER COMPLETION ANALYSIS
# --------------------------------------------------

st.divider()

st.header("👥 Passenger Completion Analysis")

st.write(
    "Evaluate how staffing decisions affect the percentage "
    "of passengers completing their airport journey within "
    "the eight-hour simulation."
)

completion_fig = px.bar(
    df.sort_values("Mean_CompletionRate", ascending=False),
    x="Configuration",
    y="Mean_CompletionRate",
    color="Feasible",
    hover_data=[
        "Mean_TotalArrivals",
        "Mean_CompletedPassengers",
        "Mean_RemainingPassengers"
    ],
    title="Passenger Completion Rate by Staffing Configuration",
    labels={
        "Configuration": "Staffing Configuration",
        "Mean_CompletionRate": "Average Completion Rate (%)"
    }
)

completion_fig.update_layout(
    xaxis_tickangle=-45
)

st.plotly_chart(
    completion_fig,
    width="stretch"
)


# --------------------------------------------------
# REMAINING PASSENGERS ANALYSIS
# --------------------------------------------------

st.subheader("Passengers Remaining at Simulation End")

remaining_fig = px.bar(
    df.sort_values("Mean_RemainingPassengers"),
    x="Configuration",
    y="Mean_RemainingPassengers",
    color="Feasible",
    title="Average Remaining Passengers by Configuration",
    labels={
        "Configuration": "Staffing Configuration",
        "Mean_RemainingPassengers": "Average Remaining Passengers"
    }
)

remaining_fig.update_layout(
    xaxis_tickangle=-45
)

st.plotly_chart(
    remaining_fig,
    width="stretch"
)

st.caption(
    "Remaining passengers represent unfinished journeys "
    "at the simulation cutoff, not necessarily passengers "
    "who would never complete the process."
)


# --------------------------------------------------
# CONFIGURATION COMPARISON
# --------------------------------------------------

st.divider()

st.header("📋 Staffing Configuration Comparison")

display_columns = [
    "Configuration",
    "Mean_WaitingTime",
    "Mean_AirportTime",
    "Mean_TotalArrivals",
    "Mean_CompletedPassengers",
    "Mean_RemainingPassengers",
    "Mean_CompletionRate",
    "Mean_StaffingCost",
    "Mean_WaitingCost",
    "Mean_TotalCost",
    "Feasible"
]

st.dataframe(
    df[display_columns]
    .sort_values("Mean_TotalCost")
    .round(2),
    width="stretch",
    hide_index=True
)

st.caption(
    "Feasibility uses the upper 95% confidence bounds "
    "for waiting and airport times. An optional completion "
    "requirement uses the lower 95% confidence bound. "
    "Cost values are simulation-model units, not calibrated "
    "currency. Recommendations are limited to the "
    "simulated configurations."
)


# --------------------------------------------------
# STAFFING SCENARIO COMPARISON
# --------------------------------------------------

st.divider()

st.header("🔍 Staffing Scenario Comparison")

st.write(
    "Compare two simulated staffing configurations "
    "to evaluate differences in passenger service, "
    "completion rates, and operating costs."
)

configurations = sorted(df["Configuration"].unique())

col_a, col_b = st.columns(2)

with col_a:
    scenario_a = st.selectbox(
        "Scenario A",
        configurations,
        index=(
            configurations.index("6-2-2-2")
            if "6-2-2-2" in configurations else 0
        )
    )

with col_b:
    scenario_b = st.selectbox(
        "Scenario B",
        configurations,
        index=(
            configurations.index("7-2-2-2")
            if "7-2-2-2" in configurations else len(configurations) - 1
        )
    )

a = df[df["Configuration"] == scenario_a].iloc[0]
b = df[df["Configuration"] == scenario_b].iloc[0]


# --------------------------------------------------
# SCENARIO COMPARISON TABLE
# --------------------------------------------------

comparison = pd.DataFrame({
    "Metric": [
        "Check-in Agents",
        "Security Officers",
        "Passport Officers",
        "Gate Agents",
        "Average Waiting Time (min)",
        "Average Airport Time (min)",
        "Average Arrivals",
        "Average Completed Passengers",
        "Average Remaining Passengers",
        "Completion Rate (%)",
        "Average Staffing Cost",
        "Average Waiting Cost",
        "Average Total Cost"
    ],

    "Scenario A": [
        a["CheckIn"],
        a["Security"],
        a["Passport"],
        a["Gate"],
        a["Mean_WaitingTime"],
        a["Mean_AirportTime"],
        a["Mean_TotalArrivals"],
        a["Mean_CompletedPassengers"],
        a["Mean_RemainingPassengers"],
        a["Mean_CompletionRate"],
        a["Mean_StaffingCost"],
        a["Mean_WaitingCost"],
        a["Mean_TotalCost"]
    ],

    "Scenario B": [
        b["CheckIn"],
        b["Security"],
        b["Passport"],
        b["Gate"],
        b["Mean_WaitingTime"],
        b["Mean_AirportTime"],
        b["Mean_TotalArrivals"],
        b["Mean_CompletedPassengers"],
        b["Mean_RemainingPassengers"],
        b["Mean_CompletionRate"],
        b["Mean_StaffingCost"],
        b["Mean_WaitingCost"],
        b["Mean_TotalCost"]
    ]
})

comparison["Difference (B - A)"] = (
    comparison["Scenario B"] - comparison["Scenario A"]
)

st.dataframe(
    comparison.round(2),
    width="stretch",
    hide_index=True
)


# --------------------------------------------------
# COMPARISON CHARTS
# --------------------------------------------------

chart_data = pd.DataFrame({
    "Scenario": [scenario_a, scenario_b],

    "Average Waiting Time": [
        a["Mean_WaitingTime"],
        b["Mean_WaitingTime"]
    ],

    "Average Total Cost": [
        a["Mean_TotalCost"],
        b["Mean_TotalCost"]
    ],

    "Completion Rate": [
        a["Mean_CompletionRate"],
        b["Mean_CompletionRate"]
    ],

    "Remaining Passengers": [
        a["Mean_RemainingPassengers"],
        b["Mean_RemainingPassengers"]
    ]
})

fig_wait = px.bar(
    chart_data,
    x="Scenario",
    y="Average Waiting Time",
    title="Passenger Waiting Time Comparison",
    text_auto=".2f"
)

st.plotly_chart(
    fig_wait,
    width="stretch"
)

fig_cost = px.bar(
    chart_data,
    x="Scenario",
    y="Average Total Cost",
    title="Total Operating Cost Comparison",
    text_auto=".2f"
)

st.plotly_chart(
    fig_cost,
    width="stretch"
)

fig_completion = px.bar(
    chart_data,
    x="Scenario",
    y="Completion Rate",
    title="Passenger Completion Rate Comparison",
    text_auto=".1f"
)

st.plotly_chart(
    fig_completion,
    width="stretch"
)

fig_remaining = px.bar(
    chart_data,
    x="Scenario",
    y="Remaining Passengers",
    title="Remaining Passengers Comparison",
    text_auto=".1f"
)

st.plotly_chart(
    fig_remaining,
    width="stretch"
)


# --------------------------------------------------
# AUTOMATIC COMPARISON INSIGHTS
# --------------------------------------------------

waiting_difference = (
    b["Mean_WaitingTime"] - a["Mean_WaitingTime"]
)

cost_difference = (
    b["Mean_TotalCost"] - a["Mean_TotalCost"]
)

completion_difference = (
    b["Mean_CompletionRate"] - a["Mean_CompletionRate"]
)

remaining_difference = (
    b["Mean_RemainingPassengers"]
    - a["Mean_RemainingPassengers"]
)

st.subheader("💡 Comparison Insight")

if waiting_difference < 0:
    st.success(
        f"Scenario B reduces average passenger waiting time "
        f"by {abs(waiting_difference):.2f} minutes "
        f"compared with Scenario A."
    )

elif waiting_difference > 0:
    st.warning(
        f"Scenario B increases average passenger waiting time "
        f"by {waiting_difference:.2f} minutes "
        f"compared with Scenario A."
    )

else:
    st.info(
        "Both scenarios have the same average waiting time."
    )


if cost_difference < 0:
    st.success(
        f"Scenario B reduces average total cost by "
        f"{abs(cost_difference):,.2f} model cost units."
    )

elif cost_difference > 0:
    st.warning(
        f"Scenario B increases average total cost by "
        f"{cost_difference:,.2f} model cost units."
    )

else:
    st.info(
        "Both scenarios have the same average total cost."
    )


if completion_difference > 0:
    st.success(
        f"Scenario B improves the average passenger completion "
        f"rate by {completion_difference:.2f} percentage points."
    )

elif completion_difference < 0:
    st.warning(
        f"Scenario B reduces the average passenger completion "
        f"rate by {abs(completion_difference):.2f} percentage points."
    )

else:
    st.info(
        "Both scenarios have the same average completion rate."
    )


if remaining_difference < 0:
    st.success(
        f"Scenario B leaves an average of "
        f"{abs(remaining_difference):.1f} fewer passengers "
        f"in the airport at the simulation cutoff."
    )

elif remaining_difference > 0:
    st.warning(
        f"Scenario B leaves an average of "
        f"{remaining_difference:.1f} more passengers "
        f"in the airport at the simulation cutoff."
    )

else:
    st.info(
        "Both scenarios have the same average number "
        "of remaining passengers."
    )

# --------------------------------------------------
# STATISTICAL VALIDATION
# --------------------------------------------------

st.divider()
st.header("📐 Statistical Validation")
st.write(
    "Explore 95% confidence intervals across eight replications per "
    "configuration. Intervals describe uncertainty in estimated mean performance."
)

CI_FILE = BASE_DIR / "results" / "confidence_intervals.csv"
if CI_FILE.exists():
    ci_df = pd.read_csv(CI_FILE)
    ci_df["Configuration"] = (
        ci_df["CheckIn"].astype(str) + "-"
        + ci_df["Security"].astype(str) + "-"
        + ci_df["Passport"].astype(str) + "-"
        + ci_df["Gate"].astype(str)
    )
    ci_metric = st.selectbox(
        "Confidence interval metric",
        ["WaitingTime", "AirportTime", "TotalCost", "CompletedPassengers"],
        format_func=lambda m: {
            "WaitingTime": "Waiting time (minutes)",
            "AirportTime": "Airport time (minutes)",
            "TotalCost": "Total cost (model units)",
            "CompletedPassengers": "Completed passengers",
        }[m],
    )
    ci_chart_df = ci_df.sort_values(f"{ci_metric}_Mean").copy()
    ci_chart_df["ErrorPlus"] = (
        ci_chart_df[f"{ci_metric}_CI_Upper"] - ci_chart_df[f"{ci_metric}_Mean"]
    ).clip(lower=0)
    ci_chart_df["ErrorMinus"] = (
        ci_chart_df[f"{ci_metric}_Mean"] - ci_chart_df[f"{ci_metric}_CI_Lower"]
    ).clip(lower=0)
    ci_fig = px.scatter(
        ci_chart_df,
        x="Configuration",
        y=f"{ci_metric}_Mean",
        error_y="ErrorPlus",
        error_y_minus="ErrorMinus",
        title=f"95% Confidence Intervals — {ci_metric}",
        labels={f"{ci_metric}_Mean": ci_metric},
    )
    ci_fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(ci_fig, width="stretch")
    st.dataframe(
        ci_df[[
            "Configuration", f"{ci_metric}_Mean",
            f"{ci_metric}_CI_Lower", f"{ci_metric}_CI_Upper",
        ]].round(2),
        width="stretch", hide_index=True,
    )
    st.subheader("Comparison of the two lowest-cost configurations")
    st.info(
        "7-2-2-1 vs 7-2-2-2: Welch t-test p = 0.9913 for waiting time "
        "and p = 0.9907 for total cost. Neither comparison showed a "
        "statistically significant difference at the 5% level. "
        "These tests assume independent replications; check the simulation "
        "random-seed design before treating the p-values as definitive."
    )
else:
    st.warning("Confidence interval file missing. Run main.py to generate it.")


# --------------------------------------------------
# STAFFING SENSITIVITY
# --------------------------------------------------

st.divider()
st.header("🎛️ Staffing Sensitivity Analysis")
st.caption(
    "Changes are averaged across tested staffing combinations. "
    "They are not predictions for untested staffing levels."
)

LEVEL_FILE = BASE_DIR / "results" / "sensitivity_levels.csv"
RANK_FILE = BASE_DIR / "results" / "sensitivity_ranking.csv"
EFFECTS_FILE = BASE_DIR / "results" / "sensitivity_effects.csv"

if LEVEL_FILE.exists() and RANK_FILE.exists():
    levels = pd.read_csv(LEVEL_FILE)
    ranking = pd.read_csv(RANK_FILE)
    sensitivity_metric = st.selectbox(
        "Sensitivity metric",
        ["WaitingTime", "TotalCost", "CompletedPassengers"],
        format_func=lambda m: {
            "WaitingTime": "Average waiting time (minutes)",
            "TotalCost": "Average total cost (model units)",
            "CompletedPassengers": "Average completed passengers",
        }[m],
    )
    station = st.selectbox(
        "Station", ["CheckIn", "Security", "Passport", "Gate"],
        format_func=lambda s: {
            "CheckIn": "Check-in", "Security": "Security",
            "Passport": "Passport control", "Gate": "Boarding gate",
        }[s],
    )
    station_levels = levels[levels["Station"] == station].sort_values("StaffingLevel")
    sensitivity_fig = px.line(
        station_levels, x="StaffingLevel", y=sensitivity_metric,
        markers=True,
        title=f"{station}: {sensitivity_metric} by staffing level",
        labels={"StaffingLevel": "Number of staff"},
    )
    sensitivity_fig.update_xaxes(dtick=1)
    st.plotly_chart(sensitivity_fig, width="stretch")
    st.subheader("Average marginal impact of one additional employee")
    st.dataframe(ranking.round(2), width="stretch", hide_index=True)
    if EFFECTS_FILE.exists():
        with st.expander("Inspect matched staffing changes"):
            effects_df = pd.read_csv(EFFECTS_FILE)
            st.dataframe(effects_df.round(2), width="stretch", hide_index=True)
    st.caption(
        "Passport control has the largest average waiting-time sensitivity "
        "over the tested combinations. The gate has the smallest. "
        "Interpret these as scenario comparisons, not proof of causal "
        "effects under every possible demand condition."
    )
else:
    st.warning("Sensitivity files missing. Run main.py to generate them.")


# --------------------------------------------------
# ECONOMIC SENSITIVITY ANALYSIS
# --------------------------------------------------

st.divider()
st.header("💰 Economic Sensitivity Analysis")
st.write(
    "Explore how hypothetical employee-hour and passenger-waiting costs "
    "change total operating costs and staffing recommendations. "
    "The same simulation outcomes are used in every scenario."
)

ECONOMIC_FILE = BASE_DIR / "results" / "economic_sensitivity.csv"

if ECONOMIC_FILE.exists():
    economic_df = pd.read_csv(ECONOMIC_FILE)
    economic_df["Configuration"] = (
        economic_df["CheckIn"].astype(str) + "-"
        + economic_df["Security"].astype(str) + "-"
        + economic_df["Passport"].astype(str) + "-"
        + economic_df["Gate"].astype(str)
    )

    # Apply the dashboard's CURRENT service and staffing constraints.
    # These constraints are based on simulation performance, which does
    # not change when only cost rates are adjusted.
    economic_df = economic_df.merge(
        df[["Configuration", "Feasible"]],
        on="Configuration",
        how="left",
        validate="many_to_one",
    )
    economic_df["Feasible"] = economic_df["Feasible"].fillna(False)

    scenarios = list(economic_df["Scenario"].drop_duplicates())
    selected_economic_scenario = st.selectbox(
        "Economic cost scenario", scenarios, key="economic_scenario"
    )
    economic_selected = economic_df[
        economic_df["Scenario"] == selected_economic_scenario
    ].copy()
    economic_feasible = economic_selected[
        economic_selected["Feasible"]
    ].sort_values("Mean_TotalCost")

    rate_row = economic_selected.iloc[0]
    st.caption(
        f"Employee-hour cost: {rate_row['StaffCostRate']:g} model units | "
        f"Passenger waiting-minute cost: {rate_row['WaitingCostRate']:g} model units. "
        "These are illustrative rates, not measured airport prices."
    )

    if economic_feasible.empty:
        st.warning(
            "No configuration meets the current sidebar service-level "
            "and staffing constraints in this scenario."
        )
    else:
        economic_best = economic_feasible.iloc[0]
        st.success(
            "Lowest-cost feasible staffing: "
            f"{economic_best['Configuration']}"
        )
        ec1, ec2, ec3 = st.columns(3)
        ec1.metric("Adjusted total cost", f"{economic_best['Mean_TotalCost']:,.2f}")
        ec2.metric("Staffing cost", f"{economic_best['Mean_StaffingCost']:,.2f}")
        ec3.metric("Passenger waiting cost", f"{economic_best['Mean_WaitingCost']:,.2f}")

        breakdown = pd.DataFrame({
            "Cost component": ["Staffing", "Passenger waiting"],
            "Mean cost": [
                economic_best["Mean_StaffingCost"],
                economic_best["Mean_WaitingCost"],
            ],
        })
        breakdown_fig = px.bar(
            breakdown,
            x="Cost component",
            y="Mean cost",
            title="Cost breakdown — lowest-cost feasible configuration",
            labels={"Mean cost": "Average cost (model units)"},
        )
        st.plotly_chart(breakdown_fig, width="stretch")

    economic_chart_data = economic_selected.sort_values("Mean_TotalCost")
    economic_fig = px.bar(
        economic_chart_data,
        x="Configuration",
        y="Mean_TotalCost",
        color="Feasible",
        hover_data=["Mean_StaffingCost", "Mean_WaitingCost", "Mean_WaitingTime"],
        title="Adjusted operating cost across all tested configurations",
        labels={
            "Configuration": "Staffing configuration",
            "Mean_TotalCost": "Average cost (model units)",
        },
    )
    economic_fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(economic_fig, width="stretch")

    st.subheader("Lowest-cost feasible configuration by economic scenario")
    scenario_summary = []
    for scenario_name, group in economic_df.groupby("Scenario", sort=False):
        eligible = group[group["Feasible"]]
        if eligible.empty:
            scenario_summary.append({
                "Scenario": scenario_name,
                "Recommended staffing": "None feasible",
                "Mean total cost": None,
                "Mean waiting time (min)": None,
            })
        else:
            winner = eligible.loc[eligible["Mean_TotalCost"].idxmin()]
            scenario_summary.append({
                "Scenario": scenario_name,
                "Recommended staffing": winner["Configuration"],
                "Mean total cost": winner["Mean_TotalCost"],
                "Mean waiting time (min)": winner["Mean_WaitingTime"],
            })
    st.dataframe(
        pd.DataFrame(scenario_summary).round(2),
        width="stretch",
        hide_index=True,
    )
    st.caption(
        "Feasibility follows the current sidebar constraints, including "
        "confidence-interval limits and any optional completion-rate requirement. "
        "Cost comparisons are estimates from eight replications per configuration; "
        "small differences may not be statistically significant."
    )
else:
    st.warning("Economic sensitivity file missing. Run main.py to generate it.")


# --------------------------------------------------
# RAW SIMULATION DATA
# --------------------------------------------------

st.divider()
st.header("🗂️ Simulation Data Explorer")
RAW_FILE = BASE_DIR / "data" / "simulation_results.csv"
if RAW_FILE.exists():
    raw_df = pd.read_csv(RAW_FILE)
    st.caption(f"{len(raw_df)} simulation runs available for inspection.")
    filter_config = st.selectbox(
        "Filter by staffing configuration",
        ["All configurations"] + sorted(df["Configuration"].unique().tolist()),
    )
    if filter_config != "All configurations":
        selected = [int(value) for value in filter_config.split("-")]
        for column, value in zip(["CheckIn", "Security", "Passport", "Gate"], selected):
            raw_df = raw_df[raw_df[column] == value]
    st.dataframe(raw_df, width="stretch", hide_index=True)
    st.download_button(
        "Download displayed simulation data (CSV)",
        data=raw_df.to_csv(index=False).encode("utf-8"),
        file_name="airport_simulation_filtered.csv",
        mime="text/csv",
    )
else:
    st.warning("Raw simulation file missing from data/simulation_results.csv.")
