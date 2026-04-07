"""
Talent aggregation and WoW importable string generation.

WoW talent export strings are base64url-encoded binary blobs. The format is
documented in the community (e.g. Simulationcraft / simc source). The structure:
  - 2-byte header: [serialization_version(1), class_id(1)]  -- actually more fields
  - Bitpacked talent choices

Because the binary format is complex and version-dependent, we take two approaches:
  1. Find the most common raw export string among the 20 parses and return that
     directly (most reliable — it's a real string from a top parse).
  2. Fallback: report talent node vote counts for manual inspection.

WCL's playerDetails returns talents as a list of {id, rank} dicts where `id` is
the talent node entry ID (not the spell ID). The actual loadout string (the one
you paste in-game) is not directly in the API response, so approach #1 requires
scraping the character page — which we skip. Instead we provide the majority-vote
talent list and note which string appeared most among parses that include it.
"""

from collections import Counter
from dataclasses import dataclass

from wcl.fetcher import FightData


@dataclass
class TalentVote:
    node_id: int
    rank: int
    votes: int
    total_parses: int

    @property
    def pick_rate(self) -> float:
        return self.votes / max(1, self.total_parses)


def aggregate_talents(fights: list[FightData]) -> list[TalentVote]:
    """
    Count how often each (node_id, rank) pair appears across all parses.
    Returns sorted by node_id for stable output.
    """
    total = len(fights)
    # (node_id, rank) -> count
    counter: Counter = Counter()

    for fight in fights:
        seen_nodes: set[int] = set()
        for talent in fight.talents:
            nid = talent.get("id") or talent.get("nodeID")
            rank = talent.get("rank", 1)
            if nid and nid not in seen_nodes:
                counter[(nid, rank)] += 1
                seen_nodes.add(nid)

    # For each node, keep the most popular rank choice
    by_node: dict[int, tuple[int, int]] = {}  # node_id -> (rank, votes)
    for (nid, rank), votes in counter.items():
        if nid not in by_node or votes > by_node[nid][1]:
            by_node[nid] = (rank, votes)

    results = [
        TalentVote(node_id=nid, rank=rank, votes=votes, total_parses=total)
        for nid, (rank, votes) in sorted(by_node.items())
    ]
    return results


def find_most_common_loadout_string(fights: list[FightData]) -> str | None:
    """
    If any fight data includes a raw loadout string (from combatant info),
    return the most common one. WCL sometimes embeds this in the talents blob.
    """
    strings: list[str] = []
    for fight in fights:
        for talent in fight.talents:
            s = talent.get("loadoutString") or talent.get("exportString")
            if s:
                strings.append(s)

    if not strings:
        return None
    most_common, _ = Counter(strings).most_common(1)[0]
    return most_common


def format_talent_report(votes: list[TalentVote], loadout_string: str | None) -> str:
    lines = []

    if loadout_string:
        lines.append("=== IMPORTABLE TALENT STRING ===")
        lines.append("Paste this in-game: Game Menu → Talents → Import")
        lines.append("")
        lines.append(loadout_string)
        lines.append("")

    lines.append("=== TALENT NODE POPULARITY ===")
    lines.append(f"{'Node ID':<12} {'Rank':<6} {'Pick Rate':<12} {'Votes'}")
    lines.append("-" * 45)
    for v in sorted(votes, key=lambda x: -x.pick_rate):
        bar = "█" * int(v.pick_rate * 20)
        lines.append(
            f"{v.node_id:<12} {v.rank:<6} {v.pick_rate:>6.0%}       "
            f"{v.votes}/{v.total_parses}  {bar}"
        )
    return "\n".join(lines)
