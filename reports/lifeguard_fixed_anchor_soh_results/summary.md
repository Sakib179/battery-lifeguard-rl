# XJTU fixed cycle-100 SOH forecast

23 held-out cells across five folds. The forecast uses charge information through cycle 100.

SOH columns are mean or maximum absolute error in percentage points. RUL MAE is in cycles.

| Rate | Model | +10 MAE | +50 MAE | Last 20 MAE | Last 20 worst | SOH MAE at EOL | RUL MAE |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2C | persistence | 0.057 | 0.491 | 16.265 | 18.510 | 17.763 | — |
| 2C | constant_fade | 0.528 | 1.978 | 1.911 | 3.910 | 2.892 | 55.000 |
| 2C | soh_dependent | 0.192 | 0.526 | 1.144 | 3.400 | 0.242 | 31.286 |
| 2C | soh_dependent_with_history | 0.266 | 1.330 | 1.305 | 3.400 | 0.214 | 114.143 |
| 2C | late_life_calibrated | 0.192 | 0.526 | 0.743 | 3.067 | 0.688 | 9.000 |
| 3C | persistence | 0.712 | 2.591 | 12.706 | 18.332 | 15.552 | — |
| 3C | constant_fade | 0.368 | 1.596 | 5.541 | 10.034 | 7.899 | 151.267 |
| 3C | soh_dependent | 0.241 | 0.396 | 2.627 | 8.758 | 2.388 | 23.600 |
| 3C | soh_dependent_with_history | 0.201 | 0.529 | 2.293 | 6.700 | 1.633 | 34.933 |
| 3C | late_life_calibrated | 0.241 | 0.422 | 2.187 | 7.120 | 2.136 | 20.800 |

## Dashboard benchmark decision

- **2C passed.** Last-20 MAE 1.144 → 0.743 pp against the best original model. Earlier RUL benchmark MAE is 9.000 cycles.
- **3C passed.** Last-20 MAE 2.293 → 2.187 pp against the best original model. Earlier RUL benchmark MAE is 21.937 cycles.

The gate requires lower last-20 MAE than the best Notebook 07 model and at most 0.05 pp higher +10 and +50 MAE than the original SOH-dependent model, with full paired coverage.

Last-20 and EOL scores require a verified crossing. The right-censored cell contributes to horizon scores when the target cycle was recorded. A forecast that reaches 80% early can show a small SOH error at observed EOL, so the RUL timing errors are reported separately.

The two calibration methods were chosen after inspecting the same XJTU cohort. Held-out cell scores here measure within-cohort performance.
