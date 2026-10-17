"""Step 1: fetch Wikipedia pages (rendered HTML) and cache them in data/.

Usage: python 01_fetch.py "Page title" ["Page title" ...]
Pages are fetched once through the MediaWiki API with a descriptive
User-Agent and a pause between requests. Content is CC BY-SA 4.0.
"""
from pathlib import Path
import json, sys, time, urllib.parse, urllib.request, ssl

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "wiki"
CACHE.mkdir(parents=True, exist_ok=True)
UA = "matthewdhanson.com research (contact: matthew.d.hanson@outlook.com)"
API = "https://en.wikipedia.org/w/api.php"


def cache_path(title):
    return CACHE / (urllib.parse.quote(title.replace(" ", "_"), safe="") + ".json")


def fetch(title):
    p = cache_path(title)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    q = urllib.parse.urlencode({"action": "parse", "page": title, "prop": "text|revid", "format": "json",
                                "redirects": 1, "formatversion": 2})
    req = urllib.request.Request(f"{API}?{q}", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60, context=ssl.create_default_context()) as r:
        d = json.loads(r.read().decode("utf-8"))
    if "error" in d:
        raise RuntimeError(f"{title}: {d['error'].get('info')}")
    out = {"title": d["parse"]["title"], "revid": d["parse"]["revid"], "html": d["parse"]["text"],
           "fetched": time.strftime("%Y-%m-%d")}
    p.write_text(json.dumps(out), encoding="utf-8")
    time.sleep(1.0)
    return out


if __name__ == "__main__":
    for t in (a.strip() for a in sys.argv[1:]):
        try:
            d = fetch(t)
            print(f"ok  {d['title']}  rev {d['revid']}  {len(d['html']):,} chars")
        except Exception as e:
            print(f"ERR {t}: {e}")
