# LifeGuard-RL RUL from charging features

**23 cells** audited · **22** verified 80% SOH crossings.

The primary decision uses predictions at cycle 100 for 3C cells. Cycle 50 provides the earlier comparison.
All models use charging data available by the observation cycle. The measured discharge defines the EOL label.

- XJTU_2C_battery-4 has status right censored and is excluded from supervised scoring.

## 3C held-out errors

| Observation cycle | Model | Cells | MAE | Worst absolute error | MAE for EOL ≤200 |
| ---: | --- | ---: | ---: | ---: | ---: |
| 50 | 3C Ridge with recent signals and change | 15 | 20.45 | 56.99 | 15.38 |
| 50 | 3C Ridge with recent signals | 15 | 21.05 | 64.77 | 16.39 |
| 50 | 3C Ridge with original features | 15 | 24.41 | 63.05 | 19.88 |
| 50 | Original Ridge with pooled 2C and 3C | 15 | 25.10 | 58.67 | 20.91 |
| 50 | Protocol median | 15 | 56.30 | 155.50 | 132.00 |
| 100 | 3C Ridge with original features | 15 | 21.49 | 59.89 | 21.68 |
| 100 | Original Ridge with pooled 2C and 3C | 15 | 21.94 | 52.85 | 21.90 |
| 100 | 3C Ridge with recent signals | 15 | 22.10 | 44.33 | 18.69 |
| 100 | 3C Ridge with recent signals and change | 15 | 22.30 | 44.42 | 21.24 |
| 100 | Protocol median | 15 | 56.30 | 155.50 | 132.00 |

Errors are in cycles. The short-life group is evaluated using the observed EOL cycle.

The rerun of the original 3C baseline at cycle 100 has MAE **21.94** and worst error **52.85** cycles.

## Benchmark decision

- 3C uses **Original Ridge with pooled 2C and 3C** for this benchmark. 0 of 3 candidates reduced both mean and worst error at cycle 100 with no increase in short-life MAE.
- 2C keeps the protocol median. Its cycle-100 MAE is **9.00** cycles.

This is a comparison on the existing XJTU folds. Any improvement needs confirmation on a separate cohort.
