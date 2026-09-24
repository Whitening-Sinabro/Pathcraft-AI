"""Create local replay clips and a readable report from the audited intervals."""
from pathlib import Path
import concurrent.futures
import datetime
import hashlib
import html
import json
import subprocess
import markdown

HERE = Path(__file__).resolve().parent
TITLE = '초반_스킬교체_정밀확인'
scenes = json.loads((HERE / 'dense_scenes.json').read_text(encoding='utf-8'))


def run(args):
    subprocess.run(args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def make_clip(scene):
    target = HERE / (scene['name'] + '_replay.mp4')
    offset = scene['scene_start'] - scene['file_start']
    if not target.exists():
        run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-y',
             '-ss', str(offset), '-i', str(HERE / scene['file']), '-t', str(scene['duration']),
             '-map', '0:v:0', '-map', '0:a:0?', '-vf', 'fps=30,scale=1280:-2',
             '-c:v', 'libx264', '-preset', 'fast', '-crf', '21', '-threads', '2',
             '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', str(target)])
    poster = HERE / (scene['name'] + '_poster.jpg')
    if not poster.exists():
        run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-y',
             '-i', str(target), '-frames:v', '1', '-q:v', '3', str(poster)])
    probe = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_type,width,height',
                            '-of', 'json', str(target)], check=True, capture_output=True, text=True)
    data = json.loads(probe.stdout)
    assert abs(float(data['format']['duration']) - scene['duration']) < .15
    assert any(x['codec_type'] == 'video' and x['width'] == 1280 for x in data['streams'])
    return {**scene, 'clip': target.name, 'poster': poster.name, 'probe': data,
            'sha256': hashlib.sha256(target.read_bytes()).hexdigest()}


with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    clips = list(pool.map(make_clip, scenes))

body = markdown.markdown((HERE / (TITLE + '.md')).read_text(encoding='utf-8'), extensions=['tables', 'fenced_code'])
for clip in clips:
    name = clip['name']
    element = f'''<div class="replay" data-origin="{clip['scene_start']}">
<video id="{name}" controls preload="metadata" playsinline poster="{clip['poster']}"><source src="{clip['clip']}" type="video/mp4"></video>
<div class="controls"><button data-action="back">−0.5초</button><button data-action="play">재생 / 일시정지</button><button data-action="forward">+0.5초</button>
<label>속도 <select aria-label="재생 속도"><option value="0.5">0.5×</option><option value="1" selected>1×</option><option value="1.5">1.5×</option></select></label>
<output aria-live="off"></output><a href="{clip['clip']}" download>영상 저장</a></div></div>'''
    assert body.count('<!-- clip:' + name + ' -->') == 1
    body = body.replace('<!-- clip:' + name + ' -->', element)

document = '''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>HCFB_CCTBurger · 초반 스킬 교체 확인</title>
<style>
:root{color-scheme:dark;font-family:"Malgun Gothic",system-ui,sans-serif;background:#10151d;color:#e3e9f0;line-height:1.8}
*{box-sizing:border-box}body{margin:0}main{max-width:1100px;margin:auto;padding:44px 28px 90px}h1{font-size:clamp(24px,4vw,36px);line-height:1.4;color:#fff;margin-bottom:12px}
h2{margin-top:50px;padding-top:20px;border-top:1px solid #334055;color:#ffe0a0}h3{margin-top:32px;color:#bedcfa}p,li{max-width:94ch}a{color:#8bc7ff;text-underline-offset:4px}
strong{color:#fff0c5}table{border-collapse:collapse;display:block;overflow-x:auto;width:100%;font-size:14px;margin:24px 0}td,th{border:1px solid #3a4656;padding:12px 14px;min-width:120px;vertical-align:top}th{background:#202c3b;text-align:left}tr:nth-child(even){background:#151f2c}
code{background:#253347;padding:2px 5px;border-radius:4px}.replay{margin:22px 0 36px;border:1px solid #3b4f68;border-radius:10px;overflow:hidden;background:#182332}video{display:block;width:100%;max-height:650px;background:#000}.controls{display:flex;align-items:center;gap:12px;flex-wrap:wrap;padding:14px}button,select{background:#2e4662;border:1px solid #607a9a;color:#fff;padding:8px 12px;border-radius:5px;cursor:pointer;font:inherit;font-size:14px}output{font-variant-numeric:tabular-nums;color:#ffe0a0}li{margin:8px 0}
@media(max-width:600px){main{padding:22px 16px 60px}.controls{gap:8px}td,th{padding:8px}h2{font-size:21px}}
</style><main>''' + body + '''</main><script>
const stamp=s=>{s=Math.floor(s);return [Math.floor(s/3600),Math.floor(s/60)%60,s%60].map(x=>String(x).padStart(2,'0')).join(':')};
document.querySelectorAll('.replay').forEach(w=>{const v=w.querySelector('video'),o=w.querySelector('output'),origin=Number(w.dataset.origin);const update=()=>o.textContent='방송 '+stamp(origin+v.currentTime);v.addEventListener('timeupdate',update);update();
w.querySelector('select').addEventListener('change',e=>v.playbackRate=Number(e.target.value));
w.querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>{const a=b.dataset.action;if(a==='play'){if(v.paused)v.play().catch(()=>{});else v.pause()}else{v.pause();v.currentTime=Math.max(0,Math.min(Number.isFinite(v.duration)?v.duration:0,v.currentTime+(a==='back'?-.5:.5)));update()}}));});
</script></html>'''
(HERE / (TITLE + '.html')).write_text(document, encoding='utf-8')
manifest = {'created_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'full_broadcasts_reviewed_continuously': False, 'keystroke_log_available': False,
            'dense_review_seconds': sum(x['duration'] for x in scenes),
            'dense_frames_reviewed': sum(round(x['duration']/x['step']) for x in scenes),
            'context_review': {'first_day_start': 14880, 'duration': 960, 'step': 10, 'frames_reviewed': 96},
            'source_time_alignment': {'method': 'Frame image comparison with locally saved full 360p VOD',
                                      'first_day_720p_offsets_checked': [90, 380, 780], 'best_offset_seconds': [0, 0, 0],
                                      'reported_timestamp_tolerance_seconds': 1},
            'user_snapshot': {'file': 'user_lookup_114946.json', 'name': 'HCFB_CCTBurger',
                              'updated_utc': '2026-09-08T11:22:16.428554Z', 'level': 23},
            'clips': clips, 'browser_playback_verified': False}
(HERE / 'review_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'html': str(HERE / (TITLE + '.html')), 'clips': len(clips),
                  'seconds': manifest['dense_review_seconds'], 'frames': manifest['dense_frames_reviewed']}, ensure_ascii=False))
