"""Assemble only this new corpus; preserve original worker submissions."""
import csv, json, shutil, sys
from pathlib import Path
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parent
BASE = ROOT.parents[2]
def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
records, sources = [], []
for short, folder in [('current','poe2-corpus-current-20260921'),('guides','poe2-corpus-guides-20260921')]:
    src = BASE / folder / 'deliverables' / ROOT.name / 'worker_output'
    dst = ROOT / 'worker_submissions' / short
    dst.mkdir(parents=True, exist_ok=True)
    for name in ['records.json','sources.jsonl','notes.md','report.md']:
        shutil.copy2(src/name, dst/name)
    records += json.loads((dst/'records.json').read_text(encoding='utf-8'))
    sources += [json.loads(x) for x in (dst/'sources.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
manager_sources = [json.loads(x) for x in (ROOT/'manager_sources.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
for s in manager_sources:
    s['published_at_raw'] = s['published_at']
    s['published_at'] = '2026-08-31'
    s['date_precision_note'] = 'Publication day retained; page timezone not established.'
sources += manager_sources
by = {r['id']:r for r in records}
sb = {s['source_id']:s for s in sources}
family_map = {'ice_shot':('ice-shot','Ice Shot'), 'plant_coc':('plants','Plants / Cast on Critical'),
              'grim_pillar_totem':('spell-totems','Spell Totems'), 'spark_totem':('spell-totems','Spell Totems'),
              'twister':('twister','Twister'), 'plants':('plants','Plants / Cast on Critical'),
              'ice-shot':('ice-shot','Ice Shot')}
for r in records:
    r['game']='POE2'
    r['original_family_id']=r['family_id']
    r['family_id'],r['family_name']=family_map.get(r['family_id'],(r['family_id'].replace('_','-'),r['family_name']))
    r['configuration_scope']='One opened guide/overview configuration sample; not every interactive variant selected.'
    r['league_evidence']={'page_badge':'0.5.5 FR','interpretation':'Forbidden Rites site label; body contemporaneity not guaranteed','source_id':r['source_ids'][0]}
    r['approval_status']='collected_not_game_validated'
    if r['league'] is None:
        r['league']='Forbidden Rites (site badge only; body applicability unverified)'
    p=r['popularity']
    if p['type'] in ('page_favorites_display','guide_favorites'):
        p['type']='guide_favorites'
    p['population_usage_inferred']=False
    r['field_provenance']={k:{'source_id':r['source_ids'][0], 'locator':sb[r['source_ids'][0]]['locator'], 'kind':'creator_claim'} for k in ['main_skills','damage_structure','defense_structure','resource_constraints','patch_sensitive_dependencies']}
    r['gaps_conflicts'].append('This is an opened-text sample, not a complete playable specification or archived patch snapshot.')

def skill(rid,name,supports,loc):
    r=by[rid]; r['skills'].append(dict(name=name,supports=supports,source_id=r['source_ids'][0],locator=loc))
def stage(rid,name,conditions,skills,transition,loc):
    r=by[rid]; r['stages'].append(dict(name=name,conditions=conditions,skills=skills,gear=[],transition=transition,source_id=r['source_ids'][0],locator=loc))
def gear(rid,name,role,condition,loc):
    r=by[rid]; r['equipment'].append(dict(name=name,role=role,condition=condition,source_id=r['source_ids'][0],locator=loc))
def claim(rid,text,loc):
    r=by[rid]; r['claims'].append(dict(id=rid+'-manager-'+str(len(r['claims'])+1),text=text,kind='creator_claim',source_id=r['source_ids'][0],locator=loc))

r=by['w2-minions']; loc='Skill Gems / Gem Priority L302-320; How it Plays L481-489'
r['main_skills']=['Skeletal Sniper','Raging Spirits','Flame Wall','Frost Bomb']
skill(r['id'],'Skeletal Sniper',['Multishot I','Fire Attunement'],loc)
skill(r['id'],'Raging Spirits',['Fire Attunement','Last Gasp'],loc)
skill(r['id'],'Flame Wall',['Rapid Casting I'],loc)
stage(r['id'],'Early minions',['Mud Burrow completed; level-2 skill gem and support gem'],['Skeletal Sniper'],'Cut Sniper and socket Multishot I.',loc)
stage(r['id'],'Spirit transition',['Freythorn completed; Raging Spirits acquired'],['Raging Spirits','Flame Wall'],'Remove Essence Drain; summon spirits with Flame Wall during Gas Arrow cooldown.',loc)
r['resource_constraints'] += ['Displayed Act1 support attributes: Str10 / Dex5 / Int10; not whole-build final requirements.','Vaal Guard spectre costs 50 Spirit per creator.']
r['damage_structure']='Sniper Gas Arrow with Flame Wall ignition; Raging Spirits summoned during cooldowns (creator advice).'
r['retrieval_status']='deep_stage_extracted'
r['field_provenance']['main_skills']['locator']=loc
r['field_provenance']['damage_structure']['locator']=loc
claim(r['id'],'Sniper+Multishot after Mud Burrow; Raging Spirits after Freythorn replaces Essence Drain.',loc)
sb['w2-s06']['retrieval_status']='deep_stage_extracted'
sb['w2-s06']['locator'] += '; manager Skill Gems / Gem Priority L302-320 and How it Plays L481-489'
sb['w2-s06']['summary'] += ' Manager added omitted core skills/supports and two concrete quest/gem transitions.'

# Small factual repairs found during the original-page review.
r=by['w1_afk']; r['stages'][0]['conditions'] += ['damage taken recouped as life >=80%','elemental damage taken recouped as life >=20%','physical damage taken recouped as life >=20%','damage taken from mana before life >=45%']
r['stages'][0]['transition']='Atziri set: place Frost Wall away; Widowhail set1: send Frostbolt toward wall; Atziri set2: add walls in projectile path; use Mirror of Refraction as described by creator.'
claim(r['id'],'Minimum-stat list also requires recoup thresholds and mana-before-life allocation, not life/ES/resists alone.','Minimum Stats L141-151; Starting the Loop L597-601')
by['w2-slam']['defense_structure']='Life, resistances, strength and armour priorities in Equipment L252-259.'
by['w2-slam']['field_provenance']['defense_structure']['locator']='Equipment L252-259'
by['w2-twister-far']['defense_structure']='Life/resistances on gear; movement speed on boots (Equipment L198-204).'
by['w2-twister-far']['field_provenance']['defense_structure']['locator']='Equipment L198-204'
gear('w2-twister-ap','Fast spear, empty offhand','required','Weapon set1 for Whirling Slash/Barrage attack-speed setup','Equipment / Weapon Sets L264-267')
gear('w2-twister-ap','Damage spear with shield, later sceptre','required','Weapon set2; replace shield after Act1','Equipment / Weapon Sets L264-267')
stage('w2-twister-ap','Weapon-set progression',['After Act1'],['Twister'],'Replace set2 shield with sceptre; keep set1 offhand empty.','Equipment / Weapon Sets L264-267')
# Kept detail-only: this extra stage was a bounded omission repair, not a new deep acceptance claim.
gear('w2-spark-ap','Lightning staff with spell levels and cast speed','example','Creator priority: levels > cast speed > increased damage > extra elemental damage','Equipment / Staff Stat Prio L275-283')
by['w2-spark-ap']['defense_structure']='Life plus Energy Shield and capped resistances early; later full ES per creator.'
by['w2-spark-ap']['field_provenance']['defense_structure']['locator']='Equipment L299-305'
by['w2-spark-ap']['resource_constraints'] += ['Mana fixes are alternatives, not all mandatory; Zenith II condition is staying at >=90% mana.']
by['w2-spark-ap']['field_provenance']['resource_constraints']['locator']='FAQ L663-665'
for rid in ['w2-snipe','w2-spark-big']:
    by[rid]['gaps_conflicts'].append('Manager checked Equipment section: retrieved item panels are image-only; no item names invented from those images.')

# Human grouping: core mechanics, not author, ascendancy, or leveling/endgame label.
families=defaultdict(list)
for r in records: families[r['family_id']].append(r['id'])
for r in records:
    related=[x for x in families[r['family_id']] if x!=r['id']]
    r['similarities_differences'] += ([{'kind':'manager_inference','related_record_ids':related,'text':'Shared core family; retain separate source/creator/ascendancy/stage configurations.','source_ids':list(dict.fromkeys(s for rid in families[r['family_id']] for s in by[rid]['source_ids']))}] if related else [])
family_review={'method':'Manager manual grouping by primary skill/mechanic; early shared leveling skills alone do not merge distinct endpoint builds.',
 'merges':['Ice Shot leveling/endgame','Plants leveling/CoC endgame','Twister across authors and ascendancies','Twisted Empyrean Lich/Titan','Spark self-cast guides','Oil Barrage Wyvern guides','Spell Totem Spark/Grim Pillars conservatively one broad family'],
 'kept_separate':['Self-cast Spark vs Spell Totems','Ignite Oil Grenade Flameblast vs cooldown Flameblast/Frostflame Nova','Grenade attacks vs grenade Ballista','Companions vs Djinn vs Witch minions','Shrine maces vs Twisted Empyrean mana maces vs generic slam leveling vs Shield Wall'],
 'families':[{'family_id':fid,'record_ids':ids} for fid,ids in sorted(families.items())]}
dump(ROOT/'family_review.json',family_review)

checks=json.loads((ROOT/'review_ledger.json').read_text(encoding='utf-8'))
# These terse facts were each read on original pages by this manager, not inferred from tab names.
facts={
 'w1_oil':('Build Overview L109-131; Equipment L232-234','52-level swap; reserve roughly30k gold and GCP/skill/support gems.'),
 'w1_plants':('Overview L122-134; Early Endgame L161-171','T1-7 early; comfortable T7 to T8/9; mana sustain governs Thunderstorm/Comet changes.'),
 'w1_ice':('How it Plays / Gear Progression L688-699','Crit bow/quiver before crit; about450ES helmet for hybrid.'),
 'w1_rue':('Overview / crit redesign L153-163','15-20div entry claim; Runeforged Double Vision; old flask strategy changed.'),
 'w1_beast':('Build Overview / Early Leveling','Level7 gem unlock differs from recommended Act3 after second lab; ~20k gold respec.'),
 'w1_grim':('Overview and Variants L136-141','Guide60+; Archmage above1500mana, EB around2500mana;395spirit target.'),
 'w1_spark_totem':('Overview L113-115; Equipment L226-233','Prospective Act2-end120spirit via3charm slots; alternative wait55-60.'),
 'w1_cold':('Leveling L149-168','Acquire Eye of Winter, replace Frost Darts; three supports stated.'),
 'w1_shrine':('Leveling / Respec to Mace L191-228','First Act2 boss around18; reserve gems; caster-to-mace passive changes.'),
 'w1_afk':('Minimum Stats L141-151; Starting Loop L597-601','All nine minimum thresholds preserved; wall/bolt setup uses explicit weapon sets.'),
 'w1_twister':('Overview L121-148; Movement Tech L958-964','Rigwald support gates faster-than-sprint movement; early-leveling tab still coming soon.'),
 'w2-ice':('Overview L113-117','Lightning Arrow/Rod until Ice Shot unlock31; linked endgame separate URL.'),
 'w2-arc':('How it Plays L514-522','Act2 Arc replaces ED/Contagion; elemental utility remains.'),
 'w2-grenade':('Gem Priority L272-286; How it Plays L445-448','Gas Grenade14; Multishot and Elemental Armament; explosive detonation.'),
 'w2-glacial':('Equipment L190-203; Passive Tree L346','Hollow Palm obtained: no weapon; no numeric unlock invented.'),
 'w2-varashta':('Overview; Variants L121-133; Equipment L214-226','Act2 ascendancy switch with level19 variant; +minion skill upgrade advice.'),
 'w2-minions':('Gem Priority L302-320; How it Plays L481-489','Mud Burrow Sniper/Multishot; Freythorn Spirits replace ED; supports extracted.'),
 'w2-edc':('Variants L119-129; Equipment L177-190','ED6; chaos set1/physical set2 from14; generic spell levels can serve both.'),
 'w2-slam':('Skill Rotation L150-176; Equipment L252-259','Before/after Perfect Strike changes boss rotation; Mace Strike remains alternative.'),
 'w2-twister-far':('Variants L154-158; Equipment L195-204','Optional Fangs of Frost6/firstlevel3gem; FrostBomb+IceNova remains alternative.'),
 'w2-plants':('Act1 checklist L144-160','Spiritgem4 RavenousSwarm+Corrosion; skillgem5 Bonestorm; not characterlevel4/5.'),
 'w2-shield':('Overview and Variants L114-150','ShieldWall22 replaces early slam; PerfectStrike14; VaalPact theory not tested.'),
 'w2-wyvern-gtd':('How it Plays L410-435','OilBarrage31; LingeringIllusion36 changes power-charge source.'),
 'w2-wyvern-peu':('Overview L111-143; Variants L170-184','OilBarrage31 boss; tier4supports clear; work-in-progress/prospective ascendancy.'),
 'w2-twister-ap':('Equipment / Weapon Sets L264-267','Filled missing equipment; spear set1 empty offhand, set2 shield to sceptre afterAct1.'),
 'w2-spark-ap':('Equipment L275-305; FAQ L663-665','Filled staff priorities/defense and optional mana fixes; no numeric CI gate invented.'),
 'w2-snipe':('Equipment L123-234','No textual item names in retrieved equipment panel; gap retained.'),
 'w2-spark-big':('Equipment L194-267','No textual item names in retrieved equipment panel; gap retained.')}
checks['checks']=[]
for rid,(loc,fact) in facts.items():
    checks['checks'].append({'record_id':rid,'url':by[rid]['url'],'opened_at':'2026-09-21','method':'manager web.run original-page open/find','locator':loc,'page_facts':[fact],'record_comparison':'accepted_after_bounded_repairs','review_scope':'Concrete stage/transition and selected factual fields; not exhaustive mechanics/UI/game validation.'})
checks['statistics_review']={'reviewer':'HQ independent Playwright original-page read','message_id':'msg_3bbdecf9df70','url':'https://poe.ninja/poe2/builds','observed_at':'2026-09-21T12:25:14.544Z','outcome':'Worker cohort counts and top-three class shares match; not build-share data.'}
dump(ROOT/'review_ledger.json',checks)
for r in records:
    r['manager_review']='deep_gate_original_page_checked' if r['retrieval_status']=='deep_stage_extracted' else 'structure_and_worker_evidence_checked'
dump(ROOT/'catalog.json',{'schema_version':'1.0','as_of':'2026-09-21','game':'POE2','approval_status':'collected_not_game_validated','records':records})
(ROOT/'sources.jsonl').write_text(''.join(json.dumps(s,ensure_ascii=False)+'\n' for s in sources),encoding='utf-8')
cols=['id','family_id','family_name','variant','game','patch','league','death_mode','economy_mode','creator','url','updated_at','accessed_at','retrieval_status','popularity_type','popularity_value','popularity_rank','popularity_scope','popularity_source_id','approval_status']
with (ROOT/'catalog.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=cols);writer.writeheader()
    for r in records:
        row={k:r.get(k) for k in cols};row.update(patch=r['patch']['value'],death_mode=r['mode']['death'],economy_mode=r['mode']['economy'])
        row.update({'popularity_'+k:r['popularity'].get(k) for k in ['type','value','rank','scope','source_id']});writer.writerow(row)
notes=ROOT/'build_notes';notes.mkdir(exist_ok=True)
for r in records:
    lines=[f"# {r['id']} — {r['family_name']}",'',f"[원문 가이드]({r['url']}) · {r['creator']}",'',f"패치 원문 표기: {r['patch']['value']} / 상태: {r['approval_status']}",'',f"샘플: {r['variant']}. 전체 UI 변형을 모두 선택한 자료는 아닙니다.",'',f"핵심 스킬: {', '.join(r['main_skills'])}",'',f"피해: {r['damage_structure']}",f"방어: {r['defense_structure']}",'', '## 단계와 전환 조건','']
    for s in r['stages']:
        lines += [f"- **{s['name']}**: {s['conditions']} → {s['transition']} (출처 {s['source_id']}, {s['locator']})"]
    if not r['stages']: lines += ['구체적 전환 조건 미추출. 단계 탭 이름만으로 조건을 만들지 않았습니다.']
    lines += ['','## 장비와 연결','']
    lines += [f"- {x['name']} [{x['role']}]: {x['condition']} ({x['source_id']}, {x['locator']})" for x in r['equipment']]
    lines += [f"- {x['name']} → {', '.join(x['supports']) or '보조젬 미추출'} ({x['source_id']}, {x['locator']})" for x in r['skills']]
    lines += ['','## 자료의 한계','']+[f'- {x}' for x in r['gaps_conflicts']]
    lines += ['','작성자 주장과 공개 페이지 사실을 정리한 수집본입니다. 실게임 성능·1.0.0 생존을 검증하지 않았습니다. 상세 자원/대안/주장별 근거는 catalog.json의 같은 ID를 확인하세요.','']
    (notes/(r['id']+'.md')).write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({'records':len(records),'families':len(families),'deep':sum(r['retrieval_status']=='deep_stage_extracted' for r in records),'sources':len(sources)},ensure_ascii=False))
