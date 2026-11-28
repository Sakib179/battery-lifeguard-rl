"use strict";

(() => {
  const {get, select, rows} = study;
  const coverage = data.coverage;
  if (!coverage?.folds || !Object.keys(coverage.folds).length) return;

  const folds = Object.keys(coverage.folds);
  const maximum = Math.max(1, ...Object.values(coverage.folds).flatMap(bins =>
    bins.flatMap(([, , two, three]) => [two, three])));
  select("coverage-fold", folds, folds[0], fold => "Fold " + fold);
  function bar(value, rate, band) {
    const wrapper = document.createElement("div");
    const meter = document.createElement("meter");
    const count = document.createElement("span");
    wrapper.className = "coverage-bar";
    meter.className = rate === "2C" ? "coverage-two" : "coverage-three";
    meter.max = maximum;
    meter.value = value;
    meter.setAttribute("aria-label", rate + " training batteries at " + band + "% SOH");
    count.textContent = value;
    count.setAttribute("aria-hidden", "true");
    wrapper.append(meter, count);
    return wrapper;
  }
  function render() {
    rows("coverage-rows", coverage.folds[get("coverage-fold").value].map(([low, high, two, three, supported]) => {
      const band = low + "–" + high;
      return [band + "%", bar(two, "2C", band), bar(three, "3C", band), supported ? "Yes" : "No"];
    }));
  }
  get("coverage-fold").addEventListener("change", render);
  get("coverage-switches").textContent = "Sustained 2C↔3C switches found on the same XJTU battery: " + coverage.switches;
  get("coverage-replay").hidden = !document.querySelector('nav a[href="switch-replay.html"]');
  get("protocol-coverage").hidden = false;
  render();
})();
