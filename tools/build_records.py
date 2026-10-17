"""Generates records.html using the shared layout from build.py."""
import json, sys
sys.argv = ["build.py"]
import os
__file_self__ = __file__
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "build.py"), encoding="utf-8").read().replace("Path(__file__)", "Path(__file_self__)"))

CODE = "https://github.com/Madaha83/matthewdhanson/tree/master/analysis/records-gap"


def fig(cid, title, note, extra=""):
    return f"""<figure class="figure" aria-labelledby="{cid}-h">
  <figcaption><h3 id="{cid}-h">{title}</h3><p class="muted">{note}</p></figcaption>
  {extra}
  <div class="chart" id="c-{cid}"><p class="muted chart-loading">Loading chart&hellip;</p></div>
  <details class="table-view"><summary>Show the data as a table</summary><div id="t-{cid}"></div></details>
</figure>"""


def legend(*items):
    return '<ul class="legend">' + "".join(f'<li><span class="key {c}"></span>{t}</li>' for c, t in items) + "</ul>"


D = json.load(open(SITE + "records-data.json", encoding="utf-8"))
E = {e["event"]: e for e in D["events"]}
P = D["pooled"]
ident = [e for e in D["events"] if e["identified"]]
below = [e for e in ident if e["plateau_ci"][1] < 1]
now = [e["ratio_now"] for e in D["events"]]
flat = sum(e["slope_20y_per_decade"] <= 0.001 for e in D["events"])
sw = [e for e in D["events"] if e["sport"] == "swimming"]
sw_m = sum(e["gain_2000_m"] for e in sw) / len(sw) * 100
sw_w = sum(e["gain_2000_w"] for e in sw) / len(sw) * 100
mar = E["Marathon"]
maj = D["majors"]["by_year"]
maj_8589 = sum(r[1] for r in maj if 1985 <= r[0] <= 1989) / len([r for r in maj if 1985 <= r[0] <= 1989])
maj_20 = sum(r[1] for r in maj if r[0] >= 2020) / len([r for r in maj if r[0] >= 2020])
lo95, hi95 = round(3 * P["tau_ci"][0]), round(3 * P["tau_ci"][1])

page = head("Do women’s records catch up? · Matthew D. Hanson, Ph.D.",
            "World-record histories in 28 running, jumping, and swimming events: how fast the gap between women and men closed once women could compete, and where it levels off.",
            "records", '\n<script src="charts.js" defer></script>\n<script src="records.js" defer></script>') + header("research") + f"""
<main id="main">
<article>
<section class="page-intro">
  <div class="wrap essay-head">
    <p class="eyebrow">Research showcase &middot; Data analysis</p>
    <h1>Do women&rsquo;s records catch up?</h1>
    <p class="lede">Men have competed in organized sport for much longer than women. If part of today&rsquo;s performance gap is a head start, the gap should shrink as women accumulate competitive history. I traced world-record histories in 28 events to see how fast it closed, and whether it is still closing.</p>
    <p class="byline muted">Matthew D. Hanson &middot; October 2026 &middot; Companion to <a href="strength.html">Did more competition close the strength gap?</a> &middot; <a href="{CODE}">Code on GitHub</a></p>
  </div>
</section>

<div class="wrap essay">
  <aside class="findings" aria-labelledby="kf-h">
    <h2 id="kf-h" class="eyebrow">Key findings</h2>
    <ol>
      <li><strong>The head start was real.</strong> Once women could compete, gaps closed fast. In the marathon, women&rsquo;s record went from 62% of men&rsquo;s speed in 1963 to 90% by 1985.</li>
      <li><strong>Then it levelled off.</strong> In events with a measurable curve, most of the catch-up happened within roughly <strong>{lo95}&ndash;{hi95} years</strong> of women gaining real access, and in {len(below)} of {len(ident)} the plateau sits clearly below parity.</li>
      <li>Across 28 events with identical rules for men and women, women&rsquo;s world records today are <strong>{min(now)*100:.0f}&ndash;{max(now)*100:.0f}%</strong> of men&rsquo;s. None has passed 95%.</li>
      <li>In swimming, both sexes&rsquo; records improved by about <strong>4%</strong> since 2000 and the ratio barely moved, so extra competitive history is no longer narrowing the elite gap there.</li>
      <li>A famous 1992 projection put marathon parity in the late 1990s. Re-running it gives <strong>{D['whipp_ward']['projected_parity_year']}</strong>. In 2026 the women&rsquo;s record is still {mar['ratio_now']*100:.0f}% of the men&rsquo;s.</li>
    </ol>
  </aside>

  <section class="essay-section" aria-labelledby="s1">
    <h2 id="s1">The question</h2>
    <p>Elite men run faster, jump higher, and swim faster than elite women. Much of that difference is biological, but not necessarily all of it. Men&rsquo;s events have had decades or centuries more competition, coaching, money, and talent development. If that head start matters, two things should show up in the data:</p>
    <ul>
      <li>Gaps should <strong>shrink</strong> as women&rsquo;s events mature.</li>
      <li>Where they stop shrinking tells us how much of the gap the head start explained, and how long catching up takes.</li>
    </ul>
  </section>

  <section class="essay-section" aria-labelledby="s2">
    <h2 id="s2">The data</h2>
    <p>I collected world-record progressions for 28 events where men and women compete under identical conditions: flat running from 100&nbsp;m to the marathon, the high, long, and triple jumps, the pole vault, and long-course swimming. Hurdles, steeplechase, and throws were excluded because barrier heights or implement weights differ. For every year, I took each sex&rsquo;s standing world record and computed women&rsquo;s performance as a share of men&rsquo;s (speed for races, distance or height for jumps). Records later rescinded or never ratified were removed. Tables come from Wikipedia&rsquo;s record-progression articles (CC BY-SA), along with winners of the five oldest World Marathon Majors.</p>
  </section>

  <section class="essay-section" aria-labelledby="s3">
    <h2 id="s3">The marathon: a late start, a fast catch-up, a plateau</h2>
    <p>Women were effectively shut out of the marathon for decades. Boston admitted women in 1972, and the Olympics added a women&rsquo;s marathon only in 1984. The women&rsquo;s record barely moved from 1926 until the 1960s. Then, as women gained access, it fell by more than an hour in two decades.</p>
    <p>In 1992, two physiologists extrapolated that steep stretch in a straight line and predicted women would match men by 1998. Re-running the same approach on data through 1992 gives {D['whipp_ward']['projected_parity_year']}. Instead, the ratio levelled off at about 90% by the mid-1980s and has moved only a couple of points since.</p>
  </section>

  {fig("marathon", "Women&rsquo;s marathon record as a share of men&rsquo;s", "Standing world records each year (mixed races). The dashed line is a straight-line projection fitted to 1963&ndash;1992; the gray curve is the catch-up model.", legend(("s-men", "World records"), ("s-ref", "Catch-up model"), ("s-ochre", "1992-style projection")))}

  <section class="essay-section" aria-labelledby="s4">
    <h2 id="s4">Every event, same shape</h2>
    <p>For each event I fitted a <strong>catch-up curve</strong>: the ratio stays flat until an <em>onset</em> year when women&rsquo;s competition takes off, rises quickly, then approaches a plateau. The model estimates the onset, the plateau, and how fast the gap closes. Pick any event below to see its history.</p>
  </section>

  {fig("event", "One event at a time", "Standing world records each year, with the fitted catch-up curve.", '<p class="select-row"><label for="ev-select">Event</label> <select id="ev-select"></select></p>' + legend(("s-men", "World records"), ("s-ref", "Catch-up model")) + '<p class="ev-summary" id="ev-summary" aria-live="polite"></p>')}

  <section class="essay-section" aria-labelledby="s5">
    <h2 id="s5">How long does catching up take?</h2>
    <p>The curve could be estimated reliably in {len(ident)} events; the rest changed in too few large steps to fit. Across those {len(ident)}, the typical catch-up time constant is about <strong>{P['tau']:.0f} years</strong> (95% interval {P['tau_ci'][0]:.0f}&ndash;{P['tau_ci'][1]:.0f}). That means most of the rise toward each event&rsquo;s plateau played out within roughly <strong>{lo95}&ndash;{hi95} years</strong> of serious women&rsquo;s competition beginning. Some events moved much faster: the women&rsquo;s triple jump and pole vault, added in the 1990s, caught up within about fifteen years, helped by coaching and training knowledge that already existed.</p>
  </section>

  {fig("window", "When each catch-up began, and roughly when it was 95% complete", "Dot: estimated onset year. Line: onset to 95% of the way to that event&rsquo;s own plateau.", legend(("s-ochre", "Athletics"), ("s-men", "Swimming")))}

  <section class="essay-section" aria-labelledby="s6">
    <h2 id="s6">Where does the gap settle?</h2>
    <p>Every estimated plateau sits well short of parity, between about 82% (pole vault) and 94% (distance freestyle swimming). Women come closest in long-distance swimming, and the gap is widest in events that depend most on explosive power, like the jumps and vault. The intervals are approximate, because world records change in a few large steps, but in {len(below)} of {len(ident)} events even the upper end of the interval stays below 100%. Across all 28 events, {flat} show flat or falling ratios over the last 20 years.</p>
  </section>

  {fig("plateau", "Estimated plateau of the women-to-men record ratio", "Dot: estimate. Line: approximate 95% interval. Events whose curve couldn&rsquo;t be estimated are left out.", legend(("s-ochre", "Athletics"), ("s-men", "Swimming")))}

  <section class="essay-section" aria-labelledby="s7">
    <h2 id="s7">Is it a plateau, or are records just frozen?</h2>
    <p>A flat ratio could mean women have stopped catching up, or just that records stopped falling. Several women&rsquo;s sprint, 800&nbsp;m, 3000&nbsp;m, and long-jump records have stood since the 1980s, an era of state-sponsored doping, so those ratios are flat because one record is frozen. Swimming is the cleaner test. Since 2000, both sexes&rsquo; records improved by almost exactly the same amount (about {sw_m:.1f}% for men and {sw_w:.1f}% for women on average), so the ratio held steady while both kept getting faster. In distance running, women have gained somewhat more than men since 2000, which is consistent with women&rsquo;s distance running still deepening.</p>
  </section>

  {fig("gains", "Improvement in the world record since 2000", "Percent faster (or farther) than the record standing in 2000.", legend(("s-men", "Men"), ("s-women", "Women")))}

  <section class="essay-section" aria-labelledby="s8">
    <h2 id="s8">Beyond single records</h2>
    <p>World records capture one extraordinary performance at a time. Race winners give a second view: across the Boston, New York, Chicago, London, and Berlin marathons, the women&rsquo;s winning time averaged {maj_8589*100:.1f}% of the men&rsquo;s speed in the late 1980s and {maj_20*100:.1f}% since 2020. That is a slow drift of about half a percentage point per decade, far smaller than the early catch-up. Below the elite level, where participation still differs most, the companion <a href="strength.html">powerlifting analysis</a> found that a growing pool of competitors explains a meaningful part of the narrowing.</p>
  </section>

  {fig("majors", "Women&rsquo;s winning time as a share of men&rsquo;s, World Marathon Majors", "Average across the majors held each year (speed ratio).")}

  <section class="essay-section" aria-labelledby="s9">
    <h2 id="s9">So how long until women compete with men?</h2>
    <p>On the evidence here: <strong>not on any trajectory we can observe.</strong> The opportunity effect was large. Gaining access moved women&rsquo;s records by 20 to 30 percentage points relative to men&rsquo;s, far more than anything since. But in event after event, the gap stops shrinking a few decades after women gain real access, and it settles 6 to 20 percent short of parity. Straight-line trends from recent decades do point to parity in some events, but only centuries from now, and that is exactly the kind of extrapolation that failed for the marathon.</p>
    <p>That doesn&rsquo;t mean culture is irrelevant. Access, coaching, investment, and participation clearly shaped how quickly women reached the plateau, and they still matter for depth of competition below the very top. But at the elite level, the remaining gap looks stable, consistent with physiological differences that more competitive history alone doesn&rsquo;t erase.</p>
  </section>

  <section class="essay-section methods" aria-labelledby="s10">
    <h2 id="s10">Methods &amp; limitations</h2>
    <p><strong>Pipeline.</strong> Python (pandas, SciPy). Record tables were parsed from cached Wikipedia pages. Rows marked as rescinded, unratified, or pending were removed. For each year, the standing record is the best mark to date. The catch-up model has a flat level until an onset year, then an exponential approach to a plateau. The onset is found by grid search, and the other parameters by least squares. Uncertainty comes from a moving-block bootstrap (18-year blocks). The shared time constant takes each event&rsquo;s onset year as given. Events whose time constant could not be pinned down were left out of the summaries. An independent methods review checked the data and models; its corrections are included. Code is on <a href="{CODE}">GitHub</a>.</p>
    <p><strong>Limitations.</strong> World records are single extreme performances, shaped by individual outliers, doping eras, equipment changes (swimsuits in 2008&ndash;09, running shoes after 2017), and pacing. So some flat ratios reflect a frozen record rather than a limit. The marathon series uses mixed-race records; women-only races give a lower ratio (about 88%). The current women&rsquo;s marathon record holder later received a doping ban based on a separate sample, and the record still stands. Early timing mixed hand and automatic methods. Records change in a few large steps, so curve fits are descriptive and intervals approximate. &ldquo;Years since women&rsquo;s competition began&rdquo; stands in for opportunity and is entangled with professionalization, policy, and investment, none of which is measured directly. The data come from Wikipedia and should be checked against World Athletics and World Aquatics for formal research.</p>
  </section>
</div>
</article>
</main>
""" + FOOTER
write("records.html", page)
