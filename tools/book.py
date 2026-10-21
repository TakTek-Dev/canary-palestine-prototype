"""Build index.html, the identity book, from the same marks, tokens and edition as the site.

python -I tools/book.py   (after brand.py and build.py)
"""
import math
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import brand  # noqa: E402
import build  # noqa: E402
from build import E, MARKS, PHOTOS, PH, V, call, esc, wordmark, day, D, LABEL  # noqa: E402

ROOT = build.ROOT


def construction():
    """The head drawn on its grid: x-height lines, the ring's centre line, the beak and eye angles."""
    s = 0.24
    W, H = 560, 380
    cx, cy = 200, 196
    ro, ri, rm = brand.R_OUT * s, (brand.R_OUT - brand.STEM) * s, brand.R_MID * s
    top, bot = cy - ro, cy + ro
    hd = brand.head(cx, cy, s)
    ray = lambda a, r: (cx + r * math.cos(math.radians(a)), cy - r * math.sin(math.radians(a)))
    lo = ray(brand.BEAK[0], ro + 70)
    hi = ray(brand.BEAK[1], ro + 70)
    ey = ray(brand.EYE_AT, rm)
    eo = ray(brand.EYE_AT, ro + 46)
    out = [
        f'<path class="gd" d="M0 {top:.1f}H{W}M0 {bot:.1f}H{W}M0 {cy:.1f}H{W}"/>',
        f'<text x="0" y="{top - 6:.1f}">x-height, overshoot</text>',
        f'<text x="0" y="{bot + 16:.1f}">baseline, overshoot</text>',
        f'<circle class="gd" cx="{cx}" cy="{cy}" r="{ro:.1f}"/><circle class="gd" cx="{cx}" cy="{cy}" r="{ri:.1f}"/>',
        f'<circle class="gd2" cx="{cx}" cy="{cy}" r="{rm:.1f}"/>',
        f'<path class="hd" d="{hd}" fill-rule="evenodd"/>',
        f'<path class="gd2" d="M{cx} {cy}L{lo[0]:.1f} {lo[1]:.1f}M{cx} {cy}L{hi[0]:.1f} {hi[1]:.1f}M{cx} {cy}L{eo[0]:.1f} {eo[1]:.1f}"/>',
        f'<text x="{lo[0] + 6:.1f}" y="{lo[1] + 4:.1f}">lower mandible {brand.BEAK[0]}°</text>',
        f'<text x="{hi[0] + 6:.1f}" y="{hi[1]:.1f}">upper mandible {brand.BEAK[1]}°</text>',
        f'<text x="{eo[0] + 6:.1f}" y="{eo[1] - 2:.1f}">eye on the stroke\'s centre line, {brand.EYE_AT}°</text>',
        f'<path class="gd2" d="M{cx - ro:.1f} {bot + 34:.1f}H{cx - ri:.1f}"/>',
        f'<text x="{cx - ro:.1f}" y="{bot + 50:.1f}">stroke {brand.STEM} u</text>',
    ]
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Construction of the head on Geologica\'s x-height">{"".join(out)}</svg>'


def singer():
    """The cover's head, singing: drawn by book.js with canaryHead(); the notes are the song call."""
    k = 0.2 * 1088 / 56
    notes = ''.join(f'<path class="n" stroke-width="{MARKS["callStroke"]}" d="{d}"/>' for d in MARKS['call']['song']['call'])
    return (f'<svg class="singer" viewBox="0 0 520 300" aria-hidden="true"><path class="hd" fill="currentColor" fill-rule="evenodd" d="{brand.head(150, 150, 0.2)}"/>'
            f'<g transform="translate({150 - 32 * k:.2f} {150 - 32 * k:.2f}) scale({k:.4f})">{notes}</g>'
            f'<path class="stylus" d="M0 270H520"/></svg>')


def zip_kit():
    path = os.path.join(ROOT, 'assets', 'brand', 'canary-palestine-identity.zip')
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(os.path.join(ROOT, 'assets', 'brand'))):
            if f.endswith('.svg'):
                z.write(os.path.join(ROOT, 'assets', 'brand', f), 'marks/' + f)
        for f in ('geologica.woff2', 'martian-mono.woff2', 'OFL-Geologica.txt', 'OFL-MartianMono.txt'):
            z.write(os.path.join(ROOT, 'assets', 'fonts', f), 'fonts/' + f)
        z.write(os.path.join(ROOT, 'favicon.svg'), 'marks/favicon.svg')
    return os.path.getsize(path) // 1024


COLOURS = [
    ('Coal', '#0E100D', 'oklch(16.5% 0.008 130)', 'The board. Where the network is listened to: masthead, the listening post, alerts, footer.', '#ECEEE6'),
    ('Canary', '#F2DA1C', 'oklch(88.6% 0.18 101)', 'The bird. Only what calls for attention: alerts, the lead, the silence band, focus.', '#0E100D'),
    ('Sonograph paper', '#EDEEE8', 'oklch(94.5% 0.007 115)', 'Where reports are read. The grey-white of the paper a Sona-Graph burned its traces into.', '#161814'),
    ('Trace', '#161814', 'oklch(19.6% 0.008 130)', 'Text and lines on paper: the stylus mark.', '#EDEEE8'),
]
TONES = [('Coal 2', '#151814', '#ECEEE6'), ('Coal 3', '#1D211C', '#ECEEE6'), ('Seam', '#2D322B', '#ECEEE6'), ('Ash', '#959B90', '#0E100D'),
         ('Chalk', '#ECEEE6', '#0E100D'), ('Paper 2', '#E3E4DC', '#161814'), ('Rule', '#C6C9BF', '#161814'), ('Graphite', '#50554D', '#EDEEE8')]
PAIRS = [('Chalk on coal', '#ECEEE6', '#0E100D', '16.3'), ('Ash on coal', '#959B90', '#0E100D', '6.7'), ('Canary on coal', '#F2DA1C', '#0E100D', '13.5'),
         ('Coal on canary', '#0E100D', '#F2DA1C', '13.5'), ('Trace on paper', '#161814', '#EDEEE8', '15.3'), ('Graphite on paper', '#50554D', '#EDEEE8', '6.6'),
         ('Canary ink on paper', '#5E5300', '#EDEEE8', '6.6')]

CALLS = [
    ('song', 'steady', 'Song', 'Working, restored or added. A trill of rising notes, even and unbroken: the canary is singing, the air is good.'),
    ('strained', 'watch', 'Strained', 'Damage, loss or a risk reported. The trill breaks: a note drops out, the last ones fall and shorten.'),
    ('alarm', 'alert', 'Alarm', 'Harm reported now. Short broadband chips in pairs, the shape an alarm call takes on a sonogram: tall, abrupt, the whole height of the band.'),
    ('silent', 'silent', 'Silent', 'No recent report. No call, and the beak is shut. The desk never fills a silence with a guess; it counts the days.'),
]


def page():
    ch = [('idea', 'The idea'), ('mark', 'The mark'), ('calls', 'The calls'), ('wordmark', 'Wordmark'), ('colour', 'Colour'),
          ('type', 'Type'), ('sonogram', 'Sonogram'), ('photos', 'Photographs'), ('motion', 'Motion & sound'),
          ('apps', 'Applications'), ('voice', 'Voice')]
    nav = ''.join(f'<li><a href="#{k}"><span class="g">{i:02d}</span>{t}</a></li>' for i, (k, t) in enumerate(ch, 1))
    no = lambda i, t: f'<p class="no"><span>{i:02d}</span><span>{t.upper()}</span></p>'
    kit = zip_kit()

    stations = list(build.stations())
    n_st = len(stations)
    lead = {st['code']: st for _, st in stations}[E['lead']['codes'][0]]
    silent = [st for _, st in stations if st['status'] == 'silent']
    sil = silent[0] if silent else None
    feat_photo = E['feature']['photo']
    has_photo = feat_photo in PHOTOS

    calls = ''.join(
        f'<article class="cc"><img src="assets/brand/mark-{k}.svg?v={V}" width="150" height="64" alt="The {t.lower()} mark: the head followed by {build.CALL[s]}">'
        f'<h3>{t}</h3><p class="s g">STATUS · {LABEL[s].upper()}</p><p>{d}</p><div class="spacer"></div>'
        + (f'<button class="btn" type="button" data-call="{s}"><svg aria-hidden="true"><use href="#i-ear"/></svg>Hear it</button>' if s != 'silent' else
           '<button class="btn" type="button" disabled>Nothing to hear</button>') + '</article>'
        for k, s, t, d in CALLS)

    colours = ''.join(
        f'<div class="sw"><div class="chip-c" style="background:{h};color:{fg}">{h}</div><dl><dt>{n}</dt><dd>{h} · {ok}</dd><p>{d}</p></dl></div>'
        for n, h, ok, d, fg in COLOURS)
    tones = ''.join(f'<div style="background:{h};color:{fg}"><b>{n}</b><span>{h}</span></div>' for n, h, fg in TONES)
    pairs = ''.join(f'<li><span class="demo" style="background:{bg};color:{fg}">{n}</span><span class="g">{fg} / {bg}</span><span class="ok">{r}:1 AA</span></li>'
                    for n, fg, bg, r in PAIRS)

    ba = f'<figure>{build.photo(feat_photo, "r32")}{build.caption(feat_photo)}</figure>' if has_photo else ''

    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Canary Palestine · Identity</title>
<meta name="description" content="The visual identity of Canary Palestine, an early-warning newsroom for water, air, power and health in Gaza and the West Bank: the singing head, the four calls, the listening post.">
<meta name="theme-color" content="#0E100D">
<meta property="og:title" content="Canary Palestine · Identity">
<meta property="og:description" content="A canary sings while the air is good. Silence is the signal.">
<meta property="og:image" content="https://taktek-dev.github.io/canary-palestine-prototype/assets/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="favicon.svg?v={V}" type="image/svg+xml">
<link rel="preload" href="assets/fonts/geologica.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/martian-mono.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/cp.css?v={V}">
<link rel="stylesheet" href="assets/css/book.css?v={V}">
<script>document.documentElement.classList.add('js')</script>
</head>
<body class="book">
{build.SPRITE}
<a class="skip" href="#idea">Skip to the book</a>
<header class="bk-top"><div class="wrap">
  <a href="#top" aria-label="Canary Palestine identity, top">{wordmark()}</a>
  <nav aria-label="Chapters"><ol>{nav}</ol></nav>
  <a class="site" href="home.html"><span>The homepage</span><svg aria-hidden="true"><use href="#i-right"/></svg></a>
</div></header>

<main>
<section class="cover" id="top" aria-labelledby="cv-h">
  <div class="wrap stage">
    <div>{wordmark("big", "Canary Palestine")}</div>
    <div>{singer()}<h1 id="cv-h">An identity for <b>Canary Palestine</b>, built from the bird it is named after: <b>it sings while the air is good, and its silence is the warning.</b></h1></div>
  </div>
  <div class="wrap"><p class="meta g"><span>IDENTITY · VERSION 1 · {day(E["date"], True).upper()}</span><span>WATER · AIR &amp; WASTE · POWER · HEALTH</span><span>GAZA STRIP · WEST BANK</span></p></div>
</section>

<section class="ch idea paper" id="idea" aria-labelledby="h-idea">
  <div class="wrap">
    <div class="ch-h">{no(1, "The idea")}<div><h2 id="h-idea">The listening post</h2></div></div>
    <p class="big">Miners carried a canary underground because it noticed first. While it sang, the air was good. <em>When it went quiet, everyone left.</em> Canary Palestine listens to water, air, power and health the same way: station by station, report by report, and it treats a silence as news.</p>
    <ol class="princ">
      <li><span class="g">01</span><h3>Listen, then say it plainly</h3><p>Every station is one place and one thing: a village water line, a clinic network, a solar plant. Its status is the desk's reading of a named report, never a feeling about the day.</p></li>
      <li><span class="g">02</span><h3>Name the source, every time</h3><p>Each reading carries who said it, through whom, and when. A reading without a source is not shown.</p></li>
      <li><span class="g">03</span><h3>Count the silence</h3><p>When a station has had no public report, the desk does not fill the gap. It shows the gap, counts the days, and asks why.</p></li>
    </ol>
  </div>
</section>

<section class="ch coal" id="mark" aria-labelledby="h-mark">
  <div class="wrap">
    <div class="ch-h">{no(2, "The mark")}<div><h2 id="h-mark">The c is the canary</h2>
      <p class="say">The first letter of the name is drawn as the bird's head: round, with an eye on the crown and the beak open, tipped up the way a canary throws its head back to sing. In the wordmark the head sings its own name: the open beak faces «anary».</p></div></div>
    <div class="grid2">
      <div class="cons">{construction()}</div>
      <div>
        <dl class="specs">
          <div><dt class="lab">Size</dt><dd>1,088 u<small>The round lowercase of Geologica at 780, overshoot to overshoot.</small></dd></div>
          <div><dt class="lab">Stroke</dt><dd>{brand.STEM} u<small>The c's own weight in the wordmark's instance, so the head never looks pasted on.</small></dd></div>
          <div><dt class="lab">Beak</dt><dd>{brand.BEAK[0]}° to {brand.BEAK[1]}°<small>Open {brand.BEAK[1] - brand.BEAK[0]}°, tipped up: singing, not shouting. Shut, it closes to {brand.SHUT[1] - brand.SHUT[0]}°.</small></dd></div>
          <div><dt class="lab">Eye</dt><dd>{brand.EYE_AT}° · ⌀ {round(brand.EYE_R * 2)} u<small>Punched through the crown on the stroke's centre line: the one detail that turns a letter into a bird.</small></dd></div>
        </dl>
        <div class="av" style="margin-top:28px"><img src="assets/brand/avatar.svg?v={V}" alt="Avatar: the head in coal on canary" width="120" height="120"><img src="assets/brand/avatar-coal.svg?v={V}" alt="Avatar: the head in canary on coal" width="120" height="120"><img class="sq sm" src="favicon.svg?v={V}" alt="Favicon" width="48" height="48"></div>
        <p class="note-s">Avatar and favicon use the head alone, singing. It holds at 16 pixels because the eye is cut from the stroke, not drawn on it.</p>
      </div>
    </div>
  </div>
</section>

<section class="ch yellow" id="calls" aria-labelledby="h-calls">
  <div class="wrap">
    <div class="ch-h">{no(3, "The calls")}<div><h2 id="h-calls">Four calls, four statuses</h2>
      <p class="say">After the head comes its call, drawn the way a sonograph draws sound: time across, pitch up. The calls are the desk's status system. They hold their meaning without colour, so the site reads the same in print, in greyscale and to a reader who cannot tell yellow from white.</p></div></div>
    <div class="callcards">{calls}</div>
    <p class="note-s">The sounds are synthesised in the page, a few hundred milliseconds each, and play only when a reader presses a button.</p>
  </div>
</section>

<section class="ch paper" id="wordmark" aria-labelledby="h-wm">
  <div class="wrap">
    <div class="ch-h">{no(4, "Wordmark")}<div><h2 id="h-wm">canary, and where it listens</h2>
      <p class="say">The wordmark is lowercase Geologica at 780 with its cursive forms switched on, so every a is single-storey and rounds off like the head. PALESTINE is set in Martian Mono, the instrument face, under «anar» and stopping short of the y: a station tag on a gauge.</p></div></div>
    <div class="grid3 lockrow">
      <figure><div class="lock on-paper">{wordmark()}</div><figcaption class="note-s">On paper: trace, one ink.</figcaption></figure>
      <figure><div class="lock on-coal">{wordmark()}</div><figcaption class="note-s">On coal: the head in canary. The only two-colour version.</figcaption></figure>
      <figure><div class="lock on-canary">{wordmark()}</div><figcaption class="note-s">On canary: coal, one ink.</figcaption></figure>
    </div>
    <div class="grid2" style="margin-top:44px">
      <div><h3 class="lab">Sizes</h3>
        <div class="sizes"><figure><svg style="width:240px" viewBox="0 0 {MARKS["wordmark"]["w"]} {MARKS["wordmark"]["h"]}" aria-hidden="true"><path class="h" d="{MARKS["wordmark"]["head"]}" fill-rule="evenodd"/><path class="l" d="{MARKS["wordmark"]["letters"]}"/><path class="p" d="{MARKS["wordmark"]["pal"]}"/></svg><figcaption class="note-s">Masthead</figcaption></figure>
        <figure><svg style="width:120px" viewBox="0 0 {MARKS["wordmark"]["w"]} {MARKS["wordmark"]["h"]}" aria-hidden="true"><path class="h" d="{MARKS["wordmark"]["head"]}" fill-rule="evenodd"/><path class="l" d="{MARKS["wordmark"]["letters"]}"/><path class="p" d="{MARKS["wordmark"]["pal"]}"/></svg><figcaption class="note-s">Smallest, 120 px</figcaption></figure></div>
        <p class="note-s">Below 120 pixels wide PALESTINE stops being legible: use the head alone. Clear space on every side is the head's eye, three times over.</p></div>
      <div><h3 class="lab">Never</h3><ul class="donts">
        <li>Redraw the head as a closed c or a full disc. The open beak and the eye are the mark.</li>
        <li>Rotate the head so the beak points down or back. It sings forward, into the name.</li>
        <li>Put the call after the wordmark as decoration. A call is a status; it is shown only where it means one.</li>
        <li>Use canary for text on paper. On paper canary is a fill, under coal; text accents use canary ink #5E5300.</li>
      </ul></div>
    </div>
  </div>
</section>

<section class="ch paper" id="colour" aria-labelledby="h-col" style="padding-top:0">
  <div class="wrap">
    <div class="ch-h">{no(5, "Colour")}<div><h2 id="h-col">Coal, canary, paper</h2>
      <p class="say">The palette is the mine and the instrument. Coal is where the network is heard; sonograph paper is where reports are read. Canary is the bird, and like the bird it is only noticed when it matters: an alert, the lead, the silence. There is no second accent colour; status is carried by the shape of the call, not by red and green.</p></div></div>
    <div class="grid4">{colours}</div>
    <div class="tones">{tones}</div>
    <ul class="pairs" aria-label="Contrast of the text pairings">{pairs}</ul>
  </div>
</section>

<section class="ch coal" id="type" aria-labelledby="h-type">
  <div class="wrap">
    <div class="ch-h">{no(6, "Type")}<div><h2 id="h-type">A voice that sharpens</h2>
      <p class="say">Geologica sets the voice: headlines, reading, navigation. It has a sharpness axis, from soft rounded joins to cut corners, and the site uses it as a status channel: a steady report is set soft, a watch halfway, an alert sharp. Martian Mono sets the instruments: codes, readings, dates. Its width axis lets a reading condense to the width of its gauge.</p></div></div>
    <div class="axis">
      <div class="row">
        <p class="demo hl" id="axis-demo" data-s="alert">Three in four Gaza water samples lacked chlorine</p>
        <div><div class="seg" role="group" aria-label="Set the sample by status">
          <button type="button" data-set="steady" aria-pressed="false">{call("steady")}Steady</button>
          <button type="button" data-set="watch" aria-pressed="false">{call("watch")}Watch</button>
          <button type="button" data-set="alert" aria-pressed="true">{call("alert")}Alert</button></div>
          <p class="val-l g" aria-live="polite">SHRP 100 · sharp</p></div>
      </div>
    </div>
    <div class="grid2" style="margin-top:44px">
      <div><p class="spec-big" style="font-variation-settings:'SHRP' 100">Aa</p><p class="lab" style="margin-top:12px;color:var(--ash)">Geologica · Monokrom · OFL · weights 300–850 · SHRP 0–100 · cursive forms on</p></div>
      <div><p class="spec-big" style="font-family:var(--gauge);font-stretch:75%;font-weight:720">W1 73%</p><p class="lab" style="margin-top:12px;color:var(--ash)">Martian Mono · Evil Martians · OFL · weights 300–800 · width 75–112.5</p></div>
    </div>
  </div>
</section>

<section class="ch paper" id="type-scale" aria-label="Type scale" style="padding-top:56px">
  <div class="wrap">
    <ul class="scale">
      <li><span class="g">LEAD · 41/1.06 · 720</span><span class="hl" data-s="alert" style="font-size:41px;line-height:1.06;font-weight:720;letter-spacing:-.022em">In August, three in four Gaza water samples lacked chlorine</span></li>
      <li><span class="g">SECTION · 38/1.1 · 700</span><span style="font-size:38px;font-weight:700;letter-spacing:-.02em">Latest readings</span></li>
      <li><span class="g">CARD · 21/1.18 · 660</span><span style="font-size:21px;font-weight:660">A new link for Bethlehem and Hebron</span></li>
      <li><span class="g">READING · 18/1.62 · 380</span><span style="font-size:18px;line-height:1.62">Chlorine left in the water after treatment is what stops bacteria growing back between a pump, a tanker and a family's container.</span></li>
      <li><span class="g">LABEL · MONO 12 · 560</span><span class="lab">Health partners via OCHA · 28 Sep</span></li>
    </ul>
    <div class="gauges">
      <div><b style="font-stretch:75%">{esc(lead["reading"])}</b><span>Reading · width 75</span></div>
      <div><b style="font-stretch:87.5%;font-size:40px">Out</b><span>Word reading · width 87.5</span></div>
      <div><b style="font-stretch:75%">17/244</b><span>Fraction · tabular figures</span></div>
    </div>
  </div>
</section>

<section class="ch coal" id="sonogram" aria-labelledby="h-son">
  <div class="wrap">
    <div class="ch-h">{no(7, "Sonogram")}<div><h2 id="h-son">The month, as the network sounds</h2>
      <p class="say">The homepage opens on the listening post: a sonogram of every report in the last 30 days. Each row is a station, each mark a report drawn as its call. Read across, a row is a station's month; read down, a column is a day on the network. Press play and the month is sung back, left to right, every station in its place in the stereo field.</p></div></div>
    <div class="anat">
      <div class="sono">{build.sonogram()}{build.sonogram(True)}<div class="tip" aria-hidden="true"></div></div>
      <ol>
        <li><span><b>Bands are the lines</b>: water, air &amp; waste, power, health, like frequency bands on a sonogram.</span></li>
        <li><span><b>Rows are stations</b>, coded by line (W1, A2, P3, H4) and named by place and subject.</span></li>
        <li><span><b>Marks are reports</b>, drawn as the call of their status. Alerts alone are canary.</span></li>
        <li><span><b>A dotted bracket is a silence</b>, from the last report to today, with its count in days.</span></li>
        <li><span><b>The lead is boxed</b>, so the story at left can be found in the month at right.</span></li>
        <li><span><b>The grain is the paper</b>, a faint static under everything, as on a real print.</span></li>
      </ol>
    </div>
    <div class="replay"><button class="btn play" type="button" data-hear="here" aria-pressed="false" data-on="Stop" data-off="Hear the month"><svg class="ico" aria-hidden="true"><use href="#i-ear"/></svg><span class="eq" aria-hidden="true"><i></i><i></i><i></i></span><span class="lbl">Hear the month</span></button></div>
  </div>
</section>

<section class="ch paper" id="photos" aria-labelledby="h-ph">
  <div class="wrap">
    <div class="ch-h">{no(8, "Photographs")}<div><h2 id="h-ph">As they were taken</h2>
      <p class="say">Most stories carry a photograph, shown in its own colour with no filter or tint, cropped only to fit its frame. The identity stays in the type, the calls and the colour around the picture, never on top of it. Where a station has no honest photograph, its card shows the station's call instead.</p></div></div>
    <div class="grid2">
      {ba}
      <ul class="rules">
        <li><b>Only what it shows.</b> A photo sits next to a story only if it shows that place or that kind of thing. The caption gives its real date and place, even when that is years before the report, and says so when it is a nearby stand-in.</li>
        <li><b>Infrastructure, not suffering.</b> Pumps, pipes, panels, clinics, landscapes. No injured people, no children in distress.</li>
        <li><b>Free and credited.</b> Wikimedia Commons, with author and licence under every picture.</li>
        <li><b>No photograph, no pretending.</b> A station without one shows its call on a plate and says "No photograph".</li>
      </ul>
    </div>
  </div>
</section>

<section class="ch coal" id="motion" aria-labelledby="h-mo">
  <div class="wrap">
    <div class="ch-h">{no(9, "Motion & sound")}<div><h2 id="h-mo">It moves like it listens</h2>
      <p class="say">Motion is the stylus and the bird, nothing else: lines draw left to right the way a sonograph writes, the head opens its beak before it sings. Everything settles fast and nothing loops while a reader is reading. With reduced motion requested, the page arrives still and complete.</p></div></div>
    <ul class="mtable">
      <li><b>The first call</b><span class="g">≈2.2 s · once</span><span>Loader, first visit per session only: the stylus line draws, the head pops in with its beak shut, throws its head back and sings its trill. Then the call fades, and the head flies into the masthead, landing exactly on the wordmark's own head while the coal clears around it. Skipped in background tabs, with reduced motion, and never held longer than 4.5 s.</span></li>
      <li><b>Arrival</b><span class="g">0.6 s · stagger 70 ms</span><span>Headers rise in line by line. On a sonogram a canary playhead sweeps once, left to right, writing each mark as it passes; a station's month is written the same way, and its call is drawn after the head.</span></li>
      <li><b>Page to page</b><span class="g">0.26 s</span><span>The wordmark stays where it is and the page crossfades beneath it, so moving between reports feels like turning a dial, not loading a site.</span></li>
      <li><b>The masthead's call</b><span class="g">every 7 s</span><span>The small call after the wordmark chirps now and then: today's most urgent status, quietly alive.</span></li>
      <li><b>Hear the month</b><span class="g">10 s · opt-in</span><span>A playhead sweeps the sonogram; each mark lights and sings as it is passed. Esc or the button stops it; leaving the tab stops it.</span></li>
      <li><b>Tooltips</b><span class="g">160 ms</span><span>A reading card follows a mark under the pointer or keyboard focus; it never covers the mark.</span></li>
      <li><b>Station flash</b><span class="g">1.4 s · once</span><span>Following a mark to its station highlights the card once, in pale canary.</span></li>
      <li><b>Easing</b><span class="g">(.22, .8, .22, 1)</span><span>A fast start and a long settle, for everything that enters. Exits accelerate out.</span></li>
    </ul>
    <div class="replay"><a class="btn" href="home.html?loader">Replay the first call<svg aria-hidden="true"><use href="#i-right"/></svg></a></div>
  </div>
</section>

<section class="ch paper" id="apps" aria-labelledby="h-apps">
  <div class="wrap">
    <div class="ch-h">{no(10, "Applications")}<div><h2 id="h-apps">Out in the world</h2>
      <p class="say">The same few pieces carry everywhere: the head, the call, a reading in Martian Mono, a sentence that names its source. An alert looks like an alert at any size, because its call does not depend on colour.</p></div></div>
    <div class="apps">
      <figure style="grid-column:span 7"><div class="og og-ph"><span class="og-img" style="background-image:url(assets/img/photo/{E["lead"]["photo"]}.webp?v={V})"></span><svg class="wm" viewBox="0 0 {MARKS["wordmark"]["w"]} {MARKS["wordmark"]["h"]}" aria-hidden="true"><path class="h" d="{MARKS["wordmark"]["head"]}" fill-rule="evenodd"/><path class="l" d="{MARKS["wordmark"]["letters"]}"/><path class="p" d="{MARKS["wordmark"]["pal"]}"/></svg>
        <h3>{esc(E["lead"]["headline"])}</h3><p class="r">{call(E["lead"]["status"])}{esc(lead["reading"])}<small>{esc(E["lead"]["reading_note"])}</small></p></div>
        <figcaption class="note-s">Link card, 1200 × 630: the lead's headline set sharp, its reading in canary, its photograph.</figcaption></figure>
      <figure style="grid-column:span 5"><div class="post-card"><p class="top-r"><span>{(sil or lead)["code"]} · SILENT</span><img src="assets/brand/mark-silent.svg?v={V}" alt="" width="150" height="64"></p>
        <p class="d">{(D(E["date"]) - D(sil["silent_since"])).days if sil else 0}<small>days</small></p>
        <p>No public report on {esc((sil or lead)["subject"].lower())} in {esc((sil or lead)["place"])}.</p><p class="f">canary palestine · silence is the signal</p></div>
        <figcaption class="note-s">Social post, 4:5: a silence, counted.</figcaption></figure>
      <figure style="grid-column:span 5"><div class="tg"><div class="who"><img src="assets/brand/avatar.svg?v={V}" alt="" width="34" height="34">Canary Palestine</div>
        <div class="bub"><p class="alert-l">||  ALERT · {lead["code"]} · {esc(lead["place"].upper())}</p><p style="margin-top:6px">{esc(E["lead"]["headline"])}.</p><p style="margin-top:6px;color:#9FB0BF">{esc(lead["source"])} · {day(lead["date"])}</p><p class="t">07:02</p></div></div>
        <figcaption class="note-s">Station alert on Telegram: status, code and place first, then the sentence and its source.</figcaption></figure>
      <figure style="grid-column:span 7"><div class="av"><img src="assets/brand/avatar.svg?v={V}" alt="Profile picture on canary" width="120" height="120"><img src="assets/brand/avatar-coal.svg?v={V}" alt="Profile picture on coal" width="120" height="120"><img class="sq" src="favicon.svg?v={V}" alt="App icon" width="120" height="120"><img class="sq sm" src="favicon.svg?v={V}" alt="" width="48" height="48"></div>
        <figcaption class="note-s">Profile pictures and app icon: the head alone, singing. Canary for social, coal for the app.</figcaption></figure>
    </div>
    <div class="dl"><a class="btn" href="assets/brand/canary-palestine-identity.zip" download>Download the marks and fonts · {kit} KB<svg aria-hidden="true"><use href="#i-down"/></svg></a></div>
  </div>
</section>

<section class="ch yellow" id="voice" aria-labelledby="h-voice">
  <div class="wrap">
    <div class="ch-h">{no(11, "Voice")}<div><h2 id="h-voice">Say what was reported</h2>
      <p class="say">The desk writes like a careful instrument: what was measured, where, by whom, when. Statuses are the desk's reading of named reports, not official alerts, and the copy never pretends otherwise.</p></div></div>
    <ul class="voice">
      <li><p class="yes"><span>In August, three in four Gaza water samples lacked the chlorine that keeps water safe.</span></p><p class="no2"><span>Gaza's water is poisoned.</span></p><p class="why note-s">The number and the test, not a conclusion the report does not make.</p></li>
      <li><p class="yes"><span>No public air-quality reading for the Strip since 12 August.</span></p><p class="no2"><span>Air quality in Gaza is unknown but likely terrible.</span></p><p class="why note-s">A silence is reported as a silence, with its date.</p></li>
      <li><p class="yes"><span>Health partners, via OCHA situation report of 25 Sep.</span></p><p class="no2"><span>Sources say.</span></p><p class="why note-s">Who said it, through whom, and when, on every reading.</p></li>
      <li><p class="yes"><span>Back since 16 Sept after a 54-day breakdown.</span></p><p class="no2"><span>Great news for Nablus!</span></p><p class="why note-s">Steady is a status, not a celebration.</p></li>
    </ul>
  </div>
</section>
</main>
<footer class="bk-foot"><div class="wrap g"><p>Canary Palestine · identity v1 · prototype by TakTek</p><p>Geologica and Martian Mono under the SIL Open Font License · photographs from Wikimedia Commons, credited in place</p></div></footer>
<script src="assets/js/marks.js?v={V}"></script>
<script src="assets/js/voice.js?v={V}" defer></script>
<script src="assets/js/cp.js?v={V}" defer></script>
<script src="assets/js/book.js?v={V}" defer></script>
</body>
</html>
'''


if __name__ == '__main__':
    open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(page())
    print('index.html', os.path.getsize(os.path.join(ROOT, 'index.html')) // 1024, 'KB')
