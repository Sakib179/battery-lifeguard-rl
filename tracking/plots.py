"""Report-backed figures for the experiment overview artifacts."""

from collections import defaultdict
from statistics import mean

from matplotlib import pyplot as plt

from .reports import POLICY_LABELS, number

MEASURED = "#2c4e81"
RECOMMENDED = "#007969"
BASELINE = "#646e7c"
ACCENT = "#a85726"
COLORS = (MEASURED, RECOMMENDED, ACCENT, BASELINE)
ERRORS = (("mae", "Mean absolute error"), ("tail", "Worst 10% mean"), ("max", "Maximum error"))


def figure(title, rows=1, cols=1, width=10, height=3.6):
    fig, axes = plt.subplots(rows, cols, figsize=(width, rows * height), squeeze=False, layout="constrained")
    fig.suptitle(title, fontsize=14, fontweight="semibold")
    for ax in axes.flat:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color="#dce3e8", linewidth=.6)
        ax.set_axisbelow(True)
    return fig, axes


def save(fig, folder, name):
    fig.savefig(folder / f"{name}.png", dpi=150, facecolor="white")
    plt.close(fig)


def line(ax, rows, x, y, color, label):
    matched = sorted((float(row[x]), number(row[y])) for row in rows if number(row[y]) is not None)
    if matched:
        xs, ys = zip(*matched)
        ax.plot(xs, ys, marker="o", markersize=3, linewidth=1.7, color=color, label=label)
        return xs
    return ()


def bars(ax, categories, series):
    count = len(series)
    size = .82 / count
    for i, (label, values, color) in enumerate(series):
        offset = (i-(count-1)/2)*size
        ax.bar([j+offset for j in range(len(categories))], values, width=size, color=color, label=label)
    ax.set_xticks(range(len(categories)), categories, rotation=26, ha="right")
    if count > 1:
        ax.legend(frameon=False, fontsize="small")


def parity(ax, groups, unit):
    extent = []
    for label, source, measured, predicted, color in groups:
        coords = [(number(row[measured]), number(row[predicted])) for row in source]
        coords = [(x, y) for x, y in coords if x is not None and y is not None]
        if not coords:
            continue
        x, y = zip(*coords)
        extent.extend(x+y)
        ax.scatter(x, y, s=9, alpha=.4, label=label, color=color, edgecolors="none")
    if extent:
        low, high = min(extent), max(extent)
        ax.plot([low, high], [low, high], linestyle="--", linewidth=1, color=BASELINE)
    ax.set(xlabel=f"Measured ({unit})", ylabel=f"Predicted ({unit})")
    ax.legend(frameon=False, fontsize="small")


def lifespan_plots(rolling, fixed, folder):
    fixed_rows = fixed.rows("soh_trajectories.csv")
    rul_rows = rolling.rows("rul_predictions.csv")
    fig, grid = figure("Battery aging forecasts on held-out XJTU cells", 2, 2, height=3)
    for index, rate in enumerate(("2", "3")):
        eligible = [row for row in fixed_rows if row["landmark_cycle"] == "100" and row["initializer"] == "charge"
                    and row["charge_rate_c"] == rate]
        cell = min(row["cell_id"] for row in eligible)
        track = [row for row in eligible if row["cell_id"] == cell]
        ax = grid[0, index]
        for column, color, label in (("observed_soh_pct", MEASURED, "Measured"),
                                     ("previous_fixed_soh_pct", BASELINE, "Previous fixed"),
                                     ("revised_fixed_soh_pct", RECOMMENDED, "Revised fixed")):
            line(ax, track, "cycle", column, color, label)
            ax.lines[-1].set_marker("")
        ax.set(title=cell, xlabel="Cycle", ylabel="SOH (%)")
        ax.legend(frameon=False, fontsize="small")
        available = [row for row in rul_rows if row["charge_rate_c"] == rate and row["observed_rul_cycles"]]
        cell = min(row["cell_id"] for row in available)
        track = [row for row in available if row["cell_id"] == cell]
        ax = grid[1, index]
        for column, color, label in (("observed_rul_cycles", MEASURED, "Observed EOL"),
                                     ("earlier_rul_cycles", BASELINE, "Earlier forecast"),
                                     ("selected_rul_cycles", RECOMMENDED, "Selected forecast")):
            line(ax, track, "cycle", column, color, label)
        ax.set(title=cell, xlabel="Forecast origin (cycle)", ylabel="RUL (cycles)")
        ax.legend(frameon=False, fontsize="small")
    save(fig, folder, "01-measured-and-forecast-curves")

    fig, grid = figure("Error by charge rate · cycle 100 starts", 2, 2, height=3.3)
    for j, target in enumerate(("soh", "rul")):
        records = rolling.rows(f"{target}_metrics.csv")
        cohort = [r for r in records if r["start_cycle"] == "100" and r["origin_window"] == "all"
                  and (r.get("horizon_cycles") == "50" if target == "soh" else r.get("actual_rul_window") == "all")]
        for i, metric in enumerate(("mae", "worst")):
            ax = grid[j, i]
            by_key = {(r["variant"], r["charge_rate_c"]): float(r[metric]) for r in cohort}
            bars(ax, ["2C", "3C"], [(label, [by_key[(variant, rate)] for rate in ("2", "3")], color)
                                   for variant, label, color in (("earlier", "Earlier rolling", BASELINE),
                                                                  ("selected", "Selected rolling", RECOMMENDED))])
            title = "50-cycle SOH" if target == "soh" else "RUL"
            error = "mean error" if metric == "mae" else "maximum error"
            ax.set(title=f"{title} {error}", ylabel="pp" if target == "soh" else "Cycles")
    save(fig, folder, "02-errors-by-charge-rate")


def measured_plots(report, folder):
    rows = report.rows("policy_metrics.csv")
    labels = [POLICY_LABELS[row["policy"]] for row in rows]
    fig, axes = figure("Recorded matches · five-cycle charging decisions", 1, 3, width=13, height=4.1)
    for ax, (column, unit, scale) in zip(axes.flat, (("charge_minutes", "Mean charging time (min)", 1),
                                                   ("hit_rate", "Energy target hit (%)", 100),
                                                   ("matched", "Number of decisions", 1))):
        values = [float(row[column])*scale for row in rows]
        series = [("Recorded matches", values, MEASURED)]
        if column == "matched":
            series.append(("Matches with Wh", [int(row["measured_wh"]) for row in rows], RECOMMENDED))
        bars(ax, labels, series)
        ax.set(ylabel=unit)
        if column == "hit_rate":
            ax.set_ylim(0, 105)
    save(fig, folder, "01-recorded-policy-comparison")


def validation_plots(report, folder):
    metrics = report.rows("validation_metrics.csv")
    totals = report.rows("recorded_rollout_totals.csv")
    targets = (("cumulative_wh", "Delivered energy", "Wh"),
               ("cumulative_minutes", "Charging time", "min"), ("final_ah", "Final capacity", "Ah"))
    fig, grid = figure("Simulator validation on recorded charging schedules", 2, 3, width=13, height=3.2)
    for i, cohort in enumerate(("randomized", "fixed")):
        for j, (key, label, unit) in enumerate(targets):
            ax = grid[i, j]
            records = [row for row in metrics if (row["cohort"], row["group"], row["metric"]) == (cohort, "all", key)]
            line(ax, records, "horizon_cycles", "baseline_mae", BASELINE, "Last same-rate observation")
            line(ax, records, "horizon_cycles", "model_mae", RECOMMENDED, "Simulator")
            ax.set(title=f"{cohort.title()} · {label}", xlabel="Operating cycles ahead", ylabel=f"MAE ({unit})", xticks=[5, 15, 30])
            ax.legend(frameon=False, fontsize="small")
    save(fig, folder, "01-error-by-horizon")
    fig, axes = figure("30-cycle recorded rollouts · measured versus predicted", 1, 3, width=13)
    for ax, (key, label, unit) in zip(axes.flat, targets):
        parity(ax, [(cohort.title(), [r for r in totals if r["cohort"] == cohort and r["horizon_cycles"] == "30"],
                     "observed_"+key, "predicted_"+key, color)
                    for cohort, color in (("randomized", MEASURED), ("fixed", ACCENT))], unit)
        ax.set_title(label)
    save(fig, folder, "02-measured-versus-predicted")


def error_panels(rows, targets, models, columns, xlabel, title, folder, name, step):
    fig, grid = figure(title, len(columns), len(targets), width=10, height=2.55)
    for j, (target, label, unit) in enumerate(targets):
        for i, (key, metric) in enumerate(columns):
            ax = grid[i, j]
            ticks = set()
            for model, color, legend in models:
                selected = [row for row in rows if row["target"] == target and row["model"] == model]
                ticks.update(line(ax, selected, step, key, color, legend))
            ax.set(title=f"{label} · {metric}", ylabel=unit, xticks=sorted(ticks), xlabel=xlabel)
            if i == 0:
                ax.legend(frameon=False, fontsize="small")
    save(fig, folder, name)


def charging_forecast_plots(report, folder):
    metrics = report.rows("forecast_metrics.csv")
    targets = (("wh", "Delivered energy", "Wh"), ("minutes", "Charging time", "min"))
    models = (("ridge", BASELINE, "Notebook 18 Ridge"), ("selected", RECOMMENDED, "Refined forecast"))
    columns = (("mae", ERRORS[0][1]), ("tail_mae", ERRORS[1][1]), ("max_error", ERRORS[2][1]))
    error_panels(metrics, targets, models, columns, "Operating cycles ahead", "Charging forecast errors",
                 folder, "01-error-by-horizon", "horizon_cycles")
    records = [r for r in report.rows("forecast_predictions.csv") if r["horizon_cycles"] == "15"]
    fig, axes = figure("15 cycles · recorded outcomes versus forecasts", 1, 2)
    for ax, (target, title, unit) in zip(axes.flat, targets):
        parity(ax, [(legend, [r for r in records if r["model"] == model], "observed_"+target, "predicted_"+target, color)
                    for model, color, legend in models], unit)
        ax.set_title(title)
    save(fig, folder, "02-measured-versus-predicted")


def training_plot(report, filename, step, columns, folder, name, title):
    data = report.rows(filename)
    fig, axes = figure(title, 1, len(columns), width=12)
    for ax, (key, label) in zip(axes.flat, columns):
        groups = defaultdict(list)
        for row in data:
            groups[int(row[step])].append(float(row[key]))
        points = sorted(groups)
        ax.fill_between(points, [min(groups[x]) for x in points], [max(groups[x]) for x in points],
                        alpha=.18, color=MEASURED, label="Min–max across runs")
        ax.plot(points, [mean(groups[x]) for x in points], marker="o", color=MEASURED, label="Mean across runs")
        ax.set(title=label, xlabel="Training update")
        ax.legend(frameon=False, fontsize="small")
    save(fig, folder, name)


def charging_controller_plots(report, folder):
    rows = report.rows("controller_metrics.csv")
    labels = ["Fixed 1C" if r["policy"] == "fixed" else POLICY_LABELS[r["policy"]] for r in rows]
    fig, axes = figure("Matched charging simulation · 15-cycle energy target", 1, 2)
    tradeoff, shortfall = axes[0]
    for row, label, color in zip(rows, labels, COLORS):
        tradeoff.scatter(float(row["minutes"]), 100*float(row["hit"]), color=color, label=label, s=55)
    tradeoff.set(xlabel="Mean charging time (min)", ylabel="Energy budget hit (%)")
    tradeoff.legend(frameon=False, fontsize="small")
    bars(shortfall, labels, [("Maximum", [float(row["max_shortfall_wh"]) for row in rows], RECOMMENDED)])
    shortfall.set(ylabel="Worst energy shortfall (Wh)")
    save(fig, folder, "01-time-and-energy-tradeoff")
    training_plot(report, "sac_training.csv", "updates",
                  (("critic_loss", "Critic loss"), ("actor_loss", "Actor loss"), ("entropy_temperature", "Temperature")),
                  folder, "02-sac-training", "SAC charging · training history")


def discharge_forecast_plots(report, folder):
    metrics = [dict(row, model=row["role"]) for row in report.rows("refinement_metrics.csv")]
    targets = (("soh", "SOH", "pp"), ("wh", "Delivered energy", "Wh"))
    models = (("original", BASELINE, "Original"), ("incumbent", MEASURED, "Previous"),
              ("recommended", RECOMMENDED, "Recommended"))
    columns = (("mae", ERRORS[0][1]), ("worst_10", ERRORS[1][1]), ("max_error", ERRORS[2][1]))
    fixed = [r for r in metrics if r["mode"] == "fixed"]
    rolling = [r for r in metrics if r["mode"] == "rolling"] + [dict(r, cycles="0") for r in fixed if r["cycles"] == "30"]
    error_panels(fixed, targets, models, columns, "Operating cycles ahead", "Discharge forecasts issued at the start",
                 folder, "01-fixed-origin-errors", "cycles")
    error_panels(rolling, targets, models, columns, "Cycles elapsed before forecast", "Refreshes for the same 30-cycle endpoint",
                 folder, "02-rolling-errors", "cycles")

    records = report.rows("refinement_predictions.csv")
    fig, grid = figure("Forecasts for a fixed endpoint · example batteries", 2, 2, height=3)
    for i, (cell, start) in enumerate((("XJTU_RW_battery-3", "307"), ("XJTU_RW_battery-5", "241"))):
        for j, (target, label, unit) in enumerate(targets):
            ax = grid[i, j]
            source = [dict(row, cycles="0" if row["mode"] == "fixed" else row["cycles"]) for row in records
                      if (row["cell_id"], row["start_cycle"], row["target"]) == (cell, start, target)
                      and (row["mode"] == "rolling" or row["cycles"] == "30")]
            if source:
                ax.axhline(float(source[0]["measured"]), color=ACCENT, linestyle="--", label="Measured endpoint")
                line(ax, source, "cycles", "incumbent", MEASURED, "Previous")
                line(ax, source, "cycles", "recommended", RECOMMENDED, "Recommended")
            ax.set(title=f"{cell} · start {start}", xlabel="Operating cycles elapsed", xticks=[0, 10, 20],
                   ylabel=f"{label} ({'%' if unit == 'pp' else unit})")
            if source:
                ax.legend(frameon=False, fontsize="small")
    save(fig, folder, "03-battery-cases")


def discharge_controller_plots(report, ppo, folder):
    source = report.rows("controller_metrics.csv")
    rows = {mode: {r["policy"]: r for r in source if r["evaluation"] == mode} for mode in ("original", "stress")}
    policies = ("lookahead", "mpc", "risk", "fqi", "sac", "ppo", "fixed", "rule")
    labels = ("Lookahead", "Forecast MPC", "Risk-aware MPC", "FQI", "SAC", "PPO", "Fixed middle", "SOH rule")
    fig, grid = figure("Matched discharge policies · original and higher disturbance", 2, 3, width=14, height=3.5)
    for ax, (column, label, scale) in zip(grid.flat, (
        ("soh_loss_pp", "Mean SOH loss (pp)", 1), ("tail_loss_pp", "Worst 10% SOH loss (pp)", 1),
        ("max_loss_pp", "Maximum SOH loss (pp)", 1), ("budget_hit", "Budget hit (%)", 100),
        ("unsupported_stop", "Support stop (%)", 100), ("max_shortfall_wh", "Maximum Wh shortfall", 1),
    )):
        bars(ax, labels, [(mode.title(), [float(rows[mode][p][column])*scale for p in policies], color)
                          for mode, color in (("original", MEASURED), ("stress", ACCENT))])
        ax.set(ylabel=label)
    save(fig, folder, "01-discharge-policy-comparison")
    training_plot(report, "sac_training.csv", "updates",
                  (("critic_loss", "Critic loss"), ("actor_loss", "Actor loss"), ("temperature", "Temperature")),
                  folder, "02-sac-training", "SAC discharge · training history")
    if ppo is not None:
        training_plot(ppo, "training_log.csv", "update", (("mean_reward", "Mean reward"), ("last_loss", "Loss")),
                      folder, "03-ppo-training", "PPO discharge · training history")
