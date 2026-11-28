# LifeGuard-RL

## Battery-Health-Aware Reinforcement Learning for Adaptive Charging and Lifetime Optimization

**Project owner / presenter:** Sakib Rayhan Yeasin\
**Project type:** AI Engineering Capstone and research project\
**Primary dataset:** [BatteryLife v12 ---
Zenodo](https://zenodo.org/records/21149533)\
**Initial scope:** One dataset collection only\
**Status:** Proposed research; no experimental results have been
established yet.

------------------------------------------------------------------------

## 1. Project in brief

LifeGuard-RL will investigate whether Reinforcement Learning (RL) can
learn battery operating policies that reduce long-term degradation while
still delivering useful energy safely.

Batteries gradually lose capacity as they are charged and discharged.
Degradation depends on factors such as chemistry, temperature,
charge/discharge rate, depth of discharge, operating range, and usage
history. A fixed operating protocol may not be equally suitable for
every battery or every stage of its life.

The project will use BatteryLife v12 to build: 1. Battery State of
Health (SOH) estimation. 2. Battery degradation analysis. 3. Remaining
Useful Life (RUL) estimation. 4. Cross-cell and cross-chemistry
generalisation experiments. 5. A data-calibrated battery simulator
(digital twin). 6. An RL agent that selects supported charging,
discharging, or rest actions in simulation.

**Main research question**

> Can a data-calibrated, safety-constrained RL policy reduce simulated
> battery degradation compared with fixed and rule-based operating
> strategies, while maintaining a defined level of energy delivery?

The intended deliverable is a reproducible research prototype, not a
certified or production Battery Management System (BMS).

------------------------------------------------------------------------

## 2. Problems and proposed solutions

### Problem 1 --- Different batteries have different health

Two batteries may have different capacities, chemistries, formats, and
cycling histories. Cycle count alone cannot describe their current
health.

**Plan:** Calculate or validate SOH using the dataset's documented
capacity reference. Train regression models using available capacity,
voltage, current, temperature, resistance, cycle, and protocol
information. Test on battery cells that were not used during training.

**Output:** Estimated SOH for a battery at a given point in its recorded
life, with uncertainty where feasible.

A common capacity-based definition is:

`SOH (%) = (current measured capacity / reference capacity) × 100`

The reference capacity convention must be consistent and documented. Do
not assume nominal capacity, first-cycle capacity, and
manufacturer-rated capacity are interchangeable.

### Problem 2 --- Charging/discharging conditions affect degradation

Different current rates, temperatures, depth-of-discharge levels, SOC
ranges, and protocols may be associated with different degradation
rates.

**Plan:** Group records by chemistry and operating protocol; calculate
capacity retention and degradation features; compare similar cells under
comparable conditions; train a model to estimate degradation from
operating conditions.

**Output:** Evidence about which recorded operating conditions are
associated with faster or slower degradation.

**Caution:** Correlation does not automatically prove causation. Control
for chemistry, cell variation, temperature, and other relevant factors.
Use causal language only if the experimental design supports it.

### Problem 3 --- Estimate SOH and Remaining Useful Life

Knowing current health is not enough. We also want to estimate how many
cycles remain before the battery reaches its dataset-defined End-of-Life
(EOL) criterion.

**Plan:** Use cycling history and documented EOL labels to train an RUL
model. Evaluate predictions at different early- and mid-life observation
points.

`RUL (cycles) = estimated EOL cycle − current cycle`

Some cells may not reach EOL during observation. These are
right-censored samples; do not invent an EOL cycle for them. Use a
suitable censored/survival-learning method or clearly exclude them from
a particular supervised RUL experiment.

RUL in cycles is not automatically RUL in months or years. Calendar-life
conversion needs a usage-frequency assumption or additional data.

### Problem 4 --- Generalise across battery chemistries

A model trained on one chemistry may fail on another because voltage
curves and degradation behaviour differ.

**Plan:** Evaluate on held-out cells within a chemistry. Where sample
counts permit, hold out a chemistry or chemical system during training.
Compare chemistry-specific models with a shared model that uses
chemistry metadata.

**Output:** Per-chemistry evidence showing where the model generalises
and where chemistry-specific modelling is needed.

Do not claim cross-chemistry generalisation if random rows from the same
cells appear in both training and testing.

### Problem 5 --- Learn adaptive operating decisions with RL

A fixed protocol may not adapt to the current battery state or long-term
degradation trade-off.

**Plan:** Train and validate health/degradation models first. Use them
to build a battery digital twin. Train an RL agent to select charging,
discharging, or rest actions supported by the data. Add an independent
safety controller. Compare RL with fixed and rule-based strategies.

**Output:** A simulated policy that seeks to reduce degradation while
delivering a defined amount of useful energy under explicit operating
constraints.

**Critical limitation:** BatteryLife records outcomes for observed
protocols; it does not contain the result of every possible action. The
initial RL action space must be restricted to protocols or operating
ranges supported by the data. A simulator may be inaccurate outside that
range. Do not claim real-world lifetime extension from simulation alone.

------------------------------------------------------------------------

## 3. Primary dataset: BatteryLife v12

**Official source:** https://zenodo.org/records/21149533

BatteryLife v12 is the only primary dataset planned for the initial
project.

### Reported overview

  Property                                          Reported value
  ----------------------------- ----------------------------------
  Total battery samples/cells                                  990
  Processed data size                        Approximately 31.9 GB
  Chemical systems                                              59
  Battery formats                                                8
  Operating temperatures                                         9
  Charge/discharge protocols                                   421
  Dataset groups                  Li-ion, Zn-ion, Na-ion, and CALB

Reported group counts:

  Group            Number
  ------------- ---------
  Lithium-ion         837
  Zinc-ion             95
  Sodium-ion           31
  CALB                 27
  **Total**       **990**

CALB is a dataset group/source designation; do not automatically treat
it as a separate chemistry. Inspect each cell's metadata.

### Types of information

Depending on the cell and file, records may include:

-   Cell/battery identifier
-   Chemistry and battery format
-   Cycle number
-   Time within a charge/discharge record
-   Voltage and current
-   Charge and discharge capacity
-   Temperature, where measured
-   Internal resistance, where measured
-   Charging and discharging protocols
-   Operating temperature
-   SOC interval or related protocol metadata
-   Nominal/rated capacity and cell metadata
-   Battery lifetime or EOL labels, where available

**Do not assume every field exists for every battery.** Inspect the
actual v12 files and metadata before coding. Field names, units,
missingness, and label definitions may vary.

### Dataset limitations

BatteryLife is a battery cycling/lifetime dataset, not a complete
solar-home-system or microgrid dataset. It does not directly provide:

-   Solar PV generation time series
-   Household electricity demand
-   Bangladesh-specific load-shedding records
-   Local electricity tariffs
-   A complete real-time BMS stream
-   Comprehensive labelled safety-fault events for every cell
-   Outcomes for every possible charging action

Therefore, the initial project must not claim to directly solve solar
forecasting, household demand forecasting, Bangladesh load-shedding
prediction, or real electricity-bill optimisation. A simulated
energy-delivery requirement may be used, but must be labelled as a
simulation assumption rather than an observed BatteryLife variable.

BatteryLife includes several battery groups, but it does not include
Lead-Acid as a supported group. Do not claim Lead-Acid support.

------------------------------------------------------------------------

## 4. Research methodology

### Phase 1 --- Dataset audit and preparation

1.  Read the official v12 documentation, metadata, files, and licence.
2.  Inspect the real directory structure and schemas.
3.  Create a manifest of cells, chemistry, formats, protocols,
    measurements, and labels.
4.  Check units, missing values, duplicates, and inconsistent records.
5.  Process the approximately 31.9 GB dataset in chunks; do not load it
    all into memory.
6.  Select an initial chemistry with enough complete cells.

**Deliverable:** Dataset inventory, data-quality report, and
reproducible preprocessing pipeline.

### Phase 2 --- SOH and RUL baselines

Start with simple models: - Linear/Ridge Regression - Random Forest -
Gradient Boosting / LightGBM

Consider LSTM or TCN only if sequential modelling is justified by the
data and baselines.

Evaluate: - SOH: MAE and RMSE. - RUL: MAE/RMSE with correct treatment of
censored cells. - Per-chemistry performance. - Prediction uncertainty
where feasible.

**Deliverable:** Trained health/lifetime models and evaluation report.

### Phase 3 --- Degradation analysis

Analyse relationships between charge/discharge current or rate,
temperature, depth of discharge, SOC interval, protocol, cycle number,
capacity retention, and resistance change where available.

Use controlled comparisons and explainable modelling. Document
confounding variables.

**Deliverable:** Degradation plots, protocol comparisons, and analysis
report.

### Phase 4 --- Battery digital twin

Build a simulator that represents battery state and predicts how it
changes after a supported action.

Candidate state variables, subject to availability: - SOH / estimated
capacity - SOC, if measured or reliably estimated - Voltage and
current - Temperature, if measured - Internal resistance, if measured -
Cycle/usage history - Chemistry and cell-specific operating limits -
Model uncertainty

The transition model should predict the next state after a charge,
discharge, or rest action.

Validate it against held-out real cycling trajectories. Measure one-step
and multi-step prediction errors. Monitor uncertainty and avoid
unsupported extrapolation.

**Deliverable:** Documented, tested battery digital twin.

### Phase 5 --- RL environment and training

Implement the environment using Gymnasium.

**State:** Current battery condition and relevant operating history.

**Action:** Initially select among observed charging/discharging
protocols or supported rates, plus rest/hold. Use continuous actions
only if reliable interpolation is supported by the data.

**Reward:** A preliminary objective may combine: - Benefit for useful
energy delivered. - Penalty for capacity/SOH degradation. - Penalty for
operating time or other explicitly modelled cost. - Penalty for unsafe
operation.

Hard safety constraints must be enforced by an independent safety layer.
Reward penalties alone are not sufficient.

Candidate algorithms: - PPO - SAC, if a justified continuous action
space is developed.

Compare RL with simpler policies. Retain RL only if it provides
measurable benefit.

**Deliverable:** Trained RL policy and reproducible experiment logs.

### Phase 6 --- Benchmark and evaluation

Compare: 1. Fixed charging/discharging protocol. 2. Simple rule-based
health-aware controller. 3. Greedy degradation-aware policy. 4.
MPC/optimization baseline, if a fair formulation is feasible. 5. RL
policy.

Evaluate: - SOH retention in simulation - Capacity fade - Cycles to
dataset-defined EOL - Useful energy delivered - Safety constraint
violations - Performance on unseen cells - Performance across supported
chemistry groups - Simulator prediction error - Computational and
inference cost

Use multiple random seeds and report variability/confidence intervals
where appropriate.

### Phase 7 --- Demonstration application

Build a simple dashboard showing: - Battery and chemistry selection -
Current cycle and estimated SOH - Predicted RUL in cycles - Historical
degradation curve - Selected charging/discharging action - Simulated
next-state health - Safety status - Comparison of fixed, rule-based, and
RL policies

The dashboard is a research demonstration, not a certified BMS.

------------------------------------------------------------------------

## 5. Initial RL formulation

The final design must be adjusted after inspecting the data and
validating the simulator.

### Candidate state

-   Current SOH/capacity estimate
-   SOC, if available or reliably estimated
-   Voltage and current
-   Temperature, if available
-   Internal resistance, if available
-   Cycle number and usage history
-   Chemistry/cell metadata
-   Model uncertainty
-   Remaining energy-delivery requirement in the simulated task

### Candidate actions

-   Select a supported charging protocol/rate.
-   Select a supported discharging protocol/rate.
-   Rest/hold.
-   Defer or stop when safety requires it.

Do not allow arbitrary current, voltage, temperature, or SOC targets
unsupported by the data or cell specifications.

### Candidate reward

`Reward = energy-service benefit − degradation cost − operating cost − safety risk`

Only include terms represented in the simulator. BatteryLife does not
provide electricity tariffs, household demand, PV generation, or outage
records. Any demand or cost term must be an explicit simulation
assumption.

### Safety

-   Enforce cell-specific voltage limits.
-   Enforce current limits from reliable cell specifications.
-   Enforce temperature limits where temperature is modelled.
-   Enforce SOC limits where SOC is modelled.
-   Reject unsupported actions.
-   Treat uncertain simulator predictions conservatively.
-   Never connect the initial research policy directly to physical
    battery hardware.

------------------------------------------------------------------------

## 6. Data splitting and leakage prevention

This is mandatory for credible results.

-   Split by battery/cell ID, not random individual rows.
-   Keep future cycles out of training when testing future-cycle
    prediction.
-   Use chronological evaluation for forecasting.
-   Use held-out cells for within-chemistry generalisation.
-   Use leave-one-chemistry/system-out evaluation only where sample
    counts permit.
-   Fit preprocessing and feature selection on training data only.
-   Never use future capacity, EOL labels, or future measurements as
    input features.
-   Do not let the RL agent observe future outcomes during simulation.

Document all splits and random seeds.

------------------------------------------------------------------------

## 7. Scope: what is and is not included

### Included initially

-   Battery health estimation
-   Battery degradation analysis
-   RUL estimation
-   Cross-cell and supported cross-chemistry generalisation
-   Battery digital twin
-   Simulation-based adaptive charging/discharging policy
-   Safety-constrained policy evaluation

### Not included initially

-   Real solar forecasting
-   Real household demand forecasting
-   Bangladesh load-shedding prediction
-   Actual electricity-bill optimisation
-   Lead-Acid battery management
-   Comprehensive sudden-fault diagnosis
-   Physical BMS deployment or hardware control

These may be future extensions if suitable data and validation become
available.

------------------------------------------------------------------------

## 8. Research novelty and baselines

BatteryLife is already a comprehensive battery-life benchmark. SOH
prediction, RUL prediction, or chemistry generalisation alone are not
sufficient novelty claims.

Required baselines: - Dataset/reference SOH and RUL methods where
available - Linear/Ridge Regression - Random Forest - LightGBM/Gradient
Boosting - Fixed protocol controller - Rule-based controller - Greedy
degradation-aware policy - MPC/optimization baseline where feasible -
PPO/SAC only when justified

Potential contribution to investigate:

> A data-calibrated, uncertainty-aware battery digital twin and
> safety-constrained adaptive charging policy evaluated across unseen
> cells, operating protocols, and supported chemical systems.

This is a **research hypothesis**, not a proven novelty claim. Conduct a
focused literature review of recent battery-health-aware charging,
model-based RL, safe RL, and BatteryLife benchmark studies before
claiming novelty.

A rigorous negative result is acceptable if RL does not outperform a
simpler controller.

------------------------------------------------------------------------

## 9. Suggested technology stack

  -----------------------------------------------------------------------
  Task                                Tools
  ----------------------------------- -----------------------------------
  Data processing                     Python, NumPy, Pandas or Polars

  Large-file processing               PyArrow / format-specific readers

  Classical ML                        scikit-learn, LightGBM

  Deep learning                       PyTorch

  RL environment                      Gymnasium

  RL algorithms                       Stable-Baselines3 (PPO/SAC, subject
                                      to action design)

  Experiment tracking                 MLflow

  Visualisation                       Matplotlib, Plotly

  Dashboard                           Streamlit

  Reproducibility                     Git, configuration files, fixed
                                      seeds
  -----------------------------------------------------------------------

Use only tools that are needed. Avoid unnecessary frameworks.

### Local MLflow demo

The native MLflow UI compares LifeGuard-RL's saved evaluation runs and recorded training histories. It uses a project-local SQLite database. From this repository root, use the Python Work environment.

```sh
../../.venv/bin/python -B -m tracking import
../../.venv/bin/python -B -m tracking links
../../.venv/bin/python -B -m tracking serve
```

Open [MLflow Tracking](http://127.0.0.1:5500). Press Ctrl+C in the terminal to stop the server. Port 5500 avoids the macOS AirPlay conflict on port 5000. If 5500 is occupied, choose another free port and pass the same `--port` to `serve` and `links`.

MLflow 2.22.5 uses the SQLAlchemy 2.0 series in this setup. If Python Work has SQLAlchemy 2.1, install the compatible version into the project's ignored dependency directory.

```sh
uv pip install --no-deps --python ../../.venv/bin/python --target .mlflow/dependencies "SQLAlchemy==2.0.58"
```

#### Suggested demo order

With the server running, use a second terminal to open a focused native chart view.

```sh
../../.venv/bin/python -B -m tracking charts soh-trajectory --open
../../.venv/bin/python -B -m tracking charts discharge-soh --open
../../.venv/bin/python -B -m tracking charts charging-policies --open
../../.venv/bin/python -B -m tracking charts discharge-sac --open
```

Run `tracking charts` through Python Work to list the other chart views. These links open MLflow's chart view with matched runs and the relevant metrics already selected. Trajectory charts use operating cycles, fixed forecast charts use cycles ahead, refresh charts use cycles elapsed, and training curves use logged updates. Controller metrics are shown as bars for each policy.

Every experiment has a **Benchmark overview** run. In **Artifacts**, open `plots/` for the figures, `sources/` for the original tables and summary, and `provenance.json` for file checksums. The **XJTU SOH and RUL**, **MIT-BIT Measured Replay**, **MIT-BIT Simulator Validation**, and **MIT-BIT Charging Forecast** experiments provide the remaining comparisons.

Set `TRACK_WITH_MLFLOW = True` in the final cell of Notebook 22 or 23 to log a completed local export. The execution record indicates when the controller benchmark was reused. Identical result tables reuse the existing comparison runs. Saved reports can also be imported from a directory or a downloaded ZIP.

```sh
../../.venv/bin/python -B -m tracking import --notebook 23 --report /path/to/downloaded-results.zip
```

The **evidence** tag distinguishes held-out forecasts, recorded matches, simulated controllers, and stored training histories. The database and locally generated plots are stored in `.mlflow/`.

### Run both interfaces with Docker

Start Docker Desktop and run these commands from the project root. The image uses its own Linux runtime. Complete any host-side MLflow imports or notebook exports before migrating the store.

```sh
docker compose build
docker compose run --rm --volume "$(pwd -P)/.mlflow:/migration:ro" lifeguard \
    python -m tracking.container migrate /migration \
    --original-artifact-root "$(pwd -P)/.mlflow/artifacts"
docker compose up
```

Open [MLflow](http://127.0.0.1:5501) or the [simulation dashboard](http://127.0.0.1:5501/simulation/). Port 5501 is published on localhost. Set `LIFEGUARD_PORT` to choose a different host port. Press Ctrl+C to stop the foreground service.

The one-time migration copies the current SQLite database and artifacts into the Compose volume. Subsequent starts use that volume. To print its saved MLflow chart links while the service is running, use:

```sh
docker compose exec lifeguard python -m tracking --store /var/lib/lifeguard/mlflow charts --port 5501
```

To import a newer report export from the host, mount the report folder for the import command:

```sh
docker compose run --rm --volume "$(pwd -P)/reports:/app/reports:ro" lifeguard \
    python -m tracking --store /var/lib/lifeguard/mlflow import
```

### Live Streamlit presentation

Start Docker Desktop and run this from the project root.

```sh
docker compose --profile demo up --build presentation
```

Open [LifeGuard-RL Live Battery Dashboard](http://127.0.0.1:8501). Use **Play** to replay the saved results automatically or **Next** to pause at each reading. The demo runs offline after building the image. Press Ctrl+C in the terminal to stop it. Set `LIFEGUARD_DEMO_PORT` to change the Docker host port.

The same dashboard runs from the existing Python Work environment.

```sh
../../.venv/bin/python -B -m streamlit run app/app.py \
    --server.address=127.0.0.1 --server.headless=true --server.fileWatcherType=none \
    --browser.gatherUsageStats=false
```

The [English presenter script](docs/live-presentation.md) describes the nine-minute demo and the expected results.

------------------------------------------------------------------------

## 10. Suggested repository structure

``` text
LifeGuard-RL/
├── README.md
├── docs/
│   ├── dataset_audit.md
│   ├── research_questions.md
│   ├── methodology.md
│   └── experiment_log.md
├── configs/
├── data/
│   ├── raw/          # Do not commit raw data
│   ├── interim/
│   └── processed/
├── notebooks/
│   ├── 01_dataset_audit.ipynb
│   ├── 02_exploratory_analysis.ipynb
│   ├── 03_soh_rul_baselines.ipynb
│   └── 04_degradation_analysis.ipynb
├── src/
│   ├── data/
│   ├── features/
│   ├── health_models/
│   ├── degradation/
│   ├── digital_twin/
│   ├── rl_env/
│   ├── agents/
│   ├── safety/
│   └── evaluation/
├── tests/
├── models/
├── reports/
│   ├── figures/
│   └── tables/
├── app/
└── requirements.txt
```

Do not commit large raw dataset files to Git. Store download
instructions, checksums, and metadata instead.

------------------------------------------------------------------------

## 11. Instructions for AI coding/research agents

Any AI agent assisting this project must follow these rules.

### Understand before coding

1.  Read this README fully.
2.  Treat BatteryLife v12 as the only primary dataset unless the project
    owner explicitly approves another dataset.
3.  Do not silently change the title, scope, objectives, or dataset.
4.  Inspect the real files and official metadata before assuming
    columns, formats, labels, or feature availability.
5.  Do not load all 31.9 GB into memory at once.

### Scientific integrity

1.  Never invent dataset fields, labels, results, citations, or
    benchmark scores.
2.  Distinguish measured data, derived features, simulated variables,
    and assumptions.
3.  Do not claim causal effects from simple correlations.
4.  Do not claim RL improves battery lifetime before fair comparative
    experiments.
5.  Do not claim simulation results prove real-world lifetime extension.
6.  Respect dataset-specific EOL definitions and censored observations.
7.  Prevent cell-level, temporal, and target leakage.
8.  Report per-chemistry sample counts and performance.
9.  Document uncertainty and limitations.

### Development order

1.  Dataset audit first; do not start with RL training.
2.  Build SOH/RUL baselines and degradation analysis.
3.  Validate the battery transition model/digital twin.
4.  Build fixed and rule-based controllers.
5.  Implement RL only after simulator validation.
6.  Compare RL fairly with simpler baselines.
7.  Build the dashboard after core experiments work.

### Reproducibility

-   Use clear Python modules and functions.
-   Keep configurations separate from code.
-   Fix random seeds and record package versions.
-   Log experiment settings, metrics, and model artifacts.
-   Test SOH calculation, RUL construction, state transitions, action
    limits, and reward calculations.
-   Explain major modelling assumptions.
-   Keep reusable code in `src/`; use notebooks for exploration.

### Ask before major assumptions

If a required variable is missing or the dataset does not support an
experiment, explain the gap and propose alternatives. Do not fabricate
solar data, household demand, tariffs, current limits, temperature
limits, or fault labels.

If the simulator cannot be validated within the observed data domain,
report the limitation and recommend a safer alternative such as
constrained optimisation, a contextual bandit, or a narrower RL action
space.

------------------------------------------------------------------------

## 12. Definition of success

The project is technically successful when it has:

-   A documented BatteryLife v12 data pipeline.
-   Valid SOH and RUL baselines.
-   A rigorous degradation analysis.
-   A validated battery transition simulator, or a documented reason why
    one cannot be reliably built.
-   Fair comparison of fixed, rule-based, optimisation-based, and RL
    policies where feasible.
-   Explicit safety constraints and no unsupported action extrapolation.
-   Evaluation on unseen cells and supported chemistry groups.
-   Reproducible results, figures, tables, and an interactive
    demonstration.

Research success is **not** defined as RL winning every experiment. It
is defined by a well-supported question, correct methodology, honest
limitations, and reproducible evidence.

------------------------------------------------------------------------

## 13. Primary reference

**BatteryLife v12 --- Zenodo:**\
https://zenodo.org/records/21149533

Use the official v12 metadata, documentation, files, and licence as the
source of truth. Record the access date and exact version used in every
experiment.

------------------------------------------------------------------------

## Final direction

LifeGuard-RL will begin with BatteryLife v12 only.

First establish trustworthy battery-health and degradation models. Then
determine whether a reliable battery simulator can be built from the
recorded protocols. Finally, test whether RL can learn safer and
less-degrading operating decisions than conventional baselines.

**Do not rush to RL. First establish that the data, health model, and
simulator are trustworthy.**
