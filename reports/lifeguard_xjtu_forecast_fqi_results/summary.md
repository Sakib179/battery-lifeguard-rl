# XJTU SOH forecasting, scenario-based lookahead and fitted Q iteration

## Results

**Selected three-test forecast: Direct Ridge with added history.** **Selected controller: Current lookahead.** FQI qualified as an improvement over PPO.

Forecast selection uses measured reference SOH. Controller selection uses the unchanged Notebook 20 simulator, so the two comparisons answer separate questions.

## SOH forecasts on held-out batteries

All rows use the same 149 three-test windows on 8 batteries. The same cohort was used in exploratory model screening. The one-test forecast remains the Notebook 19 model.

| Model | Mean absolute error (pp) | Worst 10% mean (pp) | Maximum (pp) | Paired MAE difference from Notebook 19 (95% interval) |
| --- | ---: | ---: | ---: | ---: |
| Notebook 19 recursive Ridge | 0.626 | 2.045 | 2.948 | +0.000 (+0.000 to +0.000) |
| Direct Ridge | 0.615 | 1.978 | 2.761 | -0.011 (-0.085 to +0.056) |
| Direct Ridge with added history | 0.598 | 2.035 | 2.603 | -0.027 (-0.090 to +0.036) |
| Compact Transformer | 0.648 | 2.228 | 3.294 | +0.022 (-0.109 to +0.176) |
| Residual Transformer | 0.575 | 2.205 | 2.990 | -0.050 (-0.095 to -0.001) |

The largest selected-forecast error occurred in XJTU_RW_battery-3 from recorded cycle 307. Forecast selection requires lower mean, tail and maximum errors. The table averages the three seeds for each Transformer forecast. The result bundle includes seed-level predictions and training-only Ridge selections.

## Discharge controller comparison

The evaluation reproduced every original PPO and lookahead trajectory at 133 starts. It used the same eight evaluation disturbances per start, 90% energy budget and action guard. Mean and tail controller metrics give each battery equal weight. The tail is the mean loss among the worst 10% of episodes for each battery. Modelled losses are reference-test SOH percentage points.

| Policy | Mean loss (pp) | Worst 10% mean loss (pp) | Maximum loss (pp) | Energy budget hit | Support stops |
| --- | ---: | ---: | ---: | ---: | ---: |
| PPO | 1.985 | 7.364 | 10.698 | 99.61% | 0.39% |
| Fitted Q iteration | 1.900 | 7.289 | 10.483 | 99.61% | 0.39% |
| Current lookahead | 1.755 | 7.102 | 10.480 | 99.61% | 0.39% |
| Scenario-based lookahead | 1.755 | 7.102 | 10.480 | 99.61% | 0.39% |

The scenario planner fell back to the original lookahead for 11 of 3189 decisions. It changed the executed schedule on 0 of 1064 matched evaluation episodes. Both learned policies face the same action mask. FQI uses simulated transition batches from the training batteries. The planning and evaluation draw streams have separate seeds.

## Paired controller decisions

| Comparison | Mean loss change (95% interval) | Tail loss change (pp) | Budget hit change | Support stop change | Meets comparison criteria |
| --- | ---: | ---: | ---: | ---: | --- |
| Fitted Q iteration vs PPO | -0.086 (-0.132 to -0.044) | -0.076 | +0.00 pp | +0.00 pp | Yes |
| Fitted Q iteration vs Current lookahead | +0.145 (+0.115 to +0.177) | +0.187 | +0.00 pp | +0.00 pp | No |
| Scenario-based lookahead vs Current lookahead | +0.000 (+0.000 to +0.000) | +0.000 | +0.00 pp | +0.00 pp | No |

Paired intervals resample held-out batteries. The control comparison allows up to a one percentage-point reduction in the energy budget hit rate and requires no increase in support stops. The scenario controller must improve average or tail SOH loss while the other stays at least as good. FQI's comparison uses lower average loss. The benchmark covers 30 operating cycles of modelled discharge and does not estimate real-world lifetime gains.

[Fitted Q Iteration research](https://www.jmlr.org/papers/v6/ernst05a.html) · [Scenario-based MPC research](https://arxiv.org/abs/1307.5640)
