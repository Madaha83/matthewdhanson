// Interactive charts for the strength-gap research page.
// Plain SVG, no libraries. Each chart has hover tooltips and a data table.
(function () {
  "use strict";
  var NS = "http://www.w3.org/2000/svg";

  function el(tag, attrs, parent) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function html(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }
  function niceTicks(min, max, count) {
    var span = max - min, step = Math.pow(10, Math.floor(Math.log10(span / count)));
    var err = span / count / step;
    step *= err >= 7.5 ? 10 : err >= 3.5 ? 5 : err >= 1.5 ? 2 : 1;
    var out = [];
    for (var v = Math.ceil(min / step) * step; v <= max + 1e-9; v += step) out.push(+v.toFixed(10));
    return out;
  }
  function compact(v) {
    if (Math.abs(v) >= 1000) return (v / 1000).toFixed(v >= 10000 ? 0 : 1).replace(/\.0$/, "") + "K";
    return String(v);
  }

  // ── Line chart ──
  // opts: {series:[{key,label,cls,points:[{x,y,lo,hi}]}], xLabel, yFmt, xFmt, yMin, yMax, logX, height, endLabels}
  function lineChart(host, opts) {
    host.innerHTML = "";
    var wrap = html("div", "chart-wrap");
    host.appendChild(wrap);
    var W = Math.max(300, wrap.clientWidth || host.clientWidth || 640);
    var H = opts.height || Math.round(Math.min(380, Math.max(240, W * 0.55)));
    var m = { t: 16, r: opts.endLabels ? 96 : 18, b: 40, l: 48 };
    var iw = W - m.l - m.r, ih = H - m.t - m.b;

    var all = [];
    opts.series.forEach(function (s) { s.points.forEach(function (p) { all.push(p); }); });
    var xs = all.map(function (p) { return p.x; });
    var x0 = Math.min.apply(null, xs), x1 = Math.max.apply(null, xs);
    var ys = [];
    all.forEach(function (p) { ys.push(p.y); if (p.lo != null) ys.push(p.lo, p.hi); });
    var y0 = opts.yMin != null ? opts.yMin : Math.min.apply(null, ys);
    var y1 = opts.yMax != null ? opts.yMax : Math.max.apply(null, ys);
    var pad = (y1 - y0) * 0.06; if (opts.yMin == null) y0 -= pad; if (opts.yMax == null) y1 += pad;

    var fx = opts.logX
      ? function (v) { return m.l + (Math.log(v) - Math.log(x0)) / (Math.log(x1) - Math.log(x0)) * iw; }
      : function (v) { return m.l + (v - x0) / (x1 - x0) * iw; };
    var fy = function (v) { return m.t + (1 - (v - y0) / (y1 - y0)) * ih; };
    var yFmt = opts.yFmt || function (v) { return compact(v); };
    var xFmt = opts.xFmt || function (v) { return String(v); };

    var svg = el("svg", { viewBox: "0 0 " + W + " " + H, width: "100%", role: "img", "aria-label": opts.title || "" });
    wrap.appendChild(svg);

    // grid + axes
    var g = el("g", { class: "grid" }, svg);
    niceTicks(y0, y1, 5).forEach(function (t) {
      var y = fy(t);
      el("line", { x1: m.l, x2: W - m.r, y1: y, y2: y }, g);
      var tx = el("text", { x: m.l - 8, y: y + 4, "text-anchor": "end", class: "tick" }, g);
      tx.textContent = yFmt(t);
    });
    var xt = opts.logX ? opts.xTicks : niceTicks(x0, x1, Math.max(3, Math.floor(iw / 90)));
    xt.forEach(function (t) {
      var tx = el("text", { x: fx(t), y: H - m.b + 20, "text-anchor": "middle", class: "tick" }, g);
      tx.textContent = xFmt(t);
    });
    if (opts.refY != null) {
      el("line", { x1: m.l, x2: W - m.r, y1: fy(opts.refY), y2: fy(opts.refY), class: "ref" }, svg);
    }
    if (opts.xLabel) {
      var xl = el("text", { x: m.l + iw / 2, y: H - 4, "text-anchor": "middle", class: "axis-label" }, svg);
      xl.textContent = opts.xLabel;
    }

    // bands, lines, end dots
    opts.series.forEach(function (s) {
      var pts = s.points;
      if (pts[0] && pts[0].lo != null) {
        var d = pts.map(function (p, i) { return (i ? "L" : "M") + fx(p.x) + "," + fy(p.hi); }).join("") +
          pts.slice().reverse().map(function (p) { return "L" + fx(p.x) + "," + fy(p.lo); }).join("") + "Z";
        el("path", { d: d, class: "band " + s.cls }, svg);
      }
      el("path", { d: pts.map(function (p, i) { return (i ? "L" : "M") + fx(p.x) + "," + fy(p.y); }).join(""),
        class: "line " + s.cls + (s.dashed ? " dashed" : "") }, svg);
      var last = pts[pts.length - 1];
      el("circle", { cx: fx(last.x), cy: fy(last.y), r: 4.5, class: "dot " + s.cls }, svg);
      if (opts.endLabels) {
        var lb = el("text", { x: fx(last.x) + 9, y: fy(last.y) + 4, class: "end-label" }, svg);
        lb.textContent = (s.short || s.label) + " " + (opts.yTip || yFmt)(last.y);
      }
    });
    if (opts.endLabels && opts.series.length === 2) {   // nudge colliding end labels apart
      var labs = svg.querySelectorAll(".end-label");
      var a = +labs[0].getAttribute("y"), b = +labs[1].getAttribute("y");
      if (Math.abs(a - b) < 14) {
        var mid = (a + b) / 2, up = a < b ? 0 : 1;
        labs[up].setAttribute("y", mid - 7); labs[1 - up].setAttribute("y", mid + 9);
      }
    }

    // hover layer: crosshair + tooltip at nearest x
    var hover = el("g", { class: "hover", style: "display:none" }, svg);
    var vline = el("line", { y1: m.t, y2: m.t + ih, class: "crosshair" }, hover);
    var hdots = opts.series.map(function (s) { return el("circle", { r: 5, class: "dot " + s.cls }, hover); });
    var tip = html("div", "chart-tip");
    tip.hidden = true;
    wrap.appendChild(tip);
    var xsU = Array.from(new Set(xs)).sort(function (a, b) { return a - b; });

    function show(px) {
      var best = xsU[0], bd = Infinity;
      xsU.forEach(function (v) { var dd = Math.abs(fx(v) - px); if (dd < bd) { bd = dd; best = v; } });
      var X = fx(best);
      hover.style.display = "";
      vline.setAttribute("x1", X); vline.setAttribute("x2", X);
      tip.innerHTML = "";
      tip.appendChild(html("div", "tip-x", (opts.xTip || xFmt)(best)));
      opts.series.forEach(function (s, i) {
        var p = s.points.find(function (q) { return q.x === best; });
        if (!p) { hdots[i].style.display = "none"; return; }
        hdots[i].style.display = "";
        hdots[i].setAttribute("cx", X); hdots[i].setAttribute("cy", fy(p.y));
        var row = html("div", "tip-row");
        var key = html("span", "key " + s.cls);
        row.appendChild(key);
        row.appendChild(html("span", "tip-l", s.label));
        row.appendChild(html("strong", null, (opts.yTip || yFmt)(p.y) + (p.lo != null ? "  (" + (opts.yTip || yFmt)(p.lo) + "–" + (opts.yTip || yFmt)(p.hi) + ")" : "")));
        tip.appendChild(row);
      });
      tip.hidden = false;
      var left = X / W * wrap.clientWidth;
      tip.style.left = Math.min(Math.max(left - tip.offsetWidth / 2, 0), wrap.clientWidth - tip.offsetWidth) + "px";
    }
    function hide() { hover.style.display = "none"; tip.hidden = true; }
    var hit = el("rect", { x: m.l, y: m.t, width: iw, height: ih, class: "hit", tabindex: 0 }, svg);
    function toSvgX(evt) {
      var r = svg.getBoundingClientRect();
      return (evt.clientX - r.left) / r.width * W;
    }
    hit.addEventListener("pointermove", function (e) { show(toSvgX(e)); });
    hit.addEventListener("pointerleave", hide);
    var kIdx = xsU.length - 1;
    hit.addEventListener("focus", function () { show(fx(xsU[kIdx])); });
    hit.addEventListener("blur", hide);
    hit.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft") kIdx = Math.max(0, kIdx - 1);
      else if (e.key === "ArrowRight") kIdx = Math.min(xsU.length - 1, kIdx + 1);
      else return;
      e.preventDefault(); show(fx(xsU[kIdx]));
    });
  }

  // ── Horizontal bar chart (single series) ──
  function barChart(host, rows, fmt) {
    host.innerHTML = "";
    var wrap = html("div", "chart-wrap");
    host.appendChild(wrap);
    var W = Math.max(300, wrap.clientWidth || 640), rowH = 34, m = { l: 168, r: 64, t: 6 };
    var H = rows.length * rowH + m.t + 6, iw = W - m.l - m.r;
    var max = Math.max.apply(null, rows.map(function (r) { return r.v; }));
    var svg = el("svg", { viewBox: "0 0 " + W + " " + H, width: "100%", role: "img" }, wrap);
    rows.forEach(function (r, i) {
      var y = m.t + i * rowH, w = Math.max(2, r.v / max * iw), bh = 18;
      var lab = el("text", { x: m.l - 10, y: y + rowH / 2 + 4, "text-anchor": "end", class: "bar-label" }, svg);
      lab.textContent = r.label;
      el("path", { d: "M" + m.l + "," + (y + (rowH - bh) / 2) + "h" + (w - 4) + "a4,4 0 0 1 4,4v" + (bh - 8) + "a4,4 0 0 1 -4,4h" + (4 - w) + "Z",
        class: "bar " + (r.cls || "") }, svg);
      var val = el("text", { x: m.l + w + 8, y: y + rowH / 2 + 4, class: "bar-value" }, svg);
      val.textContent = fmt(r.v);
    });
  }

  // ── Data table (the accessible view of every chart) ──
  function table(host, cols, rows) {
    var t = html("table", "data-table");
    var tr = html("tr");
    cols.forEach(function (c) { tr.appendChild(html("th", null, c)); });
    var thead = html("thead"); thead.appendChild(tr); t.appendChild(thead);
    var tb = html("tbody");
    rows.forEach(function (r) {
      var row = html("tr");
      r.forEach(function (c) { row.appendChild(html("td", null, c)); });
      tb.appendChild(row);
    });
    t.appendChild(tb);
    host.innerHTML = "";
    host.appendChild(t);
  }

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
