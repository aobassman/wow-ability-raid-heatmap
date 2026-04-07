"""Cooldowns shared across all specs."""

RAID_COOLDOWNS: dict[int, str] = {
    2825:   "Bloodlust",
    32182:  "Heroism",
    80353:  "Time Warp",
    390386: "Fury of the Aspects",
    264667: "Primal Rage",
    90355:  "Ancient Hysteria",
}

# Common consumables that appear across many specs
CONSUMABLES: dict[int, str] = {
    6262:    "Healthstone",
    1234768: "Health Potion",        # Silvermoon Health Potion (Midnight)
    1236994: "Potion of Reckless.",  # Midnight DPS potion
    1236998: "Draught of Rampant Abandon",  # Midnight DPS potion (alt)
}
