"""Manage the docs/ output directory: manifest.json and regenerated index.html."""
import json
from collections import defaultdict
from datetime import date
from pathlib import Path


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

    # Replace existing entry for the same output file (re-run)
    manifest = [e for e in manifest if e.get("file") != entry["file"]]
    manifest.append(entry)
    manifest.sort(key=lambda e: (e.get("spec", ""), e.get("encounter", "")))

    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    _write_index(output_dir, manifest)


def _write_index(output_dir: Path, manifest: list[dict]) -> None:
    by_spec: dict[str, list[dict]] = defaultdict(list)
    for e in manifest:
        by_spec[e.get("spec", "Unknown")].append(e)

    sections: list[str] = []
    for spec in sorted(by_spec):
        entries = sorted(by_spec[spec], key=lambda x: x.get("encounter", ""))
        rows = []
        for e in entries:
            enc     = e.get("encounter", "Unknown")
            parses  = e.get("parse_count", "?")
            gen     = e.get("date", "")
            file    = e.get("file", "#")
            rows.append(
                f'<li><a href="{file}">{enc}</a>'
                f'<span class="meta">{parses} parses · {gen}</span></li>'
            )
        sections.append(
            f'<section class="spec-group">'
            f'<h2>{spec}</h2>'
            f'<ul>{"".join(rows)}</ul>'
            f'</section>'
        )

    content = "\n".join(sections) or (
        "<p class='empty'>No charts yet — run the analyzer to generate some.</p>"
    )

    today = date.today().strftime("%Y-%m-%d")
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>WCL Cooldown Analyzer</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#16213e;color:#e0e0e0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;padding:2.5rem 3rem;max-width:860px}}
h1{{font-size:1.5rem;color:#90caf9;margin-bottom:.2rem}}
.updated{{color:rgba(255,255,255,.35);font-size:.8rem;margin-bottom:2.5rem}}
.spec-group{{margin-bottom:2rem}}
h2{{font-size:1rem;color:#ce93d8;border-bottom:1px solid rgba(255,255,255,.1);padding-bottom:.4rem;margin-bottom:.7rem;text-transform:uppercase;letter-spacing:.05em}}
ul{{list-style:none}}
li{{display:flex;align-items:baseline;justify-content:space-between;padding:.38rem 0;border-bottom:1px solid rgba(255,255,255,.04)}}
a{{color:#80cbc4;text-decoration:none;font-size:.92rem}}
a:hover{{color:#e0f2f1;text-decoration:underline}}
.meta{{color:rgba(255,255,255,.3);font-size:.78rem;margin-left:1rem;white-space:nowrap}}
.empty{{color:rgba(255,255,255,.4);font-style:italic;margin-top:1rem}}
</style>
</head>
<body>
<h1>WCL Cooldown Analyzer</h1>
<p class="updated">Last updated: {today}</p>
{content}
</body>
</html>"""

    (output_dir / "index.html").write_text(html, encoding="utf-8")
