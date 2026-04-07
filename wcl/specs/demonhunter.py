"""Demon Hunter specs for Midnight expansion."""

from .common import RAID_COOLDOWNS, CONSUMABLES

# ---------------------------------------------------------------------------
# Havoc
# ---------------------------------------------------------------------------
_HAVOC_OFFENSIVE = {
    200166: "Metamorphosis",
    198013: "Eye Beam",
    258860: "Essence Break",
    370965: "The Hunt",
    442294: "Reaver's Glaive",
    452497: "Abyssal Gaze",
}

_HAVOC_DEFENSIVE = {
    196555: "Netherwalk",
    212800: "Blur",
    188499: "Blade Ward",
    196718: "Darkness",
    **CONSUMABLES,
}

HAVOC = {
    "class_name": "Demon Hunter",
    "spec_name":  "Havoc",
    "wcl_class":  "DemonHunter",
    "wcl_spec":   "Havoc",
    "metric":     "dps",
    "cooldowns":  {**_HAVOC_OFFENSIVE, **_HAVOC_DEFENSIVE},
    "raid_cooldowns": RAID_COOLDOWNS,
    "cooldown_categories": {
        "Offensive": _HAVOC_OFFENSIVE,
        "Defensive": _HAVOC_DEFENSIVE,
    },
}

# ---------------------------------------------------------------------------
# Vengeance
# ---------------------------------------------------------------------------
_VENG_OFFENSIVE = {
    187827: "Metamorphosis",         # 3 min — tank meta (HP + DR)
    212084: "Fel Devastation",       # 1 min — channel heal + damage
    347765: "Fodder to the Flame",   # 1 min talent
    207407: "Soul Carver",           # 1 min
    390163: "Sigil of Spite",        # 1 min
}

_VENG_DEFENSIVE = {
    204021: "Fiery Brand",           # 1 min — single target 40% DR
    196718: "Darkness",              # 3 min — raid-wide 20% dodge
    198589: "Blur",                  # 1 min — personal 50% dodge
    **CONSUMABLES,
}

VENGEANCE = {
    "class_name": "Demon Hunter",
    "spec_name":  "Vengeance",
    "wcl_class":  "DemonHunter",
    "wcl_spec":   "Vengeance",
    "metric":     "dps",
    "cooldowns":  {**_VENG_OFFENSIVE, **_VENG_DEFENSIVE},
    "raid_cooldowns": RAID_COOLDOWNS,
    "cooldown_categories": {
        "Offensive": _VENG_OFFENSIVE,
        "Defensive": _VENG_DEFENSIVE,
    },
}
