"""Projector-friendly LifeGuard-RL demonstration."""

import json
from pathlib import Path
from time import monotonic

import altair as alt
import streamlit as st


FRAME_SECONDS = 2.0
PALETTE = {
    "Fixed 1C": "#777e8d",
    "Adaptive": "#007e74",
    "Recorded": "#166b98",
    "First forecast": "#777e8d",
    "Latest forecast": "#b4561e",
    "Health estimate": "#b4561e",
}
DASHES = {"First forecast": [2, 4], "Latest forecast": [7, 4], "Health estimate": [7, 4]}
CONTROLLERS = {
    "Lookahead": "lookahead:0",
    "Forecast MPC": "mpc:0",
    "Risk-aware MPC": "risk:0",
    "Soft Actor-Critic": "sac:42",
    "PPO": "ppo:42",
    "Fitted Q iteration": "fqi:0",
    "Battery health rule": "rule:0",
}


@st.cache_data(show_spinner=False)
def read_data():
    bundle = Path(__file__).with_name("data.json")
    if bundle.is_file():
        return json.loads(bundle.read_text(encoding="utf-8"))
    from data import collect_data

    return collect_data()


def reset():
    st.session_state.frame = 0
    st.session_state.playing = False


def start_playing():
    st.session_state.playing = True
    st.session_state.next_tick = monotonic() + FRAME_SECONDS


def pause():
    st.session_state.playing = False


def next_frame(last_frame):
    pause()
    st.session_state.frame = min(st.session_state.frame + 1, last_frame)


def playback(values, label, render, controls):
    last_frame = len(values) - 1
    with controls:
        play, stop, step, restart = st.columns(4, gap="small")
        play.button("Play", type="primary", on_click=start_playing, width="stretch",
                    disabled=st.session_state.playing or st.session_state.frame == last_frame)
        stop.button("Pause", on_click=pause, width="stretch", disabled=not st.session_state.playing)
        step.button("Next", on_click=next_frame, args=(last_frame,), width="stretch",
                    disabled=st.session_state.frame == last_frame)
        restart.button("Reset", on_click=reset, width="stretch")

    @st.fragment(run_every=FRAME_SECONDS if st.session_state.playing else None)
    def live_frame():
        if st.session_state.playing and monotonic() >= st.session_state.next_tick:
            st.session_state.frame += 1
            st.session_state.next_tick = monotonic() + FRAME_SECONDS
            if st.session_state.frame == last_frame:
                pause()
                st.rerun()
        frame = st.session_state.frame
        progress = (values[frame] - values[0]) / (values[-1] - values[0]) if last_frame else 1.0
        st.progress(progress, text=label(values[frame]))
        render(frame)

    live_frame()


def number(value, unit="", digits=2):
    if value is None:
        return "—"
    return f"{value:,.{digits}f}{unit}"


def metric_label(label, guidance):
    return f"{label} :gray[· {guidance}]"


def battery_name(cell):
    if isinstance(cell, int):
        return f"Battery {cell}"
    _, cohort, battery = cell.split("_")
    return f"Battery {battery.split('-')[-1]} · {cohort}"


def choose_case(label, cases, default, *, key, show_start=True):
    names = [
        f"{battery_name(case['cell'])} · start {case['start']}" if show_start else battery_name(case["cell"])
        for case in cases
    ]
    return cases[st.selectbox(label, range(len(cases)), index=names.index(default),
                              format_func=names.__getitem__, key=key, on_change=reset)]


def view_label(title, source):
    st.html(f"<div class='demo-view'><h2>{title}</h2><span>{source}</span></div>")


def trend(data, series, unit, x_label, *, ticks=None, zero=False, reference=None):
    records = [record for record in data if record["value"] is not None]
    x_axis = alt.Axis(values=ticks, format="d", grid=False) if ticks else alt.Axis(format="d", grid=False)
    extent = alt.Scale(domain=[ticks[0], ticks[-1]], nice=False) if ticks else alt.Scale(nice=True)
    colors = alt.Scale(domain=series, range=[PALETTE[name] for name in series])
    plot = alt.Chart(alt.Data(values=records)).mark_line(
        point=alt.OverlayMarkDef(filled=True, size=60), strokeWidth=2.6, interpolate="step-after",
    ).encode(
        x=alt.X("cycle:Q", title=x_label, axis=x_axis, scale=extent),
        y=alt.Y("value:Q", title=unit, axis=alt.Axis(tickCount=5), scale=alt.Scale(zero=zero)),
        color=alt.Color("series:N", scale=colors, title=None,
                        legend=alt.Legend(orient="top", direction="horizontal", symbolStrokeWidth=3)),
        strokeDash=alt.StrokeDash("series:N", scale=alt.Scale(domain=series,
                                range=[DASHES.get(name, [1, 0]) for name in series]), legend=None),
        tooltip=[alt.Tooltip("series:N", title="Series"), alt.Tooltip("cycle:Q", title=x_label),
                 alt.Tooltip("value:Q", title=unit, format=".2f")],
    )
    if reference is not None:
        rule = alt.Chart(alt.Data(values=[{"target": reference}])).mark_rule(
            color="#a5802e", strokeDash=[4, 4], strokeWidth=1.5,
        ).encode(y="target:Q", tooltip=alt.Tooltip("target:Q", title="Target", format=".2f"))
        layers = [rule, plot]
    else:
        layers = [plot]
    chart = alt.layer(*layers).properties(height=108, padding={"top": 5, "bottom": 5, "left": 4, "right": 4},
                                          autosize=alt.AutoSizeParams(type="fit-x", contains="padding"))
    st.altair_chart(chart, width="stretch", theme="streamlit")


def charging(data):
    view_label("Fixed vs. adaptive charging", "Simulation · MIT–BIT")
    scenario, controls = st.columns([3, 2], vertical_alignment="bottom")
    with scenario:
        case = choose_case("Charging scenario", data["cases"], "Battery 71 · start 11", key="charging_case")
    step = data["block_size"]
    fixed, adaptive = (case["policies"][name] for name in ("fixed_1c", "energy_budget"))
    budget = case["budget"]

    def render(frame):
        fixed_path, adaptive_path = fixed[:frame], adaptive[:frame]
        fixed_wh = fixed_path[-1]["cumulativeWh"] if frame else 0.0
        adaptive_wh = adaptive_path[-1]["cumulativeWh"] if frame else 0.0
        saved = fixed_path[-1]["cumulativeMinutes"] - adaptive_path[-1]["cumulativeMinutes"] if frame else 0.0
        remaining = budget - adaptive_wh
        time, energy, target = st.columns(3)
        time.metric(metric_label("Charging time saved", "Higher is better"), number(saved, " min", 1),
                    help="Fixed charging time minus adaptive charging time.", border=True)
        energy.metric(metric_label("Adaptive energy delivered", "Meet the target"), number(adaptive_wh, " Wh"), border=True)
        status = "Met" if remaining <= 0 else "Missed" if frame == len(adaptive) else "In progress"
        target.metric(f"Energy target · {budget:.2f} Wh", status, border=True)

        if frame:
            fixed_last, adaptive_last = fixed_path[-1], adaptive_path[-1]
            st.caption(f"Latest block · Fixed {fixed_last['rate']}C, Adaptive {adaptive_last['rate']}C  |  "
                       f"Total energy · Fixed {fixed_wh:.2f} Wh, Adaptive {adaptive_wh:.2f} Wh  |  "
                       f"Adaptive minus Fixed · {adaptive_wh - fixed_wh:+.2f} Wh")
        else:
            st.caption("Each step adds one five-cycle block to both strategies.")

        def series_for(field):
            return [{"series": name, "cycle": 0, "value": 0} for name in ("Fixed 1C", "Adaptive")] + [
                {"series": name, "cycle": index * step, "value": block[field]}
                for name, path in (("Fixed 1C", fixed_path), ("Adaptive", adaptive_path))
                for index, block in enumerate(path, 1)
            ]

        by_time, by_energy = st.columns(2)
        ticks = list(range(0, (len(adaptive) + 1) * step, step))
        with by_time:
            trend(series_for("cumulativeMinutes"), ["Fixed 1C", "Adaptive"], "Charging time (min) ↓",
                  "Operating cycles", zero=True, ticks=ticks)
        with by_energy:
            trend(series_for("cumulativeWh"), ["Fixed 1C", "Adaptive"], "Delivered energy (Wh)",
                  "Operating cycles", ticks=ticks, zero=True, reference=budget)

    playback(list(range(0, (len(adaptive) + 1) * step, step)),
             lambda cycle: f"Operating cycles completed · {cycle} of {step * len(adaptive)}", render, controls)


def discharge_forecast(cases):
    view_label("A new reading updates the forecast", "Recorded replay · XJTU")
    scenario, controls = st.columns([3, 2], vertical_alignment="bottom")
    with scenario:
        case = choose_case("Forecast scenario", cases, "Battery 1 · RW · start 21", key="discharge_forecast_case")
    stages, measured = case["stages"], case["measured"]
    ticks = [0, 10, 20, 30]

    def render(frame):
        latest = stages[min(frame, len(stages) - 1)]
        complete = frame == len(stages)
        health, energy = measured if complete else latest[1:3]
        health_card, energy_card, forecast_card = st.columns(3)
        health_card.metric(metric_label("Recorded battery health", "Higher is better"), number(health, "%"), border=True)
        energy_card.metric("Recorded energy delivered", number(energy, " Wh"), border=True)
        forecast_card.metric(metric_label("Latest forecast for cycle 30", "Closer to recorded is better"),
                             f"{latest[3][2]:.2f}% · {latest[4][2]:.2f} Wh", border=True)
        if complete:
            st.caption(f"Absolute error (lower is better) · First → Updated  |  Health: {abs(stages[0][3][2] - health):.3f} → "
                       f"{abs(latest[3][2] - health):.3f} percentage points  |  Energy: {abs(stages[0][4][2] - energy):.3f} → "
                       f"{abs(latest[4][2] - energy):.3f} Wh")
        else:
            st.caption(f"Latest reading · dataset cycle {latest[0]}  |  Both forecasts predict the same final endpoint.")

        def series_for(index):
            records = [
                {"cycle": ticks[i], "series": name, "value": value}
                for i, point in enumerate(stages[:frame + 1])
                for name, value in (("Latest forecast", point[index][2]), ("First forecast", stages[0][index][2]))
            ]
            if complete:
                records += [
                    {"cycle": ticks[-1], "series": "First forecast", "value": stages[0][index][2]},
                    {"cycle": ticks[-1], "series": "Latest forecast", "value": latest[index][2]},
                    {"cycle": ticks[-1], "series": "Recorded", "value": measured[index - 3]},
                ]
            return records

        soh, wh = st.columns(2)
        series = ["First forecast", "Latest forecast", "Recorded"] if complete else ["First forecast", "Latest forecast"]
        with soh:
            trend(series_for(3), series, "Final health (%)", "Operating cycles", ticks=ticks)
        with wh:
            trend(series_for(4), series, "Final energy (Wh)", "Operating cycles", ticks=ticks)

    playback(ticks, lambda cycle: f"Operating cycles completed · {cycle} of 30", render, controls)


def controller_comparison(cases):
    view_label("Fixed vs. adaptive discharging", "Simulation · XJTU")
    scenario, policy, controls = st.columns([1.75, 1.25, 2], vertical_alignment="bottom")
    with scenario:
        case = choose_case("Controller scenario", cases, "Battery 1 · RW · start 54", key="discharge_controller_case")
    with policy:
        adaptive = st.selectbox("Compare Fixed with", list(CONTROLLERS), key="controller_policy", on_change=reset)
    runs = {"Fixed": case["runs"]["fixed:0"], adaptive: case["runs"][CONTROLLERS[adaptive]]}
    actions = {"0": "Low", "1": "Middle", "2": "High"}

    def render(frame):
        st.caption(f"Shared energy target · {case['budget']:.2f} Wh  |  Each decision covers ten operating cycles.")
        for column, (name, (sequence, loss, energy, hit, stopped)) in zip(st.columns(2), runs.items()):
            with column, st.container(border=True):
                st.markdown(f"**{name}**")
                visible = [actions[action] for action in sequence[:frame]]
                st.write(" → ".join(visible) if visible else "Ready for the first action")
                if stopped and frame > len(sequence):
                    st.caption("Stopped · no supported next action")
                if frame == 3 or stopped and frame > len(sequence):
                    health, delivered = st.columns(2)
                    health.metric(metric_label("Health loss", "Lower is better"), f"{loss:+.3f} pp")
                    delivered.metric(metric_label("Energy delivered", "Meet the target"), number(energy, " Wh"))
                    if hit:
                        st.success("Energy target met")
                    else:
                        st.warning("Energy target missed")

    playback([0, 10, 20, 30], lambda cycle: f"Decision timeline · {cycle} of 30 operating cycles", render, controls)


def discharge(data, navigation):
    with navigation:
        mode = st.radio("Discharge view", ["Forecast replay", "Controller comparison"], horizontal=True,
                        label_visibility="collapsed", key="discharge_mode", on_change=reset)
    if mode == "Forecast replay":
        discharge_forecast(data["forecasts"])
    else:
        controller_comparison(data["controllers"])


def battery_life(data):
    view_label("Battery health and cycles left", "Recorded replay · XJTU")
    scenario, controls = st.columns([3, 2], vertical_alignment="bottom")
    with scenario:
        case = choose_case("Battery", data["cases"], "Battery 11 · 3C", key="battery_case", show_start=False)
    points = case["checkpoints"]

    def render(frame):
        point = points[frame]
        observed, estimated, life = st.columns(3)
        observed.metric(metric_label("Recorded battery health", "Higher is better"), number(point["observed"], "%"), border=True)
        estimated.metric(metric_label("Estimated battery health", "Closer to recorded is better"),
                         number(point["estimate"], "%"), border=True)
        life.metric(metric_label("Estimated cycles left", "More cycles means longer life"),
                    number(point["cycles_left"], " cycles", 0), border=True)
        if frame == len(points) - 1:
            if case["observed_eol"] is None:
                st.info("End of the record · battery end-of-life was not observed.")
            else:
                predicted = points[0]["cycles_left"]
                actual = case["observed_eol"] - points[0]["cycle"]
                st.success(f"Recorded end-of-life · cycle {case['observed_eol']}  |  "
                           f"At cycle {points[0]['cycle']}: {predicted:.0f} cycles estimated, {actual} cycles observed.")
        trace = [{"cycle": item["cycle"], "series": name, "value": item[key]}
                 for item in points[:frame + 1] for name, key in (("Recorded", "observed"), ("Health estimate", "estimate"))]
        trend(trace, ["Recorded", "Health estimate"], "Battery health (%)", "Cycle", reference=data["threshold"])

    playback([point["cycle"] for point in points], lambda cycle: f"Current reading · cycle {cycle}", render, controls)


def main():
    st.set_page_config(page_title="LifeGuard-RL | Live Battery Dashboard", page_icon="🔋", layout="wide")
    st.html("""
        <style>
        .stMainBlockContainer { max-width: 76rem; padding-top: 2.75rem; padding-bottom: 1.2rem; }
        [data-testid="stAppDeployButton"] { display: none; }
        .stMainBlockContainer [data-testid="stVerticalBlock"] { gap: .55rem; }
        .demo-header { display: flex; align-items: baseline; gap: 1rem; flex-wrap: wrap; margin-bottom: .2rem; }
        .demo-header h1 { padding: 0; margin: 0; font-size: 2.22rem; letter-spacing: -.045em; }
        .demo-header > span { font-weight: 600; font-size: .95rem; }
        .demo-view { display: flex; align-items: baseline; gap: .8rem; flex-wrap: wrap; }
        .demo-view h2 { padding: 0; margin: 0; font-size: 1.42rem; letter-spacing: -.025em; }
        .demo-view > span { font-size: .78rem; padding: .15rem .55rem; border: 1px solid currentColor; border-radius: .9rem; }
        [data-testid="stMetricValue"] { font-variant-numeric: tabular-nums; }
        </style>
        <div class='demo-header'><h1>LifeGuard-RL</h1><span>Live Battery Dashboard</span></div>
        """)
    if "frame" not in st.session_state:
        reset()
    try:
        data = read_data()
    except (OSError, ValueError) as error:
        st.error(f"Could not load the saved presentation results. {error}")
        st.stop()
    navigation, discharge_navigation = st.columns([3, 2])
    with navigation:
        view = st.radio("Demonstration", ["Charging", "Discharging", "Battery life"], horizontal=True,
                        label_visibility="collapsed", key="view", on_change=reset)
    if view == "Charging":
        charging(data["charging"])
    elif view == "Discharging":
        discharge(data["discharge"], discharge_navigation)
    else:
        battery_life(data["health"])


main()
