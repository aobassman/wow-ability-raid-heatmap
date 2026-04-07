"""Priest specs for Midnight expansion."""

from .common import RAID_COOLDOWNS, CONSUMABLES

# ---------------------------------------------------------------------------
# Shadow
# ---------------------------------------------------------------------------
_SHADOW_OFFENSIVE = {
    228260: "Void Eruption",
    391109: "Dark Ascension",    # talent alternative
    200174: "Mindbender",
    10060:  "Power Infusion",
    228652: "Void Torrent",
    341374: "Mindgames",
    391241: "Shadowy Insight",
    373983: "Idol of C'Thun",
}

_SHADOW_DEFENSIVE = {
    47585:  "Dispersion",
    213602: "Greater Fade",
    19236:  "Desperate Prayer",
    **CONSUMABLES,
}

SHADOW = {
    "class_name": "Priest",
    "spec_name":  "Shadow",
    "wcl_class":  "Priest",
    "wcl_spec":   "Shadow",
    "metric":     "dps",
    "cooldowns":  {**_SHADOW_OFFENSIVE, **_SHADOW_DEFENSIVE},
    "raid_cooldowns": RAID_COOLDOWNS,
    "cooldown_categories": {
        "Offensive": _SHADOW_OFFENSIVE,
        "Defensive": _SHADOW_DEFENSIVE,
    },
}

# ---------------------------------------------------------------------------
# Holy
# ---------------------------------------------------------------------------
_HOLY_PRIEST_OFFENSIVE = {
    64843:  "Divine Hymn",           # 3 min raid healing CD
    265202: "Holy Word: Salvation",  # 3 min talent raid CD
    47788:  "Guardian Spirit",       # 1 min single-target CD
    200183: "Apotheosis",            # 45s CD (enters an empowered state)
    10060:  "Power Infusion",        # 2 min
}

_HOLY_PRIEST_DEFENSIVE = {
    64901:  "Symbol of Hope",        # raid mana restore
    19236:  "Desperate Prayer",      # 90s personal defensive
    **CONSUMABLES,
}

HOLY = {
    "class_name": "Priest",
    "spec_name":  "Holy",
    "wcl_class":  "Priest",
    "wcl_spec":   "Holy",
    "metric":     "hps",
    "cooldowns":  {**_HOLY_PRIEST_OFFENSIVE, **_HOLY_PRIEST_DEFENSIVE},
    "raid_cooldowns": RAID_COOLDOWNS,
    "cooldown_categories": {
        "Offensive": _HOLY_PRIEST_OFFENSIVE,
        "Defensive": _HOLY_PRIEST_DEFENSIVE,
    },
}

# ---------------------------------------------------------------------------
# Discipline
# ---------------------------------------------------------------------------
_DISC_OFFENSIVE = {
    472433: "Evangelism",
    10060:  "Power Infusion",
    62618:  "Power Word: Barrier",
    47536:  "Rapture",
    421453: "Ultimate Penitence",
}

_DISC_DEFENSIVE = {
    19236:  "Desperate Prayer",
    **CONSUMABLES,
}

DISCIPLINE = {
    "class_name": "Priest",
    "spec_name":  "Discipline",
    "wcl_class":  "Priest",
    "wcl_spec":   "Discipline",
    "metric":     "hps",
    "cooldowns":  {**_DISC_OFFENSIVE, **_DISC_DEFENSIVE},
    "raid_cooldowns": RAID_COOLDOWNS,
    "cooldown_categories": {
        "Offensive": _DISC_OFFENSIVE,
        "Defensive": _DISC_DEFENSIVE,
    },
}
