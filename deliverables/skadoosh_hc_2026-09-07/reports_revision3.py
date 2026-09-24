"""Player-facing audit conclusions and an offline interactive resource chart."""
from pathlib import Path
import html,json
from revision3_data import HERE,OUT,BUILDS,ORIGINS,KO
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
rows=read(HERE/'progression_v3.json');pob=read(HERE/'simulation/v3_pob_results.json');resources=read(HERE/'simulation/v3_resource_results.json')
start=['# 시작 안내 · 방송 대조 v3','','현재 캐릭터가 초반 근접 단계라면 미가공 스킬 젬 3레벨에서 충격파 토템을 만들고, 캐릭터 6레벨·힘 14를 만족한 즉시 **02**를 선택한다. 트리 29점을 다 찍거나 1차 전직을 끝낼 때까지 토템 도입을 미루지 않는다.','',
 '## 파일 고르기','','| 파일 | 이때 사용 | 패시브 완성 목표 |','|---|---|---|']
why=['토템을 배우기 전 근접 시작','충격파 토템을 배우고 1차 전직까지','대장간 망치 도입부터 2차 전직까지','타락시키는 비명 I 함성·충격파 토템, 마나 유지','정신력·장비·회복 준비 후 전사 토템/혈마법','65레벨 이후 파콰테 비용 시험을 통과했을 때','후기 장비와 패시브 확장 목표']
for row,desc in zip(rows,why):start+=[f"| {row['file'][:-6]} | {desc} | 일반 {row['ordinary']} / 특화 {row['sets'][0]}·{row['sets'][1]} / 전직 {row['ascendancy']} |"]
start+=['','레벨 숫자만 보고 다음 파일로 넘어가지 않는다. **65레벨 이상이어도 캠페인이면 캠페인 필터**, 전환 장비가 없으면 04를 유지한다. 전사 토템은 실제 제작자가 54레벨에 도입했지만, 사용자에게 54레벨 전환을 강제하지 않는다. 05의 69점은 재구성한 최소 목표이며 여유 점수는 회복·방어 11점을 먼저 확장해 총 80점으로 간다. 파콰테가 없어도 이 방어 확장을 사용할 수 있다. 97점은 최종 목표다.','',
 '## 무기와 젬','','01~04: I는 한손 철퇴+방어도 방패, II는 한손 철퇴+공유 방패. 토템 II와 나머지 주요 스킬 I를 직접 지정한다. 시작 시 철퇴 하나뿐이면 무기/방패를 공유한다. 양손 철퇴를 필수로 쓰는 단계는 없다.','',
 '05 이후: I는 성소 셉터+방어도 방패, II는 한손 철퇴+성소 셉터. 선대의 전사 토템은 II만 체크하고 설치 뒤 I의 함성으로 돌아온다. **지면 분쇄는 선대의 전사 토템 안에 넣는다.** 다른 보조와 함께 토템의 소켓에 넣으며 수동 공격 버튼으로 쓸 필요가 없다.','',
 '보강하는 함성의 파콰테·메아리 연결과 지진 함성의 우주의 영사·효율 II·격노하는 함성을 섞지 않는다. 파콰테 함성 한 번 → 이동/메아리 대기, 그 사이 지진 함성으로 토템의 가시를 터뜨린다. 모든 연결과 추천 장비 옵션은 게임의 각 스킬·장비 설명과 무기세트와젬연결.md에 넣었다.','',
 '## 전환 전 확인','','05 전환 전에는 원소 저항을 현재 최대치(기본 75%)까지 보강하고 양 무기 세트에서 장비와 젬이 켜지는지 본다. 버프를 켠 상태에서 토템 설치 전 남는 정신력이 **I·II 각각 300 이상**이어야 4기를 유지한다. 부족하면 예약 버프를 조절하거나 장비/영구 보상을 먼저 확보한다. 토템 설치 비용은 이 예약과 별개다.','',
 '마을에서 젬·장비와 환불 비용을 준비해 패시브전환.md 순서대로 바꾼다. 혈마법은 마지막이다. 낮은 지역에서 토템과 함성을 평소처럼 쓰고 생명력이 회복되는지 본다. 주력 함성의 유효 젬 레벨이 셉터 교체로 낮아지는 것도 확인한다. 04에는 마나 비용의 일부를 생명력으로 바꾸는 노드가 있으므로 혈마법 전에도 두 자원을 모두 본다.','',
 '06은 조건부 단계다. 실제 반복 비용이 아직 정량 확정되지 않았으므로 파콰테 연결 후 생명력이 누적해서 내려가면 05의 타락시키는 비명 I·효율 II로 즉시 되돌린다. 05에서도 설치만으로 큰 손실이 누적되면 혈마법을 되돌리고 장비·회복을 보강한다. 마나 상태는 짧은 시험용이며 마나 플라스크 없이 무한 유지된다는 뜻이 아니다.','',
 '## 의식에서의 운영','','시작 전에 토템을 놓을 자리와 계속 움직일 공간을 확보한다. 가속 마법/희귀 무리가 한꺼번에 접근할 때는 토템 재설치·함성 연타 때문에 멈춰 있는 시간을 줄인다. 기절한 적도 회복 후 다시 추격하므로 기절만 믿고 같은 위치에 남지 않는다. 방송의 시각 효과 누적/프레임 저하가 나타나면 해당 지역에서 무리한 진행을 피하고 상태를 먼저 확인한다. 빌드·필터가 가속 몹 20마리의 동시 공격 생존을 보장하지는 않는다.','',
 '## 필터와 설치','','- 01-Campaign: 캠페인 진행, 캐릭터 65레벨 이상 포함.\n- 02-EarlyMaps: 캠페인 완료 후 초반 지도와 장비 보강.\n- 03-SettledMaps: 지도/장비가 안정되고 더 정리가 필요할 때.','',
 '세 필터는 같은 명세에서 생성한다. 한손 철퇴·방패·정신력 후보를 보강하며 양손 철퇴 전용 추가 강조는 제거했다. 필터는 미감정 장비의 생명력·저항 옵션을 알 수 없다. 감정 후 장비 칸의 추천 옵션과 비교한다.','',
 '플래너 폴더: `C:/Users/User/Documents/My Games/Path of Exile 2/BuildPlanner`\n필터 폴더: `C:/Users/User/Documents/My Games/Path of Exile 2`','',
 '플래너는 7개다. 첫 단계의 실제 파일명은 기존 캐릭터의 선택 경로를 보존하기 위해 `01 시작-근접 기초.build`를 유지하며 게임 표시명은 `01 시작 - 근접과 방패`다. 내용은 최신 방송 대조본이다. 나머지 6개는 표의 표시명과 파일명이 같다. 기존 파일 13개의 원본을 백업했고, 첫 단계 경로를 제외한 이전 12개는 활성 목록에서 제외했다. 게임 로그에서 7개 모두 정상 로드를 확인했고 실제 게임의 02 단계 트리 표시도 확인했다. `unrecognised build plan id`는 이번 설치에서 선택 중이던 파일 경로를 바꾼 뒤 남은 참조와 일치했으며, 첫 단계의 원래 경로를 복원했다.','',
 '## 근거와 한계','','방송대조보고서.md에는 3일 방송 전체 전사 대조 방법과 원본 타임스탬프를, 시뮬레이션결과.md에는 변경된 구성의 계산과 한계를 기록했다. 05의 전체 트리는 제작자 54레벨 그대로의 복제본이 아니다. 파콰테 반복 비용, 가시 전체 명중을 합친 실전 DPS, 의식 다수 피격 생존은 확정하지 못했다. 실전 무사망을 뜻하는 “완벽”으로 표시하지 않는다.','']
(OUT/'시작안내.md').write_text('\n'.join(start),encoding='utf-8')

def output(case,name):return next(x['output'] for r in pob if r['case']==case for x in r['skills'] if x['active']==name)
sim=['# 시뮬레이션 결과 · v3','','변경된 7단계와 하코 방어 확장을 기준으로 **PoB 10개 입력**, **90초 자원 계산 45개 조건**을 계산했다. 게임 엔진 전투 재현이 아니라 PoB2 v0.23.1의 실제 트리/젬 계산과 별도의 자원 사건 모델이다. 원본 PoB의 식이나 게임 데이터는 패치하지 않았다.','',
 '## 무엇을 비교했나','','02·03은 24·43레벨 공개 장비, 04는 52레벨 공개 장비를 캐릭터 65레벨/지역 55로 계산했다. 05·06은 52레벨 장비에서 후기 보존본의 성소 셉터 2개와 정신력 갑옷만 교체한 **대체 장비 시나리오**다. 철퇴는 기존 희귀 Morning Star이고 67레벨 고유를 쓰지 않았다. 기본 정신력 100을 위한 Lythara 영구 보상 완료, 기본 13레벨 함성/AWT와 11레벨 지면 분쇄를 가정했다. 실제 54레벨 장비를 전부 복원한 계산은 아니다.','',
 '07은 74레벨 보존본의 장비/젬이다. 버프는 각 무기 세트에서만 적용하고 중복 자동 부여 그룹을 제거했다. 계산의 낮은 재생 값을 두 세트 전체에 적용하며 플라스크·처치 회복·흡수·토템 피격 회생은 자원 모델에서 제외했다.','',
 '## 트리/장비 수치','','| 시나리오 | I/II 생명력 | I/II 초당 재생 | 함성 1회 기본 생명력/마나 비용 |','|---|---|---|---|']
for case in ['04_lv65_oldgear','05_lv54_proxy','05_lv65_proxy','05_lv65_defence80','06_lv65_proxy','07_lv74_source']:
    r=next(x for x in pob if x['case']==case);a,b=r['sets']['1'],r['sets']['2'];c=output(case,'Fortifying Cry')
    sim+=[f"| {case} | {a['Life']:.0f} / {b['Life']:.0f} | {a['LifeRegen']:.1f} / {b['LifeRegen']:.1f} | {c['LifeCost']:.0f} / {c['ManaCost']:.0f} |"]
sim+=['','05 대체 장비에서 토템 설치 1기 비용은 생명력 61, 버프 후 설치 전 정신력은 I 312 / II 324다. 4기 예약은 300씩 필요하다. 토템 내부 지면 분쇄의 매 공격 비용을 플레이어가 매번 낸다고 더하지 않았다. 69점 안의 계산 지속시간은 약 10초로, 제작자 54레벨 화면의 13초와 같지 않다. 트리/연결을 정확히 복제한 것이 아니므로 그 차이를 숨기지 않고 약 10초 재설치로 계산했다.','',
 '04의 타락한 피 1중첩 계산 DPS는 약 668, 05 대체 장비는 약 410이다. 기존 기본 12레벨 함성을 그대로 두면 약 351로 더 낮아졌다. **토템 전환이 함성 자체의 딜 상승이라는 뜻은 아니다.** 05는 전사 토템이 사용하는 지면 분쇄와 가시 폭발의 비중이 커진다. PoB의 지면 분쇄 기본 공격 DPS(이 예시 약 499/토템)를 가시 전체 DPS나 실전 총 DPS로 합산하지 않았다. 원거리 이동, 가시 생성과 폭발 시점, 실제 명중 수를 모두 재현하지 못한다.','',
 '## 자원 유지와 피격 여유','','| 조건 | 90초 결과 | 최소 생명력 |','|---|---|---|']
for c in resources['cases']:
    if c['case'] in ['05_lv65_proxy','05_lv65_defence80','05_lv65_mana'] and c['fort_interval']==1:
        label=c['case']+' / 피격 가정 '+str(c['incoming_after_mitigation'])+'/초';result='비용 지불 유지' if c['completed_90_seconds'] else str(c['failure']['time'])+'초에 '+c['failure']['reason']+' 부족'
        sim+=[f"| {label} | {result} | {c['minimum_life_percent']:.2f}% |"]
sim+=['','토템 4기를 유지하고 함성을 초당 1회 직접 사용한다. 69점 안은 적 피해 없이 90초 비용 지불을 유지했지만 초당 50의 경감 후 피해만 가정해도 생명력이 1.88%까지 내려갔다. 80점 회복·방어 확장에서는 같은 50/초 조건의 최저 생명력이 84.96%였다. 이런 결과 때문에 하코의 여유 점수를 방어 확장에 먼저 배정했다. 이 상수 피해는 실제 적의 타격 크기나 의식 몬스터를 재현하지 않는다.','',
 '혈마법 전 마나 시험은 플라스크 없이 약 11.62초에 마나가 부족했다. 마나 상태를 무한 유지 가능한 별도 사냥 단계로 만들지 않았다.','',
 '## 파콰테와 메아리','','두 함성을 함께 넣었다. 보강하는 함성 8초 간격, 그 사이 지진 함성 1초 간격, 토템 4기를 가정한 65레벨 예시는 반복의 추가 비용을 제외한 해석에서는 유지되지만 모든 반복에 최대 생명력/기본 비용을 부과한 스트레스 해석에서는 약 11~12초에 비용을 지불하지 못했다. 메아리 회복 2%를 포함해도 이 차이는 해소되지 않았다. 이 두 해석은 게임에서 확정한 규칙이나 엄밀한 상하한이 아니다.','',
 '방송 04:59:33의 메아리 회복 발언은 확인했지만 툴팁의 최근 사용 횟수, 반복 비용, 적 수, 처치 회복을 모두 분리한 실험은 없다. 따라서 **파콰테의 유지력 충분 판정은 보류**한다. 06은 실제 비용을 확인한 경우에 쓰는 조건부 참고 단계이며 05 연결로 되돌릴 수 있게 안내했다.','',
 '메아리에는 직접 사용 전 10미터 이동 조건이 있다. 모델은 그 거리를 충족했다고 가정하고, 각 반복이 대상에 닿았는지나 이동 중 받는 공격을 계산하지 않는다.','',
 '## 재현 자료','','`simulation/v3_inputs`에 10개 PoB 입력, `v3_pob_results.json`에 출력, `v3_resource_results.json`에 45개 사건 기록이 있다. `run_revision3.py`, `resources_revision3.py`로 재현한다. 두 개의 보조 스크립트는 이 검증을 위해 만든 도구이며 게임/프로젝트 코드를 바꾸지 않는다. 오프라인 그래프는 시뮬레이션그래프.html에서 조건을 바꿔 볼 수 있다.','']
(OUT/'시뮬레이션결과.md').write_text('\n'.join(sim),encoding='utf-8')

data=[]
for c in resources['cases']:
    data.append({k:v for k,v in c.items() if k not in ['trace']}|{'trace':[[e['t'],round(e['life']/c['life']*100,2)] for e in c['trace']]})
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>하코 자원 유지 계산 v3</title><style>body{font:17px/1.6 system-ui;margin:32px auto;max-width:1100px;padding:0 22px;color:#edf2f8;background:#101721}select{font:inherit;padding:8px;width:100%;background:#253447;color:white;border:1px solid #6b8298;border-radius:5px}svg{background:#192330;margin-top:20px;width:100%;height:auto}h1{font-size:26px}p{color:#c6d3df}.result{font-size:20px;color:#fff}a{color:#87c9ff}</style><h1>하코 자원 유지 계산 · v3</h1><p>트리·젬·장비를 정한 90초 비용 계산입니다. 몬스터 AI·기절·가시 전체 피해·한방 생존은 재현하지 않습니다. 파콰테의 두 비용 해석은 미확정 가정입니다.</p><label for="case">계산 조건</label><select id="case"></select><p id="summary" class="result"></p><svg id="chart" viewBox="0 0 1000 400" role="img" aria-label="시간에 따른 생명력 비율"></svg><p id="detail"></p><p><a href="시뮬레이션결과.md">입력과 계산 한계</a> · <a href="방송대조보고서.md">방송 근거</a></p><script>const data=DATA;const select=document.querySelector('#case');for(let i=0;i<data.length;i++){const c=data[i];const o=document.createElement('option');o.value=i;o.textContent=c.case+' | 함성 '+c.fort_interval+'초 | 피격 '+c.incoming_after_mitigation+'/초 | '+c.policy+(c.echo_heal?' | 반복 회복 포함':'');select.append(o)}function draw(){const c=data[+select.value];document.querySelector('#summary').textContent=(c.completed_90_seconds?'90초 동안 비용 지불 유지':'비용 지불 실패: '+c.failure.time+'초')+' · 최저 생명력 '+c.minimum_life_percent+'%';document.querySelector('#detail').textContent='최대 생명력 '+c.life+' / 낮은 세트 재생 '+c.regen_conservative+'/초 / 토템 설치 '+c.totem_cost_life+' / 함성 기본 생명력 비용 '+c.fort_base_life_cost+' — 마나 부족은 생명력이 남아 있어도 발생합니다.';const svg=document.querySelector('#chart');let content='';for(const y of [0,25,50,75,100]){const py=350-y*3;content+='<line x1="60" y1="'+py+'" x2="960" y2="'+py+'" stroke="#405269"/><text x="5" y="'+(py+5)+'" fill="#d5e0ed">'+y+'%</text>'}for(const t of [0,30,60,90])content+='<text x="'+(60+t*10)+'" y="383" fill="#d5e0ed">'+t+'초</text>';let points='60,50 '+c.trace.map(p=>(60+p[0]*10)+','+(350-p[1]*3)).join(' ');content+='<polyline points="'+points+'" fill="none" stroke="#78d9cf" stroke-width="2.5"/>';svg.innerHTML=content}select.value=data.findIndex(c=>c.case==='05_lv65_defence80'&&c.fort_interval===1&&c.incoming_after_mitigation===50);select.onchange=draw;draw();</script></html>'''
labels={'05_lv54_proxy':'05 전사 토템 · 54레벨 예시','05_lv65_proxy':'05 전사 토템 · 65레벨 · 69점','05_lv65_defence80':'05 회복·방어 확장 · 65레벨 · 80점','05_lv65_old_fort':'05 기존 함성 젬 유지 · 65레벨','05_lv65_mana':'05 혈마법 전 마나 시험','06_lv65_proxy':'06 파콰테 · 65레벨 예시','07_lv74_source':'07 제작자 후기 장비 · 74레벨'}
page=page.replace('const data=DATA;','const labels='+json.dumps(labels,ensure_ascii=False)+';const data=DATA;')
page=page.replace("o.textContent=c.case+", "o.textContent=(labels[c.case]||c.case)+")
page=page.replace("+c.policy+(c.echo_heal", "+({normal:'일반 비용',manual_only:'반복 추가 비용 없음 가정',echo_cost_stress:'반복마다 비용 부과 가정'}[c.policy])+(c.echo_heal")
(OUT/'시뮬레이션그래프.html').write_text(page.replace('DATA',json.dumps(data,ensure_ascii=False)),encoding='utf-8')
print('Wrote start guide, updated simulation report and offline interactive chart.')
