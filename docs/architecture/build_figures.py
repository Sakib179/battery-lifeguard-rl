"""Render LifeGuard-RL architecture figures as PDF, SVG, and PNG.

Run with the project's Python environment. Matplotlib is the only dependency.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
from matplotlib.path import Path as PlotPath


OUTPUT = Path(__file__).resolve().parent
WIDTH, HEIGHT = 1440, 810
BACKGROUND = "#F4F7FB"
WHITE = "#FFFFFF"
INK = "#12243A"
BODY = "#41546B"
MUTED = "#516680"
LINE = "#D2DCE8"
ARROW = "#586D85"
COLORS = {
    "data": ("#1D5F99", "#E8F2FB", "#B6D1EA"),
    "model": ("#087069", "#E3F3EF", "#AFD7CB"),
    "control": ("#92510B", "#FCF0E1", "#E8CCA9"),
    "evidence": ("#604788", "#F0ECF8", "#D3C7E8"),
    "serve": ("#344E68", "#EAF0F7", "#C3D1E1"),
}

matplotlib.rcParams.update({
    "font.family": "DejaVu Sans",
    "pdf.fonttype": 42,
    "svg.fonttype": "none",
    "svg.hashsalt": "lifeguard-architecture",
})


class Figure:
    def __init__(self, number, section, title, subtitle, source):
        self.fig = plt.figure(figsize=(WIDTH / 100, HEIGHT / 100), dpi=100, facecolor=BACKGROUND)
        self.ax = self.fig.add_axes((0, 0, 1, 1))
        self.ax.set(xlim=(0, WIDTH), ylim=(HEIGHT, 0))
        self.ax.set_axis_off()
        self.text_bounds = []

        self.ax.add_patch(Rectangle((0, 0), WIDTH, 7, color=INK, linewidth=0))
        self.ax.add_patch(Rectangle((0, 0), 315, 7, color=COLORS["model"][0], linewidth=0))
        self.box(62, 34, 28, 28, WHITE, edge=COLORS["model"][2], radius=6)
        self.ax.plot([68, 72, 75, 78, 84], [49, 49, 42, 54, 48], color=COLORS["model"][0],
                     lw=1.65, solid_capstyle="round", zorder=5)
        self.text(101, 40, "LIFEGUARD-RL", 10.2, weight="bold", color=INK, max_width=157)
        self.text(1378, 40, f"{section.upper()}   /   {number:02d}", 9.3, weight="bold", color=MUTED, align="right")
        self.text(61, 80, title, 28, weight="bold", color=INK, max_width=1318)
        self.text(63, 136, subtitle, 11.6, color=BODY, max_width=1315)
        self.line([(62, 168), (1378, 168)], LINE, 1.0)
        self.line([(62, 743), (1378, 743)], LINE, 1.0)
        self.text(62, 761, source, 8.4, color=MUTED, max_width=1140)
        self.text(1378, 761, "SYSTEM DESIGN", 8.3, weight="bold", color=MUTED, align="right")

    def text(self, x, y, value, size, *, color=BODY, weight="normal", align="left",
             max_width=None, max_height=None):
        obj = self.ax.text(x, y, value, fontsize=size, color=color, fontweight=weight,
                           va="top", ha=align, linespacing=1.36, zorder=5)
        self.text_bounds.append((obj, max_width, max_height))
        return obj

    def box(self, x, y, w, h, fill, *, edge="none", radius=13, linewidth=1, zorder=3):
        patch = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={radius}",
                               facecolor=fill, edgecolor=edge, lw=linewidth, zorder=zorder)
        self.ax.add_patch(patch)
        return patch

    def line(self, points, color=ARROW, width=1.5, dashed=False):
        xs, ys = zip(*points)
        self.ax.plot(xs, ys, color=color, lw=width, ls=(0, (4, 3)) if dashed else "-",
                     solid_capstyle="round", zorder=2)

    def arrow(self, points, *, color=ARROW, dashed=False):
        # Round the corners of orthogonal paths while keeping the arrow aligned to the final segment.
        verts, codes = [points[0]], [PlotPath.MOVETO]
        for prev, point, following in zip(points, points[1:], points[2:]):
            d1 = abs(point[0] - prev[0]) + abs(point[1] - prev[1])
            d2 = abs(following[0] - point[0]) + abs(following[1] - point[1])
            r = min(11, d1 / 2, d2 / 2)
            verts.extend((
                (point[0] + (prev[0] - point[0]) * r / d1, point[1] + (prev[1] - point[1]) * r / d1),
                point,
                (point[0] + (following[0] - point[0]) * r / d2, point[1] + (following[1] - point[1]) * r / d2),
            ))
            codes.extend((PlotPath.LINETO, PlotPath.CURVE3, PlotPath.CURVE3))
        verts.append(points[-1])
        codes.append(PlotPath.LINETO)
        self.ax.add_patch(FancyArrowPatch(path=PlotPath(verts, codes), arrowstyle="-|>",
                                         mutation_scale=14, color=color, lw=1.65,
                                         linestyle=(0, (4, 3)) if dashed else "-", zorder=2.4))

    def caption(self, x, y, label, kind, *, width):
        accent, tint, edge = COLORS[kind]
        self.box(x, y, width, 27, tint, edge=edge, radius=6, linewidth=0.7, zorder=4)
        self.text(x + width / 2, y + 5, label, 8.2, color=accent, weight="bold",
                  align="center", max_width=width - 18, max_height=17)

    def section(self, x, y, title, kind):
        accent = COLORS[kind][0]
        self.box(x, y + 4, 15, 4, accent, radius=2, linewidth=0)
        self.text(x + 24, y, title.upper(), 9.3, color=accent, weight="bold", max_width=1300 - x + 50)

    def card(self, x, y, width, height, kind, tag, title, lines):
        accent, tint, edge = COLORS[kind]
        self.box(x, y, width, height, WHITE, edge=edge)
        self.box(x + 16, y + 16, 14, 14, tint, edge=edge, radius=4, linewidth=0.7)
        self.box(x + 20.5, y + 20.5, 5, 5, accent, radius=1.5, linewidth=0)
        self.text(x + 38, y + 16, tag.upper(), 8.4, color=accent, weight="bold", max_width=width - 52, max_height=17)
        title_lines = title.splitlines()
        self.text(x + 16, y + 44, title, 12.6, color=INK, weight="bold",
                  max_width=width - 32, max_height=28 * len(title_lines))
        content_y = y + 75 + 23 * (len(title_lines) - 1)
        self.text(x + 16, content_y, "\n".join(lines), 10.1, max_width=width - 32,
                  max_height=y + height - content_y - 12)

    def ribbon(self, x, y, width, kind, title, details):
        accent, tint, edge = COLORS[kind]
        self.box(x, y, width, 60, tint, edge=edge, radius=10, linewidth=0.85)
        self.box(x + 13, y + 14, 4, 32, accent, radius=2, linewidth=0)
        self.text(x + 28, y + 11, title, 10.0, color=accent, weight="bold", max_width=width - 47)
        self.text(x + 28, y + 31, details, 9.5, color=INK, max_width=width - 47, max_height=20)

    def row(self, y, height, nodes):
        cols = (62, 405, 748, 1091)
        width = 287
        for x, node in zip(cols, nodes, strict=True):
            self.card(x, y, width, height, *node)
        mid = y + height / 2
        for a, b in zip(cols[:-1], cols[1:]):
            self.arrow([(a + width + 6, mid), (b - 8, mid)])

    def validate(self):
        self.fig.canvas.draw()
        renderer = self.fig.canvas.get_renderer()
        for obj, max_width, max_height in self.text_bounds:
            box = obj.get_window_extent(renderer)
            if max_width is not None and box.width > max_width:
                raise ValueError(f"{obj.get_text()!r} is {box.width:.1f}px wide, limit {max_width}px")
            if max_height is not None and box.height > max_height:
                raise ValueError(f"{obj.get_text()!r} is {box.height:.1f}px high, limit {max_height}px")
            if not (0 <= box.x0 <= box.x1 <= WIDTH and 0 <= box.y0 <= box.y1 <= HEIGHT):
                raise ValueError(f"{obj.get_text()!r} falls outside the figure")


def overall():
    f = Figure(1, "Overview", "LifeGuard-RL system architecture",
               "Recorded battery measurements support two research paths and three ways to inspect their saved outputs.",
               "Sources  ·  Notebooks 01–23  /  Saved benchmark exports  /  Streamlit, MLflow and static dashboard loaders")
    f.section(62, 193, "Battery health and life forecasting", "model")
    f.row(222, 151, (
        ("data", "Recorded input", "XJTU battery records", ["2C and 3C charge cycles", "Voltage, current and capacity", "23 cells from one battery design"]),
        ("data", "Preparation", "Features and labels", ["Available charge and discharge", "Capacity-based SOH", "Verified 80% end-of-life label"]),
        ("model", "Held-out forecasts", "Health and life models", ["Current SOH from charge data", "Rolling SOH and RUL updates", "Fixed-anchor SOH curves"]),
        ("evidence", "Notebook outputs", "SOH and RUL results", ["Held-out predictions and labels", "Average and largest errors", "Per-battery trajectories"]),
    ))
    f.section(62, 407, "Charging and discharging decisions", "control")
    f.row(436, 151, (
        ("data", "Recorded input", "Operating protocols", ["MIT–BIT randomized charging", "XJTU Random Walk discharge", "Energy and reference tests"]),
        ("model", "Digital twins", "Transition simulators", ["Charging time and delivered Wh", "Reference-test SOH and Wh", "Calibrated on training batteries"]),
        ("control", "Controller benchmarks", "Matched policy trials", ["Fixed and learned baselines", "Shared start and energy target", "Supported operating actions"]),
        ("evidence", "Selected controllers", "MPC and Lookahead", ["Charging · fixed-budget MPC", "Discharging · Original Lookahead", "Policy scores are simulated"]),
    ))
    f.ribbon(62, 650, 1316, "serve", "Saved notebook outputs",
             "Streamlit replays selected cases  ·  MLflow compares experiment metrics and artifacts  ·  Static dashboard exposes detailed study views")
    f.line([(1384, 297.5), (1402, 297.5), (1402, 511.5), (1384, 511.5)], COLORS["evidence"][0], 1.45)
    f.arrow([(1402, 511.5), (1402, 680), (1385, 680)], color=COLORS["evidence"][0])
    return f


def soh():
    f = Figure(2, "Health estimation", "Three ways to estimate battery health",
               "Choose the forecast path according to which measurements are available and when the estimate must be updated.",
               "Sources  ·  XJTU SOH benchmarks  /  Notebook 10 error audit  /  Notebook 11 rolling forecasts  /  Notebook 12 fixed forecasts")
    f.section(62, 194, "Reference data", "data")
    f.section(433, 194, "Input available to the model and selected method", "model")
    f.section(1091, 194, "What it returns", "evidence")
    f.card(62, 373, 291, 151, "data", "Measured capacity", "XJTU cycle records", [
        "Charge trace and capacity", "SOH = capacity ÷ 2.0 Ah × 100", "Measured SOH is the test target",
    ])
    cases = (
        (224, "Charge only · Notebook 10", "Guarded first-cycle correction", [
            "Use charging data through late taper and prior valid charge readings.",
            "The guard checks unusual estimates against recent charge history.",
        ], "Current SOH", ["Current health before discharge", "Cross-rate MAE · 0.217 / 0.194 pp"]),
        (379, "Charge and past discharge · Notebook 11", "Rolling trend and battery matching", [
            "Use the current charge and discharge history through cycle t − 1.",
            "Select the trend or matching method by rate, age and horizon.",
        ], "Rolling SOH forecast", ["Current, +1, +10 and +50 cycles", "Refresh every five cycles"]),
        (534, "Fixed start · Notebook 12", "Revised degradation-curve forecast", [
            "Start once at cycle 50 or 100 using charge-based or measured SOH.",
            "Project duration and fade from comparable training-battery curves.",
        ], "Full SOH trajectory", ["One complete projected curve", "Full curve and final 20 cycles"]),
    )
    for y, tag, title, lines, result, result_lines in cases:
        f.card(433, y, 593, 135, "model", tag, title, lines)
        f.card(1091, y, 287, 135, "evidence", "Forecast output", result, result_lines)
        f.arrow([(1032, y + 67.5), (1083, y + 67.5)])
    f.arrow([(358, 448.5), (391, 448.5), (391, 291.5), (425, 291.5)], color=COLORS["data"][0])
    f.arrow([(391, 448.5), (425, 448.5)], color=COLORS["data"][0])
    f.arrow([(391, 448.5), (391, 601.5), (425, 601.5)], color=COLORS["data"][0])
    f.text(62, 702, "SOH measures capacity relative to the nominal capacity. The two cross-rate errors come from separate 2C-to-3C and 3C-to-2C tests.",
           9.1, color=MUTED, max_width=1316)
    return f


def rul():
    f = Figure(3, "Lifetime prediction", "Remaining useful life prediction",
               "The model updates the number of cycles left until the battery first reaches the verified 80% SOH threshold.",
               "Sources  ·  Notebooks 03 and 06 label audits  /  Notebook 11 rolling RUL  /  Notebook 12 fixed SOH curves")
    f.section(62, 193, "Build the supervised label", "data")
    f.card(62, 221, 310, 134, "data", "Recorded trajectory", "Measure cycle health", [
        "Use completed discharge capacity.", "Normalize by the nominal 2.0 Ah.",
    ])
    f.card(438, 221, 340, 134, "data", "End-of-life audit", "Verify the first crossing", [
        "Locate the first SOH at or below 80%.", "Check it against the published label.",
    ])
    f.card(844, 221, 534, 134, "evidence", "Label for training and evaluation", "Actual RUL = verified EOL cycle − current cycle", [
        "22 batteries supplied verified EOL labels.", "The right-censored battery remains in the SOH evaluation.",
    ])
    f.arrow([(378, 288), (430, 288)])
    f.arrow([(784, 288), (836, 288)])
    f.section(62, 389, "Predict at each observation cycle", "model")
    f.card(62, 481, 313, 153, "data", "Available at cycle t", "Current battery history", [
        "Charge through cycle t", "Discharge through cycle t − 1", "Update every five cycles from 50",
    ])
    f.card(459, 418, 421, 130, "model", "2C model", "Ridge and battery matching", [
        "Cycles 50–95 · early Ridge ensemble", "Cycle 100 onward · Ridge with peer matching",
    ])
    f.card(459, 573, 421, 130, "model", "3C model", "Taper features and rolling model", [
        "Cycles 50–95 · taper-based ensemble", "Cycle 100 onward · optional boosting correction",
    ])
    f.card(987, 480, 391, 156, "evidence", "Selected direct estimate", "Estimated cycles remaining", [
        "2C mean / largest error · 7.36 / 14.92 cycles",
        "3C mean / largest error · 12.64 / 37.62 cycles",
        "Scores cover all updates from cycle 50.",
    ])
    f.arrow([(381, 557.5), (414, 557.5), (414, 483), (451, 483)], color=COLORS["data"][0])
    f.arrow([(414, 557.5), (414, 638), (451, 638)], color=COLORS["data"][0])
    f.arrow([(886, 483), (931, 483), (931, 531), (979, 531)], color=COLORS["model"][0])
    f.arrow([(886, 638), (947, 638), (947, 590), (979, 590)], color=COLORS["model"][0])
    return f


def charging():
    f = Figure(4, "MIT–BIT charging", "Charging forecast and controller flow",
               "Forecast accuracy is scored on recorded outcomes. The fixed-budget controller is selected in a separate simulation benchmark.",
               "Sources  ·  Notebooks 14–17 recorded data and transitions  /  Notebook 18 fixed-budget controller  /  Notebook 22 forecast and SAC benchmark")
    f.section(62, 193, "Forecast charging time and delivered energy", "model")
    f.row(221, 148, (
        ("data", "Recorded input", "Randomized charging", ["1C, 2C or 3C charging", "3C discharge in the study", "55 held-out batteries across folds"]),
        ("data", "Features", "History and rate plan", ["Completed charge traces", "Past capacity and delivered Wh", "Planned 5-cycle rate blocks"]),
        ("model", "Notebook 22", "Refined Ridge forecasts", ["Kernel correction with raw traces", "Wh variant depends on the fold", "Forecast 5, 10 or 15 cycles"]),
        ("evidence", "Recorded validation", "15-cycle forecast error", ["Charging time MAE · 3.882 min", "Delivered energy MAE · 0.921 Wh", "Compare with measured outcomes"]),
    ))
    f.section(62, 405, "Choose a charging rate in simulation", "control")
    f.row(433, 151, (
        ("data", "Initial state and goal", "Set the energy target", ["Initialize from completed history.", "Freeze target at 90% of the", "initial fixed-1C forecast."]),
        ("model", "Planning and scoring", "Ridge transition model", ["Estimate time, Ah and Wh.", "Use training-fold uncertainty", "for planning and stress tests."]),
        ("control", "Selected policy", "Fixed-budget MPC", ["Search the remaining schedules.", "Choose the fastest eligible plan.", "Apply its first 5-cycle action."]),
        ("evidence", "Simulation outputs", "Charge time and energy", ["Credit delivered Wh each block.", "Check the fixed energy target.", "Compare on 164 matched starts."]),
    ))
    f.arrow([(1237, 590), (1237, 625), (207, 625), (207, 592)], color=COLORS["control"][0], dashed=True)
    f.caption(492, 611, "Update the state and replan from the next block", "control", width=446)
    f.ribbon(62, 666, 1316, "evidence", "Controller selection under disturbances",
             "Original fixed-budget MPC met the energy target in 97.27% of simulations, versus 92.12% for Discrete SAC.")
    return f


def discharging():
    f = Figure(5, "XJTU discharging", "Discharge forecast and controller flow",
               "Reference tests anchor the forecast. A common simulator compares discharge actions at the same energy target.",
               "Sources  ·  Notebook 19 reference tests  /  Notebook 20 transition simulator  /  Notebook 23 final discharge benchmark")
    f.section(62, 193, "Forecast against recorded Random Walk trajectories", "model")
    f.row(221, 148, (
        ("data", "Recorded input", "Reference test history", ["Standardized capacity tests", "Completed delivered energy", "Planned first current and duration"]),
        ("model", "Notebook 23", "Forecasts by horizon", ["SOH · kernel and history methods", "Wh · Ridge-based blends", "Compare with held-out outcomes"]),
        ("model", "Measurement update", "Refresh the forecast", ["Keep the same 30-cycle endpoint.", "Refresh after cycle 10 or 20.", "Include actual energy so far."]),
        ("evidence", "149 paired windows", "Lower endpoint error", ["SOH MAE · 0.520 → 0.122 pp", "Energy MAE · 0.909 → 0.260 Wh", "Start versus refresh after cycle 20"]),
    ))
    f.section(62, 405, "Compare discharge policies in simulation", "control")
    f.row(433, 151, (
        ("data", "Common inputs", "Match starts and targets", ["133 supported starting states", "Shared disturbance paths", "Same 90% energy target"]),
        ("control", "Selected policy", "Original Lookahead", ["Rank supported discharge plans.", "Choose the next 10-cycle action.", "Replan after each interval."]),
        ("model", "Same scorer for all policies", "Frozen Notebook 20 twin", ["Return modeled SOH and Wh.", "Check action support and", "stop if no action is supported."]),
        ("evidence", "Simulation outputs", "Final health and energy", ["Mean loss · 1.755 pp", "Energy target hit · 99.61%", "Reported over 30 cycles"]),
    ))
    f.arrow([(890, 590), (890, 625), (548, 625), (548, 592)], color=COLORS["control"][0], dashed=True)
    f.caption(593, 611, "Update state after each interval", "control", width=251)
    f.ribbon(62, 666, 1316, "evidence", "Controller benchmark",
             "Mean simulated SOH loss  ·  Lookahead 1.755 pp  /  Fitted Q Iteration 1.900 pp  /  Discrete SAC 1.926 pp  /  PPO 1.985 pp")
    return f


def validation():
    f = Figure(6, "Evaluation", "How forecasts and controllers are validated",
               "Match each claim to its evidence. Forecasts use held-out measurements, while controllers use shared simulated operating scenarios.",
               "Sources  ·  Leave-cell-out benchmark protocols  /  Notebook 17 recorded rollouts  /  Notebooks 22 and 23 selection criteria")
    f.section(62, 193, "Shared experimental setup", "data")
    f.card(62, 221, 357, 139, "data", "Data preparation", "Audit the historical records", [
        "Check protocols, units and labels.", "Verify SOH and EOL where required.",
    ])
    f.card(517, 221, 357, 139, "data", "Evaluation boundary", "Hold out entire batteries", [
        "Separate training and test cells.", "Set the last cycle available as input.",
    ])
    f.card(973, 221, 405, 139, "model", "Fit using training batteries", "Tune inside the training split", [
        "Select features and settings on training folds.", "Calibrate the models and energy margins.",
    ])
    f.arrow([(425, 290.5), (509, 290.5)])
    f.arrow([(880, 290.5), (965, 290.5)])
    f.section(62, 421, "Two types of test evidence", "evidence")
    f.card(62, 460, 391, 156, "data", "Forecast test", "Compare with measured outcomes", [
        "Use ground truth after the forecast origin.", "Match forecast horizon and scored windows.", "Track mean, worst-decile and maximum error.",
    ])
    f.card(524, 460, 391, 156, "control", "Controller test", "Compare policies in simulation", [
        "Share the start, disturbances and action rules.", "Check energy targets, time and health loss.", "Apply the benchmark’s advancement criteria.",
    ])
    f.card(987, 460, 391, 156, "evidence", "Saved evidence", "Record results and provenance", [
        "Archive per-battery predictions and episodes.", "Retain settings, measures and coverage.", "Label measured and simulated results.",
    ])
    f.arrow([(1175.5, 365), (1175.5, 397), (257.5, 397), (257.5, 452)], color=COLORS["model"][0])
    f.arrow([(719.5, 397), (719.5, 452)], color=COLORS["model"][0])
    f.arrow([(921, 538), (979, 538)])
    f.arrow([(257.5, 623), (257.5, 639), (1182.5, 639), (1182.5, 623)])
    f.ribbon(62, 666, 1316, "serve", "Interpretation",
             "Accuracy claims use recorded measurements. Comparative controller results describe the modeled scenarios used in the study.")
    return f


def deployment():
    f = Figure(7, "Deployment", "From notebook exports to the demo",
               "Docker Compose serves the presentation and experiment tracking on separate local ports using saved research outputs.",
               "Sources  ·  compose.yaml  /  app/data.py  /  Dockerfiles  /  tracking/container.py  /  Project launch instructions")
    f.section(62, 193, "Presentation · Docker Compose demo profile", "serve")
    f.row(222, 151, (
        ("evidence", "Reports on disk", "Saved study exports", ["Charging trajectories", "Discharging tests and policies", "SOH and RUL checkpoints"]),
        ("model", "Docker build stage", "Validated replay bundle", ["Read selected report tables.", "Validate matching keys and totals.", "Write a compact data.json."]),
        ("serve", "Presentation container", "Streamlit dashboard", ["Read the bundle from the image.", "Step through the saved cycles.", "Display the current case metrics."]),
        ("serve", "Browser · port 8501", "Live presentation", ["Charging time and energy", "Discharge forecast and decisions", "Battery health and cycles left"]),
    ))
    f.section(62, 412, "Experiment tracking and detailed simulation · default Compose service", "serve")
    f.caption(788, 389, "Prebuilt static HTML, CSS and JS in image", "serve", width=312)
    f.arrow([(944, 418), (944, 435)], color=COLORS["serve"][0])
    runtime = (
        ("evidence", "Reports on disk", "Saved benchmark results", ["Notebook metrics and settings", "Saved forecasts and policy trials", "Evidence tables and plots"]),
        ("model", "Tracking import", "Import experiments", ["Attach measured and simulated", "metrics, charts and artifacts.", "Prepare the local MLflow store."]),
        ("serve", "LifeGuard container", "MLflow and Flask routes", ["MLflow at /", "Static studies at /simulation/", "Serve both through Gunicorn."]),
        ("serve", "Browser · port 5501", "Experiment inspection", ["Compare runs and saved charts.", "Open study artifacts or browse", "the static simulation dashboard."]),
    )
    for x, node in zip((62, 405, 748, 1091), runtime, strict=True):
        f.card(x, 441, 287, 151, *node)
    f.arrow([(355, 516.5), (397, 516.5)])
    f.arrow([(1041, 516.5), (1083, 516.5)])
    f.card(748, 613, 440, 113, "serve", "Docker named volume", "Persistent MLflow store", [
        "SQLite database, run artifacts and saved chart views",
    ])
    f.arrow([(545, 598), (545, 668), (740, 668)], color=COLORS["serve"][0], dashed=True)
    f.caption(372, 653, "One-time store migration", "serve", width=226)
    f.arrow([(934, 609), (934, 598)], color=COLORS["serve"][0])
    f.text(62, 697, "Python Work can launch the same Streamlit dashboard directly.", 8.9, color=MUTED, max_width=648)
    return f


FIGURES = (
    ("01-system-architecture", overall),
    ("02-soh-estimation-and-forecasting", soh),
    ("03-rul-prediction", rul),
    ("04-charging-forecast-and-control", charging),
    ("05-discharge-forecast-and-control", discharging),
    ("06-evaluation-and-model-selection", validation),
    ("07-deployment-and-serving", deployment),
)


def main():
    svg_dir, png_dir = OUTPUT / "svg", OUTPUT / "png"
    svg_dir.mkdir(exist_ok=True)
    png_dir.mkdir(exist_ok=True)
    metadata = {"Title": "LifeGuard-RL architecture and system flows", "Subject": "Battery research system diagrams"}
    with PdfPages(OUTPUT / "lifeguard-architecture.pdf", metadata=metadata) as pdf:
        for stem, build in FIGURES:
            figure = build()
            figure.validate()
            pdf.savefig(figure.fig, facecolor=BACKGROUND)
            svg = svg_dir / f"{stem}.svg"
            figure.fig.savefig(svg, facecolor=BACKGROUND,
                               metadata={"Date": None, "Title": stem[3:].replace("-", " ").title()})
            portable_svg = svg.read_text(encoding="utf-8").replace("'DejaVu Sans';", "'DejaVu Sans', Arial, sans-serif;")
            svg.write_text(portable_svg, encoding="utf-8")
            figure.fig.savefig(png_dir / f"{stem}.png", dpi=200, facecolor=BACKGROUND)
            plt.close(figure.fig)


if __name__ == "__main__":
    main()
