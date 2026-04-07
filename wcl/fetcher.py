"""High-level data fetching: top parses, timelines, talents."""

from dataclasses import dataclass, field
from typing import Any

from rich.console import Console
from rich.progress import track

from .client import WCLClient
from .queries import TOP_PARSES_QUERY, PLAYER_DETAILS_QUERY

console = Console()


@dataclass
class ParseMeta:
    report_code: str
    fight_id: int
    character_name: str
    server: str
    percentile: float | None
    duration_ms: int
    start_time: int
    end_time: int


@dataclass
class FightData:
    meta: ParseMeta
    player_id: int
    cooldown_events: list[dict] = field(default_factory=list)
    raid_events: list[dict] = field(default_factory=list)
    boss_events: list[dict] = field(default_factory=list)
    talents: list[dict] = field(default_factory=list)
    ability_names: dict[int, str] = field(default_factory=dict)   # gameID -> name
    ability_icons: dict[int, str] = field(default_factory=dict)  # gameID -> icon slug


def fetch_top_parses(
    client: WCLClient,
    encounter_id: int,
    class_name: str,
    spec_name: str,
    metric: str = "dps",
    count: int = 10,
    difficulty: int | None = None,
) -> list[ParseMeta]:
    results: list[ParseMeta] = []
    page = 1

    while len(results) < count:
        variables: dict = {
            "encounterID": encounter_id,
            "specName": spec_name,
            "className": class_name,
            "metric": metric.lower(),
            "page": page,
        }
        if difficulty is not None:
            variables["difficulty"] = difficulty
        data = client.query(TOP_PARSES_QUERY, variables)
        rankings = data["data"]["worldData"]["encounter"]["characterRankings"]
        rows = rankings.get("rankings", [])
        if not rows:
            break

        for row in rows:
            if len(results) >= count:
                break
            if len(results) == 0:
                console.log(f"  [dim]Sample parse row: {row}[/dim]")
            report = row["report"]
            results.append(ParseMeta(
                report_code=report["code"],
                fight_id=report["fightID"],
                character_name=row["name"],
                server=row.get("server", {}).get("name", ""),
                percentile=row.get("rankPercent") or row.get("percentile") or None,
                duration_ms=row["duration"],
                start_time=0,
                end_time=row["duration"],
            ))

        if not rankings.get("hasMorePages", False):
            break
        page += 1

    return results[:count]


def fetch_fight_data(
    client: WCLClient,
    meta: ParseMeta,
    cooldown_spell_ids: list[int],
    raid_cooldown_spell_ids: list[int],
) -> FightData:
    # Resolve absolute timestamps from the report
    pd_data = client.query(PLAYER_DETAILS_QUERY, {
        "reportCode": meta.report_code,
        "fightID": meta.fight_id,
    })
    report = pd_data["data"]["reportData"]["report"]
    fight_info = report["fights"][0]
    abs_start = fight_info["startTime"]
    abs_end = fight_info["endTime"]

    player_details_raw = report["playerDetails"]
    player_id, talents = _extract_player(player_details_raw, meta.character_name)
    master_data = report.get("masterData", {})
    boss_ids = _extract_boss_ids(master_data)
    ability_names = {
        a["gameID"]: a["name"]
        for a in master_data.get("abilities", [])
        if a.get("gameID") and a.get("name")
    }
    ability_icons = {
        a["gameID"]: a["icon"]
        for a in master_data.get("abilities", [])
        if a.get("gameID") and a.get("icon")
    }


    def normalize(events: list[dict]) -> list[dict]:
        for ev in events:
            ev["timestamp"] = ev["timestamp"] - abs_start
        return events

    # 1. Player cooldowns (filtered to this player)
    cd_filter = " or ".join(f"ability.id = {sid}" for sid in cooldown_spell_ids)
    cooldown_events = normalize(client.query_all_events(
        report_code=meta.report_code,
        fight_id=meta.fight_id,
        data_type="Casts",
        source_id=player_id,
        start_time=abs_start,
        end_time=abs_end,
        filter_expression=cd_filter or None,
    ))

    # 2. Raid-wide cooldowns (any player — Bloodlust etc.)
    raid_filter = " or ".join(f"ability.id = {sid}" for sid in raid_cooldown_spell_ids)
    raid_events = normalize(client.query_all_events(
        report_code=meta.report_code,
        fight_id=meta.fight_id,
        data_type="Casts",
        start_time=abs_start,
        end_time=abs_end,
        filter_expression=raid_filter or None,
    )) if raid_cooldown_spell_ids else []

    # 3. Boss casts — use actor IDs from masterData
    # hostilityType: Enemies fetches enemy-side events; Casts dataType only returns friendly by default
    boss_events = normalize(client.query_all_events(
        report_code=meta.report_code,
        fight_id=meta.fight_id,
        data_type="Casts",
        start_time=abs_start,
        end_time=abs_end,
        hostility="Enemies",
    ))
    cd_ids_seen = {ev["abilityGameID"] for ev in cooldown_events if "abilityGameID" in ev}
    console.log(f"  Boss events: {len(boss_events)}, cooldown events: {len(cooldown_events)}, CD spell IDs seen: {cd_ids_seen}")

    return FightData(
        meta=meta,
        player_id=player_id or -1,
        cooldown_events=cooldown_events,
        raid_events=raid_events,
        boss_events=boss_events,
        talents=talents,
        ability_names=ability_names,
        ability_icons=ability_icons,
    )


def _extract_boss_ids(master_data: dict) -> list[int]:
    """Return actor IDs for boss-type NPCs from report masterData."""
    ids = []
    for actor in master_data.get("actors", []):
        if actor.get("subType") == "Boss" and actor.get("id", -1) != -1:
            ids.append(actor["id"])
    return ids


def _extract_player(player_details_raw: Any, character_name: str) -> tuple[int | None, list]:
    if isinstance(player_details_raw, dict):
        inner = player_details_raw.get("data", player_details_raw)
        if "playerDetails" in inner:
            inner = inner["playerDetails"]
        for role_list in inner.values():
            if not isinstance(role_list, list):
                continue
            for player in role_list:
                if player.get("name", "").lower() == character_name.lower():
                    return player.get("id"), player.get("talents", [])
    return None, []


def fetch_all_fight_data(
    client: WCLClient,
    parses: list[ParseMeta],
    cooldown_spell_ids: list[int],
    raid_cooldown_spell_ids: list[int],
) -> list[FightData]:
    results = []
    for meta in track(parses, description="Fetching fight data…"):
        try:
            fd = fetch_fight_data(client, meta, cooldown_spell_ids, raid_cooldown_spell_ids)
            results.append(fd)
        except Exception as exc:
            console.log(f"[red]Skipping {meta.character_name} ({meta.report_code}): {exc}[/red]")
    return results
