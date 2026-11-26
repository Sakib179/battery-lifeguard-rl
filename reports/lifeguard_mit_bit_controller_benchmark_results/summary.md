# MIT–BIT charging controller benchmark

## Results

We compared five charging policies across **929 decisions on 55 held-out batteries**. For each five-cycle block, the goal was to deliver at least 90% of the energy measured in the preceding block.

| Policy | Energy target met | Charging time (min per 5 cycles) | Delivered energy (Wh per 5 cycles) | Discharge capacity (Ah)¹ | Matched decisions |
| --- | ---: | ---: | ---: | ---: | ---: |
| Fixed 1C | 100.0% | 186.8 | 25.38 | 1.484 | 294/929 |
| Fixed 2C | 74.4% | 74.5 | 20.14 | 1.185 | 345/929 |
| Fixed 3C | 14.2% | 35.7 | 14.51 | 0.857 | 290/929 |
| Past-observation rule | 76.1% | 94.0 | 19.50 | 1.150 | 296/929 |
| Model-guided | 100.0% | 110.3 | 21.75 | 1.279 | 339/929 |

¹ Weighted average of the median discharge capacity measured within each five-cycle block.

**The model-guided policy qualified for the next simulator experiment.** Compared with fixed 1C, its mean charging time differed by **-76.5 minutes** per block (95% CI -81.3 to -71.5). The energy target hit rate differed by **+0.0 percentage points** (95% CI +0.0 to +0.0). The policy passed the charging-time criterion and passed the energy criterion, which allows a drop of up to 5 percentage points in the hit rate.

Relative to fixed 1C, charging time changed by -40.9% and delivered energy changed by -3.63 Wh per five-cycle block. The reported hit rates use matched decisions with measured delivered energy.

The model-guided policy chose 1C in 363 decisions, 2C in 565, and 3C in 1. It used its fallback in 0 decisions.

## Evaluation details

Eligible blocks start at cycles 11–91 and require a measured previous block. There were 6 missing next-block Wh outcomes overall. Fixed 1C had 3 matched blocks with missing Wh. The model had 4. Bounding these missing outcomes gives a 95% difference interval of -2.5 to +2.3 percentage points.

Replay uses exact action matches, the documented 1/3 assignment probability and normalized weights. Each battery receives equal total weight before matching. Recorded assignment counts for 1C, 2C and 3C were 294, 345, 290. Timing is the sum of five measured charging intervals, available for 929/929 eligible blocks. For 10 cycles with a wall-clock discontinuity, the recorder's elapsed Test_Time supplies the duration. Wh is the sum of five meter-checked discharges. Bootstrap intervals use 2,000 paired battery draws with the fitted policies held fixed.

The benchmark measures a single decision on recorded randomized histories in the same MIT–BIT cohort used in Notebook 15. Evaluating battery lifetime under repeated policy decisions requires a separate experiment.

[MIT–BIT v3 data and experimental design](https://data.mendeley.com/datasets/kw34hhw7xg/3)
