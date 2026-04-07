"""Druid specs for Midnight expansion."""

from .common import RAID_COOLDOWNS, CONSUMABLES

_DRUID_DEFENSIVE = {
    22812:  "Barkskin",
    61336:  "Survival Instincts",
    **CONSUMABLES,
}

# ---------------------------------------------------------------------------
# Balance
# ---------------------------------------------------------------------------
_BALANCE_OFFENSIVE = {
    194223: "Celestial Alignment",
    102560: "Incarnation: Chosen of Elune",  # talent
    202770: "Fury of Elune",
    391528: "Convoke the Spirits",
    78674:  "Starsurge",
    191034: "Starfall",
    383410: "Astral Communion",
    205636: "Force of Nature",
    29166:  "Innervate",
}

BALANCE = {
    "class_name": "Druid",
    "spec_name":  "Balance",
    "wcl_class":  "Druid",
    "wcl_spec":   "Balance",
    "metric":     "dps",
    "cooldowns":  {**_BALANCE_OFFENSIVE, **_DRUID_DEFENSIVE},
    "raid_cooldowns": RAID_COOLDOWNS,
    "cooldown_categories": {
        "Offensive": _BALANCE_OFFENSIVE,
        "Defensive": _DRUID_DEFENSIVE,
    },
}

# ---------------------------------------------------------------------------
# Feral
# ---------------------------------------------------------------------------
_FERAL_OFFENSIVE = {
    106951: "Berserk",
    102543: "Incarnation: Avatar of Ashamane",  # talent
    5217:   "Tiger's Fury",
    391528: "Convoke the Spirits",
    274837: "Feral Frenzy",
}

FERAL = {
    "class_name": "Druid",
    "spec_name":  "Feral",
    "wcl_class":  "Druid",
    "wcl_spec":   "Feral",
    "metric":     "dps",
    "cooldowns":  {**_FERAL_OFFENSIVE, **_DRUID_DEFENSIVE},
    "raid_cooldowns": RAID_COOLDOWNS,
    "cooldown_categories": {
        "Offensive": _FERAL_OFFENSIVE,
        "Defensive": _DRUID_DEFENSIVE,
    },
}

# ---------------------------------------------------------------------------
# Restoration
# ---------------------------------------------------------------------------
_RESTO_OFFENSIVE = {
    391528: "Convoke the Spirits",
    102342: "Ironbark",
    33891:  "Incarnation: Tree of Life",
    132158: "Nature's Swiftness",
    29166:  "Innervate",
}

_RESTO_DEFENSIVE = {
    740:    "Tranquility",
    **CONSUMABLES,
}

RESTORATION = {
    "class_name": "Druid",
    "spec_name":  "Restoration",
    "wcl_class":  "Druid",
    "wcl_spec":   "Restoration",
    "metric":     "hps",
    "cooldowns":  {**_RESTO_OFFENSIVE, **_RESTO_DEFENSIVE},
    "raid_cooldowns": RAID_COOLDOWNS,
    "cooldown_categories": {
        "Offensive": _RESTO_OFFENSIVE,
        "Defensive": _RESTO_DEFENSIVE,
    },
}

# ---------------------------------------------------------------------------
# Guardian
# ---------------------------------------------------------------------------
_GUARDIAN_OFFENSIVE = {
    50334:   "Berserk",               # 3 min
    102558:  "Incarnation: Guardian of Ursoc",  # talent alt
    391528:  "Convoke the Spirits",   # talent
    204066:  "Lunar Beam",            # 1 min
    1252871: "Red Moon",              # hero talent
    1269658: "Wild Guardian",         # hero talent
}

_GUARDIAN_DEFENSIVE = {
    22812:  "Barkskin",              # 1 min
    61336:  "Survival Instincts",    # 2 min
    102342: "Ironbark",              # 1 min (cast on ally)
    **CONSUMABLES,
}

GUARDIAN = {
    "class_name": "Druid",
    "spec_name":  "Guardian",
    "wcl_class":  "Druid",
    "wcl_spec":   "Guardian",
    "metric":     "dps",
    "cooldowns":  {**_GUARDIAN_OFFENSIVE, **_GUARDIAN_DEFENSIVE},
    "raid_cooldowns": RAID_COOLDOWNS,
    "cooldown_categories": {
        "Offensive": _GUARDIAN_OFFENSIVE,
        "Defensive": _GUARDIAN_DEFENSIVE,
    },
}
