"""
Stock Price Chart

Downloads one year (ending today) of daily closing prices for JPM, MSFT, MS, HOG and SAN
from Yahoo Finance and writes a standalone, interactive HTML dashboard with a
dropdown to choose which stock is displayed, headline stats, range buttons,
a data-table view and a fire-breathing dragon whose flame becomes the price line.

Run with:
    python scripts/stock_price_chart.py
Output:
    outputs/stock_price_chart.html   (loads Plotly from a CDN, so it needs internet to display)
"""

import json
from datetime import date, timedelta
from pathlib import Path

import yfinance as yf

# Ticker -> display name. Only one stock is shown at a time, so every line is drawn as dragon fire.
# Santander US (Santander Holdings USA) has no public listing; SAN is Banco Santander's NYSE-listed ADR.
TICKERS = {
    "JPM": "JPMorgan Chase & Co.",
    "MSFT": "Microsoft Corporation",
    "MS": "Morgan Stanley",
    "HOG": "Harley-Davidson, Inc.",
    "SAN": "Banco Santander, S.A. (Santander)",
}
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "outputs" / "stock_price_chart.html"

DRAGON_SVG = """
<svg class="dragon" viewBox="0 0 320 460" xmlns="http://www.w3.org/2000/svg" aria-label="A fire-breathing dragon" role="img">
  <defs>
    <linearGradient id="scale" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#ff7a3d"/><stop offset="0.55" stop-color="#d63a3a"/><stop offset="1" stop-color="#7a1531"/>
    </linearGradient>
    <linearGradient id="wing" x1="0" y1="1" x2="1" y2="0">
      <stop offset="0" stop-color="#5b1a4a"/><stop offset="1" stop-color="#b8323f"/>
    </linearGradient>
    <linearGradient id="flame" x1="1" y1="0" x2="0" y2="0">
      <stop offset="0" stop-color="#fff3a8"/><stop offset="0.35" stop-color="#ffb02e"/><stop offset="1" stop-color="#ff3d1f" stop-opacity="0"/>
    </linearGradient>
    <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <!-- wing -->
  <g class="wing">
    <path d="M168 190 C 190 110 250 50 312 34 C 298 72 306 92 290 118 C 282 142 270 152 262 182
             C 246 166 228 172 214 196 C 204 178 186 176 168 190 Z" fill="url(#wing)" stroke="#ff9a5c" stroke-width="1.5" stroke-linejoin="round"/>
    <path d="M168 190 L312 34 M190 186 L290 118 M214 196 L262 182" stroke="#ff9a5c" stroke-width="1.2" opacity=".55" fill="none"/>
  </g>

  <!-- tail (tapering) -->
  <g fill="none" stroke-linecap="round" stroke="url(#scale)">
    <path d="M150 300 C 130 340 170 368 214 372" stroke-width="22"/>
    <path d="M214 372 C 250 376 268 356 262 332" stroke-width="12"/>
    <path d="M262 332 C 258 318 272 306 286 314" stroke-width="6"/>
  </g>
  <path d="M280 306 L304 314 L284 326 Z" fill="#ffb02e"/>

  <!-- neck + torso -->
  <path d="M122 100 C 96 150 178 158 170 222 C 164 276 104 286 150 300" fill="none" stroke="url(#scale)" stroke-width="34" stroke-linecap="round" filter="url(#glow)"/>
  <!-- belly plates -->
  <path d="M112 128 C 108 150 142 160 146 178 M150 234 C 144 258 126 268 132 290" fill="none" stroke="#ffd9a0" stroke-width="3" stroke-dasharray="3 6" stroke-linecap="round" opacity=".7"/>
  <!-- back spikes -->
  <g fill="#ffb02e">
    <path d="M132 112 L150 100 L142 124 Z"/><path d="M158 152 L180 144 L168 170 Z"/>
    <path d="M184 204 L206 200 L190 226 Z"/><path d="M178 254 L200 256 L182 278 Z"/>
    <path d="M158 300 L178 308 L156 320 Z"/>
  </g>

  <!-- legs -->
  <g stroke="url(#scale)" stroke-width="12" stroke-linecap="round" fill="none">
    <path d="M136 240 L120 282 L106 290"/><path d="M162 262 L152 306 L138 314"/>
  </g>
  <g stroke="#ffd9a0" stroke-width="3" stroke-linecap="round"><path d="M106 290 l-8 2 M106 290 l-6 6 M138 314 l-8 2 M138 314 l-6 6"/></g>

  <!-- head -->
  <g filter="url(#glow)">
    <path d="M128 60 L104 40 L116 70 Z" fill="#ffb02e"/><path d="M144 66 L128 34 L134 74 Z" fill="#ffb02e"/>
    <path d="M150 74 C 130 56 92 60 62 82 L54 90 L72 96 L64 104 C 84 116 116 122 142 112 C 158 104 160 86 150 74 Z" fill="url(#scale)" stroke="#ffb02e" stroke-width="1.5" stroke-linejoin="round"/>
    <path d="M70 98 L80 92 L88 100 L96 94 L104 102" fill="none" stroke="#fff" stroke-width="2" stroke-linejoin="round"/>
    <path d="M118 84 L100 76 L104 90 Z" fill="#111"/><circle cx="106" cy="83" r="3.4" fill="#ffe14a" class="eye"/>
    <circle cx="74" cy="84" r="2" fill="#111"/>
  </g>

  <!-- fire breath -->
  <g class="fire" filter="url(#glow)">
    <path d="M56 92 C 34 70 10 78 0 62 C 12 96 -2 110 8 128 C 22 110 34 126 46 112 C 52 106 56 100 56 92 Z" fill="url(#flame)"/>
    <path d="M56 94 C 40 88 24 96 14 92 C 24 104 30 108 44 104 Z" fill="#fff3a8" opacity=".9"/>
  </g>
  <circle id="flame-tip" cx="2" cy="95" r="1" fill="none"/>
</svg>
"""

# Placeholders are swapped in with str.replace so the CSS/JS braces need no escaping.
TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dragon Stock Watch</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>
<style>
  :root {
    --bg-0: #0b0a12;
    --bg-1: #16141f;
    --surface: #1a1825;
    --line: #2c2940;
    --text-primary: #ffffff;
    --text-secondary: #c3c2d0;
    --text-muted: #8a88a0;
    --accent: #ff7a3d;
    --up: #2fbf8f;
    --down: #e66767;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; }
  body {
    min-height: 100vh;
    color: var(--text-primary);
    font-family: "Segoe UI", system-ui, -apple-system, Roboto, sans-serif;
    background:
      radial-gradient(900px 500px at 12% -10%, rgba(255, 122, 61, .16), transparent 70%),
      radial-gradient(800px 600px at 100% 100%, rgba(214, 58, 58, .22), transparent 70%),
      var(--bg-0);
    transition: background .4s;
  }
  .page { position: relative; max-width: 1440px; margin: 0 auto; padding: 28px 24px 40px; display: grid; grid-template-columns: minmax(0, 1fr) 320px; gap: 24px; }
  header { grid-column: 1 / -1; display: flex; flex-wrap: wrap; gap: 16px 24px; align-items: flex-end; justify-content: space-between; }
  h1 { margin: 0; font-size: clamp(26px, 4vw, 40px); font-weight: 800; letter-spacing: -.02em;
       background: linear-gradient(90deg, #fff3a8, #ffb02e 35%, #ff5a3d 75%, #d63a3a); -webkit-background-clip: text; background-clip: text; color: transparent; }
  .sub { margin: 4px 0 0; color: var(--text-secondary); font-size: 14px; }

  .picker { display: flex; align-items: center; gap: 10px; }
  .picker label { color: var(--text-muted); font-size: 12px; text-transform: uppercase; letter-spacing: .12em; }
  .select-wrap { position: relative; }
  .select-wrap::after { content: ""; position: absolute; right: 16px; top: 50%; width: 8px; height: 8px; margin-top: -6px;
                        border-right: 2px solid var(--text-primary); border-bottom: 2px solid var(--text-primary); transform: rotate(45deg); pointer-events: none; }
  select { appearance: none; -webkit-appearance: none; color: var(--text-primary); background: var(--surface); border: 1px solid var(--accent);
           border-radius: 12px; padding: 12px 42px 12px 16px; font: 700 16px inherit; cursor: pointer;
           box-shadow: 0 0 0 0 transparent, 0 0 22px -6px var(--accent); transition: box-shadow .2s, border-color .4s; }
  select:hover, select:focus-visible { outline: none; box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 35%, transparent), 0 0 26px -4px var(--accent); }
  select option { background: var(--surface); color: var(--text-primary); }

  main { min-width: 0; }
  .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-bottom: 16px; }
  .stat { background: linear-gradient(180deg, rgba(255,255,255,.05), rgba(255,255,255,.015)); border: 1px solid var(--line);
          border-radius: 14px; padding: 14px 16px; backdrop-filter: blur(6px); }
  .stat .k { color: var(--text-muted); font-size: 11px; text-transform: uppercase; letter-spacing: .12em; }
  .stat .v { margin-top: 6px; font-size: 26px; font-weight: 800; font-variant-numeric: tabular-nums; }
  .stat .d { margin-top: 2px; font-size: 12px; color: var(--text-secondary); font-variant-numeric: tabular-nums; }
  .up { color: var(--up); } .down { color: var(--down); }

  .card { background: color-mix(in srgb, var(--surface) 88%, transparent); border: 1px solid var(--line); border-radius: 18px; padding: 16px 16px 8px;
          box-shadow: 0 20px 60px -30px #000, inset 0 1px 0 rgba(255,255,255,.05); }
  .toolbar { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; justify-content: space-between; margin: 2px 4px 6px; }
  .chip { display: inline-flex; align-items: center; gap: 8px; color: var(--text-secondary); font-size: 14px; }
  .chip i { width: 22px; height: 4px; border-radius: 2px; background: linear-gradient(90deg, #ff3d1f, #ffb02e, #fff3a8); box-shadow: 0 0 10px #ff7a3d; }
  .ranges { display: flex; gap: 6px; }
  .ranges button, .toggle { color: var(--text-secondary); background: transparent; border: 1px solid var(--line); border-radius: 999px; padding: 6px 14px;
                            font: 600 13px inherit; cursor: pointer; transition: all .15s; }
  .ranges button:hover, .toggle:hover { color: var(--text-primary); border-color: var(--accent); }
  .ranges button.on { color: #fff; background: var(--accent); border-color: var(--accent); box-shadow: 0 0 16px -3px var(--accent); }
  #chart { height: 470px; }

  #table-view { display: none; max-height: 470px; overflow: auto; }
  #table-view table { width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; font-size: 14px; }
  #table-view th, #table-view td { text-align: right; padding: 8px 12px; border-bottom: 1px solid var(--line); }
  #table-view th { position: sticky; top: 0; background: var(--surface); color: var(--text-muted); font-weight: 600; }
  #table-view th:first-child, #table-view td:first-child { text-align: left; }
  .show-table #table-view { display: block; } .show-table #chart { display: none; }

  aside { position: relative; display: flex; align-items: flex-end; justify-content: center; }
  .dragon { width: 100%; height: auto; max-height: 100%; overflow: visible; filter: drop-shadow(0 0 24px rgba(255, 90, 61, .35)); animation: hover 5s ease-in-out infinite; }
  .dragon .fire { transform-origin: 56px 92px; animation: flicker .35s ease-in-out infinite alternate; }
  .dragon .wing { transform-origin: 168px 190px; animation: flap 2.6s ease-in-out infinite; }
  .dragon .eye { animation: blink 4s infinite; }
  @keyframes hover { 50% { transform: translateY(-10px); } }
  @keyframes flicker { from { transform: scale(1, 1); opacity: .95; } to { transform: scale(1.14, .9); opacity: .78; } }
  @keyframes flap { 50% { transform: rotate(-7deg); } }
  @keyframes blink { 46%, 50% { fill: #111; } }

  #stream { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; overflow: visible; z-index: 5; }
  #stream path { fill: none; stroke-linecap: round; }
  #stream .core { stroke-dasharray: 18 10; animation: lick .7s linear infinite; }
  @keyframes lick { to { stroke-dashoffset: -28; } }
  footer { grid-column: 1 / -1; color: var(--text-muted); font-size: 12px; }

  @media (max-width: 980px) { .page { grid-template-columns: 1fr; } aside, #stream { display: none; } }
  @media (prefers-reduced-motion: reduce) { .dragon, .dragon *, #stream * { animation: none !important; } }
</style>
</head>
<body>
<div class="page">
  <header>
    <div>
      <h1>Dragon Stock Watch</h1>
      <p class="sub">Daily closing prices &middot; __START__ to __END__ &middot; source: Yahoo Finance</p>
    </div>
    <div class="picker">
      <label for="ticker">Choose stock</label>
      <div class="select-wrap"><select id="ticker">__OPTIONS__</select></div>
    </div>
  </header>

  <main>
    <section class="stats" aria-live="polite">
      <div class="stat"><div class="k">Latest close</div><div class="v" id="s-last"></div><div class="d" id="s-last-d"></div></div>
      <div class="stat"><div class="k">1-year change</div><div class="v" id="s-chg"></div><div class="d" id="s-chg-d"></div></div>
      <div class="stat"><div class="k">52-week high</div><div class="v" id="s-hi"></div><div class="d" id="s-hi-d"></div></div>
      <div class="stat"><div class="k">52-week low</div><div class="v" id="s-lo"></div><div class="d" id="s-lo-d"></div></div>
    </section>

    <section class="card" id="card">
      <div class="toolbar">
        <span class="chip"><i></i><span id="chip-name"></span></span>
        <div class="ranges" role="group" aria-label="Time range">
          <button data-days="30">1M</button><button data-days="91">3M</button><button data-days="182">6M</button><button data-days="365" class="on">1Y</button>
          <button class="toggle" id="toggle" aria-pressed="false">Table view</button>
        </div>
      </div>
      <div id="chart"></div>
      <div id="table-view"></div>
    </section>
  </main>

  <aside>__DRAGON__</aside>
  <svg id="stream" aria-hidden="true">
    <path class="glow" stroke="#ff3d1f" stroke-opacity=".25" stroke-width="16"/>
    <path class="mid" stroke="#ff7a3d" stroke-opacity=".7" stroke-width="7"/>
    <path class="core" stroke="#ffe27a" stroke-width="2.5"/>
  </svg>
  <footer>Closing prices are not adjusted for dividends. Not investment advice &mdash; the dragon hoards, it does not advise.</footer>
</div>

<script>
const DATA = __DATA__;
const $ = id => document.getElementById(id);
const money = v => "$" + v.toLocaleString("en-US", {minimumFractionDigits: 2, maximumFractionDigits: 2});
const day = s => new Date(s + "T00:00:00").toLocaleDateString("en-US", {month: "short", day: "numeric", year: "numeric"});
const tickers = Object.keys(DATA);
const css = getComputedStyle(document.documentElement);
const ink = n => css.getPropertyValue(n).trim();

function hexToRgba(hex, a) {
  const n = parseInt(hex.slice(1), 16);
  return "rgba(" + (n >> 16) + "," + ((n >> 8) & 255) + "," + (n & 255) + "," + a + ")";
}

// Each stock is drawn as fire: a wide red glow, an orange body with a fading fill, and a hot yellow core.
const FIRE = "255,122,61";
const traces = [];
tickers.forEach((t, i) => {
  const base = {x: DATA[t].dates, y: DATA[t].closes, type: "scatter", mode: "lines", name: t, visible: i === 0, hoverinfo: "skip"};
  const spline = w => ({shape: "spline", smoothing: 0.4, width: w});
  traces.push({...base, line: {color: "rgba(255,61,31,0.22)", ...spline(14)}});
  traces.push({...base, line: {color: "rgba(" + FIRE + ",0.75)", ...spline(6)},
    fill: "tozeroy", fillgradient: {type: "vertical", colorscale: [[0, "rgba(255,61,31,0)"], [1, "rgba(" + FIRE + ",0.34)"]]}});
  traces.push({...base, line: {color: "#ffe27a", ...spline(2.2)}, hoverinfo: "x+y",
    hovertemplate: "<b>%{x|%b %d, %Y}</b><br>Close  $%{y:,.2f}<extra>" + t + "</extra>"});
});

const layout = {
  paper_bgcolor: "rgba(0,0,0,0)", plot_bgcolor: "rgba(0,0,0,0)", margin: {l: 56, r: 16, t: 10, b: 40},
  font: {family: "Segoe UI, system-ui, sans-serif", color: ink("--text-secondary"), size: 13},
  xaxis: {gridcolor: "rgba(255,255,255,.04)", linecolor: ink("--line"), tickfont: {color: ink("--text-muted")}, showspikes: true,
          spikemode: "across", spikecolor: "rgba(255,255,255,.35)", spikethickness: 1, spikedash: "dot"},
  yaxis: {gridcolor: "rgba(255,255,255,.07)", zeroline: false, tickprefix: "$", tickfont: {color: ink("--text-muted")}, fixedrange: true},
  hovermode: "x", hoverlabel: {bgcolor: "#0e0d16", bordercolor: "#3a3754", font: {color: "#fff", size: 13}},
  showlegend: false, dragmode: "pan"
};

Plotly.newPlot("chart", traces, layout, {responsive: true, displayModeBar: false, scrollZoom: false});

function stats(t) {
  const d = DATA[t], n = d.closes.length, last = d.closes[n - 1], first = d.closes[0];
  const hi = Math.max(...d.closes), lo = Math.min(...d.closes);
  const chg = last - first, pct = chg / first * 100, cls = chg >= 0 ? "up" : "down", sign = chg >= 0 ? "+" : "";
  $("s-last").textContent = money(last);   $("s-last-d").textContent = "as of " + day(d.dates[n - 1]);
  $("s-chg").textContent = sign + pct.toFixed(1) + "%"; $("s-chg").className = "v " + cls;
  $("s-chg-d").textContent = (chg >= 0 ? "\\u25B2 " : "\\u25BC ") + sign + money(chg).replace("$-", "-$");
  $("s-hi").textContent = money(hi);       $("s-hi-d").textContent = day(d.dates[d.closes.indexOf(hi)]);
  $("s-lo").textContent = money(lo);       $("s-lo-d").textContent = day(d.dates[d.closes.indexOf(lo)]);
}

function table(t) {
  const d = DATA[t];
  let rows = "";
  for (let i = d.dates.length - 1; i >= 0; i--) {
    const prev = i > 0 ? d.closes[i - 1] : null;
    const ch = prev === null ? "" : ((d.closes[i] / prev - 1) * 100).toFixed(2) + "%";
    rows += "<tr><td>" + day(d.dates[i]) + "</td><td>" + money(d.closes[i]) + "</td><td class='" + (ch.startsWith("-") ? "down" : "up") + "'>" + ch + "</td></tr>";
  }
  $("table-view").innerHTML = "<table><thead><tr><th>Date</th><th>" + t + " close</th><th>Daily change</th></tr></thead><tbody>" + rows + "</tbody></table>";
}

let days = 365;
function setRange(n) {
  days = n;
  document.querySelectorAll(".ranges button[data-days]").forEach(b => b.classList.toggle("on", +b.dataset.days === n));
  const d = DATA[$("ticker").value], end = new Date(d.dates[d.dates.length - 1] + "T00:00:00");
  const start = new Date(end); start.setDate(start.getDate() - n);
  const from = start.toISOString().slice(0, 10);
  const shown = d.closes.filter((_, i) => d.dates[i] >= from);
  const lo = Math.min(...shown), hi = Math.max(...shown), pad = (hi - lo) * 0.12 || 1;
  // The area fill reaches down to $0, so autorange would flatten the line; scale to the visible window instead.
  Plotly.relayout("chart", {"xaxis.range": [from, d.dates[d.dates.length - 1]], "yaxis.range": [lo - pad, hi + pad]});
}

function select(t) {
  Plotly.restyle("chart", {visible: tickers.flatMap(x => [x === t, x === t, x === t])});
  $("chip-name").textContent = t + " \\u2014 " + DATA[t].name;
  stats(t); table(t); setRange(days);
}

$("ticker").addEventListener("change", e => select(e.target.value));
document.querySelectorAll(".ranges button[data-days]").forEach(b => b.addEventListener("click", () => setRange(+b.dataset.days)));
$("toggle").addEventListener("click", e => {
  const on = document.body.classList.toggle("show-table");
  e.target.textContent = on ? "Chart view" : "Table view"; e.target.setAttribute("aria-pressed", on);
  if (!on) Plotly.Plots.resize("chart");
});
select(tickers[0]);

// The dragon's flame flows into the end of the price line; re-aimed every frame because the dragon floats.
const stream = $("stream"), tip = $("flame-tip"), chart = $("chart");
function aim() {
  const fl = chart._fullLayout, d = DATA[$("ticker").value];
  if (fl && fl.xaxis && fl.yaxis && fl.xaxis.range && fl.yaxis.range && stream.getClientRects().length) {
    const box = chart.getBoundingClientRect(), root = stream.getBoundingClientRect(), t = tip.getBoundingClientRect();
    const last = d.closes[d.closes.length - 1];
    const px = box.left + fl._size.l + fl.xaxis.l2p(new Date(d.dates[d.dates.length - 1] + "T00:00:00").getTime()) - root.left;
    const py = box.top + fl._size.t + fl.yaxis.l2p(last) - root.top;
    const mx = t.left - root.left, my = t.top - root.top;
    const path = "M" + mx + " " + my + " C " + (mx - 70) + " " + my + ", " + (px + 90) + " " + py + ", " + px + " " + py;
    stream.querySelectorAll("path").forEach(p => p.setAttribute("d", path));
  }
  requestAnimationFrame(aim);
}
aim();
</script>
</body>
</html>
"""


def fetch_closing_prices(tickers, start, end):
    """Return a DataFrame of daily closing prices, one column per ticker."""
    data = yf.download(list(tickers), start=start, end=end, auto_adjust=False, progress=False)
    if data.empty:
        raise RuntimeError("Yahoo Finance returned no data. Check your internet connection.")
    return data["Close"]


def build_html(closes, start, end):
    payload = {}
    for ticker, name in TICKERS.items():
        series = closes[ticker].dropna()
        payload[ticker] = {
            "name": name,
            "dates": [d.strftime("%Y-%m-%d") for d in series.index],
            "closes": [round(float(v), 2) for v in series.values],
        }
    options = "".join(f'<option value="{t}">{t} &middot; {name}</option>' for t, name in TICKERS.items())
    return (
        TEMPLATE.replace("__DATA__", json.dumps(payload))
        .replace("__OPTIONS__", options)
        .replace("__DRAGON__", DRAGON_SVG)
        .replace("__START__", start.strftime("%b %d, %Y"))
        .replace("__END__", end.strftime("%b %d, %Y"))
    )


def main():
    end = date.today()
    start = end - timedelta(days=365)

    print(f"Downloading {', '.join(TICKERS)} closing prices from {start} to {end}...")
    closes = fetch_closing_prices(TICKERS, start, end + timedelta(days=1))  # end date is exclusive

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(build_html(closes, start, end), encoding="utf-8")
    print(f"Chart saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
