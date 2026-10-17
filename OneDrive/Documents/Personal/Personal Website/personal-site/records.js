// Charts for the "Do women's records catch up?" research page.
(function () {
  "use strict";
  var C = window.MHCharts;
  var pct1 = C.pct1;
  var pct = function (v) { return Math.round(v * 100) + "%"; };

  function draw(D) {
    var curves = {};
    D.curves.forEach(function (c) { curves[c.event] = c; });
    var ev = {};
    D.events.forEach(function (e) { ev[e.event] = e; });

    // 1. Marathon: record ratio, catch-up fit, and the 1992 straight-line projection
    var mc = curves["Marathon"];
    C.lineChart(document.getElementById("c-marathon"), {
      title: "Women's marathon record as a share of men's",
      series: [
        { label: "World records", short: "Records", cls: "s-men", points: mc.points.map(function (p) { return { x: p[0], y: p[1] }; }) },
        { label: "Catch-up model", short: "Model", cls: "s-ref", points: mc.fit.map(function (p) { return { x: p[0], y: p[1] }; }) },
        { label: "1992-style projection", short: "1992 line", cls: "s-ochre", dashed: true,
          points: D.whipp_ward.line.filter(function (p) { return p[1] <= 1.06; }).map(function (p) { return { x: p[0], y: p[1] }; }) }
      ],
      yMin: 0.6, yMax: 1.06, refY: 1, refLabel: "Parity", yFmt: pct, yTip: pct1, endLabels: true
    });
    C.table(document.getElementById("t-marathon"), ["Year", "Record ratio", "Model"],
      mc.points.filter(function (p) { return p[0] % 5 === 0 || p[0] === 2026; }).map(function (p) {
        var f = mc.fit.find(function (q) { return q[0] === p[0]; });
        return [p[0], pct1(p[1]), f ? pct1(f[1]) : "—"];
      }));

    // 2. Any event: records and fitted curve
    var sel = document.getElementById("ev-select");
    function drawEvent(name) {
      var c = curves[name], e = ev[name];
      C.lineChart(document.getElementById("c-event"), {
        title: name + ": women's record as a share of men's",
        series: [
          { label: "World records", short: "Records", cls: "s-men", points: c.points.map(function (p) { return { x: p[0], y: p[1] }; }) },
          { label: "Catch-up model", short: "Model", cls: "s-ref", points: c.fit.map(function (p) { return { x: p[0], y: p[1] }; }) }
        ],
        yFmt: pct, yTip: pct1, endLabels: true
      });
      document.getElementById("ev-summary").textContent =
        "Catch-up began around " + e.onset_year + ". Estimated plateau: " + pct1(e.plateau) +
        " (95% interval " + pct1(e.plateau_ci[0]) + "–" + pct1(e.plateau_ci[1]) + "). Today: " + pct1(e.ratio_now) + "." +
        (e.frozen ? " Note: the women's record here has stood since the 1980s–90s doping era." : "");
      C.table(document.getElementById("t-event"), ["Year", "Men", "Women", "Ratio"],
        D.series[name].map(function (r) { return [r[0], r[1], r[2], pct1(r[3])]; }));
    }
    if (!sel.options.length) {
      ["athletics", "swimming"].forEach(function (sport) {
        var og = document.createElement("optgroup");
        og.label = sport === "athletics" ? "Athletics" : "Swimming (long course)";
        D.events.filter(function (e) { return e.sport === sport; }).forEach(function (e) {
          var o = document.createElement("option"); o.value = o.textContent = e.event; og.appendChild(o);
        });
        sel.appendChild(og);
      });
      sel.value = "10,000 m";
      sel.addEventListener("change", function () { drawEvent(sel.value); });
    }
    drawEvent(sel.value);

    // 3. Plateaus vs parity
    var rows = D.events.filter(function (e) { return e.identified; }).sort(function (a, b) { return b.plateau - a.plateau; }).map(function (e) {
      return { label: e.event.replace(" (LCM)", ""), v: e.plateau, lo: e.plateau_ci[0], hi: e.plateau_ci[1],
        cls: e.sport === "swimming" ? "s-men" : "s-ochre",
        note: (e.sport === "swimming" ? "Swimming" : "Athletics") + " · today " + pct1(e.ratio_now) + (e.frozen ? " · frozen record" : "") };
    });
    C.dotChart(document.getElementById("c-plateau"), rows, {
      min: 0.75, max: 1.02, ref: 1, refLabel: "Parity", fmt: pct, fmt1: pct1, tipLabel: "Plateau",
      title: "Estimated plateau of the women-to-men record ratio, by event"
    });
    C.table(document.getElementById("t-plateau"), ["Event", "Plateau", "95% interval", "Today", "Catch-up began"],
      D.events.map(function (e) { return [e.event, pct1(e.plateau), pct1(e.plateau_ci[0]) + "–" + pct1(e.plateau_ci[1]), pct1(e.ratio_now), e.onset_year]; }));

    // 4. Catch-up windows: onset to 95% of the catch-up
    var win = D.events.filter(function (e) { return e.identified; })
      .sort(function (a, b) { return a.onset_year - b.onset_year; })
      .map(function (e) {
        return { label: e.event.replace(" (LCM)", ""), v: e.onset_year, lo: e.onset_year, hi: Math.min(2026, e.onset_year + 3 * e.tau),
          tau3: Math.round(3 * e.tau), cls: e.sport === "swimming" ? "s-men" : "s-ochre",
          note: "About " + Math.round(3 * e.tau) + " years to 95% of the catch-up" };
      });
    C.table(document.getElementById("t-window"), ["Event", "Catch-up began", "About 95% complete", "Years"],
      win.map(function (r) { return [r.label, Math.round(r.lo), r.lo + r.tau3 > 2026 ? "after 2026" : Math.round(r.lo + r.tau3), r.tau3]; }));
    C.dotChart(document.getElementById("c-window"), win, {
      min: 1900, max: 2030, fmt: String, fmt1: function (v) { return String(Math.round(v)); }, tipLabel: "Onset → 95%",
      title: "When each event's catch-up began and roughly when it was 95% complete"
    });

    // 5. Improvement since 2000, men vs women
    var gains = D.events.filter(function (e) { return e.gain_2000_m != null && !isNaN(e.gain_2000_m); })
      .sort(function (a, b) { return (b.gain_2000_m + b.gain_2000_w) - (a.gain_2000_m + a.gain_2000_w); });
    C.dumbbell(document.getElementById("c-gains"), gains.map(function (e) {
      return { label: e.event.replace(" (LCM)", ""), a: e.gain_2000_m, b: e.gain_2000_w };
    }), { min: -0.01, max: Math.max.apply(null, gains.map(function (e) { return Math.max(e.gain_2000_m, e.gain_2000_w); })) + 0.01,
      fmt: function (v) { return (v * 100).toFixed(0) + "%"; }, fmt1: function (v) { return (v >= 0 ? "+" : "") + (v * 100).toFixed(1) + "%"; },
      aCls: "s-men", bCls: "s-women", aLabel: "Men", bLabel: "Women", title: "Record improvement since 2000 by sex" });
    C.table(document.getElementById("t-gains"), ["Event", "Men", "Women", "Ratio change"],
      gains.map(function (e) { return [e.event, (e.gain_2000_m * 100).toFixed(1) + "%", (e.gain_2000_w * 100).toFixed(1) + "%",
        ((1 + e.gain_2000_w) / (1 + e.gain_2000_m) - 1 >= 0 ? "+" : "") + (((1 + e.gain_2000_w) / (1 + e.gain_2000_m) - 1) * 100).toFixed(1) + "%"]; }));

    // 6. Marathon majors winners
    var mj = D.majors.by_year.filter(function (r) { return r[0] >= 1975; });
    C.lineChart(document.getElementById("c-majors"), {
      title: "Women's winning time as a share of men's, World Marathon Majors",
      series: [{ label: "Average of majors held that year", cls: "s-ink", points: mj.map(function (r) { return { x: r[0], y: r[1] }; }) }],
      yFmt: pct, yTip: pct1
    });
    C.table(document.getElementById("t-majors"), ["Year", "Average ratio", "Races"],
      mj.map(function (r) { return [r[0], pct1(r[1]), r[2]]; }));
  }

  document.addEventListener("DOMContentLoaded", function () {
    fetch("records-data.json").then(function (r) { return r.json(); }).then(function (D) {
      draw(D);
      var w = window.innerWidth, t;
      window.addEventListener("resize", function () {
        if (Math.abs(window.innerWidth - w) < 40) return;
        w = window.innerWidth; clearTimeout(t); t = setTimeout(function () { draw(D); }, 150);
      });
    });
  });
})();
