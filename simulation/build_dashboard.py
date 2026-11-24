"""Embed the Notebook 07 CSV exports in an offline dashboard."""

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "reports" / "lifeguard_digital_twin_validation_results"


def rows(name):
    with (RESULTS / name).open(encoding="utf-8", newline="") as source:
        yield from csv.DictReader(source)


def optional(value, convert=float):
    return convert(value) if value else None


def metric_key(row):
    return "/".join(row[field] for field in ("charge_rate_c", "landmark_cycle", "initializer", "model"))


def load_results():
    config = json.loads((RESULTS / "run_config.json").read_text(encoding="utf-8"))
    cells = {}
    for row in rows("eol_audit.csv"):
        cells[row["cell_id"]] = {
            "id": row["cell_id"],
            "rate": int(row["charge_rate_c"]),
            "observedEol": optional(row["observed_eol_cycle"], int),
            "lastRecorded": int(row["last_observed_cycle"]),
            "eventStatus": row["event_status"],
            "landmarks": {},
        }

    for row in rows("rollout_starts.csv"):
        cell = cells[row["cell_id"]]
        anchor = cell["landmarks"].setdefault(
            row["landmark_cycle"], {"observed": [], "initializers": {}}
        )
        models = anchor["initializers"].setdefault(row["initializer"], {})
        models[row["model"]] = {
            "rul": optional(row["predicted_rul_cycles"]),
            "status": row["forecast_status"],
            "forecast": [],
        }

    for row in rows("soh_trajectories.csv"):
        anchor = cells[row["cell_id"]]["landmarks"][row["landmark_cycle"]]
        forecast = anchor["initializers"][row["initializer"]][row["model"]]["forecast"]
        index = int(row["cycle"]) - int(row["landmark_cycle"])
        if index != len(forecast):
            raise ValueError(f"Unexpected cycle order in the trajectory for {row['cell_id']}")
        forecast.append(optional(row["predicted_soh_pct"]))

        observed = anchor["observed"]
        value = optional(row["observed_soh_pct"])
        if index == len(observed):
            observed.append(value)
        elif observed[index] != value:
            raise ValueError(f"Conflicting measured SOH for {row['cell_id']} at cycle {row['cycle']}")

    for cell in cells.values():
        for landmark, anchor in cell["landmarks"].items():
            last_cycle = cell["observedEol"] if cell["observedEol"] is not None else cell["lastRecorded"]
            expected = last_cycle - int(landmark) + 1
            for models in anchor["initializers"].values():
                if len(anchor["observed"]) != expected or any(
                    len(model["forecast"]) != expected for model in models.values()
                ):
                    raise ValueError(f"Incomplete trajectory for {cell['id']} from cycle {landmark}")

    for row in rows("rul_predictions.csv"):
        if row["model"] == "previous_rul_model" and row["initializer"] == "charge":
            anchor = cells[row["cell_id"]]["landmarks"][row["landmark_cycle"]]
            anchor["previousRul"] = optional(row["predicted_rul_cycles"])

    soh_metrics = {}
    for row in rows("soh_horizon_metrics.csv"):
        soh_metrics.setdefault(metric_key(row), {})[row["horizon_cycles"]] = {
            "mae": optional(row["paired_mae_pp"]),
            "cells": int(row["paired_test_cells"]),
        }

    rul_metrics = {}
    for row in rows("rul_metrics.csv"):
        rul_metrics[metric_key(row)] = {
            "mae": optional(row["mae_cycles"]),
            "predictions": int(row["predicted_test_cells"]),
            "observed": int(row["observed_test_cells"]),
        }

    return {
        "cells": list(cells.values()),
        "sohMetrics": soh_metrics,
        "rulMetrics": rul_metrics,
        "eolThreshold": config["eol_soh_pct"],
        "maxRollout": config["max_rollout_steps"],
        "horizons": config["horizons"],
    }


def main():
    template = (HERE / "dashboard.template.html").read_text(encoding="utf-8")
    marker = "<!-- NOTEBOOK_RESULTS -->"
    if template.count(marker) != 1:
        raise ValueError("The dashboard template needs one Notebook 07 data marker")
    data = load_results()
    payload = json.dumps(data, separators=(",", ":"), allow_nan=False).replace("<", "\\u003c")
    embedded = f'<script id="notebook-data" type="application/json">{payload}</script>'
    output = HERE / "index.html"
    output.write_text(template.replace(marker, embedded), encoding="utf-8")
    print(f"Wrote {output.relative_to(HERE.parent)} with {len(data['cells'])} cells")


if __name__ == "__main__":
    main()
