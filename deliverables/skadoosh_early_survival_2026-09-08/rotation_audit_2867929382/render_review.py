"""Render bounded video evidence and annotated combat timelines locally."""
from pathlib import Path
import hashlib
import html
import json
import subprocess

HERE = Path(__file__).resolve().parent
VOD = 'https://www.twitch.tv/videos/2867929382'
SCENES = [
    {
        'id': 'mapping', 'title': '맵 이동 · 함성으로 진행하다 토템 추가',
        'source': 'continuous_13140_480.mp4', 'source_start': 13140,
        'start': 13156, 'duration': 20,
        'dense_range': [13158, 13174],
        'sheets': ['mapping_033918_0.jpg', 'mapping_033918_1.jpg'],
        'timeline': [
            ['03:39:18~20', '남은 정신력 313/343 상태에서 이동과 함성 효과, 적 처치가 이어진다. 이때 전방 토템 설치를 먼저 마치는 동작은 없다.'],
            ['03:39:21~25', '토템 설치 동작과 새 토템·혼백 출현이 이어지고 남은 정신력이 줄어든다. 이동 중의 함성 운영에 토템을 추가하는 구간이다.'],
            ['03:39:26~29', '소환물이 공격하는 동안 이동을 계속한다. 보강 관련 효과가 이어지며 다음 무리 쪽으로 진행한다.'],
            ['03:39:30~33', '다음 적 무리에서 함성 효과와 토템 보충이 다시 나타난다. 매 무리마다 같은 3개 버튼을 한 번씩 누르는 고정 순서를 읽어낼 수는 없다.'],
        ],
        'takeaway': '기본 진행은 함성을 이어가며 이동. 밀집 무리나 더 필요한 화력에 맞춰 토템을 추가하고 이동·함성으로 돌아간다.',
    },
    {
        'id': 'crowd', 'title': '적이 몰리는 이벤트 · 함성 뒤 토템을 연속 추가',
        'source': 'continuous_1500_420.mp4', 'source_start': 1500,
        'start': 1820, 'duration': 18,
        'dense_range': [1820, 1836],
        'sheets': ['crowd_003020_0.jpg', 'crowd_003020_1.jpg'],
        'timeline': [
            ['00:30:20~22', '기존 소환물이 남아 있는 상태로 이동해 보라색 이벤트 지점에 접근한다.'],
            ['00:30:22.5 전후', '함성 효과가 나오고 보강 관련 버프 표시가 갱신된다. 이 장면만으로 직접 입력과 메아리를 구별하지는 않는다.'],
            ['00:30:23~25', '토템을 연속으로 추가한다. 같은 세트 표시에서 남은 정신력이 약 174 → 99 → 24로 줄고 소환물이 늘어난다.'],
            ['00:30:25~35', '방패 세트로 돌아와 함성 효과와 이동을 이어간다. 소환물의 공격과 가시 생성이 함께 진행된다.'],
        ],
        'takeaway': '사용자가 말한 “함성을 쓰고 다니다가 다른 동작을 추가”하는 모습을 확인하기 좋은 구간이다. 여기서 추가하는 동작은 토템 설치로 확인된다.',
    },
    {
        'id': 'boss', 'title': '지도 보스 · 접근 후 토템을 먼저 준비',
        'source': 'continuous_1500_420.mp4', 'source_start': 1500,
        'start': 1692, 'duration': 18,
        'dense_range': [1692, 1708],
        'sheets': ['boss_002812_0.jpg', 'boss_002812_1.jpg'],
        'timeline': [
            ['00:28:12~16', '보스 쪽으로 이동한다. 남은 정신력이 충분하고 격노는 이동 중 감소한다.'],
            ['00:28:16.5~18', '토템 설치를 여러 번 이어간다. 남은 정신력이 324 → 249 → 174 → 24로 줄어드는 장면이 있다.'],
            ['00:28:18~21', '함성·소환물의 공격이 겹치며 격노가 30까지 올라간다. 함성마다 가시를 눈으로 확인하고 한 번씩 기다리는 멈춤은 관찰되지 않는다.'],
            ['00:28:22~27', '자리와 방향을 바꾸며 공격을 이어간 뒤 보스를 처치한다. 00:28:26 전후에 지도 완료 표시가 나온다.'],
        ],
        'takeaway': '보스 앞에서 토템을 미리 설치하는 설명은 이 장면에 해당한다. 일반 이동 중의 기본 흐름과 따로 이해해야 한다.',
    },
    {
        'id': 'sustained', 'title': '이어지는 무리 전투 · 이동과 설치를 번갈아 수행',
        'source': 'continuous_13140_480.mp4', 'source_start': 13140,
        'start': 13270, 'duration': 18,
        'dense_range': [13270, 13286],
        'sheets': ['fight_034110_0.jpg', 'fight_034110_1.jpg'],
        'timeline': [
            ['03:41:10~13', '기존 전투 자리에서 이동하며 함성 효과를 유지한다. 이전 토템이 사라지면서 남는 정신력이 늘어난다.'],
            ['03:41:13~20', '새 전투 위치에 토템을 반복해서 보충하고 함성 효과를 이어간다. 토템을 한 번 놓고 전투가 끝날 때까지 그대로 두는 흐름은 아니다.'],
            ['03:41:21~25', '적을 정리하며 방향을 바꾸고 추가로 설치한다. 소환물의 위치와 적의 위치에 따라 설치가 전투 사이에 들어간다.'],
        ],
        'takeaway': '토템 유지에는 사망·만료뿐 아니라 이동에 따른 재배치도 포함된다. 정해진 횟수의 함성 뒤에만 재설치하는 방식으로 외울 근거는 없다.',
    },
]


def stamp(value):
    t = int(value)
    return f'{t//3600:02}:{t//60%60:02}:{t%60:02}'


def link(t):
    t = int(t)
    return VOD + f'?t={t//3600:02}h{t//60%60:02}m{t%60:02}s'


def make_clip(scene):
    dest = HERE / (scene['id'] + '.mp4')
    if not dest.exists():
        subprocess.run([
            'ffmpeg', '-v', 'error', '-nostdin', '-ss', str(scene['start'] - scene['source_start']),
            '-i', str(HERE / scene['source']), '-t', str(scene['duration']),
            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
            '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', str(dest),
        ], check=True)
    probe = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', str(dest)]))
    assert abs(float(probe['format']['duration']) - scene['duration']) < .2
    poster = HERE / (scene['id'] + '_poster.jpg')
    if not poster.exists():
        subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-ss', '.5', '-i', str(dest),
                        '-frames:v', '1', '-q:v', '3', str(poster)], check=True)
    return {'file': dest.name, 'seconds': float(probe['format']['duration']),
            'sha256': hashlib.sha256(dest.read_bytes()).hexdigest()}


def main():
    heading = 'Skadoosh 최신 방송 · 로테이션 정밀 확인'
    lead = '함성을 이어가며 이동 → 밀집 무리·희귀에 토템 추가 → 함성·이동으로 복귀. 보스 앞에서는 토템을 미리 여러 번 설치하는 준비가 보인다.'
    limits = ('대상은 Twitch VOD 2867929382, UTC 2026-09-07 시작 방송이다. '
              '00:25~00:32와 03:39~03:47의 연속 원본 15분을 확보해 흐름을 훑고, '
              '아래 네 전투 구간 총 64초를 0.5초 간격의 128개 프레임으로 상세 대조했다. '
              '스킬 창 00:10대·03:00대도 확인했다. 방송 전체 시청이나 키 입력 로그 분석은 아니다. '
              '시각은 추출한 미디어 기준 근삿값이며 아래 영상에서 앞뒤 동작을 확인할 수 있다.')
    mechanics = [
        ('보강하는 함성', '파콰테의 타락한 피와 방어 효과를 이동 중에도 이어가는 역할. 메아리가 추가로 두 번 나가므로 화면의 함성 횟수를 직접 입력 횟수로 세지 않는다.'),
        ('지진 함성', '보강 사이에 반복하는 함성. 토템 가시 폭발과 전직의 시체 폭발·격노 유지에 관여한다. 가시가 있어야만 쓸 수 있는 버튼으로 설명한 것은 잘못이다.'),
        ('선대의 전사 토템', '밀집 무리·희귀·보스에 추가 화력을 제공한다. 설치는 II, 이후 함성은 I. 내부의 지면 분쇄가 가시를 만든다.'),
        ('푸른 선대의 혼백 · 자동', '토템을 소환할 때 응답받은 부름 전직으로 발동한다. 화면에 나타나는 동물·혼백을 별도의 추가 버튼으로 누르는 것은 아니다.'),
        ('공명하는 방패', '새 방송 스킬 창에서 장착을 확인했다. 방어도 파괴와 방패를 드는 채널링 공격이다. 검토한 장면만으로 매 전투에 끼우는 고정 순서는 확인하지 못했으므로 필수 로테이션에 추가하지 않는다.'),
    ]
    corrections = [
        '일반 이동에도 토템→보강→지진을 매번 강제하는 듯한 설명을 수정했다.',
        '지진 함성을 가시 폭발 전용으로 설명하며 시체 폭발을 빠뜨린 부분을 수정했다.',
        '이전 Day 3의 “약 4초” 발언은 당시 운용 예시다. 최신 방송의 모든 보강 입력을 4초 주기로 실측한 값처럼 쓰지 않는다.',
        '이펙트만으로 직접 보강 입력·메아리·지진 함성·설치에 겹치는 효과를 전부 구분했다고 주장하지 않는다. 토템 추가는 정신력 변화와 출현 동작으로 함께 확인했다.',
    ]
    sources = [
        ('최신 원본 방송', VOD),
        ('스킬 창 · 00:10:17 전후', link(617)),
        ('스킬 창 · 03:00:35 전후', link(10835)),
        ('메아리치는 함성의 2회 반복·이동 조건', 'https://poe2db.tw/us/Echoing_Cry'),
        ('전쟁 소집자의 고함의 시체 폭발', 'https://poe2db.tw/us/Warbringer'),
        ('지면 분쇄와 함성의 가시 폭발', 'https://poe2db.tw/us/Earthshatter'),
        ('공명하는 방패의 작동', 'https://poe2db.tw/us/Resonating_Shield'),
    ]
    md = ['# ' + heading, '', '**' + lead + '**', '', limits, '',
          '[영상 재생·0.5초 이동이 가능한 확인 페이지](방송_로테이션_정밀확인.html)', '']
    parts = ['<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
             '<title>' + heading + '</title>',
             '<style>body{margin:0;background:#101419;color:#e8edf2;font:16px/1.7 system-ui,sans-serif}main{max-width:1120px;margin:auto;padding:32px 22px}h1{font-size:30px;line-height:1.35}h2{font-size:22px;margin-top:38px}p{max-width:1000px}a{color:#8bc8ff}section{border-top:1px solid #34404e;margin-top:32px;padding-top:12px}video{width:100%;background:#000;max-height:660px}table{width:100%;border-collapse:collapse;margin:16px 0}td,th{text-align:left;vertical-align:top;padding:10px;border-bottom:1px solid #34404e}td:first-child{min-width:145px}button,select{font:inherit;background:#253344;color:white;border:1px solid #61778e;border-radius:6px;padding:6px 10px;cursor:pointer}.controls{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-top:10px}.lead{font-size:20px;background:#1a2a35;padding:18px;border-left:4px solid #83c8c0}.scope{color:#c0cad5;font-size:14px}.takeaway{color:#a2e0d4}summary{cursor:pointer}li{margin:8px 0}img{max-width:100%}</style><main>',
             '<h1>' + heading + '</h1><p class="lead">' + lead + '</p><p class="scope">' + limits + '</p>',
             '<p><a href="../타락함성_토템_스킬로테이션.md">단계별 플래너 안내</a> · <a href="방송_로테이션_정밀확인.md">텍스트 기록</a></p>']
    clip_rows = []
    for scene in SCENES:
        clip_rows.append(make_clip(scene))
        name = scene['id']
        md += ['## ' + scene['title'], '', f'[원본 {stamp(scene["start"])}]({link(scene["start"])}) · [로컬 영상]({name}.mp4)', '', '| 시각(약) | 확인한 흐름 |', '| --- | --- |']
        md += ['| ' + ' | '.join(row) + ' |' for row in scene['timeline']]
        md += ['', '**' + scene['takeaway'] + '**', '']
        md += [' · '.join(f'[0.5초 간격 프레임 {i+1}]({path})' for i, path in enumerate(scene['sheets'])), '']
        parts += [f'<section id="{name}"><h2>{html.escape(scene["title"])}</h2>',
                  f'<p><a href="{link(scene["start"])}">Twitch 원본 {stamp(scene["start"])}</a> · 발췌 {scene["duration"]}초</p>',
                  f'<video id="video-{name}" data-start="{scene["start"]}" controls preload="metadata" playsinline poster="{name}_poster.jpg" src="{name}.mp4"></video>',
                  f'<div class="controls"><button data-video="{name}" data-step="-.5">−0.5초</button><button data-video="{name}" data-step=".5">+0.5초</button><label>속도 <select data-video="{name}" aria-label="{scene["title"]} 재생 속도"><option value=".25">0.25×</option><option value=".5">0.5×</option><option selected value="1">1×</option><option value="2">2×</option></select></label><output id="time-{name}">원본 약 {stamp(scene["start"])}</output></div>',
                  '<table><thead><tr><th>시각(약)</th><th>확인한 흐름</th></tr></thead><tbody>']
        parts += ['<tr>' + ''.join('<td>' + html.escape(cell) + '</td>' for cell in row) + '</tr>' for row in scene['timeline']]
        parts += ['</tbody></table><p class="takeaway">' + html.escape(scene['takeaway']) + '</p>',
                  '<details><summary>0.5초 간격의 연속 프레임 보기</summary>']
        parts += [f'<p><a href="{path}">원본 크기로 열기</a></p><img loading="lazy" src="{path}" alt="{html.escape(scene["title"])} 연속 프레임 {i+1}">' for i, path in enumerate(scene['sheets'])]
        parts += ['</details></section>']
    md += ['## 버튼별 역할', '', '| 버튼 | 역할 |', '| --- | --- |'] + ['| ' + ' | '.join(row) + ' |' for row in mechanics]
    md += ['', '## 수정한 설명과 판독의 한계', ''] + ['- ' + text for text in corrections]
    md += ['', '## 근거', ''] + [f'- [{title}]({url})' for title, url in sources] + ['']
    parts += ['<h2>버튼별 역할</h2><table>']
    parts += ['<tr><th>' + html.escape(a) + '</th><td>' + html.escape(b) + '</td></tr>' for a, b in mechanics]
    parts += ['</table><h2>수정한 설명과 판독의 한계</h2><ul>']
    parts += ['<li>' + html.escape(text) + '</li>' for text in corrections]
    parts += ['</ul><h2>근거</h2><ul>'] + [f'<li><a href="{url}">{title}</a></li>' for title, url in sources]
    parts += ['</ul><p class="scope">추가 확인한 스킬 창</p><details><summary>스킬 이름·연결 화면 보기</summary><img loading="lazy" src="skills_001017.png" alt="00:10:17 스킬 창"><img loading="lazy" src="skills_030035.png" alt="03:00:35 스킬 창"></details></main>',
              '<script>const stamp=t=>{const h=Math.floor(t/3600),m=Math.floor(t/60)%60,s=(t%60).toFixed(1);return `${String(h).padStart(2,"0")}:${String(m).padStart(2,"0")}:${s.padStart(4,"0")}`};document.querySelectorAll("video").forEach(v=>{const show=()=>{document.getElementById(v.id.replace("video-","time-")).textContent="원본 약 "+stamp(Number(v.dataset.start)+v.currentTime)};v.addEventListener("timeupdate",show);v.addEventListener("loadedmetadata",show)});document.querySelectorAll("button[data-step]").forEach(b=>b.addEventListener("click",()=>{const v=document.getElementById("video-"+b.dataset.video);v.pause();v.currentTime=Math.max(0,Math.min(v.duration||0,v.currentTime+Number(b.dataset.step)))}));document.querySelectorAll("select[data-video]").forEach(s=>s.addEventListener("change",()=>{document.getElementById("video-"+s.dataset.video).playbackRate=Number(s.value)}));</script></html>']
    (HERE / '방송_로테이션_정밀확인.md').write_text('\n'.join(md), encoding='utf-8')
    (HERE / '방송_로테이션_정밀확인.html').write_text('\n'.join(parts), encoding='utf-8')
    manifest = {'video_id': '2867929382', 'reviewed_full_broadcast': False,
                'keystroke_log_available': False, 'timecodes_approximate': True,
                'dense_sampling_interval_seconds': .5, 'dense_frames_inspected': 128,
                'scenes': SCENES, 'clips': clip_rows,
                'interpretation': lead, 'limitations': corrections}
    (HERE / 'review_evidence.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'review_clips': len(clip_rows), 'total_excerpt_seconds': sum(x['seconds'] for x in clip_rows), 'dense_frames': 128}, ensure_ascii=False))


if __name__ == '__main__':
    main()
