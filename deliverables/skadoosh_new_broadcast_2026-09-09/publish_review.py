"""Publish research with local replays, provenance, and scoped guide links."""
from pathlib import Path
import json,re,subprocess,hashlib,html
from datetime import datetime,timezone
from urllib.parse import urlparse,unquote
import markdown

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
TITLE='새방송_변경사항'
text=(HERE/(TITLE+'.md')).read_text(encoding='utf-8')
body=markdown.markdown(text,extensions=['tables','fenced_code'])
clips=[]
for label in re.findall(r'<!-- clip:([a-z_]+) -->',body):
    meta=json.loads((HERE/'clips'/(label+'.json')).read_text(encoding='utf-8'))
    path=HERE/'clips'/(label+'.mp4')
    probe=json.loads(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,width,height','-of','json',str(path)],capture_output=True,text=True,check=True).stdout)
    duration=float(probe['format']['duration']);expected=meta['requested_end']-meta['requested_start']
    assert abs(duration-expected)<.2,(label,duration,expected)
    assert any(s.get('codec_type')=='video' and s.get('width')==1280 for s in probe['streams'])
    poster=HERE/'frames'/(label+'_poster.jpg')
    if not poster.exists():subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(path),'-frames:v','1',str(poster)],check=True)
    body=body.replace('<!-- clip:'+label+' -->',f'''<figure class="replay" data-origin="{meta['requested_start']}"><video controls preload="none" poster="frames/{label}_poster.jpg" src="clips/{label}.mp4"></video><figcaption><button data-seek="-0.5">−0.5초</button><button data-seek="0.5">+0.5초</button><label>속도 <select><option value="0.5">0.5×</option><option value="1" selected>1×</option><option value="1.5">1.5×</option></select></label><output></output><a href="https://www.twitch.tv/videos/2868822161?t={int(meta['requested_start'])}s">원본 위치</a></figcaption></figure>''')
    clips.append({'label':label,'requested_interval':[meta['requested_start'],meta['requested_end']],'duration_seconds':duration,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'streams':probe['streams']})
style='''body{margin:0;background:#111820;color:#e7edf4;font:16px/1.85 "Malgun Gothic",system-ui,sans-serif}main{max-width:1100px;margin:auto;padding:36px 24px 80px}h1{font-size:30px;line-height:1.4}h2{margin-top:48px;border-top:1px solid #384b5e;padding-top:22px;color:#efdbad}a{color:#99caff}strong{color:#ffdfa0}table{border-collapse:collapse;display:block;overflow:auto;font-size:14px}td,th{padding:12px;border:1px solid #455569;vertical-align:top;min-width:120px}th{background:#223044;text-align:left}code{overflow-wrap:anywhere;background:#243142;padding:2px 4px}.replay{margin:24px 0;background:#1b2938;border:1px solid #3c5068}video{width:100%;display:block}figcaption{display:flex;gap:12px;align-items:center;flex-wrap:wrap;padding:14px}button,select{font:inherit;background:#263e58;color:white;border:1px solid #597796;padding:5px 9px}output{font-variant-numeric:tabular-nums}li{margin:9px 0}@media(max-width:600px){main{padding:20px 14px}h1{font-size:24px}}'''
script='''const stamp=s=>{s=Math.floor(s);return [Math.floor(s/3600),Math.floor(s/60)%60,s%60].map(v=>String(v).padStart(2,'0')).join(':')};document.querySelectorAll('.replay').forEach(w=>{const v=w.querySelector('video'),o=w.querySelector('output'),a=Number(w.dataset.origin);const update=()=>o.textContent='방송 '+stamp(a+v.currentTime);v.addEventListener('timeupdate',update);update();w.querySelector('select').addEventListener('change',e=>v.playbackRate=Number(e.target.value));w.querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>{v.pause();if(Number.isFinite(v.duration))v.currentTime=Math.max(0,Math.min(v.duration,v.currentTime+Number(b.dataset.seek)));update()}))});'''
document=f'<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Skadoosh 새 방송 · 80→84와 4차 전직</title><style>{style}</style><main>{body}</main><script>{script}</script></html>'
(HERE/(TITLE+'.html')).write_text(document,encoding='utf-8')

# Add links only; do not rewrite historical claims or install newer native stages.
notice='**9월 9일 후속 조사:** [새 방송 2868822161 · 80→84레벨·4차 전직·Sunder 시험·무기 세트와 회복 주의사항](../deliverables/skadoosh_new_broadcast_2026-09-09/새방송_변경사항.html). 기존 05/06 진입 조건은 유지하며, 84레벨 성장·시험 결과를 별도로 기록했다.'
notice_md='<!-- new-vod-20260909:start -->\n'+notice+'\n<!-- new-vod-20260909:end -->\n'
docs=['2026-09-08_SKADOOSH_SESSION_CHECKPOINT.md','2026-09-05_SKADOOSH_CORRUPTING_CRY_TOTEM_WARBRINGER_0_5_5_RESEARCH.md']
for name in docs:
    path=ROOT/'Docs'/name;s=path.read_text(encoding='utf-8')
    if '<!-- new-vod-20260909:start -->' not in s:
        title,rest=s.split('\n',1);s=title+'\n\n'+notice_md+rest;path.write_text(s,encoding='utf-8')
notice_html='<!-- new-vod-20260909:start -->'+markdown.markdown(notice)+'<!-- new-vod-20260909:end -->'
for name in ['2026-09-08_SKADOOSH_SESSION_CHECKPOINT.html','2026-09-05_SKADOOSH_CORRUPTING_CRY_TOTEM_WARBRINGER_0_5_5_GUIDE_DOC.html']:
    path=ROOT/'Docs'/name;s=path.read_text(encoding='utf-8')
    if '<!-- new-vod-20260909:start -->' not in s:
        assert re.search(r'<main\b[^>]*>',s),name
        s=re.sub(r'(<main\b[^>]*>)',lambda m:m.group(1)+notice_html,s,count=1);path.write_text(s,encoding='utf-8')

missing=[]
for target in re.findall(r'(?:href|src|poster)="([^"]+)"',document):
    u=urlparse(target)
    if u.scheme or target.startswith('#'):continue
    f=(HERE/unquote(u.path)).resolve()
    if f.name=='review_validation.json':continue
    if not f.exists():missing.append(str(f))
assert not missing,missing
audio=json.loads((HERE/'audio_coverage.json').read_text(encoding='utf-8'));asr=json.loads((HERE/'asr_coverage.json').read_text(encoding='utf-8'))
assert asr['complete_audio_processed'] and audio['missing_segments']==0
assert abs(audio['expected_seconds']-asr['audio_duration_seconds'])<.1
validation={'checked_utc':datetime.now(timezone.utc).isoformat(),'video_id':'2868822161','audio':audio,'asr':asr,'focused_asr_files':len(list((HERE/'verified_asr').glob('*.json'))),'linked_clips':clips,'missing_local_links':missing,'native_planners_modified':True,'game_installation_modified':True,'planner_change_scope':'Follow-up: 05/06/07 reservation notes only; mechanics_followup/planner_note_validation.json','continuous_full_video_viewing':False,'visual_method':'64-second storyboard survey; selected 720p contact sheets and detailed G/tree frames, no claim of continuous viewing','snapshot_baseline':'stage_05_06_audit/ninja_latest.json, level 80','snapshot_latest':'creator_latest.json, level 84','uncertainties':['Precision/totem accuracy snapshot behaviour','Echoing Cry net recovery','Encase in Jade usage timing in individual fights']}
(HERE/'review_validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'report':str(HERE/(TITLE+'.html')),'clips_verified':len(clips),'missing_links':missing,'full_audio_asr':True},ensure_ascii=False))
