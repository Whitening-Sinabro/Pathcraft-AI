"""Generate and sweep the three POE2 filters from one audited specification."""
from pathlib import Path
import contextlib,hashlib,importlib.util,io,json,sys
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[1];OUT=HERE/'revision3/Filters'
def module(name,file):
    s=importlib.util.spec_from_file_location(name,REPO/'scripts'/file);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
spec=json.loads((HERE/'filter_spec.json').read_text(encoding='utf-8'))
spec['rules']=[r for r in spec['rules'] if r.get('class')!=['Two Hand Maces']]
spec['_meta']['notes'].append('v3 방송 대조: 한손 철퇴+방패 경로. 양손 철퇴 전용 추가 강조 7개를 제거하고 해당 아이템은 NeverSink 원본으로 처리.')
(HERE/'filter_spec_v3.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2),encoding='utf-8')
builder=module('v3_overlay','build_poe2_build_overlay.py');builder.GAME_CLASS_TO_FILTER_CLASS['Sceptres']='Sceptres'
sweep=module('v3_sweep','poe2_filter_sweep.py');sweep.GAME_CLASS_TO_FILTER_CLASS['Sceptres']='Sceptres';ev=sweep.load_eval()
report=[];log=io.StringIO()
for stage,base,label in [('campaign','soft','01-Campaign'),('maps','regular','02-EarlyMaps'),('endgame','strict','03-SettledMaps')]:
    src=HERE/'sources'/f'neversink_0.10.4_{base}.filter';text=src.read_text(encoding='utf-8');blocks=builder.parse_base_blocks(text);classes=builder.class_index(text)
    sceptres={b for r in spec['rules'] if r.get('class')==['Sceptres'] for b in r['base_types']};classes.update({b:'Sceptres' for b in sceptres})
    vocab=builder.base_vocabulary(text)|builder.game_base_names()|sceptres;style_values=builder.base_value_vocabulary(text)
    for key,style in spec['styles'].items():builder.check_contrast(key,style);builder.check_style_values(key,style,style_values)
    added=[]
    for r in spec['rules']:
        if stage not in r['stages']:continue
        assert set(r['base_types'])<=vocab
        generated,_,_=builder.build_rule_blocks(r,spec['styles'][r['style']],blocks,classes);added+=generated
    header=f'# Pathcraft Skadoosh HC 0.5.5 | v3 | {label} | NeverSink 0.10.4\n# Manual progression switch. Campaign includes character level 65+.\n# One-hand mace / shield / spirit targets. Added rules only Show.\n\n'
    dest=OUT/f'Pathcraft-Skadoosh-HC-{label}.filter';dest.write_text(header+'\n\n'.join(added)+'\n\n'+text,encoding='utf-8',newline='\n')
    assert dest.read_text(encoding='utf-8').endswith(text)
    own=ev.parse(sweep.overlay_only(dest));assert not ev.unmodelled_conditions(own);assert all(b.action=='Show' for b in own)
    assert 'Two Hand Maces' not in '\n\n'.join(added)
    with contextlib.redirect_stdout(log):bad=sweep.sweep(src,dest,True)
    assert bad==0,(label,bad)
    before=ev.load(src);after=ev.load(dest);samples=0
    for area in [35,50,52,60,65,70,80]:
        for bt,cls,rarity in [('Shrine Sceptre','Sceptres','Rare'),('Solar Amulet','Amulets','Rare'),('Morning Star','One Hand Maces','Rare'),('Amethyst Charm','Charms','Magic')]:
            if bt=='Morning Star' and area>60:continue
            assert ev.evaluate(after,ev.Item(bt,cls,rarity,area_level=area,item_level=area)).visible;samples+=1
    controls=0
    for bt,cls in [('Flanged Mace','One Hand Maces'),('Shrine Sceptre','Sceptres'),('Ruby','Jewels')]:
        for area in [35,65,80]:
            item=ev.Item(bt,cls,'Unique',area_level=area,item_level=area);a=ev.evaluate(before,item);b=ev.evaluate(after,item)
            assert (a.visible,a.font,a.volume,a.sound_id,a.icon_size)==(b.visible,b.font,b.volume,b.sound_id,b.icon_size);controls+=1
    report.append({'file':dest.name,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'base_tail_exact':True,'new_hide_rules':0,'sweep_regressions':bad,'progression_samples':samples,'unique_controls':controls,'removed_two_hand_priority_rules':7,'unmodelled_base_conditions':ev.unmodelled_conditions(before)})
(HERE/'filter_sweep_v3.txt').write_text(log.getvalue(),encoding='utf-8')
(HERE/'validation_filters_v3.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('PASS: 3 filters, full supported-state sweep, spirit/one-hand targets, original base tails.')
