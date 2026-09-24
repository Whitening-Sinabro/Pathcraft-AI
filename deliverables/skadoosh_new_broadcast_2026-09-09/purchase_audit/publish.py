"""Publish the bounded shopping audit, preserve source snapshots, and link guides."""
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlparse, unquote
import ast, json, re, subprocess, hashlib
import markdown

HERE=Path(__file__).resolve().parent;VOD=HERE.parent;ROOT=HERE.parents[2]
TITLE='40분대_구매와제작_추가확인'
constants={}
for n in ast.parse((VOD/'publish_review.py').read_text(encoding='utf-8')).body:
    if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ('style','script'):
        constants[n.targets[0].id]=ast.literal_eval(n.value)

evidence={}
for label,p in [('before',ROOT/'deliverables/skadoosh_early_survival_2026-09-08/stage_05_06_audit/ninja_latest.json'),('after',VOD/'creator_latest.json')]:
    d=json.loads(p.read_text(encoding='utf-8'))
    items=[i for i in d['items'] if 'Solar Amulet' in json.dumps(i,ensure_ascii=False)]
    assert len(items)==1,(label,len(items))
    evidence[label]={'source':str(p.relative_to(ROOT)),'level':d['level'],'updatedUtc':d.get('updatedUtc'),'item':items[0]}
(HERE/'amulet_evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')

body=markdown.markdown((HERE/(TITLE+'.md')).read_text(encoding='utf-8'),extensions=['tables','fenced_code'])
chapters={'purchase_37_42':[(2430,'40:30 검색'),(2468,'41:08 구매')],'purchase_42_47':[(2534,'42:14 접미어 제한'),(2688,'44:48 징조 구매'),(2726,'45:26 저항 선택')],'purchase_47_52':[(2856,'47:36 ES 결과'),(3029,'50:29 Fear 구매'),(3064,'51:04 성유 순서'),(3066,'51:06 부여 완료')]}
clips=[]
for label in re.findall(r'<!-- replay:([a-z_0-9]+) -->',body):
    meta=json.loads((HERE/(label+'.json')).read_text(encoding='utf-8'));p=HERE/(label+'.mp4')
    probe=json.loads(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,width,height','-of','json',str(p)],capture_output=True,text=True,check=True).stdout)
    duration=float(probe['format']['duration']);assert abs(duration-300)<.2
    assert any(s.get('width')==1280 and s.get('height')==720 for s in probe['streams'])
    jumps=''.join(f'<button data-player="{label}" data-jump="{sec-meta["requested_start"]}">{title}</button>' for sec,title in chapters[label])
    player=f'<div class="chapters">{jumps}</div><figure id="{label}" class="replay" data-origin="{meta["requested_start"]}"><video controls preload="none" poster="frames/vod_{meta["requested_start"]}.jpg" src="{label}.mp4"></video><figcaption><button data-seek="-0.5">−0.5초</button><button data-seek="0.5">+0.5초</button><label>속도 <select><option value="0.5">0.5×</option><option value="1" selected>1×</option><option value="1.5">1.5×</option></select></label><output></output><a href="https://www.twitch.tv/videos/2868822161?t={meta["requested_start"]}s">원본 위치</a></figcaption></figure>'
    body=body.replace('<!-- replay:'+label+' -->',player)
    clips.append({'label':label,'interval':[meta['requested_start'],meta['requested_end']],'duration':duration,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'streams':probe['streams']})
style=constants['style']+'img{max-width:100%;height:auto;display:block;margin:20px auto}p,li{overflow-wrap:anywhere}.chapters{display:flex;gap:8px;flex-wrap:wrap}figure{scroll-margin-top:20px}'
script=constants['script']+'''document.querySelectorAll('[data-jump]').forEach(b=>b.addEventListener('click',()=>{const w=document.getElementById(b.dataset.player),v=w.querySelector('video');v.pause();v.preload='auto';const go=()=>{v.currentTime=Number(b.dataset.jump);w.scrollIntoView({block:'center'})};if(v.readyState>=1)go();else{v.addEventListener('loadedmetadata',go,{once:true});v.load()}}));'''
document=f'<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Skadoosh 40분대 구매·제작 추가 확인</title><style>{style}</style><main>{body}</main><script>{script}</script></html>'
(HERE/(TITLE+'.html')).write_text(document,encoding='utf-8')

marker='<!-- purchase-audit-20260909 -->'
def add_notice(mdpath,htmlpath,notice):
    p=mdpath;s=p.read_text(encoding='utf-8')
    if marker not in s:
        title,rest=s.split('\n',1);p.write_text(title+'\n\n'+marker+'\n'+notice+'\n'+rest,encoding='utf-8')
    p=htmlpath;s=p.read_text(encoding='utf-8')
    if marker not in s:
        assert re.search(r'<main\b[^>]*>',s)
        p.write_text(re.sub(r'(<main\b[^>]*>)',lambda m:m.group(1)+marker+markdown.markdown(notice),s,count=1),encoding='utf-8')
notice='**40분대 구매 조사 보강:** [목걸이 검색·2디바인 구매·징조와 Fear 구매·성유 순서·생명력/재생 손실](../deliverables/skadoosh_new_broadcast_2026-09-09/purchase_audit/'+TITLE+'.html). 기존 조사에서 빠졌던 37~52분 구매·가공 과정을 추가 확인했다.'
for md,ht in [('2026-09-08_SKADOOSH_SESSION_CHECKPOINT.md','2026-09-08_SKADOOSH_SESSION_CHECKPOINT.html'),('2026-09-05_SKADOOSH_CORRUPTING_CRY_TOTEM_WARBRINGER_0_5_5_RESEARCH.md','2026-09-05_SKADOOSH_CORRUPTING_CRY_TOTEM_WARBRINGER_0_5_5_GUIDE_DOC.html')]:
    add_notice(ROOT/'Docs'/md,ROOT/'Docs'/ht,notice)
add_notice(VOD/'mechanics_followup/빌드핵심_추가확인.md',VOD/'mechanics_followup/빌드핵심_추가확인.html',notice.replace('../deliverables/skadoosh_new_broadcast_2026-09-09/purchase_audit/','../purchase_audit/'))
add_notice(VOD/'새방송_변경사항.md',VOD/'새방송_변경사항.html',notice.replace('../deliverables/skadoosh_new_broadcast_2026-09-09/purchase_audit/','purchase_audit/'))

old='이번 교체는 정신력 6을 내리고 스킬 레벨 등을 얻은 선택이다.'
new='이번 교체에서는 정신력 6뿐 아니라 기존의 생명력 +40, 초당 생명력 재생 12.1, 냉기 저항 +25%도 잃고 근접 스킬 +2 등을 얻었다. 실제 구매·가공 확인 결과, 새 목걸이의 ES 47% 증가는 생명력을 원했으나 붙은 옵션이다.'
for p in [VOD/'새방송_변경사항.md',VOD/'새방송_변경사항.html']:
    s=p.read_text(encoding='utf-8')
    if old in s:p.write_text(s.replace(old,new,1),encoding='utf-8')
    else:assert new in s

missing=[]
for t in re.findall(r'(?:href|src|poster)="([^"]+)"',document):
    u=urlparse(t)
    if u.scheme or t.startswith('#') or u.path=='report_validation.json':continue
    if not (HERE/unquote(u.path)).exists():missing.append(t)
assert not missing,missing
result={'checked_utc':datetime.now(timezone.utc).isoformat(),'video_id':'2868822161','interval':[2220,3120],'clips':clips,'clip_seconds':sum(c['duration'] for c in clips),'missing_local_links':missing,'asr_automatic':True,'visual_method':'10-second survey and 1-3-second targeted purchase/craft/instil frames; not continuous frame-by-frame viewing','continuous_full_video_viewing':False,'native_planners_modified_this_audit':False,'remaining_uncertainties':['Ruby search results at 40:10 do not establish jewel purchase','Exact currency grade used for the final prefix was not read from a tooltip','Abyssal Echoes consumption does not itself establish a reroll button press']}
(HERE/'report_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'report':str(HERE/(TITLE+'.html')),'clips':len(clips),'missing':missing},ensure_ascii=False))
