import io
import typing as t

from typing_extensions import Required

StatDict = dict[str, int | None | list[int] | list[None]]

Name = str
Type = str
Element = str


class ItemDict(t.TypedDict, total=False):
    name: Required[str]
    type: Required[str]
    element: Required[str]
    transform_range: Required[str]
    common: StatDict
    max_common: StatDict
    rare: StatDict
    max_rare: StatDict
    epic: StatDict
    max_epic: StatDict
    legendary: StatDict
    max_legendary: StatDict
    mythical: StatDict
    max_mythical: StatDict
    divine: StatDict


class ItemPack(t.TypedDict):
    items: list[ItemDict]


TIERS = ("common", "rare", "epic", "legendary", "mythical", "divine")
TIER_KEYS = tuple(
    key for tier in TIERS for key in ((tier, "max_" + tier) if tier != "divine" else (tier,))
)
TYPE_ORDER = {"TORSO": 0, "LEGS": 1, "DRONE": 2, "SIDE_WEAPON": 3, "TOP_WEAPON": 4, "MODULE": 5}


def load_json(file: io.TextIOWrapper) -> t.Any:
    import json

    return json.load(file)
