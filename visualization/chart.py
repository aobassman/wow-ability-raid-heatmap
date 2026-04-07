"""
Timeline chart — 3-row heatmap layout.

  Row 1: Offensive cooldowns
  Row 2: Defensive & Raid cooldowns
  Row 3: Boss abilities
"""

import json
from datetime import date
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from analysis.timeline import HeatmapData, BossAbility


SCALES = {
    "Offensive": [[0.0, "#0d1b3e"], [0.35, "#1a5ca8"], [0.7, "#3aa0ff"], [0.9, "#c0e8ff"], [1.0, "#ffffff"]],
    "Defensive": [[0.0, "#2a0a0a"], [0.35, "#8a1a1a"], [0.7, "#e03030"], [0.9, "#ffd0b0"], [1.0, "#ffffff"]],
    "Boss":      [[0.0, "#1a0a2e"], [0.35, "#6a1a9a"], [0.7, "#c040e0"], [0.9, "#f0b0ff"], [1.0, "#ffffff"]],
}

CD_ROW_H   = 34
BOSS_ROW_H = 18
MIN_H      = 40
# Target total chart height. Chosen to fit comfortably in a 1080p browser
# window (accounting for browser chrome ~130px). Responsive mode then scales
# the figure up on taller displays.
MAX_CHART_H = 900
HEADER_H    = 180  # title + margins + x-axis


def _fmt_time(t_sec: float) -> str:
    """Format seconds; for values ≥ 60 also show as Xm Ys."""
    t = int(t_sec)
    if t >= 60:
        m, s = divmod(t, 60)
        return f"{t} ({m}m {s}s)"
    return str(t)


def build_chart(
    offensive: HeatmapData,
    defensive: HeatmapData,
    boss_heatmap: HeatmapData,
    boss_abilities: list[BossAbility],
    encounter_name: str,
    spec_name: str,
    fight_duration_sec: float,
    parse_count: int,
    output_path: Path,
    spell_id_map: dict[str, int] | None = None,
    ability_icons: dict[int, str] | None = None,
) -> None:
    n_off  = max(1, len(offensive.ability_names))
    n_def  = max(1, len(defensive.ability_names))
    n_boss = max(1, len(boss_heatmap.ability_names))

    nat_off  = max(MIN_H, n_off  * CD_ROW_H)
    nat_def  = max(MIN_H, n_def  * CD_ROW_H)
    nat_boss = max(MIN_H, n_boss * BOSS_ROW_H)
    nat_content = nat_off + nat_def + nat_boss

    # Scale down proportionally if content exceeds the 1080p target
    avail = MAX_CHART_H - HEADER_H
    if nat_content > avail:
        scale = avail / nat_content
        h_off  = max(MIN_H, int(nat_off  * scale))
        h_def  = max(MIN_H, int(nat_def  * scale))
        h_boss = max(MIN_H, int(nat_boss * scale))
    else:
        h_off, h_def, h_boss = nat_off, nat_def, nat_boss

    total_h = h_off + h_def + h_boss + HEADER_H

    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        subplot_titles=["Offensive Cooldowns", "Defensive & Raid Cooldowns", "Boss Abilities"],
        vertical_spacing=0.03,
        row_heights=[h_off, h_def, h_boss],
    )

    # --- Heatmap traces ---
    _add_heatmap(fig, offensive,    "Offensive", row=1, parse_count=parse_count)
    _add_heatmap(fig, defensive,    "Defensive", row=2, parse_count=parse_count)
    _add_heatmap(fig, boss_heatmap, "Boss",      row=3, parse_count=parse_count)

    # --- X-axis ticks with min+sec labels ---
    tick_vals  = list(range(0, int(fight_duration_sec) + 1, 30))
    tick_texts = [_fmt_time(t) for t in tick_vals]

    for row in (1, 2, 3):
        fig.update_xaxes(
            range=[0, fight_duration_sec],
            tickvals=tick_vals,
            ticktext=tick_texts,
            showgrid=True, gridcolor="rgba(255,255,255,0.06)",
            tickcolor="rgba(255,255,255,0.4)",
            tickfont=dict(size=9),
            row=row, col=1,
        )
        fig.update_yaxes(
            tickfont=dict(size=8 if row == 3 else 11),
            gridcolor="rgba(255,255,255,0.04)",
            row=row, col=1,
        )
    fig.update_xaxes(title_text="Fight time", row=3, col=1)

    # --- Layout ---
    fig.update_layout(
        title=dict(
            text=(
                f"{spec_name} — {encounter_name}<br>"
                f"<sup>Top {parse_count} parses · colour intensity = % of parses using ability"
                f" · Generated {date.today().strftime('%Y-%m-%d')}</sup>"
            ),
            font=dict(size=15, color="white"),
        ),
        plot_bgcolor="#1a1a2e",
        paper_bgcolor="#16213e",
        font=dict(color="white"),
        height=total_h,
        showlegend=False,
        margin=dict(l=190, r=60, t=130, b=60),
        hoverlabel=dict(bgcolor="#16213e", font_color="white"),
        hovermode="closest",
    )

    for ann in fig.layout.annotations:
        if ann.text in ("Offensive Cooldowns", "Defensive & Raid Cooldowns", "Boss Abilities"):
            ann.font = dict(color="rgba(255,255,255,0.6)", size=11)

    fig.write_html(
        str(output_path),
        include_plotlyjs="cdn",
        config={"responsive": True},
    )

    _inject_js(output_path, spell_id_map or {})

    uri = output_path.resolve().as_uri()
    print(f"Chart saved → \033]8;;{uri}\033\\{output_path}\033]8;;\033\\")


def _inject_js(output_path: Path, spell_id_map: dict[str, int]) -> None:
    """
    Post-process the HTML to inject:
    1. Wowhead tooltip overlays on y-axis spell labels (on label hover)
    2. Wowhead spell tooltip triggered by heatmap cell hover
    3. Full-height vertical + horizontal crosshair following the mouse
    4. Back-to-index link
    """
    spell_json = json.dumps(spell_id_map)
    overlay_js = f"""
<script>
var whTooltips = {{colorLinks: false, iconizeLinks: false, renameLinks: false}};
(function() {{
  var spellIds = {spell_json};

  // --- Back-to-index link ---
  var backLink = document.createElement('a');
  backLink.href = './index.html';
  backLink.innerHTML = '&#8592; All fights';
  backLink.style.cssText = [
    'position:fixed','top:12px','right:16px',
    'color:#90caf9','font-size:12px','font-family:sans-serif',
    'background:rgba(22,33,62,0.88)','border:1px solid rgba(144,202,249,0.3)',
    'padding:4px 10px','border-radius:5px','z-index:300',
    'text-decoration:none','letter-spacing:0.02em'
  ].join(';');
  backLink.addEventListener('mouseover',function(){{backLink.style.color='#e3f2fd';}});
  backLink.addEventListener('mouseout', function(){{backLink.style.color='#90caf9';}});
  document.body.appendChild(backLink);

  // --- Y-axis label overlays (invisible Wowhead link on each label) ---
  function makeLabelOverlay(rect, spellId, sT, sL) {{
    var a = document.createElement('a');
    a.className = 'wh-spell-overlay';
    a.href = 'https://www.wowhead.com/spell=' + spellId;
    a.setAttribute('data-wowhead', 'spell=' + spellId);
    a.style.cssText = [
      'position:absolute',
      'left:'   + (rect.left + sL - 4) + 'px',
      'top:'    + (rect.top  + sT - 2) + 'px',
      'width:'  + (Math.max(rect.width,  10) + 8) + 'px',
      'height:' + (Math.max(rect.height, 14) + 4) + 'px',
      'opacity:0', 'z-index:9999', 'display:block', 'cursor:help'
    ].join(';');
    document.body.appendChild(a);
  }}

  function buildLabelOverlays() {{
    document.querySelectorAll('.wh-spell-overlay').forEach(function(el) {{ el.remove(); }});
    var sT = window.pageYOffset  || document.documentElement.scrollTop;
    var sL = window.pageXOffset || document.documentElement.scrollLeft;
    ['ytick','y2tick','y3tick','y4tick'].forEach(function(cls) {{
      document.querySelectorAll('g.' + cls + ' text').forEach(function(textEl) {{
        var id = spellIds[textEl.textContent.trim()];
        if (id) makeLabelOverlay(textEl.getBoundingClientRect(), id, sT, sL);
      }});
    }});
    if (!document.getElementById('wh-tooltips-script')) {{
      var s = document.createElement('script');
      s.id  = 'wh-tooltips-script';
      s.src = 'https://wow.zamimg.com/js/tooltips.js';
      s.onload = function() {{ if (window.WH && WH.Tooltips) WH.Tooltips.init(); }};
      document.head.appendChild(s);
    }} else if (window.WH && window.WH.Tooltips) {{
      WH.Tooltips.init();
    }}
  }}

  setTimeout(buildLabelOverlays, 900);
  window.addEventListener('resize', function() {{ setTimeout(buildLabelOverlays, 300); }});

  // --- Heatmap hover: crosshair + Wowhead spell tooltip ---
  function initHoverFeatures() {{
    var gd = document.querySelector('.plotly-graph-div');
    if (!gd) {{ setTimeout(initHoverFeatures, 200); return; }}

    var mainSvg = gd.querySelector('.main-svg');

    // Vertical crosshair — green, persistent
    var crosshairV = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    crosshairV.setAttribute('stroke', '#00e676');
    crosshairV.setAttribute('stroke-width', '1.5');
    crosshairV.style.display = 'none';
    crosshairV.style.pointerEvents = 'none';
    mainSvg.appendChild(crosshairV);

    // Horizontal crosshair — very faint white
    var crosshairH = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    crosshairH.setAttribute('stroke', 'rgba(255,255,255,0.18)');
    crosshairH.setAttribute('stroke-width', '1');
    crosshairH.style.display = 'none';
    crosshairH.style.pointerEvents = 'none';
    mainSvg.appendChild(crosshairH);

    gd.addEventListener('mousemove', function(e) {{
      var svgRect = mainSvg.getBoundingClientRect();
      var svgX = e.clientX - svgRect.left;
      var svgY = e.clientY - svgRect.top;
      var fl   = gd._fullLayout;
      var svgW = parseFloat(mainSvg.getAttribute('width')  || gd.offsetWidth);
      var svgH = parseFloat(mainSvg.getAttribute('height') || gd.offsetHeight);
      var pL = fl.margin.l, pR = svgW - fl.margin.r;
      var pT = fl.margin.t, pB = svgH - fl.margin.b;
      var inside = svgX >= pL && svgX <= pR && svgY >= pT && svgY <= pB;

      if (svgX >= pL && svgX <= pR) {{
        crosshairV.setAttribute('x1', svgX); crosshairV.setAttribute('x2', svgX);
        crosshairV.setAttribute('y1', pT);   crosshairV.setAttribute('y2', pB);
        crosshairV.style.display = 'block';
      }} else {{
        crosshairV.style.display = 'none';
      }}

      if (inside) {{
        crosshairH.setAttribute('x1', pL); crosshairH.setAttribute('x2', pR);
        crosshairH.setAttribute('y1', svgY); crosshairH.setAttribute('y2', svgY);
        crosshairH.style.display = 'block';
      }} else {{
        crosshairH.style.display = 'none';
      }}
    }});

    gd.addEventListener('mouseleave', function() {{
      crosshairV.style.display = 'none';
      crosshairH.style.display = 'none';
    }});

    // Wowhead tooltip — pinned to bottom of viewport so it never overlaps
    // the Plotly data tooltip. Hold Alt to suppress it temporarily.
    var whAnchor = document.createElement('a');
    whAnchor.style.cssText = [
      'position:fixed', 'display:inline-block',
      'width:2px', 'height:2px', 'opacity:0.01',
      'z-index:1', 'pointer-events:none'
    ].join(';');
    document.body.appendChild(whAnchor);

    // Hotkey hint — prominent banner near the top of the page
    var hintEl = document.createElement('div');
    hintEl.innerHTML = '&#9432; Hold <b>Shift</b> to hide spell tooltips';
    hintEl.style.cssText = [
      'position:fixed', 'top:10px', 'left:50%',
      'transform:translateX(-50%)',
      'color:#ffe082', 'font-size:13px',
      'font-family:sans-serif', 'z-index:200',
      'background:rgba(30,20,60,0.92)',
      'border:1px solid rgba(255,200,80,0.4)',
      'padding:6px 18px', 'border-radius:6px',
      'pointer-events:none', 'letter-spacing:0.02em'
    ].join(';');
    document.body.appendChild(hintEl);

    var lastSpellId  = null;
    var lastCx       = 0;
    var whSuppressed = false;

    function showWhTooltip(spellId, cx) {{
      var pinY = window.innerHeight - 40;
      whAnchor.href = 'https://www.wowhead.com/spell=' + spellId;
      whAnchor.setAttribute('data-wowhead', 'spell=' + spellId);
      whAnchor.style.left = cx + 'px';
      whAnchor.style.top  = pinY + 'px';
      whAnchor.dispatchEvent(new MouseEvent('mouseover', {{bubbles: true, clientX: cx, clientY: pinY}}));
    }}

    document.addEventListener('keydown', function(e) {{
      if (e.key === 'Shift') {{
        if (!whSuppressed) {{
          whSuppressed = true;
          whAnchor.dispatchEvent(new MouseEvent('mouseout', {{bubbles: true}}));
          Plotly.relayout(gd, {{'hovermode': false}});
        }}
      }}
    }});

    document.addEventListener('keyup', function(e) {{
      if (e.key === 'Shift') {{
        whSuppressed = false;
        Plotly.relayout(gd, {{'hovermode': 'closest'}});
        if (lastSpellId) showWhTooltip(lastSpellId, lastCx);
      }}
    }});

    gd.on('plotly_hover', function(data) {{
      var pt = data.points[0];
      if (!pt) return;
      var spellId = spellIds[pt.y] || null;
      var ev = data.event;
      lastCx = ev.clientX;

      if (spellId === lastSpellId) return;
      lastSpellId = spellId;

      whAnchor.dispatchEvent(new MouseEvent('mouseout', {{bubbles: true}}));
      if (!spellId || whSuppressed) return;
      showWhTooltip(spellId, lastCx);
    }});

    gd.on('plotly_unhover', function() {{
      lastSpellId = null;
      whAnchor.dispatchEvent(new MouseEvent('mouseout', {{bubbles: true}}));
    }});
  }}

  setTimeout(initHoverFeatures, 1000);
}})();
</script>
"""
    html = output_path.read_text(encoding="utf-8")
    if not html.lstrip().startswith("<!DOCTYPE"):
        html = "<!DOCTYPE html>\n" + html
    html = html.replace("</body>", overlay_js + "</body>")
    output_path.write_text(html, encoding="utf-8")


def _add_heatmap(
    fig: go.Figure,
    data: HeatmapData,
    scale_key: str,
    row: int,
    parse_count: int,
) -> None:
    if not data.ability_names:
        fig.add_trace(go.Scatter(x=[], y=[], showlegend=False), row=row, col=1)
        return

    from scipy.ndimage import maximum_filter1d

    z_raw = np.clip(data.matrix, 0, None)
    # Local-max normalization over a ±10 s window so each cast peak hits 1.0
    local_max = maximum_filter1d(z_raw, size=20, axis=1)
    local_max[local_max == 0] = 1.0
    z = (z_raw / local_max) ** 2.0

    hover = [
        [
            f"<b>{name}</b><br>Time: {_fmt_time(t)}<br>~{z_raw[i,j]:.1f}% of parses<br>"
            f"<i>{data.parse_counts[i]}/{parse_count} parses</i>"
            for j, t in enumerate(data.time_points)
        ]
        for i, name in enumerate(data.ability_names)
    ]

    fig.add_trace(
        go.Heatmap(
            x=data.time_points.tolist(),
            y=data.ability_names,
            z=z.tolist(),
            colorscale=SCALES[scale_key],
            zmin=0.0,
            zmax=1.0,
            showscale=False,
            hovertemplate="%{customdata}<extra></extra>",
            customdata=hover,
            ygap=3,
        ),
        row=row, col=1,
    )
