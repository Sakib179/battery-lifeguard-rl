# MIT–BIT fixed energy budget controller

## Results

**The fixed-budget controller met both simulation criteria.** Over 15 cycles it delivered 93.1% of fixed 1C's simulated Wh, compared with 86.3% for the moving-target controller. It changed mean charging time by -119.9 minutes (-19.9%) relative to fixed 1C.

The simulation compared all three policies on the same 164 starts across 55 held-out batteries. Each five-cycle action used 1C, 2C, or 3C charging with 3C discharge throughout.

| Policy | Charge time (min) | Delivered energy (Wh) | Energy vs fixed 1C | Budget hits | Fallback blocks |
| --- | ---: | ---: | ---: | ---: | ---: |
| Fixed 1C | 603.7 | 81.85 | 100.0% | 164/164 | 0/492 |
| Moving-target controller | 397.3 | 70.63 | 86.3% | 66/164 | 0/492 |
| Fixed-budget controller | 483.8 | 76.18 | 93.1% | 164/164 | 0/492 |

Charging time and energy give each battery equal weight. Budget hits count individual starts. Fallbacks use the rule defined by each policy.

| Policy | Average shortfall in worst 10% (Wh) | Maximum shortfall (Wh) | Worst start |
| --- | ---: | ---: | --- |
| Fixed 1C | 0.00 | 0.00 | — |
| Moving-target controller | 14.63 | 19.43 | Cell #71 at cycle 11 |
| Fixed-budget controller | 0.00 | 0.00 | — |

## Paired decision criteria

| Criterion | Difference | 95% battery bootstrap interval | Result |
| --- | ---: | ---: | --- |
| Charging time relative to fixed 1C | -119.9 min | -124.2 to -115.2 min | Pass |
| Delivered Wh relative to 90% of fixed 1C | +2.52 Wh | +2.36 to +2.68 Wh | Pass |

The controller fixed the target at 90% of the initial 15-cycle fixed-1C forecast. It replanned after each block and credited the energy delivered before the next decision. Margins used the 90% quantile of overprediction from inner held-out training rollouts. The minimum sequence support was 6 training batteries across all 27 three-block schedules and all five outer folds.

| Remaining blocks | Smallest fold margin (Wh) | Largest fold margin (Wh) |
| ---: | ---: | ---: |
| 1 | 0.68 | 0.72 |
| 2 | 1.28 | 1.41 |
| 3 | 2.11 | 2.41 |

## Measured randomized replay

Replay considered 819 eligible starting points across 55 batteries. At each exact match, the next decision received the measured outcome. A full match requires the recorded action to agree with the policy at all three steps.

| Policy | Full matches (batteries) | Complete Wh and time (batteries) | Measured time (min) | Measured energy (Wh) | Measured budget hits |
| --- | ---: | ---: | ---: | ---: | ---: |
| Fixed 1C | 21 (19) | 19 (18) | 591.6 | 80.36 | 19/19 |
| Moving-target controller | 46 (28) | 45 (27) | 269.6 | 63.16 | 3/45 |
| Fixed-budget controller | 24 (18) | 24 (18) | 478.2 | 73.30 | 24/24 |

The replay estimates use outcome-specific availability, normalized inverse-propensity weights, and equal battery weight before matching. Each policy has its own set of matching trajectories. These estimates provide a descriptive check on the simulation and have limited support for a policy-effect claim. Planning and scoring within the simulation use the same transition model. The replay uses measured outcomes.

The analysis addresses 15-cycle operation. A supported 30-cycle comparison needs measured sustained 1C trajectories. Battery lifetime requires a separate experiment.

[MIT–BIT v3 dataset and experimental design](https://data.mendeley.com/datasets/kw34hhw7xg/3)
