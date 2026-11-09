# WTO Food Notification Brief (WTO 식품 통보 브리프)

An internal digest of food-related WTO SPS and TBT notifications, summarised in Korean.

> **Status: draft.** The Korean titles, classifications and editor's notes in every issue were drafted by AI (Claude) from the original notification texts and **have not yet been reviewed by staff**. Always check the original WTO document before relying on an entry.

## What is here

| Path | Contents |
|---|---|
| `site/index.html` | Cumulative brief: No. 01 (Sept 2026), No. 02 (Oct 2026), No. 03 (26 Oct–1 Nov 2026), No. 04 (2–8 Nov 2026) |
| `site/2026-03.html` | Stand-alone issue for March 2026 |
| `site/2026-04.html` | Stand-alone issue for April 2026 |
| `src/archive.html` | Page template (fonts and data are injected at build time) |
| `data/*.json` | Built issue data used by the pages |
| `work/mo/raw_*.json` | Raw ePing API responses per month (public WTO data) |
| `work/mo/cur_*.py` | Per-notification decisions: category, topic, Korean title, exclusions with reasons |
| `work/mo/notes.json` | Editor's notes per issue |
| `work/wk/` | Data and decisions for the 26 Oct–1 Nov 2026 issue |
| `scripts/` | Fetch, data-building and page-building scripts |

The finished HTML files are self-contained (fonts and data embedded) and open without a server.

## How an issue is made

1. **Fetch** — `scripts/fetch.py` pulls all SPS and TBT notifications distributed in a period from the WTO ePing API.
2. **Merge and shortlist** (`scripts/candidates.py <month>`) — joint notifications are merged into one entry. TBT items are shortlisted if they have an ICS 67 code, the ePing keyword "Food standards", or an HS code in chapters 1–24.
3. **Read and decide** — the original texts are read; TBT items duplicating an SPS notification, or not about food, are excluded with a reason; Korean titles and categories are written (`work/mo/cur_*.py`). **This step is meant to be confirmed by a staff member.**
4. **Build** — `scripts/make_archive.py` assembles issue data; `scripts/build.py` embeds fonts and data into the page.

```bash
# 1. fetch (the API key is passed as an environment variable and is never committed)
WTO_API_KEY=<your key> python3 scripts/fetch.py 11 2026-11-01 2026-11-30

# 3. write work/mo/cur_11_sps.py, cur_11_tbt.py and the notes entry, then:

# 4. build (font folder = the @fontsource/noto-sans-kr npm package; latin folder = @fontsource/noto-sans)
python3 scripts/make_archive.py work/mo
WTO_DATA=data/archive.json python3 scripts/build.py <noto-sans-kr>/package archive.html index.html <noto-sans>/package

# stand-alone issue for one month (e.g. March): writes data/2026-03.json
python3 scripts/make_archive.py work/mo single 03
WTO_DATA=data/2026-03.json python3 scripts/build.py <noto-sans-kr>/package archive.html 2026-03.html <noto-sans>/package
```

Fonts: Noto Sans KR and Noto Sans (SIL Open Font License), subset to the characters used and embedded in the page.

## Sources

Notification data: WTO ePing (api.wto.org). Korean titles are reference translations; the legal meaning is in the original documents linked from each entry.
