"""Package the selected explanation scenes; keep viewing and generation records separate."""
from pathlib import Path
import json, re, cv2, numpy as np
HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'later_planner_audit'
FULL=HERE.parents[1]/'skadoosh_hc_2026-09-07/broadcast_audit/2866749730/video.mp4'
def save(name,data):(HERE/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

scenes=[
    ('seismic_before_paquate','seismic_early.mp4',9320,9338,20),
    ('purity_precision','purity_links.mp4',12920,12922,60),
    ('paquate_change','../later_planner_audit/paquate_transition.mp4',14040,14252,28),
    ('raging_finish','../later_planner_audit/paquate_transition.mp4',14040,14570,30),
    ('recovery_panel','../later_planner_audit/paquate_transition.mp4',14040,14140,8),
    ('echo_recovery','recovery_explained.mp4',17940,17965,24),
    ('totem_passives','../later_planner_audit/awt_transition.mp4',1620,1788,26),
    ('tooltip_not_allocation','recovery_explained.mp4',17940,18182,18),
]
save('replay_scenes.json',[dict(zip(['name','file','file_start','scene_start','duration'],x),vod='2866749730') for x in scenes])
viewed=json.loads((HERE/'viewed_boards.json').read_text(encoding='utf-8'))
totals={'2866749730_full_1200':52,'awt_transition_full_2980':42,'2866749730_full_8940':20,
        '2866749730_full_9580':18,'2866749730_full_11980':30,'2866749730_full_12720':36,
        '2866749730_full_12900':36,'tree54_full_1620':114,'tree65_full_14060':80,
        'seismic_early_full_9320':60,'2866749730_full_9100':22,'defence_progress_full_7430':28,
        'purity_links_left_12920':56,'post_paquate_full_14880':21,'2866749730_full_17940':27,
        'recovery_detail_full_18180':16,'echo_heal_full_17965':8}
counted=[];other=[]
for name in viewed:
    m=re.match(r'(.+)_(\d+)\.jpg$',name)
    if m and m[1] in totals:
        count=max(0,min(8,totals[m[1]]-int(m[2])*8));assert count
        counted.append({'board':name,'sampled_frame_entries':count})
    else:other.append(name)
save('inspection_coverage.json',{'full_broadcast_reviewed_continuously':False,
    'method':'ASR explanation search, followed by visual inspection of selected timestamped frames and tooltips',
    'total_frames_reviewed':sum(x['sampled_frame_entries'] for x in counted),
    'count_is_unique_timestamps':False,'count_excludes_separately_viewed_stills_and_node_crops':True,
    'boards_viewed':counted,'other_viewed_images':other,'asr_is_not_human_audio_listening':True})

sources={'seismic_early':(9320,180),'purity_progress':(12740,160),'defence_progress':(7430,420),
         'post_paquate':(14880,420),'purity_links':(12920,180),'recovery_explained':(17940,420)}
media=[]
for name,(origin,duration) in sources.items():
    p=HERE/(name+'.mp4');cap=cv2.VideoCapture(str(p));assert cap.isOpened()
    actual=cap.get(cv2.CAP_PROP_FRAME_COUNT)/cap.get(cv2.CAP_PROP_FPS);cap.release()
    media.append({'name':name,'vod':'2866749730','start':origin,'requested_duration':duration,'actual_duration':actual,'bytes':p.stat().st_size})
save('media_coverage.json',media)

def frame(cap,t):
    cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,im=cap.read();assert ok,t
    return cv2.resize(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY),(320,180)).astype(np.float32)
full=cv2.VideoCapture(str(FULL));assert full.isOpened()
alignment=[]
for name in ['seismic_early','purity_links','recovery_explained']:
    origin,duration=sources[name];cap=cv2.VideoCapture(str(HERE/(name+'.mp4')))
    for local in [40,duration-35]:
        target=frame(cap,local)
        scores=[{'offset':offset,'mae':float(np.abs(target-frame(full,origin+local+offset)).mean())} for offset in range(-3,4)]
        best=min(scores,key=lambda x:x['mae'])
        alignment.append({'file':name+'.mp4','local_seconds':local,'best':best,'scores':scores})
    cap.release()
full.release()
save('source_alignment.json',{'new_sources':alignment,'earlier_sources':'../later_planner_audit/source_alignment.json'})
assert all(abs(x['best']['offset'])<=1 for x in alignment),alignment

candidate=HERE/'tree54_candidate.json'
d=json.loads(candidate.read_text(encoding='utf-8'))
d['audit_status']='REJECTED: legal point count and connectivity did not match observed allocations'
d['installable']=False
d['reason']='Candidate included Bolstering Yell allocation absent from the inspected 54-level frame. Do not use as historical reconstruction.'
save(candidate.name,d)

builder=(OLD/'build_review.py').read_text(encoding='utf-8').replace("TITLE = '후속_플래너_정밀확인'","TITLE = '05_06_설명장면_재확인'").replace('03~07 플래너 정밀 확인','05·06 설명 장면 재확인')
(HERE/'build_review.py').write_text(builder,encoding='utf-8')
validator=(OLD/'validate_review.cjs').read_text(encoding='utf-8').replace('후속_플래너_정밀확인.html','05_06_설명장면_재확인.html')
validator=re.sub(r'for \(const id of \[.*?\]\)',"for (const id of JSON.parse(fs.readFileSync(path.join(__dirname, 'replay_scenes.json'), 'utf8')).map(x => x.name))",validator,count=1)
validator=validator.replace('for (const href of missing) {', "for (const href of missing) {\n      if (href === 'review_page_validation.json') continue; // Written by this validation below.")
(HERE/'validate_review.cjs').write_text(validator,encoding='utf-8')
print(json.dumps({'scenes':len(scenes),'replay_seconds':sum(x[-1] for x in scenes),'alignment':[(x['file'],x['best']['offset']) for x in alignment]},ensure_ascii=False))
