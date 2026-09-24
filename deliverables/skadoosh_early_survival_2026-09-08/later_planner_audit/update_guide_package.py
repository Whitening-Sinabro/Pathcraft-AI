"""Publish the audited transition notes without regenerating older guide sections."""
from pathlib import Path
import hashlib
import json
import re
import sys
import zipfile
import markdown

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ROOT = BASE.parent.parent
sys.path.insert(0, str(BASE))
from later_transitions import TRANSITIONS

docs = ROOT / 'Docs'
stem = '2026-09-05_SKADOOSH_CORRUPTING_CRY_TOTEM_WARBRINGER_0_5_5'
md = docs / (stem + '_RESEARCH.md')
page = docs / (stem + '_GUIDE_DOC.html')
text = md.read_text(encoding='utf-8')
link = '../deliverables/skadoosh_early_survival_2026-09-08/later_planner_audit/후속_플래너_정밀확인.html'
top = ('<!-- later-audit-summary:start -->\n'
       '**03~07 후속 플래너 재확인:** [실제 스킬 제거·보조 이동·장비 교체 영상 12개](' + link + '). '
       '04의 효율 I→II 중간 단계와 포악함 II 2개, 05에서 빠지는 스킬 전체, 06의 효율 II 이동, 07의 별도 성장 항목을 반영했다. '
       '아래 표는 성장 후 연결 목표이며 진입 순간의 필수 목록과 구분한다. 05·06은 당시 전체 트리 복제본이 아닌 기존 Pathcraft 전환안이다.\n'
       '<!-- later-audit-summary:end -->\n\n')
if '<!-- later-audit-summary:start -->' in text:
    text = re.sub(r'<!-- later-audit-summary:start -->.*?<!-- later-audit-summary:end -->\n\n', lambda _: top, text, count=1, flags=re.S)
else:
    first_break = text.index('\n\n') + 2
    text = text[:first_break] + top + text[first_break:]

for stage, note in TRANSITIONS.items():
    anchor = f'<a id="stage-{stage:02}"></a>'
    start = text.index(anchor)
    end = text.find('<a id="stage-', start + len(anchor))
    if end < 0:
        end = len(text)
    part = text[start:end]
    mark = f'<!-- later-transition-{stage:02}:start -->'
    block = (mark + '\n**방송 대조 · 교체와 성장:** ' + note.split('\n', 1)[1] + '\n\n'
             '[장면과 확인 범위](' + link + ')\n' + f'<!-- later-transition-{stage:02}:end -->\n\n')
    if mark in part:
        part = re.sub(re.escape(mark) + rf'.*?<!-- later-transition-{stage:02}:end -->\n\n', lambda _: block, part, count=1, flags=re.S)
    else:
        pos = part.index('### 스킬에 넣을 젬')
        part = part[:pos] + block + part[pos:]
    part = part.replace('### 스킬에 넣을 젬\n', '### 스킬에 넣을 젬 · 성장 후 연결 목표\n')
    if stage == 3:
        part = part.replace('빠른 공격 I + 긴급한 토템 I + 포악함 II', '빠른 공격 I + 포악함 II + 긴급한 토템 I')
    if stage == 4:
        part = part.replace('네 번째 소켓/효율 II는 나중에 추가해도 된다.', '처음 3보조로 시험하고 네 번째 효율 I를 추가한 뒤 II로 올릴 수 있다.')
        part = part.replace('**사용 순서:** 희귀/보스는 충격파 토템(II)부터 설치 → 보강하는 함성(I) → 이동 → 남은 적과 마나 확인. 잡몹은 함성 한 번 후 이동한다. 토템이 살아 있는 동안 제자리 연타를 줄인다.',
                            '**사용 순서:** 일반 무리는 보강하는 함성(I)을 쓰며 이동한다. 밀집 무리·희귀·보스에서 충격파 토템(II)을 보태고 함성(I)으로 복귀한다. 토템 유지·함성 갱신 사이에 회피하고 마나를 확인한다. 이 단계에는 메아리가 없으므로 06의 이동 조건을 적용하지 않는다.')
    if stage == 5:
        part = part.replace('마을에서 트리·무기·젬을 맞추고 혈마법은 마지막에 찍는다.',
                            '권장 작업 순서는 마을에서 트리·무기·젬을 맞춘 뒤 혈마법을 찍는 것이다. 방송은 젬 정리보다 먼저 혈마법을 선택했으므로 실제 클릭 순서와 구분한다.')
    text = text[:start] + part + text[end:]
assert all(text.count(f'<!-- later-transition-{s:02}:start -->') == 1 for s in TRANSITIONS)
assert '\ufffd' not in text
md.write_text(text, encoding='utf-8')
outer = page.read_text(encoding='utf-8')
assert outer.count('<main>') == outer.count('</main>') == 1
body = markdown.markdown(text, extensions=['tables', 'fenced_code', 'md_in_html'])
outer = outer.split('<main>', 1)[0] + '<main>' + body + '</main>' + outer.split('</main>', 1)[1]
page.write_text(outer, encoding='utf-8')

archive = BASE / 'Skadoosh-현재플래너.zip'
with zipfile.ZipFile(archive) as old:
    readme = old.read('README.md').decode('utf-8')
readme = readme.replace('2026-09-08 초반 스킬 교체 재확인 반영.', '2026-09-08 초반 및 03~07 후속 스킬 교체 재확인 반영.')
header = '\n## 03~07 후속 재확인\n'
readme = readme.split(header)[0] + header + '\n'
for stage, note in TRANSITIONS.items():
    readme += note + '\n\n'
readme += ('완성 연결과 전환 첫 연결을 구분했다. 05·06은 당시 전체 트리의 정확한 복제본이 아닌 Pathcraft 전환안이다. '
           '게임 내 재불러오기와 G 무기 세트 체크는 직접 확인한다.\n')
builds = sorted((BASE / 'BuildPlanner').glob('*.build'))
assert len(builds) == 7
with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as out:
    for build in builds:
        out.write(build, 'BuildPlanner/' + build.name)
    out.writestr('README.md', readme)
with zipfile.ZipFile(archive) as check:
    assert check.testzip() is None
    assert len(check.namelist()) == 8
    for build in builds:
        assert check.read('BuildPlanner/' + build.name) == build.read_bytes()
record = {'guide_markdown': str(md), 'guide_html': str(page), 'archive': str(archive),
          'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
          'archive_builds_match_generated': True, 'stage_sections_updated': list(TRANSITIONS)}
(HERE / 'guide_package_validation.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(record, ensure_ascii=False))
