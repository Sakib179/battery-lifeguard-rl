# LifeGuard-RL held-out digital twin validation

**23 cells** · **22 verified EOL crossings** · **five cell-level folds**.

The twin estimates future SOH under the recorded fixed charge rate. Each test cell stays outside calibration, including the charge-to-SOH fit. The charge initialization is the primary experiment.

All age trajectories contribute through the first verified EOL crossing or the last recorded cycle. EOL scoring uses the observed events. A rollout without a crossing in the simulated window has unavailable RUL.

- XJTU_2C_battery-4 contributes its measured trace through cycle 395. Its EOL was unobserved.

History adjusted the population fade estimate in **25 of 46** charge-initialized cell/landmark pairs.

## SOH forecast from the charge-only start

| Start cycle | Rate | Model | 1-cycle MAE (pp) | 10-cycle MAE (pp) | 50-cycle MAE (pp) |
| ---: | ---: | --- | ---: | ---: | ---: |
| 50 | 2C | Constant fade | 0.094 | 0.688 | 2.094 |
| 50 | 2C | Persistence | 0.048 | 0.209 | 0.375 |
| 50 | 2C | SOH-dependent fade | 0.056 | 0.310 | 0.454 |
| 50 | 2C | SOH-dependent fade + charge history | 0.056 | 0.311 | 0.469 |
| 50 | 3C | Constant fade | 0.167 | 0.437 | 1.370 |
| 50 | 3C | Persistence | 0.136 | 0.135 | 1.568 |
| 50 | 3C | SOH-dependent fade | 0.147 | 0.198 | 0.537 |
| 50 | 3C | SOH-dependent fade + charge history | 0.147 | 0.205 | 0.589 |
| 100 | 2C | Constant fade | 0.055 | 0.528 | 1.978 |
| 100 | 2C | Persistence | 0.039 | 0.057 | 0.491 |
| 100 | 2C | SOH-dependent fade | 0.039 | 0.192 | 0.526 |
| 100 | 2C | SOH-dependent fade + charge history | 0.040 | 0.266 | 1.330 |
| 100 | 3C | Constant fade | 0.129 | 0.368 | 1.596 |
| 100 | 3C | Persistence | 0.126 | 0.712 | 2.591 |
| 100 | 3C | SOH-dependent fade | 0.119 | 0.241 | 0.396 |
| 100 | 3C | SOH-dependent fade + charge history | 0.117 | 0.201 | 0.529 |

The three columns may cover different cells because a real reading is required at the forecast horizon. Methods are scored on common cells within each column. The horizon CSV includes the sample counts.

## RUL from the charge-only start

| Start cycle | Rate | Model | MAE (cycles) | Worst (cycles) | Available / observed |
| ---: | ---: | --- | ---: | ---: | ---: |
| 50 | 2C | Constant fade | 19.286 | 37.000 | 7/7 |
| 50 | 2C | Previous RUL model | 9.000 | 17.000 | 7/7 |
| 50 | 2C | SOH-dependent fade | 45.857 | 100.000 | 7/7 |
| 50 | 2C | SOH-dependent fade + charge history | 63.143 | 133.000 | 7/7 |
| 50 | 3C | Constant fade | 131.800 | 222.000 | 15/15 |
| 50 | 3C | Previous RUL model | 20.449 | 56.985 | 15/15 |
| 50 | 3C | SOH-dependent fade | 31.400 | 91.000 | 15/15 |
| 50 | 3C | SOH-dependent fade + charge history | 34.067 | 91.000 | 15/15 |
| 100 | 2C | Constant fade | 55.000 | 68.000 | 7/7 |
| 100 | 2C | Previous RUL model | 9.000 | 17.000 | 7/7 |
| 100 | 2C | SOH-dependent fade | 31.286 | 63.000 | 7/7 |
| 100 | 2C | SOH-dependent fade + charge history | 114.143 | 131.000 | 7/7 |
| 100 | 3C | Constant fade | 151.267 | 187.000 | 15/15 |
| 100 | 3C | Previous RUL model | 21.937 | 52.848 | 15/15 |
| 100 | 3C | SOH-dependent fade | 23.600 | 68.000 | 15/15 |
| 100 | 3C | SOH-dependent fade + charge history | 34.933 | 88.000 | 15/15 |

## Measured-SOH initialization at cycle 100

| Rate | Model | Charge-start 50-cycle SOH MAE (pp) | Measured-start 50-cycle SOH MAE (pp) | Common cells |
| --- | --- | ---: | ---: | ---: |
| 2C | SOH-dependent fade | 0.526 | 0.423 | 8 |
| 2C | SOH-dependent fade + charge history | 1.330 | 1.178 | 8 |
| 3C | SOH-dependent fade | 0.396 | 0.454 | 13 |
| 3C | SOH-dependent fade + charge history | 0.529 | 0.577 | 13 |

## Benchmark decision at cycle 100

- 2C RUL keeps **Previous RUL model** under the coverage, mean-error, and worst-error rule.
- 3C RUL keeps **Previous RUL model** under the coverage, mean-error, and worst-error rule.
- 2C trajectory check. The simple SOH controls remain the reference at these two horizons.
- 3C trajectory check. SOH-dependent fade, SOH-dependent fade + charge history improved both SOH horizons.

These are held-out results for the existing XJTU cohort. Every simulated trajectory keeps its original charge rate.
