"""Produce the Korean simulation evidence and an offline result viewer."""
from pathlib import Path
import hashlib,json,datetime

HERE=Path(__file__).resolve().parent; OUT=HERE.parent/'revision2'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
P={x['case']:x for x in read(HERE/'pob_results.json')}; R=read(HERE/'resource_results.json')
def active(code,name):return next(s['output'] for s in P[code]['skills'] if s['active']==name)
latest=sorted((HERE/'sources').glob('HCFR_CCTBurger_*.json'))[-1]; user=read(latest)['charModel']
tree={n['skill']:n for n in read(HERE.parent/'sources/tree_0_5.json')['nodes'].values() if 'skill'in n}
planned=read(next((OUT/'BuildPlanner').glob('01 *.build')))
ids={n['id'] for n in planned['passives']}
assert all(tree[n]['stringId'] in ids for n in user['passiveSelection'])
assert len(P)==20 and R['tests_passed']
u=P['user_current']['sets']['1'];v=P['user_current']['sets']['2']

text=f'''# 딜·회복 시뮬레이션과 HCFR_CCTBurger 추적

**판정: 초반 경로는 현재 캐릭터와 맞는다. 후기 08C는 예시 장비의 자원 유지 조건을 통과했다. 09 파콰테·메아리 전환은 보류한다.** 파일이 읽힌다는 사실과 실전 생존성은 별개다. 이전 배포본 로딩은 사용자가 확인했고, 이번에는 PoB2 계산과 별도 시간별 자원 계산을 실제로 실행했다.

## 현재 캐릭터

[HCFR_CCTBurger / CololadoBurger#7117](https://poe.ninja/poe2/profile/CololadoBurger-7117/forbiddenriteshc/character/HCFR_CCTBurger)의 공개 데이터 갱신 시각은 **{user['updatedUtc']}**, 계산에 사용한 레벨은 **{user['level']}**다. 작업 중 8→9레벨과 Smash 근접 노드 추가를 확인했다. 배정된 {len(user['passiveSelection'])}점 모두 배포 01의 근접 경로 안에 있다. 기절 축적 우회는 없다.

| 현재 장비 세트 | 생명력 | 방어도 | 막기 | 화염/냉기/번개 저항 | 생명력 재생 |
|---|---:|---:|---:|---|---:|
| I 한손 철퇴+방패 | {u['Life']:.0f} | {u['Armour']:.0f} | {u['BlockChance']:.0f}% | {u['FireResist']:.0f}/{u['ColdResist']:.0f}/{u['LightningResist']:.0f}% | {u['LifeRegen']:.1f}/초 |
| II 양손 철퇴 | {v['Life']:.0f} | {v['Armour']:.0f} | {v['BlockChance']:.0f}% | {v['FireResist']:.0f}/{v['ColdResist']:.0f}/{v['LightningResist']:.0f}% | {v['LifeRegen']:.1f}/초 |

이 저항은 액트 1의 저항 페널티 0으로 다시 계산한 값이다. poe.ninja 내보내기의 기본 -60 페널티를 그대로 읽으면 -40/-50/-54로 표시되어 초반 상태를 잘못 판단하게 된다. 실제 액트 진행과 퀘스트 선택이 달라지면 설정을 바꿔야 한다.

현재 9레벨이면 미가공 스킬 젬 3레벨로 충격파 토템을 제작해 바로 도입할 수 있다. 3레벨 충격파 토템의 캐릭터 요구는 6레벨·힘 14다. 01의 10점 완성이나 액트 1 완료를 기다리지 않고 02의 토템 스킬을 추가하며, 과잉 I·포악함 I는 확보하는 대로 연결한다. 공개 API에는 미가공 젬 보유량이 없어 실제 제작 가능 재고는 확인하지 못했다. [젬 요구 조건](https://poe2db.tw/us/Shockwave_Totem)

양손 철퇴를 얻은 상태이므로 **몰려오는 강타 I → 기절 준비 상태의 적에게 뼈 박살 II → 방패 I 복귀**를 권장한다. 실제 G 체크박스는 API에 없으므로 이 배정은 관측값이 아니라 권장안이다. II에서는 방패의 생명력·저항·막기가 사라진다. 번개 저항과 생명력이 붙은 장비를 우선 비교하고, 2차 전직용 함성 전환을 지금 당기지 않는다. 몰려오는 강타 18마나·뼈 박살 11마나에 마나 재생 {u['ManaRegen']:.1f}/초이므로 초반 연속 공격은 마나 플라스크가 필요하다.

## 실제로 돌린 계산

- 공식 커뮤니티 PoB2 **v0.23.1**, 커밋 `7d6f530cbdab20389ff8bc6ba97a37ac27f74e41`, 0.5 트리 데이터를 고정했다. 공식 `HeadlessWrapper.lua`를 LuaJIT로 실행했다. 그래픽/경로/문자 표시용 호스트만 대체했고 피해·회복 계산식과 게임 데이터는 수정하지 않았다. [릴리스](https://github.com/PathOfBuildingCommunity/PathOfBuilding-PoE2/releases/tag/v0.23.1)
- **20개 PoB 입력**: 현재 캐릭터, 배포 13단계, 같은 장비로 트리만 바꾼 비교, 함성 젬 업그레이드, 명상 제거, 메아리 제거 비교다. 각 파일의 패시브가 엔진에 전부 배정됐는지 확인했다.
- **62개 자원 시나리오**: 함성 간격·토템 수·추가 비용 해석·지속 피격량을 바꿔 최대 90초간 사용 비용, 재생, 직접 함성의 긴급한 부름 회복, 중첩 만료를 계산했다. [오프라인 결과 그래프](시뮬레이션그래프.html)
- 미래 단계 장비는 제작자의 24/34/43/46/52/74레벨 보존본이다. 현재 9레벨 사용자가 그 장비를 보유한다는 뜻이 아니다. 네이티브 플래너가 보존하지 않는 아이템 수치·젬 레벨·능력치 선택은 이 보존본을 입력 가정으로 삼았다.
- 과도한 기본 조건을 제거했다. 최대 10중첩·상시 적 디버프·상시 치명타·최종 보스 기본값을 쓰지 않았고, 플라스크/호신부도 활성화하지 않았다. 각 구간의 적 레벨·저항 페널티를 명시했다. 후기 토템 수는 정신력으로 가능한 **4기**로 제한했다.

## 전환별 딜과 회복

함성 피해는 **타락한 피 1중첩의 초당 피해**다. 현재 중첩과 실제 적용 시간을 곱해야 한다. 아래 수치는 각 단계의 가정 장비/적 조건에 해당하며 서로 다른 단계 전체를 동일 조건의 성능 순위로 읽지 않는다.

| 단계 | 가정 캐릭터/적 레벨 | 세트 I 생명력 | I 재생/초 | II 재생/초 | 함성 유효 레벨 | 타락한 피 1중첩/초 | 함성 1회 마나/생명력 |
|---|---|---:|---:|---:|---:|---:|---|
'''
for code in ('05A','06','07','08','08A','08B','08B_gem15','08C_gem15','09'):
    r=P[code]; cry=next(x for x in r['skills'] if x['active']=='Fortifying Cry'); dot=next(x for x in r['skills'] if x['active'] in ('Corrupted Cry','Twisted Pact'))
    a=r['sets']['1'];b=r['sets']['2'];c=cry['output'];suffix=' (추가 비용 제외·메아리 감폭 전)' if code=='09' else ''
    text+=f"| {code} | {r['character_level']}/{r['enemy_level']} | {a['Life']:.0f} | {a['LifeRegen']:.1f} | {b['LifeRegen']:.1f} | {cry['effective_gem_level']} | {dot['output']['CorruptingBloodDPS']:.0f}{suffix} | {c['ManaCost']:.0f}/{c['LifeCost']:.0f} |\n"
text+='''
`gem15`는 기본 15레벨 함성 젬을 넣어 후기 장비에서 유효 17레벨이 된 비교다. 레벨 65+ 캠페인은 07로 계산했고, 08 이후 후기 준비는 74레벨 가정이다. 레벨만으로 전환하도록 만들지 않았다.

1. **05A 정신력 부족 수정.** 구장비 정신력 60에 마그마 장벽 30+활력 I 20+명상 II 20을 넣으면 10 부족했다. 기본 연결에서 명상 II를 제거해 잔여 10으로 만들었다. 원본 06의 연결은 보존하되 총 정신력 70 이상일 때만 명상을 켜도록 했다.
2. **05A→06은 장비 없이 환불하면 손해다.** 같은 구장비·같은 젬·같은 적 조건에서는 1중첩 피해 261→254, 세트 I 재생 49.3→39.0/초였다. 46레벨 원본 장비의 475는 스킬 레벨 상승 등이 포함된 결과다. 16개 환불만으로 그 피해를 얻는다고 안내하지 않는다.
3. **05A·06은 마나 플라스크 단계다.** 토템 2기·함성 초당 1회·플라스크 없음 조건에서 약 6.6초/5.6초에 다음 비용을 낼 마나가 부족했다. 지속 사용 시험에는 마나 플라스크가 필요하며, 회복이 모자라면 함성 빈도를 낮추고 토템을 유지한다. 이 계산은 사냥 중 처치 회복을 포함하지 않는다.
4. **08A는 마을에서 지나가는 준비 단계다.** 08→08A에서 구장비 세트 I 재생은 106.5→81.2/초로 감소했다. 기존 함성 피해는 늘어도 회복과 토템 특화가 떨어지므로 이 상태로 파밍할 이유가 없다.
5. **08B에서 함성 젬을 같이 올린다.** 후기 셉터로 교체하면서 구형 함성 젬을 유지하면 유효 16→14로 낮아지고 1중첩 피해 847→689가 된다. 기본 15레벨 젬 비교에서는 유효 17레벨·1090이었다. 08B는 마나 플라스크를 둔 짧은 전환 시험이며, 4기·초당 함성 1회는 플라스크 없이 약 13초에 마나가 부족했다.
6. **02→03 안내도 바로잡았다.** 과잉 I 제거의 한도 -1과 1차 전직 응답받은 부름의 한도 +1이 상쇄된다. 보조를 먼저 바꾸면 한도가 줄 수 있으므로 전직 획득을 함께 확인한다. PoB의 초반 토템 한도 처리가 불완전해 02/03의 합산 토템 DPS는 확정값으로 제시하지 않는다.

## 08C: 생명력 비용을 유지할 수 있는가

유효 함성 17레벨 예시에서 함성은 생명력 **52/회**, AWT는 **72/기**다. 토템 내부 지면 분쇄가 표시하는 공격 비용을 플레이어에게 매 공격마다 또 청구하지 않았다. 토템 지속시간 13.002초와 설치 동작을 반영해 다시 설치한다.

양 세트 중 낮은 생명력 **1876**, 재생 **108.6/초**를 전체 시간에 적용했다. 직접 함성을 쓸 때 긴급한 부름의 2% 회복 **37.52**를 별도로 더했다. 시체/처치 회복·흡수·플라스크·가드·막기 효과는 계산하지 않았다. 두 무기 세트의 다른 최대 생명력 때문에 발생하는 교체 순간의 정확한 변동도 모델 밖이며, 낮은 최대치를 공통 기준으로 사용했다.

| AWT 4기, 함성 1초 간격 | 90초 비용 지불 | 최소 생명력 | 해석 |
|---|---|---:|---|
| 적 피해 없음 | 완료 | 87.1% | 사용 비용 자체는 유지 |
| 경감 후 지속 피해 50/초 가정 | 완료 | 84.7% | 임의의 낮은 지속 피해 민감도 |
| 경감 후 지속 피해 100/초 가정 | 약 66.3초에 비용 부족 | 약 0.6% | 피격까지 무한 감당하지 못함 |

50/100은 실제 몬스터의 피해량이 아니라 민감도 입력이다. **가속 마법/희귀 20마리의 공격, 강타, 기절, 바닥 피해를 재현한 시험이 아니다.** 자원 유지 통과를 하코 생존 통과로 바꾸어 읽으면 안 된다.

이 조건에서 타락한 피의 시간 평균 피해는 약 **4300/초**였다. 유효 지속시간 4.059초에 초당 1회 적용하므로 10중첩 상시 유지로 계산하지 않는다. AWT 지면 분쇄 기본 타격은 4기 구성에서 **1기당 약 4514/초**, 4기가 모두 적을 공격한다는 가정의 기본 타격+함성 부분합은 약 **2.24만/초**다. 가시 폭발·요철 지대·선대의 영혼·맵 접사와 전투 중 이탈 시간은 이 합산에 넣지 않았다. 처치 시간이나 모든 보스의 충분한 딜을 보증하는 수치는 아니다.

후기 정신력은 버프를 켠 뒤 토템 설치 전 I **312**, II **324**이고, 4기 예약 후 각각 **12/24**가 남는다. 4기보다 더 놓는 계산은 이 장비에서 성립하지 않는다. 선대의 유대는 토템당 75 정신력을 예약하고 충전 요구를 없애지만 마나/생명력 설치 비용을 없애지 않는다. [공식 0.5 패치](https://www.pathofexile.com/forum/view-thread/3932540)

## 09: 파콰테·메아리는 아직 확정할 수 없다

PoB의 함성 기본 생명력 비용 129에는 **파콰테의 최근 사용/발동에 따른 최대 생명력 추가 비용이 빠져 있다.** 메아리의 반복·이동 조건과 피해 감폭도 해당 엔진 출력에서 자동 처리되지 않는다. 따라서 표시 DPS와 재생 수치만으로 09를 승인하지 않는다. 파콰테와 메아리의 효과 정의는 [파콰테 데이터](https://poe2db.tw/us/Paquates_Pact), [메아리 데이터](https://poe2db.tw/us/Echoing_Cry)에 있다.

별도 계산에서는 직접 사용 뒤 **1.3초/2.6초에 반복**을 넣고, 매 직접 사용 전에 **10미터를 이동했다는 조건**을 둔다. 반복도 대상에게 닿는다고 가정했다. 최근은 4초, 파콰테는 1회에 5중첩, 전체 한도 10이며 각 중첩을 4.059초 뒤 만료시켰다. 메아리의 40% 피해 감폭을 타락한 피에 수동 적용한 비교다. 실제 적용 범위와 중첩 갱신 방식이 다르면 피해가 달라진다. [최근 용어](https://poe2db.tw/us/Recently)

추가 비용의 **현재 사용 포함 시점, 반복마다 기본 비용도 다시 내는지, 추가 퍼센트 비용에 비용 배율이 어디까지 적용되는지**는 실제 게임에서 확인하지 못했다. 다음은 정답의 상하한이 아니라 각 해석을 넣은 민감도다.

| 적 피해 없음·AWT 4기 | 이전 사용만 추가 비용에 집계 / 반복 기본 비용 0 가정 | 현재 사용 집계 / 반복 기본 비용도 지불 가정 |
|---|---|---|
| 직접 함성 4초 간격 | 약 7.5초에 비용 부족 | 약 4.9초에 비용 부족 |
| 직접 함성 8초 간격 | 90초 완료, 최소 생명력 62.2% | 약 11.5초에 비용 부족 |

유리한 가정에서도 08C보다 생명력 여유가 크게 줄고, 비용 해석에 따라 유지 가능 여부가 바뀐다. **따라서 현재 권장은 08C 유지다.** 09 파일은 제작자의 원본 구조를 보존한 참고 단계이며, 요구 레벨을 채웠다는 이유로 자동 전환하지 않는다. 실제 비용이 확인된 뒤 사용자 장비로 다시 계산해야 한다. 이 비교로 제작자의 실전 빌드가 작동하지 않는다고 결론 내리지도 않는다.

## 계산 한계와 재현

- PoB는 전투 AI 시뮬레이터가 아니다. 현재 도구로 의식 20마리의 접근·가속·회복 후 추격·충돌·동시 타격을 그대로 재현했다고 주장하지 않는다.
- 파콰테 추가 비용과 메아리 반복/피해 감폭은 원본 `sup_str.lua`의 상수에는 있으나 필요한 계산 연결이 없다. 초반 과잉의 `base_limit_+`는 `SkillStatMap.lua`에서 추가 쿨다운 사용으로 매핑되고, 실제 토템 한도와 지속시간 출력도 기대 효과를 반영하지 않아 총 토템 DPS 판정을 제외했다. 엔진 결함을 플레이 가능한 젬 조합의 불가능 판정으로 바꾸지 않았다.
- 긴급한 부름의 사용 시 회복은 별도 사건으로 반영했다. 반복 사용의 회복은 인정하지 않았고, 직접 사용만 인정했다. 생명력 비용을 지불할 수 있어야 그 후 회복이 발생하는 모델이다.
- 4기 수를 PoB에 명시하지 않으면 이 내보내기의 기본 10기 설정이 토템 수에 따른 피해 보정까지 부풀린다. 최종 수치는 4기로 다시 계산했다.
- 같은 젬의 여러 구성 요소가 있으므로 단순한 `TotalDPS` 하나를 완성 빌드 DPS로 사용하지 않았다. 함성 본체가 아니라 실제 발동된 Corrupted Cry/Twisted Pact를 선택했다. 이번에는 AWT 기본 타격·함성 피해를 확인했고 가시 폭발/요철 지대/선대의 영혼 전체 피해는 미완료다.
- PoB 시작 시 공개 트리의 14개 누락 연결 경고가 발생했다. 모든 이번 배정 노드가 엔진에 실제 존재하고 배정됐다는 별도 검사는 통과했다. 경고 자체를 삭제하거나 숨기지 않았다.
- 이번 결과에 맞춰 13개 플래너의 한국어 설명과 05A 연결을 수정했다. 필터 3개는 이전 검사본과 같다. 이전 배포본 로딩은 사용자 확인이며 수정 파일의 게임 재로딩·실전 조작은 별도 확인되지 않았다.

상위 배포 폴더 `simulation/`에 `pob_headless.py`, `run_scenarios.py`, `resource_model.py`, `write_report.py`, 20개 입력 XML, `pob_results.json`, `resource_results.json`, 시간별 사용자 API 보존본을 남겼다. 수정 전 결과와 플래너는 `before_simulation_corrections/`에 보존했다. 엔진은 작업공간 `.tmp/skadoosh-simulation/pob2`, Python Lua 런타임은 같은 경로의 `python-runtime`에만 설치했다.

작업공간에서 재현:

```powershell
python -B deliverables/skadoosh_hc_2026-09-07/simulation/run_scenarios.py
python -B deliverables/skadoosh_hc_2026-09-07/simulation/resource_model.py
python -B deliverables/skadoosh_hc_2026-09-07/simulation/write_report.py
```

캐릭터 공개 데이터는 캐시 때문에 지연될 수 있다. 이번 추적은 작업 중 갱신한 기록이며, 응답이 끝난 뒤 상시 감시하는 작업을 설치한 것은 아니다. 다음 장비/젬/액트 변화도 이 캐릭터 링크를 기준으로 비교한다.
'''
(OUT/'시뮬레이션결과.md').write_text(text,encoding='utf-8')

data=json.dumps(R['cases'],ensure_ascii=False).replace('</',r'<\/')
html='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Skadoosh 딜·회복 계산</title>
<style>body{font:16px/1.6 system-ui,sans-serif;max-width:1050px;margin:32px auto;padding:0 20px;color:#e6eaf0;background:#10161e}h1{font-size:26px}a{color:#9dccff}select{width:100%;padding:12px;background:#202a38;color:#fff;border:1px solid #58708a;border-radius:6px}canvas{width:100%;background:#17202b;border-radius:8px;margin-top:16px}#result{font-size:18px}small{color:#b8c2ce}table{border-collapse:collapse}td,th{padding:6px 16px;border-bottom:1px solid #344254}button{padding:8px 16px}</style>
<h1>시간별 생명력·마나 계산</h1><p>PoB2 장비 가정 + 90초 사건 계산. <strong>적 AI와 의식 20마리 전투를 재현한 결과가 아닙니다.</strong></p>
<p><a href="시뮬레이션결과.md">한국어 판정·입력 가정·계산 한계 읽기</a></p><label for="scenario">계산한 시나리오 선택</label><select id="scenario"></select><p id="result" aria-live="polite"></p>
<canvas width="1000" height="380" id="chart" aria-label="선택 시나리오의 시간별 생명력과 마나 비율"></canvas><p id="detail"></p>
<small>초록: 생명력, 파랑: 마나. 사건 직후 기록 사이를 연결한 그래프입니다. 비용을 낼 수 없어 중단된 결과는 중단 시점에서 선이 끝납니다. 파콰테 비용 해석은 미확정 가정이며 실제 사용법의 확정값이 아닙니다.</small>
<script>const rows=__DATA__;
const labels={normal:'파콰테 없음',pact_prior_only:'파콰테: 이전 사용 집계·반복 기본 비용 0',pact_current:'파콰테: 현재 사용 포함·반복 기본 비용 0',pact_repeated_base:'파콰테: 현재 사용 포함·반복 기본 비용 지불',pact_stress:'파콰테: 반복 비용 지불·추가 비용 ×1.5 민감도'};
const select=document.querySelector('#scenario');rows.forEach((r,i)=>{const o=document.createElement('option');o.value=i;o.textContent=`${r.case} · 함성 ${r.interval}초 · 토템 ${r.totems}기 · 피격 ${r.incoming_post_mitigation_dps}/초 · ${labels[r.policy]}`;select.append(o)});
select.value=rows.findIndex(r=>r.case==='08C_gem15'&&r.interval===1&&r.totems===4&&r.incoming_post_mitigation_dps===0);
function draw(){const r=rows[Number(select.value)],c=document.querySelector('#chart'),x=c.getContext('2d');x.clearRect(0,0,1000,380);x.font='14px system-ui';x.strokeStyle='#354559';x.fillStyle='#b8c2ce';for(let y=0;y<=100;y+=25){let py=325-y*2.7;x.beginPath();x.moveTo(60,py);x.lineTo(960,py);x.stroke();x.fillText(y+'%',10,py+5)}for(let t=0;t<=90;t+=10)x.fillText(t+'초',60+t*10-10,355);
function line(key,total,color){if(!total)return;x.strokeStyle=color;x.lineWidth=2.5;x.beginPath();x.moveTo(60,55);for(const p of r.trace)x.lineTo(60+p.t*10,325-p[key]/total*270);x.stroke()}
line('life',r.life,'#64dfa3');line('mana',r.mana,'#72b7ff');
document.querySelector('#result').textContent=r.completed?`90초 비용 지불 완료 · 최소 생명력 ${r.min_life_percent}%`:`${r.first_failure.time.toFixed(1)}초에 중단 · ${r.first_failure.reason==='mana_cost'?'마나 비용 부족':r.first_failure.reason==='life_cost'?'생명력 비용 부족':'지속 피해로 생명력 고갈'}`;
document.querySelector('#detail').textContent=`생명력 ${r.life}, 보수적 재생 ${r.life_regen_conservative}/초, 직접 함성 회복 ${r.manual_warcry_life_recovery}/회. 중단 전 타락한 피 평균 ${r.average_corrupted_blood_dps_until_stop}/초. ${r.movement_prerequisite?'직접 사용마다 10미터 이동, 반복이 대상에게 적중한다는 가정.':''}`;
}select.addEventListener('change',draw);draw();</script></html>'''.replace('__DATA__',data)
(OUT/'시뮬레이션그래프.html').write_text(html,encoding='utf-8')
manifest={'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pob_cases':20,'resource_cases':len(R['cases']),
          'user_source':str(latest),'user_updated_utc':user['updatedUtc'],'user_level':user['level'],'user_nodes_match_stage01':True,
          'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [HERE/'pob_results.json',HERE/'resource_results.json',OUT/'시뮬레이션결과.md',OUT/'시뮬레이션그래프.html']}}
(HERE/'validation_simulation.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Wrote Korean report and offline viewer: {len(R["cases"])} scenarios, user level {user["level"]}.')
