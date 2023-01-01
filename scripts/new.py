import bisect
import io
import typing as t
import csv

from typing_extensions import Required

StatDict = dict[str, int | None | list[int] | list[None]]


Name = str
Type = str
Element = str
State = t.Literal[0, 1, 2]


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
    items: list[ItemDict]


TIERS = ("common", "rare", "epic", "legendary", "mythical", "divine")
TIER_KEYS = tuple(
    key for tier in TIERS for key in ((tier, "max_" + tier) if tier != "divine" else (tier,))
)
TYPE_ORDER = {"TORSO": 0, "LEGS": 1, "DRONE": 2, "SIDE_WEAPON": 3, "TOP_WEAPON": 4, "MODULE": 5}
STATES = ("?", "-", "+")
NotPresent = 0
Missing = 1
Complete = 2


class ItemTuple(t.NamedTuple):
    name: Name
    type: Type
    element: Element
    state: list[State]

    def as_row(self) -> t.Iterator[str]:
        yield self.name
        yield self.type
        yield self.element

        for s in self.state:
            yield STATES[s]


def load_json(file: io.TextIOWrapper) -> t.Any:
    import json

    return json.load(file)


def dump_to_csv(
    file: io.TextIOWrapper, data: t.Iterable[t.Iterable[str]], column_names: t.Sequence[str] = ()
) -> None:
    writer = csv.writer(file, lineterminator="\n")
    if len(column_names) != 0:
        writer.writerow(column_names)
    writer.writerows(data)


def assert_tier_completeness(tier: StatDict) -> State:
    for _, value in tier.items():
        if value is None:
            return 1

        if isinstance(value, list):
            if any(x is None for x in value):
                return 1

    return 2


def main() -> None:
    with open("items.json") as file:
        data: ItemPack = load_json(file)

    items = data["items"]
    output: list[ItemTuple] = []

    for item_dict in items:
        state: list[State] = [NotPresent] * len(TIER_KEYS)

        for state_index, tier_name in enumerate(TIER_KEYS):
            tier_data: StatDict | None = item_dict.get(tier_name)

            if tier_data is None:
                continue

            state[state_index] = assert_tier_completeness(tier_data)

        # if any(v == Missing for v in state):
        #     pass

        bisect.insort(
            output,
            ItemTuple(item_dict["name"], item_dict["type"], item_dict["element"], state),
            key=lambda t: (TYPE_ORDER.get(t.type, 6), t.name, t.element)
        )

    with open("out.csv", "w") as file:
        column_names = ["name", "type", "element"]
        column_names += TIER_KEYS

        dump_to_csv(file, map(ItemTuple.as_row, output), column_names)


if __name__ == "__main__":
    main()