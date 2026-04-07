"""Windwalker Monk spec definition for Midnight expansion."""

# Offensive cooldowns
OFFENSIVE_COOLDOWNS = {
    1249625: "Zenith",              # Shado-Pan hero talent, ~90s CD
    322109:  "Touch of Death",      # 3 min CD
    383781:  "Algeth'ar Puzzle",    # trinket, ~90s CD
    1236994: "Potion of Reckless.", # DPS potion
    467307:  "Rushing Wind Kick",   # hero talent
    152175:  "Whirling Dragon Punch",
}

# Defensive cooldowns
DEFENSIVE_COOLDOWNS = {
    122470: "Touch of Karma",       # 90s CD — absorbs dmg, redirects back; used offensively by top players
    115203: "Fortifying Brew",      # 6 min CD
    1234768: "Health Potion",       # Silvermoon Health Potion
    6262:   "Healthstone",
}

# Raid-wide cooldowns — cast by anyone in the raid
RAID_COOLDOWNS = {
    2825:   "Bloodlust",
    32182:  "Heroism",
    80353:  "Time Warp",
    390386: "Fury of the Aspects",  # Augmentation Evoker
    264667: "Primal Rage",          # Hunter pet
    90355:  "Ancient Hysteria",     # Hunter pet
}

# All player-cast cooldowns (used for per-player event fetching)
PLAYER_COOLDOWNS: dict[int, str] = {
    **OFFENSIVE_COOLDOWNS,
    **DEFENSIVE_COOLDOWNS,
}

SPEC = {
    "class_name": "Monk",
    "spec_name": "Windwalker",
    "wcl_class": "Monk",
    "wcl_spec": "Windwalker",
    "metric": "dps",
    "cooldowns": PLAYER_COOLDOWNS,
    "raid_cooldowns": RAID_COOLDOWNS,
    "cooldown_categories": {
        "Offensive": OFFENSIVE_COOLDOWNS,
        "Defensive": DEFENSIVE_COOLDOWNS,
    },
}
