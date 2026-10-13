from pathlib import Path
import subprocess
import sys

BASE_DIR = Path(__file__).resolve().parent

SCRIPTS = [
    BASE_DIR / "src" / "data_processing.py",
    BASE_DIR / "src" / "optimization.py",
    BASE_DIR / "src" / "statistical_analysis.py",
    BASE_DIR / "src" / "sensitivity_analysis.py",
    BASE_DIR / "src" / "economic_sensitivity.py",
    BASE_DIR / "src" / "visualization.py",
]


def main():
    print("\nAIRPORT DIGITAL TWIN — AUTOMATED PIPELINE")
    print("=" * 55)

    for script in SCRIPTS:
        print(f"\nRunning {script.name}...", flush=True)

        subprocess.run(
            [sys.executable, str(script)],
            cwd=BASE_DIR,
            check=True
        )

    print("\nAll analyses completed successfully!")


if __name__ == "__main__":
    main()