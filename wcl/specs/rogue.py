"""Rogue specs for Midnight expansion."""

from .common import RAID_COOLDOWNS, CONSUMABLES

_ROGUE_DEFENSIVE = {
    5277:   "Evasion",
    31224:  "Cloak of Shadows",
    1856:   "Vanish",
    **CONSUMABLES,
}

# ---------------------------------------------------------------------------
# Assassination
# ---------------------------------------------------------------------------
_ASSA_OFFENSIVE = {
    360194: "Deathmark",
    385627: "Kingsbane",
    200806: "Exsanguinate",
    79140:  "Vendetta",       # may still exist in Midnight
}

ASSASSINATION = {
    "class_name": "Rogue",
    "spec_name":  "Assassination",
    "wcl_class":  "Rogue",
    "wcl_spec":   "Assassination",
    "metric":     "dps",
    "cooldowns":  {**_ASSA_OFFENSIVE, **_ROGUE_DEFENSIVE},
    "raid_cooldowns": RAID_COOLDOWNS,
    "cooldown_categories": {
        "Offensive": _ASSA_OFFENSIVE,
        "Defensive": _ROGUE_DEFENSIVE,
    },
}

# ---------------------------------------------------------------------------
# Outlaw
# ---------------------------------------------------------------------------
_OUTLAW_OFFENSIVE = {
    13750:   "Adrenaline Rush",
    315341:  "Roll the Bones",
    381989:  "Keep It Rolling",
    271877:  "Blade Rush",
    1277933: "Preparation",
}

OUTLAW = {
    "class_name": "Rogue",
    "spec_name":  "Outlaw",
    "wcl_class":  "Rogue",
    "wcl_spec":   "Outlaw",
    "metric":     "dps",
    "cooldowns":  {**_OUTLAW_OFFENSIVE, **_ROGUE_DEFENSIVE},
    "raid_cooldowns": RAID_COOLDOWNS,
    "cooldown_categories": {
        "Offensive": _OUTLAW_OFFENSIVE,
        "Defensive": _ROGUE_DEFENSIVE,
    },
}

# ---------------------------------------------------------------------------
# Subtlety
# ---------------------------------------------------------------------------
_SUB_OFFENSIVE = {
    185313: "Shadow Dance",
    212283: "Symbols of Death",
    280719: "Secret Technique",
    277925: "Shuriken Tornado",
    121471: "Shadow Blades",
}

SUBTLETY = {
    "class_name": "Rogue",
    "spec_name":  "Subtlety",
    "wcl_class":  "Rogue",
    "wcl_spec":   "Subtlety",
    "metric":     "dps",
    "cooldowns":  {**_SUB_OFFENSIVE, **_ROGUE_DEFENSIVE},
    "raid_cooldowns": RAID_COOLDOWNS,
    "cooldown_categories": {
        "Offensive": _SUB_OFFENSIVE,
        "Defensive": _ROGUE_DEFENSIVE,
    },
}
