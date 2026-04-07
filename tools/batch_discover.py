#!/usr/bin/env python3
"""
Batch discover: run spell discovery for every registered spec and save
structured results to discover_results.json.

Usage:
    python tools/batch_discover.py [--encounter 3176] [--count 5]
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from wcl.client import WCLClient
from wcl.fetcher import fetch_top_parses, _extract_player
from wcl.queries import PLAYER_DETAILS_QUERY
from wcl.specs import list_specs, get_spec_by_display

console = Console()

TABLE_QUERY = """
query DiscoverCasts($code: String!, $fightID: Int!, $sourceID: Int!, $start: Float!, $end: Float!) {
  reportData {
    report(code: $code) {
      table(
        fightIDs: [$fightID]
        dataType: Casts
        sourceID: $sourceID
        startTime: $start
        endTime: $end
      )
    }
  }
}
"""


def discover_one(client: WCLClient, spec: dict, encounter_id: int, count: int) -> dict | None:
    """Return top-60 cast spells with tracking status, or None if no parses."""
    parses = []
    for difficulty in (5, 4, 3):  # mythic → heroic → normal
        try:
            parses = fetch_top_parses(
                client,
                encounter_id=encounter_id,
                class_name=spec["wcl_class"],
                spec_name=spec["wcl_spec"],
                metric=spec.get("metric", "dps"),
                count=count,
                difficulty=difficulty,
            )
        except Exception:
            parses = []
        if parses:
            break

    if not parses:
        return None

    tracked: set[int] = (
        set(spec.get("cooldowns", {}).keys())
        | set(spec.get("raid_cooldowns", {}).keys())
    )
    counts: Counter = Counter()
    names:  dict[int, str] = {}

    for meta in parses:
        try:
            pd_data = client.query(PLAYER_DETAILS_QUERY, {
                "reportCode": meta.report_code,
                "fightID":    meta.fight_id,
            })
            report = pd_data["data"]["reportData"]["report"]
            fight  = report["fights"][0]

            player_id, _ = _extract_player(report["playerDetails"], meta.character_name)
            if not player_id:
                continue

            for a in report.get("masterData", {}).get("abilities", []):
                if a.get("gameID") and a.get("name"):
                    names[a["gameID"]] = a["name"]

            result = client.query(TABLE_QUERY, {
                "code":      meta.report_code,
                "fightID":   meta.fight_id,
                "sourceID":  player_id,
                "start":     float(fight["startTime"]),
                "end":       float(fight["endTime"]),
            })
            table_data = result["data"]["reportData"]["report"]["table"]
            if isinstance(table_data, dict):
                for entry in table_data.get("data", {}).get("entries", []):
                    sid   = entry.get("id") or entry.get("guid")
                    name  = entry.get("name", "")
                    total = entry.get("total", 1)
                    if sid:
                        counts[sid] += total
                        if name:
                            names[sid] = name
        except Exception as e:
            console.print(f"    [yellow]parse error: {e}[/yellow]")
            continue

    if not counts:
        return None

    n = max(len(parses), 1)
    return {
        str(sid): {
            "name":    names.get(sid, "?"),
            "total":   total,
            "avg":     round(total / n, 1),
            "tracked": sid in tracked,
        }
        for sid, total in counts.most_common(60)
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--encounter", type=int, default=3176)
    ap.add_argument("--count",     type=int, default=5)
    args = ap.parse_args()

    client = WCLClient()
    specs  = list_specs()
    results: dict[str, dict | None] = {}
    out_path = Path(__file__).parent / "discover_results.json"

    for spec_name in specs:
        spec = get_spec_by_display(spec_name)
        console.print(f"[cyan]→ {spec_name}[/cyan]", end=" ")
        data = discover_one(client, spec, args.encounter, args.count)
        if data is None:
            console.print("[yellow]no parses[/yellow]")
            results[spec_name] = None
        else:
            untracked = [
                (sid, v) for sid, v in data.items()
                if not v["tracked"] and v["avg"] <= 25
            ]
            console.print(
                f"[green]{len(data)} spells[/green]  "
                f"[{'red' if untracked else 'dim'}]{len(untracked)} untracked ≤25 avg[/{'red' if untracked else 'dim'}]"
            )
            results[spec_name] = data

        # Save after every spec so partial results survive a crash
        out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    console.print(f"\n[bold green]Done → {out_path}[/bold green]")


if __name__ == "__main__":
    main()
