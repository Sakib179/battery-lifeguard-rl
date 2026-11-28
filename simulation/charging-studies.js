"use strict";

(() => {
  const {get, numbers, format, percent, batteryName, select, rows, tabs, plot} = study;
  const {charging, measured, validation} = JSON.parse(get("charging-studies-data").textContent);
  const rates = path => Array.from(path, rate => rate + "C").join(" · ");
  const cycles = value => value + " cycles";
  const forecastNames = {ridge: "Notebook 18 Ridge", selected: "Refined forecast"};

  function byStart(prefix, getCases, render, defaults = {}) {
    const battery = prefix + "-battery";
    const start = prefix + "-start";
    function update() {
      const cell = Number(get(battery).value);
      const origin = Number(get(start).value);
      render(getCases().find(item => item.cell === cell && item.start === origin));
    }
    function selectBattery() {
      const cell = Number(get(battery).value);
      const choices = numbers(getCases().filter(item => item.cell === cell).map(item => item.start));
      select(start, choices, get(start).value || defaults.start);
      update();
    }
    get(battery).addEventListener("change", selectBattery);
    get(start).addEventListener("change", update);
    return function refresh() {
      select(battery, numbers(getCases().map(item => item.cell)), get(battery).value || defaults.cell, batteryName);
      selectBattery();
    };
  }

  function mountComparison(data) {
    const names = {original: "Notebook 18 MPC", improved: "Forecast-refined MPC", sac: "Discrete SAC", fixed: "Fixed 1C"};
    let selectedOrigin;
    function render() {
      const draw = Number(get("matched-draw").value);
      const seed = get("matched-seed").value;
      const current = data.cases.find(item => item.cell === selectedOrigin.cell && item.start === selectedOrigin.start &&
                                             item.draw === draw);
      get("matched-budget").textContent = "Matched energy target " + format(current.budget) + " Wh";
      rows("matched-rows", Object.entries(names).map(([policy, label]) => {
        const [sequence, time, energy] = current.runs[policy + ":" + (policy === "sac" ? seed : 0)];
        return [label, rates(sequence), format(time, 1), format(energy),
                format(Math.max(0, current.budget - energy)), energy >= current.budget ? "Met" : "Missed"];
      }));
    }
    function chooseOrigin(current) {
      selectedOrigin = current;
      const draws = numbers(data.cases.filter(item => item.cell === current.cell && item.start === current.start)
                                      .map(item => item.draw));
      select("matched-draw", draws, get("matched-draw").value, value => "Draw " + (value + 1));
      render();
    }
    const origins = data.cases.filter(item => item.draw === 0);
    select("matched-seed", [42, 73, 101], 42);
    get("matched-draw").addEventListener("change", render);
    get("matched-seed").addEventListener("change", render);
    byStart("matched", () => origins, chooseOrigin, {cell: 59})();

    rows("matched-summary", Object.entries(names).map(([policy, label]) => {
      const [time, energy, hit, worst, selected] = data.summary[policy];
      return [label + (selected ? " · selected" : ""), format(time, 1), format(energy), percent(hit), format(worst, 3)];
    }));
    get("matched-charging").hidden = false;
    get("legacy-charging").open = false;
  }

  function mountForecasts(data) {
    const horizon = () => Number(get("charge-forecast-horizon").value);
    const cases = () => data.forecasts.filter(item => item.horizon === horizon());
    const update = byStart("charge-forecast", cases, item => {
      get("charge-forecast-context").textContent = "Recorded rates by 5-cycle block: " + rates(item.sequence);
      rows("charge-forecast-rows", ["Delivered energy (Wh)", "Charging time (min)"].map((label, index) => {
        const actual = item.measured[index], ridge = item.ridge[index], refined = item.selected[index];
        return [label, ...[actual, ridge, refined, Math.abs(ridge-actual), Math.abs(refined-actual)]
                         .map(value => format(value, 3))];
      }));
      rows("charge-forecast-errors", data.errors.filter(row => row[0] === horizon())
        .map(([, target, model, windows, ...measures]) => {
          const unit = target === "wh" ? " Wh" : " min";
          return [(target === "wh" ? "Energy" : "Time") + " · " + forecastNames[model], windows,
                  ...measures.map(value => format(value, 3) + unit)];
        }));
    }, {cell: 59, start: 16});
    select("charge-forecast-horizon", [5, 10, 15], 15, cycles);
    get("charge-forecast-horizon").addEventListener("change", update);
    update();
  }

  function mountMeasured(data) {
    const names = {fixed_1c: "Fixed 1C", fixed_2c: "Fixed 2C", fixed_3c: "Fixed 3C",
                   rule: "Past-observation rule", model: "Model-guided"};
    byStart("measured", () => data.cases, item => {
      get("measured-context").textContent = `Cycles ${item.start}–${item.end} · Recorded rate ${item.logged}C · Energy target ${format(item.budget)} Wh`;
      rows("measured-block", Object.entries(names).map(([policy, label]) => {
        const [chosen, matched, hit] = item.policies[policy];
        const result = hit === null ? (matched ? "Wh unavailable" : "—") : hit ? "Met" : "Missed";
        return [label, chosen + "C", matched ? "Matched" : "Different rate",
                matched ? format(item.minutes, 1) : "—", matched ? format(item.wh) : "—", result];
      }));
    }, {cell: 1, start: 11})();
    rows("measured-summary", Object.entries(names).map(([policy, label]) => {
      const [matched, withWh, minutes, energy, hit] = data.summary[policy];
      return [label, matched + "/929", withWh, format(minutes, 1), format(energy), percent(hit)];
    }));
  }

  function mountValidation(data) {
    const cohort = () => get("validation-cohort").value;
    const horizon = () => Number(get("validation-horizon").value);
    const cases = () => data.cases.filter(item => item.cohort === cohort() && item.horizon === horizon());
    const energyPlot = plot("validation-energy", true);
    const timePlot = plot("validation-time", true);
    const capacityPlot = plot("validation-capacity");
    const labels = {
      cumulative_wh: ["Delivered energy", " Wh"], cumulative_minutes: ["Charging time", " min"],
      final_ah: ["Final capacity", " Ah"],
    };
    const update = byStart("validation", cases, item => {
      get("validation-context").textContent = "Recorded rates by 5-cycle block: " + rates(item.path.map(block => block[0]));
      const labels = item.path.map((_, index) => "+" + (index + 1) * 5);
      const delivered = [0, 0, 0, 0];
      const cumulative = item.path.map(block => {
        block.slice(1, 5).forEach((value, j) => { delivered[j] += value; });
        return [block[0], ...delivered, ...block.slice(5)];
      });
      const series = (arr, a, b) => [arr.map(block => block[a]), arr.map(block => block[b])];
      energyPlot(["Start", ...labels], series([[0, 0, 0], ...cumulative], 1, 2));
      timePlot(["Start", ...labels], series([[0, 0, 0, 0, 0], ...cumulative], 3, 4));
      capacityPlot(labels, series(cumulative, 5, 6));
      rows("validation-blocks", cumulative.map(([rate, ...metrics], index) => [
        (index + 1) * 5, rate + "C", ...metrics.map((value, j) => format(value, j >= 4 ? 3 : 2)),
      ]));
    }, {cell: 8, start: 11});

    function showBenchmark() {
      update();
      rows("validation-errors", data.errors.filter(row => row[0] === cohort() && row[1] === horizon())
        .map(([, , metric, windows, batteries, ...scores]) => {
          const [label, unit] = labels[metric];
          return [label, windows, batteries, ...scores.map(value => format(value, 3) + unit)];
        }));
    }
    select("validation-cohort", ["randomized", "fixed"], "randomized",
           value => value === "fixed" ? "Fixed-rate" : "Randomized");
    select("validation-horizon", [5, 15, 30], 15, cycles);
    get("validation-cohort").addEventListener("change", showBenchmark);
    get("validation-horizon").addEventListener("change", showBenchmark);
    showBenchmark();
  }

  if (charging) {
    mountComparison(charging);
    mountForecasts(charging);
  } else {
    get("charge-forecasts-tab").hidden = true;
  }
  if (measured) mountMeasured(measured);
  else get("charge-measured-tab").hidden = true;
  if (validation) mountValidation(validation);
  else get("charge-validation-tab").hidden = true;
  tabs("charging-tabs");
})();
