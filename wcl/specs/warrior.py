"""Warrior specs for Midnight expansion."""

from .common import RAID_COOLDOWNS, CONSUMABLES

_WARRIOR_DEFENSIVE = {
    871:    "Shield Wall",
    23920:  "Spell Reflection",
    97462:  "Rallying Cry",        # also a raid CD
    **CONSUMABLES,
}

# ---------------------------------------------------------------------------
# Fury
# ---------------------------------------------------------------------------
_FURY_OFFENSIVE = {
    1719:   "Recklessness",
    107574: "Avatar",
    46924:  "Bladestorm",
    315720: "Onslaught",
    385060: "Odyn's Fury",
    335097: "Crushing Blow",
}

FURY = {
    "class_name": "Warrior",
    "spec_name":  "Fury",
    "wcl_class":  "Warrior",
    "wcl_spec":   "Fury",
    "metric":     "dps",
    "cooldowns":  {**_FURY_OFFENSIVE, **_WARRIOR_DEFENSIVE},
    "raid_cooldowns": RAID_COOLDOWNS,
    "cooldown_categories": {
        "Offensive": _FURY_OFFENSIVE,
        "Defensive": _WARRIOR_DEFENSIVE,
    },
}

# ---------------------------------------------------------------------------
# Arms
# ---------------------------------------------------------------------------
_ARMS_OFFENSIVE = {
    107574: "Avatar",
    446035: "Bladestorm",
    262161: "Warbreaker",
    167105: "Colossus Smash",
    436358: "Demolish",
}

_ARMS_DEFENSIVE = {
    **_WARRIOR_DEFENSIVE,
    118038: "Die by the Sword",
}

ARMS = {
    "class_name": "Warrior",
    "spec_name":  "Arms",
    "wcl_class":  "Warrior",
    "wcl_spec":   "Arms",
    "metric":     "dps",
    "cooldowns":  {**_ARMS_OFFENSIVE, **_ARMS_DEFENSIVE},
    "raid_cooldowns": RAID_COOLDOWNS,
    "cooldown_categories": {
        "Offensive": _ARMS_OFFENSIVE,
        "Defensive": _ARMS_DEFENSIVE,
    },
}

# ---------------------------------------------------------------------------
# Protection
# ---------------------------------------------------------------------------
_PROT_WARRIOR_OFFENSIVE = {
    107574: "Avatar",
    228920: "Ravager",               # talent
    385954: "Shield Charge",         # talent
    46968:  "Shockwave",             # talent
}

_PROT_WARRIOR_DEFENSIVE = {
    871:    "Shield Wall",           # 4 min
    12975:  "Last Stand",            # 3 min
    1160:   "Demoralizing Shout",    # 1.5 min — raid-wide physical DR
    23920:  "Spell Reflection",      # 25s
    97462:  "Rallying Cry",          # 3 min raid CD
    **CONSUMABLES,
}

PROTECTION = {
    "class_name": "Warrior",
    "spec_name":  "Protection",
    "wcl_class":  "Warrior",
    "wcl_spec":   "Protection",
    "metric":     "dps",
    "cooldowns":  {**_PROT_WARRIOR_OFFENSIVE, **_PROT_WARRIOR_DEFENSIVE},
    "raid_cooldowns": RAID_COOLDOWNS,
    "cooldown_categories": {
        "Offensive": _PROT_WARRIOR_OFFENSIVE,
        "Defensive": _PROT_WARRIOR_DEFENSIVE,
    },
}
