"""
Build smoothed frequency heatmaps from cooldown and boss ability events.

For each ability, we compute a per-parse presence signal at every second of
the fight, then average across parses and smooth with a Gaussian kernel.
The result is a 2-D matrix (abilities × time) where each cell = smoothed
% of parses that cast the ability near that time.
"""

from dataclasses import dataclass, field

import numpy as np
from scipy.ndimage import gaussian_filter1d

from wcl.fetcher import FightData


@dataclass
class HeatmapData:
    """Smoothed frequency matrix for a group of abilities."""
    ability_names: list[str]
    time_points: np.ndarray        # 1-D, seconds from pull
    matrix: np.ndarray             # shape (n_abilities, n_time_points), values 0–100
    parse_counts: list[int]        # how many parses had ≥1 cast per ability
    spell_ids: list[int] = field(default_factory=list)  # parallel to ability_names


@dataclass
class BossAbility:
    spell_id: int
    spell_name: str
    icon: str = ""
    cast_times: list[float] = field(default_factory=list)
    parse_count: int = 0


def ms_to_sec(ms: int) -> float:
    return ms / 1000.0


def _spell_id(ev: dict) -> int | None:
    return ev.get("abilityGameID") or (ev.get("ability") or {}).get("guid")


def _spell_name(ev: dict, ability_names: dict[int, str] | None = None) -> str:
    sid = _spell_id(ev)
    if ability_names and sid and sid in ability_names:
        return ability_names[sid]
    return (ev.get("ability") or {}).get("name", f"Spell {sid}")


def build_heatmap(
    fights: list[FightData],
    cooldown_map: dict[int, str],
    fight_duration_sec: float,
    sigma_sec: float = 8.0,
    use_raid_events: bool = False,
) -> HeatmapData:
    """
    For each ability in cooldown_map, build a smoothed frequency curve.

    Per-parse signal: at each second, 1.0 if the ability was cast within
    that second window, 0.0 otherwise. Averaging across parses gives a
    fraction (0–1). Gaussian smoothing then blurs that into a continuous
    density so nearby casts blend together visually.
    """
    total = len(fights)
    t_max = int(np.ceil(fight_duration_sec))
    time_points = np.arange(0, t_max + 1, dtype=float)

    ability_ids = list(cooldown_map.keys())
    ability_names = [cooldown_map[sid] for sid in ability_ids]
    n = len(ability_ids)

    # Sum of per-parse signals, shape (n_abilities, n_time_points)
    summed = np.zeros((n, len(time_points)))
    parse_counts = [0] * n

    for fight in fights:
        source = fight.raid_events if use_raid_events else fight.cooldown_events
        # Build one presence signal per ability for this parse
        parse_signal = np.zeros((n, len(time_points)))
        for ev in source:
            if ev.get("type") != "cast":
                continue
            sid = _spell_id(ev)
            if sid not in cooldown_map:
                continue
            idx = ability_ids.index(sid)
            t = int(ms_to_sec(ev["timestamp"]))
            if 0 <= t < len(time_points):
                parse_signal[idx, t] = 1.0

        for i in range(n):
            if parse_signal[i].any():
                parse_counts[i] += 1
            summed[i] += parse_signal[i]

    # Average across parses → fraction 0–1, then scale to %
    avg = summed / total * 100.0

    # Gaussian smooth along the time axis
    sigma_samples = sigma_sec  # 1 sample = 1 second
    smoothed = gaussian_filter1d(avg, sigma=sigma_samples, axis=1)

    # Only keep abilities that appeared in at least one parse
    mask = [i for i, c in enumerate(parse_counts) if c > 0]
    if not mask:
        return HeatmapData([], time_points, np.empty((0, len(time_points))), [])

    return HeatmapData(
        ability_names=[ability_names[i] for i in mask],
        time_points=time_points,
        matrix=smoothed[mask],
        parse_counts=[parse_counts[i] for i in mask],
    )


def build_boss_heatmap(
    fights: list[FightData],
    fight_duration_sec: float,
    top_n: int = 50,
    sigma_sec: float = 5.0,
) -> tuple[HeatmapData, list[BossAbility]]:
    """
    Build a frequency heatmap for the top N boss abilities, and also return
    the raw BossAbility list (for drawing vlines on the other charts).
    """
    from collections import defaultdict

    total = len(fights)
    by_spell: dict[int, list[float]] = defaultdict(list)
    spell_names: dict[int, str] = {}
    parses_with: dict[int, set] = defaultdict(set)

    # Merge ability name/icon lookups from all fights
    merged_names: dict[int, str] = {}
    merged_icons: dict[int, str] = {}
    for fight in fights:
        merged_names.update(fight.ability_names)
        merged_icons.update(fight.ability_icons)

    for fight_idx, fight in enumerate(fights):
        for ev in fight.boss_events:
            if ev.get("type") != "cast":
                continue
            sid = _spell_id(ev)
            if not sid:
                continue
            name = _spell_name(ev, merged_names)
            t = ms_to_sec(ev["timestamp"])
            by_spell[sid].append(t)
            spell_names[sid] = name
            parses_with[sid].add(fight_idx)

    if not by_spell:
        empty = np.empty((0, int(fight_duration_sec) + 1))
        return HeatmapData([], np.arange(int(fight_duration_sec) + 1, dtype=float), empty, []), []

    ranked = sorted(by_spell.keys(), key=lambda s: -len(parses_with[s]))[:top_n]

    # Build raw BossAbility list (clustered cast times for vlines)
    boss_abilities = []
    for sid in ranked:
        cast_times = _cluster_median(sorted(by_spell[sid]), bin_size_sec=5.0)
        boss_abilities.append(BossAbility(
            spell_id=sid,
            spell_name=spell_names[sid],
            icon=merged_icons.get(sid, ""),
            cast_times=cast_times,
            parse_count=len(parses_with[sid]),
        ))

    # Build heatmap matrix
    cooldown_map = {sid: spell_names[sid] for sid in ranked}
    t_max = int(np.ceil(fight_duration_sec))
    time_points = np.arange(0, t_max + 1, dtype=float)
    n = len(ranked)
    summed = np.zeros((n, len(time_points)))
    parse_counts = [0] * n

    for fight_idx, fight in enumerate(fights):
        parse_signal = np.zeros((n, len(time_points)))
        for ev in fight.boss_events:
            if ev.get("type") != "cast":
                continue
            sid = _spell_id(ev)
            if sid not in cooldown_map:
                continue
            idx = ranked.index(sid)
            t = int(ms_to_sec(ev["timestamp"]))
            if 0 <= t < len(time_points):
                parse_signal[idx, t] = 1.0
        for i in range(n):
            if parse_signal[i].any():
                parse_counts[i] += 1
            summed[i] += parse_signal[i]

    avg = summed / total * 100.0
    smoothed = gaussian_filter1d(avg, sigma=sigma_sec, axis=1)

    return HeatmapData(
        ability_names=[spell_names[sid] for sid in ranked],
        spell_ids=list(ranked),
        time_points=time_points,
        matrix=smoothed,
        parse_counts=parse_counts,
    ), boss_abilities


def _cluster_median(times: list[float], bin_size_sec: float) -> list[float]:
    if not times:
        return []
    clusters: list[list[float]] = [[times[0]]]
    for t in times[1:]:
        if t - clusters[-1][-1] <= bin_size_sec:
            clusters[-1].append(t)
        else:
            clusters.append([t])
    return [sorted(c)[len(c) // 2] for c in clusters]
