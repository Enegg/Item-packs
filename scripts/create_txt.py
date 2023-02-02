import bisect
import operator
import typing as t
from collections import Counter
from itertools import chain, compress

from shared import TIER_KEYS, TYPE_ORDER, ItemPack, Name, StatDict, load_json


def join_dict(mapping: t.Mapping[t.Any, t.Any]) -> str:
    return ", ".join(f"{key}: {value}" for key, value in mapping.items())


def iter_two_dicts(mapping1: t.Mapping[str, int], mapping2: t.Mapping[str, int]) -> t.Iterator[tuple[str, int, int]]:
    for key, value in mapping1.items():
        yield key, value, mapping2.get(key, 0)


def main() -> None:
    with open("items.json") as file:
        data: ItemPack = load_json(file)

    items = data["items"]

    types_missing_stats = Counter[str]()
    types_finished_stats = Counter[str]()
    tiers_missing_stats = Counter[str]()

    items_with_missing_tiers_ordered_by_type: list[list[tuple[Name, list[bool]]]] = [
        [] for _ in range(len(TYPE_ORDER) + 1)
    ]

    for item in items:
        missing_tier_selectors = [False] * len(TIER_KEYS)

        for n, tier_name in enumerate(TIER_KEYS):
            tier: StatDict | None = item.get(tier_name)

            if tier is None:
                continue

            for stat, value in tier.items():
                if value is None or isinstance(value, list) and any(x is None for x in value):
                    missing_tier_selectors[n] = True
                    break

        if any(missing_tier_selectors):
            types_missing_stats[item["type"]] += 1
            tiers_missing_stats.update(compress(TIER_KEYS, missing_tier_selectors))

            index = TYPE_ORDER.get(item["type"], -1)

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
        any(item[1][n] for item in items_with_missing_tiers) for n in range(len(TIER_KEYS))
    ]

    lines = [
        header := " | ".join(
            chain((f"{'item name':<{longest_name_length}}",), compress(TIER_KEYS, column_exists))
        ),
        spacer := "-" * len(header),
    ]

    for type_list in items_with_missing_tiers_ordered_by_type:
        for item_name, selectors in type_list:
            string = f"{item_name:<{longest_name_length}} | "
            string += " | ".join(
                f"{'-' * exists:<{len(tier)}}"
                for tier, exists in compress(zip(TIER_KEYS, selectors), column_exists)
            ).rstrip()
            lines.append(string)

        if type_list:
            lines.append(spacer)

    with open("out.txt", "w") as file:
        file.write("\n".join(lines))

    all_types = types_finished_stats.copy()
    all_types.update(types_missing_stats)
    stuff = iter_two_dicts(all_types, types_finished_stats)

    print(
        f"Total items: {len(items)}",
        ", ".join(f"{key}: {v2}/{v1}" for key, v1, v2 in stuff),
        f"Missing tiers: {join_dict(tiers_missing_stats)}",
        sep="\n",
    )


if __name__ == "__main__":
    main()
