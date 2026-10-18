"""Generator for matthewdhanson.com pages (index, research, publications, cv).
Run: python tools/build.py   (then tools/build_strength.py and tools/build_records.py)
Output is plain HTML in the site folder."""
import html, re, json, datetime

from pathlib import Path
SITE = str(Path(__file__).resolve().parents[1] / "OneDrive" / "Documents" / "Personal" / "Personal Website" / "personal-site") + "/"
URL = "https://matthewdhanson.com"
EMAIL = "matthew.hanson@uri.edu"
SCHOLAR = "https://scholar.google.com/citations?user=Q8gXnk0AAAAJ&hl=en"
LINKEDIN = "https://www.linkedin.com/in/matthew-hanson-phd-83102324"
EVERGREEN = "https://evergreenassessments.com"
UPDATED = "October 2026"
YEAR = 2026

NAV = [("index.html", "About", "home"), ("research.html", "Research", "research"),
       ("publications.html", "Publications", "publications"), ("cv.html", "CV", "cv"),
       ("index.html#contact", "Contact", "contact")]


def head(title, desc, path, extra=""):
    canonical = URL + ("/" if path == "" else "/" + path)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="{"profile" if path == "" else "website"}">
<meta property="og:site_name" content="Matthew D. Hanson, Ph.D.">
<meta property="og:image:alt" content="Matthew D. Hanson, Ph.D., industrial-organizational psychologist">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{URL}/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image:alt" content="Matthew D. Hanson, Ph.D., industrial-organizational psychologist">
<meta name="theme-color" content="#FAF6EE" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#12161D" media="(prefers-color-scheme: dark)">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Sans:ital,wght@0,400;0,500;0,600;1,400&family=Newsreader:ital,opsz,wght@0,6..72,400..600;1,6..72,400&display=swap">
<link rel="stylesheet" href="style.css">
<script src="site.js"></script>
<!-- Privacy-friendly analytics by Plausible (setup line lives in site.js) -->
<script async src="https://plausible.io/js/pa-MYBDO4ji5DJVwsf6XDhP9.js"></script>{extra}
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
"""


def header(active):
    items = []
    for href, label, key in NAV:
        cur = ' aria-current="page"' if key == active else ""
        items.append(f'<li><a href="{href}"{cur}>{label}</a></li>')
    return f"""<header class="site-header">
  <div class="wrap">
    <a class="wordmark" href="index.html">Matthew D. Hanson<span class="phd">, Ph.D.</span></a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button>
    <nav class="site-nav" id="site-nav" aria-label="Primary">
      <ul>
        {chr(10).join('        ' + i for i in items).strip()}
      </ul>
    </nav>
  </div>
</header>
"""


FOOTER = f"""<footer class="site-footer">
  <div class="wrap">
    <p class="disclaimer">This is a personal website. Views expressed here are my own and do not represent the University of Rhode Island. Descriptions of my earlier work with the U.S. Army and U.S. Navy do not imply their endorsement. Evergreen Assessments LLC is a private business, separate from my university role.</p>
    <ul>
      <li><a href="{SCHOLAR}">Google Scholar</a></li>
      <li><a href="{LINKEDIN}">LinkedIn</a></li>
      <li><a href="mailto:{EMAIL}">Email</a></li>
    </ul>
    <p>&copy; {YEAR} Matthew D. Hanson &middot; Updated {UPDATED}</p>
  </div>
</footer>
</body>
</html>
"""


def contact_band():
    return f"""<section class="contact-band" id="contact" aria-labelledby="contact-h">
  <div class="wrap">
    <div>
      <p class="eyebrow">Contact</p>
      <h2 id="contact-h">Let&rsquo;s talk about measurement, learning, or leadership.</h2>
      <p class="lead">I&rsquo;m especially interested in collaborating on mindfulness and self-regulation in training, need satisfaction and recovery, and validity and fairness in leadership assessment, including field studies with Rhode Island organizations. URI students and HR practitioners are welcome to write too. Email is the best way to reach me.</p>
    </div>
    <dl class="contact-list">
      <div><dt>Email</dt><dd><a class="big" href="mailto:{EMAIL}">{EMAIL}</a></dd></div>
      <div><dt>Faculty</dt><dd>College of Business, University of Rhode Island<br>Kingston, RI</dd></div>
      <div><dt>Students</dt><dd>Interested in the ANCHOR Lab? Email me about joining through MGT 491.</dd></div>
      <div><dt>Profiles</dt><dd><a href="{SCHOLAR}">Google Scholar</a> &middot; <a href="{LINKEDIN}">LinkedIn</a></dd></div>
    </dl>
  </div>
</section>
"""


# ───────────────────────── Publications data (from April 2026 CV) ─────────────────────────
ME = re.compile(r"Hanson, M\.(?: D\.)?")

ARTICLES = [
    dict(year=2025, authors="Randall, J. G., Zajac, S. A., & Hanson, M. D.", title="Mindful training: Integrating mindfulness into workplace learning",
         venue="Human Resource Development Review", details="Advance online publication", doi="10.1177/15344843251395914"),
    dict(year=2022, authors="Randall, J. G., Hanson, M. D., & Nassrelgrgawi, A. S.", title="Staying focused when nobody is watching: Self-regulatory strategies to reduce mind wandering during self-directed learning",
         venue="Applied Psychology: An International Review", details="71(4), 1428&ndash;1464", doi="10.1111/apps.12366"),
    dict(year=2020, authors="Ulatowska, J., Olszewska, J., & Hanson, M. D.", title="Does test type influence false recognition in the DRM paradigm? Comparison of the yes/no recognition test and two-alternative forced-choice test",
         venue="American Journal of Psychology", details="133(1), 49&ndash;62", doi="10.5406/amerjpsyc.133.1.0049"),
    dict(year=2020, authors="Steinert, S. W., Hanson, M. D., Weiss, N., Berg, J. V., Hong, P. Y., & Lancaster, R.", title="A critical analysis of student nurses&rsquo; knowledge and use of the American Psychological Association&rsquo;s Publication Manual",
         venue="TNNMC Journal of Nursing Education and Administration", details="8(1), 31&ndash;39"),
    dict(year=2019, authors="Lee, S. Y., Hanson, M. D., & Cheung, H. K.", title="Incorporating bystander intervention into sexual harassment training",
         venue="Industrial and Organizational Psychology", details="12(1), 52&ndash;57", doi="10.1017/iop.2019.8"),
    dict(year=2018, authors="Hong, P. Y., Hanson, M. D., Lishner, D. A., Kelso, S. L., & Steinert, S. W.", title="A field experiment examining mindfulness on eating enjoyment and behavior in children",
         venue="Mindfulness", details="9(6), 1748&ndash;1756", doi="10.1007/s12671-018-0916-1"),
    dict(year=2018, authors="Atherton, R. P., Chrobak, Q. M., Rauscher, F. H., Karst, A. T., Hanson, M. D., Steinert, S. W., & Bowe, K. L.", title="Shared processing of language and music: Evidence from a cross-modal interference paradigm",
         venue="Experimental Psychology", details="65(1), 40&ndash;48", doi="10.1027/1618-3169/a000388"),
    dict(year=2016, authors="Ulatowska, J., Olszewska, J., & Hanson, M. D.", title="Do format differences in the presentation of information affect susceptibility to memory distortions? The three-stage misinformation procedure reconsidered",
         venue="American Journal of Psychology", details="129(4), 407&ndash;417", doi="10.5406/amerjpsyc.129.4.0407"),
]
CHAPTERS = [
    dict(year=2020, authors="Hanson, M. D., Randall, J. G., Danna, G. C., & Le, H. Q.", title="Enhancing workplace learning through mindfulness",
         venue="The Routledge Companion to Mindfulness at Work", pre="In S. K. Dhiman (Ed.), ", details="Routledge"),
]
REPORTS = [
    dict(year=2023, authors="Bizarro, A., Dilweg, D., Hernandez, D., Hanson, M. D., & Louie, J.", title="Development of a leadership competency model for submarine command triads",
         venue="Defense Technical Information Center", details="Publication No. AD1217151", url="https://apps.dtic.mil/sti/citations/AD1217151"),
    dict(year=2022, authors="Bizarro, A., Hernandez, D., Hanson, M. D., Peltier, C., & Handy, J.", title="Development of the Submarine Environment Fit (SUBFIT) Assessment: Psychometric review and comparison of enlisted and officer trainees",
         venue="Defense Technical Information Center", details="Publication No. AD1183611", url="https://apps.dtic.mil/sti/citations/AD1183611"),
]
REVIEW = [
    dict(authors="Hanson, M. D., Randall, J. G., & Banfi, J. T.", title="Practice, label, or placebo? An experimental test of mindfulness effects in organizational training"),
    dict(authors="Hanson, M. D., Randall, J. G., & Banfi, J. T.", title="Basic psychological need satisfaction across life domains: Implications for work recovery and well-being"),
    dict(authors="Hanson, M. D., & Hong, P. Y.", title="Brief focused-attention and open-monitoring mindfulness meditation: A randomized controlled experiment on mindfulness, anxiety, affect, and attention"),
    dict(authors="Hong, P. Y., Hanson, M. D., Lishner, D. A., Kelso, S., & Steinert, S.", title="A randomized field experiment examining the effect of mindfulness on children&rsquo;s, parents&rsquo;, and teachers&rsquo; ratings of children&rsquo;s mood and behavior"),
]
TALKS = [
    dict(year=2024, authors="Clark, D., Hernandez, D., Dilweg, D., Hanson, M. D., & Bizarro, A.", title="Associations between submarine officer personality and operational outcomes", venue="Military Health System Research Symposium", details="Kissimmee, FL"),
    dict(year=2024, authors="Hernandez, D. B., Dilweg, D. R., & Hanson, M. D.", title="Building a competency model for Submarine Force leadership", venue="Office of Naval Research Manpower, Personnel, Training, and Education Program Review", details="Annapolis, MD"),
    dict(year=2024, authors="Hernandez, D., Dilweg, D., Hanson, M. D., & Clark, D. A.", title="SUBFOR research progress and results", venue="Office of Naval Research Manpower, Personnel, Training, and Education Annual Workshop", details="San Diego, CA"),
    dict(year=2023, authors="Hanson, M. D., Louie, J. F., Bizarro, A., Dilweg, D., Hernandez, D., & Clark, D. A.", title="Building a competency model for Submarine Force leadership", venue="Office of Naval Research Manpower, Personnel, Training, and Education Program Review", details="Arlington, VA"),
    dict(year=2021, authors="Hanson, M. D., Baranik, L. E., Smith, R. W., & Fan, L.", title="Development of the refugee job search stressor scale", venue="Academy of Management Annual Meeting", details="Symposium, virtual"),
    dict(year=2021, authors="Hanson, M. D., & Randall, J. G.", title="Training on purpose: Mindfulness in a training environment", venue="Society for Industrial and Organizational Psychology Annual Conference", details="Symposium co-chair and presenter"),
    dict(year=2021, authors="Baranik, L. E., Hanson, M. D., Mian, M., & Yeo, A.", title="Refugee Roundtable survey: Supporting economic stability", venue="Capital Region Refugee Roundtable", details="Albany, NY"),
    dict(year=2020, authors="Randall, J., Hanson, M. D., Neuburger, A., & Shaju, S.", title="Training evaluation efforts to help professionalize direct support professionals", venue="Society for Industrial and Organizational Psychology Annual Conference", details="Symposium"),
]
POSTERS = [
    dict(year=2024, authors="Handy, J., Clark, D. A., Hernandez, D. B., Hanson, M. D., Marshall, J., & Harris, E.", title="Non-clinical personality indices and stress coping behaviors predict attrition from the Navy nuclear training pipeline", venue="Military Health System Research Symposium", details="Kissimmee, FL"),
    dict(year=2022, authors="Handy, J., Bizarro, A., Clark, D. A., Hanson, M. D., Hernandez, D., & Smallidge, T.", title="Warrior toughness improves outcomes for enlisted sailors at Naval Nuclear Power Training Command", venue="Military Health System Research Symposium", details="Kissimmee, FL"),
    dict(year=2019, authors="Hanson, M. D., Randall, J. G., & Nassrelgrgawi, A. S.", title="Self-regulation interventions in a self-directed learning environment", venue="Society for Industrial and Organizational Psychology Annual Conference", details="National Harbor, MD"),
    dict(year=2019, authors="Randall, J. G., Hanson, M. D., Arredondo, M. L., & Jandrew, M.", title="Predicting self-regulation failures in training", venue="Society for Industrial and Organizational Psychology Annual Conference", details="National Harbor, MD"),
    dict(year=2017, authors="Zimmerman, C., Hong, P. Y., Lishner, D. A., Ebert, A., Hanson, M. D., Steinert, S., & Kelso, S.", title="Mindfulness, academic performance, and mood", venue="Society for Personality and Social Psychology Annual Convention", details="San Antonio, TX"),
    dict(year=2017, authors="Hong, P. Y., Zimmerman, C. N., Lishner, D. A., & Hanson, M. D.", title="Mindfulness and eating enjoyment and behavior in preschool children", venue="Society for Personality and Social Psychology Annual Convention", details="San Antonio, TX"),
    dict(year=2016, authors="Ebert, A., Hanson, M. D., Rapp, E., Wenzel, T., Bagley, A., & Hong, P. Y.", title="The effect of perceived child intelligence on public perception of hyper-parenting: A replication study", venue="Association for Psychological Science Annual Convention", details="Chicago, IL"),
    dict(year=2016, authors="Hanson, M. D., Ebert, A., Voskuil, T., Barbieri, A., Schlueter, A., Steinert, S. W., Kelso, S., Zimmerman, C., Hong, P. Y., & Lishner, D. A.", title="Anxiety, attention, and mindfulness following focused attention and open-monitoring mindfulness meditation", venue="International Conference on Mindfulness", details="Rome, Italy"),
    dict(year=2015, authors="Steinert, S., Hanson, M. D., Kelso, S., Lishner, D. A., Hong, P. Y., & Vitacco, M. J.", title="A replication of psychopathic callous affect as a predictor of empathic concern and positive affect toward those in need", venue="Association for Behavioral and Cognitive Therapies Annual Convention", details="Chicago, IL"),
    dict(year=2015, authors="Ebert, A., Kelso, S., Steinert, S., Hanson, M. D., Hong, P. Y., & Lishner, D. A.", title="An examination of the role of source credibility on invalidating messages on affect", venue="Association for Behavioral and Cognitive Therapies Annual Convention", details="Chicago, IL"),
    dict(year=2015, authors="Hanson, M. D., Steinert, S., Kelso, S., Ebert, A., Lishner, D. A., Hong, P. Y., & Vitacco, M. J.", title="Psychopathy and ability emotional intelligence: A re-analysis of Lishner, Swim, Hong, &amp; Vitacco (2011)", venue="American Psychological Association Annual Convention", details="Toronto, Canada"),
    dict(year=2015, authors="Miller, T., Pionk, T., Kelso, S., Steinert, S., Hanson, M. D., Lishner, D. A., Hong, P. Y., & Vitacco, M. J.", title="Psychopathic callous affect as a predictor of empathic concern and happiness toward those in need", venue="Midwestern Psychological Association Annual Meeting", details="Chicago, IL"),
]


def auth(a):
    a = a.replace("&", "&amp;").replace("&amp;amp;", "&amp;")
    return ME.sub(lambda m: f"<strong>{m.group(0)}</strong>", a, count=1)


def pub_li(p, status=None):
    link = None
    if p.get("doi"):
        link = "https://doi.org/" + p["doi"]
    elif p.get("url"):
        link = p["url"]
    title = f'<a href="{link}">{p["title"]}</a>' if link else p["title"]
    year = p.get("year", "")
    venue = ""
    if p.get("venue"):
        venue = f'{p.get("pre", "")}<cite>{p["venue"]}</cite>'
        if p.get("details"):
            venue += f', {p["details"]}'
    pill = f' <span class="pill">{status}</span>' if status else ""
    links = ""
    if p.get("doi"):
        links = f'<p class="links"><a href="{link}">DOI</a></p>'
    elif p.get("url"):
        links = f'<p class="links"><a href="{link}">Read on DTIC</a></p>'
    return f"""  <li class="pub">
    <span class="year"{"" if year else ' aria-hidden="true"'}>{year if year else "&mdash;"}</span>
    <div>
      <p class="title">{title}{pill}</p>
      <p class="authors">{auth(p["authors"])}</p>
      {f'<p class="venue">{venue}</p>' if venue else ''}
      {links}
    </div>
  </li>"""


def group(gid, gtype, label, items, status=None, collapse=False):
    lis = "\n".join(pub_li(p, status) for p in items)
    ul = f'<ol class="pub-list">\n{lis}\n</ol>'
    if collapse:
        ul = f'<details class="more-pubs"><summary>Show all {len(items)}</summary>\n{ul}\n</details>'
    return f"""<section class="pub-group" data-type="{gtype}" aria-labelledby="{gid}">
  <h2 id="{gid}">{label} <span class="count">{len(items)}<span class="visually-hidden"> items</span></span></h2>
  {ul}
</section>"""


def write(name, content):
    with open(SITE + name, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("wrote", name, len(content))


# ───────────────────────── Home ─────────────────────────
JSONLD = {
    "@context": "https://schema.org", "@type": "Person", "@id": URL + "/#person",
    "name": "Matthew D. Hanson", "honorificSuffix": "Ph.D.",
    "jobTitle": "Assistant Professor of Human Resource Management",
    "worksFor": {"@type": "CollegeOrUniversity", "name": "University of Rhode Island, College of Business", "url": "https://web.uri.edu/business/"},
    "description": "Industrial-organizational psychologist studying leadership assessment, workplace learning, and work motivation and well-being.",
    "url": URL + "/", "image": URL + "/headshot-960.jpg", "email": "mailto:" + EMAIL,
    "alumniOf": [{"@type": "CollegeOrUniversity", "name": "University at Albany, State University of New York"},
                 {"@type": "CollegeOrUniversity", "name": "University of Wisconsin Oshkosh"}],
    "knowsAbout": ["Industrial-organizational psychology", "Leadership assessment", "Psychometrics", "Training and development",
                   "Mindfulness", "Self-determination theory", "Work recovery", "Burnout"],
    "address": {"@type": "PostalAddress", "addressRegion": "RI", "addressCountry": "US"},
    "sameAs": [SCHOLAR, LINKEDIN],
}
jsonld = '\n<script type="application/ld+json">\n' + json.dumps(JSONLD, indent=1, ensure_ascii=False) + "\n</script>"

home = head("Matthew D. Hanson, Ph.D. · Industrial-Organizational Psychologist",
            "Matthew D. Hanson is an assistant professor of human resource management at the University of Rhode Island who studies how people learn, lead, and recover at work.",
            "", jsonld) + header("home") + f"""
<main id="main">

<section class="hero">
  <div class="wrap">
    <div>
      <p class="eyebrow rise">Assistant Professor &middot; University of Rhode Island</p>
      <h1 class="rise rise-2">Evidence for how people learn, lead, and recover at work.</h1>
      <p class="lede rise rise-3">I&rsquo;m Matthew Hanson, an industrial-organizational psychologist and assistant professor of human resource management in URI&rsquo;s College of Business. I build and validate leadership assessments, and I study how training design and psychological needs shape learning, motivation, and recovery at work.</p>
      <div class="btn-row rise rise-4">
        <a class="btn btn-primary" href="research.html">Explore my research</a>
        <a class="btn btn-secondary" href="matthew-hanson-cv.pdf">Download CV <span class="meta">PDF</span></a>
      </div>
    </div>
    <div class="portrait rise rise-3">
      <picture>
        <source type="image/webp" srcset="headshot-480.webp 480w, headshot-960.webp 960w" sizes="(min-width: 860px) 25rem, 18rem">
        <img src="headshot-960.jpg" srcset="headshot-480.jpg 480w, headshot-960.jpg 960w" sizes="(min-width: 860px) 25rem, 18rem"
             width="480" height="600" fetchpriority="high"
             alt="Matthew Hanson, smiling, wearing glasses and a blue shirt, seated at a table by a sunlit window">
      </picture>
    </div>
  </div>
</section>

<div class="wrap">
  <ul class="facts" aria-label="At a glance">
    <li><span class="k">Ph.D., I-O Psychology</span><span class="v">University at Albany, SUNY</span></li>
    <li><span class="k">8 journal articles</span><span class="v">plus a Routledge chapter and two DTIC reports</span></li>
    <li><span class="k">$395K in grants</span><span class="v">as co-investigator, Defense Health Program</span></li>
    <li><span class="k">Army &amp; Navy</span><span class="v">assessment research for leaders and submariners</span></li>
    <li><span class="k">Teaching</span><span class="v">Human resource management at URI</span></li>
  </ul>
</div>

<section class="section" aria-labelledby="about-h">
  <div class="wrap section-grid">
    <div class="section-label">
      <p class="eyebrow">About</p>
      <h2 id="about-h">Scientist-practitioner</h2>
    </div>
    <div class="prose">
      <p>I&rsquo;m the Fred &rsquo;78 and Sue Newton Assistant Professor of Human Resource Management in the University of Rhode Island&rsquo;s College of Business. I came to URI from applied research. At the U.S. Army&rsquo;s Center for the Army Profession and Leadership, I developed and validated leadership assessments and helped turn research into feedback leaders could use. Before that, I spent three years with Leidos at the Naval Submarine Medical Research Laboratory, building leadership competency models and studying what helps sailors succeed in the submarine training pipeline.</p>
      <p>My research asks three connected questions. How do we design training that actually helps people learn? How do we measure people accurately and fairly when decisions about their careers depend on it? And what do people need, at work and away from it, to stay motivated and recover? I earned my Ph.D. in industrial-organizational psychology at the University at Albany, SUNY, and my M.S. in experimental psychology at the University of Wisconsin Oshkosh.</p>
      <p>That background shapes how I research and teach: I design studies whose results organizations can act on, and I bring real assessment programs and workplace problems into the classroom. I live in Rhode Island with my family.</p>
    </div>
  </div>
</section>

<section class="section" id="uri" aria-labelledby="uri-h">
  <div class="wrap section-grid">
    <div class="section-label">
      <p class="eyebrow">University of Rhode Island</p>
      <h2 id="uri-h">At URI</h2>
      <p>College of Business &middot; since 2026</p>
    </div>
    <div>
      <p class="prose">I joined the University of Rhode Island&rsquo;s College of Business in August 2026 as the Fred &rsquo;78 and Sue Newton Assistant Professor of Human Resource Management. The role brings together the three things I care most about: research that improves how organizations select, develop, and support people; teaching the next generation of HR professionals and managers; and working with Rhode Island employers on the problems they actually face.</p>
      <div class="uri-grid">
        <article class="uri-item">
          <h3>The ANCHOR Lab</h3>
          <p>My research lab studies assessment, psychological needs, competencies, and resilience in people and organizations. URI students join through MGT 491 (Directed Study).</p>
          <a class="more" href="research.html#anchor">About the lab &rarr;</a>
        </article>
        <article class="uri-item">
          <h3>Teaching</h3>
          <p>MGT 342 Human Resource Management, LHR 500 / MBA 571 Labor Relations and Human Resources, and MGT 491 Directed Study, taught with real assessment programs and workplace decisions from my applied career.</p>
          <a class="more" href="cv.html#teaching">Teaching &rarr;</a>
        </article>
        <article class="uri-item">
          <h3>COB Behavioral Lab</h3>
          <p>I co-direct the College of Business Behavioral Lab in URI&rsquo;s Coastal Institute, which supports experimental and survey research across the college.</p>
        </article>
        <article class="uri-item">
          <h3>Partnerships</h3>
          <p>Interested in collaborating with Rhode Island organizations in defense, healthcare, manufacturing, and the public sector on selection, development, and well-being.</p>
          <a class="more" href="#contact">Get in touch &rarr;</a>
        </article>
      </div>
    </div>
  </div>
</section>

<section class="section" aria-labelledby="themes-h">
  <div class="wrap section-grid">
    <div class="section-label">
      <p class="eyebrow">Research</p>
      <h2 id="themes-h">What I study</h2>
      <p>Three connected lines of work, and one that&rsquo;s next.</p>
    </div>
    <div class="themes">
      <article class="theme">
        <span class="num">01</span>
        <h3>Training &amp; workplace learning</h3>
        <p class="q">When learning happens on a screen and nobody is watching, what keeps attention on the task?</p>
        <p>Experiments and theory on mindfulness, mind wandering, and self-regulation in training.</p>
        <a class="more" href="research.html#learning">More on this theme &rarr;</a>
      </article>
      <article class="theme">
        <span class="num">02</span>
        <h3>Assessment &amp; selection</h3>
        <p class="q">How do we know a leadership assessment measures something real, and treats people fairly?</p>
        <p>Competency models, validation studies, and assessments built for high-stakes settings.</p>
        <a class="more" href="research.html#assessment">More on this theme &rarr;</a>
      </article>
      <article class="theme">
        <span class="num">03</span>
        <h3>Motivation &amp; well-being</h3>
        <p class="q">Can a good life outside work make up for needs that go unmet at work?</p>
        <p>Self-determination theory applied to recovery, burnout, and sustained motivation.</p>
        <a class="more" href="research.html#motivation">More on this theme &rarr;</a>
      </article>
      <article class="theme">
        <span class="num">04</span>
        <h3>Next: AI-assisted assessment &amp; feedback</h3>
        <p class="q">Can conversational AI deliver developmental feedback that is both scalable and scientifically sound?</p>
        <p>Pairing large language models with validated assessment frameworks.</p>
        <a class="more" href="research.html#next">More on this theme &rarr;</a>
      </article>
    </div>
  </div>
</section>

<section class="section" aria-labelledby="feat-h">
  <div class="wrap section-grid">
    <div class="section-label">
      <p class="eyebrow">Featured analysis</p>
      <h2 id="feat-h">Research showcases</h2>
    </div>
    <div class="feature-stack">
    <a class="feature-card" href="strength.html">
      <p class="eyebrow">Data analysis &middot; 2.7 million results</p>
      <h3>Did more competition close the strength gap?</h3>
      <p>As women&rsquo;s powerlifting grew 280-fold, women gained on men at every level. How much of that is a bigger talent pool, and how much is real improvement? Statistical models and machine learning on two decades of competition data.</p>
      <span class="go">Read the analysis &rarr;</span>
    </a>
    <a class="feature-card" href="records.html">
      <p class="eyebrow">Data analysis &middot; 28 events, 100+ years of records</p>
      <h3>Do women&rsquo;s records catch up?</h3>
      <p>If men&rsquo;s head start in organized sport explains part of the performance gap, the gap should shrink as women&rsquo;s events mature. World-record histories show how fast it closed, and where it levels off.</p>
      <span class="go">Read the analysis &rarr;</span>
    </a>
    </div>
  </div>
</section>

<section class="section" aria-labelledby="sel-h">
  <div class="wrap section-grid">
    <div class="section-label">
      <p class="eyebrow">Publications</p>
      <h2 id="sel-h">Selected work</h2>
      <p><a href="publications.html">All publications &rarr;</a></p>
    </div>
    <div>
      <ol class="pub-list">
{pub_li(ARTICLES[0])}
{pub_li(REPORTS[0])}
{pub_li(ARTICLES[1])}
{pub_li(CHAPTERS[0])}
      </ol>
    </div>
  </div>
</section>

<section class="section" aria-labelledby="beyond-h">
  <div class="wrap section-grid">
    <div class="section-label">
      <p class="eyebrow">Beyond research</p>
      <h2 id="beyond-h">Evergreen Assessments</h2>
    </div>
    <div class="venture">
      <div>
        <h3>Science-based assessment for small organizations</h3>
        <p>Evergreen Assessments LLC is my independent practice, offering practical, research-based assessment and feedback for small organizations. Its first product, Groundwise, is a self-assessment for frontline supervisors, now in development.</p>
        <p class="fine muted">Evergreen is a private business, run on my own time and separate from my role at URI.</p>
      </div>
      <a class="btn btn-secondary" href="{EVERGREEN}">Visit Evergreen &rarr;</a>
    </div>
  </div>
</section>


{contact_band()}
</main>
""" + FOOTER
write("index.html", home)

# ───────────────────────── Research ─────────────────────────
research = head("Research · Matthew D. Hanson, Ph.D.",
                "Matthew Hanson's research on training and workplace learning, leadership assessment and selection, and work motivation, recovery, and well-being.",
                "research") + header("research") + """
<main id="main">
<section class="page-intro">
  <div class="wrap">
    <p class="eyebrow">Research</p>
    <h1>Field research on how people learn, are assessed, and stay motivated at work.</h1>
    <p class="lede">My work spans academic, government, and military settings, and now continues at the University of Rhode Island. I use randomized experiments, longitudinal surveys, structural equation modeling, and multilevel models, and I work closely with the organizations involved so the findings inform real decisions.</p>
  </div>
</section>

<section class="section pt-2">
  <div class="wrap research-layout">
    <nav class="toc" aria-label="On this page">
      <p class="eyebrow">On this page</p>
      <ol>
        <li><a href="#learning"><span>01</span> Training &amp; learning</a></li>
        <li><a href="#assessment"><span>02</span> Assessment &amp; selection</a></li>
        <li><a href="#motivation"><span>03</span> Motivation &amp; well-being</a></li>
        <li><a href="#next"><span>04</span> AI-assisted feedback</a></li>
        <li><a href="#uri-agenda"><span>&rarr;</span> Agenda at URI</a></li>
        <li><a href="#anchor"><span>&rarr;</span> ANCHOR Lab</a></li>
        <li><a href="#projects"><span>&rarr;</span> Selected projects</a></li>
      </ol>
    </nav>
    <div class="prose">

      <article class="theme-detail" id="learning">
        <span class="num">01</span>
        <h2>Training &amp; workplace learning</h2>
        <p class="q">When learning happens on a screen and nobody is watching, what keeps attention on the task?</p>
        <div class="body">
          <p>Learning is one of the most consequential things people do at work, and a growing share of it is self-paced and online. My work examines how attention, mindfulness, and self-regulation shape what people take away from training. It includes a 2&times;2 experiment in an air traffic control simulation that separates the effects of actual mindfulness practice from simply calling something &ldquo;mindfulness,&rdquo; and a conceptual model of <em>mindful training</em> that brings mindfulness theory together with established principles of learning science.</p>
        </div>
        <div class="takeaway">
          <p class="eyebrow">Takeaway</p>
          <p>In self-directed online learning, off-task attention is especially costly. Strategies such as goal setting and mindfulness may help learners stay focused when distraction is the default.</p>
        </div>
        <div class="key-work">
          <h3>Key work</h3>
          <ul>
            <li>Randall, Zajac, &amp; Hanson (2025), <cite>Human Resource Development Review</cite></li>
            <li>Randall, Hanson, &amp; Nassrelgrgawi (2022), <cite>Applied Psychology: An International Review</cite></li>
            <li>Hanson, Randall, Danna, &amp; Le (2020), <cite>The Routledge Companion to Mindfulness at Work</cite></li>
            <li>Hanson, Randall, &amp; Banfi, <em>Practice, label, or placebo?</em> An experimental test of mindfulness in training (manuscript under review)</li>
            <li>Lee, Hanson, &amp; Cheung (2019), bystander intervention in harassment training, <cite>Industrial and Organizational Psychology</cite></li>
            <li>Research assistant on an Army Research Institute grant on informal, self-regulated learning</li>
          </ul>
        </div>
        <p class="uri-note"><span class="eyebrow">At URI</span> Taking the mindful-training framework into new settings and testing its boundary conditions: when, and for whom, mindfulness-based approaches actually improve learning, including informal learning on the job.</p>
      </article>

      <article class="theme-detail" id="assessment">
        <span class="num">02</span>
        <h2>Assessment &amp; selection</h2>
        <p class="q">How do we know a leadership assessment measures something real, and treats people fairly?</p>
        <div class="body">
          <p>Organizations make decisions about selection, development, and promotion based on assessments. I build and evaluate those tools: defining what good performance looks like in a specific role, writing items that capture it, and testing whether scores are reliable, valid, and fair.</p>
          <p>At the Naval Submarine Medical Research Laboratory I contributed to the Submarine Environment Fit (SUBFIT) assessment and to a leadership competency model for submarine command teams, along with a method for gathering criterion-related validity evidence for it. At the Center for the Army Profession and Leadership, I led the development and validation of leadership assessments that support Army leader development.</p>
        </div>
        <div class="takeaway">
          <p class="eyebrow">Takeaway</p>
          <p>&ldquo;Good leadership&rdquo; looks different from one role to the next. Defining role-specific competencies first is what makes later selection and feedback tools defensible.</p>
        </div>
        <div class="key-work">
          <h3>Key work</h3>
          <ul>
            <li><a href="https://apps.dtic.mil/sti/citations/AD1217151">Leadership competency model for submarine command triads</a> (2023), DTIC technical report</li>
            <li><a href="https://apps.dtic.mil/sti/citations/AD1183611">SUBFIT Assessment: Psychometric review</a> (2022), DTIC technical report</li>
            <li>Development of a refugee job search stressor scale (Academy of Management, 2021), from an NSF-funded project</li>
          </ul>
        </div>
        <p class="uri-note"><span class="eyebrow">At URI</span> Studying the validity and fairness of HR assessment systems, especially in public-sector and high-stakes settings where scores shape hiring, promotion, and who gets identified as leadership talent.</p>
      </article>

      <article class="theme-detail" id="motivation">
        <span class="num">03</span>
        <h2>Motivation &amp; well-being</h2>
        <p class="q">Can a good life outside work make up for needs that go unmet at work?</p>
        <div class="body">
          <p>Self-determination theory holds that people need autonomy, competence, and relatedness. My dissertation, <em>Barking up the Wrong Need</em>, tested whether satisfying a need outside work that goes unmet at work produces better recovery. Using a time-lagged design and response surface analysis, I found that need satisfaction outside work predicted well-being and recovery overall, but it did not compensate for the specific needs that work left unmet.</p>
          <p>I carried this line of work into two Defense Health Program grants as co-investigator, studying burnout, need satisfaction, and training success among submariners.</p>
        </div>
        <div class="takeaway">
          <p class="eyebrow">Takeaway</p>
          <p>Need satisfaction at work and outside it are both necessary, not interchangeable. A great weekend won&rsquo;t fully offset a job that leaves people without autonomy, competence, or connection.</p>
        </div>
        <div class="key-work">
          <h3>Key work</h3>
          <ul>
            <li>Hanson, Randall, &amp; Banfi, need satisfaction across life domains (manuscript under review)</li>
            <li>How psychological need satisfaction and motivation influence burnout in submariners (Defense Health Program, $130K, co-investigator)</li>
            <li>Submariner training success: Predicting graduation from the submarine training pipeline (Defense Health Program, $265K, co-investigator)</li>
          </ul>
        </div>
        <p class="uri-note"><span class="eyebrow">At URI</span> Testing how work design, managerial practices, and recovery interventions can support sustained motivation and retention, and preparing my dissertation research on need satisfaction across life domains for publication.</p>
      </article>

      <article class="theme-detail" id="next">
        <span class="num">04</span>
        <h2>Next: AI-assisted assessment &amp; feedback</h2>
        <p class="q">Can conversational AI deliver developmental feedback that is both scalable and scientifically sound?</p>
        <div class="body">
          <p>Good developmental feedback is expensive to deliver at scale. I&rsquo;m exploring how large language models can be paired with validated assessment frameworks to administer assessments conversationally and generate personalized feedback, without giving up the psychometric standards that make the results trustworthy. I&rsquo;m also interested in how these tools can help translate competency models into practical guidance, for example for service members moving into civilian careers.</p>
        </div>
        <p class="uri-note"><span class="eyebrow">At URI</span> Developing this into a formal, externally funded research program, starting from a proof-of-concept platform for conversational assessment and personalized feedback.</p>
      </article>

      <section class="uri-agenda" id="uri-agenda" aria-labelledby="uri-agenda-h">
        <p class="eyebrow">University of Rhode Island &middot; College of Business</p>
        <h2 id="uri-agenda-h">Research agenda at URI</h2>
        <p>As the Fred &rsquo;78 and Sue Newton Assistant Professor of Human Resource Management, I&rsquo;m building a research program around questions that matter to HR practice:</p>
        <ol class="agenda">
          <li><strong>Leader assessment and AI-assisted feedback.</strong> Pairing large language models with validated assessment frameworks to make high-quality developmental feedback accessible and scalable.</li>
          <li><strong>Precision and fairness in measurement.</strong> Improving the accuracy, fairness, and interpretability of assessments used in personnel decisions.</li>
          <li><strong>Motivation, recovery, and well-being.</strong> How work and nonwork conditions together sustain motivation and performance, and prevent burnout.</li>
          <li><strong>Training that works.</strong> Extending the mindful-training framework into new settings and testing when mindfulness-based approaches help people learn.</li>
        </ol>
        <div class="lab" id="anchor">
          <h3>The ANCHOR Lab</h3>
          <p>This work happens in the ANCHOR Lab, which studies assessment, psychological needs, competencies, and resilience in people and organizations. Undergraduate and graduate students take part in real projects, from study design to analysis, and URI students can join for credit through MGT 491 (Directed Study). Interested? <a href="mailto:matthew.hanson@uri.edu">Email me</a> with a note about your interests.</p>
          <p>I also co-direct the <strong>College of Business Behavioral Lab</strong> in URI&rsquo;s Coastal Institute, a shared facility for experimental and survey research.</p>
        </div>
        <p>I&rsquo;m especially interested in partnerships with Rhode Island employers in defense, healthcare, manufacturing, and the public sector. The <a href="strength.html">strength-gap</a> and <a href="records.html">world-records</a> analyses are examples of the data-science side of this work.</p>
      </section>

    </div>
  </div>
</section>

<section class="section" id="projects" aria-labelledby="proj-h">
  <div class="wrap section-grid">
    <div class="section-label">
      <p class="eyebrow">Applied work</p>
      <h2 id="proj-h">Selected projects</h2>
    </div>
    <div class="cards">
      <article class="card">
        <p class="status">Research showcase</p>
        <h3><a class="stretch" href="strength.html">Did more competition close the strength gap?</a></h3>
        <p>An analysis of 2.7 million powerlifting results using depth-matched comparisons, mixed-effects growth models, and gradient-boosted machine learning.</p>
        <p class="meta">Independent analysis &middot; 2026</p>
        <span class="go">Read the analysis &rarr;</span>
      </article>
      <article class="card">
        <p class="status">Research showcase</p>
        <h3><a class="stretch" href="records.html">Do women&rsquo;s records catch up?</a></h3>
        <p>World-record histories in 28 running, jumping, and swimming events, modeled as catch-up curves with onset years, plateaus, and bootstrap intervals.</p>
        <p class="meta">Independent analysis &middot; 2026</p>
        <span class="go">Read the analysis &rarr;</span>
      </article>
      <article class="card">
        <p class="status done">Completed</p>
        <h3>Leadership assessment development</h3>
        <p>End-to-end development and validation of leadership assessments for an Army leader-development program, from item writing through pilot studies and integration.</p>
        <p class="meta">Center for the Army Profession and Leadership &middot; 2024&ndash;2025</p>
      </article>
      <article class="card">
        <p class="status done">Army research</p>
        <h3>Leader behavior &amp; command climate</h3>
        <p>Co-led studies of how leader behavior relates to command climate, with the goal of giving leaders actionable steps.</p>
        <p class="meta">Center for the Army Profession and Leadership &middot; 2025&ndash;2026</p>
      </article>
      <article class="card">
        <p class="status done">Completed</p>
        <h3><a class="stretch" href="https://apps.dtic.mil/sti/citations/AD1217151">Submarine Force leadership competency model</a></h3>
        <p>A role-specific competency model for submarine command teams, plus a validation study linking it to performance indicators.</p>
        <p class="meta">Naval Submarine Medical Research Laboratory &middot; 2022&ndash;2024</p>
        <span class="go">Technical report &rarr;</span>
      </article>
      <article class="card">
        <p class="status done">Completed</p>
        <h3>Assessment feedback as development</h3>
        <p>Tested whether personalized feedback from the SUBFIT assessment improves trainees&rsquo; job satisfaction and self-efficacy, treating assessment as a development tool and not only a screen.</p>
        <p class="meta">Naval Submarine Medical Research Laboratory &middot; 2022&ndash;2024</p>
      </article>
    </div>
  </div>
</section>
</main>
""" + FOOTER
write("research.html", research)

# ───────────────────────── Publications ─────────────────────────
n_all = len(ARTICLES) + len(CHAPTERS) + len(REPORTS) + len(REVIEW) + len(TALKS) + len(POSTERS)
pubs = head("Publications · Matthew D. Hanson, Ph.D.",
            "Peer-reviewed articles, book chapters, technical reports, and conference presentations by Matthew D. Hanson, Ph.D.",
            "publications") + header("publications") + f"""
<main id="main">
<section class="page-intro">
  <div class="wrap">
    <p class="eyebrow">Publications</p>
    <h1>Research &amp; writing</h1>
    <p class="lede">Peer-reviewed articles, a book chapter, technical reports, and conference work. For citation counts, see my <a href="{SCHOLAR}">Google Scholar profile</a>.</p>
  </div>
</section>

<section class="section pt-1">
  <div class="wrap">
    <fieldset class="filter" hidden>
      <legend>Show</legend>
      <div class="chips">
        <label class="chip"><input type="radio" name="type" value="all" checked><span>All <span class="n">{n_all}</span></span></label>
        <label class="chip"><input type="radio" name="type" value="article"><span>Articles <span class="n">{len(ARTICLES)}</span></span></label>
        <label class="chip"><input type="radio" name="type" value="chapter"><span>Chapters <span class="n">{len(CHAPTERS)}</span></span></label>
        <label class="chip"><input type="radio" name="type" value="report"><span>Reports <span class="n">{len(REPORTS)}</span></span></label>
        <label class="chip"><input type="radio" name="type" value="review"><span>Under review <span class="n">{len(REVIEW)}</span></span></label>
        <label class="chip"><input type="radio" name="type" value="talk"><span>Presentations <span class="n">{len(TALKS) + len(POSTERS)}</span></span></label>
      </div>
      <p class="filter-status" aria-live="polite"></p>
    </fieldset>

{group("g-articles", "article", "Peer-reviewed articles", ARTICLES)}
{group("g-chapters", "chapter", "Book chapters", CHAPTERS)}
{group("g-reports", "report", "Technical reports", REPORTS)}
{group("g-review", "review", "Manuscripts under review", REVIEW)}
{group("g-talks", "talk", "Conference presentations", TALKS, collapse=True)}
{group("g-posters", "talk", "Conference posters", POSTERS, collapse=True)}
  </div>
</section>
</main>
""" + FOOTER
write("publications.html", pubs)

# ───────────────────────── CV ─────────────────────────
cv = head("CV · Matthew D. Hanson, Ph.D.",
          "Curriculum vitae of Matthew D. Hanson, Ph.D.: education, positions, grants, teaching, service, and skills.",
          "cv") + header("cv") + """
<main id="main">
<section class="page-intro">
  <div class="wrap cv-head">
    <div>
      <p class="eyebrow">Curriculum vitae</p>
      <h1>CV</h1>
      <p class="lede">A summary of my training and experience. The full CV, including every presentation and poster, is available as a PDF.</p>
    </div>
    <div class="btn-row">
      <a class="btn btn-primary" href="matthew-hanson-cv.pdf">Download full CV <span class="meta">PDF, updated Oct 2026</span></a>
    </div>
  </div>
</section>

<section class="section pt-15">
  <div class="wrap">
    <div class="prose">

      <div class="cv-block">
        <h2>Positions</h2>
        <ol class="timeline">
          <li>
            <p class="when">2026&ndash;present</p>
            <h3>Fred &rsquo;78 and Sue Newton Assistant Professor of Human Resource Management</h3>
            <p class="org">College of Business, University of Rhode Island &middot; Kingston, RI</p>
            <p>Director, ANCHOR Lab. Co-Director, College of Business Behavioral Lab (Coastal Institute).</p>
          </li>
          <li>
            <p class="when">2024&ndash;2026</p>
            <h3>Research Psychologist, Industrial-Organizational Psychology</h3>
            <p class="org">Center for the Army Profession and Leadership, U.S. Army</p>
            <p>Led research on leadership assessment and development, including the design, validation, and delivery of assessment programs. Served as an internal expert on assessment design, feedback reports, and professional writing, and briefed senior leaders on evidence-based assessment decisions.</p>
          </li>
          <li>
            <p class="when">2021&ndash;2024</p>
            <h3>Research Scientist, Industrial-Organizational Psychology</h3>
            <p class="org">Leidos, at the Naval Submarine Medical Research Laboratory &middot; Groton, CT</p>
            <p>Co-investigator on $395K in Defense Health Program grants, including a longitudinal study of burnout and need satisfaction. Developed and validated assessments of personality, attitudes, and leader competencies for the U.S. Submarine Force, and led feedback sessions with trainees.</p>
          </li>
          <li>
            <p class="when">2019&ndash;2023</p>
            <h3>Research Project Assistant</h3>
            <p class="org">SUNY Research Foundation, University at Albany</p>
            <p>Faculty-led projects on refugee job search, informal workplace learning, and self-regulation in training: factor analysis, qualitative coding, structured interviews, and presentations to academic and community audiences.</p>
          </li>
        </ol>
      </div>

      <div class="cv-block">
        <h2>Education</h2>
        <ol class="timeline">
          <li>
            <p class="when">2023</p>
            <h3>Ph.D., Industrial-Organizational Psychology</h3>
            <p class="org">University at Albany, State University of New York</p>
            <p>Dissertation: <em>Barking up the Wrong Need: How Basic Psychological Need Satisfaction at and Outside of Work Interact to Influence Work Recovery</em>. Chair: Dr. Jason Randall.</p>
          </li>
          <li>
            <p class="when">2017</p>
            <h3>M.S., Experimental Psychology</h3>
            <p class="org">University of Wisconsin Oshkosh</p>
            <p>Thesis: <em>Anxiety, Attention, and Mindfulness Following Focused Attention and Open-Monitoring Mindfulness Meditation</em>. Chair: Dr. Phan Hong.</p>
          </li>
          <li>
            <p class="when">2014</p>
            <h3>B.S., Psychology, Neuroscience minor</h3>
            <p class="org">University of Wisconsin Oshkosh &middot; Magna cum laude</p>
          </li>
        </ol>
      </div>

      <div class="cv-block">
        <h2>Grants</h2>
        <ul class="plain-list">
          <li class="grant"><span class="when">2024&ndash;2025</span> <span class="amt">$265,000</span> &middot; Submariner training success: A statistical model of cognitive and psychological health for predicting graduation from the submarine training pipeline. <span class="muted">Defense Health Program, co-investigator.</span></li>
          <li class="grant"><span class="when">2023&ndash;2025</span> <span class="amt">$130,000</span> &middot; How psychological need satisfaction and motivation influence burnout in submariners. <span class="muted">Defense Health Program, co-investigator.</span></li>
          <li class="grant"><span class="when">2019&ndash;2023</span> <span class="amt">$181,896</span> &middot; Promoting informal self-regulated learning: A multi-level approach. <span class="muted">U.S. Army Research Institute, research assistant.</span></li>
          <li class="grant"><span class="when">2018&ndash;2021</span> <span class="amt">$315,997</span> &middot; Privacy-preserving mobile data collection for social and behavioral research. <span class="muted">National Science Foundation, research assistant.</span></li>
          <li class="grant"><span class="when">2023</span> <span class="amt">$480</span> &middot; Dissertation research grant. <span class="muted">University at Albany Benevolent Association.</span></li>
        </ul>
      </div>

      <div class="cv-block">
        <h2 id="teaching">Teaching</h2>
        <ul class="plain-list">
          <li><span class="when">2026&ndash;present</span> <strong>MGT 342 Human Resource Management</strong> <span class="muted">&middot; University of Rhode Island</span></li>
          <li><span class="when">2026&ndash;present</span> <strong>LHR 500 / MBA 571 Labor Relations and Human Resources</strong> <span class="muted">&middot; University of Rhode Island</span></li>
          <li><span class="when">2026&ndash;present</span> <strong>MGT 491 Directed Study</strong> <span class="muted">&middot; University of Rhode Island &middot; ANCHOR Lab research</span></li>
          <li><span class="when">2020, 2021</span> Instructor of record, <strong>Industrial/Organizational Psychology</strong> <span class="muted">&middot; University at Albany &middot; about 125 students per section</span></li>
          <li><span class="when">2019</span> Instructor of record, <strong>Learning</strong> <span class="muted">&middot; University at Albany</span></li>
          <li><span class="when">Graduate</span> Teaching assistant, undergraduate statistics <span class="muted">&middot; University at Albany</span></li>
        </ul>
      </div>

      <div class="cv-block">
        <h2>Service</h2>
        <ul class="plain-list">
          <li><span class="when">2025&ndash;present</span> Co-lead, Conference Submission Subcommittee, SIOP Military and Veterans Inclusion Committee</li>
          <li><span class="when">2017&ndash;2018</span> Assistant Editor, <cite>Journal of Business and Psychology</cite></li>
          <li><span class="when">2019</span> Volunteer, Girls Inc. EUREKA! STEM program, University at Albany</li>
          <li><span class="when">2015</span> Mentor, McNair Scholars Program, University of Wisconsin Oshkosh</li>
        </ul>
      </div>

      <div class="cv-block">
        <h2>Skills &amp; credentials</h2>
        <ul class="plain-list">
          <li><span class="when">Methods</span> Randomized experiments, longitudinal designs, SEM, CFA, HLM, polynomial regression and response surface analysis, scale development and validation</li>
          <li><span class="when">Tools</span> R, SQL, SPSS, Mplus, Power BI, E-Prime</li>
          <li><span class="when">Certifications</span> Hogan Assessments (Foundational, Advanced Interpretation, Advanced Feedback); CITI human subjects research and responsible conduct of research</li>
          <li><span class="when">Memberships</span> SIOP, Academy of Management, American Psychological Association, SHRM</li>
        </ul>
      </div>

    </div>
  </div>
</section>
</main>
""" + FOOTER
write("cv.html", cv)
