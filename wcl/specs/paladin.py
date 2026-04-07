"""Paladin specs for Midnight expansion."""

from .common import RAID_COOLDOWNS, CONSUMABLES

# ---------------------------------------------------------------------------
# Retribution
# ---------------------------------------------------------------------------
_RET_OFFENSIVE = {
    # Major cooldowns (confirmed IDs from Midnight)
    31884:  "Avenging Wrath",
    454351: "Avenging Wrath (Might)", # Templar hero talent variant
    231895: "Crusade",              # talent alternative to Avenging Wrath
    343721: "Final Reckoning",      # 1 min CD, defines damage window
    255937: "Wake of Ashes",        # 45s CD, generates HP + damage
    343527: "Execution Sentence",   # 1 min talent CD
    304971: "Divine Toll",          # 1 min talent CD, 5x Judgment
    383781: "Algeth'ar Puzzle",     # trinket/CD used on cooldown
    # Hero talent abilities (Templar tree)
    427453: "Hammer of Light",      # Templar major ability
    # Rotational-but-important (short CDs)
    53385:  "Divine Storm",         # AoE spender
    24275:  "Hammer of Wrath",      # execute range short CD
}

_RET_DEFENSIVE = {
    642:    "Divine Shield",
    403876: "Divine Protection",
    184662: "Shield of Vengeance",
    86659:  "Guardian of Ancient Kings",
    375576: "Eye of Tyr",
    6940:   "Blessing of Sacrifice",
    633:    "Lay on Hands",
    **CONSUMABLES,
}

RETRIBUTION = {
    "class_name": "Paladin",
    "spec_name":  "Retribution",
    "wcl_class":  "Paladin",
    "wcl_spec":   "Retribution",
    "metric":     "dps",
    "cooldowns":  {**_RET_OFFENSIVE, **_RET_DEFENSIVE},
    "raid_cooldowns": RAID_COOLDOWNS,
    "cooldown_categories": {
        "Offensive": _RET_OFFENSIVE,
        "Defensive": _RET_DEFENSIVE,
    },
}

# ---------------------------------------------------------------------------
# Holy
# ---------------------------------------------------------------------------
_HOLY_OFFENSIVE = {
    31884:  "Avenging Wrath",
    216331: "Avenging Crusader",    # talent alternative
    375576: "Divine Toll",
    53600:  "Shield of the Righteous",
}

_HOLY_DEFENSIVE = {
    31821:  "Aura Mastery",
    642:    "Divine Shield",
    498:    "Divine Protection",
    6940:   "Blessing of Sacrifice",
    633:    "Lay on Hands",
    **CONSUMABLES,
}

HOLY = {
    "class_name": "Paladin",
    "spec_name":  "Holy",
    "wcl_class":  "Paladin",
    "wcl_spec":   "Holy",
    "metric":     "hps",
    "cooldowns":  {**_HOLY_OFFENSIVE, **_HOLY_DEFENSIVE},
    "raid_cooldowns": RAID_COOLDOWNS,
    "cooldown_categories": {
        "Offensive": _HOLY_OFFENSIVE,
        "Defensive": _HOLY_DEFENSIVE,
    },
}

# ---------------------------------------------------------------------------
# Protection
# ---------------------------------------------------------------------------
_PROT_OFFENSIVE = {
    212641: "Guardian of Ancient Kings",  # 5 min
    31884:  "Avenging Wrath",             # 2 min
    375576: "Divine Toll",                # 1 min talent
    427453: "Hammer of Light",            # Templar hero talent
}

_PROT_DEFENSIVE = {
    31850:  "Ardent Defender",        # 2 min — auto-res if fatal
    642:    "Divine Shield",          # 5 min
    403876: "Divine Protection",      # 1 min
    6940:   "Blessing of Sacrifice",  # 2 min
    633:    "Lay on Hands",           # 10 min
    **CONSUMABLES,
}

PROTECTION = {
    "class_name": "Paladin",
    "spec_name":  "Protection",
    "wcl_class":  "Paladin",
    "wcl_spec":   "Protection",
    "metric":     "dps",
    "cooldowns":  {**_PROT_OFFENSIVE, **_PROT_DEFENSIVE},
    "raid_cooldowns": RAID_COOLDOWNS,
    "cooldown_categories": {
        "Offensive": _PROT_OFFENSIVE,
        "Defensive": _PROT_DEFENSIVE,
    },
}
