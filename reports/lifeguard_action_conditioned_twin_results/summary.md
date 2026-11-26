# XJTU action-conditioned twin validation

This report evaluates constant-rate forecasts on held-out batteries. Each start uses measured SOH and ten cycles of past SOH through the completed anchor cycle. Subsequent rollout steps use predicted SOH. The rows summarize errors on the recorded protocol. MAE gives each battery equal weight.

The raw audit found **0 sustained same-battery 2C↔3C switches** in the 23-battery cohort. A switch needs two adjacent classified cycles on each side. The action overlap table describes where both rates have training observations. Actual switching effects require independent evidence.

## Raw data coverage

| Rate | Batteries | Verified EOL | Rate classified as expected | Valid discharge energy | Median charge-to-cutoff, min |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2C | 8 | 7 | 3211/3211 | 3210/3211 | 42.5 |
| 3C | 15 | 15 | 3727/3727 | 3727/3727 | 33.8 |

## Held-out forecast errors

Each entry is **MAE / worst absolute error (scored/eligible)**. SOH uses percentage points. Cumulative energy uses Wh from the cycle after the anchor through the target. Its forecast stops accumulating after predicted EOL. EOL error is in cycles. SOH holds at 80% after predicted EOL. A missing energy measurement invalidates cumulative energy targets that include it.

### SOH

| Rate | Anchor | Window | Persistence | Notebook 07 | Ridge |
| --- | ---: | --- | ---: | ---: | ---: |
| 2C | 50 | 1 | 0.025 / 0.050 (8/8) | 0.025 / 0.044 (8/8) | 0.024 / 0.040 (8/8) |
| 2C | 50 | 10 | 0.150 / 0.200 (8/8) | 0.245 / 0.352 (8/8) | 0.286 / 0.355 (8/8) |
| 2C | 50 | 50 | 0.444 / 0.900 (8/8) | 0.373 / 0.765 (8/8) | 0.818 / 1.134 (8/8) |
| 2C | 50 | last20 | 16.766 / 18.900 (140/140) | 1.508 / 3.400 (140/140) | 1.305 / 3.400 (140/140) |
| 2C | 100 | 1 | 0.062 / 0.100 (8/8) | 0.048 / 0.085 (8/8) | 0.038 / 0.079 (8/8) |
| 2C | 100 | 10 | 0.031 / 0.050 (8/8) | 0.134 / 0.210 (8/8) | 0.268 / 0.353 (8/8) |
| 2C | 100 | 50 | 0.544 / 0.800 (8/8) | 0.423 / 0.869 (8/8) | 1.018 / 1.288 (8/8) |
| 2C | 100 | last20 | 16.309 / 18.500 (140/140) | 1.120 / 3.400 (140/140) | 1.221 / 3.400 (140/140) |
| 3C | 50 | 1 | 0.060 / 0.200 (15/15) | 0.076 / 0.219 (15/15) | 0.061 / 0.202 (15/15) |
| 3C | 50 | 10 | 0.160 / 0.500 (15/15) | 0.158 / 0.392 (15/15) | 0.102 / 0.300 (15/15) |
| 3C | 50 | 50 | 1.637 / 4.750 (15/15) | 0.648 / 2.343 (15/15) | 0.781 / 1.645 (15/15) |
| 3C | 50 | last20 | 14.337 / 19.450 (300/300) | 3.614 / 12.903 (300/300) | 7.818 / 19.450 (300/300) |
| 3C | 100 | 1 | 0.063 / 0.200 (15/15) | 0.040 / 0.137 (15/15) | 0.049 / 0.137 (15/15) |
| 3C | 100 | 10 | 0.707 / 2.300 (15/15) | 0.220 / 0.810 (15/15) | 0.280 / 0.474 (15/15) |
| 3C | 100 | 50 | 2.615 / 8.350 (13/13) | 0.454 / 2.791 (13/13) | 4.525 / 7.287 (13/13) |
| 3C | 100 | last20 | 12.700 / 18.250 (300/300) | 2.558 / 7.995 (300/300) | 2.150 / 6.700 (300/300) |

### Cumulative energy (Wh)

| Rate | Anchor | Window | Persistence | Notebook 07 | Ridge |
| --- | ---: | --- | ---: | ---: | ---: |
| 2C | 50 | 1 | 0.016 / 0.022 (8/8) | 0.016 / 0.023 (8/8) | 0.016 / 0.023 (8/8) |
| 2C | 50 | 10 | 0.184 / 0.255 (8/8) | 0.226 / 0.313 (8/8) | 0.235 / 0.317 (8/8) |
| 2C | 50 | 50 | 0.581 / 1.580 (8/8) | 1.587 / 2.167 (8/8) | 2.414 / 2.983 (8/8) |
| 2C | 100 | 1 | 0.010 / 0.018 (8/8) | 0.009 / 0.017 (8/8) | 0.008 / 0.016 (8/8) |
| 2C | 100 | 10 | 0.037 / 0.088 (8/8) | 0.052 / 0.120 (8/8) | 0.098 / 0.169 (8/8) |
| 2C | 100 | 50 | 0.856 / 1.433 (8/8) | 0.974 / 1.618 (8/8) | 2.392 / 2.859 (8/8) |
| 3C | 50 | 1 | 0.011 / 0.032 (15/15) | 0.012 / 0.033 (15/15) | 0.011 / 0.032 (15/15) |
| 3C | 50 | 10 | 0.101 / 0.207 (15/15) | 0.108 / 0.234 (15/15) | 0.093 / 0.200 (15/15) |
| 3C | 50 | 50 | 2.366 / 6.852 (15/15) | 1.228 / 2.664 (15/15) | 1.273 / 3.187 (15/15) |
| 3C | 100 | 1 | 0.006 / 0.023 (15/15) | 0.008 / 0.034 (15/15) | 0.010 / 0.039 (15/15) |
| 3C | 100 | 10 | 0.236 / 0.548 (15/15) | 0.064 / 0.193 (15/15) | 0.156 / 0.353 (15/15) |
| 3C | 100 | 50 | 4.611 / 12.559 (13/13) | 0.759 / 3.253 (13/13) | 6.080 / 9.378 (13/13) |

### EOL (cycles)

| Rate | Anchor | Window | Persistence | Notebook 07 | Ridge |
| --- | ---: | --- | ---: | ---: | ---: |
| 2C | 50 | eol | — (0/7) | 42.43 / 95.00 (7/7) | 53.86 / 91.00 (7/7) |
| 2C | 100 | eol | — (0/7) | 28.86 / 58.00 (7/7) | 27.00 / 53.00 (7/7) |
| 3C | 50 | eol | — (0/15) | 35.60 / 93.00 (15/15) | 43.56 / 148.00 (9/15) |
| 3C | 100 | eol | — (0/15) | 23.53 / 70.00 (15/15) | 79.47 / 154.00 (15/15) |

### Largest Ridge errors at cycle 50 or 100 starts

| Metric | Worst error | Cell | Anchor | Target or observed EOL cycle |
| --- | ---: | --- | ---: | ---: |
| soh_pp | 19.450 | XJTU_3C_battery-2 | 50 | 291 |
| cumulative_wh | 9.378 | XJTU_3C_battery-4 | 100 | 150 |
| eol_cycles | 154.000 | XJTU_3C_battery-4 | 100 | 321 |

## Validation outcome

- Ridge improved SOH MAE over Notebook 07 in **1/8** paired 10- and 50-cycle groups.
- The improved groups were 3C at 50 +10.
- Folds share training support for both rates in these two-point SOH bins: 80–82%, 82–84%, 84–86%, 86–88%, 88–90%, 90–92%, 92–94%, 94–96%, 96–98%, 98–100%.
- EOL errors use verified events and report prediction coverage. Right-censored batteries contribute only their available SOH and energy labels.
- The validation applies to fixed rates on the observed protocols. The switch audit records candidate events separately from fixed-rate scoring.
- rolling_reference.csv gives the Notebook 11 comparison on aligned targets with its own information at the origin. The rolling estimates did not enter fitting or selection.
