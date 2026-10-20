"""Write tools/out/og.html, the 1200 x 630 link card, then capture it as assets/og.png.

python -I tools/og.py
node --experimental-websocket tools/shot.mjs http://localhost:8165/tools/out/og.html assets/og.png 1200 630 view

The card is the lead of the day: the wordmark, the headline set sharp, the reading in canary, its call, and its photograph.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402
from build import E, call, esc, wordmark, SPRITE  # noqa: E402

L = E['lead']
lead = {st['code']: st for _, st in build.stations()}[L['codes'][0]]
html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<link rel="stylesheet" href="../../assets/css/cp.css"><link rel="stylesheet" href="../../assets/css/book.css">
<style>html,body{{margin:0;background:#0E100D}}.wrapog{{display:grid;grid-template-columns:700px 500px;width:1200px;height:630px}}
.og{{width:700px;height:630px;box-sizing:border-box;padding:52px 56px}}.og .wm{{width:300px}}.og h3{{font-size:44px;max-width:none}}
.og .r{{font-size:64px}}.og .r small{{font-size:17px}}.og .r .call{{width:52px;height:32px}}
.ph{{background:#1D211C url(../../assets/img/photo/{L["photo"]}.webp) center/cover}}</style></head>
<body>{SPRITE}<div class="wrapog"><div class="og">{wordmark()}<h3 class="hl" data-s="alert">{esc(L["headline"])}</h3>
<p class="r">{call(L["status"])}{esc(lead["reading"])}<small>{esc(L["reading_note"])}</small></p></div><div class="ph"></div></div></body></html>'''
os.makedirs(os.path.join(build.ROOT, 'tools', 'out'), exist_ok=True)
open(os.path.join(build.ROOT, 'tools', 'out', 'og.html'), 'w', encoding='utf-8').write(html)
print('tools/out/og.html')
