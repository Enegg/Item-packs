import io
import typing as t

from typing_extensions import Required

StatDict = dict[str, int | None | list[int | None]]

Name = str
Type = str
Element = str


class ItemDict(t.TypedDict, total=False):
    name: Required[Name]
    type: Required[Type]
    element: Required[Element]
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
    version: str
    key: str
    name: str
    description: str
    items: list[ItemDict]


TIER_KEYS = (
    "common",
    "max_common",
    "rare",
    "max_rare",
    "epic",
    "max_epic",
    "legendary",
    "max_legendary",
    "mythical",
    "max_mythical",
    "divine",
)
TYPE_ORDER = {"TORSO": 0, "LEGS": 1, "DRONE": 2, "SIDE_WEAPON": 3, "TOP_WEAPON": 4, "MODULE": 5}


def load_json(file: io.TextIOWrapper) -> t.Any:
    import json

    return json.load(file)
