"""Self-hosted WOFF2 subsets of the two brand faces.

python -I tools/fonts.py   (from the project root; sources in research/font-src, gitignored)

Geologica (Monokrom / Cyreal, OFL) sets the voice: headlines, reading, navigation.
Its SHRP axis (sharpness, 0-100) carries the desk status into the letters: a steady
report is set soft, an alert is set sharp. CRSV is pinned on (single-storey a, g, y).
Martian Mono (Evil Martians, OFL) sets the instruments: station codes, readings, dates.
Its width axis lets a reading be condensed to the width of its gauge.
Both are instanced to the axis ranges the site uses, and every layout feature is kept.
"""
import io
import os
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'research', 'font-src')
OUT = os.path.join(ROOT, 'assets', 'fonts')
os.makedirs(OUT, exist_ok=True)

# Basic Latin + Latin-1 + Latin Extended-A, the transliteration letters place names use
# (ḥ ṣ ḍ ṭ ẓ ʿ ʾ), typographic punctuation, arrows, primes, the multiplication and minus signs,
# superscript 3 for m³ and the per-mille sign.
UNICODES = (
    list(range(0x20, 0x7F)) + list(range(0xA0, 0x180)) +
    [0x1E0C, 0x1E0D, 0x1E24, 0x1E25, 0x1E62, 0x1E63, 0x1E6C, 0x1E6D, 0x1E92, 0x1E93, 0x02BE, 0x02BF, 0x02BC,
     0x2009, 0x200A, 0x2010, 0x2011, 0x2012, 0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2022, 0x2026,
     0x2030, 0x2032, 0x2033, 0x2039, 0x203A, 0x2044, 0x20AC, 0x20AA, 0x2116, 0x2190, 0x2191, 0x2192, 0x2193,
     0x2197, 0x2198, 0x2212, 0x2248, 0x2260, 0x2264, 0x2265, 0x00D7, 0x00B0, 0x00B7, 0x00B3, 0x00B2]
)

JOBS = [
    # (source, out, axis limits)
    ('Geologica-var.ttf', 'geologica.woff2', {'wght': (300, 850), 'SHRP': (0, 100), 'CRSV': 1, 'slnt': 0}),
    ('MartianMono-var.ttf', 'martian-mono.woff2', {'wght': (300, 800), 'wdth': (75, 112.5)}),
]


def options():
    o = subset.Options()
    o.flavor = 'woff2'
    o.layout_features = ['*']
    o.name_IDs = ['*']
    o.name_languages = ['*']
    o.notdef_outline = True
    o.glyph_names = False
    o.hinting = False
    o.desubroutinize = True
    return o


for src, out, limits in JOBS:
    font = TTFont(os.path.join(SRC, src))
    font = instancer.instantiateVariableFont(font, limits)
    buf = io.BytesIO()
    font.save(buf)  # round-trip so the partial instance subsets cleanly
    buf.seek(0)
    font = TTFont(buf)
    sub = subset.Subsetter(options())
    sub.populate(unicodes=UNICODES)
    sub.subset(font)
    path = os.path.join(OUT, out)
    subset.save_font(font, path, options())
    print(out, os.path.getsize(path) // 1024, 'KB')

for lic in ('OFL-Geologica.txt', 'OFL-MartianMono.txt'):
    with open(os.path.join(SRC, lic), encoding='utf-8') as f, open(os.path.join(OUT, lic), 'w', encoding='utf-8') as g:
        g.write(f.read())
