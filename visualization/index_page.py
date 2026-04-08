"""Manage the docs/ output directory: manifest.json and regenerated index.html."""
import json
from datetime import date
from pathlib import Path

_KNOWN_CLASSES = [
    "Death Knight", "Demon Hunter", "Druid", "Evoker",
    "Hunter", "Mage", "Monk", "Paladin", "Priest",
    "Rogue", "Shaman", "Warlock", "Warrior",
]


def _extract_class(entry: dict) -> tuple[str, str]:
    """Return (spec_name, class_name) from a manifest entry."""
    if "class" in entry:
        cls = entry["class"]
        spec = entry["spec"].replace(cls, "").strip() if entry["spec"].endswith(cls) else entry["spec"]
        return spec, cls
    # Fallback: parse from "Spec ClassName" display string
    display = entry.get("spec", "")
    for cls in _KNOWN_CLASSES:
        if display.endswith(cls):
            return display[: -len(cls)].strip(), cls
    parts = display.rsplit(" ", 1)
    return (parts[0], parts[1]) if len(parts) == 2 else (display, "Unknown")


def update_docs(output_dir: Path, entry: dict) -> None:
    """Add/update entry in manifest.json and regenerate index.html."""
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "manifest.json"

    manifest: list[dict] = []
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    manifest = [e for e in manifest if e.get("file") != entry["file"]]
    manifest.append(entry)
    manifest.sort(key=lambda e: (e.get("class", ""), e.get("spec", ""), e.get("encounter", "")))

    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    _write_index(output_dir, manifest)


def _write_index(output_dir: Path, manifest: list[dict]) -> None:
    # Build nested: class_name -> spec_name -> [entries]
    tree: dict[str, dict[str, list[dict]]] = {}
    for e in manifest:
        spec_name, class_name = _extract_class(e)
        tree.setdefault(class_name, {}).setdefault(spec_name, []).append(e)

    # Sort everything
    sorted_tree = {
        cls: {
            sp: sorted(entries, key=lambda x: x.get("encounter", ""))
            for sp, entries in sorted(specs.items())
        }
        for cls, specs in sorted(tree.items())
    }

    # Flatten to JS-friendly structure
    js_data: dict[str, dict[str, list[dict]]] = {}
    for cls, specs in sorted_tree.items():
        js_data[cls] = {}
        for sp, entries in specs.items():
            js_data[cls][sp] = [
                {
                    "enc":    e.get("encounter", "Unknown"),
                    "file":   e.get("file", "#"),
                    "parses": e.get("parse_count", "?"),
                    "date":   e.get("date", ""),
                }
                for e in entries
            ]

    today = date.today().strftime("%Y-%m-%d")
    data_json = json.dumps(js_data, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>WCL Cooldown Analyzer</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#16213e;color:#e0e0e0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
     display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;padding:2rem}}
h1{{font-size:1.6rem;color:#90caf9;margin-bottom:.25rem;letter-spacing:.02em}}
.subtitle{{color:rgba(255,255,255,.3);font-size:.78rem;margin-bottom:2.5rem}}
.pickers{{display:flex;flex-direction:column;gap:.9rem;width:100%;max-width:400px}}
.row{{display:flex;flex-direction:column;gap:.3rem}}
label{{color:rgba(255,255,255,.45);font-size:.72rem;text-transform:uppercase;letter-spacing:.07em}}
select{{
  width:100%;padding:.6rem .85rem;border-radius:6px;
  background:#1a2744;color:#e0e0e0;
  border:1px solid rgba(144,202,249,0.25);
  font-size:.92rem;appearance:none;cursor:pointer;
  outline:none;transition:border-color .15s;
}}
select:focus{{border-color:#90caf9}}
select:disabled{{opacity:.35;cursor:default}}
.go-row{{margin-top:.4rem}}
button{{
  width:100%;padding:.65rem;border-radius:6px;
  background:#1565c0;color:#fff;border:none;
  font-size:.95rem;font-weight:600;cursor:pointer;
  letter-spacing:.03em;transition:background .15s;
}}
button:hover:not(:disabled){{background:#1976d2}}
button:disabled{{opacity:.3;cursor:default}}
.meta-line{{color:rgba(255,255,255,.25);font-size:.75rem;margin-top:.3rem;min-height:1em;text-align:right}}
</style>
</head>
<body>
<h1>WCL Cooldown Analyzer</h1>
<p class="subtitle">Last updated: {today}</p>
<div class="pickers">
  <div class="row">
    <label for="sel-class">Class</label>
    <select id="sel-class"><option value="">— Select class —</option></select>
  </div>
  <div class="row">
    <label for="sel-spec">Spec</label>
    <select id="sel-spec" disabled><option value="">— Select spec —</option></select>
  </div>
  <div class="row">
    <label for="sel-boss">Boss</label>
    <select id="sel-boss" disabled><option value="">— Select boss —</option></select>
  </div>
  <div class="go-row">
    <button id="go-btn" disabled>View chart →</button>
    <div class="meta-line" id="meta-line"></div>
  </div>
</div>
<script>
var DATA = {data_json};

var selClass = document.getElementById('sel-class');
var selSpec  = document.getElementById('sel-spec');
var selBoss  = document.getElementById('sel-boss');
var goBtn    = document.getElementById('go-btn');
var metaLine = document.getElementById('meta-line');

// Populate class dropdown
Object.keys(DATA).sort().forEach(function(cls) {{
  var o = document.createElement('option');
  o.value = cls; o.textContent = cls;
  selClass.appendChild(o);
}});

function reset(sel, placeholder) {{
  sel.innerHTML = '<option value="">' + placeholder + '</option>';
  sel.disabled = true;
}}

selClass.addEventListener('change', function() {{
  reset(selSpec, '— Select spec —');
  reset(selBoss, '— Select boss —');
  goBtn.disabled = true;
  metaLine.textContent = '';
  var cls = this.value;
  if (!cls) return;
  var specs = DATA[cls];
  Object.keys(specs).sort().forEach(function(sp) {{
    var o = document.createElement('option');
    o.value = sp; o.textContent = sp;
    selSpec.appendChild(o);
  }});
  selSpec.disabled = false;
  if (selSpec.options.length === 2) {{ selSpec.selectedIndex = 1; selSpec.dispatchEvent(new Event('change')); }}
}});

selSpec.addEventListener('change', function() {{
  reset(selBoss, '— Select boss —');
  goBtn.disabled = true;
  metaLine.textContent = '';
  var cls = selClass.value, sp = this.value;
  if (!cls || !sp) return;
  var entries = DATA[cls][sp];
  entries.forEach(function(e) {{
    var o = document.createElement('option');
    o.value = e.file;
    o.textContent = e.enc;
    o.dataset.parses = e.parses;
    o.dataset.date   = e.date;
    selBoss.appendChild(o);
  }});
  selBoss.disabled = false;
  if (selBoss.options.length === 2) {{ selBoss.selectedIndex = 1; selBoss.dispatchEvent(new Event('change')); }}
}});

selBoss.addEventListener('change', function() {{
  var opt = this.options[this.selectedIndex];
  if (!this.value) {{ goBtn.disabled = true; metaLine.textContent = ''; return; }}
  goBtn.disabled = false;
  metaLine.textContent = opt.dataset.parses + ' parses · ' + opt.dataset.date;
}});

goBtn.addEventListener('click', function() {{
  if (selBoss.value) window.location.href = selBoss.value;
}});
</script>
</body>
</html>"""

    (output_dir / "index.html").write_text(html, encoding="utf-8")
