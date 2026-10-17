"""Generates strength.html using the shared layout from build.py."""
import json, sys
sys.argv = ["build.py"]
import os
__file_self__ = __file__
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "build.py"), encoding="utf-8").read().replace("Path(__file__)", "Path(__file_self__)"))

CODE = "https://github.com/Madaha83/matthewdhanson/tree/master/analysis/strength-gap"
OPL = "https://www.openpowerlifting.org"


def fig(cid, title, note, extra=""):
    return f"""<figure class="figure" aria-labelledby="{cid}-h">
  <figcaption><h3 id="{cid}-h">{title}</h3><p class="muted">{note}</p></figcaption>
  {extra}
  <div class="chart" id="c-{cid}"><p class="muted chart-loading">Loading chart&hellip;</p></div>
  <details class="table-view"><summary>Show the data as a table</summary><div id="t-{cid}"></div></details>
</figure>"""


def legend(*items):
    return '<ul class="legend">' + "".join(f'<li><span class="key {c}"></span>{t}</li>' for c, t in items) + "</ul>"


def toggle(name, opts):
    return ('<fieldset class="toggle"><legend class="visually-hidden">Choose a series</legend>' +
            "".join(f'<label class="chip"><input type="radio" name="{name}" value="{v}"{" checked" if i == 0 else ""}><span>{t}</span></label>'
                    for i, (v, t) in enumerate(opts)) + "</fieldset>")


D = json.load(open(SITE + "strength-data.json", encoding="utf-8"))
ml = D["ml"]
ds = D["depth_summary"]
pp = {p["year"]: p for p in D["participation"]}
growth_f = pp[2024]["women"] / pp[2000]["women"]
growth_m = pp[2024]["men"] / pp[2000]["men"]
cm = D["cell_model"]["coef"]
b_m = cm["logn"][0]; b_f = b_m + cm["female:logn"][0]
ten_m = (10 ** b_m - 1) * 100; ten_f = (10 ** b_f - 1) * 100
adj = {r["year"]: r for r in ml["adjusted_by_year"]}

summary_rows = "".join(
    f"<tr><th scope='row'>{label}</th><td>+{ds[k]*100:.1f} pts</td><td>{'&mdash;' if s is None else f'{s*100:.0f}%'}</td></tr>"
    for label, k, s in [("Top 10, as observed", "observed_top10", None),
                        ("Top 10, men sampled to women&rsquo;s field size", "matched_to_women_n", ds["share_matched_to_women_n"]),
                        ("Top 10, both sexes in fields of 400", "fixed_pool", ds["share_fixed_pool"]),
                        ("99th percentile (unaffected by field size)", "p99", ds["share_p99"]),
                        ("Median lifter", "median", None)])

strength = head("Did more competition close the strength gap? · Matthew D. Hanson, Ph.D.",
                "An analysis of 2.7 million powerlifting results: how women's strength grew relative to men's as competition expanded, using statistical models and machine learning.",
                "strength", '\n<script src="charts.js" defer></script>\n<script src="strength.js" defer></script>') + header("research") + f"""
<main id="main">
<article>
<section class="page-intro">
  <div class="wrap essay-head">
    <p class="eyebrow">Research showcase &middot; Data analysis</p>
    <h1>Did more competition close the strength gap?</h1>
    <p class="lede">Women&rsquo;s powerlifting has grown enormously over the past twenty years. I used 2.7 million competition results to ask whether women&rsquo;s strength grew faster than men&rsquo;s as the field expanded, and how much of today&rsquo;s gap reflects a historically thinner pool of competitors.</p>
    <p class="byline muted">Matthew D. Hanson &middot; October 2026 &middot; <a href="{CODE}">Code on GitHub</a></p>
  </div>
</section>

<div class="wrap essay">
  <aside class="findings" aria-labelledby="kf-h">
    <h2 id="kf-h" class="eyebrow">Key findings</h2>
    <ol>
      <li>Women&rsquo;s participation in drug-tested raw powerlifting grew about <strong>{growth_f:.0f}-fold</strong> from 2000 to 2024, versus {growth_m:.0f}-fold for men.</li>
      <li>The gap narrowed at every level. From 2012 to 2025, top-10 women went from <strong>{D['trend'][0]['top'][0]*100:.0f}% to {D['trend'][-1]['top'][0]*100:.0f}%</strong> of men&rsquo;s bodyweight-adjusted strength, and the median lifter from {D['trend'][0]['median'][0]*100:.0f}% to {D['trend'][-1]['median'][0]*100:.0f}%.</li>
      <li>Field size explains part of it: roughly <strong>a quarter to a half</strong> of the elite narrowing disappears when women and men are compared in equally sized fields.</li>
      <li>The rest looks like real improvement. Holding constant who competes, a machine-learning model still shows women gaining on men, and women improve faster early in their careers.</li>
      <li>None of this suggests the gap is closing entirely. At the elite level women remain at about <strong>75&ndash;78%</strong> of men under every method.</li>
    </ol>
  </aside>

  <section class="essay-section" aria-labelledby="s1">
    <h2 id="s1">The question</h2>
    <p>Men outperform women in absolute strength, largely because of physiological differences that emerge at puberty. But performance at the top of any sport also depends on how many people compete. A bigger pool produces more exceptional performers, and for decades far fewer women than men competed in strength sports.</p>
    <p>That raises a measurable question: <em>as women&rsquo;s participation caught up, did women&rsquo;s performance grow faster than men&rsquo;s, and how much of the remaining gap is about the size of the talent pool?</em></p>
  </section>

  <section class="essay-section" aria-labelledby="s2">
    <h2 id="s2">The data</h2>
    <p>I used the public <a href="{OPL}">OpenPowerlifting</a> database (updated October 9, 2026), which records full-meet results (squat, bench press, and deadlift) from federations worldwide. After cleaning, that is <strong>2.67 million results</strong>. The main analysis uses <strong>drug-tested, raw</strong> competition, with no supportive suits or bench shirts, which is the fairest like-for-like comparison. It covers {D['meta']['lifters_main']:,} lifters.</p>
    <p>Because men are heavier on average, I compare <strong>bodyweight-adjusted strength</strong>: a lifter&rsquo;s total divided by bodyweight to the 2/3 power, a standard scaling from muscle physiology. Among the strongest lifters, this exponent fits both sexes almost exactly. Each lifter counts once per year, using their best meet.</p>
  </section>

  {fig("participation", "Women&rsquo;s participation exploded", "Lifters per year in drug-tested raw powerlifting. The 2020 dip reflects pandemic cancellations.", legend(("s-women", "Women"), ("s-men", "Men")))}

  <section class="essay-section" aria-labelledby="s3">
    <h2 id="s3">The gap narrowed at every level</h2>
    <p>Women&rsquo;s share of lifters rose from {pp[2000]['women']/(pp[2000]['women']+pp[2000]['men'])*100:.0f}% in 2000 to {pp[2024]['women']/(pp[2024]['women']+pp[2024]['men'])*100:.0f}% in 2024. Over the same period, women&rsquo;s strength relative to men&rsquo;s rose among the very best, at the 99th percentile, and for the typical lifter. Raw lifting became the main stage for elite competitors around 2012, so I treat 2012&ndash;2025 as the primary window. Earlier raw results are thinner and less representative.</p>
  </section>

  {fig("gap", "Women&rsquo;s strength as a share of men&rsquo;s", "Bodyweight-adjusted. Shaded band: approximate 95% bootstrap interval.", toggle("gap-level", [("top", "Top 10"), ("p99", "99th percentile"), ("median", "Median")]))}

  <section class="essay-section" aria-labelledby="s4">
    <h2 id="s4">How much is just a bigger pool?</h2>
    <p>The top of a larger field is higher simply by chance: the best of 20,000 people beats the best of 500 even when both groups come from the same population. To separate that statistical effect from real change, I compared women and men drawn from <strong>equally sized pools</strong>, repeatedly sampling 400 lifters of each sex per year.</p>
  </section>

  {fig("depth", "Comparing equally sized fields", "Top-10 ratio as observed, and when both sexes are drawn from pools of 400 lifters.", legend(("s-men", "Observed"), ("s-ochre", "Equal fields")))}

  <div class="summary-wrap">
    <table class="summary-table">
      <caption>Change in the women-to-men ratio, 2012 to 2025, by method</caption>
      <thead><tr><th scope="col">Method</th><th scope="col">Change</th><th scope="col">Share of the observed top-10 change removed</th></tr></thead>
      <tbody>{summary_rows}</tbody>
    </table>
  </div>

  <section class="essay-section" aria-labelledby="s5">
    <h2 id="s5" class="visually-hidden">Field size across countries</h2>
    <p>Across methods, roughly <strong>a quarter to a half</strong> of the elite narrowing since 2012 is attributable to the women&rsquo;s field getting bigger. The rest persists even in equal-size comparisons.</p>
    <p>A model across {D['cell_model']['n_countries']} countries (country fixed effects and separate year effects for each sex) points the same way. Elite performance rises with field size for both sexes, but about <strong>twice as steeply for women</strong>: each tenfold increase in field size goes with roughly {ten_f:.0f}% higher elite strength for women versus {ten_m:.0f}% for men. That fits a growing pool drawing in talented women who previously would never have competed. Field size isn&rsquo;t randomly assigned, though, so this is an association, not proof of cause.</p>
  </section>

  <section class="essay-section" aria-labelledby="s6">
    <h2 id="s6">Women improve faster early on</h2>
    <p>Following {D['careers']['lifters']:,} lifters who started between 2012 and 2020 and competed at least three times, a mixed-effects growth model shows women gaining strength proportionally faster in their first years. A likely reason is more room to grow, since many women arrive with less prior strength training.</p>
  </section>

  {fig("careers", "Strength gain since first meet", "Mixed-effects growth model, adjusted for starting age. Percent change from each sex&rsquo;s own starting level.", legend(("s-women", "Women"), ("s-men", "Men")))}

  <section class="essay-section" aria-labelledby="s7">
    <h2 id="s7">Machine learning: is it just who&rsquo;s competing?</h2>
    <p>As the sport grew, the mix of lifters changed: more novices, different ages and bodyweights, more countries. To check that the narrowing isn&rsquo;t simply a change in who competes, I trained gradient-boosted tree models on {ml['n_train']:,} lifter-years and tested them on {ml['n_test']:,} results from lifters the models never saw.</p>
    <ul>
      <li>A typical-performance model explains <strong>{ml['mean_model']['r2']*100:.0f}%</strong> of the variation in held-out lifters&rsquo; strength, versus {ml['baseline_r2']*100:.0f}% from sex, age, and bodyweight alone.</li>
      <li>An elite model, trained to predict the 95th percentile, is well calibrated: {ml['elite_model']['coverage']*100:.1f}% of held-out results fall below its predictions, against a 95% target.</li>
    </ul>
    <p>I then took each sex&rsquo;s actual lifters and changed only the calendar year, asking the models what the same people would be predicted to lift in 2012 versus 2025. The gap still narrows, from {adj[2012]['elite']*100:.1f}% to {adj[2025]['elite']*100:.1f}% for elite performance and from {adj[2012]['typical']*100:.1f}% to {adj[2025]['typical']*100:.1f}% for typical performance, so a changing mix of lifters doesn&rsquo;t explain it away.</p>
  </section>

  {fig("adjusted", "Holding the lifters constant", "Model-predicted women-to-men ratio when only the year changes.", toggle("adj-level", [("elite", "Elite (95th percentile)"), ("typical", "Typical")]))}

  {fig("importance", "What the model relies on", "Drop in explained variance (R&sup2;) when each group of inputs is shuffled. Related inputs are shuffled together, so sex and bodyweight share credit instead of splitting it.")}

  <section class="essay-section" aria-labelledby="s8">
    <h2 id="s8">The longer view</h2>
    <p>Drug-tested equipped lifting has records back to the 1980s. There, the top-10 ratio rose from about 69% in 1990 to 79% in 2025, the same direction over a much longer span. The pattern also holds in untested federations and when wrist wraps are excluded.</p>
  </section>

  {fig("robust", "Top-10 ratio by division", "Years with at least 50 lifters of each sex.", '<p class="select-row"><label for="rob-div">Division</label> <select id="rob-div"></select></p>')}

  <section class="essay-section" aria-labelledby="s9">
    <h2 id="s9">What it means</h2>
    <p>The answer to the original question is <strong>yes, partly</strong>. Women&rsquo;s strength has grown faster than men&rsquo;s as competition expanded, and the historically smaller pool of women competitors did make the measured gap look larger than it otherwise would have. But field size accounts for only part of the narrowing, and even in equal comparisons a substantial gap remains. Most of today&rsquo;s gap among elite lifters is not a participation artifact.</p>
    <p>For people who study performance and talent, the broader lesson is about measurement: comparisons between groups are only fair when the groups had comparable opportunity to produce their best performers. That applies to selection systems and leadership pipelines as much as to sport.</p>
  </section>

  <section class="essay-section methods" aria-labelledby="s10">
    <h2 id="s10">Methods &amp; limitations</h2>
    <p><strong>Pipeline.</strong> Python (pandas, statsmodels, scikit-learn, SHAP), in five scripts: data preparation, exploration, statistical models, machine learning, and export. Code is on <a href="{CODE}">GitHub</a>; the raw data is public from OpenPowerlifting. An independent methods review checked the analysis, and two estimates that proved unstable were dropped.</p>
    <p><strong>Limitations.</strong> These are observational competition records, not samples of underlying ability. Raw drug-tested lifting grew alongside a shift away from equipped lifting, so early-year elites under-represent the strongest lifters. &ldquo;Drug-tested&rdquo; is a federation label, not individual testing. The 2/3 bodyweight scaling fits elite lifters of both sexes but changes the gap&rsquo;s level, though not its trend. Field size is not randomly assigned, and within one country it rises almost in step with time, which limits how cleanly field depth can be separated from general improvement. Career analyses include only lifters who kept competing. Bootstrap intervals for extreme statistics are approximate. Machine-learning importance describes the model&rsquo;s predictions, not causes. Estimates of the share due to field size vary by method and should be read as indicative.</p>
  </section>
</div>
</article>
</main>
""" + FOOTER
write("strength.html", strength)
