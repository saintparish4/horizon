"""
Render benchmarks/results.json into a self-contained HTML report.

    python -m benchmarks.chart

Design follows the project's dataviz rules: two categorical hues for the two
strategies actually being compared, de-emphasis gray for context, a dashed
reference line for the oracle ceiling (chrome, not a series), hairline grid,
legend plus selective direct labels, a crosshair tooltip, a table view, and a
dark mode stepped for the dark surface rather than flipped.
"""

import json
import pathlib

RESULTS = pathlib.Path("benchmarks/results.json")
OUTPUT = pathlib.Path("benchmarks/routing_benchmark.html")

# Plot geometry
W, H = 900, 400
PAD_L, PAD_R, PAD_T, PAD_B = 52, 132, 24, 44
PW, PH = W - PAD_L - PAD_R, H - PAD_T - PAD_B

# Series roles. Order is fixed and follows the entity, never its rank.
SERIES = [
    ("horizon", "Horizon", "var(--series-1)", 2.0, None),
    ("capability", "Capability-only", "var(--series-2)", 2.0, None),
    ("random", "Random", "var(--muted)", 2.0, None),
]
ORACLE = ("oracle", "Oracle ceiling", "var(--muted)", 1.5, "6 4")


def _x(i: int, n: int) -> float:
    return PAD_L + (PW * i / max(1, n - 1))


def _y(v: float) -> float:
    return PAD_T + PH * (1 - v)


def _path(values: list[float]) -> str:
    n = len(values)
    return "M" + " L".join(f"{_x(i, n):.2f},{_y(v):.2f}" for i, v in enumerate(values))


def _gridlines() -> str:
    out = []
    for pct in range(0, 101, 20):
        y = _y(pct / 100)
        out.append(
            f'<line class="grid" x1="{PAD_L}" y1="{y:.1f}" x2="{PAD_L + PW}" y2="{y:.1f}"/>'
            f'<text class="tick y" x="{PAD_L - 10}" y="{y + 4:.1f}">{pct}%</text>'
        )
    return "".join(out)


def _xaxis(n: int, offset: int = 0) -> str:
    out = [
        f'<line class="axis" x1="{PAD_L}" y1="{PAD_T + PH}" x2="{PAD_L + PW}" y2="{PAD_T + PH}"/>'
    ]
    # Round tick values, not evenly-divided indices — 599/799/999 reads as noise.
    step = 200 if n > 600 else 100 if n > 300 else 50
    ticks = list(range(0, n, step))
    if ticks[-1] < n - 1:
        ticks.append(n - 1)
    for i in ticks:
        x = _x(i, n)
        label = n + offset if i == n - 1 else i + offset
        out.append(f'<text class="tick x" x="{x:.1f}" y="{PAD_T + PH + 22}">{label:,}</text>')
    out.append(f'<text class="axis-title" x="{PAD_L + PW / 2:.0f}" y="{H - 4}">Tasks routed</text>')
    return "".join(out)


def _end_label(key: str, label: str, color: str, values: list[float], n: int) -> str:
    """End dot with a 2px surface ring, plus a direct label in the gutter."""
    v = values[-1]
    x, y = _x(n - 1, n), _y(v)
    return (
        f'<circle class="end-dot" cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{color}"/>'
        f'<text class="end-label" x="{x + 12:.1f}" y="{y - 2:.1f}">{label}</text>'
        f'<text class="end-value" x="{x + 12:.1f}" y="{y + 13:.1f}">{v:.0%}</text>'
    )


def build(data: dict) -> str:
    strat = data["strategies"]
    cfg = data["config"]

    # Drop just the first few points, where the rolling mean is computed over a
    # handful of samples and swings between 0% and 100%. Trimming the full window
    # would cut the convergence, which is the thing the chart exists to show.
    warmup = min(20, len(strat["horizon"]["rolling"]) - 1)
    for st in strat.values():
        st["rolling"] = st["rolling"][warmup:]
    n = len(strat["horizon"]["rolling"])

    horizon_final = strat["horizon"]["final_accuracy"]
    cap_final = strat["capability"]["final_accuracy"]
    oracle_final = strat["oracle"]["final_accuracy"]
    lift = horizon_final - cap_final
    ceiling_pct = horizon_final / oracle_final if oracle_final else 0

    # --- plot marks -------------------------------------------------------
    marks = []
    oracle_vals = strat["oracle"]["rolling"]
    marks.append(
        f'<path class="line ref" d="{_path(oracle_vals)}" stroke="{ORACLE[2]}" '
        f'stroke-width="{ORACLE[3]}" stroke-dasharray="{ORACLE[4]}"/>'
    )
    # Annotate the ceiling inline, mid-plot. At the right edge it lands on top of
    # Horizon (they converge by design) and the two labels become unreadable.
    ref_x = PAD_L + PW * 0.30
    ref_i = int((n - 1) * 0.30)
    marks.append(
        f'<text class="ref-label" x="{ref_x:.0f}" y="{_y(oracle_vals[ref_i]) - 10:.1f}">'
        f"Oracle ceiling</text>"
    )
    for key, _label, color, width, _dash in SERIES:
        vals = strat[key]["rolling"]
        marks.append(
            f'<path class="line" d="{_path(vals)}" stroke="{color}" stroke-width="{width}"/>'
        )
    for key, label, color, _w, _d in SERIES:
        marks.append(_end_label(key, label, color, strat[key]["rolling"], n))

    # --- pick distribution ------------------------------------------------
    agents = list(strat["horizon"]["pick_distribution"].keys())
    best_by_agent = data.get("best_agent_for", {})
    bars = []
    bw, gap, group = 24, 8, 92
    bx0 = 30
    # Scale to the tallest bar, with headroom for its label.
    peak = max(max(strat[k]["pick_distribution"].values()) for k in ("horizon", "capability"))
    span = 132 / max(0.01, peak * 1.12)
    for i, a in enumerate(agents):
        gx = bx0 + i * group
        for j, (key, color) in enumerate(
            (("horizon", "var(--series-1)"), ("capability", "var(--series-2)"))
        ):
            v = strat[key]["pick_distribution"][a]
            h = max(0.0, v) * span
            x = gx + j * (bw + gap)
            y = 160 - h
            bars.append(
                f'<rect class="bar" x="{x}" y="{y:.1f}" width="{bw}" height="{h:.1f}" '
                f'rx="3" fill="{color}"><title>{key}: {a} {v:.0%}</title></rect>'
            )
            if v > 0.02:
                bars.append(
                    f'<text class="bar-value" x="{x + bw / 2}" y="{y - 6:.1f}">{v:.0%}</text>'
                )
        note = " ★" if best_by_agent.get(a) else ""
        bars.append(f'<text class="bar-label" x="{gx + bw + gap / 2}" y="196">{a}{note}</text>')

    # --- table view -------------------------------------------------------
    rows = "".join(
        f"<tr><th scope='row'>{name}</th>"
        f"<td>{strat[k]['overall_accuracy']:.1%}</td>"
        f"<td>{strat[k]['final_accuracy']:.1%}</td>"
        f"<td>${strat[k]['cost_per_success']:.4f}</td>"
        f"<td>${strat[k]['total_cost']:.2f}</td></tr>"
        for k, name in (
            ("oracle", "Oracle ceiling"),
            ("horizon", "Horizon"),
            ("capability", "Capability-only"),
            ("random", "Random"),
        )
    )
    fam_rows = "".join(
        f"<tr><th scope='row'>{fam.replace('_', ' ')}</th>"
        f"<td>{d['oracle']:.0%}</td><td>{d['horizon']:.0%}</td>"
        f"<td>{d['capability']:.0%}</td><td>{d['random']:.0%}</td></tr>"
        for fam, d in data["per_family"].items()
    )

    series_js = json.dumps(
        {
            "n": n,
            "offset": warmup,
            "padL": PAD_L,
            "padT": PAD_T,
            "pw": PW,
            "ph": PH,
            "series": [
                {"key": "oracle", "label": "Oracle ceiling", "values": strat["oracle"]["rolling"]},
                *[
                    {"key": k, "label": lbl, "values": strat[k]["rolling"]}
                    for k, lbl, _c, _w, _d in SERIES
                ],
            ],
        }
    )

    return TEMPLATE.format(
        tasks=f"{cfg['tasks']:,}",
        window=cfg["window"],
        tail=f"{cfg['tail']:,}",
        seed=cfg["seed"],
        horizon_final=f"{horizon_final:.1%}",
        lift=f"{lift * 100:+.1f}pp",
        ceiling=f"{ceiling_pct:.0%}",
        cost=f"${strat['horizon']['cost_per_success']:.4f}",
        cost_random=f"${strat['random']['cost_per_success']:.4f}",
        cap_final=f"{cap_final:.1%}",
        grid=_gridlines(),
        xaxis=_xaxis(n, warmup),
        marks="".join(marks),
        bars="".join(bars),
        rows=rows,
        fam_rows=fam_rows,
        W=W,
        H=H,
        PAD_T=PAD_T,
        PAD_L=PAD_L,
        PW=PW,
        PH=PH,
        PH_END=PAD_T + PH,
        series_js=series_js,
    )


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Horizon routing benchmark</title>
<style>
  .viz-root {{
    color-scheme: light;
    --surface-1: #fcfcfb;
    --plane: #f9f9f7;
    --text-primary: #0b0b0b;
    --text-secondary: #52514e;
    --muted: #898781;
    --grid: #e1e0d9;
    --axis: #c3c2b7;
    --border: rgba(11,11,11,0.10);
    --series-1: #2a78d6;
    --series-2: #eb6834;
  }}
  @media (prefers-color-scheme: dark) {{
    :root:where(:not([data-theme="light"])) .viz-root {{
      color-scheme: dark;
      --surface-1: #1a1a19;
      --plane: #0d0d0d;
      --text-primary: #ffffff;
      --text-secondary: #c3c2b7;
      --muted: #898781;
      --grid: #2c2c2a;
      --axis: #383835;
      --border: rgba(255,255,255,0.10);
      --series-1: #3987e5;
      --series-2: #d95926;
    }}
  }}
  :root[data-theme="dark"] .viz-root {{
    color-scheme: dark;
    --surface-1: #1a1a19; --plane: #0d0d0d;
    --text-primary: #ffffff; --text-secondary: #c3c2b7; --muted: #898781;
    --grid: #2c2c2a; --axis: #383835; --border: rgba(255,255,255,0.10);
    --series-1: #3987e5; --series-2: #d95926;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: var(--plane); }}
  .viz-root {{
    font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
    background: var(--plane); color: var(--text-primary);
    padding: 40px 24px 64px; min-height: 100vh;
  }}
  .wrap {{ max-width: 980px; margin: 0 auto; }}
  h1 {{ font-size: 22px; font-weight: 600; margin: 0 0 6px; letter-spacing: -0.01em; }}
  .sub {{ color: var(--text-secondary); font-size: 13.5px; margin: 0 0 28px; line-height: 1.55; }}
  .card {{
    background: var(--surface-1); border: 1px solid var(--border);
    border-radius: 12px; padding: 22px 24px; margin-bottom: 20px;
  }}
  .kpis {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px;
           background: var(--border); border: 1px solid var(--border);
           border-radius: 12px; overflow: hidden; margin-bottom: 20px; }}
  .kpi {{ background: var(--surface-1); padding: 18px 20px; }}
  .kpi .label {{ font-size: 12px; color: var(--text-secondary); margin-bottom: 8px; }}
  .kpi .value {{ font-size: 30px; font-weight: 600; letter-spacing: -0.02em; line-height: 1; }}
  .kpi .value.hero {{ font-size: 48px; }}
  .kpi .note {{ font-size: 11.5px; color: var(--muted); margin-top: 7px; }}
  h2 {{ font-size: 14px; font-weight: 600; margin: 0 0 3px; }}
  .cap {{ font-size: 12.5px; color: var(--text-secondary); margin: 0 0 16px; line-height: 1.5; }}
  .legend {{ display: flex; gap: 20px; flex-wrap: wrap; margin: 0 0 12px; }}
  .legend span {{ display: inline-flex; align-items: center; gap: 7px;
                  font-size: 12.5px; color: var(--text-secondary); }}
  .key {{ width: 14px; height: 2px; border-radius: 1px; }}
  .key.dash {{ background: repeating-linear-gradient(90deg,
               var(--muted) 0 4px, transparent 4px 7px); height: 2px; }}
  svg {{ display: block; width: 100%; height: auto; overflow: visible; }}
  .grid {{ stroke: var(--grid); stroke-width: 1; }}
  .axis {{ stroke: var(--axis); stroke-width: 1; }}
  .line {{ fill: none; stroke-linejoin: round; stroke-linecap: round; }}
  .tick {{ fill: var(--muted); font-size: 11px; }}
  .tick.y {{ text-anchor: end; }}
  .tick.x {{ text-anchor: middle; }}
  .axis-title {{ fill: var(--text-secondary); font-size: 12px; text-anchor: middle; }}
  .end-dot {{ stroke: var(--surface-1); stroke-width: 2; }}
  .end-label, .ref-label {{ fill: var(--text-primary); font-size: 12px; font-weight: 500; }}
  .ref-label {{ fill: var(--text-secondary); }}
  .end-value {{ fill: var(--text-secondary); font-size: 11.5px; }}
  .bar-label {{ fill: var(--text-secondary); font-size: 11.5px; text-anchor: middle; }}
  .bar-value {{ fill: var(--muted); font-size: 10.5px; text-anchor: middle; }}
  .crosshair {{ stroke: var(--axis); stroke-width: 1; opacity: 0; }}
  .hover-dot {{ stroke: var(--surface-1); stroke-width: 2; opacity: 0; }}
  .tip {{
    position: absolute; pointer-events: none; opacity: 0; transition: opacity .1s;
    background: var(--surface-1); border: 1px solid var(--border); border-radius: 8px;
    padding: 9px 11px; font-size: 12px; box-shadow: 0 4px 14px rgba(0,0,0,.10);
    min-width: 150px; z-index: 5;
  }}
  .tip .h {{ color: var(--text-secondary); margin-bottom: 6px; font-size: 11.5px; }}
  .tip .r {{ display: flex; align-items: center; gap: 7px; margin-top: 3px; }}
  .tip .r b {{ margin-left: auto; font-variant-numeric: tabular-nums; font-weight: 600; }}
  .dot {{ width: 8px; height: 8px; border-radius: 50%; flex: none; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 12.5px; }}
  th, td {{ text-align: right; padding: 8px 10px; border-bottom: 1px solid var(--border); }}
  th[scope=row] {{ text-align: left; font-weight: 500; }}
  thead th {{ color: var(--text-secondary); font-weight: 500; font-size: 11.5px; }}
  td {{ font-variant-numeric: tabular-nums; color: var(--text-secondary); }}
  .foot {{ font-size: 11.5px; color: var(--muted); margin-top: 18px; line-height: 1.6; }}
</style>
</head>
<body>
<div class="viz-root"><div class="wrap">

  <h1>Routing accuracy improves with execution history</h1>
  <p class="sub">
    {tasks} synthetic tasks across four families, five agents, seed {seed}.
    Every strategy sees the same task stream and the same random draw per task,
    so the oracle is a strict per-task upper bound.
    <b>Capability-only</b> is the identical router with the feedback loop switched
    off &mdash; it isolates what the execution history contributes.
    Curves are a {window}-task rolling mean.
  </p>

  <div class="kpis">
    <div class="kpi">
      <div class="label">Horizon accuracy</div>
      <div class="value hero">{horizon_final}</div>
      <div class="note">final {tail} tasks</div>
    </div>
    <div class="kpi">
      <div class="label">Lift from the feedback loop</div>
      <div class="value">{lift}</div>
      <div class="note">vs {cap_final} capability-only</div>
    </div>
    <div class="kpi">
      <div class="label">Of achievable ceiling</div>
      <div class="value">{ceiling}</div>
      <div class="note">oracle knows true competence</div>
    </div>
    <div class="kpi">
      <div class="label">Cost per success</div>
      <div class="value">{cost}</div>
      <div class="note">vs {cost_random} random</div>
    </div>
  </div>

  <div class="card">
    <h2>Rolling accuracy over the task stream</h2>
    <p class="cap">The two are indistinguishable for roughly the first 30 tasks
       &mdash; Horizon has no history to route on yet. A sustained gap opens by task
       ~64 and holds for the rest of the run.</p>
    <div class="legend">
      <span><i class="key" style="background:var(--series-1)"></i>Horizon</span>
      <span><i class="key" style="background:var(--series-2)"></i>Capability-only</span>
      <span><i class="key" style="background:var(--muted)"></i>Random</span>
      <span><i class="key dash"></i>Oracle ceiling</span>
    </div>
    <div id="plot" style="position:relative">
      <svg viewBox="0 0 {W} {H}" role="img"
           aria-label="Rolling routing accuracy by strategy over the task stream.">
        {grid}{xaxis}{marks}
        <line id="cross" class="crosshair" y1="{PAD_T}" y2="{PH_END}"/>
        <g id="hoverdots"></g>
        <rect id="hit" x="{PAD_L}" y="{PAD_T}" width="{PW}" height="{PH}" fill="transparent"/>
      </svg>
      <div class="tip" id="tip"></div>
    </div>
  </div>

  <div class="card">
    <h2>Which agent each strategy chose</h2>
    <p class="cap">The mechanism behind the gap. Capability-only never selects
       <b>alpha</b> or <b>gamma</b> even once &mdash; the generalist <b>omni</b>
       over-claims every family and wins on declared capability, so the two real
       specialists are never discovered. Horizon tries them, sees the outcomes,
       and converges on all four. ★ marks the genuinely best agent for a family.</p>
    <div class="legend">
      <span><i class="key" style="background:var(--series-1)"></i>Horizon</span>
      <span><i class="key" style="background:var(--series-2)"></i>Capability-only</span>
    </div>
    <svg viewBox="0 0 500 192" style="max-width:620px" role="img"
         aria-label="Share of tasks routed to each agent, by strategy.">
      <line class="axis" x1="24" y1="160" x2="486" y2="160"/>
      {bars}
    </svg>
  </div>

  <div class="card">
    <h2>Table view</h2>
    <table>
      <thead><tr><th scope="col" style="text-align:left">Strategy</th>
        <th scope="col">Overall</th><th scope="col">Final {tail}</th>
        <th scope="col">$/success</th><th scope="col">Total cost</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
    <table style="margin-top:22px">
      <thead><tr><th scope="col" style="text-align:left">Task family (final quarter)</th>
        <th scope="col">Oracle</th><th scope="col">Horizon</th>
        <th scope="col">Capability</th><th scope="col">Random</th></tr></thead>
      <tbody>{fam_rows}</tbody>
    </table>
    <p class="foot">
      Synthetic workload with offline deterministic embeddings, run against a live
      PostgreSQL with pgvector. Agent competence is ground truth the router cannot
      see; agents over-claim in their declared capabilities, as real registries do.
      Reproduce with <code>python -m benchmarks.run --tasks {tasks} --seed {seed}</code>.
    </p>
  </div>

</div></div>
<script type="module">
const D = {series_js};
const COLORS = {{
  oracle: 'var(--muted)', horizon: 'var(--series-1)',
  capability: 'var(--series-2)', random: 'var(--muted)'
}};
const svg = document.querySelector('#plot svg');
const hit = document.getElementById('hit');
const cross = document.getElementById('cross');
const tip = document.getElementById('tip');
const dots = document.getElementById('hoverdots');

for (const s of D.series) {{
  const c = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
  c.setAttribute('r', 4.5);
  c.setAttribute('class', 'hover-dot');
  c.setAttribute('fill', COLORS[s.key]);
  c.dataset.key = s.key;
  dots.appendChild(c);
}}

const xOf = i => D.padL + D.pw * i / Math.max(1, D.n - 1);
const yOf = v => D.padT + D.ph * (1 - v);

function move(ev) {{
  const r = svg.getBoundingClientRect();
  const scale = D.pw ? (r.width / svg.viewBox.baseVal.width) : 1;
  const px = (ev.clientX - r.left) / scale;
  let i = Math.round((px - D.padL) / D.pw * (D.n - 1));
  i = Math.max(0, Math.min(D.n - 1, i));

  cross.setAttribute('x1', xOf(i)); cross.setAttribute('x2', xOf(i));
  cross.style.opacity = 1;

  let rows = '';
  for (const c of dots.children) {{
    const s = D.series.find(s => s.key === c.dataset.key);
    c.setAttribute('cx', xOf(i)); c.setAttribute('cy', yOf(s.values[i]));
    c.style.opacity = 1;
    rows += `<div class="r"><i class="dot" style="background:${{COLORS[s.key]}}"></i>`
          + `${{s.label}}<b>${{(s.values[i]*100).toFixed(0)}}%</b></div>`;
  }}
  tip.innerHTML = `<div class="h">After ${{(i + D.offset).toLocaleString()}} tasks</div>${{rows}}`;
  tip.style.opacity = 1;
  const left = Math.min(ev.clientX - r.left + 16, r.width - tip.offsetWidth - 8);
  tip.style.left = Math.max(0, left) + 'px';
  tip.style.top = Math.max(0, ev.clientY - r.top - tip.offsetHeight / 2) + 'px';
}}

function leave() {{
  cross.style.opacity = 0; tip.style.opacity = 0;
  for (const c of dots.children) c.style.opacity = 0;
}}

hit.addEventListener('mousemove', move);
hit.addEventListener('mouseleave', leave);
</script>
</body>
</html>
"""


def main() -> None:
    if not RESULTS.exists():
        raise SystemExit("no results — run: python -m benchmarks.run")
    data = json.loads(RESULTS.read_text())

    from benchmarks.world import AGENTS, FAMILIES

    data["best_agent_for"] = {
        max(AGENTS, key=lambda a: a.competence[f.name]).name: f.name for f in FAMILIES
    }

    html = (
        build(data)
        .replace("{PAD_T}", str(PAD_T))
        .replace("{PH_END}", str(PAD_T + PH))
        .replace("{PAD_L}", str(PAD_L))
        .replace("{PW}", str(PW))
        .replace("{PH}", str(PH))
    )
    OUTPUT.write_text(html)
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
