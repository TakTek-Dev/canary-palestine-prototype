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
  function firstCall() {
    const el = $('.first');
    const force = /[?&]loader\b/.test(location.search);
    if (!el) return light();
    if (!force && (reduce || store.get('cp-heard') || document.visibilityState === 'hidden')) { el.remove(); return light(); }
    store.set('cp-heard', '1');
    root.classList.add('hearing');
    const hp = $('.first .hd'), notes = $$('.first .note'), sty = $('.first .stylus'), cap = $('.first .cap');
    const s = 0.1, cx = 80, cy = 66;
    let done = false;
    const finish = () => {
      if (done) return; done = true;
      el.classList.add('go');
      light();
      setTimeout(() => { el.remove(); root.classList.remove('hearing'); }, 800);
    };
    const t0 = performance.now();
    const ease = (t) => 1 - Math.pow(1 - Math.min(1, Math.max(0, t)), 3);
    const back = (t) => { t = Math.min(1, Math.max(0, t)); const c = 1.9; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); };
    const lens = notes.map((n) => n.getTotalLength());
    notes.forEach((n, i) => { n.style.strokeDasharray = lens[i]; n.style.strokeDashoffset = lens[i]; });
    const sl = sty.getTotalLength(); sty.style.strokeDasharray = sl;
    function frame(now) {
      if (done) return;
      const t = now - t0;
      sty.style.strokeDashoffset = sl * (1 - ease(t / 650));
      const k = back((t - 180) / 520);                       // head pops in, beak shut
      const open = ease((t - 700) / 260);                    // then throws its head back and opens
      const [s0, s1] = window.CANARY_SHUT, [b0, b1] = window.CANARY_BEAK;
      const lo = s0 + (b0 - s0) * open, hi = s1 + (b1 - s1) * open;
      hp.setAttribute('d', head(cx, cy, s * Math.max(0.001, k), lo, hi));
      hp.setAttribute('transform', `rotate(${-8 * open} ${cx} ${cy})`);
      notes.forEach((n, i) => { n.style.strokeDashoffset = lens[i] * (1 - ease((t - 880 - i * 110) / 160)); });
      cap.style.opacity = ease((t - 900) / 300);
      if (t > 1900) return finish();
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
    setTimeout(finish, 4500);                                  // guard: never hold the page
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
  // Each report is played as its call, left to right through the month: the steady song is a trill of
  // rising notes, a watch is the trill breaking, an alert is the alarm's broadband chips, and a silent
  // station plays nothing — which is the point. Lines are spread across the stereo field.
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

  /* ---------- 5 share: copy the page's link ---------- */
  $$('[data-copy]').forEach((b) => b.addEventListener('click', async () => {
    const box = b.closest('.share'), note = box && $('.note', box);
    try { await navigator.clipboard.writeText(b.dataset.copy); if (note) note.textContent = 'Link copied.'; }
    catch (e) { if (note) note.textContent = b.dataset.copy; }
  }));

  firstCall();
  if (location.hash) setTimeout(() => flash(location.hash.slice(1)), 600);
})();
