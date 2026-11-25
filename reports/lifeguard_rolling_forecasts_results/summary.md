# XJTU rolling SOH and RUL

Each update uses the current charge and completed discharges through the preceding cycle. MAE weights each battery equally. SOH errors use percentage points and RUL errors use cycles.

Earlier SOH uses the rolling charge-only estimate through ten cycles ahead and the saved fixed forecast at fifty cycles. The earlier RUL reference for cycles 50–95 uses the cycle-50 Notebook 06 timing model. The right-censored battery contributes to SOH but has no verified RUL label.

## Updates at cycles 50–95

### SOH

| Rate | Horizon | Paired points | Coverage | Earlier MAE | Selected MAE | Earlier max | Selected max | Worst selected at |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 2C | 0 | 80 | 100.0% | 0.082 | 0.031 | 0.265 | 0.120 | XJTU_2C_battery-8 at 60 |
| 2C | 1 | 80 | 100.0% | 0.089 | 0.043 | 0.422 | 0.209 | XJTU_2C_battery-7 at 80 |
| 2C | 10 | 80 | 100.0% | 0.125 | 0.056 | 0.313 | 0.235 | XJTU_2C_battery-7 at 55 |
| 2C | 50 | 80 | 100.0% | 0.835 | 0.154 | 2.756 | 0.530 | XJTU_2C_battery-7 at 50 |
| 3C | 0 | 150 | 100.0% | 0.090 | 0.041 | 0.506 | 0.219 | XJTU_3C_battery-7 at 75 |
| 3C | 1 | 150 | 100.0% | 0.108 | 0.054 | 0.506 | 0.283 | XJTU_3C_battery-7 at 75 |
| 3C | 10 | 150 | 100.0% | 0.168 | 0.119 | 0.859 | 0.439 | XJTU_3C_battery-11 at 95 |
| 3C | 50 | 147 | 100.0% | 1.163 | 0.710 | 9.564 | 3.774 | XJTU_3C_battery-15 at 90 |

### RUL

| Rate | Actual cycles left | Paired points | Coverage | Earlier MAE | Selected MAE | Earlier max | Selected max | Worst selected at |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 2C | all | 70 | 100.0% | 9.000 | 6.995 | 17.000 | 13.439 | XJTU_2C_battery-1 at 55 |
| 2C | 1–20 | 0 | — | — | — | — | — | — |
| 2C | >50 | 70 | 100.0% | 9.000 | 6.995 | 17.000 | 13.439 | XJTU_2C_battery-1 at 55 |
| 3C | all | 150 | 100.0% | 20.449 | 13.464 | 56.985 | 32.419 | XJTU_3C_battery-9 at 50 |
| 3C | 1–20 | 0 | — | — | — | — | — | — |
| 3C | 21–50 | 4 | 100.0% | 16.260 | 1.860 | 16.260 | 2.196 | XJTU_3C_battery-11 at 95 |
| 3C | >50 | 146 | 100.0% | 20.449 | 13.451 | 56.985 | 32.419 | XJTU_3C_battery-9 at 50 |

## All updates from cycle 50

### SOH

| Rate | Horizon | Paired points | Coverage | Earlier MAE | Selected MAE | Earlier max | Selected max | Worst selected at |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 2C | 0 | 564 | 99.8% | 0.111 | 0.045 | 0.405 | 0.307 | XJTU_2C_battery-5 at 360 |
| 2C | 1 | 564 | 99.8% | 0.089 | 0.064 | 0.517 | 0.446 | XJTU_2C_battery-7 at 285 |
| 2C | 10 | 550 | 99.8% | 0.186 | 0.176 | 1.599 | 1.599 | XJTU_2C_battery-2 at 380 |
| 2C | 50 | 487 | 100.0% | 1.037 | 0.319 | 4.463 | 2.486 | XJTU_2C_battery-8 at 310 |
| 3C | 0 | 603 | 100.0% | 0.185 | 0.044 | 4.543 | 0.290 | XJTU_3C_battery-7 at 115 |
| 3C | 1 | 603 | 100.0% | 0.210 | 0.072 | 4.643 | 0.430 | XJTU_3C_battery-7 at 115 |
| 3C | 10 | 576 | 100.0% | 0.418 | 0.182 | 5.343 | 1.436 | XJTU_3C_battery-3 at 255 |
| 3C | 50 | 456 | 100.0% | 1.858 | 0.928 | 9.564 | 4.425 | XJTU_3C_battery-3 at 200 |

### RUL

| Rate | Actual cycles left | Paired points | Coverage | Earlier MAE | Selected MAE | Earlier max | Selected max | Worst selected at |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 2C | all | 495 | 99.8% | 8.179 | 7.357 | 17.000 | 14.915 | XJTU_2C_battery-3 at 100 |
| 2C | 1–20 | 27 | 96.4% | 5.259 | 4.918 | 16.795 | 14.175 | XJTU_2C_battery-1 at 385 |
| 2C | 21–50 | 42 | 100.0% | 4.944 | 5.187 | 14.868 | 12.249 | XJTU_2C_battery-1 at 365 |
| 2C | >50 | 426 | 100.0% | 8.679 | 7.718 | 17.000 | 14.915 | XJTU_2C_battery-3 at 100 |
| 3C | all | 603 | 100.0% | 15.067 | 12.644 | 56.985 | 37.615 | XJTU_3C_battery-9 at 100 |
| 3C | 1–20 | 60 | 100.0% | 3.907 | 2.391 | 15.305 | 8.848 | XJTU_3C_battery-3 at 265 |
| 3C | 21–50 | 90 | 100.0% | 9.303 | 6.832 | 24.823 | 20.463 | XJTU_3C_battery-8 at 220 |
| 3C | >50 | 453 | 100.0% | 17.718 | 15.059 | 56.985 | 37.615 | XJTU_3C_battery-9 at 100 |

## All updates from cycle 100

### SOH

| Rate | Horizon | Paired points | Coverage | Earlier MAE | Selected MAE | Earlier max | Selected max | Worst selected at |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 2C | 0 | 484 | 99.8% | 0.116 | 0.047 | 0.405 | 0.307 | XJTU_2C_battery-5 at 360 |
| 2C | 1 | 484 | 99.8% | 0.089 | 0.067 | 0.517 | 0.446 | XJTU_2C_battery-7 at 285 |
| 2C | 10 | 470 | 99.8% | 0.197 | 0.197 | 1.599 | 1.599 | XJTU_2C_battery-2 at 380 |
| 2C | 50 | 407 | 100.0% | 1.075 | 0.352 | 4.463 | 2.486 | XJTU_2C_battery-8 at 310 |
| 3C | 0 | 453 | 100.0% | 0.229 | 0.049 | 4.543 | 0.290 | XJTU_3C_battery-7 at 115 |
| 3C | 1 | 453 | 100.0% | 0.262 | 0.089 | 4.643 | 0.430 | XJTU_3C_battery-7 at 115 |
| 3C | 10 | 426 | 100.0% | 0.596 | 0.220 | 5.343 | 1.436 | XJTU_3C_battery-3 at 255 |
| 3C | 50 | 309 | 100.0% | 1.821 | 1.024 | 9.123 | 4.425 | XJTU_3C_battery-3 at 200 |

### RUL

| Rate | Actual cycles left | Paired points | Coverage | Earlier MAE | Selected MAE | Earlier max | Selected max | Worst selected at |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 2C | all | 425 | 99.8% | 8.045 | 7.404 | 17.000 | 14.915 | XJTU_2C_battery-3 at 100 |
| 2C | 1–20 | 27 | 96.4% | 5.259 | 4.918 | 16.795 | 14.175 | XJTU_2C_battery-1 at 385 |
| 2C | 21–50 | 42 | 100.0% | 4.944 | 5.187 | 14.868 | 12.249 | XJTU_2C_battery-1 at 365 |
| 2C | >50 | 356 | 100.0% | 8.616 | 7.841 | 17.000 | 14.915 | XJTU_2C_battery-3 at 100 |
| 3C | all | 453 | 100.0% | 13.051 | 12.187 | 37.615 | 37.615 | XJTU_3C_battery-9 at 100 |
| 3C | 1–20 | 60 | 100.0% | 3.907 | 2.391 | 15.305 | 8.848 | XJTU_3C_battery-3 at 265 |
| 3C | 21–50 | 86 | 100.0% | 8.894 | 7.156 | 24.823 | 20.463 | XJTU_3C_battery-8 at 220 |
| 3C | >50 | 307 | 100.0% | 16.818 | 16.666 | 37.615 | 37.615 | XJTU_3C_battery-9 at 100 |

SOH worst-error cycles refer to the origin of the forecast. Add the horizon to get the target cycle.
RUL windows use verified observed EOL. The cycle-100 forecast model also exports current SOH at cycle 100.
The early model settings were selected on this XJTU cohort. Performance on additional batteries is unverified.
