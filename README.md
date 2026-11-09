# yjvclimayconfort.es

Static site of YJV Clima y Confort, served by GitHub Pages from `main` / root (custom domain in `CNAME`).
`_config.yml` keeps `tools/` and `content/` out of the published site.

## Publish a winter-campaign page

1. Write a spec in `content/invierno/AAAA-MM-DD-<slug>.json` (fields documented in `tools/publish.py`).
2. `python3 tools/publish.py content/invierno/<spec>.json`
3. `python3 tools/check.py`
4. Commit and push to `main`; GitHub Pages rebuilds in about a minute.

Never delete existing pages, `robots.txt`, `llms.txt`, the IndexNow key file `7b2e9c4a1f6d48e3a05c9d8e2f1b3a76.txt`
or the `google-site-verification` meta in `index.html`.
