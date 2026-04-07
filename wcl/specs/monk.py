"""Monk specs for Midnight expansion (Brewmaster, Mistweaver)."""

from .common import RAID_COOLDOWNS, CONSUMABLES

# ---------------------------------------------------------------------------
# Brewmaster
# ---------------------------------------------------------------------------
_BM_OFFENSIVE = {
    132578:  "Invoke Niuzao, the Black Ox",  # 3 min
    115399:  "Black Ox Brew",                # 1.5 min — restores Brews/Stagger
    325153:  "Exploding Keg",                # 1 min
    1263438: "Empty the Cellar",             # hero talent
    322109:  "Touch of Death",               # 3 min
}

_BM_DEFENSIVE = {
    115176: "Zen Meditation",    # 5 min
    122278: "Dampen Harm",       # 2 min — reduces big hits by 50%
    122783: "Diffuse Magic",     # 1.5 min talent — magic DR
    322507: "Celestial Brew",    # 1 min — absorb shield
    115203: "Fortifying Brew",   # 6 min
    **CONSUMABLES,
}

BREWMASTER = {
    "class_name": "Monk",
    "spec_name":  "Brewmaster",
    "wcl_class":  "Monk",
    "wcl_spec":   "Brewmaster",
    "metric":     "dps",
    "cooldowns":  {**_BM_OFFENSIVE, **_BM_DEFENSIVE},
    "raid_cooldowns": RAID_COOLDOWNS,
    "cooldown_categories": {
        "Offensive": _BM_OFFENSIVE,
        "Defensive": _BM_DEFENSIVE,
    },
}

# ---------------------------------------------------------------------------
# Mistweaver
# ---------------------------------------------------------------------------
_MW_OFFENSIVE = {
    322118: "Invoke Yu'lon, the Jade Serpent",  # 3 min
    325197: "Invoke Chi-Ji, the Red Crane",     # talent alt
    115310: "Revival",              # 3 min — mass group heal + dispel
    116849: "Life Cocoon",          # 2 min — single target absorb
    197908: "Mana Tea",             # 1.5 min mana CD
    443028: "Celestial Conduit",    # hero talent
    443591: "Unity Within",         # hero talent
}

_MW_DEFENSIVE = {
    122470: "Touch of Karma",       # 90s — absorb + redirect dmg
    116844: "Ring of Peace",        # 45s CC utility
    **CONSUMABLES,
}

MISTWEAVER = {
    "class_name": "Monk",
    "spec_name":  "Mistweaver",
    "wcl_class":  "Monk",
    "wcl_spec":   "Mistweaver",
    "metric":     "hps",
    "cooldowns":  {**_MW_OFFENSIVE, **_MW_DEFENSIVE},
    "raid_cooldowns": RAID_COOLDOWNS,
    "cooldown_categories": {
        "Offensive": _MW_OFFENSIVE,
        "Defensive": _MW_DEFENSIVE,
    },
}
