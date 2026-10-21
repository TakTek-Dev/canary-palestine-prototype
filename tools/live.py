"""Check the published site: every built page and every file it references answers 200,
and an unknown address gets the silent 404 page.

python -I tools/live.py [base-url]
"""
import concurrent.futures as cf
import glob
import os
import re
import sys
import urllib.error
import urllib.request
from urllib.parse import urljoin, urldefrag

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = (sys.argv[1] if len(sys.argv) > 1 else 'https://taktek-dev.github.io/canary-palestine-prototype/').rstrip('/') + '/'
UA = {'User-Agent': 'CanaryPalestine-livecheck/1.0'}


def get(url, body=False):
    req = urllib.request.Request(url, headers=UA, method='GET' if body else 'HEAD')
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, (r.read().decode('utf-8', 'replace') if body else '')
    except urllib.error.HTTPError as e:
        return e.code, (e.read().decode('utf-8', 'replace') if body else '')
    except Exception as e:
        return 0, str(e)


pages = sorted(os.path.relpath(p, ROOT).replace(os.sep, '/') for p in glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True)
               if not re.search(r'(^|/)(research|tools)/', os.path.relpath(p, ROOT).replace(os.sep, '/')))
bad, assets = [], set()
with cf.ThreadPoolExecutor(12) as ex:
    for rel, (code, html) in zip(pages, ex.map(lambda r: get(BASE + r, True), pages)):
        if code != 200:
            bad.append((code, rel))
            continue
        for ref in re.findall(r'(?:src|href)="([^"#][^"]*)"', html):
            url = urldefrag(urljoin(BASE + rel, ref.replace('&amp;', '&')))[0]
            if url.startswith(BASE) and not url.endswith('.html') and url != BASE:
                assets.add(url)
    for url, (code, _) in zip(sorted(assets), ex.map(get, sorted(assets))):
        if code != 200:
            bad.append((code, url[len(BASE):]))

code, html = get(BASE + 'no-such-page/at/depth.html', True)
nf_ok = code == 404 and 'This page is silent.' in html
for b in bad:
    print(*b)
print(f'{len(pages)} pages, {len(assets)} assets, {len(bad)} failing; 404 page: {"ok" if nf_ok else "NOT ok (" + str(code) + ")"}')
sys.exit(1 if bad or not nf_ok else 0)
