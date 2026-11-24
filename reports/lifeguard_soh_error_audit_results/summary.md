# LifeGuard-RL XJTU SOH error audit

23 cells · 6,938 cycles · 1 flagged charge rows.

All predictions use the charge trace through late taper and, when available, prior charging data from the same cell. The discharge measurement supplies training targets and held-out labels.

Errors are reported for cycles where every model supplied an estimate. Coverage includes every recorded cycle.

| Evaluation | Model | MAE (pp) | SOH ≤82% MAE (pp) | Errors above 1 pp | Worst (pp) | Coverage |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2C_to_3C | First cycle + history | 0.515 | 1.138 | 236 | 4.851 | 100.00% |
| 2C_to_3C | First-cycle correction | 0.225 | 0.631 | 78 | 4.611 | 100.00% |
| 2C_to_3C | Linear + check | 0.244 | 0.631 | 90 | 5.450 | 100.00% |
| 3C_to_2C | First cycle + history | 0.556 | 0.769 | 3 | 2.313 | 99.97% |
| 3C_to_2C | First-cycle correction | 0.194 | 0.386 | 2 | 2.071 | 99.97% |
| 3C_to_2C | Linear + check | 0.206 | 0.386 | 10 | 5.279 | 99.97% |
| within_xjtu | First cycle + history | 0.147 | 0.261 | 69 | 4.668 | 99.99% |
| within_xjtu | First-cycle correction | 0.165 | 0.390 | 71 | 4.598 | 99.99% |
| within_xjtu | Linear + check | 0.181 | 0.390 | 91 | 5.409 | 99.99% |

## Where the largest errors were concentrated

| Model | First-cycle test cells | First-cycle MAE (pp) | First-cycle errors above 1 pp | Errors above 1 pp on XJTU_3C_battery-3 |
| --- | ---: | ---: | ---: | ---: |
| Linear + check | 23 | 4.944 | 23 | 61 |
| First-cycle correction | 23 | 0.361 | 3 | 60 |
| First cycle + history | 23 | 0.361 | 3 | 74 |

## Benchmark decision

Keep **First-cycle correction** for this benchmark.

Both transfer directions must have lower mean error and retain coverage. Near-EOL error, errors above one point, and the worst error must stay at or below the baseline in each direction.

1 of 2 candidates met these conditions. The error patterns were identified on these same XJTU cells. Any improvement needs confirmation on a separate cohort.
