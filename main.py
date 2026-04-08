"""
WCL Analyzer — entry point.

Usage:
  python main.py                        # interactive prompts
  python main.py --spec windwalker --encounter 2901 --count 20
"""

import argparse
import re
import sys
import statistics
from pathlib import Path

import questionary
from rich.console import Console
from rich.progress import track
from rich.table import Table

from wcl.client import WCLClient
from wcl.fetcher import fetch_top_parses, fetch_all_fight_data
from wcl.specs import get_spec, get_spec_by_display, list_specs
from wcl.queries import ENCOUNTER_LIST_QUERY
from analysis.timeline import build_heatmap, build_boss_heatmap
from analysis.talents import aggregate_talents, find_most_common_loadout_string, format_talent_report
from visualization.chart import build_chart
from visualization.index_page import update_docs

console = Console()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="WCL Cooldown Analyzer")
    p.add_argument("--spec", help="Spec name (e.g. windwalker)")
    p.add_argument("--encounter", type=int, help="Encounter ID")
    p.add_argument("--difficulty", type=int, help="Difficulty ID (e.g. 4=Heroic, 5=Mythic)")
    p.add_argument("--encounter-name", dest="encounter_name", help="Human-readable encounter name (used in output filename and chart title)")
    p.add_argument("--count", type=int, default=10, help="Number of top parses, max 100 (default: 10)")
    p.add_argument("--metric", default="dps", help="Ranking metric (default: dps)")
    p.add_argument("--no-cache", action="store_true", help="Disable API response cache")
    p.add_argument("--output", help="Override output HTML path (default: auto-named in --output-dir)")
    p.add_argument("--output-dir", default="docs", help="Directory for generated HTML files (default: docs/)")
    p.add_argument("--discover", action="store_true", help="Print all player cast spell IDs ranked by frequency and exit")
    return p.parse_args()


def _slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def _auto_output(output_dir: Path, spec_name: str, encounter_name: str) -> Path:
    """Build a unique filename: {spec}-{encounter-with-difficulty}.html"""
    slug = f"{_slugify(spec_name)}-{_slugify(encounter_name)}"
    return output_dir / f"{slug}.html"



def _discover_spells(client: "WCLClient", parses: list, tracked_ids: set[int]) -> None:
    """
    Use WCL's table query (aggregated cast counts, single request per fight)
    instead of paginating through raw events — much faster and cacheable.
    """
    from collections import Counter
    from wcl.queries import PLAYER_DETAILS_QUERY
    from wcl.fetcher import _extract_player

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

    counts: Counter = Counter()
    names: dict[int, str] = {}

    for meta in track(parses, description="Discovering spells…"):
        pd_data = client.query(PLAYER_DETAILS_QUERY, {
            "reportCode": meta.report_code,
            "fightID": meta.fight_id,
        })
        report    = pd_data["data"]["reportData"]["report"]
        fight     = report["fights"][0]
        abs_start = fight["startTime"]
        abs_end   = fight["endTime"]

        player_id, _ = _extract_player(report["playerDetails"], meta.character_name)
        if not player_id:
            continue

        for a in report.get("masterData", {}).get("abilities", []):
            if a.get("gameID") and a.get("name"):
                names[a["gameID"]] = a["name"]

        result = client.query(TABLE_QUERY, {
            "code": meta.report_code,
            "fightID": meta.fight_id,
            "sourceID": player_id,
            "start": float(abs_start),
            "end": float(abs_end),
        })
        table_data = result["data"]["reportData"]["report"]["table"]
        if isinstance(table_data, dict):
            for entry in table_data.get("data", {}).get("entries", []):
                sid  = entry.get("id") or entry.get("guid")
                name = entry.get("name", "")
                total = entry.get("total", 1)
                if sid:
                    counts[sid] += total
                    if name:
                        names[sid] = name

    n = max(len(parses), 1)
    rich_table = Table(title=f"Player cast spells across {n} parses", show_lines=False)
    rich_table.add_column("",          width=2, no_wrap=True)   # tracked indicator
    rich_table.add_column("Spell ID",  style="cyan", no_wrap=True)
    rich_table.add_column("Name",      style="white")
    rich_table.add_column("Total casts", style="green", justify="right")
    rich_table.add_column("Avg/fight",   style="yellow", justify="right")

    for sid, total in counts.most_common(60):
        if sid in tracked_ids:
            marker = "[green]✓[/green]"
        else:
            marker = "[bold red]✗[/bold red]"
        rich_table.add_row(marker, str(sid), names.get(sid, "?"), str(total), f"{total/n:.1f}")

    console.print(rich_table)
    console.print("[dim]✓ = already tracked in spec   [bold red]✗[/bold red] = not tracked (consider adding)[/dim]")


def pick_spec_interactively() -> dict:
    choices = list_specs()  # sorted display names: "Retribution Paladin", etc.
    choice = questionary.select("Choose a specialization:", choices=choices).ask()
    if not choice:
        sys.exit(0)
    return get_spec_by_display(choice)


EXPANSION_FILTER = "midnight"


def pick_encounter_interactively(client: WCLClient) -> tuple[int, str]:
    console.log("Fetching encounter list…")
    data = client.query(ENCOUNTER_LIST_QUERY)
    expansions = data["data"]["worldData"]["expansions"]

    # Only include the Midnight expansion
    midnight_exps = [
        e for e in expansions
        if EXPANSION_FILTER in e["name"].lower()
    ]
    if not midnight_exps:
        available = [e["name"] for e in expansions]
        console.print(f"[red]No expansion matching '{EXPANSION_FILTER}' found.[/red]")
        console.print(f"Available: {available}")
        sys.exit(1)

    # Build flat list grouped by zone
    choices = []
    meta: dict[str, tuple[int, str]] = {}  # label -> (id, name)

    # enc_label -> (encounter_id, encounter_name, [(diff_id, diff_name), ...])
    enc_difficulties: dict[str, list[tuple[int, str]]] = {}

    for exp in midnight_exps:
        for zone in exp.get("zones", []):
            zname = zone["name"].lower()
            if any(word in zname for word in ("beta", "ptr", "test", "complete", "mythic+")):
                continue
            raid_diffs = [
                (d["id"], d["name"]) for d in zone.get("difficulties", [])
                if d["name"].lower() in ("normal", "heroic", "mythic")
            ]
            if not raid_diffs:
                continue
            for enc in zone.get("encounters", []):
                label = f"{zone['name']} — {enc['name']}"
                choices.append(label)
                meta[label] = (enc["id"], enc["name"])
                enc_difficulties[label] = raid_diffs

    if not choices:
        console.print("[red]No encounters found.[/red]")
        sys.exit(1)

    enc_choice = questionary.select("Choose a boss encounter:", choices=choices).ask()
    if not enc_choice:
        sys.exit(0)

    enc_id, enc_name = meta[enc_choice]
    diffs = enc_difficulties.get(enc_choice, [])

    diff_id = None
    if len(diffs) > 1:
        diff_labels = [name for _, name in diffs]
        diff_choice = questionary.select("Choose difficulty:", choices=diff_labels).ask()
        if not diff_choice:
            sys.exit(0)
        diff_id = next(did for did, dname in diffs if dname == diff_choice)
        enc_name = f"{enc_name} ({diff_choice})"
    elif diffs:
        diff_id, diff_label = diffs[0]
        enc_name = f"{enc_name} ({diff_label})"

    return enc_id, enc_name, diff_id


def print_parse_table(parses) -> None:
    table = Table(title="Top Parses", show_lines=False)
    table.add_column("#", style="dim", width=4)
    table.add_column("Character")
    table.add_column("Server")
    table.add_column("Percentile", justify="right")
    table.add_column("Duration", justify="right")
    for i, p in enumerate(parses, 1):
        mins = p.duration_ms // 60000
        secs = (p.duration_ms % 60000) // 1000
        table.add_row(
            str(i),
            p.character_name,
            p.server,
            f"{p.percentile:.1f}%" if p.percentile is not None else "--",
            f"{mins}:{secs:02d}",
        )
    console.print(table)


def main() -> None:
    args = parse_args()
    client = WCLClient(cache=not args.no_cache)

    # --- Spec selection ---
    if args.spec:
        spec = get_spec(args.spec)
    else:
        spec = pick_spec_interactively()

    # --- Encounter + difficulty selection ---
    if args.encounter:
        encounter_id = args.encounter
        difficulty = getattr(args, "difficulty", None)
        diff_label = {5: "Mythic", 4: "Heroic", 3: "Normal"}.get(difficulty, "")
        base_name = args.encounter_name or f"Encounter {encounter_id}"
        encounter_name = f"{base_name} ({diff_label})" if diff_label else base_name
    else:
        encounter_id, encounter_name, difficulty = pick_encounter_interactively(client)

    # --- Parse count ---
    if args.count != 10:
        # Explicitly passed on CLI — use it directly
        parse_count_arg = min(args.count, 100)
    elif args.spec and args.encounter:
        # Fully non-interactive invocation — keep default silently
        parse_count_arg = 10
    else:
        raw = questionary.text(
            "Number of top parses to analyse (max 100):",
            default="10",
            validate=lambda v: v.isdigit() and 1 <= int(v) <= 100 or "Enter a number between 1 and 100",
        ).ask()
        parse_count_arg = int(raw) if raw else 10

    console.rule(f"[bold]{spec['spec_name']} — {encounter_name}[/bold]")

    # --- Fetch top parses ---
    console.log(f"Fetching top {parse_count_arg} parses…")
    parses = fetch_top_parses(
        client,
        encounter_id=encounter_id,
        class_name=spec["wcl_class"],
        spec_name=spec["wcl_spec"],
        metric=args.metric,
        count=parse_count_arg,
        difficulty=difficulty,
    )

    if not parses:
        console.print("[red]No parses found for this encounter/spec combination.[/red]")
        sys.exit(1)

    print_parse_table(parses)

    # --- Fetch fight data ---
    cooldown_map: dict[int, str] = spec["cooldowns"]
    raid_cd_map: dict[int, str] = spec.get("raid_cooldowns", {})

    if args.discover:
        tracked = set(spec.get("cooldowns", {}).keys()) | set(spec.get("raid_cooldowns", {}).keys())
        _discover_spells(client, parses, tracked)
        sys.exit(0)

    fights = fetch_all_fight_data(
        client, parses,
        cooldown_spell_ids=list(cooldown_map.keys()),
        raid_cooldown_spell_ids=list(raid_cd_map.keys()),
    )

    if not fights:
        console.print("[red]No fight data retrieved.[/red]")
        sys.exit(1)

    # Median fight duration for x-axis
    durations = [f.meta.duration_ms / 1000.0 for f in fights]
    fight_duration = statistics.median(durations)

    # --- Aggregate ---
    off_map  = spec.get("cooldown_categories", {}).get("Offensive", cooldown_map)
    def_map  = {**spec.get("cooldown_categories", {}).get("Defensive", {}), **raid_cd_map}

    offensive_heatmap = build_heatmap(fights, off_map, fight_duration)
    defensive_heatmap = build_heatmap(fights, def_map, fight_duration,
                                       use_raid_events=False)
    # Raid CDs come from raid_events
    if raid_cd_map:
        raid_heatmap = build_heatmap(fights, raid_cd_map, fight_duration,
                                     use_raid_events=True)
        # Merge raid rows into defensive heatmap
        import numpy as np
        if raid_heatmap.ability_names:
            defensive_heatmap.ability_names += raid_heatmap.ability_names
            defensive_heatmap.parse_counts  += raid_heatmap.parse_counts
            if defensive_heatmap.matrix.size:
                defensive_heatmap.matrix = np.vstack(
                    [defensive_heatmap.matrix, raid_heatmap.matrix]
                )
            else:
                defensive_heatmap.matrix = raid_heatmap.matrix

    boss_heatmap, boss_abilities = build_boss_heatmap(fights, fight_duration, top_n=12)

    # Merge ability icons from all fights (covers both player and boss spells)
    merged_ability_icons: dict[int, str] = {}
    for fd in fights:
        merged_ability_icons.update(fd.ability_icons)

    # Build spell name → ID map for Wowhead y-axis tooltips
    spell_id_map: dict[str, int] = {
        name: sid for sid, name in spec.get("cooldowns", {}).items()
    }
    spell_id_map.update({
        name: sid for sid, name in spec.get("raid_cooldowns", {}).items()
    })
    for ab in boss_abilities:
        spell_id_map[ab.spell_name] = ab.spell_id

    # --- Chart ---
    output_dir = Path(args.output_dir)
    spec_label = f"{spec['spec_name']} {spec['class_name']}"
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = _auto_output(output_dir, spec_label, encounter_name)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    import traceback as _tb
    try:
        build_chart(
            offensive=offensive_heatmap,
            defensive=defensive_heatmap,
            boss_heatmap=boss_heatmap,
            boss_abilities=boss_abilities,
            encounter_name=encounter_name,
            spec_name=spec_label,
            fight_duration_sec=fight_duration,
            parse_count=len(fights),
            output_path=output_path,
            spell_id_map=spell_id_map,
            ability_icons=merged_ability_icons,
        )
        from datetime import date as _date
        update_docs(output_dir, {
            "spec":        spec_label,
            "class":       spec["class_name"],
            "encounter":   encounter_name,
            "parse_count": len(fights),
            "date":        _date.today().strftime("%Y-%m-%d"),
            "file":        output_path.name,
        })
    except Exception:
        _tb.print_exc()

    # --- Talents ---
    talent_votes = aggregate_talents(fights)
    loadout_string = find_most_common_loadout_string(fights)
    report = format_talent_report(talent_votes, loadout_string)

    talent_path = output_path.with_suffix(".talents.txt")
    talent_path.write_text(report)
    talent_uri = talent_path.resolve().as_uri()
    console.print(f"\n[green]Talent report saved → [link={talent_uri}]{talent_path}[/link][/green]")

    if loadout_string:
        console.print(f"\n[bold cyan]Import string:[/bold cyan] {loadout_string}")
    else:
        console.print(
            "\n[yellow]No importable talent string found in API data. "
            "See talent report for node-level pick rates.[/yellow]"
        )

    chart_uri = output_path.resolve().as_uri()
    console.print(f"\n[bold green]Done! → [link={chart_uri}]{output_path}[/link][/bold green]")


if __name__ == "__main__":
    main()
