import bisect
import json
import operator
import typing as t
from collections import Counter
from itertools import compress, chain
from typing import TypedDict

from typing_extensions import Required

StatDict = dict[str, int | None | list[int] | list[None]]


class ItemDict(TypedDict, total=False):
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


with open("items.json") as file:
    data: ItemPack = json.load(file)

items = data["items"]
tiers = ("common", "rare", "epic", "legendary", "mythical", "divine")
types_order = ("TORSO", "LEGS", "DRONE", "SIDE_WEAPON", "TOP_WEAPON", "MODULE")

types_missing_stats = Counter[str]()
types_finished_stats = Counter[str]()
tiers_missing_stats = Counter[str]()

# list[<0: TORSO>list[tuple[<name>str, <selectors>list[bool]]], ...]
items_with_missing_tiers_ordered_by_type: list[list[tuple[str, list[bool]]]] = [[] for _ in range(len(types_order) + 1)]

tiers_with_max = tuple(
    key for tier in tiers for key in ((tier, "max_" + tier) if tier != "divine" else (tier,))
)

for item in items:
    missing_tier_selectors = [False] * len(tiers_with_max)

    for n, tier_name in enumerate(tiers_with_max):
        tier: StatDict | None = item.get(tier_name)

        if tier is None:
            continue

        for stat, value in tier.items():
            if value is None or isinstance(value, list) and any(x is None for x in value):
                missing_tier_selectors[n] = True
                break

    if any(missing_tier_selectors):
        types_missing_stats[item["type"]] += 1
        tiers_missing_stats.update(compress(tiers_with_max, missing_tier_selectors))

        index = -1 if item["type"] not in types_order else types_order.index(item["type"])

        bisect.insort(
            items_with_missing_tiers_ordered_by_type[index],
            (item["name"], missing_tier_selectors),
            key=operator.itemgetter(0),
        )

    else:
        types_finished_stats[item["type"]] += 1

items_with_missing_tiers = list(chain.from_iterable(items_with_missing_tiers_ordered_by_type))
sorted_item_names = [item_name for item_name, _ in items_with_missing_tiers]
longest_name_length = max(map(len, sorted_item_names))

# exclude completed tiers
column_exists = [
    any(item[1][n] for item in items_with_missing_tiers) for n in range(len(tiers_with_max))
]

lines = [
    header := " | ".join(
        chain((f"{'item name':<{longest_name_length}}",), compress(tiers_with_max, column_exists))
    ),
    spacer := "-" * len(header),
]

for type_list in items_with_missing_tiers_ordered_by_type:
    for item_name, selectors in type_list:
        string = f"{item_name:<{longest_name_length}} | "
        string += " | ".join(
            f"{'-' * exists:<{len(tier)}}"
            for tier, exists in compress(zip(tiers_with_max, selectors), column_exists)
        )
        lines.append(string)
    lines.append(spacer)

def join_dict(mapping: t.Mapping[t.Any, t.Any]) -> str:
    return ", ".join(f"{key}: {value}" for key, value in mapping.items())


with open("out.txt", "w") as file:
    print(
        f"Total items: {len(items)}",
        f"Done: {join_dict(types_finished_stats)}",
        f"Pending: {join_dict(types_missing_stats)}",
        f"Missing tiers: {join_dict(tiers_missing_stats)}",
        sep="\n",
    )
    file.write("\n".join(lines))
