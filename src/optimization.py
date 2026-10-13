from pathlib import Path
import pandas as pd

# Project directories
BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"

# Input from our previous analysis
SUMMARY_FILE = RESULTS_DIR / "staffing_summary.csv"

# Output
OPTIMIZATION_FILE = RESULTS_DIR / "optimization_results.csv"

# Operational constraints (initial assumptions)
MAX_WAITING_TIME = 10.0  # minutes
MAX_AIRPORT_TIME = 35.0  # minutes

# Staffing availability
MAX_CHECKIN = 7
MAX_SECURITY = 2
MAX_PASSPORT = 2
MAX_GATE = 2


def optimize_staffing():

    # Load automatically generated simulation statistics
    data = pd.read_csv(SUMMARY_FILE)

    # Apply service-level constraints
    feasible = data[
         (data["CI_Upper_WaitingTime"] <= MAX_WAITING_TIME)
    & (data["CI_Upper_AirportTime"] <= MAX_AIRPORT_TIME)
        & (data["CheckIn"] <= MAX_CHECKIN)
        & (data["Security"] <= MAX_SECURITY)
        & (data["Passport"] <= MAX_PASSPORT)
        & (data["Gate"] <= MAX_GATE)
    ].copy()

    # Check whether any feasible solutions exist
    if feasible.empty:
        print("No staffing configuration satisfies the constraints.")
        return

    # Rank feasible configurations by total operating cost
    feasible = feasible.sort_values(
        by="Mean_TotalCost",
        ascending=True
    )

    # Save all feasible configurations
    feasible.to_csv(OPTIMIZATION_FILE, index=False)

    # Select the best configuration
    best = feasible.iloc[0]

    print("\nAIRPORT DIGITAL TWIN — STAFFING OPTIMIZATION")
    print("=" * 55)

    print("\nOPTIMAL STAFFING CONFIGURATION (AMONG TESTED OPTIONS)")
    print("-" * 55)

    print(f"Check-in agents:      {int(best['CheckIn'])}")
    print(f"Security officers:    {int(best['Security'])}")
    print(f"Passport officers:    {int(best['Passport'])}")
    print(f"Gate agents:          {int(best['Gate'])}")

    print("\nEXPECTED PERFORMANCE")
    print("-" * 55)

    print(f"Average airport time:  {best['Mean_AirportTime']:.2f} min")
    print(f"Average waiting time:  {best['Mean_WaitingTime']:.2f} min")
    print(f"Average staffing cost: {best['Mean_StaffingCost']:.2f}")
    print(f"Average waiting cost:  {best['Mean_WaitingCost']:.2f}")
    print(f"Average total cost:    {best['Mean_TotalCost']:.2f}")

    print(f"\nFeasible configurations found: {len(feasible)}")
    print(f"Results saved to: {OPTIMIZATION_FILE}")


if __name__ == "__main__":
    optimize_staffing()