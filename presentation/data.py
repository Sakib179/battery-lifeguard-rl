"""Build the presentation data from the validated simulation exports."""

import argparse
import json
from pathlib import Path

from simulation.build_dashboard import load_controller_replay, load_results
from simulation.study_data import load_discharge


def load_health(report):
    cases = []
    start = 100
    for cell in report["cells"]:
        observed = cell["landmarks"][str(start)]["observed"]
        checkpoints = [
            {
                "cycle": point["cycle"],
                "observed": observed[point["cycle"] - start],
                "estimate": point["soh"].get(0),
                "cycles_left": point["rul"],
            }
            for point in cell.get("rolling", [])
            if point["cycle"] >= start
        ]
        end = start + len(observed) - 1
        if not checkpoints:
            raise ValueError(f"Missing battery-life checkpoints for {cell['id']}")
        if checkpoints[-1]["cycle"] < end:
            checkpoints.append({"cycle": end, "observed": observed[-1], "estimate": None, "cycles_left": None})
        cases.append({"cell": cell["id"], "observed_eol": cell["observedEol"], "checkpoints": checkpoints})
    return {"threshold": report["eolThreshold"], "cases": cases}


def collect_data():
    charging = load_controller_replay()
    discharge = load_discharge()
    if charging is None or discharge is None:
        raise FileNotFoundError("The charging or discharge report exports are missing.")
    charging_cases = [
        {**case, "policies": {name: case["policies"][name] for name in ("fixed_1c", "energy_budget")}}
        for case in charging["cases"]
    ]
    return {
        "charging": {"cases": charging_cases, "block_size": charging["blockSize"]},
        "discharge": {
            "forecasts": discharge["forecasts"],
            "controllers": [case for case in discharge["controllers"] if case["evaluation"] == "original"
                            and case["draw"] == 0],
        },
        "health": load_health(load_results()),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="Path to the presentation JSON bundle")
    args = parser.parse_args()
    args.output.write_text(json.dumps(collect_data(), separators=(",", ":"), allow_nan=False), encoding="utf-8")
