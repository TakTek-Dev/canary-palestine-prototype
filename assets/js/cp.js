/* Canary Palestine — behaviour.
   1 the first call (loader, once per session)   2 the sonogram: tooltips, keyboard, jump to a station
   3 hearing the network (Web Audio, opt-in)     4 station alerts form */
(() => {
  const root = document.documentElement;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const store = { get(k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } },
                  set(k, v) { try { sessionStorage.setItem(k, v); } catch (e) {} } };

  const head = window.canaryHead;          // tools/brand.py writes it into marks.js

  const light = () => requestAnimationFrame(() => requestAnimationFrame(() => root.classList.add('lit')));

  /* ---------- 1 the first call ---------- */
  // The stylus line draws, the head pops in with its beak shut, throws itself back and sings its trill.
  // Then the call and the stylus fade, and the head flies into the masthead, landing exactly on the
  // wordmark's own head while the coal behind it clears and the page rises in underneath.
  const ease = (t) => 1 - Math.pow(1 - Math.min(1, Math.max(0, t)), 3);
  const inOut = (t) => { t = Math.min(1, Math.max(0, t)); return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
  const back = (t) => { t = Math.min(1, Math.max(0, t)); const c = 1.9; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); };

  function firstCall() {
    const el = $('.first');
    const force = /[?&]loader\b/.test(location.search);
    if (!el) return arrive();
    if (!force && (reduce || store.get('cp-heard') || document.visibilityState === 'hidden')) { el.remove(); return arrive(); }
    store.set('cp-heard', '1');
    root.classList.add('hearing');
    const svg = $('svg', el), hp = $('.first .hd'), notes = $$('.first .note'), sty = $('.first .stylus'), cap = $('.first .cap');
    const s = 0.1, cx = 80, cy = 66, R = 544;
    const [s0, s1] = window.CANARY_SHUT, [b0, b1] = window.CANARY_BEAK;
    const lens = notes.map((n) => n.getTotalLength());
    notes.forEach((n, i) => { n.style.strokeDasharray = lens[i]; n.style.strokeDashoffset = lens[i]; });
    const sl = sty.getTotalLength(); sty.style.strokeDasharray = sl;
    const SING = 1500, FLY = 720;
    let done = false, flight = null, lit = false;

    // where the head is now and where it lands, in screen pixels
    function plan() {
      const target = $('.brand .wm');
      const hc = window.CANARY_MARKS.wordmark.hc;
      if (!target || scrollY > 4) return null;
      const m = svg.getScreenCTM(), n = target.getScreenCTM(), box = svg.getBoundingClientRect();
      if (!m || !n) return null;
      const from = { x: m.a * cx + m.e, y: m.d * cy + m.f, r: m.a * R * s };
      const to = { x: n.a * hc[0] + n.e, y: n.d * hc[1] + n.f, r: n.a * hc[2] };
      if (to.y < 0 || to.y > innerHeight) return null;
      return { from, to, L: box.left, T: box.top };
    }
    const finish = () => {
      if (done) return; done = true;
      if (!lit) { lit = true; arrive(); }
      el.remove(); root.classList.remove('hearing');
    };
    const t0 = performance.now();
    function frame(now) {
      if (done) return;
      const t = now - t0;
      sty.style.strokeDashoffset = sl * (1 - ease(t / 650));
      const k = back((t - 180) / 520);
      const open = ease((t - 700) / 260);
      const lo = s0 + (b0 - s0) * open, hi = s1 + (b1 - s1) * open;
      // the head tips back to sing, and comes level again in flight
      const level = t > SING ? inOut((t - SING) / FLY) : 0;
      hp.setAttribute('d', head(cx, cy, s * Math.max(0.001, k), lo, hi));
      hp.setAttribute('transform', `rotate(${-8 * open * (1 - level)} ${cx} ${cy})`);
      notes.forEach((n, i) => { n.style.strokeDashoffset = lens[i] * (1 - ease((t - 880 - i * 110) / 160)); });
      const out = 1 - ease((t - SING) / 220);
      notes.forEach((n) => { n.style.opacity = out; });
      sty.style.opacity = out;
      cap.style.opacity = Math.min(ease((t - 900) / 300), out);
      if (t > SING) {
        if (flight === null) flight = plan() || false;
        const f = inOut((t - SING) / FLY);
        if (flight) {
          const { from, to, L, T } = flight;
          const z = 1 + (to.r / from.r - 1) * f;
          const x = from.x + (to.x - from.x) * f, y = from.y + (to.y - from.y) * f;
          svg.style.transformOrigin = '0 0';
          svg.style.transform = `translate(${x - L - z * (from.x - L)}px, ${y - T - z * (from.y - T)}px) scale(${z})`;
        } else {
          svg.style.opacity = 1 - f;
        }
        el.style.backgroundColor = `rgba(14,16,13,${1 - ease((t - SING - 120) / 480)})`;
        if (!lit && t > SING + 160) { lit = true; arrive(); }
        if (t > SING + FLY) return finish();
      }
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
    setTimeout(finish, 4500);                                  // guard: never hold the page
  }

  // The page arrives: headers rise line by line, and on a sonogram a canary playhead sweeps once
  // left to right, writing each mark as it passes (the marks' CSS delays follow the same clock).
  function arrive() {
    light();
    if (reduce) return;
    $$('.sono svg[data-k]').forEach((svg) => {
      if (!svg.getBoundingClientRect().width) return;
      const ph = $('.head-play', svg), x0 = +svg.dataset.x0, x1 = +svg.dataset.x1, k = +svg.dataset.k;
      if (!ph) return;
      const start = performance.now() + 350, dur = (x1 - x0) * k;
      svg.classList.add('sweeping');
      const tick = (now) => {
        const p = Math.min(1, Math.max(0, (now - start) / dur));
        const x = x0 + (x1 - x0) * p;
        ph.setAttribute('x1', x); ph.setAttribute('x2', x);
        if (p < 1) return requestAnimationFrame(tick);
        svg.classList.remove('sweeping');
      };
      requestAnimationFrame(tick);
    });
  }

  /* ---------- 2 the sonogram ---------- */
  const sono = $('.sono');
  const tip = $('.tip');
  function place(rep) {
    const box = sono.getBoundingClientRect(), r = rep.getBoundingClientRect();
    const d = rep.dataset;
    tip.innerHTML = `<p class="t1 g"><b>${d.code}</b>${d.date}<svg class="call ${d.s}" aria-hidden="true"><use href="#call-${d.s}"/></svg>${d.label}</p>` +
      `<p class="t2">${d.place}</p><p class="t3">${d.v}</p>`;
    let x = r.left - box.left + r.width / 2 - 145, y = r.top - box.top - tip.offsetHeight - 12;
    x = Math.max(0, Math.min(box.width - 290, x));
    if (y < 0) y = r.bottom - box.top + 12;
    tip.style.left = x + 'px'; tip.style.top = y + 'px';
    tip.classList.add('on');
  }
  if (sono && tip) {
    $$('.rep', sono).forEach((rep) => {
      rep.addEventListener('mouseenter', () => place(rep));
      rep.addEventListener('focus', () => place(rep));
      rep.addEventListener('mouseleave', () => tip.classList.remove('on'));
      rep.addEventListener('blur', () => tip.classList.remove('on'));
    });
  }
  // landing on a station card from the sonogram, the newest list or a link: flash it once
  function flash(id) {
    const card = id && document.getElementById(id);
    if (!card || !card.classList.contains('st')) return;
    card.classList.remove('flash'); void card.offsetWidth; card.classList.add('flash');
    setTimeout(() => card.classList.remove('flash'), 1400);
  }
  addEventListener('hashchange', () => flash(location.hash.slice(1)));

  /* ---------- 3 hearing the network ---------- */
  // Each report is played as its call (assets/js/voice.js), left to right through the month; a silent
  // station plays nothing, which is the point. Lines are spread across the stereo field.
  const PAN = { water: -0.6, air: -0.2, power: 0.2, health: 0.6 };
  const SPAN = 10;                                   // seconds for the whole month
  let ctx = null, raf = 0, startAt = 0;
  const buttons = $$('[data-hear]');
  function stop() {
    cancelAnimationFrame(raf);
    if (ctx) { ctx.close(); ctx = null; }
    sono && sono.classList.remove('playing');
    $$('.rep.lit').forEach((r) => r.classList.remove('lit'));
    buttons.forEach((b) => { b.setAttribute('aria-pressed', 'false'); const l = $('.lbl', b); if (l) l.textContent = b.dataset.off; });
  }
  function play() {
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC || !sono) return;
    ctx = new AC();
    const svg = $$('svg', sono).find((s) => s.getBoundingClientRect().width > 0), x0 = +svg.dataset.x0, x1 = +svg.dataset.x1;
    const reps = $$('.rep', svg).map((r) => ({ el: r, x: +r.dataset.x, s: r.dataset.s, line: r.dataset.line }));
    startAt = ctx.currentTime + 0.15;
    reps.forEach((r) => window.CanaryVoice.sing(ctx, startAt + ((r.x - x0) / (x1 - x0)) * SPAN, r.s, PAN[r.line] || 0));
    const ph = $('.head-play', svg);
    sono.classList.add('playing');
    buttons.forEach((b) => { b.setAttribute('aria-pressed', 'true'); const l = $('.lbl', b); if (l) l.textContent = b.dataset.on; });
    const tick = () => {
      if (!ctx) return;
      const k = (ctx.currentTime - startAt) / SPAN, x = x0 + (x1 - x0) * Math.max(0, k);
      ph.setAttribute('x1', x); ph.setAttribute('x2', x);
      reps.forEach((r) => r.el.classList.toggle('lit', r.x <= x + 1));
      if (k >= 1.04) return stop();
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
  }
  buttons.forEach((b) => b.addEventListener('click', () => {
    if (ctx) return stop();
    if (b.dataset.hear === 'jump' && sono) sono.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'center' });
    play();
  }));
  addEventListener('keydown', (e) => { if (e.key === 'Escape' && ctx) stop(); });
  document.addEventListener('visibilitychange', () => { if (document.hidden && ctx) stop(); });

  /* ---------- 4 station alerts ---------- */
  const form = $('.alerts form');
  if (form) form.addEventListener('submit', (e) => {
    e.preventDefault();
    const n = $$('input[type=checkbox]:checked', form).length, note = $('.note[aria-live]', form);
    note.textContent = n ? `Prototype: nothing is sent yet. You chose ${n} station${n > 1 ? 's' : ''}; alerts will go out when the desk's mailing service is connected.`
                         : 'Choose at least one station to follow.';
  });

  /* ---------- 6 the archive: search and filters, kept in the address so a search can be shared ---------- */
  const results = $('[data-results]');
  if (results) {
    const q = $('#q'), rows = $$('.rrow', results), count = $('[data-count]'), said = $('[data-said]'), empty = $('.empty');
    const chips = $$('.find [data-f]');
    const params = new URLSearchParams(location.search);
    q.value = params.get('q') || '';
    chips.forEach((c) => { if ((params.get(c.dataset.f) || '').split(',').includes(c.dataset.v)) c.setAttribute('aria-pressed', 'true'); });
    const picked = (f) => chips.filter((c) => c.dataset.f === f && c.getAttribute('aria-pressed') === 'true').map((c) => c.dataset.v);
    function apply(push) {
      const words = q.value.toLowerCase().split(/\s+/).filter(Boolean), lines = picked('line'), states = picked('s');
      let n = 0;
      rows.forEach((r) => {
        const ok = words.every((w) => r.dataset.text.includes(w)) && (!lines.length || lines.includes(r.dataset.line)) && (!states.length || states.includes(r.dataset.s));
        r.hidden = !ok; if (ok) n++;
      });
      count.textContent = n;
      empty.hidden = n > 0;
      said.textContent = words.length || lines.length || states.length ? `${n} of ${rows.length} match` : '';
      if (push) {
        const p = new URLSearchParams();
        if (q.value.trim()) p.set('q', q.value.trim());
        if (lines.length) p.set('line', lines.join(','));
        if (states.length) p.set('s', states.join(','));
        history.replaceState(null, '', p.toString() ? '?' + p : location.pathname);
      }
    }
    q.addEventListener('input', () => apply(true));
    $('.find').addEventListener('submit', (e) => { e.preventDefault(); apply(true); });
    chips.forEach((c) => c.addEventListener('click', () => { c.setAttribute('aria-pressed', String(c.getAttribute('aria-pressed') !== 'true')); apply(true); }));
    $('[data-clear]').addEventListener('click', () => { q.value = ''; chips.forEach((c) => c.setAttribute('aria-pressed', 'false')); apply(true); q.focus(); });
    apply(false);
  }

  // alerts page: "All" ticks every station in a line, or clears them if they are all ticked
  $$('[data-all]').forEach((b) => b.addEventListener('click', () => {
    const boxes = $$('input[type=checkbox]', b.closest('fieldset')), on = boxes.every((x) => x.checked);
    boxes.forEach((x) => { x.checked = !on; });
  }));

  /* ---------- 5 share: copy the page's link ---------- */
  $$('[data-copy]').forEach((b) => b.addEventListener('click', async () => {
    const box = b.closest('.share'), note = box && $('.note', box);
    try { await navigator.clipboard.writeText(b.dataset.copy); if (note) note.textContent = 'Link copied.'; }
    catch (e) { if (note) note.textContent = b.dataset.copy; }
  }));

  firstCall();
  if (location.hash) setTimeout(() => flash(location.hash.slice(1)), 600);
})();
