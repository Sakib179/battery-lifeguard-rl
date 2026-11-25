# XJTU mean and worst-error audit

## Current SOH

SOH errors are in percentage points. MAE weights each held-out cell equally. Near-EOL scores use measured SOH of 82% or lower. The guard uses past valid charge-based estimates.

| Evaluation | Source model | Variant | MAE | Worst | Near-EOL MAE | Coverage (%) |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| 2C_to_3C | First-cycle + history | baseline | 0.515 | 4.851 | 1.138 | 100.000 |
| 2C_to_3C | First-cycle + history | guarded | 0.507 | 3.598 | 1.138 | 100.000 |
| 2C_to_3C | First-cycle correction | baseline | 0.225 | 4.611 | 0.631 | 100.000 |
| 2C_to_3C | First-cycle correction | guarded | 0.217 | 3.375 | 0.631 | 100.000 |
| 3C_to_2C | First-cycle + history | baseline | 0.556 | 2.313 | 0.769 | 99.969 |
| 3C_to_2C | First-cycle + history | guarded | 0.556 | 2.313 | 0.765 | 99.969 |
| 3C_to_2C | First-cycle correction | baseline | 0.194 | 2.071 | 0.386 | 99.969 |
| 3C_to_2C | First-cycle correction | guarded | 0.194 | 2.071 | 0.386 | 99.969 |
| within_xjtu | First-cycle + history | baseline | 0.147 | 4.668 | 0.261 | 99.986 |
| within_xjtu | First-cycle + history | guarded | 0.141 | 3.369 | 0.260 | 99.986 |
| within_xjtu | First-cycle correction | baseline | 0.165 | 4.598 | 0.390 | 99.986 |
| within_xjtu | First-cycle correction | guarded | 0.159 | 3.334 | 0.390 | 99.986 |

## RUL at cycle 100

MAE and maximum errors are in cycles. The short-life group reached EOL by cycle 200.

| Charge rate | Model | MAE | Worst | Short-life MAE |
| --- | --- | ---: | ---: | ---: |
| 3C | ridge_charge_history_pooled | 21.937 | 52.848 | 21.900 |
| 3C | ridge_3c_recent_signals | 22.102 | 44.334 | 18.686 |
| 3C | ridge_average | 21.228 | 48.175 | 20.293 |
| 3C | tail_penalized_linear | 21.166 | 46.972 | 18.477 |
| 2C | protocol_median | 9.000 | 17.000 | — |

## 3C future SOH from cycle 100

| RUL input | Full curve MAE (pp) | Last 20 MAE (pp) | Last 20 worst (pp) | +50 MAE (pp) | EOL timing MAE (cycles) |
| --- | ---: | ---: | ---: | ---: | ---: |
| late_life_calibrated | 1.330 | 2.187 | 7.120 | 0.422 | 20.800 |
| tail_penalized_linear | 1.484 | 2.370 | 7.520 | 0.481 | 21.933 |

The RUL model tunes the coefficient penalty inside each outer training fold. The guard and loss weights were chosen during exploration on this XJTU cohort. The results describe held-out cells within that cohort.
