/* The canary's four calls, synthesised (no audio files). Played only after a reader presses a button.
   steady  the song: a trill of four rising notes
   watch   the song breaking: a note, a gap, two falling notes
   alert   the alarm: broadband chips in pairs, the way an alarm call shows on a sonogram
   silent  nothing */
window.CanaryVoice = (() => {
  const noises = new WeakMap();
  function noise(ctx) {
    if (!noises.has(ctx)) {
      const b = ctx.createBuffer(1, Math.round(ctx.sampleRate * 0.05), ctx.sampleRate), ch = b.getChannelData(0);
      for (let i = 0; i < ch.length; i++) ch[i] = Math.random() * 2 - 1;
      noises.set(ctx, b);
    }
    return noises.get(ctx);
  }
  function out(ctx, pan) {
    const p = ctx.createStereoPanner();
    p.pan.value = pan || 0;
    p.connect(ctx.destination);
    return p;
  }
  function chirp(ctx, t, f0, f1, dur, g, pan) {
    const o = ctx.createOscillator(), a = ctx.createGain();
    o.type = 'sine';
    o.frequency.setValueAtTime(f0, t);
    o.frequency.exponentialRampToValueAtTime(f1, t + dur);
    a.gain.setValueAtTime(0.0001, t);
    a.gain.exponentialRampToValueAtTime(g, t + dur * 0.25);
    a.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    o.connect(a).connect(out(ctx, pan));
    o.start(t);
    o.stop(t + dur + 0.02);
  }
  function chip(ctx, t, g, pan) {
    const src = ctx.createBufferSource(), bp = ctx.createBiquadFilter(), a = ctx.createGain();
    src.buffer = noise(ctx);
    bp.type = 'bandpass'; bp.frequency.value = 4200; bp.Q.value = 1.4;
    a.gain.setValueAtTime(0.0001, t);
    a.gain.exponentialRampToValueAtTime(g, t + 0.004);
    a.gain.exponentialRampToValueAtTime(0.0001, t + 0.03);
    src.connect(bp).connect(a).connect(out(ctx, pan));
    src.start(t);
    src.stop(t + 0.04);
  }
  function sing(ctx, t, s, pan) {
    if (s === 'steady') for (let i = 0; i < 4; i++) chirp(ctx, t + i * 0.075, 2600 + i * 170, 4100 + i * 170, 0.05, 0.05, pan);
    if (s === 'watch') {
      chirp(ctx, t, 2600, 4000, 0.05, 0.05, pan);
      chirp(ctx, t + 0.16, 3100, 3500, 0.045, 0.04, pan);
      chirp(ctx, t + 0.24, 3000, 2500, 0.06, 0.035, pan);
    }
    if (s === 'alert') [0, 0.055, 0.2, 0.255].forEach((d) => chip(ctx, t + d, 0.22, pan));
  }
  return { sing, length: { steady: 0.3, watch: 0.32, alert: 0.29, silent: 0 } };
})();
