// Real wheel scrolling through Chrome DevTools Protocol: does the page ever move backwards on its own?
// node --experimental-websocket tools/scrolltest.mjs <url> [width] [height] [steps]
// Prints the scroll positions after each wheel step; a position lower than the one before is a jump.
import { spawn } from 'node:child_process';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const [url, w = '1280', h = '800', steps = '8'] = process.argv.slice(2);
const port = 9500 + Math.floor(Math.random() * 300);
const proc = spawn('C:/Program Files/Google/Chrome/Application/chrome.exe', ['--headless=new', `--remote-debugging-port=${port}`,
  `--user-data-dir=${mkdtempSync(join(tmpdir(), 'cp-scroll-'))}`, 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let ws, id = 0; const pending = new Map();
const send = (method, params = {}) => new Promise((res, rej) => { const i = ++id; pending.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); });
const val = async (expr) => (await send('Runtime.evaluate', { expression: expr, returnByValue: true })).result.value;
try {
  let t; for (let k = 0; k < 50 && !t; k++) { try { t = (await (await fetch(`http://127.0.0.1:${port}/json`)).json()).find((x) => x.type === 'page'); } catch {} await sleep(150); }
  ws = new WebSocket(t.webSocketDebuggerUrl); await new Promise((r) => ws.addEventListener('open', r));
  ws.addEventListener('message', (ev) => { const m = JSON.parse(ev.data); if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id); m.error ? p.rej(new Error(m.error.message)) : p.res(m.result); } });
  await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: +w, height: +h, deviceScaleFactor: 1, mobile: +w < 768 });
  await send('Page.addScriptToEvaluateOnNewDocument', { source: "try{sessionStorage.setItem('cp-heard','1')}catch(e){}" });
  await send('Page.navigate', { url }); await sleep(2500);
  await val("window.__log=[];addEventListener('scroll',()=>__log.push(Math.round(scrollY)),{passive:true});1");
  const after = [];
  for (let i = 0; i < +steps; i++) {
    await send('Input.dispatchMouseEvent', { type: 'mouseWheel', x: +w / 2, y: +h / 2, deltaX: 0, deltaY: 700 });
    await sleep(900);
    after.push(await val('Math.round(scrollY)'));
  }
  const log = await val('__log');
  const jumps = log.filter((y, i) => i && y < log[i - 1]).length;
  console.log(url, w, 'after each step:', after.join(','), '| backward moves:', jumps, '| locked:', await val("getComputedStyle(document.body).overflow"));
} finally { try { ws.close(); } catch {} proc.kill(); }
