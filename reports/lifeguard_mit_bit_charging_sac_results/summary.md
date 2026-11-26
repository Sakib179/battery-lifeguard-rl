# MIT–BIT charging forecast refinement and Discrete SAC

## Results

**Selected controller: Notebook 18 MPC.** Forecasts were validated against measured charge timing and meter-checked delivered Wh. Controllers used a common Ridge transition simulator with training-fold disturbances. Each policy retained the original 90% energy budget.

## Held-out forecast comparison

| Horizon | Model | Outcome | Windows | Mean absolute error | Worst 10% mean | Maximum error |
| ---: | --- | --- | ---: | ---: | ---: | ---: |
| 5 cycles | Notebook 18 Ridge | Delivered Wh | 923 | 0.470 | 1.501 | 3.451 |
| 5 cycles | Notebook 18 Ridge | Charging minutes | 923 | 2.692 | 10.761 | 24.411 |
| 5 cycles | Selected per training fold | Delivered Wh | 923 | 0.300 | 1.001 | 3.203 |
| 5 cycles | Selected per training fold | Charging minutes | 923 | 1.252 | 4.752 | 11.216 |
| 10 cycles | Notebook 18 Ridge | Delivered Wh | 862 | 0.901 | 2.700 | 6.323 |
| 10 cycles | Notebook 18 Ridge | Charging minutes | 862 | 5.090 | 19.077 | 50.153 |
| 10 cycles | Selected per training fold | Delivered Wh | 862 | 0.644 | 2.016 | 6.014 |
| 10 cycles | Selected per training fold | Charging minutes | 862 | 2.509 | 8.487 | 18.842 |
| 15 cycles | Notebook 18 Ridge | Delivered Wh | 801 | 1.411 | 3.946 | 6.905 |
| 15 cycles | Notebook 18 Ridge | Charging minutes | 801 | 7.767 | 26.807 | 80.495 |
| 15 cycles | Selected per training fold | Delivered Wh | 801 | 0.921 | 2.787 | 6.806 |
| 15 cycles | Selected per training fold | Charging minutes | 801 | 3.882 | 12.566 | 32.274 |

The final catalog includes Ridge, capacity-anchored linear correction, Kernel Ridge residual correction, gradient boosting and a compact GRU. All candidate scores and fold selections are in the ZIP. The same MIT–BIT cohort was used in model screening.

Delivered energy reduced mean, worst-decile and maximum errors by 34.7%, 29.4% and 1.4%, respectively, and fell short of the full 20% / 15% / 10% target. Its mean error change had a paired 95% interval of -0.610 to -0.371.

Charging time reduced mean, worst-decile and maximum errors by 50.0%, 53.1% and 59.9%, respectively, and met the full 20% / 15% / 10% target. Its mean error change had a paired 95% interval of -4.788 to -3.056.

### Previously identified cases

| Battery | Start cycle | Target | Ridge absolute error at 15 cycles | Selected absolute error at 15 cycles |
| --- | ---: | --- | ---: | ---: |
| #59 | 16 | minutes | 80.495 | 22.581 |
| #77 | 56 | wh | 6.905 | 6.806 |

## Controller simulation on 164 matched starts

The original deterministic MPC and fixed 1C budgets reproduce Notebook 18. The table below includes eight matched disturbance paths per start. SAC is averaged across three training seeds. Means weight batteries equally.

| Policy | Charging minutes | Delivered Wh | Budget hit rate | Worst Wh shortfall |
| --- | ---: | ---: | ---: | ---: |
| Fixed 1C | 604.12 | 81.68 | 99.92% | 0.696 |
| Notebook 18 MPC | 489.95 | 76.41 | 97.27% | 2.180 |
| Forecast-refined MPC | 486.78 | 76.07 | 92.27% | 5.374 |
| Discrete SAC | 486.46 | 76.04 | 92.12% | 5.374 |

## Paired controller comparisons

| Policy vs baseline | Charging-time difference (95% interval, min) | Budget hit change | Max Wh shortfall change | Qualifies |
| --- | ---: | ---: | ---: | --- |
| Forecast-refined MPC vs Notebook 18 MPC | -3.16 (-5.01 to -1.33) | -5.00 pp | +3.193 | No |
| Discrete SAC vs Notebook 18 MPC | -3.49 (-5.36 to -1.67) | -5.15 pp | +3.193 | No |
| Discrete SAC vs Forecast-refined MPC | -0.33 (-0.77 to -0.02) | -0.15 pp | +0.000 | Yes |

Advancement requires a negative upper 95% confidence bound for charging time, a budget hit-rate decrease of at most one percentage point, and no increase in maximum Wh shortfall. Intervals resample batteries. The simulated outcomes cover 15 cycles with 3C discharge.

## Recorded randomized replay

| Policy | Seed | Full matches | Complete matches (batteries) | Measured minutes | Measured Wh |
| --- | ---: | ---: | ---: | ---: | ---: |
| Forecast-refined MPC | — | 28/819 | 28 (23) | 474.47 | 74.17 |
| Discrete SAC | 42 | 26/819 | 26 (22) | 468.41 | 72.95 |
| Discrete SAC | 73 | 26/819 | 26 (22) | 468.41 | 72.95 |
| Discrete SAC | 101 | 26/819 | 26 (22) | 468.41 | 72.95 |
| Fixed 1C | — | 21/819 | 19 (18) | 591.62 | 80.36 |
| Notebook 18 MPC | — | 24/819 | 24 (18) | 478.21 | 73.30 |

Only actions that match all three recorded choices contribute to the outcome-specific replay estimates. Each policy can match a different set of trajectories. Replay means use normalized inverse propensity weights and equal battery weight before matching. The replay evidence is descriptive.

[MIT–BIT v3 dataset](https://data.mendeley.com/datasets/kw34hhw7xg/3) · [Discrete SAC](https://arxiv.org/abs/1910.07207)
