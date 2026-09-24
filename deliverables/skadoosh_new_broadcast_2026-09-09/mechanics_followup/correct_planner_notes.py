"""Correct reservation wording only; preserve build structure and unrelated files."""
from pathlib import Path
import copy, hashlib, json, shutil, zipfile
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EARLY = ROOT / 'deliverables/skadoosh_early_survival_2026-09-08'
GAME = Path('C:/Users/User/Documents/My Games/Path of Exile 2/BuildPlanner')
REPLACEMENTS = {
    '정밀함의 추가 점유까지 합산해 버프를 켜고 토템 설치 전 I·II 각각 남는 정신력을 확인한다. 4기 목표는 각 300이다.':
    '성소 셉터의 순수함은 보조 툴팁 점유를 실제 추가 점유로 단정하지 않는다. 버프를 켠 뒤 G에서 토템 설치 전 I·II 각각 실제 남는 정신력을 확인한다. 4기 목표는 각 300이다.',
    '추가 정신력 점유 20을 포함해 양 세트의 남는 정신력을 확인한다.':
    '보조 툴팁의 추가 점유 20을 성소 셉터의 실제 추가 점유로 단정하지 않는다. 9월 9일 방송의 순수함 연결은 단순 합산과 맞지 않으므로, 버프를 켠 뒤 G에서 양 세트의 실제 남는 정신력을 확인한다.',
    '따뜻한 피·정밀함 II 추가 뒤 버프 점유를 합산한다. 토템 설치 전 남는 정신력 300을 I와 II에서 각각 확보해야 4기를 유지한다.':
    '따뜻한 피·정밀함 II 연결 뒤 버프를 켜고 G에서 실제 점유를 확인한다. 성소 셉터의 순수함에 연결한 보조는 툴팁 점유의 단순 합산과 다를 수 있다. 토템 설치 전 남는 정신력 300을 I와 II에서 각각 확보해야 4기를 유지한다.',
}

def digest(data):
    return hashlib.sha256(data).hexdigest()

def replace(s):
    for old, new in REPLACEMENTS.items():
        s = s.replace(old, new)
    return s

def without_notes(value):
    if isinstance(value, dict):
        return {k: without_notes(v) for k, v in value.items() if k not in ('description', 'additional_text')}
    if isinstance(value, list):
        return [without_notes(v) for v in value]
    return value

def main():
    backup = HERE / 'planner_note_backups'
    backup.mkdir(exist_ok=True)
    archive = EARLY / 'Skadoosh-현재플래너.zip'
    plans = []
    for p in sorted((EARLY / 'BuildPlanner').glob('0[5-7]*.build')):
        before = p.read_bytes()
        old = json.loads(before.decode('utf-8-sig'))
        text = replace(before.decode('utf-8-sig'))
        after = text.encode('utf-8')
        new = json.loads(text)
        assert without_notes(old) == without_notes(new), p.name
        installed = GAME / p.name
        assert installed.read_bytes() in (before, after), f'User-modified installation: {installed}'
        plans.append((p, before, after, installed))
    assert len(plans) == 3
    with zipfile.ZipFile(archive) as z:
        members = [(i, z.read(i.filename)) for i in z.infolist()]
    for p, before, after, installed in plans:
        entry = next(data for i, data in members if i.filename == 'BuildPlanner/' + p.name)
        assert entry in (before, after), p.name
    changes = []
    for p in [EARLY / 'stage_05_06_progression.py', EARLY / 'later_transitions.py']:
        before = p.read_bytes()
        after = replace(before.decode('utf-8-sig')).encode('utf-8')
        compile(after.decode('utf-8'), str(p), 'exec')
        if before != after:
            (backup / (p.name + '.' + digest(before)[:12])).write_bytes(before)
            p.write_bytes(after)
        changes.append({'source': str(p), 'sha256': digest(after)})
    untouched_before = {p.name: digest(p.read_bytes()) for p in GAME.glob('*.build') if p.name not in {x[0].name for x in plans}}
    for p, before, after, installed in plans:
        if before != after:
            (backup / (p.stem + '.' + digest(before)[:12] + '.build')).write_bytes(before)
            p.write_bytes(after)
            installed.write_bytes(after)
        assert p.read_bytes() == installed.read_bytes() == after
        changes.append({'planner': p.name, 'before_sha256': digest(before), 'after_sha256': digest(after), 'structure_unchanged': True, 'installed_matches': True})
    updates = {'BuildPlanner/' + p.name: after for p, before, after, installed in plans}
    if any(updates.get(i.filename, data) != data for i, data in members):
        archive_bytes = archive.read_bytes()
        (backup / ('Skadoosh-current.' + digest(archive_bytes)[:12] + '.zip')).write_bytes(archive_bytes)
        temporary = archive.with_name(archive.name + '.mechanics.tmp')
        with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED) as z:
            for i, data in members:
                z.writestr(i, updates.get(i.filename, data))
        temporary.replace(archive)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for p in (EARLY / 'BuildPlanner').glob('*.build'):
            assert z.read('BuildPlanner/' + p.name) == p.read_bytes()
        for i, data in members:
            if i.filename not in updates:
                assert z.read(i.filename) == data
    assert untouched_before == {name: digest((GAME / name).read_bytes()) for name in untouched_before}
    result = {'checked_utc': datetime.now(timezone.utc).isoformat(), 'scope': '05/06/07 reservation notes only', 'changes': changes, 'zip_all_seven_match': True, 'other_installed_builds_unchanged': True, 'game_ui_reload_checked': False}
    (HERE / 'planner_note_validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))

if __name__ == '__main__':
    main()
