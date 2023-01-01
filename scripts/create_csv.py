import bisect
import csv
import io
import typing as t

from shared import Element, ItemPack, Name, StatDict, Type, TIER_KEYS, TYPE_ORDER

State = t.Literal[0, 1, 2]

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
            return Missing

        if isinstance(value, list):
            if any(x is None for x in value):
                return Missing

    return Complete


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

        bisect.insort_right(
            output,
            ItemTuple(item_dict["name"], item_dict["type"], item_dict["element"], state),
            key=lambda t: (TYPE_ORDER.get(t.type, 6), t.name, t.element),
        )

    with open("out.csv", "w") as file:
        column_names = ["name", "type", "element"]
        column_names += TIER_KEYS

        dump_to_csv(file, map(ItemTuple.as_row, output), column_names)


if __name__ == "__main__":
    main()
