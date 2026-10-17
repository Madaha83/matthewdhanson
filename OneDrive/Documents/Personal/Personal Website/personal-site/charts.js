// Shared SVG chart engine for the research pages. No libraries.
// Exposes window.MHCharts = { lineChart, barChart, dotChart, table, pct, pct1, compact }.
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
      if (opts.refLabel) {
        var rlab = el("text", { x: m.l + 6, y: fy(opts.refY) - 6, class: "tick ref-label" }, svg);
        rlab.textContent = opts.refLabel;
      }
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
    if (opts.endLabels) {   // spread colliding end labels apart, keeping their order
      var labs = Array.prototype.slice.call(svg.querySelectorAll(".end-label"))
        .sort(function (p, q) { return +p.getAttribute("y") - +q.getAttribute("y"); });
      for (var k = 1; k < labs.length; k++) {
        var prev = +labs[k - 1].getAttribute("y"), cur = +labs[k].getAttribute("y");
        if (cur - prev < 15) labs[k].setAttribute("y", prev + 15);
      }
    }

    // hover layer: crosshair + tooltip at nearest x
    var hover = el("g", { class: "hover" }, svg);
    hover.style.display = "none";   // set via CSSOM: the CSP blocks style attributes
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

  // ── Dot-and-whisker chart (one row per item, estimate with interval) ──
  // rows: [{label, v, lo, hi, cls, note}], opts: {min, max, ref, refLabel, fmt}
  function dotChart(host, rows, opts) {
    host.innerHTML = "";
    var wrap = html("div", "chart-wrap");
    host.appendChild(wrap);
    var W = Math.max(300, wrap.clientWidth || 640), rowH = 26;
    var m = { l: Math.min(190, W * 0.42), r: 20, t: 8, b: 34 };
    var H = rows.length * rowH + m.t + m.b, iw = W - m.l - m.r;
    var fx = function (v) { return m.l + (Math.min(Math.max(v, opts.min), opts.max) - opts.min) / (opts.max - opts.min) * iw; };
    var svg = el("svg", { viewBox: "0 0 " + W + " " + H, width: "100%", role: "img", "aria-label": opts.title || "" }, wrap);
    var g = el("g", { class: "grid" }, svg);
    niceTicks(opts.min, opts.max, Math.max(3, Math.floor(iw / 80))).forEach(function (t) {
      el("line", { x1: fx(t), x2: fx(t), y1: m.t, y2: H - m.b }, g);
      var tx = el("text", { x: fx(t), y: H - m.b + 18, "text-anchor": "middle", class: "tick" }, g);
      tx.textContent = opts.fmt(t);
    });
    if (opts.ref != null) {
      el("line", { x1: fx(opts.ref), x2: fx(opts.ref), y1: m.t, y2: H - m.b, class: "ref" }, svg);
      if (opts.refLabel) {
        var rl = el("text", { x: fx(opts.ref) - 6, y: m.t + 10, "text-anchor": "end", class: "tick ref-label" }, svg);
        rl.textContent = opts.refLabel;
      }
    }
    var tip = html("div", "chart-tip"); tip.hidden = true; wrap.appendChild(tip);
    rows.forEach(function (r, i) {
      var y = m.t + i * rowH + rowH / 2;
      var lab = el("text", { x: m.l - 10, y: y + 4, "text-anchor": "end", class: "bar-label" }, svg);
      lab.textContent = r.label;
      el("line", { x1: fx(r.lo), x2: fx(r.hi), y1: y, y2: y, class: "whisker " + r.cls }, svg);
      el("circle", { cx: fx(r.v), cy: y, r: 4.5, class: "dot " + r.cls }, svg);
      var hit = el("rect", { x: m.l, y: y - rowH / 2, width: iw, height: rowH, class: "hit", tabindex: 0 }, svg);
      var show = function () {
        tip.innerHTML = "";
        tip.appendChild(html("div", "tip-x", r.label));
        var row = html("div", "tip-row");
        row.appendChild(html("span", "tip-l", opts.tipLabel || "Estimate"));
        row.appendChild(html("strong", null, opts.fmt1(r.v) + "  (" + opts.fmt1(r.lo) + "–" + opts.fmt1(r.hi) + ")"));
        tip.appendChild(row);
        if (r.note) tip.appendChild(html("div", "tip-note", r.note));
        tip.hidden = false;
        tip.style.left = Math.min(Math.max(fx(r.v) / W * wrap.clientWidth - tip.offsetWidth / 2, 0), wrap.clientWidth - tip.offsetWidth) + "px";
        tip.style.top = (y / H * wrap.clientHeight + 14) + "px";
      };
      hit.addEventListener("pointerenter", show);
      hit.addEventListener("focus", show);
      hit.addEventListener("pointerleave", function () { tip.hidden = true; });
      hit.addEventListener("blur", function () { tip.hidden = true; });
    });
  }


  // ── Dumbbell chart: two values per row (e.g., men vs women) ──
  // rows: [{label, a, b}], opts: {min, max, fmt, aCls, bCls, aLabel, bLabel}
  function dumbbell(host, rows, opts) {
    host.innerHTML = "";
    var wrap = html("div", "chart-wrap");
    host.appendChild(wrap);
    var W = Math.max(300, wrap.clientWidth || 640), rowH = 26;
    var m = { l: Math.min(190, W * 0.42), r: 20, t: 8, b: 34 };
    var H = rows.length * rowH + m.t + m.b, iw = W - m.l - m.r;
    var fx = function (v) { return m.l + (v - opts.min) / (opts.max - opts.min) * iw; };
    var svg = el("svg", { viewBox: "0 0 " + W + " " + H, width: "100%", role: "img", "aria-label": opts.title || "" }, wrap);
    var g = el("g", { class: "grid" }, svg);
    niceTicks(opts.min, opts.max, Math.max(3, Math.floor(iw / 80))).forEach(function (t) {
      el("line", { x1: fx(t), x2: fx(t), y1: m.t, y2: H - m.b, class: t === 0 ? "zero" : "" }, g);
      var tx = el("text", { x: fx(t), y: H - m.b + 18, "text-anchor": "middle", class: "tick" }, g);
      tx.textContent = opts.fmt(t);
    });
    var tip = html("div", "chart-tip"); tip.hidden = true; wrap.appendChild(tip);
    rows.forEach(function (r, i) {
      var y = m.t + i * rowH + rowH / 2;
      var lab = el("text", { x: m.l - 10, y: y + 4, "text-anchor": "end", class: "bar-label" }, svg);
      lab.textContent = r.label;
      el("line", { x1: fx(r.a), x2: fx(r.b), y1: y, y2: y, class: "connector" }, svg);
      el("circle", { cx: fx(r.a), cy: y, r: 4.5, class: "dot " + opts.aCls }, svg);
      el("circle", { cx: fx(r.b), cy: y, r: 4.5, class: "dot " + opts.bCls }, svg);
      var hit = el("rect", { x: m.l, y: y - rowH / 2, width: iw, height: rowH, class: "hit", tabindex: 0 }, svg);
      var show = function () {
        tip.innerHTML = "";
        tip.appendChild(html("div", "tip-x", r.label));
        [[opts.aLabel, r.a, opts.aCls], [opts.bLabel, r.b, opts.bCls]].forEach(function (x) {
          var row = html("div", "tip-row");
          row.appendChild(html("span", "key " + x[2]));
          row.appendChild(html("span", "tip-l", x[0]));
          row.appendChild(html("strong", null, opts.fmt1(x[1])));
          tip.appendChild(row);
        });
        tip.hidden = false;
        tip.style.left = Math.min(Math.max(fx((r.a + r.b) / 2) / W * wrap.clientWidth - tip.offsetWidth / 2, 0), wrap.clientWidth - tip.offsetWidth) + "px";
        tip.style.top = (y / H * wrap.clientHeight + 14) + "px";
      };
      hit.addEventListener("pointerenter", show);
      hit.addEventListener("focus", show);
      hit.addEventListener("pointerleave", function () { tip.hidden = true; });
      hit.addEventListener("blur", function () { tip.hidden = true; });
    });
  }

  window.MHCharts = { lineChart: lineChart, barChart: barChart, dotChart: dotChart, dumbbell: dumbbell, table: table,
    pct: pct, pct1: pct1, compact: compact, el: el, html: html };
})();
