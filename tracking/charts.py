"""Focused native MLflow chart views for the saved LifeGuard-RL runs."""

from dataclasses import dataclass
from hashlib import sha256
import json
import re
from urllib.parse import urlencode


@dataclass(frozen=True)
class ChartView:
    experiment: str
    title: str
    filters: str
    metrics: tuple[str, ...]
    variants: tuple[str, ...] = ()


SOH_RUL = "XJTU SOH and RUL"
CHARGE_FORECAST = "MIT-BIT Charging Forecast"
CHARGE_POLICY = "MIT-BIT Charging Controller"
DISCHARGE_FORECAST = "XJTU Discharge Forecast"
DISCHARGE_POLICY = "XJTU Discharge Controller"


def score_metrics(unit):
    return f"mae_{unit}", f"worst_10_mae_{unit}", f"max_error_{unit}"


VIEWS = {
    "discharge-soh": ChartView(DISCHARGE_FORECAST, "Discharge SOH error by forecast horizon",
                               "params.target = 'soh' and params.forecast_mode = 'fixed'",
                               score_metrics("pp"), ("original", "recommended")),
    "discharge-wh": ChartView(DISCHARGE_FORECAST, "Discharge energy error by forecast horizon",
                              "params.target = 'wh' and params.forecast_mode = 'fixed'",
                              score_metrics("wh"), ("original", "recommended")),
    "rolling-soh": ChartView(DISCHARGE_FORECAST, "Discharge SOH error after 10 and 20 cycles",
                             "params.target = 'soh' and params.forecast_mode = 'rolling'",
                             score_metrics("pp"), ("original", "recommended")),
    "rolling-wh": ChartView(DISCHARGE_FORECAST, "Discharge energy error after 10 and 20 cycles",
                            "params.target = 'wh' and params.forecast_mode = 'rolling'",
                            score_metrics("wh"), ("original", "recommended")),
    "soh-trajectory": ChartView(SOH_RUL, "Measured versus predicted SOH across cycles",
                                "params.trajectory = 'soh_pct'", ("soh_pct",)),
    "rul-trajectory": ChartView(SOH_RUL, "Observed versus predicted RUL across cycles",
                                "params.trajectory = 'rul_cycles'", ("rul_cycles",)),
    "charging-time": ChartView(CHARGE_FORECAST, "Charging time error by forecast horizon",
                               "params.target = 'minutes'", score_metrics("minutes"), ("ridge", "selected")),
    "charging-wh": ChartView(CHARGE_FORECAST, "Charging energy error by forecast horizon",
                             "params.target = 'wh'", score_metrics("wh"), ("ridge", "selected")),
    "charging-policies": ChartView(CHARGE_POLICY, "Charging policies: minutes, budget and shortfall",
                                   "tags.evidence = 'controller_simulation'",
                                   ("charging_minutes", "budget_hit_pct", "max_shortfall_wh")),
    "discharge-policies": ChartView(DISCHARGE_POLICY, "Discharge policies: SOH loss and budget",
                                    "tags.evidence = 'controller_simulation' and params.evaluation = 'original'",
                                    ("mean_soh_loss_pp", "worst_10_soh_loss_pp", "budget_hit_pct")),
    "charging-sac": ChartView(CHARGE_POLICY, "Charging SAC: loss and entropy by training update",
                              "tags.run_kind = 'training' and params.fold = '1'",
                              ("critic_loss", "actor_loss", "entropy_temperature")),
    "discharge-sac": ChartView(DISCHARGE_POLICY, "Discharge SAC: loss and entropy by training update",
                               "tags.run_kind = 'training' and params.algorithm = 'SAC' and "
                               "params.cell_id = 'XJTU_RW_battery-1'",
                               ("critic_loss", "actor_loss", "entropy_temperature")),
    "discharge-ppo": ChartView(DISCHARGE_POLICY, "Discharge PPO: reward and loss by training update",
                               "tags.run_kind = 'training' and params.algorithm = 'PPO' and "
                               "params.cell_id = 'XJTU_RW_battery-1'",
                               ("mean_reward", "loss")),
    "measured-replay": ChartView("MIT-BIT Measured Replay", "Recorded charging matches and target hits",
                                  "tags.evidence = 'recorded_exact_match'",
                                  ("charging_minutes", "budget_hit_pct", "matched_decisions")),
    "simulator-validation": ChartView("MIT-BIT Simulator Validation", "Simulator energy errors on recorded schedules",
                                       "params.cohort = 'randomized' and params.target = 'cumulative_wh'",
                                       score_metrics("wh")),
}


def chart_url(client, key, port):
    chart = VIEWS[key]
    experiment = client.get_experiment_by_name(f"LifeGuard-RL / {chart.experiment}")
    if experiment is None or experiment.lifecycle_stage != "active":
        return None
    exp_id = experiment.experiment_id
    overview = client.search_runs([exp_id], "tags.run_kind = 'overview' and attributes.status = 'FINISHED'",
                                  order_by=["attributes.start_time DESC"], max_results=1)
    if not overview:
        return None
    fingerprint = overview[0].data.tags["report_fingerprint"]
    query = f"{chart.filters} and tags.report_fingerprint = '{fingerprint}' and attributes.status = 'FINISHED'"
    runs = client.search_runs([exp_id], query, max_results=100)
    ids = [
        run.info.run_id for run in runs if set(chart.metrics).issubset(run.data.metrics)
        and (not chart.variants or run.data.tags.get("model_or_policy") in chart.variants)
    ]
    if not ids:
        return None
    ids_sql = ", ".join(repr(run_id) for run_id in sorted(ids))
    regex = "|".join(re.escape(key) for key in chart.metrics)
    # MLflow's Share action stores this state on the experiment. A shared
    # chart link restores the filters even when the browser has an older view.
    state = json.dumps({
        "searchFilter": f"attributes.run_id IN ({ids_sql})",
        "chartsSearchFilter": f"^({regex})$",
        "selectedColumns": [],
        "runsExpanded": {},
        "runsPinned": [],
        "runsHiddenMode": "SHOW_ALL",
        "runsHidden": [],
        "runsVisibilityMap": {},
        "viewMaximized": False,
        "runListHidden": False,
        "isAccordionReordered": False,
        "useGroupedValuesInCharts": True,
        "hideEmptyCharts": True,
        "groupBy": None,
        "groupsExpanded": {},
        "autoRefreshEnabled": False,
        "globalLineChartConfig": {"xAxisKey": "step", "lineSmoothness": 0, "selectedXAxisMetricKey": ""},
    }, separators=(",", ":"), sort_keys=True)
    view_key = sha256(state.encode()).hexdigest()
    tag = f"mlflow.sharedViewState.{view_key}"
    if experiment.tags.get(tag) != state:
        client.set_experiment_tag(exp_id, tag, state)
    params = urlencode({"compareRunsMode": "CHART", "viewStateShareKey": view_key})
    return f"http://127.0.0.1:{port}/#/experiments/{exp_id}?{params}"
