"""Build comparable MLflow runs from the saved notebook reports."""

from collections import defaultdict
import csv
from dataclasses import dataclass, field
from hashlib import sha256
import io
import json
from math import isfinite
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
REPORT_NAMES = {
    11: "rolling_forecasts", 12: "fixed_soh_forecast", 16: "mit_bit_controller_benchmark",
    17: "mit_bit_multiblock_simulator", 20: "xjtu_discharge_ppo",
    22: "mit_bit_charging_sac", 23: "xjtu_discharge_forecast_sac",
}


class Report:
    def __init__(self, notebook, path=None):
        self.notebook = notebook
        default = REPORTS / f"lifeguard_{REPORT_NAMES[notebook]}_results"
        self.path = Path(path).expanduser().resolve() if path is not None else default
        if path is None and not self.path.is_dir():
            self.path = default.with_suffix(".zip")
        if not self.path.exists():
            raise FileNotFoundError(self.path)
        self._files = {}

    def read(self, name):
        if name not in self._files:
            if self.path.is_dir():
                contents = (self.path / name).read_bytes()
            else:
                with ZipFile(self.path) as archive:
                    names = [m for m in archive.namelist() if PurePosixPath(m).name == name and not m.endswith("/")]
                    if not names:
                        raise FileNotFoundError(f"{name} in {self.path}")
                    if len(names) != 1:
                        raise ValueError(f"More than one {name} in {self.path}")
                    contents = archive.read(names[0])
            self._files[name] = contents
        return self._files[name]

    def rows(self, name):
        return list(csv.DictReader(io.StringIO(self.read(name).decode("utf-8-sig"), newline="")))

    def config(self):
        try:
            return json.loads(self.read("run_config.json"))
        except FileNotFoundError:
            return {}


@dataclass
class Run:
    name: str
    evidence: str
    notebook: int
    params: dict
    metrics: dict
    tags: dict = field(default_factory=dict)

    @property
    def key(self):
        return json.dumps([self.notebook, self.name, self.evidence, self.params, self.tags], sort_keys=True)


@dataclass
class Experiment:
    title: str
    dataset: str
    runs: list
    files: list
    plotter: object

    @property
    def name(self):
        return "LifeGuard-RL / " + self.title

    @property
    def fingerprint(self):
        data = sha256(b"lifeguard-mlflow-v1")
        for report, name in self.files:
            if name not in ("summary.md", "run_config.json"):
                data.update(f"{report.notebook}/{name}\0".encode())
                data.update(sha256(report.read(name)).digest())
        return data.hexdigest()


def number(value):
    if value in ("", None):
        return None
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"Non-finite archived metric {value}")
    return result


def grouped(rows, fields):
    buckets = defaultdict(list)
    for row in rows:
        buckets[tuple(row[field] for field in fields)].append(row)
    return buckets


def metric_series(rows, mapping, step=None):
    """Each MLflow point uses the physical horizon or logged training step."""
    result = {}
    for metric, source in mapping.items():
        column, scale = source if isinstance(source, tuple) else (source, 1)
        points = {}
        for row in rows:
            value = number(row[column])
            tick = int(row[step]) if step else 0
            if value is not None:
                if tick in points:
                    raise ValueError(f"Duplicate metric {metric} at step {tick}")
                points[tick] = value * scale
        if points:
            result[metric] = sorted(points.items())
    return result


def parameters(report, names):
    config = report.config()
    return {name: config[name] for name in names if name in config}


def training(report, filename, fold, algorithm, metrics, step, config):
    runs = []
    for (battery, seed), rows in grouped(report.rows(filename), (fold, "seed")).items():
        name = f"{algorithm} training · {battery} · seed {seed}"
        params = {**parameters(report, config), fold: battery, "seed": int(seed), "algorithm": algorithm,
                  "step_axis": "training_update"}
        runs.append(Run(name, "training_history", report.notebook, params, metric_series(rows, metrics, step),
                        {"run_kind": "training", "model_or_policy": algorithm}))
    return runs


def listed(report, names):
    return [(report, name) for name in names]


POLICY_LABELS = {
    "fixed_1c": "Fixed 1C", "fixed_2c": "Fixed 2C", "fixed_3c": "Fixed 3C",
    "rule": "Past-observation rule", "model": "Model-guided", "original": "Notebook 18 MPC",
    "improved": "Forecast-refined MPC", "sac": "Discrete SAC", "ppo": "PPO", "fqi": "Fitted Q iteration",
    "lookahead": "Original Lookahead", "mpc": "Forecast MPC", "risk": "Risk-aware MPC",
}
CONTROLLER_CONFIG = ("seeds", "sac_updates", "sac_batch_size", "sac_batch", "learning_rate",
                     "target_update", "sac_hidden_layers", "training_entropy_fraction",
                     "energy_budget_fraction", "starts", "disturbance_paths", "disturbance_seed",
                     "stress_scale", "planning_paths", "conservative_planning_paths")
SAC_METRICS = {"critic_loss": "critic_loss", "actor_loss": "actor_loss"}
CHARGING_CONTROLLER_METRICS = {"charging_minutes": "minutes", "delivered_wh": "wh", "budget_hit_pct": ("hit", 100),
                               "max_shortfall_wh": "max_shortfall_wh", "worst_10_shortfall_wh": "tail_shortfall_wh",
                               "episodes": "episodes"}
DISCHARGE_CONTROLLER_METRICS = {"mean_soh_loss_pp": "soh_loss_pp", "worst_10_soh_loss_pp": "tail_loss_pp",
                                "max_soh_loss_pp": "max_loss_pp", "budget_hit_pct": ("budget_hit", 100),
                                "support_stop_pct": ("unsupported_stop", 100)}


def lifespan_chart_runs(rolling, fixed):
    """Log a paired recorded trajectory for the native MLflow line charts."""
    shown = []
    for report, name, chart, measured, prediction in (
        (fixed, "soh_trajectories.csv", "soh_pct", "observed_soh_pct", "revised_fixed_soh_pct"),
        (rolling, "rul_predictions.csv", "rul_cycles", "observed_rul_cycles", "selected_rul_cycles"),
    ):
        eligible = [row for row in report.rows(name) if row["charge_rate_c"] == "3"
                    and (report.notebook == 11 or (row["initializer"], row["landmark_cycle"]) == ("charge", "100"))
                    and row[measured] and row[prediction]]
        groups = grouped(eligible, ("cell_id",))
        cell, = min(key for key, records in groups.items() if len(records) > 1)
        records = groups[(cell,)]
        params = {"cell_id": cell, "charge_rate_c": 3, "step_axis": "operating_cycle", "trajectory": chart}
        for role, label, field in (("measured", "Measured", measured), ("predicted", "Predicted", prediction)):
            target = "SOH" if chart == "soh_pct" else "RUL"
            shown.append(Run(f"{label} {target} · {cell}", "held_out_trajectory", report.notebook,
                             {**params, "series": role}, metric_series(records, {chart: field}, "cycle"),
                             {"run_kind": "chart_trajectory", "model_or_policy": role}))
    return shown


def lifespan(rolling, fixed):
    from .plots import lifespan_plots

    runs = []
    for target in ("soh", "rul"):
        selected = rolling.rows(f"{target}_metrics.csv")
        conditions = ("start_cycle", "origin_window", "charge_rate_c", "variant")
        if target == "rul":
            conditions += ("actual_rul_window",)
        unit = "pp" if target == "soh" else "cycles"
        for key, rows in grouped(selected, conditions).items():
            tags = dict(zip(conditions, key))
            params = {**tags, "target": target, "forecast_mode": "rolling"}
            if target == "soh":
                params["step_axis"] = "forecast_horizon_cycles"
            details = " ".join(key)
            run = Run(f"{target.upper()} rolling · {details}", "held_out_forecast", 11, params,
                      metric_series(rows, {f"mae_{unit}": "mae", f"max_error_{unit}": "worst",
                                           "coverage_pct": "coverage_pct", "scored_points": "scored_points", "cells": "cells"},
                                    "horizon_cycles" if target == "soh" else None),
                      {"model_or_policy": tags["variant"]})
            runs.append(run)
    for row in fixed.rows("metrics.csv"):
        name = f"SOH fixed · {row['model']} · {row['charge_rate_c']}C · cycle {row['landmark_cycle']} · {row['initializer']}"
        params = {key: row[key] for key in ("model", "charge_rate_c", "landmark_cycle", "initializer")}
        runs.append(Run(name, "held_out_forecast", 12, {**params, "target": "soh", "forecast_mode": "fixed"},
                        metric_series([row], {key: key for key in (
                            "full_mae_pp", "full_max_pp", "last20_mae_pp", "last20_max_pp", "horizon_10_mae_pp",
                            "horizon_50_mae_pp", "full_cells", "last20_cells", "full_points", "last20_points")}),
                        {"model_or_policy": row["model"]}))
    runs.extend(lifespan_chart_runs(rolling, fixed))
    return Experiment("XJTU SOH and RUL", "XJTU", runs,
                      listed(rolling, ["soh_metrics.csv", "rul_metrics.csv", "soh_predictions.csv", "rul_predictions.csv",
                                       "run_config.json", "summary.md"]) +
                      listed(fixed, ["metrics.csv", "soh_trajectories.csv", "summary.md"]),
                      lambda folder: lifespan_plots(rolling, fixed, folder))


def measured_replay(report):
    from .plots import measured_plots

    runs = []
    for row in report.rows("policy_metrics.csv"):
        policy = row["policy"]
        mapping = {"charging_minutes": "charge_minutes", "delivered_wh": "delivered_wh", "capacity_ah": "capacity_ah",
                   "budget_hit_pct": ("hit_rate", 100), "matched_decisions": "matched",
                   "matches_with_wh": "measured_wh", "eligible_decisions": "origins", "matched_batteries": "matched_batteries",
                   "budget_hit_lower_pct": ("hit_lower", 100), "budget_hit_upper_pct": ("hit_upper", 100)}
        runs.append(Run(POLICY_LABELS[policy], "recorded_exact_match", 16, {"policy": policy, "horizon_cycles": 5},
                        metric_series([row], mapping), {"model_or_policy": policy}))
    return Experiment("MIT-BIT Measured Replay", "MIT-BIT", runs,
                      listed(report, ["policy_metrics.csv", "decisions.csv", "comparisons_vs_fixed_1c.csv",
                                      "run_config.json", "summary.md"]),
                      lambda folder: measured_plots(report, folder))


def simulator_validation(report):
    from .plots import validation_plots

    units = {"cumulative_wh": "wh", "cumulative_minutes": "minutes", "final_ah": "ah"}
    runs = []
    for (cohort, group, target), rows in grouped(report.rows("validation_metrics.csv"), ("cohort", "group", "metric")).items():
        unit = units[target]
        for prefix, label in (("baseline", "Last same-rate observation"), ("model", "Rollout simulator")):
            mapping = {f"mae_{unit}": f"{prefix}_mae", f"worst_10_mae_{unit}": f"{prefix}_worst_decile_mae",
                       f"max_error_{unit}": f"{prefix}_max_error", "windows": "windows", "batteries": "batteries"}
            params = {"cohort": cohort, "group": group, "target": target, "method": prefix,
                      "step_axis": "forecast_horizon_cycles"}
            runs.append(Run(f"{label} · {cohort} {group} · {target}", "held_out_recorded_schedule", 17, params,
                            metric_series(rows, mapping, "horizon_cycles"), {"model_or_policy": prefix}))
    return Experiment("MIT-BIT Simulator Validation", "MIT-BIT", runs,
                      listed(report, ["validation_metrics.csv", "recorded_rollout_totals.csv",
                                      "recorded_trajectories.csv", "run_config.json", "summary.md"]),
                      lambda folder: validation_plots(report, folder))


def charging_forecast(report):
    from .plots import charging_forecast_plots

    runs = []
    for (target, model), rows in grouped(report.rows("forecast_metrics.csv"), ("target", "model")).items():
        mapping = {f"mae_{target}": "mae", f"worst_10_mae_{target}": "tail_mae", f"max_error_{target}": "max_error",
                   "windows": "windows", "mae_reduction_pct": "mean_reduction",
                   "tail_reduction_pct": "tail_reduction", "max_reduction_pct": "max_reduction"}
        mapping.update({key: (mapping[key], 100) for key in ("mae_reduction_pct", "tail_reduction_pct", "max_reduction_pct")})
        params = {"target": target, "model": model, "step_axis": "forecast_horizon_cycles"}
        runs.append(Run(f"{model} · {target}", "held_out_forecast", 22, params,
                        metric_series(rows, mapping, "horizon_cycles"), {"model_or_policy": model}))
    return Experiment("MIT-BIT Charging Forecast", "MIT-BIT", runs,
                      listed(report, ["forecast_metrics.csv", "forecast_predictions.csv", "forecast_selection.csv",
                                      "run_config.json", "summary.md"]),
                      lambda folder: charging_forecast_plots(report, folder))


def charging_controller(report):
    from .plots import charging_controller_plots

    runs = []
    for row in report.rows("controller_metrics.csv"):
        policy = row["policy"]
        label = "Fixed 1C" if policy == "fixed" else POLICY_LABELS[policy]
        params = {**parameters(report, CONTROLLER_CONFIG), "policy": policy, "horizon_cycles": 15}
        runs.append(Run(label, "controller_simulation", 22, params,
                        metric_series([row], CHARGING_CONTROLLER_METRICS),
                        {"model_or_policy": policy, "selected": row["selected"].lower()}))
    runs.extend(training(report, "sac_training.csv", "fold", "SAC",
                         {**SAC_METRICS, "entropy_temperature": "entropy_temperature"}, "updates", CONTROLLER_CONFIG))
    return Experiment("MIT-BIT Charging Controller", "MIT-BIT", runs,
                      listed(report, ["controller_metrics.csv", "controller_comparisons.csv", "controller_episodes.csv",
                                      "sac_training.csv", "measured_metrics.csv", "run_config.json", "summary.md"]),
                      lambda folder: charging_controller_plots(report, folder))


def discharge_forecast(report):
    from .plots import discharge_forecast_plots

    runs = []
    for (mode, target, role), rows in grouped(report.rows("refinement_metrics.csv"), ("mode", "target", "role")).items():
        unit = "pp" if target == "soh" else "wh"
        params = {"target": target, "model": role, "forecast_mode": mode,
                  "step_axis": "forecast_horizon_cycles" if mode == "fixed" else "elapsed_cycles"}
        mapping = {f"mae_{unit}": "mae", f"worst_10_mae_{unit}": "worst_10", f"max_error_{unit}": "max_error",
                   "windows": "windows", "mae_reduction_pct": "mae_reduction_pct",
                   "tail_reduction_pct": "tail_reduction_pct", "max_reduction_pct": "max_reduction_pct"}
        runs.append(Run(f"{role} · {target.upper()} · {mode}", "held_out_forecast", 23, params,
                        metric_series(rows, mapping, "cycles"), {"model_or_policy": role}))
    return Experiment("XJTU Discharge Forecast", "XJTU Random Walk", runs,
                      listed(report, ["refinement_metrics.csv", "refinement_predictions.csv", "refinement_selections.csv",
                                      "refinement_difficult_cases.csv", "run_config.json", "summary.md"]),
                      lambda folder: discharge_forecast_plots(report, folder))


def discharge_controller(report, ppo):
    from .plots import discharge_controller_plots

    runs = []
    for row in report.rows("controller_metrics.csv"):
        policy, test = row["policy"], row["evaluation"]
        label = {"fixed": "Fixed middle template", "rule": "SOH rule"}.get(policy, POLICY_LABELS.get(policy))
        params = {**parameters(report, CONTROLLER_CONFIG), "policy": policy, "evaluation": test, "horizon_cycles": 30}
        mapping = {**DISCHARGE_CONTROLLER_METRICS, "episodes": "episodes", "delivered_wh": "delivered_wh",
                   "max_shortfall_wh": "max_shortfall_wh"}
        runs.append(Run(f"{label} · {test}", "controller_simulation", 23, params, metric_series([row], mapping),
                        {"model_or_policy": policy, "selected": row["selected"].lower()}))
    for row in report.rows("controller_seed_metrics.csv"):
        policy, test, seed = row["policy"], row["evaluation"], int(row["seed"])
        name = f"{POLICY_LABELS[policy]} · {test} · seed {seed}"
        runs.append(Run(name, "controller_simulation_seed", 23,
                        {"policy": policy, "evaluation": test, "seed": seed, "horizon_cycles": 30},
                        metric_series([row], DISCHARGE_CONTROLLER_METRICS), {"model_or_policy": policy, "run_kind": "seed_evaluation"}))
    runs.extend(training(report, "sac_training.csv", "cell_id", "SAC",
                         {**SAC_METRICS, "entropy_temperature": "temperature"}, "updates", CONTROLLER_CONFIG))
    if ppo is not None:
        runs.extend(training(ppo, "training_log.csv", "cell_id", "PPO",
                             {"mean_reward": "mean_reward", "loss": "last_loss", "train_steps": "train_steps"},
                             "update", ("updates", "samples_per_update", "seeds")))
    files = listed(report, ["controller_metrics.csv", "controller_comparisons.csv", "controller_seed_metrics.csv",
                            "controller_episodes.csv", "sac_training.csv", "oracle_headroom.csv",
                            "run_config.json", "summary.md"])
    if ppo is not None:
        files.extend(listed(ppo, ["training_log.csv", "run_config.json", "summary.md"]))
    return Experiment("XJTU Discharge Controller", "XJTU Random Walk", runs, files,
                      lambda folder: discharge_controller_plots(report, ppo, folder))


def experiments(notebook=None, path=None):
    result = []
    if notebook is None:
        result.extend((lifespan(Report(11), Report(12)), measured_replay(Report(16)), simulator_validation(Report(17))))
    if notebook in (None, 22):
        report = Report(22, path)
        result.extend((charging_forecast(report), charging_controller(report)))
    if notebook in (None, 23):
        report = Report(23, path)
        ppo = None
        try:
            ppo = Report(20)
        except FileNotFoundError:
            if notebook is None:
                raise
        result.extend((discharge_forecast(report), discharge_controller(report, ppo)))
    return result
