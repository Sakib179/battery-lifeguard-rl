# XJTU fixed-anchor SOH forecast comparison

All errors are SOH percentage points. Each error column compares the saved dashboard forecast, the previous exploratory method, and the revision, in that order.

| Anchor | Charge rate | SOH input | Whole-curve MAE | Whole-curve max | Last 20 MAE | Last 20 max |
|---:|---|---|---:|---:|---:|---:|
| 50 | 2C | Charge-based | 2.537 → 0.603 → 0.603 | 9.758 → 4.260 → 4.185 | 1.411 → 0.719 → 0.724 | 3.400 → 2.507 → 2.399 |
| 50 | 2C | Measured | 2.308 → 0.564 → 0.563 | 9.500 → 4.243 → 4.168 | 1.508 → 0.719 → 0.725 | 3.400 → 2.503 → 2.394 |
| 50 | 3C | Charge-based | 1.754 → 1.482 → 1.488 | 11.450 → 8.561 → 8.071 | 3.154 → 1.675 → 1.664 | 9.564 → 5.804 → 5.730 |
| 50 | 3C | Measured | 1.895 → 1.497 → 1.495 | 12.903 → 8.664 → 8.142 | 3.614 → 1.764 → 1.756 | 12.903 → 5.837 → 5.763 |
| 100 | 2C | Charge-based | 0.964 → 0.589 → 0.576 | 4.487 → 4.031 → 4.031 | 0.743 → 0.696 → 0.696 | 3.067 → 2.316 → 2.316 |
| 100 | 2C | Measured | 1.703 → 0.567 → 0.567 | 7.650 → 4.277 → 4.277 | 1.120 → 0.708 → 0.708 | 3.400 → 2.411 → 2.411 |
| 100 | 3C | Charge-based | 1.330 → 1.219 → 1.141 | 9.123 → 6.468 → 6.405 | 2.187 → 1.509 → 1.422 | 7.120 → 4.745 → 4.655 |
| 100 | 3C | Measured | 1.539 → 1.194 → 1.124 | 9.700 → 6.519 → 6.427 | 2.558 → 1.508 → 1.429 | 7.995 → 4.636 → 4.584 |

## Revised forecast diagnostics

| Anchor | Charge rate | SOH input | Whole-curve max at | Last 20 max at | +10 MAE (n) | +50 MAE (n) |
|---:|---|---|---|---|---:|---:|
| 50 | 2C | Charge-based | XJTU_2C_battery-8 / 372 | XJTU_2C_battery-8 / 399 | 0.310 (8) | 0.380 (8) |
| 50 | 2C | Measured | XJTU_2C_battery-8 / 372 | XJTU_2C_battery-8 / 399 | 0.245 (8) | 0.323 (8) |
| 50 | 3C | Charge-based | XJTU_3C_battery-9 / 211 | XJTU_3C_battery-11 / 130 | 0.198 (15) | 0.509 (15) |
| 50 | 3C | Measured | XJTU_3C_battery-9 / 209 | XJTU_3C_battery-11 / 130 | 0.158 (15) | 0.580 (15) |
| 100 | 2C | Charge-based | XJTU_2C_battery-8 / 375 | XJTU_2C_battery-3 / 392 | 0.192 (8) | 0.322 (8) |
| 100 | 2C | Measured | XJTU_2C_battery-8 / 373 | XJTU_2C_battery-8 / 399 | 0.134 (8) | 0.265 (8) |
| 100 | 3C | Charge-based | XJTU_3C_battery-9 / 237 | XJTU_3C_battery-14 / 146 | 0.241 (15) | 0.311 (13) |
| 100 | 3C | Measured | XJTU_3C_battery-9 / 237 | XJTU_3C_battery-14 / 146 | 0.220 (15) | 0.368 (13) |

The whole-curve metric weights each battery equally. The last 20 metric covers the 20 cycles ending at verified EOL. The right-censored cell contributes its available whole-curve and horizon data. Each horizon lists the number of cells with that exact cycle.

The revised model's projected RUL is the offset to its first 80% SOH crossing on the full forecast grid. The crossing can occur after the last measured cycle. The rollout starts CSV records the projected EOL and RUL for each battery, anchor, and SOH input.

The dashboard comparison uses notebook 07 SOH-dependent fade, plus notebook 08 late-life calibration for Charge-based SOH at cycle 100. All models are evaluated on the same cells and cycles within each row. The revision was selected on this XJTU cohort. Its benefit on additional batteries still needs validation.
