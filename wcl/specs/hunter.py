"""Hunter specs for Midnight expansion."""

from .common import RAID_COOLDOWNS, CONSUMABLES

_HUNTER_DEFENSIVE = {
    186265: "Aspect of the Turtle",
    109304: "Exhilaration",
    264735: "Survival of the Fittest",
    **CONSUMABLES,
}

# ---------------------------------------------------------------------------
# Beast Mastery
# ---------------------------------------------------------------------------
_BM_OFFENSIVE = {
    19574:  "Bestial Wrath",
    359844: "Call of the Wild",
    321530: "Bloodshed",
    193530: "Aspect of the Wild",
}

BEAST_MASTERY = {
    "class_name": "Hunter",
    "spec_name":  "Beast Mastery",
    "wcl_class":  "Hunter",
    "wcl_spec":   "BeastMastery",
    "metric":     "dps",
    "cooldowns":  {**_BM_OFFENSIVE, **_HUNTER_DEFENSIVE},
    "raid_cooldowns": {**RAID_COOLDOWNS, 264667: "Primal Rage"},
    "cooldown_categories": {
        "Offensive": _BM_OFFENSIVE,
        "Defensive": _HUNTER_DEFENSIVE,
    },
}

# ---------------------------------------------------------------------------
# Marksmanship
# ---------------------------------------------------------------------------
_MM_OFFENSIVE = {
    288613:  "Trueshot",
    257044:  "Rapid Fire",
    260243:  "Volley",
    1264949: "Moonlight Chakram",
}

MARKSMANSHIP = {
    "class_name": "Hunter",
    "spec_name":  "Marksmanship",
    "wcl_class":  "Hunter",
    "wcl_spec":   "Marksmanship",
    "metric":     "dps",
    "cooldowns":  {**_MM_OFFENSIVE, **_HUNTER_DEFENSIVE},
    "raid_cooldowns": RAID_COOLDOWNS,
    "cooldown_categories": {
        "Offensive": _MM_OFFENSIVE,
        "Defensive": _HUNTER_DEFENSIVE,
    },
}

# ---------------------------------------------------------------------------
# Survival
# ---------------------------------------------------------------------------
_SV_OFFENSIVE = {
    360952:  "Coordinated Assault",
    259495:  "Wildfire Bomb",
    320976:  "Flanking Strike",
    1261193: "Boomstick",
    1250646: "Takedown",
    186289:  "Aspect of the Eagle",
}

SURVIVAL = {
    "class_name": "Hunter",
    "spec_name":  "Survival",
    "wcl_class":  "Hunter",
    "wcl_spec":   "Survival",
    "metric":     "dps",
    "cooldowns":  {**_SV_OFFENSIVE, **_HUNTER_DEFENSIVE},
    "raid_cooldowns": RAID_COOLDOWNS,
    "cooldown_categories": {
        "Offensive": _SV_OFFENSIVE,
        "Defensive": _HUNTER_DEFENSIVE,
    },
}
