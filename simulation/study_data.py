"""Load the saved evidence for the charging and discharge dashboard views."""

import csv
from collections import defaultdict
from math import isclose, isfinite
from pathlib import Path


REPORTS = Path(__file__).resolve().parent.parent / "reports"
DISCHARGE_POLICIES = ("lookahead", "mpc", "risk", "sac", "ppo", "fqi", "fixed", "rule")
CHARGING_POLICIES = ("original", "improved", "sac", "fixed")
REPLAY_POLICIES = ("fixed_1c", "fixed_2c", "fixed_3c", "rule", "model")
SEEDS = (42, 73, 101)


def saved_tables(study, *names):
    folder = REPORTS / f"lifeguard_{study}_results"
    if not all((folder / f"{name}.csv").is_file() for name in names):
        return None
    tables = []
    for name in names:
        with (folder / f"{name}.csv").open(encoding="utf-8", newline="") as file:
            tables.append(list(csv.DictReader(file)))
    return tables


def measure(value):
    if not value:
        return None
    number = float(value)
    if not isfinite(number):
        raise ValueError(f"Invalid measurement {value}")
    return number


def flag(value):
    if value not in ("True", "False"):
        raise ValueError(f"Invalid boolean value {value}")
    return value == "True"


def integers(row, *keys):
    return tuple(int(row[key]) for key in keys)


def measurements(row, *keys):
    return [measure(row[key]) for key in keys]


def unique_insert(mapping, key, item):
    if key in mapping:
        raise ValueError(f"Duplicate dashboard key {key}")
    mapping[key] = item


def load_coverage():
    tables = saved_tables("action_conditioned_twin", "action_support", "observed_switches")
    if tables is None:
        return None
    rows, switches = tables
    folds = defaultdict(dict)
    for row in rows:
        low, high = measurements(row, "soh_bin_start_pct", "soh_bin_end_pct")
        two, three = integers(row, "training_cells_2c", "training_cells_3c")
        if not 0 <= low < high or min(two, three) < 0:
            raise ValueError(f"Bad XJTU coverage row {row}")
        unique_insert(folds[int(row["fold"])], low, [low, high, two, three, flag(row["both_rates_supported"])])
    return {"switches": len(switches),
            "folds": {fold: [bins[k] for k in sorted(bins)] for fold, bins in sorted(folds.items())}}


def load_charging_updates():
    tables = saved_tables("mit_bit_charging_sac", "controller_episodes", "controller_metrics",
                           "forecast_predictions", "forecast_metrics")
    if tables is None:
        return None
    episodes, metrics, forecasts, errors = tables
    cases = {}
    for row in episodes:
        cell, start, draw, seed = integers(row, "cell_id", "start_cycle", "draw", "seed")
        policy, sequence = row["policy"], row["sequence"]
        energy, time, budget, fixed = measurements(row, "wh", "minutes", "budget", "fixed")
        if policy not in CHARGING_POLICIES or len(sequence) != 3 or set(sequence) - set("123"):
            raise ValueError(f"Bad Notebook 22 actions {row}")
        if energy < 0 or time <= 0 or not isclose(.9 * fixed, budget):
            raise ValueError(f"Bad Notebook 22 budget or outcome {row}")
        case = cases.setdefault((cell, start, draw), {"cell": cell, "start": start, "draw": draw,
                                                      "budget": budget, "runs": {}})
        if not isclose(case["budget"], budget):
            raise ValueError(f"Unmatched Notebook 22 energy budget for {cell}/{start}/{draw}")
        unique_insert(case["runs"], f"{policy}:{seed}", [sequence, time, energy])
    expected = {f"{policy}:0" for policy in CHARGING_POLICIES if policy != "sac"}
    expected.update(f"sac:{seed}" for seed in SEEDS)
    if (len(cases) != 164 * 8 or len({key[:2] for key in cases}) != 164 or
            any(case["runs"].keys() != expected for case in cases.values())):
        raise ValueError("Incomplete matched Notebook 22 controller comparison")
    summary = {row["policy"]: [*measurements(row, "minutes", "wh", "hit", "max_shortfall_wh"),
                                flag(row["selected"])] for row in metrics}
    if summary.keys() != set(CHARGING_POLICIES):
        raise ValueError("Incomplete Notebook 22 controller summary")

    points = {}
    for row in forecasts:
        if row["model"] not in ("ridge", "selected"):
            continue
        cell, start, horizon = integers(row, "cell_id", "start_cycle", "horizon_cycles")
        measured = measurements(row, "observed_wh", "observed_minutes")
        case = points.setdefault((horizon, cell, start), {"cell": cell, "start": start, "horizon": horizon,
                                                          "sequence": row["sequence"], "measured": measured})
        if (case["measured"] != measured or case["sequence"] != row["sequence"] or
                len(case["sequence"]) * 5 != horizon or set(case["sequence"]) - set("123")):
            raise ValueError(f"Unmatched Notebook 22 forecast {row}")
        unique_insert(case, row["model"], measurements(row, "predicted_wh", "predicted_minutes"))
    if (any(not {"ridge", "selected"} <= case.keys() for case in points.values()) or
            [sum(key[0] == h for key in points) for h in (5, 10, 15)] != [923, 862, 801]):
        raise ValueError("Incomplete Notebook 22 held-out forecast comparison")
    forecast_metrics = [
        [int(row["horizon_cycles"]), row["target"], row["model"], int(row["windows"]),
         *measurements(row, "mae", "tail_mae", "max_error")]
        for row in errors if row["model"] in ("ridge", "selected")
    ]
    return {"cases": list(cases.values()), "summary": summary, "forecasts": list(points.values()),
            "errors": forecast_metrics}


def load_measured_charging():
    tables = saved_tables("mit_bit_controller_benchmark", "decisions", "policy_metrics")
    if tables is None:
        return None
    decisions, metrics = tables
    cases = {}
    for row in decisions:
        cell, start, end, logged, chosen = integers(
            row, "cell_id", "start_cycle", "end_cycle", "logged_rate_c", "chosen_rate_c")
        budget, energy, minutes = measurements(row, "target_wh", "logged_wh", "logged_charge_minutes")
        key = (cell, start)
        case = cases.setdefault(key, {"cell": cell, "start": start, "end": end, "logged": logged,
                                      "budget": budget, "wh": energy, "minutes": minutes, "policies": {}})
        if (end - start != 4 or (end, logged, budget, energy, minutes) !=
                tuple(case[field] for field in ("end", "logged", "budget", "wh", "minutes"))):
            raise ValueError(f"Conflicting Notebook 16 observations for {key}")
        matched = flag(row["matched"])
        hit = measure(row["energy_target_hit"])
        if hit is not None:
            if hit not in (0., 1.):
                raise ValueError(f"Invalid Notebook 16 energy outcome for {key}")
            hit = bool(hit)
        if matched != (logged == chosen) or hit != (energy >= budget if matched and energy is not None else None):
            raise ValueError(f"Invalid Notebook 16 match for {key}")
        unique_insert(case["policies"], row["policy"], [chosen, matched, hit])
    if len(cases) != 929 or any(case["policies"].keys() != set(REPLAY_POLICIES) for case in cases.values()):
        raise ValueError("Incomplete Notebook 16 recorded policy comparisons")
    summary = {}
    for row in metrics:
        policy = row["policy"]
        matched = sum(case["policies"][policy][1] for case in cases.values())
        with_wh = sum(case["policies"][policy][2] is not None for case in cases.values())
        if integers(row, "origins", "matched", "measured_wh") != (len(cases), matched, with_wh):
            raise ValueError(f"Notebook 16 summary differs from case counts for {policy}")
        summary[policy] = [matched, with_wh, *measurements(row, "charge_minutes", "delivered_wh", "hit_rate")]
    return {"cases": list(cases.values()), "summary": summary}


def load_simulator_validation():
    tables = saved_tables("mit_bit_multiblock_simulator", "recorded_trajectories",
                           "recorded_rollout_totals", "validation_metrics")
    if tables is None:
        return None
    records, totals, errors = tables
    series = defaultdict(dict)
    for row in records:
        cell, start, step, block, rate = integers(row, "cell_id", "start_cycle", "step", "block_start", "rate")
        if block != start + (step - 1)*5 or rate not in (1, 2, 3):
            raise ValueError(f"Invalid Notebook 17 trajectory {row}")
        key = (row["cohort"], cell, start)
        values = measurements(row, "observed_wh", "predicted_wh", "observed_minutes", "predicted_minutes",
                              "observed_ah", "predicted_ah")
        unique_insert(series[key], step, [rate, *values])

    cases = []
    seen = set()
    for row in totals:
        cell, start, blocks, horizon = integers(row, "cell_id", "start_cycle", "blocks", "horizon_cycles")
        key = (row["cohort"], cell, start, horizon)
        if key in seen or horizon != blocks*5:
            raise ValueError(f"Invalid Notebook 17 scored horizon {key}")
        seen.add(key)
        path = [series[key[:3]][step] for step in range(1, blocks+1)]
        sequence = "".join(str(values[0]) for values in path)
        observed_predicted = measurements(row, "observed_cumulative_wh", "predicted_cumulative_wh",
                                          "observed_cumulative_minutes", "predicted_cumulative_minutes",
                                          "observed_final_ah", "predicted_final_ah")
        expected = [sum(values[i] for values in path) for i in range(1, 5)] + path[-1][5:]
        if (sequence != row["sequence"] or
                not all(isclose(a, b, abs_tol=1e-9) for a, b in zip(expected, observed_predicted))):
            raise ValueError(f"Notebook 17 trajectory differs from scored total {key}")
        cases.append({"cohort": row["cohort"], "cell": cell, "start": start, "horizon": horizon, "path": path})
    metrics = [[row["cohort"], int(row["horizon_cycles"]), row["metric"], int(row["windows"]),
                int(row["batteries"]), *measurements(row, "baseline_mae", "model_mae", "model_worst_decile_mae",
                                                    "model_max_error")] for row in errors if row["group"] == "all"]
    return {"cases": cases, "errors": metrics}


def load_discharge():
    tables = saved_tables("xjtu_discharge_forecast_sac", "refinement_predictions", "refinement_metrics",
                           "controller_episodes", "controller_metrics")
    references = saved_tables("xjtu_discharge_soh", "reference_intervals")
    if tables is None or references is None:
        return None
    forecasts, errors, episodes, controller_metrics = tables
    intervals = {(row["cell_id"], int(row["start_cycle"])): row for row in references[0]
                 if row["cohort"] == "RW" and row["status"] == "valid"}
    predictions = defaultdict(dict)
    for row in forecasts:
        stage = (int(row["cycles"]) if row["mode"] == "rolling"
                 else 0 if row["mode"] == "fixed" and row["cycles"] == "30" else None)
        if stage is None:
            continue
        key = (row["cell_id"], int(row["start_cycle"]), int(row["end_cycle"]))
        unique_insert(predictions[key], (stage, row["target"]), row)

    cases = []
    for (cell, start, end), readings in sorted(predictions.items()):
        origin = start
        energy = 0.
        stages = []
        for stage in (0, 10, 20):
            row = intervals[cell, origin]
            soh, wh = (readings[stage, target] for target in ("soh", "wh"))
            observed = float(row["soh_before"])
            if not all(isclose(float(item["forecast_origin_soh"]), observed) for item in (soh, wh)):
                raise ValueError(f"Invalid Notebook 23 forecast origin {cell}/{origin}")
            stages.append([origin, observed, energy, measurements(soh, "original", "incumbent", "recommended"),
                            measurements(wh, "original", "incumbent", "recommended")])
            origin = int(row["end_cycle"])
            energy += float(row["realized_wh"])
        final_soh = float(row["soh_after"])
        if origin != end or any(not isclose(float(item["measured"]), final_soh if target == "soh" else energy)
                                for (_, target), item in readings.items()):
            raise ValueError(f"Notebook 23 reference endpoint differs from forecast {cell}/{start}")
        cases.append({"cell": cell, "start": start, "end": end, "stages": stages, "measured": [final_soh, energy]})
    if len(cases) != 149:
        raise ValueError("Incomplete Notebook 23 rolling forecast endpoints")
    summary = [
        [0 if row["mode"] == "fixed" else int(row["cycles"]), row["target"], row["role"], int(row["windows"]),
         *measurements(row, "mae", "worst_10", "max_error")]
        for row in errors if (row["mode"] == "rolling" or row["cycles"] == "30")
        and row["role"] in ("original", "incumbent", "recommended")
    ]

    runs = {}
    for row in episodes:
        cell, evaluation, policy = (row[name] for name in ("cell_id", "evaluation", "policy"))
        start, draw, seed, completed = integers(row, "start_cycle", "draw", "seed", "intervals_completed")
        actions = row["actions"]
        loss, energy, budget = measurements(row, "soh_loss_pp", "delivered_wh", "budget_wh")
        hit, stopped = flag(row["budget_hit"]), flag(row["unsupported_stop"])
        if (evaluation not in ("original", "stress") or policy not in DISCHARGE_POLICIES or
                completed != len(actions) or not 1 <= completed <= 3 or set(actions) - set("012") or
                stopped != (completed < 3) or hit != (energy >= budget and not stopped)):
            raise ValueError(f"Invalid Notebook 23 controller outcome {row}")
        key = (evaluation, cell, start, draw)
        case = runs.setdefault(key, {"evaluation": evaluation, "cell": cell, "start": start, "draw": draw,
                                     "budget": budget, "runs": {}})
        if not isclose(case["budget"], budget):
            raise ValueError(f"Unmatched Notebook 23 energy budget for {key}")
        unique_insert(case["runs"], f"{policy}:{seed}", [actions, loss, energy, hit, stopped])
    expected = {f"{policy}:0" for policy in DISCHARGE_POLICIES if policy not in ("sac", "ppo")}
    expected.update(f"{policy}:{seed}" for policy in ("sac", "ppo") for seed in SEEDS)
    if (len(runs) != 2*133*8 or len({key[1:3] for key in runs}) != 133 or
            any(case["runs"].keys() != expected for case in runs.values())):
        raise ValueError("Incomplete matched Notebook 23 controller comparison")
    results = [
        [row["evaluation"], row["policy"], *measurements(row, "soh_loss_pp", "tail_loss_pp", "max_loss_pp",
          "budget_hit", "unsupported_stop"), flag(row["selected"])]
        for row in controller_metrics
    ]
    return {"forecasts": cases, "errors": summary, "controllers": list(runs.values()), "summary": results}
