"""
Batch runner: all specs × first N bosses × mythic, top K parses.
Skips runs where the output HTML already exists.
Run from the wcl-analyzer/ directory.
"""

import subprocess
import sys
import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from wcl.client import WCLClient
from wcl.queries import ENCOUNTER_LIST_QUERY
from wcl.specs.registry import _REGISTRY

# ── config ────────────────────────────────────────────────────────────────────
BOSS_COUNT  = 3      # first N bosses in the raid
PARSE_COUNT = 50
DIFFICULTY  = 5      # mythic
OUTPUT_DIR  = "docs"
# ─────────────────────────────────────────────────────────────────────────────


def _slugify(s: str) -> str:
    import re
    s = s.lower().strip()
    s = re.sub(r"[''']", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def fetch_encounters(client: WCLClient, n: int) -> list[dict]:
    """Return first n raid encounters from the Midnight expansion."""
    data = client.query(ENCOUNTER_LIST_QUERY)
    encounters = []
    for exp in data["data"]["worldData"]["expansions"]:
        if "midnight" not in exp["name"].lower():
            continue
        for zone in exp.get("zones", []):
            zname = zone["name"].lower()
            if any(w in zname for w in ("beta", "ptr", "test", "complete", "mythic+")):
                continue
            diffs = [d for d in zone.get("difficulties", []) if d["name"].lower() in ("normal", "heroic", "mythic")]
            if not diffs:
                continue
            for enc in zone.get("encounters", [])[:n]:
                encounters.append({"id": enc["id"], "name": enc["name"]})
    return encounters[:n]


def already_done(spec_key: str, spec: dict, enc_name: str, output_dir: str) -> bool:
    slug = f"{_slugify(spec['spec_name'])}-{_slugify(spec['class_name'])}-{_slugify(enc_name)}-mythic"
    path = Path(output_dir) / f"{slug}.html"
    return path.exists()


def run_one(spec_key: str, enc_id: int, enc_name: str) -> bool:
    cmd = [
        sys.executable, "main.py",
        "--spec",           spec_key,
        "--encounter",      str(enc_id),
        "--encounter-name", enc_name,
        "--difficulty",     str(DIFFICULTY),
        "--count",          str(PARSE_COUNT),
        "--output-dir",     OUTPUT_DIR,
    ]
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def main():
    client = WCLClient()
    print(f"Fetching first {BOSS_COUNT} Midnight encounters…")
    encounters = fetch_encounters(client, BOSS_COUNT)
    if not encounters:
        print("ERROR: No encounters found. Check expansion name filter.")
        sys.exit(1)

    for enc in encounters:
        print(f"  {enc['id']:>6}  {enc['name']}")

    spec_keys = list(_REGISTRY.keys())
    total = len(spec_keys) * len(encounters)
    done = 0
    skipped = 0
    failed = []

    print(f"\nRunning {len(spec_keys)} specs × {len(encounters)} bosses = {total} charts\n")

    for enc in encounters:
        for key in spec_keys:
            spec = _REGISTRY[key]
            label = f"{spec['spec_name']} {spec['class_name']} — {enc['name']}"
            done += 1

            if already_done(key, spec, enc["name"], OUTPUT_DIR):
                print(f"[{done}/{total}] SKIP  {label}")
                skipped += 1
                continue

            print(f"[{done}/{total}] RUN   {label}")
            ok = run_one(key, enc["id"], enc["name"])
            if not ok:
                print(f"  !! FAILED: {label}")
                failed.append(label)
            time.sleep(3)  # small pause between runs to avoid rate limits

    print(f"\n{'='*60}")
    print(f"Done. Skipped (already existed): {skipped}")
    print(f"Failed: {len(failed)}")
    for f in failed:
        print(f"  - {f}")


if __name__ == "__main__":
    main()
