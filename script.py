import json

mode = int(input('Select mode: 0 - reloaded items, 1 - legacy: '))
if mode not in {0, 1}:
    raise ValueError('Mode must be of range {0, 1}')

print('***If there\'s [x] before input field, you can press enter to use the x as default***')

path_to_file = ('items.json', 'legacy_items.json')[mode]
with open(path_to_file) as file:
    item_list = json.loads(file.read())

#lookup tables
elements = {'p': 'PHYSICAL', 'h': 'EXPLOSIVE', 'e': 'ELECTRIC', 'c': 'COMBINED'}
types = {'tors': 'TORSO', 'legs': 'LEGS', 'side': 'SIDE_WEAPON', 'top': 'TOP_WEAPON', 'mod': 'MODULE', 'dron': 'DRONE', 'tele': 'TELEPORTER', 'hook': 'HOOK', 'char': 'CHARGE'}
all_stats = ('weight', 'health', 'eneCap', 'eneReg', 'heaCap', 'heaCol', 'push', 'pull', 'recoil', 'advance', 'retreat', 'range', 'walk', 'jump', 'uses', 'backfire')
resistance = ('phyRes', 'expRes', 'eleRes')
physical = ('phyDmg', 'phyResDmg')
explosive = ('expDmg', 'heaDmg', 'expResDmg', 'heaCapDmg', 'heaColDmg')
electric = ('eleDmg', 'eneDmg', 'eleResDmg', 'eneCapDmg', 'eneRegDmg')
cost = ('eneCost', 'heaCost')
divineable = {'health', 'eneCap', 'eneReg', 'heaCap', 'heaCol', 'phyDmg', 'expDmg', 'heaDmg', 'eleDmg', 'eneDmg'}
type_reference = {'SIDE_WEAPON': 'WEAPON', 'TOP_WEAPON': 'WEAPON', 'DRONE': 'WEAPON', 'HOOK': 'SPECIAL', 'TELEPORTER': 'SPECIAL', 'CHARGE': 'SPECIAL'}
what_to_ask_for = {
    'TORSO': (1, 2, 3, 4, 5, resistance),
    'LEGS': (1, [physical, explosive, electric], 6, 11, 12, 13),
    'WEAPON': ([physical, explosive, electric], 6, 7, *((8, 9, 10) if mode == 0 else ()), 11, 14, *((15,) if mode == 0 else ()), cost),
    'MODULE': (1, 2, 3, 4, 5, list(resistance)),
    'SPECIAL': ([physical, explosive, electric], 6, 11, cost)}

last_type, last_elem, last_tier, last_price = '', '', '', 0
_type, elem, tier, price, level = '', '', '', 0, 1
last_id = item_list[-1]['id'] if not mode else 0
tr = ''

while True:
    item = {}
    if not mode:
        last_id += 1
        item['id'] = last_id

    item['name'] = input('Name: ')

    _type = input(f'{"[" + last_type + "] " if last_type else ""}Type: ').lower() or _type
    item['type'] = last_type = types.get(_type, 'undefined')

    elem = input(f'{"[" + last_elem + "] " if last_elem else ""}Element [PHEC]: ')[:1].lower() or elem
    item['element'] = last_elem = elements.get(elem, 'undefined')

    if mode:
        tier = input(f'{"[" + tier + "] " if tier else ""}Tier [CRELM]: ')[:1].upper() or tier
        item['transform_range'] = tier if tier in 'CRELM' else 'C'

        level = input(f'[{level}] Level [1-30]: ') or level
        item['level'] = int(level)

        if item['transform_range'] in 'CRE':
            price = input(f'[{last_price}] Price: ')
            if price:
                if price == 'l': price = last_price
                item['price'] = last_price = int(price)

    else:
        tr = input(f'{"[" + last_tier + "] " if last_tier else ""}Transform range [CRELMD][ CRELMD]: ').replace('-', '').upper() or tr
        item['transform_range'] = last_tier = f'{tr[0]}-{tr[1] if len(tr) > 1 else tr[0]}'

    stats = {}
    divine = {}
    stats_to_ask_for = [0]
    item_type = str(item['type'])
    item_elem = str(item.get('element', ''))
    is_divine = item['transform_range'].endswith('D')
    item_type = type_reference.get(item_type, item_type)
    stats_to_ask_for.extend(what_to_ask_for.get(item_type, []))

    for key in stats_to_ask_for:
        if isinstance(key, int):
            stat = all_stats[key]
            value = input(stat + ': ')
            if not value: continue
            value = [int(x) for x in value.split('-')] if '-' in value else int(value)
            stats[stat] = value

            if not is_divine or stat not in divineable: continue
            value = input(stat + ' (divine): ')
            if not value: continue
            value = [int(x) for x in value.split('-')] if '-' in value else int(value)
            divine[stat] = value

        if isinstance(key, list):
            if item_elem == 'COMBINED': key = tuple(key)
            else: key = key[('PHYSICAL', 'EXPLOSIVE', 'ELECTRIC').index(item_elem)] if item_elem else 'PHYSICAL'

        if isinstance(key, tuple):
            text = '/'.join(key)
            values = input(text + ': ').split('/')
            if not values[0]: continue
            stats.update({x[0]: ([int(n) for n in x[1].split('-')] if '-' in x[1] else int(x[1])) for x in zip(key, values) if x[1] != '0'})

            if not is_divine or stat not in divineable: continue
            values = input(text + ' (divine)' + ': ').split('/')
            if not values[0]: continue
            divine.update({x[0]: ([int(n) for n in x[1].split('-')] if '-' in x[1] else int(x[1])) for x in zip(key, values) if x[1] != '0'})

    item['stats'] = stats
    if is_divine and divine: item['divine'] = divine
    print(json.dumps(item, indent=4))
    confirm = input('Save? [Y/N] ').upper()
    if bool(('N', 'Y').index(confirm) if confirm in {'Y', 'N'} else False):
        item_list.append(item)
        with open(path_to_file, 'wt') as file:
            file.write(json.dumps(item_list, indent=4))
    else: last_id -= 1

    confirm = input('Continue? [Y/N] ').upper()
    if bool(('Y', 'N').index(confirm) if confirm in {'Y', 'N'} else False):
        exit()