# LifeGuard-RL XJTU SOH reliability

**23 cells** · **6,938 cycles** · **1 flagged charge rows**.

The inputs are charge measurements available by the late-taper cutoff. The supervised target is measured discharge SOH.
Five within-XJTU folds hold out complete cells. Two transfer tests hold out a charge rate.

MAE averages cell-level errors on cycles where all methods provided an estimate. Coverage includes every recorded cycle.

| Evaluation | Model | MAE (pp) | SOH ≤82% MAE (pp) | Errors above 1 pp | Worst (pp) | Coverage |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2C_to_3C | Linear | 0.244 | 0.631 | 90 | 5.450 | 100.00% |
| 2C_to_3C | Linear + charge check | 0.244 | 0.631 | 90 | 5.450 | 100.00% |
| 2C_to_3C | Huber taper correction | 0.216 | 0.728 | 120 | 5.704 | 100.00% |
| 2C_to_3C | Huber + charge check | 0.216 | 0.728 | 120 | 5.704 | 100.00% |
| 3C_to_2C | Linear | 0.209 | 0.386 | 10 | 10.614 | 99.97% |
| 3C_to_2C | Linear + charge check | 0.206 | 0.386 | 10 | 5.279 | 99.97% |
| 3C_to_2C | Huber taper correction | 0.142 | 0.499 | 10 | 10.735 | 99.97% |
| 3C_to_2C | Huber + charge check | 0.139 | 0.499 | 10 | 5.646 | 99.97% |
| within_xjtu | Linear | 0.182 | 0.390 | 91 | 10.683 | 99.99% |
| within_xjtu | Linear + charge check | 0.181 | 0.390 | 91 | 5.409 | 99.99% |
| within_xjtu | Huber taper correction | 0.160 | 0.479 | 111 | 10.754 | 99.99% |
| within_xjtu | Huber + charge check | 0.159 | 0.479 | 111 | 5.741 | 99.99% |

## Cycle 390 check

The discharge measurement was **83.40% SOH**. Estimates on that cycle were:

- Linear gave **94.01%** with status **current**.
- Linear + charge check gave **81.52%** with status **fallback**.
- Huber taper correction gave **94.13%** with status **current**.
- Huber + charge check gave **81.37%** with status **fallback**.

## Benchmark decision

Keep **Linear + charge check** for this benchmark.

A candidate must retain coverage, keep average and near-EOL error at or below the linear baseline in both transfer directions, and reduce the number or size of large misses. The CSV records each check.

1 of 3 candidate methods met the rule. The XJTU check covers one cell design and two laboratory charge rates.
