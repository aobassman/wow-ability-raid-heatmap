"""Evoker specs for Midnight expansion."""

from .common import RAID_COOLDOWNS, CONSUMABLES

_EVOKER_DEFENSIVE = {
    363916: "Obsidian Scales",
    374348: "Renewing Blaze",
    **CONSUMABLES,
}

# ---------------------------------------------------------------------------
# Devastation
# ---------------------------------------------------------------------------
_DEV_OFFENSIVE = {
    375087: "Dragonrage",
    357208: "Fire Breath",
    359073: "Eternity Surge",
    370553: "Tip the Scales",
    433874: "Deep Breath",
    374968: "Time Spiral",
}

DEVASTATION = {
    "class_name": "Evoker",
    "spec_name":  "Devastation",
    "wcl_class":  "Evoker",
    "wcl_spec":   "Devastation",
    "metric":     "dps",
    "cooldowns":  {**_DEV_OFFENSIVE, **_EVOKER_DEFENSIVE},
    "raid_cooldowns": RAID_COOLDOWNS,
    "cooldown_categories": {
        "Offensive": _DEV_OFFENSIVE,
        "Defensive": _EVOKER_DEFENSIVE,
    },
}

# ---------------------------------------------------------------------------
# Augmentation
# ---------------------------------------------------------------------------
_AUG_OFFENSIVE = {
    395152: "Ebon Might",
    442204: "Breath of Eons",
    396286: "Upheaval",
    370553: "Tip the Scales",
    406732: "Spatial Paradox",
    374968: "Time Spiral",
    404977: "Time Skip",
}

_AUG_DEFENSIVE = {
    363916: "Obsidian Scales",
    374348: "Renewing Blaze",
    **CONSUMABLES,
}

AUGMENTATION = {
    "class_name": "Evoker",
    "spec_name":  "Augmentation",
    "wcl_class":  "Evoker",
    "wcl_spec":   "Augmentation",
    "metric":     "dps",
    "cooldowns":  {**_AUG_OFFENSIVE, **_AUG_DEFENSIVE},
    "raid_cooldowns": {**RAID_COOLDOWNS, 390386: "Fury of the Aspects"},
    "cooldown_categories": {
        "Offensive": _AUG_OFFENSIVE,
        "Defensive": _AUG_DEFENSIVE,
    },
}

# ---------------------------------------------------------------------------
# Preservation
# ---------------------------------------------------------------------------
_PRES_OFFENSIVE = {
    363534: "Rewind",                # 2.5 min — reverse time major heal CD
    374227: "Zephyr",                # 2 min — raid-wide 20% dodge
    359816: "Dream Flight",          # 2 min — healing channel
    370960: "Emerald Communion",     # 3 min talent — channel + heal
    389784: "Stasis",                # 1.5 min talent
    370553: "Tip the Scales",        # 1 min
    357170: "Time Dilation",         # 1.5 min — extends buffs on ally
    355941: "Dream Breath",          # 1 min — major heal
    374968: "Time Spiral",           # 2 min talent — resets mobility
}

PRESERVATION = {
    "class_name": "Evoker",
    "spec_name":  "Preservation",
    "wcl_class":  "Evoker",
    "wcl_spec":   "Preservation",
    "metric":     "hps",
    "cooldowns":  {**_PRES_OFFENSIVE, **_EVOKER_DEFENSIVE},
    "raid_cooldowns": RAID_COOLDOWNS,
    "cooldown_categories": {
        "Offensive": _PRES_OFFENSIVE,
        "Defensive": _EVOKER_DEFENSIVE,
    },
}
