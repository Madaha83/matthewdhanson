# Do women's records catch up?

Analysis behind [matthewdhanson.com/records](https://matthewdhanson.com/records), a companion
to the [strength-gap](../strength-gap) analysis.

World-record progressions for 28 events where men and women compete under identical
conditions (flat running, jumps, long-course swimming) are modeled as catch-up curves:
a flat level until an onset year, then an exponential approach to a plateau.

## Reproduce

1. `python scripts/01_fetch.py "<page title>" ...` caches Wikipedia pages (CC BY-SA) into
   `data/wiki/` via the MediaWiki API. Page titles and event metadata are in
   `output/events_meta.json` (copy it to `data/` before running).
2. `scripts/02_build.py` parses record tables (dropping rows Wikipedia marks as
   rescinded, unratified, or pending) and builds annual series per event and sex.
3. `scripts/03_model.py` fits catch-up curves with a moving-block bootstrap, a pooled
   time constant, a 1992-style straight-line projection, and marathon-major winners.
4. `scripts/04_export.py` writes the JSON the website reads.

Requires `pandas numpy scipy lxml beautifulsoup4`.

Limitations are listed at the end of the published page.
