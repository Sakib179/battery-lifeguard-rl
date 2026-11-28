"use strict";

(() => {
  const {get, values, numbers, format, percent, batteryName, select, rows, tabs, playback, plot} = study;
  const data = JSON.parse(get("discharge-data").textContent);
  const algorithms = {
    lookahead: "Original Lookahead", mpc: "Forecast MPC", risk: "Risk-aware MPC", sac: "Discrete SAC",
    ppo: "PPO", fqi: "Fitted Q iteration", fixed: "Fixed middle template", rule: "SOH rule",
  };
  const plotSoh = plot("endpoint-soh");
  const plotWh = plot("endpoint-wh");
  let forecast;
  let audited;

  function renderForecast(step) {
    const finished = step === 3;
    const lastForecast = Math.min(step, 2);
    const [origin, observedSOH, observedWh] = forecast.stages[lastForecast];
    const measured = forecast.measured;
    get("discharge-status").textContent = (finished ? "Measured endpoint" : "Forecast issued at recorded cycle " + origin) +
        " · target is recorded cycle " + forecast.end;
    const now = finished ? measured : [observedSOH, observedWh];
    get("discharge-context").textContent = "Measured at this point: " + format(now[0], 2) + "% SOH · " +
        format(now[1], 2) + " Wh delivered since the start.";
    const scoredStages = finished ? [0, 1, 2] : [lastForecast];
    rows("endpoint-values", scoredStages.flatMap(stage => forecast.stages[stage].slice(3).map((forecasts, index) => {
      const obs = measured[index];
      const unit = index === 0 ? " pp" : " Wh";
      const time = ["Start", "+10 cycles", "+20 cycles"][stage];
      const target = index === 0 ? "SOH (%)" : "Energy (Wh)";
      return [time + " · " + target, ...forecasts.map(value => format(value, 3)),
        finished ? format(obs, 3) : "At finish",
        finished ? format(Math.abs(forecasts[1] - obs), 3) + unit : "—",
        finished ? format(Math.abs(forecasts[2] - obs), 3) + unit : "—"];
    })));
    const visibleStages = forecast.stages.slice(0, lastForecast + 1);
    const labels = ["Start", "+10", "+20"].slice(0, visibleStages.length);
    plotSoh(labels, [visibleStages.map(() => finished ? measured[0] : null), visibleStages.map(item => item[3][2])]);
    plotWh(labels, [visibleStages.map(() => finished ? measured[1] : null), visibleStages.map(item => item[4][2])]);
    const elapsed = lastForecast * 10;
    get("discharge-error-context").textContent = elapsed === 0
      ? "30 operating cycles ahead at the start · 8 held-out batteries."
      : "Updated after " + elapsed + " operating cycles · " + (30 - elapsed) + " cycles still ahead · 8 held-out batteries.";
    const descriptions = {original: "Original", incumbent: "Previous", recommended: "Recommended"};
    rows("endpoint-errors", data.errors.filter(item => item[0] === elapsed)
      .map(([, target, role, count, ...measures]) => {
        const name = target === "soh" ? "SOH" : "Energy";
        const unit = target === "soh" ? " pp" : " Wh";
        return [name + " · " + descriptions[role], count, ...measures.map(item => format(item, 3) + unit)];
      }));
  }

  const forecastPlayer = playback("discharge", ["Start", "+10 cycles", "+20 cycles", "Finish"],
                                  renderForecast, "discharge-forecast");
  function chooseForecast() {
    forecast = data.forecasts.find(item => item.cell === get("discharge-battery").value &&
                                          item.start === Number(get("discharge-start").value));
    forecastPlayer.restart();
  }

  function chooseForecastBattery(start) {
    select("discharge-start", numbers(data.forecasts.filter(item =>
      item.cell === get("discharge-battery").value).map(item => item.start)), start);
    chooseForecast();
  }
  const forecastCells = values(data.forecasts.map(item => item.cell));
  select("discharge-battery", forecastCells, "XJTU_RW_battery-3", batteryName);
  get("discharge-battery").addEventListener("change", () => chooseForecastBattery(get("discharge-start").value));
  get("discharge-start").addEventListener("change", chooseForecast);
  for (const [cell, start] of [[3, 307], [5, 241]]) {
    get("example-" + cell).addEventListener("click", () => {
      get("discharge-battery").value = "XJTU_RW_battery-" + cell;
      chooseForecastBattery(start);
    });
  }
  chooseForecastBattery(307);

  function renderControllers(step) {
    const seed = get("controller-seed").value;
    const actionNames = ["Low", "Middle", "High"];
    get("controller-status").textContent = "Energy budget " + format(audited.budget) + " Wh · " +
      (step ? step * 10 + " operating cycles elapsed" : "Ready");
    rows("controller-actions", Object.entries(algorithms).map(([key, label]) => {
      const id = key + ":" + (key === "sac" || key === "ppo" ? seed : 0);
      const [sequence, loss, energy, hit, stopped] = audited.runs[id];
      const done = step >= sequence.length;
      const blocks = [0, 1, 2].map(index => {
        if (index >= step) return "—";
        return index < sequence.length ? actionNames[Number(sequence[index])] : "Stopped";
      });
      return [label, ...blocks, done ? format(loss, 3) : "—", done ? format(energy) : "—",
        done ? (stopped ? "Support stop" : hit ? "Met" : "Missed") : "Pending"];
    }));
    rows("controller-summary", data.summary.filter(row => row[0] === audited.evaluation)
      .sort((a, b) => Object.keys(algorithms).indexOf(a[1]) - Object.keys(algorithms).indexOf(b[1]))
      .map(([, policy, mean, tail, maximum, hit, stopped, selected]) => [
        algorithms[policy] + (selected ? " · selected" : ""), format(mean, 3), format(tail, 3),
        format(maximum, 3), percent(hit), percent(stopped),
      ]));
  }

  const controllerPlayer = playback("controller", ["Start", "+10 cycles", "+20 cycles", "+30 cycles"],
                                    renderControllers, "discharge-policies");
  function chooseController() {
    const evaluation = get("controller-evaluation").value;
    const cell = get("controller-battery").value;
    const start = Number(get("controller-start").value);
    const draw = Number(get("controller-draw").value);
    audited = data.controllers.find(item => item.evaluation === evaluation && item.cell === cell &&
                                            item.start === start && item.draw === draw);
    controllerPlayer.restart();
  }

  function chooseDisturbance() {
    const evaluation = get("controller-evaluation").value;
    const sample = data.controllers.filter(item => item.evaluation === evaluation);
    const cell = select("controller-battery", values(sample.map(item => item.cell)),
                        get("controller-battery").value, batteryName);
    const starts = sample.filter(item => item.cell === cell);
    const origin = select("controller-start", numbers(starts.map(item => item.start)), get("controller-start").value);
    select("controller-draw", numbers(starts.filter(item => item.start === Number(origin)).map(item => item.draw)),
           get("controller-draw").value, value => "Draw " + (value + 1));
    chooseController();
  }

  select("controller-evaluation", ["original", "stress"], "original",
         value => value === "original" ? "Original" : "25% larger");
  select("controller-seed", [42, 73, 101], 42);
  for (const id of ["controller-evaluation", "controller-battery", "controller-start"]) {
    get(id).addEventListener("change", chooseDisturbance);
  }
  get("controller-draw").addEventListener("change", chooseController);
  get("controller-seed").addEventListener("change", () => controllerPlayer.update());
  chooseDisturbance();
  tabs("discharge-tabs");
})();
