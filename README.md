# Airport Digital Twin
### Simulation-Based Staffing Optimization & Decision Support

An industrial engineering project integrating discrete-event simulation,
statistical analysis, optimization, and interactive data visualization
to evaluate airport passenger flow and staffing decisions.

## Project Overview

Airport operations involve multiple interconnected service stations.
Insufficient staffing can create congestion, increase passenger waiting
times, and reduce operational efficiency.

This project develops a simulation-based decision-support framework
to evaluate staffing configurations and identify cost-effective
resource allocations while considering passenger service levels.

## Technologies

- AnyLogic — Discrete-event simulation
- Python — Data processing and optimization
- Pandas & NumPy — Data analysis
- SciPy — Statistical analysis
- Plotly — Interactive visualizations
- Streamlit — Decision-support dashboard

## Simulation Model

The airport model represents the following passenger-processing stages:

1. Check-in
2. Security screening
3. Passport control (international passengers)
4. Boarding
5. Passenger exit

The model incorporates passenger arrivals, service times, resource
capacities, queueing behavior, and passenger waiting times.

### Experimental Design

- Simulation duration: 480 minutes (8 hours)
- Passenger arrival rate: 1.3 passengers/minute
- Staffing configurations: 32
- Replications per configuration: 8
- Total simulation runs: 256

## Optimization Framework

The optimization framework evaluates simulated staffing configurations
using operating costs and passenger service-level constraints.

The objective is to minimize:

Total Operating Cost = Staffing Cost + Passenger Waiting Cost

The framework evaluates:

- Average passenger waiting time
- Average airport processing time
- Passenger throughput
- Staffing cost
- Waiting cost
- Total operating cost

The optimization is limited to the staffing configurations included
in the simulation experiments.

## Statistical Analysis

The project incorporates:

- Replication-based performance analysis
- 95% confidence intervals
- Statistical comparison of staffing configurations
- Staffing sensitivity analysis
- Economic sensitivity analysis

These methods support uncertainty-aware comparisons and help assess
how resource allocation and cost assumptions influence recommendations.

## Key Findings

Under the baseline assumptions and tested configurations:

**Lowest estimated-cost feasible staffing allocation:**

| Station | Employees |
|---------|-----------|
| Check-in | 7 |
| Security | 2 |
| Passport control | 2 |
| Boarding | 1 |

Selected performance results:

| Metric | Result |
|--------|--------|
| Average passenger waiting time | 3.25 minutes |
| Average airport processing time | 22.22 minutes |
| Average completed passengers | 597.38 |
| Passenger completion rate | 95.29% |
| Average total operating cost | 2,152.06 model units |

The 7–2–2–2 configuration produced a similar estimated operating cost.
Statistical testing did not identify a significant difference between
these two configurations under the tested conditions.

## Interactive Dashboard

The Streamlit dashboard provides:

- Staffing configuration comparisons
- Cost and service-level visualization
- Feasibility-based staffing recommendations
- Confidence interval analysis
- Staffing sensitivity analysis
- Economic sensitivity scenarios
- Simulation data exploration

The dashboard analyzes previously generated simulation results.
It does not currently execute new AnyLogic simulations from user inputs.

## Project Structure

```text
Airport Digital Twin/
├── anylogic/
│   └── AirportDigitalTwinFinal.alp
├── data/
│   └── simulation_results.csv
├── results/
├── src/
├── dashboard.py
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the analysis pipeline

```bash
python main.py
```

### 3. Launch the dashboard

```bash
streamlit run dashboard.py
```

The analysis pipeline uses simulation results stored in
`data/simulation_results.csv`.

The AnyLogic model is provided separately in the `anylogic` folder.

## Assumptions and Limitations

- Results represent a modeled airport system rather than a validated
  real-world airport.
- The baseline simulation uses a fixed passenger arrival rate.
- Staffing recommendations are restricted to the configurations tested.
- Operating costs are expressed in hypothetical model units.
- Statistical results reflect the available simulation replications.
- Economic sensitivity scenarios reweight simulated costs rather than
  rerunning the simulation.

## Applications

The framework demonstrates industrial engineering methods applicable to:

- Airport operations management
- Resource allocation
- Queueing systems
- Capacity planning
- Simulation-based optimization
- Operational decision support