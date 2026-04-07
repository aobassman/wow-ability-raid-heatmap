"""Shaman specs for Midnight expansion."""

from .common import RAID_COOLDOWNS, CONSUMABLES

_SHAMAN_DEFENSIVE = {
    108271: "Astral Shift",
    **CONSUMABLES,
}

# ---------------------------------------------------------------------------
# Enhancement
# ---------------------------------------------------------------------------
_ENH_OFFENSIVE = {
    51533:   "Feral Spirit",
    114051:  "Ascendance",
    384352:  "Doom Winds",
    204945:  "Skyfury Totem",
    1218090: "Primordial Storm",
}

ENHANCEMENT = {
    "class_name": "Shaman",
    "spec_name":  "Enhancement",
    "wcl_class":  "Shaman",
    "wcl_spec":   "Enhancement",
    "metric":     "dps",
    "cooldowns":  {**_ENH_OFFENSIVE, **_SHAMAN_DEFENSIVE},
    "raid_cooldowns": {**RAID_COOLDOWNS, 2825: "Bloodlust"},
    "cooldown_categories": {
        "Offensive": _ENH_OFFENSIVE,
        "Defensive": _SHAMAN_DEFENSIVE,
    },
}

# ---------------------------------------------------------------------------
# Elemental
# ---------------------------------------------------------------------------
_ELE_OFFENSIVE = {
    191634: "Stormkeeper",
    114050: "Ascendance",
    375982: "Primordial Wave",
    198067: "Fire Elemental",
    192249: "Storm Elemental",   # talent
    210714: "Icefury",
    382009: "Deeply Rooted Elements",
    378081: "Nature's Swiftness",
    79206:  "Spiritwalker's Grace",
}

ELEMENTAL = {
    "class_name": "Shaman",
    "spec_name":  "Elemental",
    "wcl_class":  "Shaman",
    "wcl_spec":   "Elemental",
    "metric":     "dps",
    "cooldowns":  {**_ELE_OFFENSIVE, **_SHAMAN_DEFENSIVE},
    "raid_cooldowns": {**RAID_COOLDOWNS, 2825: "Bloodlust"},
    "cooldown_categories": {
        "Offensive": _ELE_OFFENSIVE,
        "Defensive": _SHAMAN_DEFENSIVE,
    },
}

# ---------------------------------------------------------------------------
# Restoration
# ---------------------------------------------------------------------------
_RESTO_OFFENSIVE = {
    114052: "Ascendance",
    98008:  "Spirit Link Totem",
    108280: "Healing Tide Totem",
    16191:  "Mana Tide Totem",
    378081: "Nature's Swiftness",
    79206:  "Spiritwalker's Grace",
    192077: "Wind Rush Totem",
}

RESTORATION = {
    "class_name": "Shaman",
    "spec_name":  "Restoration",
    "wcl_class":  "Shaman",
    "wcl_spec":   "Restoration",
    "metric":     "hps",
    "cooldowns":  {**_RESTO_OFFENSIVE, **_SHAMAN_DEFENSIVE},
    "raid_cooldowns": {**RAID_COOLDOWNS, 2825: "Bloodlust"},
    "cooldown_categories": {
        "Offensive": _RESTO_OFFENSIVE,
        "Defensive": _SHAMAN_DEFENSIVE,
    },
}
