"""Warlock specs for Midnight expansion."""

from .common import RAID_COOLDOWNS, CONSUMABLES

_WARLOCK_DEFENSIVE = {
    108416: "Dark Pact",
    6789:   "Mortal Coil",
    104773: "Unending Resolve",
    **CONSUMABLES,
}

# ---------------------------------------------------------------------------
# Affliction
# ---------------------------------------------------------------------------
_AFFLIC_OFFENSIVE = {
    113860:  "Dark Soul: Misery",
    205180:  "Summon Darkglare",
    278350:  "Vile Taint",
    334275:  "Soul Rot",
    316099:  "Malefic Rapture",
    386997:  "Seed of Corruption",
    1257052: "Dark Harvest",
}

AFFLICTION = {
    "class_name": "Warlock",
    "spec_name":  "Affliction",
    "wcl_class":  "Warlock",
    "wcl_spec":   "Affliction",
    "metric":     "dps",
    "cooldowns":  {**_AFFLIC_OFFENSIVE, **_WARLOCK_DEFENSIVE},
    "raid_cooldowns": RAID_COOLDOWNS,
    "cooldown_categories": {
        "Offensive": _AFFLIC_OFFENSIVE,
        "Defensive": _WARLOCK_DEFENSIVE,
    },
}

# ---------------------------------------------------------------------------
# Destruction
# ---------------------------------------------------------------------------
_DESTRO_OFFENSIVE = {
    113858: "Dark Soul: Instability",
    1122:   "Summon Infernal",
    265273: "Summon Blasphemy",   # talent
    442726: "Malevolence",
    152108: "Cataclysm",
}

DESTRUCTION = {
    "class_name": "Warlock",
    "spec_name":  "Destruction",
    "wcl_class":  "Warlock",
    "wcl_spec":   "Destruction",
    "metric":     "dps",
    "cooldowns":  {**_DESTRO_OFFENSIVE, **_WARLOCK_DEFENSIVE},
    "raid_cooldowns": RAID_COOLDOWNS,
    "cooldown_categories": {
        "Offensive": _DESTRO_OFFENSIVE,
        "Defensive": _WARLOCK_DEFENSIVE,
    },
}

# ---------------------------------------------------------------------------
# Demonology
# ---------------------------------------------------------------------------
_DEMO_OFFENSIVE = {
    265187:  "Summon Demonic Tyrant",
    267217:  "Nether Portal",
    264130:  "Power Siphon",
    1276452: "Grimoire: Imp Lord",
}

DEMONOLOGY = {
    "class_name": "Warlock",
    "spec_name":  "Demonology",
    "wcl_class":  "Warlock",
    "wcl_spec":   "Demonology",
    "metric":     "dps",
    "cooldowns":  {**_DEMO_OFFENSIVE, **_WARLOCK_DEFENSIVE},
    "raid_cooldowns": RAID_COOLDOWNS,
    "cooldown_categories": {
        "Offensive": _DEMO_OFFENSIVE,
        "Defensive": _WARLOCK_DEFENSIVE,
    },
}
