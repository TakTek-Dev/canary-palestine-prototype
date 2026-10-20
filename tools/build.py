"""Build home.html from tools/edition.json.

python -I tools/build.py

Everything a reader needs is in the HTML: the sonogram is drawn here as static SVG, the station
register, the reporting and the silence band are plain markup. assets/js/cp.js only adds the
loader, tooltips and the network's sound.
"""
import datetime as dt
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = '10'                                      # bump on any asset change (Chrome caches hard)
E = json.load(open(os.path.join(ROOT, 'tools', 'edition.json'), encoding='utf-8'))
MARKS = json.load(open(os.path.join(ROOT, 'tools', 'out', 'marks.json'), encoding='utf-8'))   # written by brand.py
PH = json.load(open(os.path.join(ROOT, 'tools', 'photos.json'), encoding='utf-8')) if os.path.exists(
    os.path.join(ROOT, 'tools', 'photos.json')) else {}
PHOTOS = json.load(open(os.path.join(ROOT, 'tools', 'out', 'photos.json'), encoding='utf-8')) if os.path.exists(
    os.path.join(ROOT, 'tools', 'out', 'photos.json')) else {}

esc = html.escape
D = lambda s: dt.date.fromisoformat(s)
LABEL = {'alert': 'Alert', 'watch': 'Watch', 'steady': 'Steady', 'silent': 'Silent'}
CALL = {'alert': 'the alarm call', 'watch': 'the song breaking', 'steady': 'the song', 'silent': 'no call'}
RANK = {'alert': 0, 'watch': 1, 'steady': 2, 'silent': 3}
TODAY = D(E['date'])
W0, W1 = D(E['window'][0]), TODAY


def day(d, year=False):
    d = D(d) if isinstance(d, str) else d
    return f"{d.day} {d.strftime('%b')}" + (f" {d.year}" if year else '')


def stations():
    for line in E['lines']:
        for st in line['stations']:
            yield line, st


# ---------------------------------------------------------------- glyph sprite
# The four calls at text size: drawn in a 26 x 16 box, stroked in currentColor.
SPRITE = '''<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>
<symbol id="call-steady" viewBox="0 0 26 16"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M2 13q1.6-.4 3.2-6"/><path d="M8.5 11.5q1.6-.4 3.2-6"/><path d="M15 10q1.6-.4 3.2-6"/><path d="M21.5 8.5q1.6-.4 3.2-6"/></g></symbol>
<symbol id="call-watch" viewBox="0 0 26 16"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M2 13q1.6-.4 3.2-6"/><path d="M15 12q1.1-.3 2.2-4"/><path d="M21.5 13.5q.7-.2 1.4-2.4"/></g></symbol>
<symbol id="call-alert" viewBox="0 0 26 16"><g stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M3 1.5v13M7.5 1.5v13M16 1.5v13M20.5 1.5v13"/></g></symbol>
<symbol id="call-silent" viewBox="0 0 26 16"><path d="M1.5 8h23" stroke="currentColor" stroke-width="1.6" stroke-dasharray="2 3"/></symbol>
<symbol id="ln-water" viewBox="0 0 24 24"><path d="M12 3c3.5 4.6 6 8 6 11a6 6 0 0 1-12 0c0-3 2.5-6.4 6-11z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></symbol>
<symbol id="ln-air" viewBox="0 0 24 24"><path d="M3 9h11a3 3 0 1 0-3-3M3 13h15a3 3 0 1 1-3 3M3 17h7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></symbol>
<symbol id="ln-power" viewBox="0 0 24 24"><path d="M13 2 5 13.5h6L10 22l8-11.5h-6z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></symbol>
<symbol id="ln-health" viewBox="0 0 24 24"><path d="M9 3h6v6h6v6h-6v6H9v-6H3V9h6z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></symbol>
<symbol id="i-down" viewBox="0 0 16 16"><path d="M8 3v10M3.5 8.5 8 13l4.5-4.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></symbol>
<symbol id="i-right" viewBox="0 0 16 16"><path d="M3 8h10M8.5 3.5 13 8l-4.5 4.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></symbol>
<symbol id="i-bell" viewBox="0 0 16 16"><path d="M8 2.5a4 4 0 0 1 4 4V10l1.5 2h-11L4 10V6.5a4 4 0 0 1 4-4zM6.5 14h3" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></symbol>
<symbol id="i-ear" viewBox="0 0 16 16"><path d="M4.5 6a3.5 3.5 0 1 1 6.4 2c-.9 1.3-1.9 1.9-1.9 3.4A2 2 0 0 1 7 13.5M6.6 6.2a1.4 1.4 0 1 1 2.4 1" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></symbol>
</defs></svg>'''


def call(s, cls=''):
    return f'<svg class="call {s} {cls}" aria-hidden="true"><use href="#call-{s}"/></svg>'


def wordmark(cls='wm', label='Canary Palestine'):
    w = MARKS['wordmark']
    return (f'<svg class="{cls}" viewBox="0 0 {w["w"]} {w["h"]}" role="img" aria-label="{label}">'
            f'<path class="h" d="{w["head"]}" fill-rule="evenodd"/><path class="l" d="{w["letters"]}"/><path class="p" d="{w["pal"]}"/></svg>')


# ---------------------------------------------------------------- the sonogram
class G:
    """Sonogram geometry. The desktop drawing shows 30 days with named lanes; the phone drawing
    shows the last 14 days with lane codes only, so its type stays readable at 375 px."""
    def __init__(self, compact=False):
        self.compact = compact
        self.SW, self.LX, self.RX = (358, 34, 10) if compact else (780, 150, 22)
        self.LH, self.BG = (16, 22) if compact else (16, 23)
        self.W0 = TODAY - dt.timedelta(days=13) if compact else W0
        self.DAYS = (TODAY - self.W0).days + 1
        self.DX = (self.SW - self.LX - self.RX) / self.DAYS
        self.id = 'sono-m' if compact else 'sono'

    def x(self, d):
        d = D(d) if isinstance(d, str) else d
        return self.LX + ((d - self.W0).days + 0.5) * self.DX


def static(g, y1):
    """The sonograph's grain: faint specks over the drawing area, the same every build."""
    import random
    rnd = random.Random(20261020)
    d = []
    for _ in range(420 if g.compact else 900):
        x = g.LX + rnd.random() * (g.SW - g.RX - g.LX)
        yy = 30 + rnd.random() * (y1 - 30)
        w = 0.6 + rnd.random() * 2.4
        d.append(f'M{x:.1f} {yy:.1f}h{w:.1f}')
    return f'<path class="grain" d="{"".join(d)}"/>'


def note_path(s, x, cy):
    """A report as its call, centred on x in a lane centred on cy."""
    if s == 'steady':
        return ''.join(f'M{x - 8 + i * 5.2:.1f} {cy + 5.5 - i * 1.8:.1f}q1.4 -.3 2.8 -6' for i in range(3))
    if s == 'watch':
        return f'M{x - 8:.1f} {cy + 5.5:.1f}q1.4 -.3 2.8 -6M{x + 2.4:.1f} {cy + 3.5:.1f}q1 -.2 2 -3.8M{x + 6.8:.1f} {cy + 6:.1f}q.5 -.1 1 -2'
    if s == 'alert':
        return ''.join(f'M{x + dx:.1f} {cy - 7:.1f}V{cy + 7:.1f}' for dx in (-7, -3.6, 2.4, 5.8))
    return ''


def sonogram(compact=False):
    g = G(compact)
    y = 26
    parts, reps, lanes = [], [], []
    for line in E['lines']:
        y += g.BG
        name = line['name'].upper().replace(' & WASTE', '') if compact else line['name'].upper()
        parts.append(f'<text class="band-l" x="0" y="{y - 6}">{esc(name)}</text>')
        for st in line['stations']:
            cy = y + g.LH / 2
            lanes.append((st, cy))
            short = '' if compact else f' <tspan fill="#6E7469">{esc(st["short"])}</tspan>'
            parts.append(f'<text class="lane-l" x="0" y="{cy + 3.5:.1f}">{st["code"]}{short}</text>')
            parts.append(f'<path class="hum" d="M{g.LX} {cy:.1f}H{g.SW - g.RX + 6}"/>')
            for d, s in st['history']:
                if D(d) < g.W0:
                    continue
                x = g.x(d)
                lab = f'{st["code"]}, {st["place"]}, {st["subject"]}: {LABEL[s].lower()} on {day(d)}'
                if d == st['date']:
                    lab += f'. Reading {st["reading"]}'
                v = st['reading'] if d == st['date'] else LABEL[s]
                reps.append(
                    f'<a class="rep {s}" href="#{st["code"].lower()}" data-s="{s}" data-line="{line["key"]}" data-x="{x:.1f}" '
                    f'data-code="{st["code"]}" data-date="{day(d)}" data-label="{LABEL[s]}" data-place="{esc(st["place"])} · {esc(st["subject"])}" '
                    f'data-v="{esc(v)}" style="--d:{350 + int((x - g.LX) * (3 if compact else 1.4))}" aria-label="{esc(lab)}">'
                    f'<rect class="hit" x="{x - 10:.1f}" y="{cy - 9:.1f}" width="20" height="18"/>'
                    f'<path class="n {s}" d="{note_path(s, x, cy)}"/></a>')
            if st['status'] == 'silent':
                xs = max(g.x(st['silent_since']), g.LX - 9)
                xe = g.x(TODAY)
                n = (TODAY - D(st['silent_since'])).days
                parts.append(f'<path class="quiet" d="M{xs + 9:.1f} {cy - 5:.1f}v10M{xs + 9:.1f} {cy:.1f}H{xe:.1f}M{xe:.1f} {cy - 5:.1f}v10"/>')
                if xe - xs > 120:
                    parts.append(f'<text class="quiet-t" x="{(xs + 9 + xe) / 2:.1f}" y="{cy - 3:.1f}" text-anchor="middle" paint-order="stroke" '
                                 f'stroke="#0E100D" stroke-width="5">SILENT {n} DAYS</text>')
            y += g.LH
    H = y + 30
    grid, ax = [], []
    for i in range(g.DAYS):
        d = g.W0 + dt.timedelta(days=i)
        x = g.LX + i * g.DX
        grid.append(f'<path class="day{" wk" if d.weekday() == 0 else ""}" d="M{x:.1f} 30V{y + 4}"/>')
        if (d.weekday() == 0 or i == 0) and (TODAY - d).days > 3:
            ax.append(f'<text class="ax" x="{x + 2:.1f}" y="{y + 20}">{day(d).upper()}</text>')
    xn = g.x(TODAY)
    lead_codes = set(E['lead']['codes'])
    leadbox = ''.join(f'<rect class="lead-mark" x="{g.x(st["date"]) - 12:.1f}" y="{cy - 10:.1f}" width="24" height="20"/>'
                      for st, cy in lanes if st['code'] in lead_codes and D(st['date']) >= g.W0)
    n_st = sum(1 for _ in stations())
    desc = (f'A sonogram of the network. Time runs left to right from {day(g.W0)} to today, {day(TODAY)}. '
            "Each row is a station; each mark is a report drawn as the canary's call: an alarm call for an alert, "
            'a breaking song for a watch, a full song for steady. A dotted bracket is a silence: no report since that date.')
    return (f'<svg class="{"sono-m" if compact else "sono-d"}" viewBox="0 0 {g.SW} {H}" width="{g.SW}" height="{H}" '
            f'data-x0="{g.LX}" data-x1="{g.SW - g.RX}" role="group" aria-labelledby="{g.id}-t" aria-describedby="{g.id}-d">'
            f'<title id="{g.id}-t">The listening post: every report on {n_st} stations over {g.DAYS} days</title>'
            f'<desc id="{g.id}-d">{esc(desc)}</desc>'
            f'<text class="ax" x="{g.LX}" y="12">{day(g.W0).upper()}</text>'
            f'<text class="now-t" x="{xn}" y="12" text-anchor="end">TODAY {E["sweep"]}</text>' + static(g, y)
            + ''.join(grid) + ''.join(parts) + leadbox +
            f'<path class="now-l" d="M{xn:.1f} 18V{y + 4}"/>'
            + ''.join(ax) +
            f'<g class="reps">{"".join(reps)}</g>'
            f'<line class="head-play" x1="{g.LX}" x2="{g.LX}" y1="20" y2="{y + 4}"/></svg>')


def lane(st):
    """A station's month as a 1-line strip for its card."""
    w, h, cy = 240, 16, 8
    days = (TODAY - W0).days + 1
    x = lambda d: 4 + ((D(d) - W0).days + 0.5) / days * (w - 8)
    out = [f'<path class="base" d="M4 {cy}H{w - 4}"/>']
    for d, s in st['history']:
        if D(d) < W0:
            continue
        xx = x(d)
        if s == 'alert':
            out.append(f'<path class="n" d="M{xx - 2.5:.1f} 2V14M{xx + 1:.1f} 2V14" stroke-width="2"/>')
        elif s == 'watch':
            out.append(f'<path class="n" d="M{xx - 4:.1f} 12.5q1 -.3 2 -4.5M{xx + 2:.1f} 13q.5 -.2 1 -2.5"/>')
        else:
            out.append(f'<path class="n" d="M{xx - 4:.1f} 12.5q1 -.3 2 -4.5M{xx:.1f} 11q1 -.3 2 -4.5"/>')
    if st['status'] == 'silent':
        out.append(f'<path class="q" d="M{x(st["silent_since"]) + 4:.1f} {cy}H{w - 4}"/>')
    return (f'<svg class="lane" viewBox="0 0 {w} {h}" preserveAspectRatio="none" role="img" '
            f'aria-label="{len([1 for d, _ in st["history"] if D(d) >= W0])} reports in the last 30 days">{"".join(out)}</svg>')


# ---------------------------------------------------------------- page parts
def plate(st):
    """No photograph: the station's call, printed large on the paper, with its code."""
    s = st['status']
    return (f'<figure class="st-ph"><div class="plate" data-s="{s}">{call(s, "big")}<span class="g">{st["code"]}</span></div>'
            f'<figcaption>No photograph. {esc(st["place"])}.</figcaption></figure>')


def station_card(line, st, plates=False):
    s = st['status']
    if s == 'silent':
        n = (TODAY - D(st['silent_since'])).days
        val = f'<p class="val">{n} days<small>since the last report, {day(st["silent_since"])}</small></p>'
    else:
        val = f'<p class="val{" word" if st.get("word") else ""}">{esc(st["reading"])}</p>'
    src = '' if s == 'silent' and not st.get('url') else \
        f'<p class="src">{esc(st["source"])} · <a href="{esc(st["url"])}" rel="noopener">{day(st["date"])}</a></p>'
    fig = f'<figure class="st-ph">{photo(st.get("photo"), "r32")}{caption(st.get("photo"), True)}</figure>' if has(st.get('photo')) else (plate(st) if plates else '')
    return (f'<article class="st{" has-ph" if fig else ""}" id="{st["code"].lower()}" data-s="{s}" aria-labelledby="h-{st["code"].lower()}">'
            f'{fig}<div class="st-top"><span class="code">{st["code"]}</span><span class="chip lab">{call(s)}{LABEL[s]}</span></div>'
            f'<h4 id="h-{st["code"].lower()}">{esc(st["place"])}<span class="sr"> · </span><span class="p">{esc(st["subject"])}</span></h4>'
            f'{val}<p class="what">{esc(st["what"])}</p>{lane(st)}{src}</article>')


def photo(slug, ratio='r43', pos=None, eager=False):
    if not slug or slug not in PHOTOS:
        return ''
    pos = pos or PH[slug].get('pos')
    p = PHOTOS[slug]
    style = f' style="object-position:{pos}"' if pos else ''
    return (f'<div class="scan {ratio}"><img src="assets/img/photo/{slug}.webp?v={V}" width="{p["w"]}" height="{p["h"]}" '
            f'alt="{esc(PH[slug]["alt"])}" loading="{"eager" if eager else "lazy"}" decoding="async"{style}></div>')


def caption(slug, short=False):
    if not slug or slug not in PHOTOS:
        return ''
    c = PH[slug]
    if short:
        return f'<figcaption><b>{esc(c["year"])}</b>{esc(c["place"])}. Photo: {esc(c["credit"])}</figcaption>'
    return f'<figcaption><b>{esc(c["year"])}</b>{esc(c["caption"])} Photo: {esc(c["credit"])}</figcaption>'


def has(slug):
    return bool(slug) and slug in PHOTOS


def page():
    tally = {k: 0 for k in RANK}
    for _, st in stations():
        tally[st['status']] += 1
    n_st = sum(tally.values())
    worst = min((st['status'] for _, st in stations() if st['status'] != 'silent'), key=RANK.get)
    L = E['lead']
    lead_st = {st['code']: st for _, st in stations()}
    reading = lead_st[L['codes'][0]]

    nav = ''.join(f'<li><a href="#rack-{l["key"]}"><span class="code">{l["code"]}</span>{esc(l["name"])}</a></li>' for l in E['lines'])
    nav += '<li><a href="#silence">Silence</a></li><li><a href="#reporting">Reporting</a></li>'

    newest = ''.join(
        f'<li><a href="#{n["code"].lower()}">{photo(n.get("photo"), "thumb") if has(n.get("photo")) else '<span class="scan thumb none"></span>'}'
        f'<span class="nt"><span class="g"><time datetime="{n["date"]}">{day(n["date"])}</time> · <span class="code">{n["code"]}</span></span>{esc(n["text"])}</span></a></li>'
        for n in E['newest'])

    racks = []
    for line in E['lines']:
        sts = line['stations']
        plates = any(has(st.get('photo')) for st in sts)
        cells = ''.join(station_card(line, st, plates) for st in sts)
        wide = ' three' if len(sts) % 3 == 0 and len(sts) > 3 else (' wide' if len(sts) > 4 else '')
        racks.append(f'<section class="rack" id="rack-{line["key"]}" aria-labelledby="rk-{line["key"]}"><div class="rack-l">'
                     f'<h3 id="rk-{line["key"]}"><svg aria-hidden="true"><use href="#ln-{line["key"]}"/></svg>{esc(line["name"])}</h3>'
                     f'<p class="g">{len(sts)} stations</p></div><div class="cells{wide}" style="--n:{len(sts)}">{cells}</div></section>')

    silent = [st for _, st in stations() if st['status'] == 'silent']
    quiet = ''.join(
        f'<div class="q"><p class="code">{st["code"]} · {esc(st["place"]).upper()}</p>'
        f'<p class="days">{(TODAY - D(st["silent_since"])).days}<small>days</small></p>'
        f'<p>{esc(st["subject"])}: {esc(st["what"])}</p><p class="last">Last report {day(st["silent_since"], True)} · {esc(st.get("source", ""))}</p></div>'
        for st in silent)

    F = E['feature']
    feat_body = ''.join(f'<p>{esc(p)}</p>' for p in F['body'])
    cards = []
    for c in E['cards']:
        fig = f'<figure>{photo(c["photo"], "r43")}{caption(c["photo"])}</figure>' if has(c.get('photo')) else ''
        extra = ''
        if c.get('points'):
            extra = '<ul class="pts">' + ''.join(f'<li><b>{esc(a)}</b><span>{esc(b)}</span></li>' for a, b in c['points']) + '</ul>'
        cards.append(f'<article class="card" data-s="{c["s"]}" aria-labelledby="c-{c["id"]}">{fig}'
                     f'<p class="kick lab"><span class="tag">{call(c["s"])}{esc(c["codes"])}</span>{esc(c["kicker"])}</p>'
                     f'<h3 id="c-{c["id"]}" class="hl"><a href="{esc(c["url"])}" rel="noopener">{esc(c["headline"])}</a></h3>'
                     f'{"<p class=sum>" + esc(c["summary"]) + "</p>" if c.get("summary") else ""}{extra}'
                     f'<p class="src">{esc(c["src"])}</p></article>')

    more = ''.join(
        f'<article class="mr" data-s="{m["s"]}"><a href="{esc(m["url"])}" rel="noopener">{photo(m.get("photo"), "r32")}'
        f'<p class="kick lab"><span class="tag">{call(m["s"])}{esc(m["codes"])}</span>{day(m["date"])}</p>'
        f'<h3 class="hl">{esc(m["headline"])}</h3></a><p class="src">{esc(m["src"])}</p></article>'
        for m in E.get('more', []))

    picks = ''.join(f'<li class="pick"><input type="checkbox" id="pk-{st["code"].lower()}" name="st" value="{st["code"]}"{" checked" if st["code"] in L["codes"] else ""}>'
                    f'<span><span class="code">{st["code"]}</span>{esc(st["short"])}</span></li>'
                    for _, st in stations() if st['status'] != 'silent') + \
            ''.join(f'<li class="pick"><input type="checkbox" id="pk-{st["code"].lower()}" name="st" value="{st["code"]}">'
                    f'<span><span class="code">{st["code"]}</span>{esc(st["short"])} · silent</span></li>' for st in silent)

    first_head = '<path class="hd" fill="currentColor" fill-rule="evenodd" d=""/>'
    # the song call exactly as the mark draws it, scaled from the mark's 56-unit head to the loader's head
    k = 0.1 * 1088 / 56
    first_notes = (f'<g transform="translate({80 - 32 * k:.2f} {66 - 32 * k:.2f}) scale({k:.4f})">' +
                   ''.join(f'<path class="note" stroke-width="{MARKS["callStroke"]}" d="{d}"/>' for d in MARKS['call']['song']['call']) + '</g>')

    desc = E['description']
    title = f'Canary Palestine · {E["weekday"]} {day(E["date"], True)}'
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#0E100D">
<meta property="og:type" content="website">
<meta property="og:title" content="Canary Palestine">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="https://taktek-dev.github.io/canary-palestine-prototype/assets/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="favicon.svg?v={V}" type="image/svg+xml">
<link rel="preload" href="assets/fonts/geologica.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/martian-mono.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/cp.css?v={V}">
<script>document.documentElement.classList.add('js')</script>
</head>
<body>
{SPRITE}
<a class="skip" href="#main">Skip to the reports</a>
<div class="first" aria-hidden="true">
  <svg viewBox="0 0 300 150">{first_head}{first_notes}<path class="stylus" d="M0 128H300"/><text class="cap" x="150" y="146" text-anchor="middle" style="opacity:0">LISTENING · {n_st} STATIONS · {E["sweep"]} JERUSALEM</text></svg>
</div>

<div class="top">
  <div class="util"><div class="wrap">
    <p class="g"><time datetime="{E["date"]}">{E["weekday"]} {day(E["date"], True)}</time><span>Last sweep <b>{E["sweep"]}</b> Jerusalem</span></p>
    <p class="tally g" aria-label="Network today: {tally["alert"]} alert, {tally["watch"]} watch, {tally["steady"]} steady, {tally["silent"]} silent">
      <span>{call("alert")}<b>{tally["alert"]}</b> alert</span><span>{call("watch")}<b>{tally["watch"]}</b> watch</span><span>{call("steady")}<b>{tally["steady"]}</b> steady</span><span>{call("silent")}<b>{tally["silent"]}</b> silent</span></p>
  </div></div>
  <header class="mast"><div class="wrap">
    <a class="brand" href="./home.html" aria-label="Canary Palestine, home">{wordmark()}
      <span class="now g" aria-hidden="true">{call(worst)}<span>{n_st} stations</span></span></a>
    <nav class="nav" aria-label="Sections"><ul>{nav}</ul></nav>
    <div class="acts">
      <button class="btn ghost" type="button" data-hear="jump" aria-pressed="false" data-on="Stop" data-off="Hear the network"><svg aria-hidden="true"><use href="#i-ear"/></svg><span class="lbl">Hear the network</span></button>
      <a class="btn hot" href="#alerts"><svg aria-hidden="true"><use href="#i-bell"/></svg>Station alerts</a>
    </div>
  </div></header>
</div>

<main id="main">
  <section class="post" aria-label="The listening post">
    <div class="wrap post-grid">
      <article class="lead" data-s="{L["status"]}" aria-labelledby="lead-h">
        {f'<figure class="lead-ph rise" style="--i:0">{photo(L.get("photo"), "r21", eager=True)}{caption(L.get("photo"), True)}</figure>' if has(L.get('photo')) else ''}
        <p class="status lab rise" style="--i:0">{call(L["status"])}<span>{LABEL[L["status"]]} · {" + ".join(L["codes"])}</span><span class="bg">{esc(L["when"])}</span></p>
        <h1 id="lead-h" class="hl rise" style="--i:1"><a href="#{L["codes"][0].lower()}">{esc(L["headline"])}</a></h1>
        <p class="dek rise" style="--i:2">{esc(L["dek"])}</p>
        <div class="reading rise" style="--i:3"><p class="v">{esc(reading["reading"])}</p><p>{esc(L["reading_note"])}</p></div>
        <p class="src g rise" style="--i:4">{esc(L["src"])}</p>
        <a class="more rise" style="--i:5" href="#reporting">Read the report<svg aria-hidden="true"><use href="#i-down"/></svg></a>

      </article>
      <div class="net">
        <div class="sono-h rise" style="--i:1">
          <div><h2>The listening post</h2><p>Every report on the network in the last <span class="d-only">30</span><span class="m-only">14</span> days, drawn as the canary's call. Hover or tab through a mark; follow it to the station.</p></div>
          <button class="btn play" type="button" data-hear="here" aria-pressed="false" data-on="Stop" data-off="Hear the month"><svg class="ico" aria-hidden="true"><use href="#i-ear"/></svg><span class="eq" aria-hidden="true"><i></i><i></i><i></i></span><span class="lbl">Hear the month</span></button>
        </div>
        <div class="sono">{sonogram()}{sonogram(True)}<div class="tip" aria-hidden="true"></div></div>
        <ul class="calls" aria-label="How a status sounds">
          <li>{call("alert")}<b>Alert</b> harm reported now</li>
          <li>{call("watch")}<b>Watch</b> damage, loss or risk</li>
          <li>{call("steady")}<b>Steady</b> working, restored, added</li>
          <li>{call("silent")}<b>Silent</b> no recent report</li>
        </ul>
        <p class="fine">Statuses are the desk's reading of named reports, not official alerts.</p>
        <section class="newest rise" style="--i:6" aria-labelledby="new-h"><h2 id="new-h" class="lab">Newest reports</h2><ol>{newest}</ol></section>
      </div>
    </div>
  </section>

  <section class="reg paper" aria-labelledby="reg-h">
    <div class="wrap">
      <div class="sec-h"><h2 id="reg-h">Latest readings</h2><p>Each station is one place and one thing the desk listens to. The strip under a reading is its month.</p></div>
      {"".join(racks)}
    </div>
  </section>

  <section class="silence" id="silence" aria-labelledby="sil-h">
    <div class="wrap silence-grid">
      <div><svg class="shut" viewBox="0 0 64 64" aria-hidden="true"><path d="{MARKS["call"]["silent"]["head"]}" fill-rule="evenodd"/></svg><h2 id="sil-h">{esc(E["silence"]["title"])}</h2><p class="say">{esc(E["silence"]["say"])}</p></div>
      <div class="ql">{quiet}</div>
    </div>
  </section>

  <section class="inv paper" id="reporting" aria-labelledby="inv-h">
    <div class="wrap">
      <div class="sec-h"><h2 id="inv-h">Reporting</h2><p>The stories behind the readings, each sourced to the report it rests on.</p></div>
      <article class="feat" data-s="{F["s"]}" aria-labelledby="f-h">
        <figure>{photo(F["photo"], "r43", eager=False)}{caption(F["photo"])}</figure>
        <div>
          <p class="kick lab"><span class="tag">{call(F["s"])}{esc(F["codes"])}</span>{esc(F["kicker"])}</p>
          <h2 id="f-h" class="hl">{esc(F["headline"])}</h2>
          <div class="body">{feat_body}</div>
        </div>
      </article>
      <div class="cards">{"".join(cards)}</div>
      {'<div class="more-h"><h3 class="lab">More from the network</h3></div><div class="mores">' + more + '</div>' if more else ''}
    </div>
  </section>

  <section class="alerts" id="alerts" aria-labelledby="al-h">
    <div class="wrap alerts-grid">
      <div><h2 id="al-h">Station alerts</h2><p class="say">Follow the stations you care about. When one of them changes its call, the desk writes to you once, with the report it rests on.</p></div>
      <form action="#" novalidate>
        <fieldset><legend class="lab">Stations to follow</legend><ul class="picks">{picks}</ul></fieldset>
        <div class="sub"><label><span class="sr">Email address</span><input type="email" name="email" autocomplete="email" placeholder="you@example.org" required></label>
          <button class="btn" type="submit">Follow<svg aria-hidden="true"><use href="#i-right"/></svg></button></div>
        <p class="note" aria-live="polite"></p>
      </form>
    </div>
  </section>
</main>

<footer class="foot">
  <div class="wrap">
    <div class="foot-grid">
      <div><a href="./home.html" aria-label="Canary Palestine, home">{wordmark("wm")}</a>
        <p class="about">{esc(E["about"])}</p></div>
      <nav aria-labelledby="fn-1"><h2 id="fn-1" class="lab">Network</h2><ul>{"".join(f'<li><a href="#rack-{l["key"]}">{esc(l["name"])}</a></li>' for l in E["lines"])}</ul></nav>
      <nav aria-labelledby="fn-2"><h2 id="fn-2" class="lab">Desk</h2><ul><li><a href="#reporting">Reporting</a></li><li><a href="index.html#calls">How statuses are set</a></li><li><a href="#">Corrections</a></li><li><a href="#">Send a report</a></li></ul></nav>
      <nav aria-labelledby="fn-3"><h2 id="fn-3" class="lab">Follow</h2><ul><li><a href="#alerts">Station alerts</a></li><li><a href="#">Telegram</a></li><li><a href="#">RSS</a></li><li><a href="index.html">The identity</a></li></ul></nav>
    </div>
    <div class="fine g"><p>© 2026 Canary Palestine · prototype</p><p>Statuses are the desk's reading of named reports, not official alerts.</p></div>
  </div>
</footer>
<script src="assets/js/marks.js?v={V}"></script>
<script src="assets/js/voice.js?v={V}" defer></script>
<script src="assets/js/cp.js?v={V}" defer></script>
</body>
</html>
'''


if __name__ == '__main__':
    open(os.path.join(ROOT, 'home.html'), 'w', encoding='utf-8').write(page())
    print('home.html', os.path.getsize(os.path.join(ROOT, 'home.html')) // 1024, 'KB')
