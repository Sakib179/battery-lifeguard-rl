# LifeGuard-RL live presentation

## Set up the screen

Open the Streamlit dashboard in a full-screen browser window. Begin on **Charging** with **Battery 71 · start 11** at cycle 0. Use **Next** to pause on each result during this script. **Play** demonstrates how the same steps update automatically, and **Reset** returns to the first reading. If the server fails during the talk, open [the offline dashboard](../simulation/index.html) in the browser and use its charging and discharge pages.

## 0:00–1:00 · Start with the question

> Two batteries can both read 100% charged and still hold different amounts of energy. Over time, their capacity can shrink. This demo follows one battery at a time and shows how updated measurements can inform charging and discharging decisions.

Point to **Fixed 1C** and **Adaptive**. They start from the same recorded battery state in the simulation and share the same delivered-energy target of **85.91 Wh**.

## 1:00–3:30 · Charging time and delivered energy

1. Click **Next** once. Both strategies charge at the same rate for the first block. They have each delivered **31.64 Wh** and the time saving is **0.0 minutes**.
2. Click **Next** again. The adaptive strategy moves to **2C**, twice the fixed charging current, for the second block. The time saving reaches **139.8 minutes**. Point to both energy totals. Fixed has delivered **63.42 Wh** and adaptive has delivered **58.48 Wh**.
3. Click **Next** to finish. Adaptive returns to **1C**, saves **147.5 minutes** overall, and delivers **89.49 Wh** against the **85.91 Wh** target. Fixed delivers **95.46 Wh**.

> The adaptive strategy finished sooner and supplied enough energy for this target. Fixed charging supplied about six watt-hours more. The result shows a trade-off between time and delivered energy.

If asked about electricity consumption, explain that the Wh reported here is the energy supplied during discharge. Input electricity consumption and operating cost would require additional measurements.

## 3:30–5:45 · A forecast updates with new readings

Go to **Discharging → Forecast replay**, **Battery 1 · RW · start 21**. Explain that both lines predict health and cumulative delivered energy at the same future endpoint. The gray line preserves the first forecast and the orange line updates as readings arrive.

Click **Next** at 10 and 20 operating cycles. Point to the running measured energy and the updated endpoint forecast. Click **Next** at 30 cycles to show the result. In this example, the absolute health error decreases from **0.566 to 0.059 percentage points** and the energy error decreases from **0.800 to 0.073 Wh**.

> Each update gives the forecast more evidence and a shorter period to predict. Here, the last update was closer to the measured result.

## 5:45–7:45 · Compare operating decisions

Go to **Discharging → Controller comparison**, **Battery 1 · RW · start 54**. Leave **Lookahead** selected. Both methods face the same **176.45 Wh** target. Step through the three decisions. Fixed chooses **Middle** every time, while Lookahead chooses **Low** for this example. Both hit the energy target. Point to the final simulated health loss of **3.016** versus **2.562 percentage points**.

> Lookahead compares future choices before selecting the next action. The step-by-step display shows its choices. The totals show how this run ended.

For questions about reinforcement learning, select **Soft Actor-Critic** or **PPO** and replay the same scenario. On the full Notebook 23 benchmark, Lookahead had lower mean simulated health loss than both. Charging and discharge controller results are simulated. Experiments with physical batteries would be needed to establish an effect on lifetime.

## 7:45–9:00 · Battery life and takeaway

Go to **Battery life → Battery 11 · 3C**. At cycle 100, the model estimates **42 cycles left**. Use **Play** to reach the end of the recording. The battery reached the study’s 80% health threshold at cycle 130, which was **30 cycles later**.

> We can update our forecast as the battery runs and use those estimates to compare decisions. We can also measure how far each estimate was from the recorded outcome.

For Q&A, keep the original [charging comparison](../reports/lifeguard_mit_bit_energy_budget_controller_results/summary.md), [discharge results](../reports/lifeguard_xjtu_discharge_forecast_sac_results/summary.md), and [battery life forecasts](../reports/lifeguard_rolling_forecasts_results/summary.md) open in separate tabs.
