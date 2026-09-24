"""Build the two map extensions; audit the untouched creator campaign filter."""
from pathlib import Path
from dataclasses import dataclass
import contextlib, hashlib, importlib.util, io, json, logging, re, sys

sys.stdout.reconfigure(encoding='utf-8')
logging.disable(logging.INFO)
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUT = HERE / 'Filters'
OUT.mkdir(exist_ok=True)

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, REPO/'scripts'/filename)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

builder = module('arserina_overlay', 'build_poe2_build_overlay.py')
sweep = module('arserina_sweep', 'poe2_filter_sweep.py')
ev = sweep.load_eval()
# Extend only this verification process. No shared evaluator files are changed.
ev.NUMERIC_FIELDS['GemLevel'] = 'gem_level'
ev.NUMERIC_CONDITIONS.add('GemLevel')
@dataclass
class GemItem(ev.Item):
    gem_level: int = 1
ev.Item = GemItem

spec = read(HERE/'filter_spec.json')
pins = {x['stage']: x for x in read(HERE/'sources/filter_sources.json')['sources']}
creator = HERE/'sources/Arserina-POE2-Act-original.filter'
metadata = read(HERE/'sources/arserina_filter_metadata.json')
assert metadata['id'] == 'qOlkq0TV'
assert metadata['owner'] == 'Arserina#5429'
assert metadata['validation']['valid'] is True
campaign = OUT/'Arserina-01-POE2-Act.filter'
campaign.write_bytes(creator.read_bytes())
assert digest(campaign) == digest(creator)
game = Path.home()/'Documents/My Games/Path of Exile 2'
sounds = sorted(set(re.findall(r'^\s*CustomAlertSound(?:Optional)?\s+"([^"]+)"',
                             creator.read_text(encoding='utf-8'), re.M)))
sound_checks = []
for sound in sounds:
    path = game/sound
    assert path.is_file() and path.stat().st_size > 100, f'Missing sound: {sound}'
    sound_checks.append({'file': sound, 'sha256': digest(path), 'bytes': path.stat().st_size})

report = {'creator_campaign': {'file': campaign.name, 'sha256': digest(campaign),
          'unchanged_from_creator': True, 'source': spec['_meta']['creator_filter'],
          'version': metadata['version'], 'server_validation': metadata['validation'],
          'sound_files': sound_checks}, 'maps': [], 'game_runtime_verified': False}
log = io.StringIO()
for stage in spec['_meta']['stages']:
    key = stage['stage']
    source = HERE/'sources'/f"neversink_0.10.4_{stage['base']}.filter"
    assert digest(source) == pins[stage['base']]['sha256']
    base_text = source.read_text(encoding='utf-8')
    parsed = builder.parse_base_blocks(base_text)
    classes = builder.class_index(base_text)
    vocab = builder.base_vocabulary(base_text) | builder.game_base_names()
    for name, style in spec['styles'].items():
        builder.check_contrast(name, style)
        builder.check_style_values(name, style, builder.base_value_vocabulary(base_text))
    generated = []
    for rule in spec['rules']:
        if key not in rule['stages']:
            continue
        assert rule.get('kind', 'show') == 'show'
        assert set(rule['base_types']) <= vocab, set(rule['base_types'])-vocab
        assert set(rule.get('class', [])) <= vocab
        blocks, _, _ = builder.build_rule_blocks(rule, spec['styles'][rule['style']], parsed, classes)
        generated.extend(blocks)
    header = (f"# Pathcraft Arserina SC | {key} | NeverSink 0.10.4\n"
              "# Pathcraft map extension. This is NOT a filter published by Arserina.\n"
              "# Arserina campaign original: https://pathofexile2.com/item-filter/qOlkq0TV\n"
              "# Added rules only Show; the unchanged NeverSink base retains its Hide rules.\n"
              "# Manual switch: campaign completion -> early maps -> settled equipment.\n\n")
    target = OUT/stage['file']
    target.write_text(header+'\n\n'.join(generated)+'\n\n'+base_text, encoding='utf-8', newline='\n')
    own = ev.parse(header+'\n\n'.join(generated))
    assert all(b.action == 'Show' for b in own)
    assert not ev.unmodelled_conditions(own)
    assert target.read_bytes().endswith(source.read_bytes())
    assert 'CustomAlertSound' not in target.read_text(encoding='utf-8')
    with contextlib.redirect_stdout(log):
        bad = sweep.sweep(source, target, True)
    assert bad == 0, (key, bad)
    before, after = ev.load(source), ev.load(target)
    required = [('Chiming Staff','Staves','Normal'),('Chiming Staff','Staves','Rare'),
        ('Bombard Crossbow','Crossbows','Normal'),('Cannonade Crossbow','Crossbows','Magic'),
        ('Ruby','Jewels','Magic'),('Ruby Ring','Rings','Rare'),('Topaz Ring','Rings','Rare'),
        ('Gold Amulet','Amulets','Rare'),('Utility Belt','Belts','Rare'),
        ('Conqueror Plate','Body Armours','Unique'),('Ultimate Life Flask','Life Flasks','Magic'),
        ('Ultimate Mana Flask','Mana Flasks','Magic'),('Thawing Charm','Charms','Magic'),
        ('Stone Charm','Charms','Magic'),('Silver Charm','Charms','Magic'),
        ("Gemcutter's Prism",'Stackable Currency','Normal'),
        ("Greater Jeweller's Orb",'Stackable Currency','Normal'),
        ("Perfect Jeweller's Orb",'Stackable Currency','Normal'),
        ('Perfect Essence of Sorcery','Stackable Currency','Normal'),
        ('Greater Desert Rune','Augment','Normal'),('Rune of Vitality','Augment','Normal'),
        ('Ancient Rune of Detonation','Augment','Normal'),
        ("Hedgewitch Assandra's Rune of Wisdom",'Augment','Normal')]
    samples = 0
    for base, cls, rarity in required:
        for area in [52,64,65,70,75,80,82]:
            item = ev.Item(base,cls,rarity,area_level=area,item_level=max(75,area))
            assert ev.evaluate(after,item).visible, (key,base,area)
            samples += 1
    # Verify required support grades and skill/spirit gems, including boundaries
    # where NeverSink changes their alerts. GemLevel is modelled here explicitly.
    gem_checks = 0
    for base, cls, levels in [('Uncut Support Gem','Stackable Currency',[1,2,3,4,5]),
                             ('Uncut Skill Gem','Stackable Currency',[10,13,14,17,18,19,20]),
                             ('Uncut Spirit Gem','Stackable Currency',[10,13,14,17,18,19,20])]:
        for level in levels:
            for area in [52,64,65,70,78,79,80,82]:
                item = GemItem(base,cls,area_level=area,item_level=area,gem_level=level)
                a,b = ev.evaluate(before,item),ev.evaluate(after,item)
                assert b.visible, (key,base,level,area)
                assert (a.visible,a.font,a.volume,a.sound_id,a.icon_size) == (b.visible,b.font,b.volume,b.sound_id,b.icon_size)
                gem_checks += 1
    # Control gem levels prove the extension is actually evaluated, not ignored.
    assert ev.evaluate(after,GemItem('Uncut Skill Gem',gem_level=20,area_level=82)).sound_id == 6
    assert ev.evaluate(after,GemItem('Uncut Skill Gem',gem_level=13,area_level=82)).sound_id != 6
    controls = 0
    for base,cls,rarity in [('Divine Orb','Stackable Currency','Normal'),
                          ('Mirror of Kalandra','Stackable Currency','Normal'),
                          ('Ruby','Jewels','Unique'),('Chiming Staff','Staves','Unique'),
                          ('Gold Amulet','Amulets','Unique'),('Waystone','Waystones','Rare')]:
        for area in [65,75,82]:
            item=ev.Item(base,cls,rarity,area_level=area,item_level=area)
            a,b=ev.evaluate(before,item),ev.evaluate(after,item)
            assert (a.visible,a.font,a.volume,a.sound_id,a.icon_size)==(b.visible,b.font,b.volume,b.sound_id,b.icon_size)
            controls += 1
    # Late armour protection starts at its declared ilvl. The shared builder must
    # not silently drop that bound when it adds conditional loudness variants.
    if key == 'endgame':
        relevant = [b for b in own if any(k=='BaseType' and 'Champion Helm' in v for k,o,v in b.conditions)]
        assert relevant
        low=ev.Item('Champion Helm','Helmets','Rare',area_level=82,item_level=74)
        high=ev.Item('Champion Helm','Helmets','Rare',area_level=82,item_level=75)
        assert not any(ev.matches(b,low) for b in relevant)
        assert any(ev.matches(b,high) for b in relevant)
    report['maps'].append({'file':target.name,'sha256':digest(target),'base_sha256':digest(source),
        'base_tail_exact':True,'new_hide_rules':0,'sweep_regressions':bad,
        'required_drop_checks':samples,'gem_checks':gem_checks,'unchanged_value_controls':controls,
        'unmodelled_base_conditions':ev.unmodelled_conditions(before)})
    print('Verified',target.name,flush=True)
(HERE/'filter_sweep.txt').write_text(log.getvalue(),encoding='utf-8')
(HERE/'filter_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS: creator original + 2 map extensions; 17 installed sound references; gem levels modelled.')
