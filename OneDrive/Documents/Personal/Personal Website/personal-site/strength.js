// Interactive charts for the strength-gap research page.
// Plain SVG, no libraries. Each chart has hover tooltips and a data table.
(function () {
  "use strict";
  var C = window.MHCharts, lineChart = C.lineChart, barChart = C.barChart, table = C.table, compact = C.compact;
  var pct = function (v) { return Math.round(v * 100) + "%"; };
  var pct1 = function (v) { return (v * 100).toFixed(1) + "%"; };

  function draw(D) {
    // 1. Participation
    var part = D.participation;
    lineChart(document.getElementById("c-participation"), {
      title: "Lifters per year by sex",
      series: [
        { label: "Women", short: "Women", cls: "s-women", points: part.map(function (p) { return { x: p.year, y: p.women }; }) },
        { label: "Men", short: "Men", cls: "s-men", points: part.map(function (p) { return { x: p.year, y: p.men }; }) }
      ],
      yMin: 0, endLabels: true
    });
    table(document.getElementById("t-participation"), ["Year", "Women", "Men", "Women's share"],
      part.map(function (p) { return [p.year, p.women.toLocaleString(), p.men.toLocaleString(), pct(p.women / (p.women + p.men))]; }));

    // 2. Gap over time, with level toggle
    var levels = { top: "Top 10", p99: "99th percentile", median: "Median" };
    function drawGap(level) {
      lineChart(document.getElementById("c-gap"), {
        title: "Women's strength as a share of men's",
        series: [{ label: levels[level], cls: "s-ink",
          points: D.trend.map(function (r) { return { x: r.year, y: r[level][0], lo: r[level][1], hi: r[level][2] }; }) }],
        yFmt: pct, yTip: pct1
      });
    }
    var gapSel = document.querySelector("input[name=gap-level]:checked");
    drawGap(gapSel ? gapSel.value : "top");
    document.querySelectorAll("input[name=gap-level]").forEach(function (r) {
      r.onchange = function () { drawGap(r.value); };
    });
    table(document.getElementById("t-gap"), ["Year", "Top 10", "99th percentile", "Median"],
      D.trend.map(function (r) { return [r.year, pct1(r.top[0]), pct1(r.p99[0]), pct1(r.median[0])]; }));

    // 3. Observed vs equal-size fields
    var dm = D.depth_matched.filter(function (r) { return r.fixed; });
    lineChart(document.getElementById("c-depth"), {
      title: "Top-10 ratio, observed and with equal-size fields",
      series: [
        { label: "Observed", short: "Observed", cls: "s-men", points: dm.map(function (r) { return { x: r.year, y: r.observed }; }) },
        { label: "Equal fields (" + D.meta.fixed_pool + " each)", short: "Equal", cls: "s-ochre",
          points: dm.map(function (r) { return { x: r.year, y: r.fixed[0], lo: r.fixed[1], hi: r.fixed[2] }; }) }
      ],
      yFmt: pct, yTip: pct1, endLabels: true
    });
    table(document.getElementById("t-depth"), ["Year", "Observed", "Equal fields", "95% interval"],
      dm.map(function (r) { return [r.year, pct1(r.observed), pct1(r.fixed[0]), pct1(r.fixed[1]) + "–" + pct1(r.fixed[2])]; }));

    // 4. Career growth
    var cv = D.careers.curve.filter(function (r) { return r.t <= 3; });
    lineChart(document.getElementById("c-careers"), {
      title: "Strength gain since first meet",
      series: ["F", "M"].map(function (s) {
        return { label: s === "F" ? "Women" : "Men", short: s === "F" ? "Women" : "Men", cls: s === "F" ? "s-women" : "s-men",
          points: cv.filter(function (r) { return r.sex === s; }).map(function (r) { return { x: r.t, y: r.pct }; }) };
      }),
      yMin: 0, xLabel: "Years since first meet", yFmt: function (v) { return "+" + v + "%"; },
      yTip: function (v) { return "+" + v.toFixed(1) + "%"; }, xTip: function (v) { return v + " years"; }, endLabels: true
    });
    var cvF = cv.filter(function (r) { return r.sex === "F"; });
    table(document.getElementById("t-careers"), ["Years", "Women", "Men"],
      cvF.filter(function (r) { return r.t % 1 === 0; }).map(function (r) {
        var mm = cv.find(function (q) { return q.sex === "M" && q.t === r.t; });
        return [r.t, "+" + r.pct.toFixed(1) + "%", "+" + mm.pct.toFixed(1) + "%"];
      }));

    // 5. ML: permutation importance
    var pi = D.ml.perm_importance;
    barChart(document.getElementById("c-importance"),
      pi.map(function (r) { return { label: r.feature, v: Math.max(0, r.drop_r2), cls: "s-men" }; }),
      function (v) { return v.toFixed(v < 0.1 ? 3 : 2); });
    table(document.getElementById("t-importance"), ["Feature", "Drop in R² when shuffled"],
      pi.map(function (r) { return [r.feature, r.drop_r2.toFixed(3)]; }));

    // 6. ML: composition-adjusted gap by year
    var adj = D.ml.adjusted_by_year;
    var adjNames = { elite: "Elite lifter (95th percentile model)", typical: "Typical lifter (mean model)" };
    function drawAdj(which) {
      lineChart(document.getElementById("c-adjusted"), {
        title: "Women's predicted strength as a share of men's, same lifters in every year",
        series: [{ label: adjNames[which], cls: "s-ink", points: adj.map(function (r) { return { x: r.year, y: r[which] }; }) }],
        yFmt: pct1, yTip: pct1
      });
    }
    var adjSel = document.querySelector("input[name=adj-level]:checked");
    drawAdj(adjSel ? adjSel.value : "elite");
    document.querySelectorAll("input[name=adj-level]").forEach(function (r) {
      r.onchange = function () { drawAdj(r.value); };
    });
    table(document.getElementById("t-adjusted"), ["Year", "Typical", "Elite"],
      adj.map(function (r) { return [r.year, pct1(r.typical), pct1(r.elite)]; }));

    // 7. Robustness: longer history by division
    var divs = {};
    D.robustness.forEach(function (r) { (divs[r.div] = divs[r.div] || []).push(r); });
    function drawRob(div) {
      lineChart(document.getElementById("c-robust"), {
        title: "Top-10 ratio by division",
        series: [{ label: div, cls: "s-ink", points: divs[div].map(function (r) { return { x: r.year, y: r.top }; }) }],
        yFmt: pct, yTip: pct1
      });
      table(document.getElementById("t-robust"), ["Year", "Women", "Men", "Top-10 ratio", "Median ratio"],
        divs[div].map(function (r) { return [r.year, r.nf.toLocaleString(), r.nm.toLocaleString(), pct1(r.top), pct1(r.median)]; }));
    }
    var robSel = document.getElementById("rob-div");
    if (robSel && !robSel.options.length) {
      Object.keys(divs).forEach(function (k) { var o = document.createElement("option"); o.value = o.textContent = k; robSel.appendChild(o); });
      robSel.value = "Equipped, tested";
      robSel.addEventListener("change", function () { drawRob(robSel.value); });
    }
    drawRob(robSel ? robSel.value : "Equipped, tested");
  }

  document.addEventListener("DOMContentLoaded", function () {
    fetch("strength-data.json").then(function (r) { return r.json(); }).then(function (D) {
      draw(D);
      var w = window.innerWidth, t;
      window.addEventListener("resize", function () {
        if (Math.abs(window.innerWidth - w) < 40) return;
        w = window.innerWidth; clearTimeout(t); t = setTimeout(function () { draw(D); }, 150);
      });
    });
  });
})();
