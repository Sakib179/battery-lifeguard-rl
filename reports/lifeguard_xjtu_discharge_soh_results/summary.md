# XJTU reference-test SOH forecasting and RL feasibility

## Conclusion

**The Random Walk evidence meets the prespecified criteria for a PPO pilot.** This experiment predicts SOH measured during standardized capacity tests from the preceding health measurements and a specified discharge schedule.

## Reference test audit

| Cohort | Batteries | Reference tests verified | Accepted intervals | Intervals with measured SOH increase |
| --- | ---: | ---: | ---: | ---: |
| Random Walk | 8 | 173/173 | 165 | 24 |
| R3 | 8 | 945/945 | 937 | 181 |

SOH is diagnostic discharge capacity divided by nominal 2.0 Ah. The audit verifies the discharge current, voltage cutoff, charge current and agreement between measured and integrated capacity. Random Walk intervals have ten operating cycles and R3 intervals have five. Changes in measured SOH can include short-term recovery and measurement variability.

## Held-out forecast errors

All errors are SOH percentage points. MAE gives each battery equal weight. The tail uses the largest 10% of absolute errors across scored windows. The realized-exposure row uses data recorded during the forecast interval and is a retrospective diagnostic.

| Cohort | Tests ahead | Model | Windows | Mean absolute error | Worst 10% mean | Maximum error |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| Random Walk | 1 | Persistence | 165 | 1.141 | 3.768 | 5.800 |
| Random Walk | 1 | Past trend | 165 | 0.592 | 1.784 | 2.300 |
| Random Walk | 1 | No-action Ridge | 165 | 0.195 | 0.498 | 0.707 |
| Random Walk | 1 | Current-only Ridge | 165 | 0.197 | 0.481 | 0.717 |
| Random Walk | 1 | Action-aware Ridge | 165 | 0.196 | 0.492 | 0.757 |
| Random Walk | 1 | Realized-exposure Ridge (diagnostic) | 165 | 0.196 | 0.560 | 0.695 |
| Random Walk | 3 | Persistence | 149 | 2.821 | 8.880 | 12.900 |
| Random Walk | 3 | Past trend | 149 | 1.984 | 5.143 | 6.600 |
| Random Walk | 3 | No-action Ridge | 149 | 0.653 | 2.019 | 2.815 |
| Random Walk | 3 | Current-only Ridge | 149 | 0.640 | 2.004 | 2.738 |
| Random Walk | 3 | Action-aware Ridge | 149 | 0.626 | 2.045 | 2.948 |
| Random Walk | 3 | Realized-exposure Ridge (diagnostic) | 149 | 0.581 | 2.017 | 2.734 |
| R3 | 1 | Persistence | 937 | 0.227 | 0.752 | 1.400 |
| R3 | 1 | Past trend | 937 | 0.115 | 0.373 | 1.250 |
| R3 | 1 | No-action Ridge | 937 | 0.086 | 0.227 | 0.454 |
| R3 | 1 | Current-only Ridge | 937 | 0.086 | 0.227 | 0.454 |
| R3 | 1 | Action-aware Ridge | 937 | 0.086 | 0.227 | 0.454 |
| R3 | 1 | Realized-exposure Ridge (diagnostic) | 937 | 0.086 | 0.225 | 0.453 |
| R3 | 3 | Persistence | 921 | 0.578 | 1.982 | 3.800 |
| R3 | 3 | Past trend | 921 | 0.269 | 1.107 | 2.900 |
| R3 | 3 | No-action Ridge | 921 | 0.193 | 0.523 | 1.221 |
| R3 | 3 | Current-only Ridge | 921 | 0.193 | 0.523 | 1.221 |
| R3 | 3 | Action-aware Ridge | 921 | 0.193 | 0.523 | 1.221 |
| R3 | 3 | Realized-exposure Ridge (diagnostic) | 921 | 0.191 | 0.507 | 1.188 |

## What the action data added

The primary comparison uses Random Walk at three tests ahead. Each row compares the same held-out windows. A negative difference favors the action-aware model. Intervals resample whole batteries.

| Baseline | Action-aware MAE change (pp) | 95% interval (pp) | Batteries with lower error |
| --- | ---: | ---: | ---: |
| Past trend | -1.358 | -1.812 to -0.848 | 8/8 |
| No-action Ridge | -0.028 | -0.055 to -0.008 | 6/8 |

**Comparable choices across folds** · 2 A for 2 min, 2 A for 3 min, 2 A for 4 min, 2 A for 5 min, 2 A for 6 min, 3 A for 2 min, 3 A for 3 min, 3 A for 4 min, 3 A for 5 min, 3 A for 6 min, 4 A for 2 min, 4 A for 3 min, 4 A for 4 min, 4 A for 5 min, 4 A for 6 min. Each pair had records on at least 4 training batteries in both reference SOH bands from 80% to under 90% and from 90% upward. The gate requires these pairs to cover at least two different current levels.

Verified an initial current–duration pair in 1650/1650 Random Walk operating cycles. The interval audit excluded 0 intervals across both cohorts. The forecast treats the first plateaus as the prescribed schedule. Remaining discharge and cutoff-dependent timing are observational and enter the retrospective model only.

The R3 comparison stays separate because its verified intervals repeat the same five rates and use a different diagnostic charging current. The cohort tests forecast accuracy under that schedule.

[Original XJTU experimental protocols](https://wang-fujin.github.io/) · [XJTU battery dataset](https://zenodo.org/records/10963339)
