'use strict';
// Taengjung route view (9/20 live): 00~02 별이슬 act trees, map-entry switch, 03~07 Taengjung. Data from planner_contract.json via adapt_data.py.
window.transitionBudget=function(s){
 const b=s.budgets||s.authored_checkpoint?.budgets;
 if(b&&['ordinary_common','weapon_set_1','weapon_set_2','ordinary_points_required','ascendancy_points_required'].every(k=>Number.isFinite(b[k])))return {ordinary:b.ordinary_points_required,ordinaryCommon:b.ordinary_common,weapon1:b.weapon_set_1,weapon2:b.weapon_set_2,ascendancy:b.ascendancy_points_required,free:(b.free_ascendancy_nodes||0)+(b.free_class_start||0)};
 const ids=[...new Set((s.passives||[]).map(n=>String(n.id)))],one=(s.weapon_set_nodes?.['1']||[]).map(String).filter(id=>ids.includes(id)),two=(s.weapon_set_nodes?.['2']||[]).map(String).filter(id=>ids.includes(id));
 const freeIds=[...new Set(['47175','5852','9988',...(s.passives||[]).filter(n=>n.isFreeAllocate===true).map(n=>String(n.id))])],free=ids.filter(id=>freeIds.includes(id));
 const paid=(s.passives||[]).filter(n=>!freeIds.includes(String(n.id))),asc=paid.filter(n=>n.ascendancyName),common=paid.filter(n=>!n.ascendancyName&&!one.includes(String(n.id))&&!two.includes(String(n.id)));
 return {ordinary:common.length+Math.max(one.length,two.length),ordinaryCommon:common.length,weapon1:one.length,weapon2:two.length,ascendancy:asc.length,free:free.length};
};

// Korean node names = poe2db.tw/kr (the repo translation file has 탄탈륨/내열성/키바). 60913 and 16276 are both "키타바의 각인" in Korean.
const ASC_KO={'14960':'화염 저항','57959':'석탄 때기','9988':'대장장이의 걸작(무료)','61039':'탄탈룸 합금','9997':'녹아내린 상징','64962':'키타바에 대한 헌신','25438':'내열 처리','110':'내부 층','60913':'키타바의 각인(생명력 15%)'};

// Short next actions per contract phase (index 1..6); phase 1 is the uninstalled 40-level alternative.
const TAENGJUNG_ACTIONS={
 1:['대안(설치 안 함): 40레벨에서 바로 탱정 트리로 가는 Pathcraft 구성. 탱정 본인 순서는 액트 뒤 전환(03)입니다.'],
 2:['액트가 끝나 맵에 들어갈 때 마을에서 한 번에: 별이슬 막간 트리 → 이 트리 (번호 순서는 02 카드)',
  '흰색(일반) 갑옷(예: 전쟁군주 흉갑). 전직은 액트에 이어 키타바에 대한 헌신 → 내열 처리(전직 포인트 8이면 내부 층 → 키타바의 각인·생명력 15%)',
  '방패 방어도 1000이면 T15까지 충분, 사지 말고 제작 · 액트 보상 루비 반지(화염 품질 10+) 2개',
  '저항 75%+ · 카오스 60%(1일차는 40%도 괜찮음). 1일차는 흰템으로 끝냄(2일차에 싼 게 많다 · 첫날도 생각보다 싸다는 말도 함)',
  '방패의 벽은 세트 1, 함성은 전부 세트 2(방송). 벽이 안 터지면 지옥불 함성, 대기 중이면 보강하는 함성으로 터뜨림',
  '포인트가 61보다 많으면 07 트리의 세트 1 공격 속도 · 세트 2 함성 노드부터(무기 세트 노드도 일반 포인트를 씀)',
  '다음: 무자본이면 03+(구매 없이 성장), 자본이 있으면 04. 안의 성채는 비싸서(HC 약 3 Divine) 살 수 있을 때만'],
 3:['2일차: 운명의 저항 목걸이만 먼저(하나씩)',
  '장비만으로 화염 저항 75% 이상 — 탱정 목표는 화염 저항 합계 250~260%',
  '황동 철갑은 한꺼번에(마을): Masterwork 분기 + Masterwork 환불 → 황동 철갑 → Forged in Flame · Heat of the Forge',
  '바로 다음: 올로스의 결의(필수 생존 플라스크)',
  '3일차에 돈이 조금 모이면 셉터(최신 저장본: 신성한 불꽃). 셉터로 바꾸면 충격파 토템은 못 씀 → 두 함성으로 벽 파괴'],
 4:['아홉꼬리 묶음은 한꺼번에(미리 사 두기): 허리띠 + 저항용 Desert Rune + 트리 재조정(지능 요구치 확인). 생명력 플라스크는 빼도 되고 안 빼도 됨',
  '젬: 영원한 격노 켜기(캐릭터 59) · Elemental Weakness + Lifetap(체크포인트에서 세네 번 걸어 생명력을 깎음) · 동결의 징표 · 방패의 벽 Execute III · Clash · Rapid Attacks II + Armour Break III(늑대 호신부 뒤엔 Concentrated Area)',
  'Execute III · Enraged Warcry II는 레벨 5 미가공 보조 젬(드롭 레벨 55)',
  '"저자본의 모토는 편의성을 버린다" — 탱정 발언: 교체 1 Divine 미만, 전체 10~15 Divine(9/20 시세)'],
 5:['목 죄이는 명령(2소켓 고유 Viper Cap, 탱정 발언 9~11 Divine)을 착용한 뒤 원형(포위) 노드 — Paranoia · Thrill of Battle · Frantic Fighter',
  'Frantic Fighter는 포위 시 명중 30% 감소 — 실제 명중 확인 후 찍기',
  '혈통 젬은 살 수 있을 때: 안의 성채(Armour Break III 자리) · 카옴의 광기(5칸째) · 우트레드의 의례. 다레소의 열정만 싸서 젬 칸에. 남는 포인트는 07 저자본 완성 트리로'],
 7:['무자본(리그 스타터 · zero2hero): 03 구성 그대로, 사는 것 없이 성장',
  '포인트: 무기 세트 노드(세트 1 공격 속도 · 세트 2 함성)부터 — 29d39에서 포위·저생명력 노드를 뺀 트리(Pathcraft 구성)',
  '전직 8: 03의 6 + 내부 층 → 키타바의 각인(생명력 15%)',
  '스킬: 미가공 보조만(혈통 젬 없음). 4칸은 방패의 벽',
  '돈이 모이면 04(운명의 저항)로 — 더 찍은 일반·무기 세트 노드는 07 트리에 있어 환불 불필요, 전직은 04에서 걸작 분기 전체(내부 층 · 키타바의 각인 포함) 환불'],
 6:['탱정 최신 저자본(29d39) 트리 그대로: 일반 118 · 무기 특화 24 · 유료 전직 8 (저장 캐릭터 97레벨, 최소치 아님)',
  '06에서 환불 없이 더하기만: 일반 +48 · 무기 특화 한도 4 → 24(세트 1 노드 24 · 세트 2 노드 23) · 전직 +2. 포인트 생기는 대로',
  '자본 여유가 있으면 우물 심장 주얼(싸다고 함). 신성모독(Blasphemy)은 저자본엔 없어도 되고 후반에']};

window.renderTransition=function(ctx){
const {D,state,template,clone,save,render,diffHTML,displayName,legacyNotice,bindLegacy}=ctx;
const openDetails=[...document.querySelectorAll('#workbench details')].map(e=>e.open);
const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const ko=n=>displayName?displayName(n):n;
const prefs=state.transitionPlanning||{},checks=state.checks,level=prefs.level??state.profile.level;
// Two versions share 00~03: 무자본(zero2hero) continues to 03+, 약간의 자본 to 04~07. `now` is a 0-based position in the chosen track.
const track=prefs.track==='zero'?'zero':'capital';
const route=((D.tracks||{})[track]||D.activeStageIds||[]).map(id=>D.stages.find(s=>s.id===id)).filter(Boolean);
const now=Math.min(Math.max(0,prefs.route??0),Math.max(0,route.length-1));
const fileOf=id=>D.nativeFiles?.[id]||D.referenceFiles?.[id];
const pad=i=>String(i).padStart(2,'0');
const numOf=s=>s.display_label??s.display_number??0;
const displayOfPhase=ph=>(D.taengjung?.stages||[]).find(s=>s.index===ph)?.display_number;
function download(id){const f=fileOf(id);if(!f)return;const bytes=Uint8Array.from(atob(f.base64),c=>c.charCodeAt(0)),url=URL.createObjectURL(new Blob([bytes],{type:'application/octet-stream'}));const a=document.createElement('a');a.href=url;a.download=f.downloadFilename||f.filename;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}
// Displayed budgets are targets. Entry minimums follow the contract: growth stages enter from the connected
// 48-point core (+ this stage's own extension), phase 1 works with 2 paid ascendancy points (Coal Stoker only),
// and stages with ascendancy_alternative may defer the Heat of the Forge pair.
function minimums(s,b){
 if(s.entry_minimum)return s.entry_minimum;
 const sub=s.growth_subtargets||[];
 return {ordinary:sub.length?sub[0].ordinary+(b.ordinary-sub[sub.length-1].ordinary):b.ordinary,weapon:Math.max(b.weapon1,b.weapon2),ascendancy:s.index===1?2:(s.ascendancy_alternative?.paid_points??b.ascendancy)};
}
// Level-derived points are a guaranteed floor; unknown quest rewards are never added.
function shortages(s,b){
 const floor=Math.max(0,level-1),min=minimums(s,b),weaponNeed=Math.max(b.weapon1,b.weapon2);
 const rows=[['일반',floor+(prefs.quest??0),min.ordinary,b.ordinary,prefs.quest===undefined?'레벨 유래 '+floor+' · 보상 미입력':null],['무기 특화 · 세트당',prefs.weapon??(weaponNeed===0?0:null),min.weapon,weaponNeed,null],['유료 전직',prefs.ascendancy??null,min.ascendancy,b.ascendancy,null]];
 return rows.map(([name,have,low,goal,note])=>({name,ready:have!==null&&have>=low,text:name+': '+(have===null?'확보량 미입력 · 목표 '+goal+(low<goal?' (최소 '+low+')':''):have>=goal?'확보 '+have+' / 목표 '+goal+' 충족':have>=low?'확보 '+have+' · 최소 '+low+' 충족, 목표 '+goal+'까지 '+(goal-have):'확보 '+have+' / 최소 '+low+' · '+(low-have)+' 부족'+(note?' ('+note+')':''))}));
}
const bullets=a=>'<ul>'+(a||[]).map(x=>'<li>'+esc(x)+'</li>').join('')+'</ul>';
const setLabel=w=>String(w)==='1'?'무기 세트 1':String(w)==='2'?'무기 세트 2':'공통';

function skillsHTML(s){return (s.skills||[]).map(k=>{const active=k.gems?.[0],gated=(k.gems||[]).slice(1).filter(g=>g.crafting_level>1);return '<p><strong>'+esc(ko(k.active))+'</strong> · '+esc(setLabel(k.weapon_set))+'<br>'+esc(k.supports.map(ko).join(' + ')||'보조 없음')+'<br><span class="mini">보조 소켓 '+k.supports.length+' · 기본 젬 최소 캐릭터 '+esc(active?.min_character_level??'확인 필요')+' · '+esc(k.condition||'')+(gated.length?'<br>미가공 보조 젬 레벨: '+esc(gated.map(g=>g.name+' '+g.crafting_level+'(드롭 '+g.uncut_support_drop_level+')').join(' · ')):'')+'</span>'+lineageHTML(k)+'</p>'}).join('')+(s.lineage_note?'<p class="mini">'+esc(s.lineage_note)+'</p>':'')}
// Lineage supports: capital files put them in the gem slots within 4 sockets; the rest (Kaom, 03's Ahn's) are text only.
function lineageHTML(k){return (k.lineage||[]).length?'<br><strong>혈통 젬</strong>: '+k.lineage.map(l=>esc(l.ko+' ('+l.name+', 캐릭터 '+l.min_character_level+'부터) · '+(l.in_slots?'젬 칸에 넣음':'선택 · 젬 칸엔 없음'))+'<br><span class="mini">'+esc(l.note)+'</span>').join('<br>'):''}
function skillChanges(prev,s){
 if(!prev)return [];
 const before=prev.skills||[],after=s.skills||[],out=[];
 for(const k of after){const p=before.find(x=>x.active===k.active);if(!p){out.push('＋ '+ko(k.active)+(k.supports.length?' ('+k.supports.join(' · ')+')':''));continue}for(const x of k.supports.filter(x=>!p.supports.includes(x)))out.push('＋ '+ko(k.active)+' 보조 '+x);for(const x of p.supports.filter(x=>!k.supports.includes(x)))out.push('− '+ko(k.active)+' 보조 '+x)}
 for(const p of before.filter(x=>!after.some(k=>k.active===x.active)))out.push('− '+ko(p.active));
 return out;
}
const KO_SKILL={'Shield Wall':'방패의 벽','Infernal Cry':'지옥불 함성','Fortifying Cry':'보강하는 함성','Shockwave Totem':'충격파 토템','Eternal Rage':'영원한 격노'};
function weaponSetHTML(s){const r=s.weapon_set_roles;if(!r)return '';const k=a=>(a||[]).map(x=>KO_SKILL[x]||x).join(' · ')||'없음';const one=(w,what)=>'<li><strong>세트 '+w+' · '+what+'</strong>: '+esc(k(r[w].skills))+' · 세트 전용 패시브 '+r[w].passive_count+'개'+(r[w].notables.length?' ('+esc(r[w].notables.join(' · '))+')':'')+'</li>';return '<ul>'+one('1','방패로 벽 세우기')+one('2','함성으로 벽 터뜨리기')+'<li>양쪽 공통: '+esc(k(r['0'].skills))+'</li><li class="mini">스킬을 세트에 배정하면 쓸 때 그 세트로 바뀝니다. 저장본에는 세트 2 무기 칸이 비어 있어 세트 2에 무엇을 드는지는 확인 안 됨.</li></ul>'}
function equipmentHTML(s){return '<ul>'+(s.equipment||[]).map(e=>'<li><strong>'+esc(e.slot)+'</strong> · '+esc(ko(e.name))+(e.status==='prepare_not_equip'?' · 준비만, 아직 착용 안 함':'')+'<br><span class="mini">'+esc(e.condition||'')+'</span></li>').join('')+'</ul>'}
function bandOf(s){const bands={};for(const t of s.growth_subtargets||[]){for(const p of t.passives||[])bands[p.numeric_id]=bands[p.numeric_id]||t.ordinary;for(const o of t.added_operations||[])bands[o.numeric_id]=t.ordinary}return bands}
function opsList(ops){return '<ol class="operation-list">'+ops.map(o=>'<li class="'+(o.action==='refund'?'refund-operation':'add-operation')+'">'+(o.action==='refund'?'− 환불 ':'＋ 추가 ')+esc(o.name)+' ['+esc(o.numeric_id)+'] · '+esc(setLabel(o.weapon_set))+'</li>').join('')+'</ol>'}
function changesHTML(s,prev){
 const d=s.diff_from_previous||{},ops=d.operations||[],asc=d.ascendancy_operations||[],bands=bandOf(s),skills=skillChanges(prev,s);
 const skillPart=skills.length?'<h3>스킬 · 보조</h3>'+bullets(skills):'';
 // Phase 2 is entered from the 별이슬 interlude tree, not from the 40-level alternative: its tree order is on the 02 card.
 if(s.index===2)return skillPart+'<p>일반 트리는 02 카드의 "02 → 03 번호 순서"대로 바꿉니다.</p><h3>전직 (이 단계 전체)</h3>'+bullets((s.ascendancy_nodes||[]).filter(n=>n.id!=='5852').map(n=>(ASC_KO[n.id]||n.name)+' ['+n.id+']'))+'<p class="mini">액트 때 찍은 화염 저항 → 석탄 때기 → 대장장이의 걸작 → 탄탈룸 합금 → 녹아내린 상징에 이어 키타바에 대한 헌신 → 내열 처리. 흰색 갑옷을 입은 상태여야 합니다. 전직 포인트 8이면 내부 층 → 키타바의 각인(생명력 15%).</p>';
 if(!ops.length&&!asc.length)return '<p>패시브 트리·전직은 앞 단계와 같습니다.</p>'+skillPart;
 return skillPart+'<p>일반 추가 '+ops.length+' · 일반 환불 '+(d.ordinary_refunds||0)+' · 전직 환불 '+(d.ascendancy_paid_refunds||0)+' / 추가 '+(d.ascendancy_paid_additions||0)+'</p>'+(ops.length?'<ol class="operation-list">'+ops.map(o=>'<li class="add-operation">＋ '+esc(o.name)+' ['+esc(o.numeric_id)+'] · '+esc(setLabel(o.weapon_set))+(bands[o.numeric_id]?' · '+bands[o.numeric_id]+' 구간':'')+'</li>').join('')+'</ol><p class="mini">연결을 유지하는 순서 예시입니다(저자 클릭 순서 아님). 실제로 얻은 포인트만큼만 진행하세요.</p>':'')+(asc.length?'<h3>전직 (마을에서 따로)</h3><ol>'+asc.map(o=>'<li class="'+(o.action==='refund'?'refund-operation':'add-operation')+'">'+(o.action==='refund'?'− 환불 ':'＋ 추가 ')+esc(o.name)+' ['+esc(o.numeric_id)+'] · '+(o.paid?'유료':'무료')+'</li>').join('')+'</ol>':'')+(s.ascendancy_alternative?'<p class="mini">'+esc(s.ascendancy_alternative.reason)+'</p>':'');
}
function stepButton(pos){return pos!==now?'<button data-transition-step="'+pos+'">지금 단계로 표시</button>':''}
function stageCard(s,pos){
 const id=s.id,num=numOf(s),b=window.transitionBudget(s),min=minimums(s,b),short=shortages(s,b),f=fileOf(id),conds=s.conditions||[];
 const done=conds.every((g,j)=>checks['transition:'+id+':'+j]),ready=short.every(x=>x.ready);
 return '<section class="transition-stage'+(pos===now?' current-step':'')+'" id="transition-'+esc(id)+'"><p class="eyebrow">단계 '+pad(num)+(s.track==='zero'?' · 무자본':s.index>=3?' · 자본':s.index===2?' · 공통':'')+(pos===now?' · 지금 단계':pos<now?' · 지난 단계':'')+'</p><h2>'+esc(pad(num)+' '+s.label)+'</h2>'+bullets(TAENGJUNG_ACTIONS[s.index])
  +'<div class="transition-budget"><p><strong>'+b.ordinary+'</strong> 일반 포인트 목표'+(min.ordinary<b.ordinary?' · 최소 '+min.ordinary:'')+'</p><p><strong>'+Math.max(b.weapon1,b.weapon2)+'</strong> 무기 특화 · 세트당</p><p><strong>'+b.ascendancy+'</strong> 유료 전직 목표'+(min.ascendancy<b.ascendancy?' · 최소 '+min.ascendancy:'')+'</p></div>'
  +'<ul class="budget-checks">'+short.map(x=>'<li class="'+(x.ready?'status-ready':'status-missing')+'">'+esc(x.text)+'</li>').join('')+'</ul>'
  +'<div class="toolbar">'+(f?'<button data-transition-download="'+esc(id)+'">'+esc(f.downloadFilename)+' ↓</button>':'')+'<button data-transition-load="'+esc(id)+'">목표로 불러오기</button>'+stepButton(pos)+'</div>'
  +'<details><summary>조건 확인 '+conds.filter((g,j)=>checks['transition:'+id+':'+j]).length+' / '+conds.length+'</summary>'+conds.map((g,j)=>'<label class="manual-confirm"><input type="checkbox" data-transition-check="'+esc(id)+':'+j+'" '+(checks['transition:'+id+':'+j]?'checked':'')+'>'+esc(g)+'</label>').join('')+'<p class="transition-status">'+(done&&ready?'✓ 입력한 조건·최소 포인트 확인 · 게임에서 대조 후 진행, 남는 포인트는 목표까지':'○ 조건이 남았거나 최소 포인트 미달이면 앞 단계를 유지')+'</p></details>'
  +'<details><summary>스킬 · 보조 · 무기 세트</summary>'+skillsHTML(s)+'</details>'
  +'<details><summary>무기 세트 · 저항 맞추기</summary>'+weaponSetHTML(s)+bullets(s.resistance_plan||[])+'</details>'
  +'<details><summary>장비 · 부위별 추천 옵션</summary>'+(s.gear_note?'<p><strong>'+esc(s.gear_note)+'</strong></p>':'')+equipmentHTML(s)+'</details>'
  +'<details><summary>앞 단계에서 바뀌는 것</summary>'+changesHTML(s,route[pos-1])+'</details></section>';
}
// 00~02: 별이슬 act trees (Taengjung: acts follow 별이슬, 9/20 live). 02 carries the verified town respec into 03.
function refCard(r,pos){
 const c=r.counts,f=fileOf(r.id),ops=r.transition_to_03||[],num=numOf(r);
 const lines=['탱정 9/20 방송: 액트는 별이슬골짜기 방패벽 액트 가이드로(1부 0:07:12 · 2부 1:06:44). 이 트리 "'+r.spec_title+'": 일반 '+c.ordinary_common+' · 무기 세트 '+c.weapon_set_1+' / '+c.weapon_set_2,
  '전직: 별이슬 원본은 워브링어, 탱정 보정은 키타바. 워브링어를 골랐다면 03~07 전직이 맞지 않으니 먼저 확인',
  '이 파일에 넣은 전직: '+(r.ascendancy_nodes||[]).filter(n=>n.id!=='5852').map(n=>ASC_KO[n.id]||n.name).join(' → '),
  '액트 전직 순서(탱정 8/17 영상 4:32~7:15): 1차 2포인트 = 화염 저항 → 석탄 때기. 2차부터 대장장이의 걸작(무료, 흰색 갑옷만) 아래로 탄탈룸 합금 → 녹아내린 상징 → 키타바에 대한 헌신 → 내열 처리 → 내부 층 → 키타바의 각인(최대 생명력 15%, Kitavan Engraving). 한국어로 "키타바의 각인"이 두 개라 영광 생성 60% 쪽(Kitavan Imprint)은 아님. 순서는 취향대로 바꿔도 된다고 함(5:11~5:19)'];
 if(r.spec_title==='3')lines.splice(1,0,'게임 화면의 무기 세트 포인트 10/10과 같아 지금 트리로 추정(확인 안 됨)');
 if(ops.length)lines.push('액트가 끝나 맵에 들어갈 때 마을에서 03(탱정 1일차)으로: 환불 '+c.refunds+' → 추가 '+c.allocations+', 겹치는 노드 '+c.kept+'개 — 사실상 재분배. 환불 골드는 게임에서 확인');
 else lines.push('별이슬 가이드 순서대로 진행. 탱정 세팅은 액트가 끝난 뒤(03)입니다');
 return '<section class="transition-stage'+(pos===now?' current-step':'')+'" id="transition-'+esc(r.id)+'"><p class="eyebrow">단계 '+pad(num)+' · 별이슬 액트 트리'+(pos===now?' · 지금 단계':pos<now?' · 지난 단계':'')+'</p><h2>'+esc(r.label)+'</h2>'+bullets(lines)
  +'<div class="toolbar">'+(f?'<button data-transition-download="'+esc(r.id)+'">'+esc(f.downloadFilename)+' ↓</button>':'')+stepButton(pos)+'</div>'
  +'<details><summary>장비 · 액트 부위별 안내</summary>'+(r.gear_note?'<p><strong>'+esc(r.gear_note)+'</strong></p>':'')+equipmentHTML(r)+'</details>'
  +'<details><summary>스킬(별이슬 구성)</summary>'+skillsHTML(r)+'</details>'
  +(ops.length?'<details><summary>02 → 03 번호 순서 ('+ops.length+'개 · 환불 위주, 연결이 끊기지 않게 추가를 사이에 섞음)</summary>'+opsList(ops)+'<p class="mini">매 단계 두 무기 세트 트리가 연결되도록 검증한 순서입니다(저자 클릭 순서 아님). 일반·무기 세트 노드만이며 전직은 03 카드대로. 실제 트리가 다르면 게임 플래너에서 03을 골라 대조하세요.</p></details>':'')+'</section>';
}
function card(s,pos){return s.isRef?refCard(s,pos):stageCard(s,pos)}
function actionsOf(s){return s.isRef?['탱정 9/20 방송: 액트는 별이슬 방패벽 액트 가이드로. 이 단계는 별이슬 트리 "'+s.spec_title+'"','액트가 끝나 맵에 들어갈 때 02 → 03 전환(마을 재분배)']:TAENGJUNG_ACTIONS[s.index]}
const rewardData=window.TRANSITION_REWARDS||{},rewards=rewardData.rewards||[],claimed=rewards.reduce((sum,r,i)=>sum+(checks['transition:reward:'+i]?r.points:0),0);
const rewardHTML='<details class="reward-checklist"><summary>받은 퀘스트 보상 체크 · '+claimed+' / '+(rewardData.maximum_total||24)+'</summary>'+rewards.map((r,i)=>'<label class="manual-confirm"><input type="checkbox" data-transition-check="reward:'+i+'" '+(checks['transition:reward:'+i]?'checked':'')+'>'+esc(r.stage+' · '+r.objective+' ('+r.area+') +'+r.points)+'</label>').join('')+'<button id="apply-reward-budget">체크한 '+claimed+'점을 일반 포인트에 적용</button><p class="mini">출처: <a href="'+esc(rewardData.source||'')+'" target="_blank" rel="noreferrer">'+esc(rewardData.author||'')+' 0.5 캠페인 체크리스트</a> · 받지 않은 보상은 체크하지 마세요.</p></details>';
const budgetHTML='<details class="advanced-budget"><summary>내 포인트 입력 · 레벨 '+esc(level)+' · 보상 '+(prefs.quest??'미입력')+' · 전직 '+(prefs.ascendancy??'미입력')+'</summary><p>일반 포인트 = 레벨 − 1 + 실제로 받은 퀘스트 보상. 모르는 보상은 더하지 않습니다.</p><div class="fields"><label>현재 레벨 (1–100)<input data-transition-level type="number" min="1" max="100" value="'+esc(level)+'"></label><label>받은 일반 퀘스트 포인트<input data-transition-budget="quest" type="number" min="0" max="24" value="'+esc(prefs.quest??'')+'" placeholder="게임에서 확인"></label><label>무기 특화 포인트 · 세트당<input data-transition-budget="weapon" type="number" min="0" max="24" value="'+esc(prefs.weapon??'')+'" placeholder="게임에서 확인"></label><label>유료 전직 포인트<input data-transition-budget="ascendancy" type="number" min="0" max="8" value="'+esc(prefs.ascendancy??'')+'" placeholder="게임에서 확인"></label></div>'+rewardHTML+'</details>';
const gear=prefs.gear||{},fields=[['currentArmour','현재 방패 방어도'],['currentBlock','현재 방패 막기 %'],['candidateArmour','후보 방패 방어도'],['candidateBlock','후보 방패 막기 %'],['requiredLevel','후보 요구 레벨'],['strength','현재 힘'],['requiredStrength','후보 요구 힘']];
const requirement=(name,have,need)=>need===undefined?name+' 요구 미입력':have===undefined?name+' 현재값 미입력':have>=need?name+' 충족':name+' '+(need-have)+' 부족';
const compare=(label,k)=>gear['current'+k]===undefined||gear['candidate'+k]===undefined?label+' 비교 미입력':label+' '+gear['current'+k]+' → '+gear['candidate'+k]+' ('+(gear['candidate'+k]-gear['current'+k]>=0?'+':'')+(gear['candidate'+k]-gear['current'+k])+')';
const gearHTML='<details class="shield-candidate"><summary>후보 방패 수치 비교</summary><p>아이템 툴팁 값을 입력하세요. 빈 값은 0으로 치지 않습니다.</p><div class="fields">'+fields.map(([k,label])=>'<label>'+label+'<input data-shield-candidate="'+k+'" type="number" min="0" value="'+esc(gear[k]??'')+'"></label>').join('')+'</div><ul class="shield-comparison"><li>'+compare('방어도','Armour')+'</li><li>'+compare('막기','Block')+'</li><li>'+requirement('레벨',level,gear.requiredLevel)+'</li><li>'+requirement('힘',gear.strength,gear.requiredStrength)+'</li></ul></details>';
const buying='<section class="level40-purchases"><h2>살 것 · 순서</h2><p>보유: 5 Divine · 17 Chaos · 61 Exalted / 상급 세공사의 오브 3 · 하급 29. 화폐를 서로 환산하지 않고 시세는 추정하지 않습니다. 거래는 직접 하세요. 탱정 9/20: 액트 4 전에는 거래 없이, 1일차는 흰템으로 끝냄.</p><ol><li><strong>액트(00~02):</strong> 별이슬 가이드 장비. 방패는 방어도 위주.</li><li><strong>맵 진입(03):</strong> 흰색 방어도 갑옷 → 방패 방어도(1000이면 T15까지, 제작 권장) → 액트 루비 반지 2개 → 부족한 저항·생명력</li><li><strong>저자본 순서:</strong> 운명의 저항(04, 하나씩) → 화염 저항 장비 → 황동 철갑(04, 전직과 한꺼번에) → 올로스의 결의(바로 다음) → 3일차 셉터 → 아홉꼬리 묶음(05, 한꺼번에) → 목 죄이는 명령(06). 미리 사 둬도 되지만 그 단계 조건 전에는 착용하지 않습니다.</li><li><strong>보조 젬:</strong> Rapid Attacks II · Armour Break III · Enraged Warcry I은 레벨 4 미가공 보조 젬(드롭 레벨 45), 05의 Execute III · Enraged Warcry II는 레벨 5(드롭 레벨 55)에서 만듭니다.</li><li><strong>장비 옵션:</strong> 방패의 벽 피해는 방패 방어도에서 나옵니다(방패 방어도 15당 물리 피해 추가). 방패 방어도 → 장갑 · 철퇴의 +근접 스킬 레벨 → 저항 → 생명력 순. 함성 옵션은 한손 철퇴 Desecrated 접미사(함성 재사용 대기 회복) · 장갑 룬 Boar Idol 정도라 함성은 주로 트리 · 보조 젬으로. 부위별 순서는 각 단계의 "장비 · 부위별 추천 옵션"에.</li><li><strong>저항:</strong> 탱정 목표는 원소 저항 75%+ · 카오스 60% · 화염 저항 합계 250~260%. Coal Stoker 때문에 장비의 화염 저항이 냉기·번개도 절반씩 채웁니다. 04 황동 철갑 전에는 장비만으로 화염 75% 이상(일반 갑옷 분기의 +75%가 빠짐).</li><li><strong>세공사의 오브:</strong> 상급 3개 = 4칸 스킬 최대 3개, 완벽 0개 = 5칸 없음. 00~03·03+는 방패의 벽 4칸(상급 1), 자본 05~07도 방패의 벽 4칸(Armour Break III). 혈통 젬은 종류별 1개만(0.5 PoB), 일반 보조는 여러 스킬에 겹쳐 써도 됩니다.</li><li><strong>무자본(03+):</strong> 사는 것 없이 흰색 갑옷 · 희귀 장비 · 미가공 보조로 성장. 돈이 모이면 04부터 자본 버전.</li></ol>'+gearHTML+'</section>';
const swaps=D.taengjung?.lowbudget_swaps||[];
const swapHTML=swaps.length?'<section class="lowbudget-swaps"><h2>저자본 사는 순서 · 하나씩 / 한꺼번에</h2><p>탱정 9/20 방송 순서입니다. "한꺼번에"는 마을에서 한 번에 바꾸는 묶음이고, "하나씩"은 그 칸만 바꿔도 됩니다. 금액은 탱정이 그날 말한 값이며 시세는 바뀝니다.</p><ol>'+swaps.map(x=>'<li><strong>'+esc(x.item)+'</strong> · '+esc(x.slot)+' · 단계 '+pad(displayOfPhase(x.stage)??0)+' · <span class="'+(x.swap==='한꺼번에'?'status-missing':'status-ready')+'">'+esc(x.swap)+'</span><br>'+esc(x.how)+'<br><span class="mini">근거: '+esc(x.source)+'</span></li>').join('')+'</ol></section>':'';
const hcGates=['현재 클래스·전직이 전사 / Smith of Kitava인지 확인했다','장착할 방패·갑옷·저항·능력치와 젬 요구조건을 확인했다','방패의 벽 세트 1 · 함성 세트 2와 자원·회복을 게임에서 확인했다','장비 교체·환불 뒤 생존 조건을 확인하기 전에는 위험 콘텐츠에 들어가지 않는다'];
const hcHTML='<details><summary>하드코어 전환 전 직접 확인</summary>'+hcGates.map((g,i)=>'<label class="manual-confirm"><input type="checkbox" data-transition-check="hc:'+i+'" '+(checks['transition:hc:'+i]?'checked':'')+'>'+esc(g)+'</label>').join('')+'<p class="mini">체크는 사용자의 확인 기록이며 실게임 안전을 보증하지 않습니다.</p></details>';
const refIds=Object.keys(D.referenceFiles||{});
const referenceHTML='<details class="earlier-campaign"><summary>참고 자료 · 기본 경로 아님</summary><p>탱정 저장본 원본과 40레벨 조기 전환 대안은 선택 참고용입니다. 최신 29d39 전체 트리(일반 118 · 저장 레벨 97)는 진입 최소치가 아닙니다. 게임 폴더에는 설치하지 않았습니다.</p><div class="toolbar">'+refIds.map(id=>'<button data-transition-download="'+esc(id)+'">'+esc(D.referenceFiles[id].downloadFilename)+' ↓</button>').join('')+'</div><p class="mini">이전 룬드 경로와 이전 번호 파일은 삭제하지 않고 게임 BuildPlanner 폴더 밖의 백업 폴더에 보관했습니다.</p></details>';
const toc='<nav class="transition-toc" aria-label="탱정 경로">'+route.map((s,pos)=>'<a href="#transition-'+esc(s.id)+'"'+(pos===now?' aria-current="step"':'')+'>'+esc(s.isRef?s.label:pad(numOf(s))+' '+s.label)+(pos===now?' · 지금':'')+'</a>').join('')+'</nav>';
const cur=route[now];
const host=document.getElementById('workbench');
const trackHTML='<div class="toolbar track-switch" role="group" aria-label="버전"><button data-track="zero" aria-pressed="'+(track==='zero')+'">무자본 · 리그 스타터(zero2hero)</button><button data-track="capital" aria-pressed="'+(track==='capital')+'">약간의 자본 · 저자본(탱정 9/20)</button></div><p class="mini">'+(track==='zero'?'지금 보는 버전: 무자본. 00~03 뒤 03+ — 고유 장비·혈통 젬 없이 흰색 갑옷으로 성장. 돈이 모이면 04부터 자본 버전으로.':'지금 보는 버전: 약간의 자본. 00~03 뒤 04~07 — 운명의 저항 → 황동 철갑 → 아홉꼬리 → 목 죄이는 명령. 혈통 젬은 다레소의 열정만 젬 칸에, 나머지는 비싸서 살 수 있을 때(방패 칸 목록).')+'</p>';
host.innerHTML=(legacyNotice?legacyNotice():'')+'<section class="now-configuration">'+trackHTML+'<p class="eyebrow">지금 단계 · '+pad(cur?numOf(cur):0)+'</p><h2>'+esc(cur?(cur.isRef?cur.label:pad(numOf(cur))+' '+cur.label):'단계 자료 없음')+'</h2>'+bullets(cur?actionsOf(cur):[])+'<div class="toolbar">'+(cur&&fileOf(cur.id)?'<button data-transition-download="'+esc(cur.id)+'">'+esc(fileOf(cur.id).downloadFilename)+' ↓</button>':'')+(now<route.length-1?'<button data-transition-step="'+(now+1)+'">다음 단계('+pad(numOf(route[now+1]))+')로 넘어감</button>':'')+'</div><p class="mini">게임 BuildPlanner에서 '+(track==='zero'?'00 → 01 → 02 → 03 → 03+ [무자본]':'00 → … → 07 ([자본] 04~07)')+' 순서로 고르세요. 00~02는 별이슬 액트 트리, 03~06 · 03+는 Pathcraft 구성안(탱정 액트별 트리 아님), 07은 탱정 저자본 저장본 트리입니다.</p></section>'+toc+budgetHTML+route.map((s,pos)=>card(s,pos)).join('')+buying+swapHTML+hcHTML+referenceHTML+'<section><h2>현재 → 목표 비교</h2>'+diffHTML()+'<div class="guide-links"><a data-page="passives" href="passives.html">패시브 트리</a><a data-page="skills" href="skills.html">스킬</a><a data-page="equipment" href="equipment.html">장비</a></div>'+((state.design.transitionHistory||[]).length?'<button id="restore-transition-target">불러오기 전 목표 복원</button>':'')+'</section><nav class="pager"><a data-page="interlude" href="interlude.html">← 막간 가이드</a><a data-page="low-budget" href="low-budget.html">최신 저자본 가이드 →</a></nav>';
host.querySelectorAll('details').forEach((e,i)=>{if(openDetails[i])e.open=true});
if(bindLegacy)bindLegacy();
host.querySelectorAll('[data-transition-check]').forEach(e=>e.onchange=()=>{checks['transition:'+e.dataset.transitionCheck]=e.checked;save();render()});
host.querySelectorAll('[data-transition-budget]').forEach(e=>e.onchange=()=>{state.transitionPlanning ||= {};if(e.value==='')delete state.transitionPlanning[e.dataset.transitionBudget];else state.transitionPlanning[e.dataset.transitionBudget]=Math.max(0,Math.min(e.dataset.transitionBudget==='ascendancy'?8:24,+e.value||0));save();render()});
host.querySelector('[data-transition-level]').onchange=e=>{state.transitionPlanning ||= {};state.transitionPlanning.level=Math.max(1,Math.min(100,+e.target.value||1));save();render()};
host.querySelectorAll('[data-transition-download]').forEach(e=>e.onclick=()=>download(e.dataset.transitionDownload));
host.querySelectorAll('[data-track]').forEach(e=>e.onclick=()=>{state.transitionPlanning ||= {};state.transitionPlanning.track=e.dataset.track;save();render()});
host.querySelectorAll('[data-transition-step]').forEach(e=>e.onclick=()=>{state.transitionPlanning ||= {};state.transitionPlanning.route=+e.dataset.transitionStep;save();render();document.getElementById('transition-'+route[state.transitionPlanning.route]?.id)?.scrollIntoView({block:'start'})});
host.querySelectorAll('[data-transition-load]').forEach(e=>e.onclick=()=>{if(!confirm('이 단계를 목표로 불러올까요? 현재 세팅과 기존 초안은 유지하고 이전 목표는 복원 기록에 보존합니다.'))return;state.design.transitionHistory ||= [];state.design.transitionHistory.push({target:clone(state.design.target),sourceSHA256:D.sourceSHA256,savedAt:Date.now()});state.design.target=template(e.dataset.transitionLoad);save();render()});
host.querySelector('#apply-reward-budget').onclick=()=>{state.transitionPlanning ||= {};state.transitionPlanning.quest=claimed;save();render()};
host.querySelectorAll('[data-shield-candidate]').forEach(e=>e.onchange=()=>{state.transitionPlanning ||= {};state.transitionPlanning.gear ||= {};if(e.value==='')delete state.transitionPlanning.gear[e.dataset.shieldCandidate];else state.transitionPlanning.gear[e.dataset.shieldCandidate]=Math.max(0,+e.value||0);save();render()});
const restore=host.querySelector('#restore-transition-target');if(restore)restore.onclick=()=>{const h=state.design.transitionHistory,last=h[h.length-1],old=clone(state.design.target);state.design.target=clone(last.target);last.target=old;save();render()};
};
