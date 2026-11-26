# XJTU discharge forecasts and controller benchmark

**Selected controller under the original simulation is Original Lookahead.**
Forecasts were scored against recorded reference SOH and integrated Wh. Controller outcomes came from the frozen Notebook 20 simulator. Results represent modeled outcomes over 30 operating cycles.

## Revised forecasts on the same held-out windows

Each error cell shows original Ridge or Direct Ridge, the previous Notebook 23 recommendation, and the revised recommendation. The proposed correction is promoted when mean, worst-decile and maximum error all match or improve on the previous recommendation and at least one decreases.

| Setting | Target | Windows | Mean absolute error | Worst 10% mean | Maximum error | Recommendation |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 10 ahead at the start | SOH (pp) | 165 | 0.196 → 0.123 → 0.123 | 0.492 → 0.345 → 0.345 | 0.757 → 0.528 → 0.528 | Previous |
| 10 ahead at the start | Delivered energy (Wh) | 165 | 0.436 → 0.259 → 0.259 | 1.223 → 0.762 → 0.762 | 1.865 → 1.203 → 1.203 | Previous |
| 20 ahead at the start | SOH (pp) | 157 | 0.409 → 0.409 → 0.356 | 1.167 → 1.167 → 0.910 | 1.586 → 1.586 → 1.522 | Revised |
| 20 ahead at the start | Delivered energy (Wh) | 157 | 0.838 → 0.485 → 0.458 | 2.144 → 1.440 → 1.307 | 2.960 → 2.156 → 2.080 | Revised |
| 30 ahead at the start | SOH (pp) | 149 | 0.598 → 0.598 → 0.520 | 2.035 → 2.035 → 1.747 | 2.603 → 2.603 → 2.377 | Revised |
| 30 ahead at the start | Delivered energy (Wh) | 149 | 1.258 → 0.909 → 0.909 | 3.172 → 2.291 → 2.291 | 4.186 → 3.378 → 3.378 | Previous |
| Refresh after 10 of 30 | SOH (pp) | 149 | 0.406 → 0.406 → 0.342 | 1.185 → 1.185 → 0.901 | 1.586 → 1.586 → 1.522 | Revised |
| Refresh after 10 of 30 | Delivered energy (Wh) | 149 | 0.834 → 0.491 → 0.466 | 2.170 → 1.475 → 1.330 | 2.960 → 2.156 → 2.081 | Revised |
| Refresh after 20 of 30 | SOH (pp) | 149 | 0.192 → 0.122 → 0.122 | 0.503 → 0.350 → 0.350 | 0.757 → 0.528 → 0.528 | Previous |
| Refresh after 20 of 30 | Delivered energy (Wh) | 149 | 0.416 → 0.260 → 0.260 | 1.086 → 0.787 → 0.787 | 1.504 → 1.203 → 1.203 | Previous |

### Proposed correction compared with the previous recommendation

| Setting | Target | Mean error reduction | Worst 10% reduction | Maximum reduction | Paired MAE change 95% interval |
| --- | --- | ---: | ---: | ---: | ---: |
| 10 ahead at the start | SOH (pp) | +0.0% | +0.0% | +0.0% | +0.000 to +0.000 |
| 10 ahead at the start | Delivered energy (Wh) | +4.1% | +4.6% | -6.1% | -0.025 to +0.000 |
| 20 ahead at the start | SOH (pp) | +13.0% | +22.0% | +4.0% | -0.085 to -0.022 |
| 20 ahead at the start | Delivered energy (Wh) | +5.5% | +9.2% | +3.6% | -0.058 to +0.007 |
| 30 ahead at the start | SOH (pp) | +13.2% | +14.1% | +8.7% | -0.117 to -0.040 |
| 30 ahead at the start | Delivered energy (Wh) | +3.2% | -1.9% | -15.7% | -0.081 to +0.015 |
| Refresh after 10 of 30 | SOH (pp) | +15.8% | +23.9% | +4.0% | -0.110 to -0.026 |
| Refresh after 10 of 30 | Delivered energy (Wh) | +5.0% | +9.8% | +3.5% | -0.059 to +0.013 |
| Refresh after 20 of 30 | SOH (pp) | -1.2% | +0.0% | +0.0% | +0.000 to +0.004 |
| Refresh after 20 of 30 | Delivered energy (Wh) | +4.7% | +4.7% | -5.1% | -0.027 to -0.001 |

Weights and correction limits were selected within the training batteries. Inner candidate predictions and Wh bias-training residuals were cross-fitted by battery. Rolling energy predictions add the energy measured before the update to the remaining energy forecast. These eight batteries also informed earlier screening.

The 50/50 blends appear in the CSV as exploratory comparisons. The CSVs also include fold settings, worst cases, and the subset whose SOH was below 90% when the forecast was made.

The controller section reports the original Notebook 23 benchmark with the earlier planner forecasts.

## Earlier Notebook 23 forecast benchmark

The tables report the earlier baseline followed by the fold-selected forecast. Mean absolute errors give each battery equal weight. The upper decile pools matched windows. The tables use an identical forecast origin for each within-row comparison. A positive reduction means lower error.

| Setting | Target | Windows | Mean absolute error | Worst 10% mean | Maximum error | Recommendation |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| At the start, 10 ahead | SOH (pp) | 165 | 0.196 → 0.123 (+37.1% reduction) | 0.492 → 0.345 (+29.9% reduction) | 0.757 → 0.528 (+30.2% reduction) | New |
| At the start, 10 ahead | Delivered energy (Wh) | 165 | 0.436 → 0.259 (+40.6% reduction) | 1.223 → 0.762 (+37.6% reduction) | 1.865 → 1.203 (+35.5% reduction) | New |
| At the start, 20 ahead | SOH (pp) | 157 | 0.409 → 0.354 (+13.5% reduction) | 1.167 → 1.104 (+5.4% reduction) | 1.586 → 1.717 (-8.2% reduction) | Baseline |
| At the start, 20 ahead | Delivered energy (Wh) | 157 | 0.838 → 0.485 (+42.2% reduction) | 2.144 → 1.440 (+32.9% reduction) | 2.960 → 2.156 (+27.2% reduction) | New |
| At the start, 30 ahead | SOH (pp) | 149 | 0.598 → 0.613 (-2.4% reduction) | 2.035 → 1.972 (+3.1% reduction) | 2.603 → 3.401 (-30.6% reduction) | Baseline |
| At the start, 30 ahead | Delivered energy (Wh) | 149 | 1.258 → 0.909 (+27.7% reduction) | 3.172 → 2.291 (+27.8% reduction) | 4.186 → 3.378 (+19.3% reduction) | New |
| 10 elapsed of 30 | SOH (pp) | 149 | 0.406 → 0.351 (+13.5% reduction) | 1.185 → 1.125 (+5.1% reduction) | 1.586 → 1.717 (-8.2% reduction) | Baseline |
| 10 elapsed of 30 | Delivered energy (Wh) | 149 | 0.834 → 0.491 (+41.2% reduction) | 2.170 → 1.475 (+32.1% reduction) | 2.960 → 2.156 (+27.2% reduction) | New |
| 20 elapsed of 30 | SOH (pp) | 149 | 0.192 → 0.122 (+36.4% reduction) | 0.503 → 0.350 (+30.6% reduction) | 0.757 → 0.528 (+30.2% reduction) | New |
| 20 elapsed of 30 | Delivered energy (Wh) | 149 | 0.416 → 0.260 (+37.5% reduction) | 1.086 → 0.787 (+27.5% reduction) | 1.504 → 1.203 (+20.0% reduction) | New |

Fixed forecasts used up to five past reference tests, completed operating energy and a measured reference discharge curve. Forecasts also used the first prescribed current and duration of each planned discharge cycle. Energy candidates included cycle-level Ridge, an approximate Kernel Ridge, shallow boosting, a compact GRU and a variant with a cross-fitted SOH forecast. The SOH catalog included local trend, training-battery matches, curve-based regression and an R3-transfer model adapted on the Random Walk training batteries.

The model catalog and blends were selected by nested leave-one-battery-out folds. Fixed-origin recommendations require all three error metrics to match or improve on the incumbent. The experiment targeted a 50% reduction in all three fixed-origin error metrics at 30 cycles. The same cohort informed earlier model screening. The rolling results use actual measurements made before each refreshed prediction. The CSVs include battery-level predictions, bias correction settings and overlap sensitivity for the age and nearest-battery methods.

### Prespecified difficult cases

| Target | Battery | Start cycle | Prior absolute error | New absolute error |
| --- | --- | ---: | ---: | ---: |
| SOH | XJTU_RW_battery-3 | 307 | 2.603 | 2.555 |
| WH | XJTU_RW_battery-1 | 32 | 4.186 | 0.975 |

## Controller outcomes

All policies shared 133 starts, eight disturbances per start, the 90% energy budget and the original action guard. Forecast-based planners could use corrected forecasts to rank schedules and used the same simulator for scoring. Simulated updates supplied reference SOH and delivered Wh. The last measured physical discharge curve was held fixed during simulated rollouts. The original study and the 25% larger disturbance study are shown below.

| Disturbance | Policy | Mean SOH loss (pp) | Worst 10% loss (pp) | Maximum SOH loss (pp) | Budget hit | Support stops |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Original | Fixed middle template | 1.984 | 7.268 | 10.480 | 99.61% | 0.39% |
| Original | Fitted Q iteration | 1.900 | 7.289 | 10.483 | 99.61% | 0.39% |
| Original | Original Lookahead | 1.755 | 7.102 | 10.480 | 99.61% | 0.39% |
| Original | Forecast MPC | 1.842 | 7.157 | 10.521 | 99.61% | 0.39% |
| Original | PPO | 1.985 | 7.364 | 10.698 | 99.61% | 0.39% |
| Original | Risk-aware MPC | 1.842 | 7.158 | 10.521 | 99.61% | 0.39% |
| Original | SOH rule | 1.988 | 7.286 | 10.587 | 99.61% | 0.39% |
| Original | Discrete SAC | 1.926 | 7.367 | 10.698 | 99.61% | 0.39% |
| Stress | Fixed middle template | 1.905 | 7.325 | 10.884 | 99.61% | 0.39% |
| Stress | Fitted Q iteration | 1.821 | 7.346 | 10.992 | 99.61% | 0.39% |
| Stress | Original Lookahead | 1.676 | 7.164 | 10.884 | 99.61% | 0.39% |
| Stress | Forecast MPC | 1.762 | 7.219 | 10.926 | 99.61% | 0.39% |
| Stress | PPO | 1.907 | 7.420 | 11.103 | 99.61% | 0.39% |
| Stress | Risk-aware MPC | 1.762 | 7.220 | 10.926 | 99.61% | 0.39% |
| Stress | SOH rule | 1.909 | 7.339 | 10.992 | 99.61% | 0.39% |
| Stress | Discrete SAC | 1.849 | 7.424 | 11.103 | 99.61% | 0.39% |

### Paired comparisons against original Lookahead

| Policy | Mean loss reduction | Worst 10% loss reduction | Mean change 95% interval (pp) | Qualifies |
| --- | ---: | ---: | ---: | --- |
| Fixed middle template | -13.1% | -2.3% | +0.209 to +0.248 | No |
| SOH rule | -13.3% | -2.6% | +0.209 to +0.254 | No |
| Forecast MPC | -5.0% | -0.8% | +0.055 to +0.124 | No |
| Risk-aware MPC | -5.0% | -0.8% | +0.055 to +0.124 | No |
| PPO | -13.1% | -3.7% | +0.202 to +0.257 | No |
| Fitted Q iteration | -8.3% | -2.6% | +0.115 to +0.177 | No |
| Discrete SAC | -9.8% | -3.7% | +0.152 to +0.193 | No |

Advancement requires a reduction of at least 10% in mean or worst-decile SOH loss, a negative upper paired 95% confidence bound for that metric, no increase in the other SOH loss metrics or support stops, and a budget hit rate decline of at most one percentage point.

### Discrete SAC by seed

| Seed | Mean SOH loss (pp) | Worst 10% loss (pp) | Maximum loss (pp) | Budget hit |
| ---: | ---: | ---: | ---: | ---: |
| 42 | 1.942 | 7.313 | 10.480 | 99.61% |
| 73 | 1.913 | 7.330 | 10.698 | 99.61% |
| 101 | 1.924 | 7.338 | 10.590 | 99.61% |

SAC uses the same simulated training transitions as FQI. The finite-horizon reward is the reference SOH change, with a terminal penalty of three per Wh of energy shortfall and a five-point penalty for stopping outside support. Controller intervals resample batteries.

### Planning headroom in the simulator

| Disturbance | Episodes with a feasible complete schedule | Lookahead matches hindsight minimum |
| --- | ---: | ---: |
| Original | 1061 | 1061 |
| Stress | 1061 | 1061 |

The hindsight calculation enumerates complete, guard-compliant schedules that meet the original energy budget. It has access to the full simulator disturbance trajectory for each episode. This bound applies to the fixed set of templates and to the transition assumptions in this simulator.

[XJTU protocols](https://wang-fujin.github.io/) · [XJTU dataset](https://zenodo.org/records/10963339) · [Discrete SAC](https://arxiv.org/abs/1910.07207)
