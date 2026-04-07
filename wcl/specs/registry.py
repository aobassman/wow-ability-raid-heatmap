"""Registry of all supported specs."""

from .windwalker  import SPEC as WINDWALKER
from .monk        import BREWMASTER, MISTWEAVER
from .paladin     import RETRIBUTION, HOLY as HOLY_PALADIN, PROTECTION as PROT_PALADIN
from .mage        import FIRE, ARCANE
from .mage        import FROST as FROST_MAGE
from .warrior     import FURY, ARMS, PROTECTION as PROT_WARRIOR
from .deathknight import BLOOD, UNHOLY
from .deathknight import FROST as FROST_DK
from .demonhunter import HAVOC, VENGEANCE
from .druid       import BALANCE, FERAL, GUARDIAN
from .druid       import RESTORATION as RESTO_DRUID
from .hunter      import BEAST_MASTERY, MARKSMANSHIP, SURVIVAL
from .priest      import SHADOW, DISCIPLINE, HOLY as HOLY_PRIEST
from .shaman      import ENHANCEMENT, ELEMENTAL
from .shaman      import RESTORATION as RESTO_SHAMAN
from .warlock     import AFFLICTION, DESTRUCTION, DEMONOLOGY
from .rogue       import ASSASSINATION, OUTLAW, SUBTLETY
from .evoker      import DEVASTATION, AUGMENTATION, PRESERVATION

_REGISTRY: dict[str, dict] = {
    # Death Knight
    "blood":         BLOOD,
    "unholy":        UNHOLY,
    "frost-dk":      FROST_DK,
    # Demon Hunter
    "havoc":         HAVOC,
    "vengeance":     VENGEANCE,
    # Druid
    "balance":       BALANCE,
    "feral":         FERAL,
    "guardian":      GUARDIAN,
    "resto-druid":   RESTO_DRUID,
    # Evoker
    "augmentation":  AUGMENTATION,
    "devastation":   DEVASTATION,
    "preservation":  PRESERVATION,
    # Hunter
    "bm":            BEAST_MASTERY,
    "mm":            MARKSMANSHIP,
    "survival":      SURVIVAL,
    # Mage
    "arcane":        ARCANE,
    "fire":          FIRE,
    "frost":         FROST_MAGE,
    # Monk
    "brewmaster":    BREWMASTER,
    "mistweaver":    MISTWEAVER,
    "windwalker":    WINDWALKER,
    # Paladin
    "holy-paladin":  HOLY_PALADIN,
    "prot-paladin":  PROT_PALADIN,
    "retribution":   RETRIBUTION,
    # Priest
    "discipline":    DISCIPLINE,
    "holy-priest":   HOLY_PRIEST,
    "shadow":        SHADOW,
    # Rogue
    "assassination": ASSASSINATION,
    "outlaw":        OUTLAW,
    "subtlety":      SUBTLETY,
    # Shaman
    "elemental":     ELEMENTAL,
    "enhancement":   ENHANCEMENT,
    "resto-shaman":  RESTO_SHAMAN,
    # Warlock
    "affliction":    AFFLICTION,
    "demonology":    DEMONOLOGY,
    "destruction":   DESTRUCTION,
    # Warrior
    "arms":          ARMS,
    "fury":          FURY,
    "prot-warrior":  PROT_WARRIOR,
}


def get_spec(name: str) -> dict:
    # Try exact key first, then with hyphens/spaces normalised
    key = name.lower().strip()
    if key in _REGISTRY:
        return _REGISTRY[key]
    normalised = key.replace(" ", "").replace("-", "")
    for k, v in _REGISTRY.items():
        if k.replace("-", "") == normalised:
            return v
    raise ValueError(f"Unknown spec '{name}'. Available: {list(_REGISTRY)}")


def list_specs() -> list[str]:
    """Return display names ('Retribution Paladin') sorted alphabetically."""
    names = [f"{v['spec_name']} {v['class_name']}" for v in _REGISTRY.values()]
    return sorted(names)


def get_spec_by_display(display_name: str) -> dict:
    for v in _REGISTRY.values():
        if f"{v['spec_name']} {v['class_name']}" == display_name:
            return v
    raise ValueError(f"Unknown spec display name: {display_name!r}")
