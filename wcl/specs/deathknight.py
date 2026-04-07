"""Death Knight specs for Midnight expansion."""

from .common import RAID_COOLDOWNS, CONSUMABLES

_DK_DEFENSIVE = {
    48792:  "Icebound Fortitude",
    49039:  "Lichborne",
    48707:  "Anti-Magic Shell",
    **CONSUMABLES,
}

# ---------------------------------------------------------------------------
# Blood
# ---------------------------------------------------------------------------
_BLOOD_OFFENSIVE = {
    49028:   "Dancing Rune Weapon",   # 2 min — parry + threat amp
    42650:   "Army of the Dead",      # 10 min
    194844:  "Bonestorm",             # 1 min talent
    1263566: "Abomination Limb",      # 1.5 min
}

_BLOOD_DEFENSIVE = {
    55233:  "Vampiric Blood",        # 1.5 min
    51052:  "Anti-Magic Zone",       # 2 min raid-wide magic DR
    219809: "Tombstone",             # 30s talent
    48792:  "Icebound Fortitude",
    49039:  "Lichborne",
    48707:  "Anti-Magic Shell",
    **CONSUMABLES,
}

BLOOD = {
    "class_name": "Death Knight",
    "spec_name":  "Blood",
    "wcl_class":  "DeathKnight",
    "wcl_spec":   "Blood",
    "metric":     "dps",
    "cooldowns":  {**_BLOOD_OFFENSIVE, **_BLOOD_DEFENSIVE},
    "raid_cooldowns": RAID_COOLDOWNS,
    "cooldown_categories": {
        "Offensive": _BLOOD_OFFENSIVE,
        "Defensive": _BLOOD_DEFENSIVE,
    },
}

# ---------------------------------------------------------------------------
# Unholy
# ---------------------------------------------------------------------------
_UNHOLY_OFFENSIVE = {
    42650:   "Army of the Dead",
    207289:  "Unholy Assault",
    1233448: "Dark Transformation",
    49206:   "Summon Gargoyle",
    1247378: "Putrefy",
}

UNHOLY = {
    "class_name": "Death Knight",
    "spec_name":  "Unholy",
    "wcl_class":  "DeathKnight",
    "wcl_spec":   "Unholy",
    "metric":     "dps",
    "cooldowns":  {**_UNHOLY_OFFENSIVE, **_DK_DEFENSIVE},
    "raid_cooldowns": RAID_COOLDOWNS,
    "cooldown_categories": {
        "Offensive": _UNHOLY_OFFENSIVE,
        "Defensive": _DK_DEFENSIVE,
    },
}

# ---------------------------------------------------------------------------
# Frost
# ---------------------------------------------------------------------------
_FROST_OFFENSIVE = {
    51271:   "Pillar of Frost",
    47568:   "Empower Rune Weapon",
    1249658: "Breath of Sindragosa",
    305392:  "Chill Streak",
    279302:  "Frostwyrm's Fury",
    439843:  "Reaper's Mark",
}

FROST = {
    "class_name": "Death Knight",
    "spec_name":  "Frost",
    "wcl_class":  "DeathKnight",
    "wcl_spec":   "Frost",
    "metric":     "dps",
    "cooldowns":  {**_FROST_OFFENSIVE, **_DK_DEFENSIVE},
    "raid_cooldowns": RAID_COOLDOWNS,
    "cooldown_categories": {
        "Offensive": _FROST_OFFENSIVE,
        "Defensive": _DK_DEFENSIVE,
    },
}
