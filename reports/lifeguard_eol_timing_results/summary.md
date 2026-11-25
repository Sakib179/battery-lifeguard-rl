# XJTU 3C cycle-100 EOL timing

15 verified cells across the five saved folds. Every feature comes from cycles through 100.

## Direct RUL estimates

| Model | Mean error (cycles) | Worst (cycles) | EOL ≤200 MAE (cycles) |
| --- | ---: | ---: | ---: |
| Notebook 06 pooled Ridge | 21.937 | 52.848 | 21.900 |
| Notebook 06 recent-signal Ridge | 22.102 | 44.334 | 18.686 |
| Notebook 06 equal-weight average | 21.228 | 48.175 | 20.293 |
| Charge summary | 22.157 | 44.334 | 19.799 |
| Charge summary + charge curve | 24.866 | 60.736 | 17.649 |
| Charge summary + charge and discharge curves | 24.692 | 88.928 | 16.447 |

## SOH trajectories

| Model | Full curve MAE (pp) | Last 20 MAE (pp) | Last 20 worst (pp) | +10 MAE (pp) | +50 MAE (pp) | Curve EOL MAE (cycles) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Notebook 07 SOH-dependent fade | 1.576 | 2.627 | 8.758 | 0.241 | 0.396 | 23.600 |
| Notebook 08 late-life calibrated | 1.330 | 2.187 | 7.120 | 0.241 | 0.422 | 20.800 |
| Notebook 06 recent-signal Ridge | 1.415 | 2.212 | 7.372 | 0.241 | 0.438 | 19.600 |
| Notebook 06 equal-weight average | 1.349 | 2.141 | 7.238 | 0.241 | 0.428 | 20.133 |
| Charge summary | 1.428 | 2.243 | 7.372 | 0.241 | 0.446 | 20.200 |
| Charge summary + charge curve | 1.485 | 2.343 | 7.502 | 0.241 | 0.459 | 22.133 |
| Charge summary + charge and discharge curves | 1.537 | 2.553 | 9.421 | 0.241 | 0.459 | 23.467 |

## Dashboard decision

Keep **Notebook 08 late-life calibrated** as the existing 3C dashboard model.

Candidate approval requires complete coverage, lower direct RUL MAE than the equal-weight average, and lower full-curve and last-20 SOH MAE than Notebook 08. The +10 and +50 SOH errors may rise by at most 0.05 pp relative to the Notebook 07 SOH-dependent curve.

All reported SOH MAEs weight cells equally. The per-cell table includes errors at the observed EOL. This is a within-cohort comparison on the same XJTU cells used for prior development.
