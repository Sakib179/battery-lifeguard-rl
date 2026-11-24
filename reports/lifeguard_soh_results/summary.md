# LifeGuard-RL XJTU SOH results

Mode **benchmark** · 23 cells · 6,937 of 6,938 eligible cycles

SOH uses full discharge capacity divided by the 2.0 Ah nominal capacity. Each prediction uses data available before discharge.

Pilot 80% crossings verified at cycle 401 for the 2C cell and cycle 291 for the 3C cell.

- Excluded **1** cycles with no taper cutoff.

Dual-GPU stage **disabled**.

Lowest observed held-out mean per-cell MAE **hist_gradient_boosting**.

MAE and RMSE are calculated within each held-out cell and then averaged across cells.

| Model | Cells | Cycles | MAE (pp) | RMSE (pp) |
| --- | ---: | ---: | ---: | ---: |
| hist_gradient_boosting | 23 | 6937 | 0.1549 | 0.2555 |
| ridge_charging_features | 23 | 6937 | 0.1931 | 0.3840 |
| ridge_cycle_and_rate | 23 | 6937 | 2.4899 | 3.0332 |
| ridge_cycle_only | 23 | 6937 | 2.7211 | 3.2926 |

The comparison estimates within-collection performance on unseen XJTU cells at the two represented charge rates. Re-evaluate the selected model on an independent collection before claiming broader generalisation.
