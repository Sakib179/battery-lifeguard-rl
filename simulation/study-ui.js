"use strict";

const study = (() => {
  const get = id => document.getElementById(id);
  const values = list => [...new Set(list)];
  const numbers = list => values(list).sort((a, b) => a - b);
  const format = (value, digits = 2) => Number.isFinite(value) ? value.toFixed(digits) : "—";
  const percent = value => Number.isFinite(value) ? format(100 * value, 2) + "%" : "—";
  const batteryName = cell => typeof cell === "number" ? "Battery #" + cell : "Battery " + cell.split("-").at(-1);

  function select(id, items, preferred, label = value => value) {
    const element = get(id);
    element.replaceChildren(...items.map(value => new Option(label(value), value)));
    if (items.some(value => String(value) === String(preferred))) element.value = String(preferred);
    return element.value;
  }

  function rows(id, entries) {
    get(id).replaceChildren(...entries.map(columns => {
      const row = document.createElement("tr");
      columns.forEach((value, index) => {
        const cell = document.createElement(index ? "td" : "th");
        if (!index) cell.scope = "row";
        if (value instanceof Node) cell.append(value);
        else cell.textContent = value;
        row.append(cell);
      });
      return row;
    }));
  }

  function tabs(id) {
    const list = get(id);
    const buttons = [...list.querySelectorAll('[role="tab"]')].filter(button => !button.hidden);
    const panels = buttons.map(button => get(button.getAttribute("aria-controls")));
    function show(index, focus = false) {
      buttons.forEach((button, position) => {
        const active = index === position;
        button.setAttribute("aria-selected", String(active));
        button.tabIndex = active ? 0 : -1;
        if (!active && !panels[position].hidden) panels[position].dispatchEvent(new Event("study-hide"));
        panels[position].hidden = !active;
      });
      panels[index].dispatchEvent(new Event("study-show"));
      if (focus) buttons[index].focus();
    }
    if (!buttons.length) return;
    buttons.forEach((button, index) => {
      button.addEventListener("click", () => show(index));
      button.addEventListener("keydown", event => {
        const shifts = {ArrowLeft: -1, ArrowRight: 1};
        let selected = index;
        if (event.key in shifts) selected = (index + shifts[event.key] + buttons.length) % buttons.length;
        else if (event.key === "Home") selected = 0;
        else if (event.key === "End") selected = buttons.length - 1;
        else return;
        event.preventDefault();
        show(selected, true);
      });
    });
    show(0);
  }

  function playback(prefix, labels, update, panel) {
    const player = get(prefix + "-play");
    const next = get(prefix + "-next");
    let position = 0;
    let timer;
    const end = labels.length - 1;
    const markers = labels.map((label, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = label;
      button.addEventListener("click", () => { pause(); jump(index); });
      return button;
    });
    get(prefix + "-timeline").replaceChildren(...markers);

    function pause() {
      clearInterval(timer);
      timer = undefined;
      player.textContent = position === end ? "Replay" : "Play";
    }

    function jump(step) {
      position = step;
      next.disabled = position === end;
      if (next.disabled) pause();
      markers.forEach((button, index) => button.setAttribute("aria-pressed", String(index === position)));
      update(position);
    }
    player.addEventListener("click", () => {
      if (timer !== undefined) {
        pause();
        return;
      }
      if (position === end) jump(0);
      player.textContent = "Pause";
      timer = setInterval(() => jump(position + 1), 950);
    });
    next.addEventListener("click", () => { pause(); jump(Math.min(position + 1, end)); });
    get(prefix + "-reset").addEventListener("click", () => { pause(); jump(0); });
    get(panel).addEventListener("study-hide", pause);
    document.addEventListener("visibilitychange", () => { if (document.hidden) pause(); });
    return {restart() { pause(); jump(0); }, update() { update(position); }};
  }

  function plot(id, zero = false) {
    const canvas = get(id);
    let traces = [];
    let labels = [];
    const colors = ["#adbfff", "#78e2ca"];
    function draw() {
      const width = canvas.clientWidth, height = canvas.clientHeight;
      if (!width || !height || !traces.length) return;
      const ratio = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.round(width * ratio);
      canvas.height = Math.round(height * ratio);
      const ctx = canvas.getContext("2d");
      ctx.scale(ratio, ratio);
      const range = traces.flat().filter(Number.isFinite);
      if (!range.length) return;
      const bottom = height - 27, top = 12, left = 43, right = width - 16;
      let low = zero ? 0 : Math.min(...range);
      let high = Math.max(...range);
      const pad = Math.max((high - low) / 10, high === low ? .1 : .01);
      if (!zero) low -= pad;
      high += pad;
      const x = index => left + (right - left) * (labels.length === 1 ? .5 : index / (labels.length - 1));
      const y = number => bottom - (number - low) / (high - low) * (bottom - top);
      ctx.font = "12px system-ui";
      ctx.fillStyle = "#b4c5ce";
      ctx.textAlign = "right";
      ctx.textBaseline = "middle";
      for (let i = 0; i <= 3; i++) {
        const value = low + (high - low) * i / 3;
        ctx.strokeStyle = "#324650";
        ctx.beginPath();
        ctx.moveTo(left, y(value));
        ctx.lineTo(right, y(value));
        ctx.stroke();
        ctx.fillText(format(value, high - low < 10 ? 2 : 0), left - 6, y(value));
      }
      ctx.textAlign = "center";
      labels.forEach((label, index) => { ctx.fillText(label, x(index), height - 10); });
      traces.forEach((trace, series) => {
        ctx.strokeStyle = ctx.fillStyle = colors[series];
        ctx.lineWidth = 2;
        ctx.beginPath();
        trace.forEach((value, index) => {
          if (!Number.isFinite(value)) return;
          if (index > 0 && Number.isFinite(trace[index - 1])) ctx.lineTo(x(index), y(value));
          else ctx.moveTo(x(index), y(value));
        });
        ctx.stroke();
        trace.forEach((value, index) => {
          if (!Number.isFinite(value)) return;
          ctx.beginPath();
          ctx.arc(x(index), y(value), 3.5, 0, Math.PI * 2);
          ctx.fill();
        });
      });
    }
    new ResizeObserver(draw).observe(canvas);
    return (newLabels, newTraces) => { labels = newLabels; traces = newTraces; draw(); };
  }

  return {get, values, numbers, format, percent, batteryName, select, rows, tabs, playback, plot};
})();
