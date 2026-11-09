"""Sanity checks before pushing: every sitemap URL has a file, key files exist, internal links resolve."""
import os, re, sys
from sitegen import ROOT, B, rd, all_html

errors = []
for f in ['index.html', 'sitemap.xml', 'robots.txt', 'llms.txt', '7b2e9c4a1f6d48e3a05c9d8e2f1b3a76.txt', 'CNAME', 'og-image.jpg', 'favicon.ico']:
    if not os.path.exists(os.path.join(ROOT, f)):
        errors.append(f'missing {f}')
if 'google-site-verification' not in rd('index.html'):
    errors.append('google-site-verification meta missing from index.html')


def exists(path):
    p = os.path.join(ROOT, path.lstrip('/'))
    return os.path.isfile(p) or os.path.isfile(os.path.join(p, 'index.html'))


locs = re.findall(r'<loc>([^<]+)</loc>', rd('sitemap.xml'))
for u in locs:
    if not exists(u[len(B):]):
        errors.append(f'sitemap URL without file: {u}')
pages = list(all_html())
for p in pages:
    for href in re.findall(r'href="(/[^"#?]*)', rd(p)):
        if not exists(href):
            errors.append(f'{p}: broken link {href}')
print(f'{len(locs)} sitemap URLs, {len(pages)} pages')
if errors:
    print('\n'.join(errors)); sys.exit(1)
print('OK')
