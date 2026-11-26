# MIT–BIT multi-block battery simulator

## Results

**The model-guided controller fell short of the advancement criteria.** Across all 164 paired starts, the 30-cycle simulation estimated 824.5 minutes of charging and 139.4 Wh delivered for the model-guided policy. Fixed 1C used 1217.9 minutes and delivered 164.2 Wh. The model-guided policy retained 84.9% of fixed 1C's simulated energy.

## Accuracy under recorded charge rates

Each rollout begins with measured history and feeds its own predictions back into the next step. The baseline reuses the last measurement for the requested rate, with training medians where history is missing. The reported intervals use paired battery resampling. The MAE difference is simulator minus baseline.

| Cohort | Cycles | Outcome | Batteries | Windows | Baseline MAE | Simulator MAE | Worst-decile MAE | Max error | 95% CI for MAE difference |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Randomized | 5 | Cumulative delivered energy (Wh) | 55 | 923 | 2.27 | 0.47 | 1.50 | 3.45 | -1.98 to -1.61 |
| Randomized | 5 | Cumulative charging time (min) | 55 | 923 | 9.3 | 2.7 | 10.8 | 24.4 | -7.3 to -6.0 |
| Randomized | 5 | Final block capacity (Ah) | 55 | 923 | 0.128 | 0.027 | 0.086 | 0.187 | -0.112 to -0.090 |
| Randomized | 15 | Cumulative delivered energy (Wh) | 55 | 801 | 7.70 | 1.41 | 3.95 | 6.91 | -7.01 to -5.55 |
| Randomized | 15 | Cumulative charging time (min) | 55 | 801 | 31.4 | 7.8 | 26.8 | 80.5 | -26.2 to -20.9 |
| Randomized | 15 | Final block capacity (Ah) | 55 | 801 | 0.190 | 0.037 | 0.099 | 0.188 | -0.172 to -0.135 |
| Randomized | 30 | Cumulative delivered energy (Wh) | 55 | 627 | 20.02 | 3.51 | 8.99 | 14.97 | -18.70 to -14.45 |
| Randomized | 30 | Cumulative charging time (min) | 55 | 627 | 76.1 | 17.7 | 51.7 | 101.0 | -65.3 to -51.6 |
| Randomized | 30 | Final block capacity (Ah) | 55 | 627 | 0.273 | 0.053 | 0.132 | 0.205 | -0.244 to -0.196 |

## Sustained fixed-rate stress test

Audited 22 fixed-profile battery folders. Workbook outcomes were 14 other discharge rate, 5 missing aging workbook, 3 included. The fixed cohort uses only verified 3C discharge. Its model was fitted using randomized batteries.

| Charge rate | Cycles | Outcome | Batteries | Windows | Baseline MAE | Simulator MAE | Worst-decile MAE | Max error | 95% CI for MAE difference |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2C | 5 | Cumulative delivered energy (Wh) | 2 | 34 | 0.95 | 0.29 | 0.66 | 0.68 | -0.75 to -0.57 |
| 2C | 5 | Cumulative charging time (min) | 2 | 34 | 3.4 | 2.0 | 4.7 | 5.5 | -1.7 to -1.0 |
| 2C | 5 | Final block capacity (Ah) | 2 | 34 | 0.054 | 0.016 | 0.039 | 0.041 | -0.043 to -0.033 |
| 3C | 5 | Cumulative delivered energy (Wh) | 1 | 17 | 1.00 | 0.86 | 1.10 | 1.11 | — (1 battery) |
| 3C | 5 | Cumulative charging time (min) | 1 | 17 | 2.4 | 2.1 | 4.4 | 4.4 | — (1 battery) |
| 3C | 5 | Final block capacity (Ah) | 1 | 17 | 0.057 | 0.047 | 0.060 | 0.060 | — (1 battery) |
| 2C | 15 | Cumulative delivered energy (Wh) | 2 | 30 | 5.86 | 1.54 | 3.67 | 3.76 | -4.77 to -3.88 |
| 2C | 15 | Cumulative charging time (min) | 2 | 30 | 21.0 | 7.1 | 14.7 | 15.7 | -16.5 to -11.3 |
| 2C | 15 | Final block capacity (Ah) | 2 | 30 | 0.165 | 0.042 | 0.099 | 0.102 | -0.133 to -0.112 |
| 3C | 15 | Cumulative delivered energy (Wh) | 1 | 15 | 6.02 | 4.54 | 5.39 | 5.41 | — (1 battery) |
| 3C | 15 | Cumulative charging time (min) | 1 | 15 | 14.7 | 8.7 | 15.3 | 15.5 | — (1 battery) |
| 3C | 15 | Final block capacity (Ah) | 1 | 15 | 0.165 | 0.121 | 0.140 | 0.142 | — (1 battery) |
| 2C | 30 | Cumulative delivered energy (Wh) | 2 | 24 | 21.46 | 5.09 | 11.31 | 11.57 | -17.47 to -15.28 |
| 2C | 30 | Cumulative charging time (min) | 2 | 24 | 77.0 | 20.0 | 31.0 | 32.5 | -65.1 to -48.8 |
| 2C | 30 | Final block capacity (Ah) | 2 | 24 | 0.335 | 0.075 | 0.164 | 0.169 | -0.272 to -0.248 |
| 3C | 30 | Cumulative delivered energy (Wh) | 1 | 12 | 21.38 | 13.10 | 14.97 | 15.02 | — (1 battery) |
| 3C | 30 | Cumulative charging time (min) | 1 | 12 | 52.3 | 23.8 | 34.7 | 35.2 | — (1 battery) |
| 3C | 30 | Final block capacity (Ah) | 1 | 12 | 0.314 | 0.184 | 0.201 | 0.202 | — (1 battery) |

## Five-policy simulation over 30 cycles

All policies start from identical measured histories at cycles 11, 41, or 66. The counts in the last three columns use whole simulated blocks. The initial target is 90% of the measured energy immediately before the rollout. The moving target is 90% of the preceding predicted block.

| Policy | Charging time (min) | Delivered energy (Wh) | Energy vs fixed 1C | Blocks below initial target | Blocks below moving target | Starts passing sequence checks |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Fixed 1C | 1217.9 | 164.2 | 100.0% | 0/984 | 0/984 | 0/164 |
| Fixed 2C | 424.8 | 114.7 | 69.8% | 625/984 | 65/984 | 164/164 |
| Fixed 3C | 191.9 | 76.7 | 46.7% | 957/984 | 266/984 | 0/164 |
| Past-observation rule | 585.4 | 112.4 | 68.4% | 574/984 | 175/984 | 32/164 |
| Model-guided | 824.5 | 139.4 | 84.9% | 173/984 | 0/984 | 87/164 |

The model-guided policy fell below the moving target in 0 of 984 blocks and below the initial target in 173 blocks.

## Advancement checks

| Cycles | Simulator accuracy | Supported model / fixed 1C starts | Charging-time criterion | Cumulative energy criterion | Result |
| ---: | --- | ---: | --- | --- | --- |
| 15 | Pass | 164 | Pass | Fail | Fail |
| 30 | Pass | 0 | Insufficient support | Insufficient support | Fail |

At 15 cycles, on 164 supported starts, simulated energy was 86.3% of fixed 1C. The paired charging-time change was -206.4 minutes (95% CI -231.0 to -181.7). The paired energy margin above the 90% requirement was -3.03 Wh (95% CI -4.42 to -1.69).

Sequence support requires complete measured windows from at least 2 distinct batteries. When support depends on the fixed cohort, the sustained-rate simulator must also match or beat the baseline on all three outcomes. Charging time and cumulative energy use paired 95% bootstrap intervals. The energy threshold is 90% of fixed 1C's Wh.

Policy estimates are simulated and use the same MIT–BIT chemistry and discharge protocol. A battery-level bootstrap quantifies variability across the observed starts with fitted models held fixed. Battery lifetime and irreversible degradation require a separate evaluation.

[MIT–BIT v3 dataset and experimental design](https://data.mendeley.com/datasets/kw34hhw7xg/3)
