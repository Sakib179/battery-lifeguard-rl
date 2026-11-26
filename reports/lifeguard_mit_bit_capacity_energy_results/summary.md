# MIT–BIT charging switches — Capacity and energy forecast

## বাংলা সারাংশ

একই held-out split-এ **55টি ব্যাটারির 990টি ব্লক** forecast করেছি। Ah ও Wh-এর ভুল Notebook 14-এর history-aware model-এর সঙ্গে একই scored row-তে তুলনা করা হয়েছে।

| Rate বদল | মেট্রিক | গড় ভুল | সবচেয়ে ভুল ১০%-এর গড় | সর্বোচ্চ ভুল | Scored / eligible |
| --- | --- | ---: | ---: | ---: | ---: |
| 2-to-3 | Ah | 0.061 → 0.034 | 0.170 → 0.090 | 0.215 → 0.127 | 98/100 |
| 2-to-3 | Wh | 2.659 → 0.605 | 7.309 → 1.611 | 9.768 → 2.259 | 96/100 |
| 3-to-2 | Ah | 0.048 → 0.023 | 0.131 → 0.058 | 0.163 → 0.081 | 122/125 |
| 3-to-2 | Wh | 2.020 → 0.393 | 4.534 → 0.986 | 7.315 → 1.472 | 122/125 |

Benchmark গ্রহণের শর্ত **4/4** তুলনায় পূরণ হয়েছে। #77-এর সাইকেল ৩৬–৪০-এ capacity ভুল 0.198 → 0.059 Ah এবং energy ভুল 9.768 → 1.072 Wh।

এই পরীক্ষা MIT–BIT-এ recorded action-এর পরের পাঁচ সাইকেল নিয়ে। নতুন dataset-এ যাচাই ও controller benchmark পরের ধাপ।

## Held-out metrics

MAE and bias give equal weight to each battery. The worst-decile mean uses the largest ceil(10% × scored blocks) absolute errors. Bias is forecast minus measured. Capacity is the median of five measured discharge capacities. Energy is the sum of five meter-checked discharge energies. The nominal percentage columns use a fixed 2.4 Ah denominator.

| Group | Unit | MAE old → new | Worst-decile mean old → new | Max old → new | New bias | Blocks | New worst location |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| all | Ah | 0.059 → 0.027 | 0.192 → 0.086 | 0.419 → 0.187 | -0.000 | 935 | #77 · 11–15 |
| all | Wh | 2.294 → 0.470 | 6.233 → 1.501 | 13.352 → 3.451 | +0.000 | 923 | #77 · 11–15 |
| 2-to-3 | Ah | 0.061 → 0.034 | 0.170 → 0.090 | 0.215 → 0.127 | -0.002 | 98 | #75 · 31–35 |
| 2-to-3 | Wh | 2.659 → 0.605 | 7.309 → 1.611 | 9.768 → 2.259 | -0.039 | 96 | #9 · 16–20 |
| 3-to-2 | Ah | 0.048 → 0.023 | 0.131 → 0.058 | 0.163 → 0.081 | +0.000 | 122 | #59 · 46–50 |
| 3-to-2 | Wh | 2.020 → 0.393 | 4.534 → 0.986 | 7.315 → 1.472 | +0.012 | 122 | #59 · 46–50 |
| same-rate | Ah | 0.030 → 0.013 | 0.074 → 0.035 | 0.102 → 0.056 | +0.000 | 297 | #47 · 21–25 |
| same-rate | Wh | 2.221 → 0.231 | 5.408 → 0.584 | 10.734 → 1.019 | +0.003 | 291 | #63 · 81–85 |
| other-switch | Ah | 0.079 → 0.034 | 0.244 → 0.103 | 0.419 → 0.187 | +0.001 | 418 | #77 · 11–15 |
| other-switch | Wh | 2.358 → 0.614 | 6.764 → 1.792 | 13.352 → 3.451 | +0.006 | 414 | #77 · 11–15 |

## Sensitivity to the first recorded charging rate

Hold out all batteries with the specified first rate and score the two switch directions together. Both models are refitted on the same other batteries. This comparison uses the Notebook 14 feature set with alpha 1 and the 75:25 candidate with alpha 1 in each Ridge component.

| First rate | Unit | MAE old → new | Worst-decile mean old → new | Max old → new | Scored blocks |
| --- | --- | ---: | ---: | ---: | ---: |
| 1C | Ah | 0.106 → 0.033 | 0.210 → 0.095 | 0.247 → 0.135 | 70 |
| 1C | Wh | 3.697 → 0.590 | 7.918 → 1.729 | 9.092 → 2.501 | 70 |
| 2C | Ah | 0.036 → 0.032 | 0.098 → 0.081 | 0.134 → 0.139 | 66 |
| 2C | Wh | 1.644 → 0.568 | 4.523 → 1.473 | 5.969 → 2.383 | 65 |
| 3C | Ah | 0.069 → 0.028 | 0.166 → 0.068 | 0.206 → 0.087 | 84 |
| 3C | Wh | 4.565 → 0.493 | 10.240 → 1.207 | 13.811 → 1.361 | 83 |

## Reproducibility

Selection uses the four inner fold predictions within each outer training set. The inner score averages the two switch directions equally. Each direction uses weights 0.50 for MAE, 0.35 for worst-decile mean, and 0.15 for maximum error.

The saved MIT–BIT cohort was also used during exploration. The results assess this cohort and serve as a baseline for a separate dataset.
