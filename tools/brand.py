"""Canary Palestine marks, drawn on Geologica's own metrics.

python -I tools/brand.py   -> assets/brand/*.svg + assets/js/marks.js + favicon.svg

The mark is the c of «canary» drawn as the bird's head: a round head with an eye on the
crown and the beak open, tilted up the way a canary throws its head back to sing.
In the wordmark the head sings its own name: the open beak faces «anary».
Standing alone, the head is followed by its call, drawn the way a sonograph draws sound
(time across, pitch up). There are four calls, one for each desk status:
  song     steady  - an even trill of rising notes
  strained watch   - the trill breaks: notes drop out and fall
  alarm    alert   - short broadband chips, the canary's alarm call, drawn as full-height bars
  silent   silent  - no call, and the beak is shut
"""
import io
import json
import math
import os

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'research', 'font-src')
OUT = os.path.join(ROOT, 'assets', 'brand')
os.makedirs(OUT, exist_ok=True)

COAL, CHALK, CANARY, PAPER, TRACE = '#0E100D', '#ECEEE6', '#F2DA1C', '#EDEEE8', '#161814'

WGHT, SHRP = 780, 60          # the wordmark's instance of Geologica
STEM = 296                    # ring weight: the c's own thickness at 780 (its bowl is lighter than the l stem, 357)
XH_TOP, XH_BOT = 1058, -30    # top and bottom overshoot of the round lowercase
R_OUT = (XH_TOP - XH_BOT) / 2
R_MID = R_OUT - STEM / 2
CY = (XH_TOP + XH_BOT) / 2    # font units, y up
BEAK = (-12, 46)              # the open beak, in degrees: lower and upper mandible
SHUT = (12, 20)               # the beak almost closed (silent)
EYE_AT, EYE_R = 76, 0.25 * STEM


def f(v):
    return f'{v:.1f}'.rstrip('0').rstrip('.')


def instance(path, limits):
    font = instancer.instantiateVariableFont(TTFont(path), limits)
    buf = io.BytesIO()
    font.save(buf)
    buf.seek(0)
    return TTFont(buf)


def head(cx, cy, s, beak=BEAK, eye=True):
    """The head as one path (even-odd): ring from the upper mandible round to the lower one,
    eye punched through the crown. cx, cy in output units (y down); s = output units per font unit."""
    lo, hi = beak
    ro, ri = R_OUT * s, (R_OUT - STEM) * s
    a0, a1 = math.radians(hi), math.radians(lo + 360)
    pt = lambda r, a: (cx + r * math.cos(a), cy - r * math.sin(a))
    x1, y1 = pt(ro, a0)
    x2, y2 = pt(ro, a1)
    x3, y3 = pt(ri, a1)
    x4, y4 = pt(ri, a0)
    large = 1 if (a1 - a0) > math.pi else 0
    d = (f'M{f(x1)} {f(y1)}A{f(ro)} {f(ro)} 0 {large} 0 {f(x2)} {f(y2)}'
         f'L{f(x3)} {f(y3)}A{f(ri)} {f(ri)} 0 {large} 1 {f(x4)} {f(y4)}Z')
    if eye:
        ea = math.radians(EYE_AT)
        ex, ey = pt(R_MID * s, ea)
        er = EYE_R * s
        d += f'M{f(ex - er)} {f(ey)}a{f(er)} {f(er)} 0 1 0 {f(2 * er)} 0a{f(er)} {f(er)} 0 1 0 {f(-2 * er)} 0Z'
    return d


def call(kind, x, base, h, unit):
    """The call after the head, as stroke paths (round caps), in output units.
    x: left edge, base: baseline (y down), h: x-height, unit: stroke weight."""
    out = []
    if kind == 'song':
        # an even trill: four rising notes, each a short upward sweep, the line of notes climbing
        for i in range(4):
            x0 = x + i * unit * 2.7
            y0 = base - h * 0.2 - i * h * 0.12
            out.append(f'M{f(x0)} {f(y0)}q{f(unit * 0.5)} {f(-h * 0.04)} {f(unit * 1.5)} {f(-h * 0.42)}')
    elif kind == 'strained':
        # the trill breaks: the second note drops out, the last ones fall and shorten
        for i, note in enumerate([(0, 0.5), None, (0.06, 0.34), (0.2, 0.2)]):
            if note is None:
                continue
            dy, ln = note
            x0 = x + i * unit * 2.7
            y0 = base - h * 0.2 - i * h * 0.12 + dy * h
            k = ln / 0.5
            out.append(f'M{f(x0)} {f(y0)}q{f(unit * 0.5 * k)} {f(-h * 0.04 * k)} {f(unit * 1.5 * k)} {f(-h * 0.42 * k)}')
    elif kind == 'alarm':
        # three broadband chips: full-height bars, the alarm call on a sonogram
        for i in range(4):  # chip-chip, chip-chip
            x0 = x + unit * 0.6 + i * unit * 2.3 + (i // 2) * unit * 2.2
            out.append(f'M{f(x0)} {f(base - h * 0.02)}V{f(base - h * 0.98)}')
    return out


def glyphs(font, text, x0, base, s, kern=True):
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    paths, x = [], x0
    for ch in text:
        g = cmap[ord(ch)]
        pen = SVGPathPen(gs)
        gs[g].draw(TransformPen(pen, (s, 0, 0, -s, x, base)))
        paths.append(pen.getCommands())
        x += gs[g].width * s
    return ''.join(paths), x


def svg(w, h, body, bg=None, label='Canary Palestine'):
    rect = f'<rect width="{f(w)}" height="{f(h)}" fill="{bg}"/>' if bg else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {f(w)} {f(h)}" width="{f(w)}" height="{f(h)}" '
            f'role="img" aria-label="{label}">{rect}{body}</svg>\n')


HEAD_JS = f"""
/* The head as brand.py draws it, for drawing it live (the loader, the book): a ring from the upper
   mandible (hi) round to the lower one (lo), in degrees, and the eye punched through the crown.
   cx, cy: centre in SVG units (y down); s: SVG units per font unit (the head is {round(2 * R_OUT)} units across). */
window.canaryHead = function (cx, cy, s, lo = {BEAK[0]}, hi = {BEAK[1]}) {{
  const RO = {R_OUT} * s, RI = {R_OUT - STEM} * s, RM = {R_MID} * s, ER = {EYE_R} * s, E = {EYE_AT} * Math.PI / 180;
  const a0 = hi * Math.PI / 180, a1 = (lo + 360) * Math.PI / 180, L = a1 - a0 > Math.PI ? 1 : 0;
  const p = (r, a) => [cx + r * Math.cos(a), cy - r * Math.sin(a)];
  const [x1, y1] = p(RO, a0), [x2, y2] = p(RO, a1), [x3, y3] = p(RI, a1), [x4, y4] = p(RI, a0), [ex, ey] = p(RM, E);
  return `M${{x1}} ${{y1}}A${{RO}} ${{RO}} 0 ${{L}} 0 ${{x2}} ${{y2}}L${{x3}} ${{y3}}A${{RI}} ${{RI}} 0 ${{L}} 1 ${{x4}} ${{y4}}Z` +
    `M${{ex - ER}} ${{ey}}a${{ER}} ${{ER}} 0 1 0 ${{2 * ER}} 0a${{ER}} ${{ER}} 0 1 0 ${{-2 * ER}} 0Z`;
}};
window.CANARY_BEAK = [{BEAK[0]}, {BEAK[1]}];
window.CANARY_SHUT = [{SHUT[0]}, {SHUT[1]}];
"""


def main():
    geo = instance(os.path.join(SRC, 'Geologica-var.ttf'), {'wght': WGHT, 'SHRP': SHRP, 'CRSV': 1, 'slnt': 0})
    mono = instance(os.path.join(SRC, 'MartianMono-var.ttf'), {'wght': 560, 'wdth': 87.5})
    gs = geo.getGlyphSet()
    cw = gs['c'].width

    # ---- wordmark: the head, then "anary"; PALESTINE in Martian Mono on a line under "anar",
    # ending before the y's descender, tracked by a third of a letter
    s = 0.06                      # 2000 upm -> x-height ~65 px
    pad = 6
    base = XH_TOP * s + pad
    word_head = head(pad + R_OUT * s, base - CY * s, s)
    x0 = pad + 2 * R_OUT * s + (70 - 60) * s       # a's own side bearing is 60; leave the head 70
    letters, x_end = glyphs(geo, 'anary', x0, base, s)
    mgs = mono.getGlyphSet()
    mcmap = mono.getBestCmap()
    pal_x0 = x0 + 60 * s
    pal_x1 = x_end - gs['y'].width * s - 10 * s
    adv = (pal_x1 - pal_x0) / (9 + 8 * 0.34)
    ms = adv / mgs[mcmap[ord('P')]].width
    track = adv * 0.34
    pal_y = base + XH_TOP * s * 0.22 + 1400 * ms
    pal = []
    for i, ch in enumerate('PALESTINE'):
        pen = SVGPathPen(mgs)
        mgs[mcmap[ord(ch)]].draw(TransformPen(pen, (ms, 0, 0, -ms, pal_x0 + i * (adv + track), pal_y)))
        pal.append(pen.getCommands())
    pal = ''.join(pal)
    W, H = x_end + pad, max(pal_y, base + 447 * s) + pad
    marks = {'wordmark': {'w': round(W, 1), 'h': round(H, 1), 'head': word_head, 'letters': letters, 'pal': pal}}

    def wordmark(ink, headc, palc, bg=None):
        return svg(W, H, f'<path d="{word_head}" fill="{headc}" fill-rule="evenodd"/>'
                         f'<path d="{letters}" fill="{ink}"/><path d="{pal}" fill="{palc}"/>', bg)

    open(os.path.join(OUT, 'wordmark.svg'), 'w', encoding='utf-8').write(wordmark(TRACE, TRACE, TRACE))
    open(os.path.join(OUT, 'wordmark-coal.svg'), 'w', encoding='utf-8').write(wordmark(CHALK, CANARY, '#8E948A', COAL))
    open(os.path.join(OUT, 'wordmark-canary.svg'), 'w', encoding='utf-8').write(wordmark(COAL, COAL, COAL, CANARY))

    # ---- the mark: head + call; the head is 56 high on a 64 high field
    hs = 56 / (XH_TOP - XH_BOT)
    sw = STEM * hs * 0.44
    calls = {}
    for kind in ('song', 'strained', 'alarm', 'silent'):
        hd = head(4 + R_OUT * hs, 4 + R_OUT * hs, hs, SHUT if kind == 'silent' else BEAK)
        strokes = call(kind, 4 + 2 * R_OUT * hs + 10, 60, 56, sw)
        calls[kind] = {'head': hd, 'call': strokes}
        body = (f'<path d="{hd}" fill="{{c}}" fill-rule="evenodd"/>'
                f'<path d="{"".join(strokes)}" stroke="{{c}}" stroke-width="{f(sw)}" stroke-linecap="round" fill="none"/>')
        for name, bg, c in (('', None, TRACE), ('-coal', COAL, CANARY)):
            open(os.path.join(OUT, f'mark-{kind}{name}.svg'), 'w', encoding='utf-8').write(
                svg(150, 64, body.replace('{c}', c), bg, f'Canary Palestine mark, {kind}'))
    marks['call'] = calls
    marks['callStroke'] = round(sw, 2)

    # ---- avatar and favicon: the head alone, singing, on canary / coal
    av = head(256, 262, 300 / (XH_TOP - XH_BOT))
    open(os.path.join(OUT, 'avatar.svg'), 'w', encoding='utf-8').write(svg(512, 512, f'<path d="{av}" fill="{COAL}" fill-rule="evenodd"/>', CANARY))
    open(os.path.join(OUT, 'avatar-coal.svg'), 'w', encoding='utf-8').write(svg(512, 512, f'<path d="{av}" fill="{CANARY}" fill-rule="evenodd"/>', COAL))
    fav = head(16, 16.6, 25 / (XH_TOP - XH_BOT))
    open(os.path.join(ROOT, 'favicon.svg'), 'w', encoding='utf-8').write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="7" fill="{COAL}"/>'
        f'<path d="{fav}" fill="{CANARY}" fill-rule="evenodd"/></svg>\n')

    os.makedirs(os.path.join(ROOT, 'assets', 'js'), exist_ok=True)
    os.makedirs(os.path.join(ROOT, 'tools', 'out'), exist_ok=True)
    json.dump(marks, open(os.path.join(ROOT, 'tools', 'out', 'marks.json'), 'w', encoding='utf-8'))
    open(os.path.join(ROOT, 'assets', 'js', 'marks.js'), 'w', encoding='utf-8').write(
        '// generated by tools/brand.py — do not edit\nwindow.CANARY_MARKS = ' + json.dumps(marks) + ';\n' + HEAD_JS)
    print('wordmark', round(W), 'x', round(H))


if __name__ == '__main__':
    main()
