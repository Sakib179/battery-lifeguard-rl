# MIT–BIT charging-rate switch replay

MIT–BIT v3, DOI 10.17632/kw34hhw7xg.3. Run mode benchmark. Read 55 of 55 requested randomized workbooks. The 55-cell publisher cohort is the coverage reference.

The aging workbooks start with a discharge-only boundary at raw cycle 1. The block clock starts at raw cycle 2. Operational SOH normalizes median block capacity to the median of the first five complete aging discharges. It describes capacity available under the recorded 3C discharge. The effect of a switch on this measurement can include short-term changes in available capacity.

The audit found 5,555 raw cycles, 1,045 verified complete blocks and 5,493 meter-checked cycle energy estimates.

## Held-out forecast errors

Five battery-level folds evaluated 55 cells. Tuning and model choice used only the training cells of each fold. The earlier block provides the measured initial condition. Each row reports cell-weighted mean absolute error (MAE) and maximum absolute error. Bias is forecast minus measured.

| Recorded transition | Target | Model | MAE | Max | Bias | Scored / eligible | Worst cell / start |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| all | SOH pp | Persistence | 18.697 | 77.290 | +2.809 | 935/990 | #77 / 11 |
| all | SOH pp | Rate-only Ridge | 9.110 | 63.587 | +0.021 | 935/990 | #77 / 26 |
| all | SOH pp | History-aware Ridge | 3.790 | 40.847 | +0.026 | 935/990 | #77 / 26 |
| all | SOH pp | Fold-selected | 3.790 | 40.847 | +0.026 | 935/990 | #77 / 26 |
| all | Wh | Persistence | 5.142 | 13.971 | +0.755 | 923/990 | #77 / 11 |
| all | Wh | Rate-only Ridge | 2.696 | 11.507 | +0.006 | 923/990 | #77 / 91 |
| all | Wh | History-aware Ridge | 2.294 | 13.352 | +0.016 | 923/990 | #77 / 56 |
| all | Wh | Fold-selected | 2.294 | 13.352 | +0.016 | 923/990 | #77 / 56 |
| 2-to-3 | SOH pp | Persistence | 24.625 | 42.398 | +24.625 | 98/100 | #77 / 36 |
| 2-to-3 | SOH pp | Rate-only Ridge | 6.026 | 13.744 | -0.052 | 98/100 | #4 / 11 |
| 2-to-3 | SOH pp | History-aware Ridge | 3.873 | 19.251 | -0.497 | 98/100 | #77 / 36 |
| 2-to-3 | SOH pp | Fold-selected | 3.873 | 19.251 | -0.497 | 98/100 | #77 / 36 |
| 2-to-3 | Wh | Persistence | 6.675 | 8.250 | +6.675 | 96/100 | #75 / 31 |
| 2-to-3 | Wh | Rate-only Ridge | 3.086 | 8.995 | -0.735 | 96/100 | #9 / 16 |
| 2-to-3 | Wh | History-aware Ridge | 2.659 | 9.768 | -0.595 | 96/100 | #77 / 36 |
| 2-to-3 | Wh | Fold-selected | 2.659 | 9.768 | -0.595 | 96/100 | #77 / 36 |
| 3-to-2 | SOH pp | Persistence | 15.959 | 29.463 | -15.959 | 122/125 | #65 / 76 |
| 3-to-2 | SOH pp | Rate-only Ridge | 8.522 | 34.989 | -8.169 | 122/125 | #76 / 16 |
| 3-to-2 | SOH pp | History-aware Ridge | 3.006 | 11.282 | +0.630 | 122/125 | #65 / 76 |
| 3-to-2 | SOH pp | Fold-selected | 3.006 | 11.282 | +0.630 | 122/125 | #65 / 76 |
| 3-to-2 | Wh | Persistence | 4.336 | 6.398 | -4.336 | 122/125 | #65 / 76 |
| 3-to-2 | Wh | Rate-only Ridge | 2.533 | 7.236 | -1.622 | 122/125 | #61 / 11 |
| 3-to-2 | Wh | History-aware Ridge | 2.020 | 7.315 | -0.013 | 122/125 | #77 / 76 |
| 3-to-2 | Wh | Fold-selected | 2.020 | 7.315 | -0.013 | 122/125 | #77 / 76 |
| same-rate | SOH pp | Persistence | 2.984 | 11.459 | +2.509 | 297/325 | #56 / 21 |
| same-rate | SOH pp | Rate-only Ridge | 7.285 | 18.904 | +1.685 | 297/325 | #55 / 21 |
| same-rate | SOH pp | History-aware Ridge | 1.883 | 9.932 | +0.310 | 297/325 | #77 / 46 |
| same-rate | SOH pp | Fold-selected | 1.883 | 9.932 | +0.310 | 297/325 | #77 / 46 |
| same-rate | Wh | Persistence | 0.844 | 2.872 | +0.720 | 291/325 | #56 / 21 |
| same-rate | Wh | Rate-only Ridge | 2.546 | 9.117 | +0.538 | 291/325 | #77 / 86 |
| same-rate | Wh | History-aware Ridge | 2.221 | 10.734 | +0.241 | 291/325 | #77 / 51 |
| same-rate | Wh | Fold-selected | 2.221 | 10.734 | +0.241 | 291/325 | #77 / 51 |
| other-switch | SOH pp | Persistence | 29.060 | 77.290 | +3.249 | 418/440 | #77 / 11 |
| other-switch | SOH pp | Rate-only Ridge | 11.253 | 63.587 | +1.230 | 418/440 | #77 / 26 |
| other-switch | SOH pp | History-aware Ridge | 5.094 | 40.847 | -0.355 | 418/440 | #77 / 26 |
| other-switch | SOH pp | Fold-selected | 5.094 | 40.847 | -0.355 | 418/440 | #77 / 26 |
| other-switch | Wh | Persistence | 8.027 | 13.971 | +0.872 | 414/440 | #77 / 11 |
| other-switch | Wh | Rate-only Ridge | 2.854 | 11.507 | +0.405 | 414/440 | #77 / 91 |
| other-switch | Wh | History-aware Ridge | 2.358 | 13.352 | +0.096 | 414/440 | #77 / 56 |
| other-switch | Wh | Fold-selected | 2.358 | 13.352 | +0.096 | 414/440 | #77 / 56 |

## History effect and examples

- 2-to-3, SOH history-aware MAE changed by -2.153 pp relative to rate-only Ridge.
- 2-to-3, WH history-aware MAE changed by -0.427 Wh relative to rate-only Ridge.
- 3-to-2, SOH history-aware MAE changed by -5.516 pp relative to rate-only Ridge.
- 3-to-2, WH history-aware MAE changed by -0.513 Wh relative to rate-only Ridge.

The replay includes an example nearest the median held-out SOH error and the largest SOH error for each switch direction. It displays forecasts under the recorded action sequence. Controller benefits and alternative charge schedules require separate evaluation.
