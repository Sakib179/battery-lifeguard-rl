"""Embed saved digital twin benchmarks in an offline dashboard."""

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "reports" / "lifeguard_digital_twin_validation_results"
LATE_LIFE_RESULTS = HERE.parent / "reports" / "lifeguard_fixed_anchor_soh_results"
ROLLING_RESULTS = HERE.parent / "reports" / "lifeguard_rolling_forecasts_results"
FIXED_SOH_RESULTS = HERE.parent / "reports" / "lifeguard_fixed_soh_forecast_results"
SWITCH_RESULTS = HERE.parent / "reports" / "lifeguard_mit_bit_switch_replay_results"
FIXED_SOH_MODELS = {"dashboard_fixed", "previous_fixed", "revised_fixed"}


def rows(name, directory=RESULTS):
    with (directory / name).open(encoding="utf-8", newline="") as source:
        yield from csv.DictReader(source)


def optional(value, convert=float):
    return convert(value) if value else None


def metric_key(row):
    return "/".join(row[field] for field in ("charge_rate_c", "landmark_cycle", "initializer", "model"))


def load_rolling(cells):
    config_file = ROLLING_RESULTS / "run_config.json"
    if not config_file.is_file():
        return None
    config = json.loads(config_file.read_text(encoding="utf-8"))
    starts = config.get("start_cycles") or [config["start_cycle"]]
    start = min(starts)
    step = config["checkpoint_interval"]
    horizons = config["soh_horizons"]
    by_cell = {cell: {} for cell in cells}
    for row in rows("rul_predictions.csv", ROLLING_RESULTS):
        cell = row["cell_id"]
        cycle = int(row["cycle"])
        anchor = cells[cell]["landmarks"][str(start)]
        if (int(row["charge_rate_c"]) != cells[cell]["rate"] or cycle < start
                or (cycle - start) % step or cycle - start >= len(anchor["observed"])
                or cycle in by_cell[cell]):
            raise ValueError(f"Invalid rolling checkpoint for {cell} at cycle {cycle}")
        by_cell[cell][cycle] = {
            "cycle": cycle, "rul": float(row["selected_rul_cycles"]),
            "earlierRul": float(row["earlier_rul_cycles"]), "soh": {},
        }

    for row in rows("soh_predictions.csv", ROLLING_RESULTS):
        cell = row["cell_id"]
        origin = int(row["origin_cycle"])
        horizon = int(row["horizon_cycles"])
        target = int(row["target_cycle"])
        observed = cells[cell]["landmarks"][str(start)]["observed"]
        estimates = by_cell[cell][origin]["soh"]
        if (horizon not in horizons or horizon in estimates or target != origin + horizon
                or target - start >= len(observed) or float(row["observed_soh_pct"]) != observed[target - start]):
            raise ValueError(f"Invalid rolling SOH target for {cell} at cycle {target}")
        estimates[horizon] = float(row["selected_soh_pct"])

    for cell, points in by_cell.items():
        if points:
            cells[cell]["rolling"] = [points[cycle] for cycle in sorted(points)]

    benchmarks = {}

    def cohort_metrics(row, table):
        anchor = int(row.get("start_cycle", start))
        windows = benchmarks.setdefault(anchor, {})
        view = windows.setdefault(row.get("origin_window", "all"), {"soh": {}, "rul": {}})
        return view[table].setdefault(row["charge_rate_c"], {})

    for row in rows("soh_metrics.csv", ROLLING_RESULTS):
        if row["variant"] == "selected" and row["mae"]:
            cohort_metrics(row, "soh")[row["horizon_cycles"]] = {
                "mae": float(row["mae"]), "worst": float(row["worst"]),
            }

    for row in rows("rul_metrics.csv", ROLLING_RESULTS):
        if (row["mae"] and row["variant"] in ("earlier", "selected")
                and row["actual_rul_window"] in ("all", "1–20")):
            group = cohort_metrics(row, "rul").setdefault(row["actual_rul_window"], {})
            group[row["variant"]] = {
                "mae": float(row["mae"]), "worst": float(row["worst"]),
                "worstCell": row["worst_cell"], "worstCycle": int(row["worst_cycle"]),
            }
    if set(starts) != benchmarks.keys() or any("all" not in views for views in benchmarks.values()):
        raise ValueError("Rolling benchmarks are incomplete for the available start cycles")
    return {"starts": starts, "step": step, "horizons": horizons, "benchmarks": benchmarks}


def load_fixed_soh(cells, soh_metrics, eol_threshold):
    metrics_file = FIXED_SOH_RESULTS / "metrics.csv"
    trajectories_file = FIXED_SOH_RESULTS / "soh_trajectories.csv"
    if not metrics_file.is_file() and not trajectories_file.is_file():
        return {}

    curves = {}
    for cell in cells.values():
        for start, anchor in cell["landmarks"].items():
            for mode in ("charge", "measured"):
                reference = anchor["initializers"][mode]["soh_dependent"]["forecast"]
                # Notebook 12 scores only cycles after the anchor and preserves this initial SOH.
                curves[cell["id"], start, mode] = [reference[0]]

    for row in rows(trajectories_file.name, FIXED_SOH_RESULTS):
        cell_id, start, mode = row["cell_id"], row["landmark_cycle"], row["initializer"]
        cell = cells[cell_id]
        observed = cell["landmarks"][start]["observed"]
        curve = curves[cell_id, start, mode]
        cycle = int(row["cycle"])
        offset = cycle - int(start)
        if (offset != len(curve) or offset >= len(observed)
                or int(row["horizon_cycles"]) != offset
                or int(row["charge_rate_c"]) != cell["rate"]
                or optional(row["observed_eol_cycle"], int) != cell["observedEol"]
                or float(row["observed_soh_pct"]) != observed[offset]):
            raise ValueError(f"Invalid Notebook 12 trajectory for {cell_id} at cycle {cycle}")
        curve.append(float(row["revised_fixed_soh_pct"]))

    starts = {}
    if (FIXED_SOH_RESULTS / "rollout_starts.csv").is_file():
        for row in rows("rollout_starts.csv", FIXED_SOH_RESULTS):
            cell_id, start, mode = row["cell_id"], row["landmark_cycle"], row["initializer"]
            key = cell_id, start, mode
            curve = curves.get(key)
            if key in starts or curve is None or row["model"] != "revised_fixed":
                raise ValueError(f"Unexpected Notebook 12 rollout for {cell_id} from cycle {start} ({mode})")
            rul = optional(row["predicted_rul_cycles"], int)
            eol = optional(row["predicted_eol_cycle"], int)
            limit = int(row["max_rollout_steps"])
            status = row["forecast_status"]
            expected_status = "crossed" if rul is not None else "no_crossing_by_limit"
            expected_eol = int(start) + rul if rul is not None else None
            visible_crossing = next((offset for offset, value in enumerate(curve)
                                     if value <= eol_threshold + 1e-9), None)
            expected_crossing = rul if rul is not None and rul < len(curve) else None
            if (float(row["eol_soh_pct"]) != eol_threshold or int(row["charge_rate_c"]) != cells[cell_id]["rate"]
                    or status != expected_status or eol != expected_eol or len(curve) - 1 > limit
                    or (rul is not None and not 0 <= rul <= limit) or visible_crossing != expected_crossing):
                raise ValueError(f"Invalid Notebook 12 RUL for {cell_id} from cycle {start} ({mode})")
            starts[key] = {"rul": rul, "status": status, "maxRollout": limit}
        if starts.keys() != curves.keys():
            raise ValueError("Incomplete Notebook 12 RUL projections")

    coverage = {}
    for (cell_id, start, mode), curve in curves.items():
        cell = cells[cell_id]
        anchor = cell["landmarks"][start]
        if len(curve) != len(anchor["observed"]):
            raise ValueError(f"Incomplete Notebook 12 trajectory for {cell_id} from cycle {start} ({mode})")
        anchor["initializers"][mode]["revised_fixed"] = {
            "forecast": curve, **starts.get((cell_id, start, mode), {}),
        }
        key = f"{cell['rate']}/{start}/{mode}"
        coverage.setdefault(key, set()).add(cell_id)

    comparisons = {}
    for row in rows(metrics_file.name, FIXED_SOH_RESULTS):
        key, model = metric_key(row).rsplit("/", 1)
        group = comparisons.setdefault(key, {})
        if key not in coverage or model not in FIXED_SOH_MODELS or model in group:
            raise ValueError(f"Unexpected Notebook 12 metrics for {key}/{model}")
        group[model] = {}
        for window in ("full", "last20"):
            worst_cell = row[f"{window}_worst_cell_id"]
            count = int(row[f"{window}_cells"])
            expected = (len(coverage[key]) if window == "full"
                        else sum(cells[cell]["observedEol"] is not None for cell in coverage[key]))
            if count != expected or worst_cell not in coverage[key]:
                raise ValueError(f"Invalid Notebook 12 {window} coverage for {key}/{model}")
            group[model][window] = {
                "mae": float(row[f"{window}_mae_pp"]),
                "worst": float(row[f"{window}_max_pp"]),
                "cells": count,
                "worstCell": worst_cell,
                "worstCycle": int(row[f"{window}_worst_cycle"]),
            }
        if model == "revised_fixed":
            soh_metrics[f"{key}/{model}"] = {
                str(horizon): {
                    "mae": optional(row[f"horizon_{horizon}_mae_pp"]),
                    "cells": int(row[f"horizon_{horizon}_cells"]),
                }
                for horizon in (10, 50)
            }
    if comparisons.keys() != coverage.keys() or any(
        group.keys() != FIXED_SOH_MODELS for group in comparisons.values()
    ):
        raise ValueError("Incomplete Notebook 12 cohort comparisons")
    return comparisons


def load_results():
    config = json.loads((RESULTS / "run_config.json").read_text(encoding="utf-8"))
    approved = set()
    if (LATE_LIFE_RESULTS / "model_selection.csv").is_file():
        approved = {metric_key(row) for row in rows("model_selection.csv", LATE_LIFE_RESULTS)
                    if row["approved"] == "True"}

    def forecast_rows(name):
        yield from rows(name)
        if approved:
            yield from (row for row in rows(name, LATE_LIFE_RESULTS) if metric_key(row) in approved)

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

    for row in forecast_rows("rollout_starts.csv"):
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

    for row in forecast_rows("soh_trajectories.csv"):
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
    for row in forecast_rows("soh_horizon_metrics.csv"):
        soh_metrics.setdefault(metric_key(row), {})[row["horizon_cycles"]] = {
            "mae": optional(row["paired_mae_pp"]),
            "cells": int(row["paired_test_cells"]),
        }

    rul_metrics = {}
    for row in forecast_rows("rul_metrics.csv"):
        rul_metrics[metric_key(row)] = {
            "mae": optional(row["mae_cycles"]),
            "predictions": int(row["predicted_test_cells"]),
            "observed": int(row["observed_test_cells"]),
        }

    late_life_metrics = {}
    if approved:
        approved_contexts = {key.rsplit("/", 1)[0] for key in approved}
        for row in rows("soh_benchmark.csv", LATE_LIFE_RESULTS):
            key = metric_key(row)
            if row["window"] == "last_20_cycles" and key.rsplit("/", 1)[0] in approved_contexts:
                late_life_metrics[key] = {
                    "mae": optional(row["mae_pp"]),
                    "worst": optional(row["worst_error_pp"]),
                    "cells": int(row["paired_test_cells"]),
                }

    fixed_soh = load_fixed_soh(cells, soh_metrics, config["eol_soh_pct"])
    rolling = load_rolling(cells)
    return {
        "cells": list(cells.values()),
        "sohMetrics": soh_metrics,
        "rulMetrics": rul_metrics,
        "lateLifeMetrics": late_life_metrics,
        "fixedSohMetrics": fixed_soh,
        "rolling": rolling,
        "eolThreshold": config["eol_soh_pct"],
        "maxRollout": config["max_rollout_steps"],
        "horizons": config["horizons"],
    }


def embed_data(script_id, data):
    payload = json.dumps(data, separators=(",", ":"), allow_nan=False).replace("<", "\\u003c")
    return f'<script id="{script_id}" type="application/json">{payload}</script>'


def load_switch_replay():
    filenames = ("run_config.json", "replay_cases.csv", "replay_blocks.csv", "metrics.csv")
    if not all((SWITCH_RESULTS / name).is_file() for name in filenames):
        return None
    config = json.loads((SWITCH_RESULTS / filenames[0]).read_text(encoding="utf-8"))
    if config["mode"] != "benchmark" or config["doi"] != "10.17632/kw34hhw7xg.3":
        return None

    cases = {}
    for row in rows("replay_cases.csv", SWITCH_RESULTS):
        case_id = row["case_id"]
        if case_id in cases:
            raise ValueError(f"Duplicate switch replay {case_id}")
        cases[case_id] = {
            "id": case_id, "direction": row["direction"], "kind": row["kind"],
            "cell": int(row["cell_id"]), "focus": int(row["focus_start_cycle"]), "blocks": [],
        }

    size = config["block_size"]
    for row in rows("replay_blocks.csv", SWITCH_RESULTS):
        case = cases[row["case_id"]]
        block = {
            "start": int(row["start_cycle"]), "end": int(row["end_cycle"]),
            "rate": int(row["charge_rate_c"]), "priorRate": int(row["previous_rate_c"]),
            "measuredSoh": optional(row["observed_soh_pct"]), "predictedSoh": optional(row["predicted_soh"]),
            "measuredWh": optional(row["observed_wh"]), "predictedWh": optional(row["predicted_wh"]),
            "sohModel": row["soh_model"], "whModel": row["wh_model"],
        }
        if (int(row["cell_id"]) != case["cell"] or block["end"] - block["start"] + 1 != size
                or any(b["start"] == block["start"] for b in case["blocks"])):
            raise ValueError(f"Invalid block in switch replay {case['id']}")
        case["blocks"].append(block)

    direction_rates = {"2-to-3": (2, 3), "3-to-2": (3, 2)}
    for case in cases.values():
        case["blocks"].sort(key=lambda block: block["start"])
        focus = next((block for block in case["blocks"] if block["start"] == case["focus"]), None)
        if (focus is None or focus["measuredSoh"] is None or focus["predictedSoh"] is None
                or (focus["priorRate"], focus["rate"]) != direction_rates.get(case["direction"])):
            raise ValueError(f"Missing verified focus block for {case['id']}")

    benchmark = {}
    for row in rows("metrics.csv", SWITCH_RESULTS):
        if row["model"] == "selected" and row["direction"] in direction_rates:
            benchmark.setdefault(row["direction"], {})[row["target"]] = {
                "mae": optional(row["mae"]), "worst": optional(row["worst_error"]),
                "scored": int(row["scored_blocks"]), "eligible": int(row["eligible_blocks"]),
            }
    if {case["direction"] for case in cases.values()} != set(direction_rates):
        return None
    return {"cases": list(cases.values()), "metrics": benchmark, "scoredCells": config["scored_cells"]}


def main():
    template = (HERE / "dashboard.template.html").read_text(encoding="utf-8")
    marker = "<!-- NOTEBOOK_RESULTS -->"
    if template.count(marker) != 1:
        raise ValueError("The dashboard template needs one notebook data marker")
    data = load_results()
    embedded = embed_data("notebook-data", data)
    replay = load_switch_replay()
    replay_link = ""
    if replay is not None:
        replay_template = (HERE / "switch_replay.template.html").read_text(encoding="utf-8")
        replay_marker = "<!-- SWITCH_RESULTS -->"
        if replay_template.count(replay_marker) != 1:
            raise ValueError("The switch replay template needs one data marker")
        (HERE / "switch-replay.html").write_text(
            replay_template.replace(replay_marker, embed_data("switch-data", replay)), encoding="utf-8")
        replay_link = '<p class="replay-link"><a href="switch-replay.html">MIT–BIT switch replay</a></p>'
        print(f"Wrote simulation/switch-replay.html with {len(replay['cases'])} held-out examples")
    output = HERE / "index.html"
    output.write_text(template.replace(marker, embedded).replace("<!-- SWITCH_REPLAY_LINK -->", replay_link),
                      encoding="utf-8")
    print(f"Wrote {output.relative_to(HERE.parent)} with {len(data['cells'])} cells")


if __name__ == "__main__":
    main()
