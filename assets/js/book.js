/* The identity book: the cover's head sings, the call cards play their call, the type sample
   takes a status, and the chapter bar follows the reader. */
(() => {
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // cover: every few seconds the head throws itself back and sings its trill
  const singer = $('.singer');
  if (singer && !reduce) {
    const hd = $('.hd', singer), notes = $$('.n', singer);
    const lens = notes.map((n) => n.getTotalLength());
    const [s0, s1] = window.CANARY_SHUT, [b0, b1] = window.CANARY_BEAK;
    const ease = (t) => 1 - Math.pow(1 - Math.min(1, Math.max(0, t)), 3);
    let t0 = performance.now(), visible = true;
    new IntersectionObserver(([e]) => { visible = e.isIntersecting; }).observe(singer);
    const CYCLE = 5200;
    const frame = (now) => {
      if (visible && !document.hidden) {
        const t = (now - t0) % CYCLE;
        // 0-300 open, 300-1100 sing, 2400-2700 close, rest quiet (the silence is part of the song)
        const open = t < 2400 ? ease(t / 300) : 1 - ease((t - 2400) / 300);
        const lo = s0 + (b0 - s0) * open, hi = s1 + (b1 - s1) * open;
        hd.setAttribute('d', window.canaryHead(150, 150, 0.2, lo, hi));
        hd.setAttribute('transform', `rotate(${-7 * open} 150 150)`);
        notes.forEach((n, i) => {
          const on = ease((t - 300 - i * 120) / 180), off = ease((t - 2100 - i * 60) / 260);
          n.style.strokeDasharray = lens[i];
          n.style.strokeDashoffset = lens[i] * (1 - on);
          n.style.opacity = 1 - off;
        });
      }
      requestAnimationFrame(frame);
    };
    requestAnimationFrame(frame);
  }

  // call cards: play one call
  let ctx = null;
  $$('[data-call]').forEach((b) => b.addEventListener('click', () => {
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return;
    ctx = ctx || new AC();
    if (ctx.state === 'suspended') ctx.resume();
    window.CanaryVoice.sing(ctx, ctx.currentTime + 0.03, b.dataset.call, 0);
  }));

  // type: the sample takes the sharpness of a status
  const demo = $('#axis-demo'), out = $('.axis .val-l');
  const SH = { steady: [0, 'soft'], watch: [62, 'halfway'], alert: [100, 'sharp'] };
  $$('.seg button').forEach((b) => b.addEventListener('click', () => {
    $$('.seg button').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
    demo.dataset.s = b.dataset.set;
    out.textContent = `SHRP ${SH[b.dataset.set][0]} · ${SH[b.dataset.set][1]}`;
  }));

  // chapter bar: mark the chapter being read, and slide the bar sideways to keep it in view.
  // Only the bar scrolls: scrollIntoView() would also move the page and fight the reader's scroll.
  const bar = $('.bk-top nav');
  const links = new Map($$('.bk-top li a').map((a) => [a.getAttribute('href').slice(1), a]));
  const io = new IntersectionObserver((es) => es.forEach((e) => {
    if (!e.isIntersecting) return;
    links.forEach((a, k) => a.setAttribute('aria-current', String(k === e.target.id)));
    const a = links.get(e.target.id);
    if (!a || !bar || bar.scrollWidth <= bar.clientWidth) return;
    const r = a.getBoundingClientRect(), b = bar.getBoundingClientRect();
    const left = bar.scrollLeft + (r.left - b.left) - (bar.clientWidth - r.width) / 2;
    bar.scrollTo({ left: Math.max(0, left), behavior: reduce ? 'auto' : 'smooth' });
  }), { rootMargin: '-45% 0px -50% 0px' });
  links.forEach((_, k) => { const s = document.getElementById(k); if (s) io.observe(s); });
})();
