"""Mage specs for Midnight expansion."""

from .common import RAID_COOLDOWNS, CONSUMABLES

_MAGE_DEFENSIVE = {
    45438:  "Ice Block",
    342245: "Alter Time",
    414658: "Ice Cold",
    **CONSUMABLES,
}

# ---------------------------------------------------------------------------
# Fire
# ---------------------------------------------------------------------------
_FIRE_OFFENSIVE = {
    190319: "Combustion",
    153561: "Meteor",
    257541: "Phoenix Flames",
    382440: "Shifting Power",
    108853: "Fire Blast",
    108843: "Flamestrike",
    55342:  "Mirror Image",
}

FIRE = {
    "class_name": "Mage",
    "spec_name":  "Fire",
    "wcl_class":  "Mage",
    "wcl_spec":   "Fire",
    "metric":     "dps",
    "cooldowns":  {**_FIRE_OFFENSIVE, **_MAGE_DEFENSIVE},
    "raid_cooldowns": {**RAID_COOLDOWNS, 80353: "Time Warp"},
    "cooldown_categories": {
        "Offensive": _FIRE_OFFENSIVE,
        "Defensive": _MAGE_DEFENSIVE,
    },
}

# ---------------------------------------------------------------------------
# Frost
# ---------------------------------------------------------------------------
_FROST_OFFENSIVE = {
    12472:  "Icy Veins",
    84714:  "Frozen Orb",
    205021: "Ray of Frost",
    199786: "Glacial Spike",
}

FROST = {
    "class_name": "Mage",
    "spec_name":  "Frost",
    "wcl_class":  "Mage",
    "wcl_spec":   "Frost",
    "metric":     "dps",
    "cooldowns":  {**_FROST_OFFENSIVE, **_MAGE_DEFENSIVE},
    "raid_cooldowns": {**RAID_COOLDOWNS, 80353: "Time Warp"},
    "cooldown_categories": {
        "Offensive": _FROST_OFFENSIVE,
        "Defensive": _MAGE_DEFENSIVE,
    },
}

# ---------------------------------------------------------------------------
# Arcane
# ---------------------------------------------------------------------------
_ARCANE_OFFENSIVE = {
    365350: "Arcane Surge",
    210824: "Touch of the Magi",
    376103: "Radiant Spark",
    321507: "Shifting Power",
    342247: "Alter Time",
    365362: "Arcane Orb",
    205025: "Presence of Mind",
    55342:  "Mirror Image",
}

ARCANE = {
    "class_name": "Mage",
    "spec_name":  "Arcane",
    "wcl_class":  "Mage",
    "wcl_spec":   "Arcane",
    "metric":     "dps",
    "cooldowns":  {**_ARCANE_OFFENSIVE, **_MAGE_DEFENSIVE},
    "raid_cooldowns": {**RAID_COOLDOWNS, 80353: "Time Warp"},
    "cooldown_categories": {
        "Offensive": _ARCANE_OFFENSIVE,
        "Defensive": _MAGE_DEFENSIVE,
    },
}
