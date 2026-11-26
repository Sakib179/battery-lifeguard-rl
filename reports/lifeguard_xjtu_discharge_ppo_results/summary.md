# XJTU discharge PPO pilot

## Conclusion

**PPO fell short of the retention criteria in this simulation.** PPO trained on the validated Random Walk SOH transition model, with a separate delivered-Wh model. The benchmark compares the change in reference-test SOH at a shared energy budget.

Evaluation used 133 starts on 8 held-out batteries. The support checks excluded 16 additional starts. Each evaluated start used 8 shared disturbance paths and PPO used 3 seeds per battery fold.

## Policy comparison over three reference-test intervals

| Policy | Mean SOH loss (pp) | Worst SOH loss (pp) | Mean energy (Wh) | Budget hit rate | Support stops |
| --- | ---: | ---: | ---: | ---: | ---: |
| Fixed middle template | 1.984 | 10.480 | 189.77 | 99.6% | 0.4% |
| SOH rule | 1.988 | 10.587 | 189.76 | 99.6% | 0.4% |
| Constrained lookahead | 1.755 | 10.480 | 190.25 | 99.6% | 0.4% |
| PPO | 1.985 | 10.698 | 189.79 | 99.6% | 0.4% |

Mean outcomes give each held-out battery equal weight. A positive SOH loss means lower capacity at the endpoint. A support stop ended a trajectory early and counted as a budget miss.

The PPO-minus-lookahead SOH loss difference was **+0.231 pp** (95% interval +0.202 to +0.257). The budget hit rate difference was +0.00 percentage points (95% interval +0.00 to +0.00). A paired bootstrap resampled batteries with the fitted policies and disturbances held fixed.

## Recorded-trajectory forecast check

| Tests ahead | Target | Windows | Mean absolute error | Max error |
| --- | --- | ---: | ---: | ---: |
| 1 | SOH (percentage points) | 165 | 0.196 | 0.757 |
| 1 | Delivered energy (Wh) | 165 | 0.436 | 1.865 |
| 3 | SOH (percentage points) | 149 | 0.626 | 2.948 |
| 3 | Delivered energy (Wh) | 149 | 1.258 | 4.186 |

The SOH forecasts reproduce Notebook 19. This check feeds back predicted SOH after the initial state and uses the recorded first-plateau schedules. The Wh model is fit and evaluated using separate batteries.

## Scope

Each decision selects a supported ten-cycle template, with one current and duration for the first discharge plateau of each cycle. The fixed baseline repeats the middle-exposure observed template. All policies share the operating-domain check and the 90% energy budget. The remaining pulse profile and delivered energy are represented by the fitted Random Walk transition.

The benchmark is a comparison inside the simulator. It covers modeled reference-test SOH over up to 30 operating cycles. Prospective cycling would be needed to establish an effect on battery lifetime.

[Original XJTU experimental protocols](https://wang-fujin.github.io/) · [Gymnasium environment API](https://gymnasium.farama.org/api/env/)
