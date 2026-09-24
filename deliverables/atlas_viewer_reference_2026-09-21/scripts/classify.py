"""아틀라스 노드를 하코 위험도로 분류한다(poe.ninja stat id 기준)."""
import json, re
d = json.load(open('ninja/atlas_tree.json', encoding='utf-8')); N = d['nodes']
DANGER = re.compile(r'(?<!per_)monster_modifier|monster_additional_modifier|map_mod_effect|modifier_cap|modifier_min|effectiveness|potency|empowered|deadly_boss|double_boss|powerful_map_boss|boss_additional_modifier|difficulty_selector|undead_overrun|invaded|rare_monster_replaced_by_random_map_boss|upgrade_nearby_map_boss|citadel_boss')
MORE = re.compile(r'rogue_exile_chance|rogue_exiles_chance|contains_rogue_exiles|extra_rare_beasts|tormented_spirit_chance|tormented_spirits_maximum_power|boss_area_chance_to_be_corrupted|number_of_rare_packs|number_of_magic_packs|additional_rare_in_rare_pack|duplicate_x_rare|pack_size|sanctified_packs|(?<!rarity_)(?<!rarity_permyriad_if_)possessed(?!_)|additional_packs|all_packs_are_magic|doubled|guarded_by_rare|chance_to_be_rare|chance_to_be_magic|summon')
def cat(nid):
    n = N[nid]; s = ' '.join(x['id'] for x in n['stats'])
    if n.get('isKeystone'): return '선택형'
    if n.get('isRootOfAtlasTree'): return '시작점'
    if re.search(r'rarity_\S*if_possessed|rarity_permyriad_if_possessed', s) and not DANGER.search(s): return '안전'
    if DANGER.search(s): return '위험'
    if MORE.search(s): return '주의'
    return '안전'
def show(nid):
    n = N[nid]; return f"{n['name']} [{cat(nid)}] " + '; '.join(f"{x['id']} {x['v']}" for x in n['stats'])
