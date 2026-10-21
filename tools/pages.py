"""Build the inner pages from tools/edition.json: one page per report, one per station, one per line,
the about page and the 404.

python -I tools/pages.py   (after build.py; same shell, tokens and calls as the homepage)

report/<id>.html   the report: status, reading, photograph, the text, its source, its station's month
station/<code>.html the station: its call, reading, month, every report the desk has on it
<line>.html        a line: its band of the sonogram, its stations, its reports
about.html         what the desk is, how a status is set, sources, corrections, sending a report
404.html           a silent page
"""
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402
from build import (E, MARKS, LABEL, CALL, RANK, TODAY, D, day, esc, call, photo, caption, has, note_path,  # noqa: E402
                   station_card, lane, sonogram, head, top, foot, rlink, slink, stations)

ROOT = build.ROOT
REPORTS = E['reports']
BY_ID = {r['id']: r for r in REPORTS}
STATION = {st['code']: (line, st) for line, st in stations()}
LINE = {l['key']: l for l in E['lines']}
AREA = {'gaza': 'Gaza Strip', 'wb-north': 'Northern West Bank', 'wb-centre-south': 'Centre & south West Bank', 'wb': 'West Bank',
        'area-c': 'Area C', 'jerusalem': 'Jerusalem'}
INTRO = {
    'water': 'Production, quality, networks, wells, springs and wastewater: whether people can get safe water, and what is stopping it.',
    'air': 'Waste dumps, landfills, rubble and the few air sensors there are. Where there are no measurements, the desk says so.',
    'power': 'Electricity, fuel and gas: what keeps pumps, clinics and kitchens running, and the lines that are cut.',
    'health': 'Disease surveillance, medicines, hospitals, mobile clinics and the attacks that stop care reaching people.',
}


def first_sentence(t):
    import re
    m = re.match(r'(.+?[.!?])(\s+[A-Z]|$)', t)
    return m.group(1) if m else t


def sentence(t):
    return t[:1].upper() + t[1:]


def setR(r):
    build.R = r


def big_mark(kind, on='coal'):
    """The head and its call, as the identity draws it, at display size."""
    c = MARKS['call'][kind]
    sw = MARKS['callStroke']
    return (f'<svg class="bigmark {kind}" viewBox="0 0 150 64" aria-hidden="true"><path d="{c["head"]}" fill-rule="evenodd"/>'
            f'<path class="cl" d="{"".join(c["call"])}" pathLength="1" stroke-width="{sw}" fill="none" stroke-linecap="round"/></svg>')


KIND = {'steady': 'song', 'watch': 'strained', 'alert': 'alarm', 'silent': 'silent'}


def month(st, compact=False):
    """A station's month, drawn large: day grid, its calls, a silence bracket, today.
    On phones the last 14 days, so the marks and dates stay readable at 375 px."""
    w, h = (360, 86) if compact else (1000, 86)
    w0 = TODAY - dt.timedelta(days=13) if compact else D(E['window'][0])
    days = (TODAY - w0).days + 1
    dx = (w - 20) / days
    x = lambda d: 10 + (((D(d) if isinstance(d, str) else d) - w0).days + 0.5) * dx
    cy = 44
    out = [f'<path class="hum" d="M10 {cy}H{w - 10}"/>']
    for i in range(days):
        d = w0 + dt.timedelta(days=i)
        xx = 10 + i * dx
        out.append(f'<path class="day{" wk" if d.weekday() == 0 else ""}" d="M{xx:.1f} 14V{h - 14}"/>')
        if d.weekday() == 0 or (compact and i == 0):
            out.append(f'<text class="ax" x="{xx + 3:.1f}" y="{h - 1}">{day(d).upper()}</text>')
    for d, s in st['history']:
        if D(d) < w0:
            continue
        xx = x(d)
        k = 1.5 if compact else 2.1
        out.append(f'<g transform="translate({xx:.1f} {cy}) scale({k}) translate({-xx:.1f} {-cy})"><path class="n {s}" d="{note_path(s, xx, cy)}"/></g>')
    if st['status'] == 'silent':
        xs = max(x(st['silent_since']), 10)
        out.append(f'<path class="quiet" d="M{xs + 14:.1f} {cy - 10}v20M{xs + 14:.1f} {cy}H{x(TODAY):.1f}M{x(TODAY):.1f} {cy - 10}v20"/>')
        n = (TODAY - D(st['silent_since'])).days
        if x(TODAY) - xs > 110:
            out.append(f'<text class="quiet-t" x="{(xs + x(TODAY)) / 2:.1f}" y="{cy - 6}" text-anchor="middle" paint-order="stroke" stroke="#0E100D" stroke-width="6">SILENT {n} DAYS</text>')
    out.append(f'<path class="now-l" d="M{x(TODAY):.1f} 6V{h - 14}"/><text class="now-t" x="{x(TODAY):.1f}" y="10" text-anchor="end">TODAY</text>')
    n = sum(1 for d, _ in st['history'] if D(d) >= w0)
    return (f'<div class="sono month {"month-m" if compact else "month-d"}"><svg viewBox="0 0 {w} {h}" role="img" aria-label="{st["code"]} over {14 if compact else 30} days: {n} report{"s" if n != 1 else ""}'
            f'{", silent since " + day(st["silent_since"]) if st["status"] == "silent" else ""}">{"".join(out)}</svg></div>')


def row(r):
    """A report in a list: photograph (or the call), date, code, status, headline."""
    fig = photo(r['photo'], 'r32') if has(r.get('photo')) else f'<div class="plate sm" data-s="{r["status"]}">{call(r["status"], "big")}</div>'
    code = r['station'] or LINE[r['line']]['code']
    return (f'<li class="rrow" data-s="{r["status"]}"><a href="{rlink(r["id"])}">{fig}<span class="rt">'
            f'<span class="kick lab"><span class="tag">{call(r["status"])}{code}</span>{day(r["published"])}</span>'
            f'<span class="hl">{esc(r["headline"])}</span><span class="src">{esc(r["src"])}</span></span></a></li>')


def share(url, title):
    from urllib.parse import quote
    u, t = quote(url, safe=''), quote(title, safe='')
    return (f'<div class="share"><p class="lab">Share</p><ul>'
            f'<li><button class="btn" type="button" data-copy="{esc(url)}"><svg aria-hidden="true"><use href="#i-link"/></svg><span class="lbl">Copy link</span></button></li>'
            f'<li><a class="btn" href="https://wa.me/?text={t}%20{u}" rel="noopener" target="_blank">WhatsApp</a></li>'
            f'<li><a class="btn" href="https://t.me/share/url?url={u}&amp;text={t}" rel="noopener" target="_blank">Telegram</a></li>'
            f'<li><a class="btn" href="https://x.com/intent/post?url={u}&amp;text={t}" rel="noopener" target="_blank">X</a></li>'
            f'<li><a class="btn" href="https://www.facebook.com/sharer/sharer.php?u={u}" rel="noopener" target="_blank">Facebook</a></li>'
            f'</ul><p class="note g" aria-live="polite"></p></div>')


BASE = 'https://taktek-dev.github.io/canary-palestine-prototype/'


def crumb(*parts):
    li = ''.join(f'<li><a href="{h}">{esc(t)}</a></li>' if h else f'<li aria-current="page">{esc(t)}</li>' for t, h in parts)
    return f'<nav class="crumb g" aria-label="Breadcrumb"><ol>{li}</ol></nav>'


# ---------------------------------------------------------------- report
def report_page(r):
    setR('../')
    line = LINE[r['line']]
    st = STATION.get(r['station'], (None, None))[1]
    s = r['status']
    body = r['body'] or [r['summary']]
    # the dek is the summary's first sentence when the page has a full body, else the reading's note
    dek = first_sentence(r['summary']) if r['body'] else r['reading_note']
    fig = (f'<figure class="rpt-ph">{photo(r["photo"], "r169", eager=True)}{caption(r["photo"])}</figure>' if has(r.get('photo')) else '')
    same = [x for x in REPORTS if x['id'] != r['id'] and st and x['station'] == r['station']][:4]
    near = [x for x in REPORTS if x['id'] != r['id'] and x['line'] == r['line'] and x not in same][:6 - len(same)]
    station_box = ''
    if st:
        station_box = (f'<section class="side-st" aria-labelledby="ss-h"><h2 id="ss-h" class="lab">The station</h2>'
                       f'<a class="st-link" href="{slink(st["code"])}" data-s="{st["status"]}"><span class="code">{st["code"]}</span>'
                       f'<span class="chip lab">{call(st["status"])}{LABEL[st["status"]]}</span><b>{esc(st["place"])}</b><span>{esc(st["subject"])}</span>'
                       f'<span class="v">{esc(st["reading"]) if st["status"] != "silent" else str((TODAY - D(st["silent_since"])).days) + " days"}</span>'
                       f'{lane(st)}<span class="go">Station page<svg aria-hidden="true"><use href="#i-right"/></svg></span></a></section>')
    background = '<p class="bgnote g">Background: this report is older than the desk\'s 30-day window and is kept for context.</p>' if r['background'] else ''
    html = head(f'{r["headline"]} · Canary Palestine', r['summary']) + top(r['line']) + f'''
<main id="main" class="rpt" data-s="{s}">
  <header class="rpt-head">
    <div class="wrap">
      {crumb(("Home", "../home.html"), (line["name"], f"../{line['key']}.html"), ((st["code"] + " · " + st["short"]) if st else AREA[r["area"]], slink(st["code"]) if st else None))}
      <p class="status lab rise" style="--i:0">{call(s)}<span>{LABEL[s]}{" · " + r["station"] if r["station"] else ""}</span><span class="bg">{esc(r["place"])} · {day(r["published"], True)}</span></p>
      <h1 class="hl rise" style="--i:1" data-s="{s}">{esc(r["headline"])}</h1>
      <p class="dek rise" style="--i:2">{esc(dek)}</p>
      <div class="reading rise" style="--i:3"><p class="v">{esc(r["reading"])}</p><p>{esc(r["reading_note"])}</p></div>
    </div>
  </header>
  <div class="wrap rpt-grid">
    <article class="rpt-main" aria-labelledby="rpt-h">
      <h2 id="rpt-h" class="sr">The report</h2>
      {fig}
      {background}
      <div class="body">{"".join(f"<p>{esc(p)}</p>" for p in body)}</div>
      <aside class="srcbox" aria-label="Source">
        <p class="lab">Source</p>
        <p><b>{esc(r["source"])}</b>, via {esc(r["via"])}. Event {day(r["date"], True)}; published {day(r["published"], True)}.</p>
        <p><a href="{esc(r["url"])}" rel="noopener" target="_blank">Read the original report<svg aria-hidden="true"><use href="#i-right"/></svg></a></p>
        <p class="note-s">The status is the desk's reading of this report, not an official alert. Found a mistake? <a href="../about.html#corrections">Tell the desk</a>.</p>
      </aside>
      {share(BASE + "report/" + r["id"] + ".html", r["headline"])}
    </article>
    <aside class="rpt-side">
      {station_box}
      <section aria-labelledby="more-h"><h2 id="more-h" class="lab">{"From the same station" if same else "More on " + line["name"].lower()}</h2>
        <ol class="rlist compact">{"".join(row(x) for x in (same + near))}</ol>
        <a class="more-l" href="../{line["key"]}.html">All of {line["name"].lower()}<svg aria-hidden="true"><use href="#i-right"/></svg></a></section>
    </aside>
  </div>
</main>
''' + foot()
    return html


# ---------------------------------------------------------------- station
def station_page(line, st):
    setR('../')
    s = st['status']
    reps = [BY_ID[i] for i in st['items'] if i in BY_ID]
    reps.sort(key=lambda r: r['published'], reverse=True)
    if s == 'silent':
        n = (TODAY - D(st['silent_since'])).days
        val = f'<p class="v">{n} days</p><p>since the last public report, {day(st["silent_since"], True)}. {esc(sentence(st["what"]))}</p>'
    else:
        val = f'<p class="v">{esc(st["reading"])}</p><p>{esc(st["what"])}</p>'
    fig = f'<figure class="st-big">{photo(st["photo"], "r32", eager=True)}{caption(st["photo"])}</figure>' if has(st.get('photo')) else ''
    sibs = [x for x in line['stations'] if x['code'] != st['code']]
    silent_note = ''
    if s == 'silent':
        silent_note = ('<div class="silent-note"><p class="lab">Why this station is silent</p><p>The desk has found no public report on this since the date above. '
                       'It does not fill the gap with a guess: it counts the days and keeps asking. If you have a report, '
                       '<a href="../about.html#send">send it to the desk</a>.</p></div>')
    html = head(f'{st["code"]} · {st["place"]}, {st["subject"].lower()} · Canary Palestine', f'{st["place"]}: {st["subject"].lower()}. {LABEL[s]}. {st["what"]}') + top(line['key']) + f'''
<main id="main" class="stp" data-s="{s}">
  <header class="stp-head">
    <div class="wrap stp-grid">
      <div>
        {crumb(("Home", "../home.html"), (line["name"], f"../{line['key']}.html"), (st["code"], None))}
        <p class="code-big g rise" style="--i:0">{st["code"]}</p>
        <h1 class="rise" style="--i:1">{esc(st["place"])}<span>{esc(st["subject"])}</span></h1>
        <p class="status lab rise" style="--i:2">{call(s)}<span>{LABEL[s]}</span><span class="bg">{CALL[s]} · {AREA[st["area"]]}</span></p>
      </div>
      <div class="stp-mark rise" style="--i:2">{big_mark(KIND[s])}<div class="reading">{val}</div>
        <p class="src g">{esc(st["source"])} · {day(st["date"])}</p></div>
    </div>
    <div class="wrap"><h2 class="lab month-h">The station's <span class="d-only">month</span><span class="m-only">last 14 days</span></h2>{month(st)}{month(st, True)}</div>
  </header>
  <div class="wrap stp-body">
    {silent_note}
    <div class="stp-cols">
      <section aria-labelledby="rep-h"><h2 id="rep-h" class="sec-t">Every report on {st["code"]}</h2>
        <ol class="rlist">{"".join(row(r) for r in reps)}</ol></section>
      <aside>
        {fig}
        <section class="follow" aria-labelledby="fo-h"><h2 id="fo-h" class="lab">Follow {st["code"]}</h2>
          <p>When this station changes its call, the desk writes to you once, with the report it rests on.</p>
          <a class="btn" href="../home.html#alerts"><svg aria-hidden="true"><use href="#i-bell"/></svg>Station alerts</a></section>
      </aside>
    </div>
    <section class="sibs" aria-labelledby="sib-h"><h2 id="sib-h" class="sec-t">Other {line["name"].lower()} stations</h2>
      <ul class="sib-list">{"".join(f'<li data-s="{x["status"]}"><a href="{slink(x["code"])}"><span class="code">{x["code"]}</span>{call(x["status"])}<b>{esc(x["place"])}</b><span>{esc(x["subject"])}</span></a></li>' for x in sibs)}</ul></section>
  </div>
</main>
''' + foot()
    return html


# ---------------------------------------------------------------- line
def line_page(line):
    setR('')
    sts = line['stations']
    t = {k: sum(1 for x in sts if x['status'] == k) for k in RANK}
    reps = [r for r in REPORTS if r['line'] == line['key']]
    plates = any(has(x.get('photo')) for x in sts)
    cells = ''.join(station_card(line, x, plates) for x in sts)
    wide = ' three' if len(sts) % 3 == 0 and len(sts) > 3 else (' wide' if len(sts) > 4 else '')
    html = head(f'{line["name"]} · Canary Palestine', INTRO[line['key']]) + top(line['key']) + f'''
<main id="main" class="lnp">
  <section class="post lnp-head" aria-labelledby="ln-h">
    <div class="wrap">
      {crumb(("Home", "home.html"), (line["name"], None))}
      <div class="lnp-grid">
        <div>
          <h1 id="ln-h" class="rise" style="--i:0"><svg aria-hidden="true"><use href="#ln-{line["key"]}"/></svg>{esc(line["name"])}</h1>
          <p class="dek rise" style="--i:1">{esc(INTRO[line["key"]])}</p>
          <ul class="lnp-tally g">{"".join(f'<li>{call(k)}<b>{t[k]}</b> {k}</li>' for k in ("alert", "watch", "steady", "silent") if t[k])}</ul>
        </div>
        <div class="net"><div class="sono">{sonogram(only=line["key"])}{sonogram(True, only=line["key"])}<div class="tip" aria-hidden="true"></div></div></div>
      </div>
    </div>
  </section>
  <section class="reg paper" aria-labelledby="lst-h">
    <div class="wrap">
      <div class="sec-h"><h2 id="lst-h">Stations</h2><p>{len(sts)} stations on this line. Follow one to its page for every report the desk has on it.</p></div>
      <div class="rack solo"><div class="cells{wide}" style="--n:{len(sts)}">{cells}</div></div>
    </div>
  </section>
  <section class="inv paper" aria-labelledby="lr-h">
    <div class="wrap">
      <div class="sec-h"><h2 id="lr-h">Reports</h2><p>{len(reps)} sourced reports, newest first.</p></div>
      <ol class="rlist grid">{"".join(row(r) for r in reps)}</ol>
    </div>
  </section>
</main>
''' + foot()
    return html


# ---------------------------------------------------------------- about
def about_page():
    setR('')
    calls = ''.join(
        f'<li data-s="{s}">{big_mark(KIND[s])}<div><h3>{LABEL[s]}</h3><p class="g">{CALL[s].upper()}</p><p>{d}</p></div></li>'
        for s, d in (('alert', 'Harm reported now: a line cut, a well demolished, medicines at zero stock, a team stopped on the road.'),
                     ('watch', 'Damage, loss or a risk reported: a network losing half its water, a plant not running, outbreaks expected.'),
                     ('steady', 'Working, restored or added: a well back on, a dump cleared, a plan launched.'),
                     ('silent', 'No recent public report. The desk counts the days since the last one and keeps asking.')))
    srcs = sorted({r['via'].split(' (')[0].split(';')[0].strip() for r in REPORTS})
    html = head('About the desk · Canary Palestine', E['about']) + top('about') + f'''
<main id="main" class="abt">
  <header class="post abt-head"><div class="wrap">
    {crumb(("Home", "home.html"), ("About", None))}
    <h1 class="rise" style="--i:0">A canary sings while the air is good.<br>When it goes quiet, everyone listens.</h1>
    <p class="dek rise" style="--i:1">{esc(E["about"])}</p>
  </div></header>
  <div class="wrap abt-body">
    <section id="method" aria-labelledby="m-h"><h2 id="m-h" class="sec-t">How a status is set</h2>
      <p class="lede">Every station is one place and one thing: a village water line, a set of clinics, a power line. When a named organisation publishes a report on it, the desk reads the report and gives the station one of four statuses, drawn as the canary's call. The status is the desk's reading, not an official alert, and it always links to the report it rests on.</p>
      <ul class="callrows">{calls}</ul></section>
    <section id="sources" aria-labelledby="s-h"><h2 id="s-h" class="sec-t">Who the desk listens to</h2>
      <p class="lede">Public reports only: UN agencies, Palestinian authorities, local councils and named officials quoted by news agencies. A reading without a named source is not shown.</p>
      <ul class="srcs g">{"".join(f"<li>{esc(x)}</li>" for x in srcs)}</ul></section>
    <section id="corrections" aria-labelledby="c-h"><h2 id="c-h" class="sec-t">Corrections</h2>
      <p class="lede">When the desk gets something wrong, the station's page and the report say so, with the date of the correction and what changed. Nothing is quietly rewritten.</p>
      <p class="ph-note">Corrections address: to be set when the desk's domain is live.</p></section>
    <section id="send" aria-labelledby="se-h"><h2 id="se-h" class="sec-t">Send a report</h2>
      <p class="lede">Councils, water and power utilities, clinics and residents can send the desk a report: what happened, where, when, and who can confirm it. The desk checks it against a second source before a station changes its call.</p>
      <p class="ph-note">Submission form and contact details: to be added with the content management panel.</p></section>
  </div>
</main>
''' + foot()
    return html


def page_404():
    setR('')
    html = head('Silent page · Canary Palestine', 'This page does not exist.') + top() + f'''
<main id="main" class="nf">
  <div class="wrap">
    <svg class="shut" viewBox="0 0 64 64" aria-hidden="true"><path d="{MARKS["call"]["silent"]["head"]}" fill-rule="evenodd"/></svg>
    <p class="g code-big">404</p>
    <h1>This page is silent.</h1>
    <p class="dek">There is nothing at this address. The network is still listening on the homepage.</p>
    <p class="acts"><a class="btn hot" href="home.html">Back to the listening post<svg aria-hidden="true"><use href="#i-right"/></svg></a>
      <a class="btn" href="about.html">About the desk</a></p>
  </div>
</main>
''' + foot()
    # GitHub Pages serves 404.html at any depth: make every relative link absolute to the site root
    import re
    return re.sub(r'(href|src)="(?!https?:|#|data:|mailto:)', lambda m: f'{m.group(1)}="{BASE}', html)


# ---------------------------------------------------------------- the archive: every report, searchable
def reports_page():
    setR('')
    lines = ''.join(f'<li><button type="button" data-f="line" data-v="{l["key"]}" aria-pressed="false">'
                    f'<svg aria-hidden="true"><use href="#ln-{l["key"]}"/></svg>{esc(l["name"])}</button></li>' for l in E['lines'])
    states = ''.join(f'<li><button type="button" data-f="s" data-v="{k}" aria-pressed="false">{call(k)}{LABEL[k]}</button></li>'
                     for k in ('alert', 'watch', 'steady'))
    items = []
    for r in REPORTS:
        text = ' '.join([r['headline'], r['summary'], r['place'], r['subject'], r['source'], r['station'] or '']).lower()
        items.append(row(r).replace('<li class="rrow"', f'<li class="rrow" data-line="{r["line"]}" data-text="{esc(text)}"', 1))
    html = head('Reporting · Canary Palestine', 'Every report the desk has used, with its source: search by place, subject or source, or filter by line and status.') + top('reports') + f'''
<main id="main" class="arc">
  <header class="post arc-head"><div class="wrap">
    {crumb(("Home", "home.html"), ("Reporting", None))}
    <h1 class="rise" style="--i:0">Reporting</h1>
    <p class="dek rise" style="--i:1">Every report the desk has used, newest first, each with the source it rests on.</p>
    <form class="find rise" style="--i:2" role="search" action="reports.html">
      <label for="q" class="sr">Search the reports</label>
      <div class="q-row"><svg aria-hidden="true"><use href="#i-search"/></svg><input id="q" name="q" type="search" placeholder="A place, a subject or a source: Tubas, chlorine, WHO" autocomplete="off"></div>
      <div class="chips"><ul aria-label="Line">{lines}</ul><ul aria-label="Status">{states}</ul></div>
    </form>
  </div></header>
  <section class="paper arc-list" aria-labelledby="res-h"><div class="wrap">
    <div class="sec-h"><h2 id="res-h"><span data-count>{len(REPORTS)}</span> reports</h2><p aria-live="polite" class="g" data-said></p></div>
    <ol class="rlist grid" data-results>{"".join(items)}</ol>
    <div class="empty" hidden><svg class="shut" viewBox="0 0 64 64" aria-hidden="true"><path d="{MARKS["call"]["silent"]["head"]}" fill-rule="evenodd"/></svg>
      <p>Nothing on the network matches that. Try a place name or a source, or <button type="button" data-clear>clear the filters</button>.</p></div>
  </div></section>
</main>
''' + foot()
    return html


# ---------------------------------------------------------------- the silence
def silence_page():
    setR('')
    silent = [(line, st) for line, st in stations() if st['status'] == 'silent']
    blocks = []
    for line, st in silent:
        last = BY_ID.get(st['item'])
        n = (TODAY - D(st['silent_since'])).days
        blocks.append(f'''<article class="qs" aria-labelledby="q-{st["code"].lower()}">
      <div class="qs-top"><p class="code g">{st["code"]} · {esc(line["name"]).upper()}</p><p class="days">{n}<small>days</small></p></div>
      <h2 id="q-{st["code"].lower()}"><a href="{slink(st["code"])}">{esc(st["place"])}<span>{esc(st["subject"])}</span></a></h2>
      <p>{esc(sentence(st["what"]))}</p>
      {month(st)}{month(st, True)}
      <p class="last g">Last report {day(st["silent_since"], True)} · {esc(st["source"])}{f' · <a href="{rlink(last["id"])}">read it</a>' if last else ''}</p>
    </article>''')
    html = head('Silence · Canary Palestine', 'The stations with no recent public report, and how long they have been quiet.') + top('silence') + f'''
<main id="main" class="sil">
  <header class="silence sil-head"><div class="wrap">
    <nav class="crumb g" aria-label="Breadcrumb"><ol><li><a href="home.html">Home</a></li><li aria-current="page">Silence</li></ol></nav>
    <svg class="shut rise" style="--i:0" viewBox="0 0 64 64" aria-hidden="true"><path d="{MARKS["call"]["silent"]["head"]}" fill-rule="evenodd"/></svg>
    <h1 class="rise" style="--i:1">{esc(E["silence"]["title"])}</h1>
    <p class="say rise" style="--i:2">{esc(E["silence"]["say"])}</p>
    <p class="count g rise" style="--i:3">{len(silent)} stations silent today</p>
  </div></header>
  <div class="wrap sil-body">
    <div class="qs-list">{"".join(blocks)}</div>
    <section class="sil-how" aria-labelledby="how-h"><h2 id="how-h" class="sec-t">How a silence is counted</h2>
      <p class="lede">A station goes silent when the reports the desk relies on stop mentioning it: no new figures, no statement, no follow-up. The count starts on the day of the last public report and runs until a new one appears. A silence is not a finding about what is happening on the ground; it is a finding about what nobody is saying.</p>
      <p class="lede">If you have a report on a silent station, <a href="about.html#send">send it to the desk</a>.</p></section>
  </div>
</main>
''' + foot()
    return html


# ---------------------------------------------------------------- station alerts
def alerts_page():
    setR('')
    groups = []
    for line in E['lines']:
        picks = ''.join(f'<li class="pick"><input type="checkbox" id="al-{st["code"].lower()}" name="st" value="{st["code"]}">'
                        f'<span><span class="code">{st["code"]}</span>{esc(st["short"])}{" · silent" if st["status"] == "silent" else ""}</span></li>'
                        for st in line['stations'])
        groups.append(f'<fieldset><legend class="lab"><svg aria-hidden="true"><use href="#ln-{line["key"]}"/></svg>{esc(line["name"])}'
                      f'<button type="button" class="all" data-all>All</button></legend><ul class="picks">{picks}</ul></fieldset>')
    html = head('Station alerts · Canary Palestine', 'Follow the stations you care about: the desk writes when one of them changes its call.') + top('alerts') + f'''
<main id="main" class="alp">
  <section class="alerts alp-body" aria-labelledby="al-h"><div class="wrap">
    {crumb(("Home", "home.html"), ("Station alerts", None))}
    <div class="alerts-grid">
      <div><h1 id="al-h" class="rise" style="--i:0">Station alerts</h1>
        <p class="say rise" style="--i:1">Choose the stations to follow. When one of them changes its call, the desk writes to you once, with the report it rests on. Nothing else, no newsletter.</p>
        <ul class="how g rise" style="--i:2"><li>{call("alert")}An alert goes out the same day</li><li>{call("watch")}A watch, in the evening digest</li><li>{call("silent")}A silence, when it passes three weeks</li></ul></div>
      <form action="#" novalidate>
        {"".join(groups)}
        <fieldset><legend class="lab">How often</legend><div class="radios">
          <label><input type="radio" name="freq" value="each" checked> Every change</label>
          <label><input type="radio" name="freq" value="daily"> One digest a day</label></div></fieldset>
        <div class="sub"><label><span class="sr">Email address</span><input type="email" name="email" autocomplete="email" placeholder="you@example.org" required></label>
          <button class="btn" type="submit">Follow<svg aria-hidden="true"><use href="#i-right"/></svg></button></div>
        <p class="note" aria-live="polite"></p>
        <p class="fine">Your email and stations are used only to send these alerts. <a href="privacy.html">Privacy</a>.</p>
      </form>
    </div>
  </div></section>
</main>
''' + foot()
    return html


# ---------------------------------------------------------------- privacy and photo credits
def privacy_page():
    setR('')
    html = head('Privacy · Canary Palestine', 'What the site collects, and what it does not.') + top() + f'''
<main id="main" class="abt">
  <header class="post abt-head"><div class="wrap">
    {crumb(("Home", "home.html"), ("Privacy", None))}
    <h1 class="rise" style="--i:0">Privacy</h1>
    <p class="dek rise" style="--i:1">The desk listens to public reports, not to its readers.</p>
  </div></header>
  <div class="wrap abt-body">
    <section aria-labelledby="p1"><h2 id="p1" class="sec-t">What is collected</h2>
      <p class="lede">Only what you type into the station alerts form: an email address and the stations you chose. It is used to send those alerts and nothing else, and it is deleted when you unsubscribe.</p></section>
    <section aria-labelledby="p2"><h2 id="p2" class="sec-t">What is not</h2>
      <p class="lede">No advertising, no tracking cookies, no third-party analytics. The fonts and photographs are served from this site. Remembering that you have already seen the opening animation uses your browser's session storage and never leaves your device.</p></section>
    <section aria-labelledby="p3"><h2 id="p3" class="sec-t">Sharing</h2>
      <p class="lede">The share buttons on a report open WhatsApp, Telegram, X or Facebook only when you press them; nothing is loaded from those services before that.</p>
      <p class="ph-note">Data controller, contact and legal address: to be added before launch.</p></section>
  </div>
</main>
''' + foot()
    return html


def credits_page():
    setR('')
    used = sorted({slug for slug in build.PH if has(slug)})
    rows = ''.join(f'''<li><figure>{photo(slug, "r32")}</figure><div><p><b>{esc(build.PH[slug]["place"])}</b> · {esc(build.PH[slug]["year"])}</p>
      <p>{esc(build.PH[slug]["caption"])}</p>
      <p class="g">{esc(build.PH[slug]["author"])} · <a href="{esc(build.PH[slug]["license_url"] or build.PH[slug]["page_url"])}" rel="noopener">{esc(build.PH[slug]["license"])}</a> · <a href="{esc(build.PH[slug]["page_url"])}" rel="noopener">Wikimedia Commons</a></p></div></li>''' for slug in used)
    html = head('Photo credits · Canary Palestine', 'Every photograph on the site, its author and its licence.') + top() + f'''
<main id="main" class="abt">
  <header class="post abt-head"><div class="wrap">
    {crumb(("Home", "home.html"), ("Photo credits", None))}
    <h1 class="rise" style="--i:0">Photo credits</h1>
    <p class="dek rise" style="--i:1">All {len(used)} photographs come from Wikimedia Commons under free licences. Each is shown as taken, resized only, and captioned with its real date and place.</p>
  </div></header>
  <div class="wrap"><ul class="credits">{rows}</ul></div>
</main>
''' + foot()
    return html


def write(rel, html):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(html)


if __name__ == '__main__':
    for r in REPORTS:
        write(f'report/{r["id"]}.html', report_page(r))
    for line, st in stations():
        write(f'station/{st["code"].lower()}.html', station_page(line, st))
    for l in E['lines']:
        write(f'{l["key"]}.html', line_page(l))
    write('about.html', about_page())
    write('reports.html', reports_page())
    write('silence.html', silence_page())
    write('alerts.html', alerts_page())
    write('privacy.html', privacy_page())
    write('credits.html', credits_page())
    write('404.html', page_404())
    setR('')
    print('reports', len(REPORTS), 'stations', sum(1 for _ in stations()), 'lines', len(E['lines']),
          '+ about, reports, silence, alerts, privacy, credits, 404')
