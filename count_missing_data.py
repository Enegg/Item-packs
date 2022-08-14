from collections import Counter
import json
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


with open("items.json") as file:
    data: list[ItemDict] = json.load(file)

types_missing_stats = Counter[str]()
types_finished_stats = Counter[str]()
items_with_missing_tiers = dict[str, list[str]]()

tiers = ("common", "rare", "epic", "legendary", "mythical", "divine")



tiers_with_max = tuple(key for tier in tiers for key in ((tier, "max_" + tier) if tier != "divine" else (tier,)))

for item in data:
    missing_tiers = list[str]()

    for tier in (
        key2
        for key in tiers
        for key2 in ((key, "max_" + key) if key != "divine" else (key,))
        if key2 in item
    ):
        for stat, value in item[tier].items():
            if value is None:
                missing_tiers.append(tier)
                break

            elif isinstance(value, list) and any(x is None for x in value):
                missing_tiers.append(tier)
                break

    if missing_tiers:
        types_missing_stats[item["type"]] += 1
        items_with_missing_tiers[item["name"]] = missing_tiers

    else:
        types_finished_stats[item["type"]] += 1

with open("out.txt", "w") as file:
    print(f"Total: {len(data)}", "Done:", types_finished_stats, "Pending:", types_missing_stats, sep="\n", file=file)
    print("\n".join(f"{name}: {missing}" for name, missing in items_with_missing_tiers.items()), file=file)
