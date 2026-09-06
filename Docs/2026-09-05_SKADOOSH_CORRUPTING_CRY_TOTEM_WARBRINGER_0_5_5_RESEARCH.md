# Skadoosh "Corrupting Cry Totem Warbringer" — 0.5.5 HC 리그 스타트 리서치

- 작성일: 2026-09-05 (Forbidden Rites 이벤트 리그 시작 당일, KST 05:00 런칭)
- 대상: Skadoosh(YouTube @SkadooshPoE, Twitch skadoosh_c, poe.ninja 계정 ITheCon-2183)의 워브링어(Warbringer) 빌드 "[0.4] Skadoosh's Corrupting Cry Totem Warbringer"와, 그가 오늘 HC Forbidden Rites에서 실제로 굴리는 캐릭터.
- 표기 규칙: 게임 용어는 poe2db.tw/kr 또는 레포 기존 문서에서 확인된 한국어명만 병기한다. **한국어명 없이 영문만 쓴 이름은 전부 미확인**이며, 주요 이름은 첫 등장에 (한국어명 미확인)을 붙였다(보조 젬 등 나머지는 표시 없이 영문). AWT = Ancestral Warrior Totem(선대의 전사 토템, poe2db/kr 표기; 레포 기존 문서엔 이 이름이 없다 — 젬링 문서 grep 0회).
- 목적: 사용자가 **이 빌드를 직접 따라 하기 위한 실행 계획(0장)** + 그 근거(1~8장). 리서치 보고서가 아니라 플레이 준비 문서로 읽는다.
- 라벨: **사실** = 패치노트·poe2db·GGPK·캡처 파일에서 그대로 확인. **제작자 발언** = Skadoosh(또는 다른 제작자)의 말/글, 독립 검증 안 됨. **추정** = 이 문서의 해석.
- 근거 약어: E/S/L/U = mobalytics 캡처 `scratchpad/mobalytics/warbringer_endgame_full.txt` / `_starter_section.txt` / `_leveling_section.txt` / `_uber_section.txt`의 줄 번호. PN/<id> L<n> = `D:/Pathcraft-AI/data/_cache/patchnotes/poe2/<id>_*.txt`의 줄 번호(1행 = 제목). poe2db 버전 페이지 = `scratchpad/poe2db_txt/Version_<v>.us.txt`(캐시 밖 0.2.x~0.3.x 노트의 근거). 영상 = `https://youtu.be/<ID>?t=<초>` + [m:ss], 자동 자막 기준. 영상 약어: **BO** = BLc0SguI0gk(0.3 개요), **D1** = B8yBMkd-jsE(0.3 Day 1), **CA** = F6ou4sj0uZE(0.3 Corrupting Army), **VID-A** = CoskGFogxhA(0.4 플랜), **KsK** = KsK6tNjh50s(0.1 엔드게임), **gWQ** = gWQNu6xddow(0.1 우버). **Discord** = `scratchpad/discord_findings.md`(Skadoosh's Hideout #build-help·#clips-and-highlights, 데스크톱 클라이언트 스크린샷 전사, KST 표시 시각). GGPK 추출본(`data/game_data_poe2/`)은 0.5 데이터이며 0.5.5가 아니다.

---

## 먼저 기억할 결론

0. **따라 할 사람은 0장부터.** 1→33 레벨링(그의 가이드 + 24레벨 실캐릭 + POEGuy 교차 확인), 전직 순서, 33·46·53레벨 전환점, 하지 말 것, 매일 볼 URL이 0장에 있다. 그가 "전부 미검증"이라고 한 46+ 구간은 계획으로만 적었다. 방송 1일차에서 본인이 말한 것("I personally would not follow this though — I wouldn't follow what I'm doing unless you're really interested in playing a warrior — until I can showcase what it becomes")은 0.0절.
1. **빌드 한 줄.** 워브링어가 **지진 함성(Seismic Cry)**에 **타락시키는 비명(Corrupting Cry)**을 꽂아 화면 전체에 **타락한 피(Corrupted Blood)** DoT를 깔고, 전직 **전쟁 소집자의 고함(Warcaller's Bellow)**으로 함성 쿨다운을 무시하며 시체를 터뜨린다. 단일 대상은 무기 세트 2로 스왑해 **충격파 토템(Shockwave Totem)**(우버 변형은 AWT)을 깔고 **지진(Earthquake)** 요철 지대 + **대장간 망치(Forge Hammer)**로 처리하는 두-세트 빌드다. 〔근거: E:50–69, E:521–600〕
2. **가이드 상태(사실).** mobalytics 가이드 제목 `[0.4]`, 4개 변형 전부 "(outdated)", 헤더 "CHECK OUT NEW VERSION ON GEMLING IN 0.5!", 변경 로그 마지막 항목 2025-12-20. 프로필의 "Updated on Sep 5, 2026"은 오늘 저장 흔적이고, 0.5 변경 로그·젬/장비 갱신은 0줄 — 헤더의 젬링 링크 한 줄이 페이지 유일의 0.5 언급이다. 〔E:30–50, E:100–103, E:686–708〕
3. **오늘 실제로 하는 것(사실).** HC Forbidden Rites 캐릭터 `SkadooshShoutedHard` 레벨 24(스냅샷 updatedUtc 2026-09-04T23:16Z = 런칭 3h16m 후, lastSeen 23:13Z). 1차 전직 2점을 **Totem Life → 응답받은 부름(Answered Call)**에 썼다. 가이드가 못 박은 "첫 전직 = Warcaller's Bellow"(E:82–84)와 다르다. 지진 함성·타락시키는 비명은 없고 **충격파 토템 L7**(3소켓: Rapid Attacks I / Urgent Totems I / **포악함(Brutality) II**) + **지옥불 함성(Infernal Cry) L3** + 지진 L1 요철 지대 + **마그마 장벽(Magma Barrier)**이 골격이다. 스왑 무기 세트는 스냅샷에 없다. 생명력 733, 막기 33%, 저항 F/C/L/Ch −5/12/4/11(ninja가 −60 패널티를 적용한 값). 〔`scratchpad/ninja_shoutedhard.json`; 4장〕
4. **0.4→0.5 최대 변화(사실).** 0.5.0 노트: "Corrupting Cry I, Corrupting Cry II: No longer causes the supported skill to inflict Corrupted Blood, but instead it triggers a skill which inflicts Corrupted Blood, scaled by the level of the gem it is socketed into." (PN/3932540 L1044). 새 발동 스킬 **타락한 함성(Corrupted Cry)**의 피해는 소켓된 함성 젬 레벨 표로 정해진다 — lv1 5.9/s, lv3 12.5/s, lv11 71.6/s, lv20 287/s, lv27 806.4/s, lv40 6119.2/s — 그리고 스탯 블록에 힘(Strength) 항목이 없다(https://poe2db.tw/us/Corrupted_Cry). "modifiers to warcry damage also apply to this skill" 한 줄은 남아 있다. 정리: **힘은 더 이상 기본 피해 입력이 아니다**(사실). 힘에서 파생된 "함성 피해 증가" 류가 아직 흘러들어가는지는 어떤 소스도 답하지 않는다(미확인).
5. **Skadoosh 본인의 판정(제작자 발언).** 2026-05-25 영상: "Does that mean it doesn't scale with strength anymore? Maybe." [13:36] → "it was playable last season, but now of course it's going to need a couple of big changes and I wouldn't recommend it honestly in the 3.5 [sic, 자막; 문맥상 0.5]. The total tank is good though, but yeah." [13:46–13:56] https://youtu.be/Jj2eKr4Ez-A?t=826. 자막은 "total tank"이고 "totem tank"가 아니다(음성 미확인). 05-25 시점 0.5 스타터 계획은 "the build that I'll probably actually be league starting in 0.5 is whirling assault most likely stun titan" [23:49] https://youtu.be/Jj2eKr4Ez-A?t=1429(실행 여부는 자막으로 미확인; Discord 09-02 01:12 "I have 2 titans in 0.5 / Concussive was my league starter", 채널의 06-06 개요 영상은 "Concussed Titan Ward Stacker"), 6월에 젬링(Gemling Legionnaire) 포크 "Corrupting Wings"를 만들었다. **오늘 워브링어로 돌아온 이유와 계획은 본인 Discord에 있다**(#build-help 2026-09-02 01:07–01:32, 09-03 19:40–20:30 KST): "I'm playing warbringer for 0.5.5 / Will be a lot more focus on the totems" · "it's a leaguestart able version of corrupting cry / And doesn't require any uniques" · "**Guide is outdated / I'll be using fortifying like Gemling**" · "instead of seismic and stacking strength, use fortifying and get melee levels again, technically it's all untested, and i'll be playing HC at least at teh start" · "At endgame it will be 2 [buttons] probrably. Totem for rares, and corrupting cry to detonate Earthshatter spikes, and apply corrupted blood/crit weakness, regen hp" · "I'll be using ancestral warriors" · "I'll be using ancestral bond for ancestral warrior totem" · "currently the idea is only rare gear and the build won't be meta". 정리: 0.5.5 계획 = 지진 함성·힘 스택 대신 **보강하는 함성 + 근접 스킬 레벨(젬링식)** + **AWT + 선대의 유대(Ancestral Bond)** 키스톤 + 함성으로 지면 분쇄 스파이크 파쇄, 레어 장비만, 본인 표현으로 "전부 미검증". 이 문서의 2·5장은 0.4 가이드 기준이고, 실캐릭(4장)에서 이 계획이 나타나는지는 다음 스냅샷의 관찰 대상이다. 방송 1일차 VOD 전사(0.0절)가 이 계획을 본인 음성으로 확인한다 — 선대의 유대, Howling Beast 치명 약화, 혈마법, "Corrupting Cry, I can't use until level 45 plus-ish", 그리고 "I personally would not follow this though". Rallying 코어·메아리치는 함성은 젬링(Corrupting Wings) 문의에 답하며 나온 말이라 워브링어 계획으로 단정하지 않는다(8.2 S3·S8).
6. **가이드 레벨 규칙의 역전(추정, 근거는 사실 — 0.4 가이드 기준).** "Keep Seismic Cry at lvl 11"(S:167–169), "Infernal Cry should be kept at lvl 3"(L:132–134, S:171–173)는 0.5에서 정반대로 작용한다. 함성 젬 레벨이 곧 타락한 피 피해이므로 lv3 지옥불 함성에 타락시키는 비명 I을 꽂으면 12.5/s, lv11 지진 함성이면 71.6/s다. 0.5.5 신규 소울 코어 **Jiquani's Soul Core of Rallying**(한국어명 미확인) "+1 to Level of all Warcry Skill Gems"가 직접 레버가 된다. 제작자의 0.5.5 계획(결론 5)은 지진 함성이 아니라 보강하는 함성 레벨 스택이므로, 이 역전은 가이드를 그대로 따르는 사람에게 해당하고 Rallying 코어의 +1은 보강하는 함성에도 똑같이 닿는다(사실: 문구가 "all Warcry Skill Gems").
7. **살아 있는 것(사실).** Warcaller's Bellow 텍스트 "Warcries Explode Corpses dealing 25% of their Life as Physical Damage / Ignore Warcry Cooldowns" 그대로(0.5.2는 같은 시체 무한 폭발 버그만 수정). 응답받은 부름 "+1 to maximum number of Summoned Totems / Trigger Ancestral Spirits when you Summon a Totem"(0.5.0 핫픽스 3에서 혼백 "took no actions" 버그 수정). **나무 벽(Wooden Wall)** 20%, **비취의 전승(Jade Heritage)**, **거북이 호신부(Turtle Charm)** 무변경. AWT "Consume 3 Endurance Charges … Cannot have more than 10", 0.4.0에서 "25% less Totem Attack Speed" 삭제, 0.5.0에서 숨은 0.6초 딜레이가 "50% of the skill's attack time"으로 교체. 제작자가 예고한 **선대의 유대(Ancestral Bond)** 키스톤은 0.5.0 L790 "Your Totem Limit is doubled, No Charge requirement for placing Totems, Totems reserve 75 Spirit each"(poe2db 라이브 동일) — AWT의 3충전 관문이 사라지는 대신 토템당 정신력 75가 관문이 된다(레벨 24 실캐릭의 정신력은 30, 전부 마그마 장벽). 충격파 토템 무변경, 지진 여진 184–666%(0.5.0 상향). 워브링어 전직은 0.5.0 노트에 0줄.
8. **죽은 것(사실 + 제작자 발언).** Uber Endgame 변형(Hateforge 인내 충전 엔진): 0.4.0(12-09 추가분) "Now has Gain a random charge on reaching maximum Rage, no more than once every 3-6 seconds (previously 1-3 charges)" + "Guatelitzi's Soul Core of Endurance is now Limited to: 1." 제작자 로그 "It's killed, Uber endgame variant dead for now"(E:698–700). **새로운 활력(Second Wind) III** 함성 회복 트릭은 0.3.1에 죽고(제작자 changelog E:684–685 "no longer works with no cd warcrys"; GGG 0.3.1 노트·poe2db 0.3.1 페이지엔 Second Wind 0회 → GGG 문구 미확인) 0.4.0에서 2%→1%로 반감됐는데(PN/3883495 L409, 사실), Endgame 변형의 **보강하는 함성(Fortifying Cry)** 소켓에는 오늘도 꽂혀 있다(가이드 내부 모순, E:702–704 "Forgot to remove").
9. **0.5.5 사실.** 밸런스 섹션 없음(TOC 9개 섹션; 함성/토템/워브링어/타락한 피 0회). 그러나 Bug Fixes 네 줄이 이 두-세트 빌드에 기능 변경으로 작용한다: "Fixed a bug which would allow Skills from an alternate Weapon Set to be used without the corresponding Weapon swap occurring." / "…Auras and Support Gems from an inactive Weapon Set to still apply to the player." / "…snapshot the effects of the Prism of Belief and From Nothing Unique Jewels." / "…using a Unique item granted Skill with non-Unique Weapons which were equipped in another Weapon Set." (PN/4000864 L389/393/391/395). 리그: HC는 SC에 parented(죽으면 SC Forbidden Rites로 이어감), 캠페인 전 지역 Ritual, 1.0(12-11)까지 진행. 신규 소울 코어 17종 중 Rallying/Quaking/Automation(함성/강타/토템 젬 +1)이 이 빌드 대상.
10. **HC 주의(사실).** 기본 막기 상한 50%(거북이 호신부로 75%), **Titanrot Cataphract(거신부패 비늘 갑옷)**는 "You have no Life Regeneration", **혈마법(Blood Magic)** 아래 함성 비용은 생명력(지진 함성 lv20 = 85 마나 상당), **파콰테의 맹약(Paquate's Pact)**은 최근 4초 내 사용·발동 횟수당 최대 생명력 10%, 상한 30% 비용, 0.5.4b부터 피격 중 포탈 불가, 0.5.1부터 로그아웃해도 강타 기절 유지, **룬 수호(Runic Ward)**가 새 방어층. 0.5에서 AWT+지면 분쇄 워브링어를 HC로 굴린 Sesul은 죽었다(제작자 발언).
11. **래더/커뮤니티(사실).** HC Forbidden Rites 11시간 시점 2,658명 중 워브링어 13명, Corrupting Cry I/II·파콰테의 맹약·AWT 소켓 캐릭터 0명. 0.5 본 리그(Runes of Aldur)에서 "지진 함성 + 타락시키는 비명 + AWT 스왑" 조합은 사실상 발자국이 없고, 살아남은 형태는 보강하는 함성 + 파콰테의 맹약 + 근접 스킬 레벨 스택(Xeph 등). Maxroll 0.5.5 스타터 티어표에 이 빌드 없음. 공식 포럼 스레드 제목이 "Corrupting cry is dead".
12. **검증 못 한 것.** 제작자 본인 PoB 공개본 없음(mobalytics 페이지 텍스트에 트리 없음 → export payload로 복원, 0.5 GGPK 이름으로 매핑; Discord에도 PoB·문서화된 세팅 없음), 4h42m Twitch VOD(v2865212551)는 자막이 없어 0:00–1:32 연속 + 이후 질문 구간만 전사(0.0절; 1:32 이후 게임플레이 잡담은 대부분 미전사), 타락한 피 갱신 규칙, 타락한 함성의 힘 스케일 여부, 스왑 세트 존재(스냅샷에 없음), Discord 계획(보강하는 함성 + 근접 레벨 + AWT + 선대의 유대)이 실캐릭에 언제 나타나는지 — 제작자 스스로 "전부 미검증", "Seismic Cry gives double power" 버그 잔존 여부, "total/totem tank" 음성.

---

## 0. 오늘부터 따라 하기 — 실행 계획

사용자 목표는 "Skadoosh 것을 그대로 한다"이다. 이 장은 1~8장의 근거를 **누를 것·살 것·찍을 것** 순서로 다시 쓴 것이다. 라벨은 같다 — **사실** / **제작자 발언** / **추정**. 그가 본인 입으로 "technically it's all untested"(Discord 09-02 01:29)라고 한 부분은 그의 *계획*이지 검증된 세팅이 아니므로, 그 구간은 그의 캐릭터가 실제로 그렇게 되는지(0.7) 보면서 간다.

### 0.0 방송 1일차 VOD에서 그가 직접 말한 것 (제작자 발언, 전사)

Twitch VOD v2865212551(4h42m, 자막 없음)을 **채팅 리플레이(175건) + 시청자 질문 시각의 음성 국소 전사(Whisper large-v3-turbo, 로컬)** 로 읽었다. 원문·방법·ASR 주의는 `scratchpad/twitch_findings.md`, 전사 파일 `scratchpad/twitch/audio/*.txt`. 인용은 ASR을 읽기 쉽게 다듬은 것이다(명백한 오인식 교정, 완충어·반복 생략); 고유명사 교정과 삽입은 [ ]로 표시했다. 축자 원문은 전사 파일에 있고, 시각은 전사 세그먼트 시작 시각이라 실제 발화는 그 뒤 수십 초 안에 있다. 0:00–1:32는 연속 전사, 그 뒤는 시청자 질문 시각만 국소 전사했다.

| 시각 | 발언(요지·인용) | 이 문서에 미치는 것 |
|---|---|---|
| 0:03:15 · 0:09:45 | "it's not technically a new build … more like a rehash or a rework … reforged" / (옛 PoB를 열며) "this is what [the] warcry build was before … this Corrupting Cry just wasn't that good back in the day … **I'm going to reconfigure this into a build that can be played in 0.5 or 0.5.5. This current version is technically playable but [that was] before … [you] scale strength and stuff, which I don't do anymore**" | 0.4 가이드 = 원형, 0.5.5 = 재구성. 결론 4·6과 일치 |
| **0:15:50–0:16:25**(세그먼트 [0:15:13]) | "**I usually don't like saying you should try the thing that I'm trying … I don't know if it'll be good. Well, it'll be solid I think, but I'm gonna be playing hardcore … it's a bit more hardcore-oriented. It's slower, not as comfy as other builds, but somewhat league-start friendly. I personally would not follow this though — I wouldn't follow what I'm doing unless you're really interested in playing a warrior — until I can showcase what it becomes. It's definitely gonna be slower, a bit more buttons**" | **본인이 "아직 따라 하지 말라"고 했다.** 이 문서를 따라 시작하는 건 그 경고를 안고 하는 것이다 |
| 0:13:03–0:14:32 | mobalytics 가이드를 방송 중 편집: "delete all of this … [this endgame utilises Ancestral Warrior Totem with Earthshatter — ASR 'Estreau if earth shatter', 문구는 캡처 E:66–70에서 복원] … add this to all [variants] … in case people are clicking on this guide expecting exactly what I planned" | 방송 중 각 변형에 AWT+지면 분쇄 안내문을 넣었다(사실: 음성+캡처). "(outdated)" 표기가 이때 붙었는지는 발언에 없다(미확인). 프로필의 "Updated on Sep 5"가 이 편집(09-04 18:43Z; 표시 시간대에 따라 Sep 4/5)인지는 추정 — 어느 쪽이든 0.5.5 개정은 아니다(결론 2) |
| 0:20:00(프레임) | **비공개 PoB "Skadoosh' Corrupting Cry Warbringer 0.5"** 화면: 96레벨 계획, 119/123점, 메인 스킬 드롭다운 "Ancestral Warrior Totem, Earthshatter" + "Ancestral Warrior Totem" ×2, Full DPS 2,598,134(15× Earthshatter 2,569,332), "Best Corr. Blood DPS 28,802 from Corrupted Cry", 생명력 2,766, 재생 213.7/s, 방어도 11,558(물리 감소 60%), 정신력 427(미예약 7), ES 430, 힘 341, 저항 F 6 / C −26 / L −26 / Ch 37, 이동 +28.3%, 트리 0_5 | PoB는 존재하고 계획 수치가 이렇다(사실: 화면). 저항이 캡 미달이라 완성본이 아닌 것으로 보인다(추정). 타락한 피는 2.6M 중 28.8k — **딜은 토템(지면 분쇄), 타락한 피는 클리어 보조**라는 구조가 숫자로 보인다. 추가 프레임(0:18:00~0:40:30, 화면 시각 09-04 20:48~21:10, 출시 전 대기열 1,139명): PoB Community Fork 0.23.1, 트리 스펙 4개 — Default(96~97레벨, 118~120/123점, 세트1·세트2 각 24/24) · Act 1(18레벨, 21점, 세트1 3/24) · Act 2(22레벨, 25점) · Act 3(49레벨, 60점, 세트2 12/24). Act 3 49레벨 수치: 힘 211, 생명력 1,824, 방어도 6,254, Full DPS 372k. 96레벨은 마나 비용 0 · 생명력 비용 187(초당 966) = 혈마법이 트리에 있다(사실: 화면). 호버한 노드: Vigilance(막기 확률 12%, 막기 시 생명력 10, 최대 막기 +2%; 세트1 할당 모드) · Reverberating Impact(방어도 파괴 25%, 공격 범위 12%; Act 3). Skills·Items 탭은 어느 프레임에도 없다 — 젬 링크와 장비는 PoB 화면으로는 못 읽는다 |
| 0:29:41–0:31:28 | "**act three is going to be a different one — this is where I'm going to try out OG** … I can post the PoBs I guess, but when I make PoBs I end up completely switching up a lot of stuff when I actually play … **I don't want to bait … so ideally people just follow me on stream if they want to play the build I'm playing, and I'll usually update as I go along**" | PoB 공개 미정. 추적 경로 = 스트림·ninja(0.7) |
| 0:38:23–0:39:57 | "**just this node here allows me to basically apply maximum Critical Weakness just by spamming warcries, and this one which gives me damage when I apply warcries, and it just buffs up my totems to an insane degree** … now that totems can use your weapon it's easier to scale crit … **I wonder if these nodes actually work … once my totem is crit … or if it snapshots from me**" | 노드 이름은 이 구간에 안 나오고 4:40:38 "this Howling Beast"로 확인(추정: 같은 노드) — **Howling Beast** "Warcries inflict 3 Critical Weakness on Enemies"(poe2db, 드루이드 늑대 노터블; 각인 가능). 함성→치명 약화→토템 크릿 축은 **본인도 작동 여부 미확인** |
| **0:40:03** | "**I'll be using Ancestral Bond now instead of endurance charges to get totems. Problem is the defenses — the defense is not bad, Warbringer is a pretty tanky class, but I don't know if it's enough. I have this wheel and that's it … I have block … I don't think that's enough, I think I need much more armour; if I can get armour on jewels maybe that's fine**" | 선대의 유대 확정(제작자 발언). HC 방어는 본인이 걱정 중 → 6장 |
| 0:41:01 | "Sanguine Tolerance — immune to Corrupted Blood — this might be a really good anoint in this league, if you can do [Trial — ASR 'Temple'] of Chaos" | 방어용 각인 아이디어(몬스터가 거는 타락한 피 면역) |
| 0:42:15–0:45:55 · 채팅 0:42:42 | poe2db에서 0.5.5 소울 코어를 발견: "**that's going to make the build like 1 billion times cheaper. It has to be socketed in a weapon** … new soul core in weapon, +1 to warcries … it just solves a lot of problems … means you don't need a sanctified [weapon/gloves]" / 채팅에 직접 "Rallying +1 to Level of all Warcry Skill Gems" | **Jiquani's Soul Core of Rallying**(무기 소켓, 레벨 50; 출처 Trial of Chaos는 0.5.5 L79/L137 기준) — 함성 젬 전반의 0.5.5 버프(3.5·0.5). 이 대화의 맥락은 젬링(Corrupting Wings) 장비("sanctified gloves/weapon", Kopec orb)이지만 문구가 "all Warcry Skill Gems"라 워브링어의 보강하는 함성에도 그대로 닿는다(사실) |
| 1:02:25 | "**Corrupting Cry I is a tier three support gem so that won't work until at minimum act three, and even then at that point you want to use Fortifying Cry** … **you kind of need Echoing Cry to get three and sustain the cry** … **Echoing Cry is a tier five support which comes in like end of act 4** … Seismic Cry also does damage but not significant … **it's not viable in the campaign**" | **젬링 레벨링 질문(1:02:29 odeitxo "level up … a gemling legionnaire with infernal cry + corrupting cry I?")에 대한 답.** "Corrupting Cry I = 3막 최소, 그때는 보강하는 함성"은 일반론이라 워브링어에도 닿는다(0.4절 보강). 메아리치는 함성이 *그의 워브링어* 계획에 있는지는 발언이 없다 — 전쟁 소집자의 고함이 쿨다운을 없애므로 필요성 자체가 다르다(추정, 8.2 S8) |
| 1:31:55 | (이 빌드 가이드 있나?) "**Not currently. No. I have an old guide which has very similar leveling setup … the leveling setup is basically the same … but what I'm planning to do, like endgame or late campaign, is not there**" | 0.2절(레벨링)만 가이드와 같다는 본인 확인 |
| 2:59:44–3:01:26 | (언제 본 빌드로?) "I use totems at like act two … **the actual build when I use Ancestral Warrior Totems … I'm not exactly sure honestly, this is the first time I'm doing it** … **Ancestral Warrior Totems will be a bit later on, at the start of endgame; the normal totem setup gets you through campaign** … **Corrupting Cry, I can't use until level 45 plus-ish**" | 전환 시점 본인 미정. AWT = 엔드게임 초(젬 요구 53과 맞음) |
| 3:57:19 (· 3:35:30) | (왜 다시 Corrupting Cry?) "**for specifically this build, not typically — it's just a league starter version I guess, but it focuses more on totems; there's some cool totem stuff that is good with it, especially Ancestral Bond** … but for Corrupting Wings in 0.5.5 there's actually a new rune that goes in your weapon that gives you +1 warcries, which is an insane buff" / 3:35:30(MadWolfTTV의 Corrupting Wings 질문에) "the build's looking pretty good though, we got a buff this league — a new rune … +1 to level of warcries" | 워브링어 복귀 이유로 든 것은 **리그스타트 가능 + 토템 중심 + 선대의 유대**뿐이다(8.2 S3 해소). Rallying 코어 칭찬은 같은 답의 후반과 3:35:30 모두 **Corrupting Wings(젬링) 맥락**이다 — 워브링어에도 닿는 사실이지만 그의 복귀 이유로 적으면 안 된다 |
| **4:39:49–4:41:33** | (최종 목표?) "**I'm playing hardcore … to beat the game, do all the challenges on hardcore. But the actual build is gonna be a warcry-spamming [Ancestral Warrior?] Earthshatter build: I'll be putting down Ancestral Warrior Totems via [Ancestral] Bond … and I'll spam warcries to explode the Earthshatter spikes, apply Corrupted Blood — hopefully I can use Corrupted Blood purely for clear as well; totems are just for killing tanky mobs — and then with this Howling Beast I'll apply Critical Weakness and I'll have my totems crit a ton. It's like a combo warcry totem build** … it's going to take a while because I'm playing hardcore" | 0.5절의 최종 형태를 본인 문장으로 확정. "ancestral cry"로 들리는 부분은 ASR 불확실(Ancestral Cry 젬은 카옴 화신 함성이라 문맥과 안 맞음 — 추정: "ancestral warrior") |
| 0:50:05–0:52:34 | (젬링 플레이어 reapershell777의 "figure out the spirit"에 답한 것; "my character" = 그의 0.5 Corrupting Wings 캐릭터 — 이 시각엔 HC 워브링어가 아직 없다) "it's not mandatory but you definitely want the plus one … it means you don't need the Kopec orb or you don't need to sanctify … Prism of Belief will not exist early league … **40 is the max, you can't go over 40 [gem level] — on my character I have 40; I took out the support gem for +1 because I have 41, so I added an AoE**" | 젬 레벨 상한 40(제작자 발언; 결론 6의 레벨 표와 맞물림). +1 소스가 늘면 Physical Mastery 자리를 다른 보조로 |
| 0:55:35 · 0:56:56–0:57:38 | "we're just gonna wing it like I usually do … I'm not like other people where I make a whole new video guide for league start" / "**This would be an interesting build to min-max, if I can even get to that point on hardcore. If I die, I'll probably just go softcore and keep playing** … ideally I can keep it going hardcore. **The interesting thing is that [Ancestral] Bond allows me to do this, because the build didn't really work and I don't want to transform into bear to generate endurance charges — you can, but it's slow and annoying, it makes you stand still**" | 선대의 유대가 이 빌드를 되살린 이유(3충전 관문 삭제). HC 사망 시 SC 계속(Discord 09-02 01:15와 일치) |
| 0:59:08–0:59:21 | (트리) "I don't want any crit chance … 10% crit chance is just all damage(?) … **we're gonna go Blood Magic** though … too many points" | 혈마법 키스톤은 계획에 있다(제작자 발언). 24레벨 실캐릭엔 키스톤 0 |
| 1:05:11 | "**I'm going to play warcries as a league starter on a Warbringer though, which is just a different build — it's like more of a totem build, [totems] placed for single target(?)**" | 젬링(Corrupting Wings)과 다른 빌드라고 본인이 선을 그음 |
| 1:21:06–1:22:22 | "one thing I want on this build … [Vorana's?] Carnage … **recover 5% of max life when you use warcry … with the node [다급한 부름 2%] gives you 7% every time you warcry — you just spam that and you're full HP instantly. It does mean that the warcry / corrupting cry aspect of this build will definitely take a sideline; hopefully it's enough to kill white mobs and blue mobs, but it will definitely not be enough to kill bosses**" | ASR "Warner's carnage" = **Vorana's Carnage**(poe2db: 투구 Augment 소켓 룬, "Can roll Berserking modifiers", 접미 "Recover (4—5)% of maximum Life when you use a Warcry", 드롭 레벨 65; 0.5.4 노트 L77에 이름 등장 — 사실). 함성 = 회복·클리어, 보스 = 토템이라는 역할 분담을 본인이 명시. 0.5.4b "Recover X% of maximum Life when you use a Warcry" 수정의 소스 = 이 Augment 접미(8.1 Q10 해소) |
| 1:26:23 · 1:32:00 | "it's an event league, I think it's fine to just take it easy … **I'm playing hardcore, which I'm definitely not prepared for. Just kind of YOLOing it** … I'm sure it'll be fun before I die, like first boss" / "**I think I've yet to play hardcore to the endgame** … oh, you can't respawn at a checkpoint on a hardcore character, I forgot about that" | 그의 HC 경험은 얕다(본인 발언). 6장의 HC 근거를 그의 검증으로 읽으면 안 된다 |
| 채팅 | `!build` → Nightbot 링크는 0.4 가이드(본인: 0:02:02 "I don't have a link for what I'm going to play … might as well link to my old build") | 0.7 추적 경로 |
| 프레임 | 4:30:00 Sekhemas 시련 제단 + 퀘스트 트래커 "Ascent to Power: Use the Relic Altar to start the Trial"(sec_16200.jpg) → 4:41:30 종료(733/733; 레벨 24는 ninja 스냅샷 값) | 응답받은 부름은 방송 막바지 시련 뒤에 찍었다(추정: 제단 시각 + 23:16Z 스냅샷의 전직 2점) — 4장 스냅샷 = 방송 종료 상태 |

### 0.1 전제 — 그가 정한 것

| 항목 | Skadoosh | 근거 |
|---|---|---|
| 리그·모드 | **HC Forbidden Rites, 트레이드.** HC에서 죽으면 캐릭터는 SC Forbidden Rites로 이어진다 | Discord 09-03 19:40 "Current plan is hardcore trade"; 0.5.5 L53(사실) |
| 클래스 | Warrior → **워브링어(Warbringer)**. 캐릭터명 `SkadooshShoutedHard` | poe.ninja(사실) |
| 장비 방침 | **레어만.** "doesn't require any uniques" / "currently the idea is only rare gear" | Discord 09-02 01:17, 09-03 19:47(제작자 발언) |
| 기대치 | "won't be meta… too slow I think" / "Should be really tanky and have really good damage" / 죽어도 리롤 안 함("Unless I get another idea for a build") | Discord 09-03 19:47·20:30, 09-02 01:15(제작자 발언) |
| 최종 형태 | **2버튼**: 세트2 **선대의 전사 토템(AWT)**("Totem for rares"; 보스 용도는 추정) + 세트1 함성(**보강하는 함성** + 타락시키는 비명)으로 **지면 분쇄(Earthshatter)** 스파이크 파쇄·타락한 피·재생. 힘 스택 대신 **근접 스킬 레벨 스택**, AWT는 **선대의 유대(Ancestral Bond)**로 | Discord 09-02 01:22·01:25·01:29, 09-03 19:48·20:27(제작자 발언, 미검증) |
| 0.4 가이드 | **낡았다.** "Guide is outdated / I'll be using fortifying like Gemling" — 젬 링크·트리는 그대로 따르지 말 것 | Discord 09-02 01:25–01:26(제작자 발언); 5장 유효성 열 |

### 0.2 1 → 33레벨 — 그의 레벨링 가이드 + 24레벨 실캐릭

레벨링은 검증된 부분이다. 그의 "Warrior Leveling 1-33"(2026-01-06, 태그 HC/SSF)과 오늘 24레벨 스냅샷이 같은 루프를 쓰고, 다른 제작자 POEGuy의 워브링어 레벨링 가이드(0.5.0 태그 페이지, 2026-09-03 갱신)가 1막~2막 초입까지 같은 경로다(0.2.4). 젬 레벨 요구치는 GGPK 0.5 `SkillGems.MinLevelReq`(사실; 0.5.5 미대조).

**0.2.1 밴드별 젬 (가이드 원문 순서, 세트 배정 포함)** 〔`scratchpad/mobalytics/leveling_Level_*_section.txt`〕

| 밴드 | 세트1 (한손 철퇴 + 방패) | 세트2 (양손 철퇴) | 세트 무관 | 가이드 팁 |
|---|---|---|---|---|
| **1–10** | (세트 표시 없음 — 가이드는 11–20부터 세트를 배정한다) | (세트 표시 없음) | Mace Strike · Boneshatter(뼈 박살) → Impact Shockwave · Rolling Slam(몰려오는 강타) · **지옥불 함성 lv3 고정**("NEVER upgraded") · Raise Shield(방패 들기) | Rolling Slam(또는 Mace Strike)으로 기절 프라임 → Boneshatter 광역. 방패 들기 후 막고 놓으면 방패 타격(기절 축적). 구르기 중 스페이스 유지 = 스프린트 |
| **11–20** | Rolling Slam → Stun I; **지진(Earthquake)** → Prolonged Duration I; **마그마 장벽**(정신력 30) | Mace Strike; Boneshatter → Impact Shockwave · Magnified Area I; **충격파 토템(Shockwave Totem, lv7~)** → Overabundance I · Brutality I | 지옥불 함성 lv3 | **"Don't forget to equip a 2-handed mace in weapon set 2!"** 지진으로 보스 밑에 요철 지대 여러 장 → 충격파 토템으로 폭발. 방패 막기 → 마그마 장벽 인내 충전 → 지옥불 함성 쿨 리셋. G 메뉴에서 스킬별 세트 지정 |
| **21–30** | Mace Strike; Rolling Slam → Brink I; 지진 → Prolonged Duration I · Persistent Ground I; 마그마 장벽 | Boneshatter → Impact Shockwave · Magnified Area I; 충격파 토템 → Overabundance I · Urgent Totems I; **화산 균열(Volcanic Fissure, lv23)** → Rage I · Jagged Ground I; Herald of Ash | 지옥불 함성 | "방패 들기 → 마그마 장벽 인내 충전 → 화산 균열(요철 지대 I) → 그 위에 충격파 토템". 젬 레벨 우선 셋: 충격파 토템 · Rolling Slam · Boneshatter("Prioritize …" — 순서 아님). 골드 리스펙 발생 |
| **31–41** | Rolling Slam → Brink I; 지진 → Persistent Ground I · Encroaching Ground; 마그마 장벽 | Boneshatter → Impact Shockwave; **대장간 망치(Forge Hammer, lv32)** → Fist of War I · Rageforged I(화산 균열 대체, 인내 충전 불필요, 지옥불 함성으로 버프); 충격파 토템 → Overabundance I · Rapid Attacks II; Herald of Ash | 지옥불 함성 → Raging Cry | 3막 첫 지역 Sandswept Marsh(Orok Campfire)의 **Lesser Jeweller's Orb**는 "Corrupting Cry 빌드용으로 아껴라". Venom Draught = 기절 한계치(6막은 카오스 저항). 보조 젬 몇 개는 전환용으로 남겨라. **33레벨 또는 Corrupting Cry I 입수 시 골드로 리스펙** |

**0.2.2 24레벨 실캐릭이 실제로 든 것(사실, 스냅샷 2026-09-04T23:16Z)** — 4장 요약. 가이드 21–30 밴드와의 차이는 **Rapid Attacks I·Brutality II·Encroaching Ground 추가 / Magnified Area I·Overabundance I·Prolonged Duration I·Herald of Ash·Mace Strike 제외, 공명하는 방패 추가**.

- 충격파 토템 L7 → Rapid Attacks I · Urgent Totems I · **Brutality II**(3소켓 = Lesser Jeweller's Orb 사용, 추정) / 지진 L1 → Encroaching Ground · Persistent Ground I / **공명하는 방패(Resonating Shield, lv15)** L7 → Rage I / 화산 균열 L7 → Jagged Ground I / Rolling Slam L6 → Brink I / Boneshatter L6 → Impact Shockwave / 지옥불 함성 **L3** / 마그마 장벽 L4(정신력 30 전부) / 방패 들기 / 선대의 혼백(응답받은 부름 부여).
- 장비: 레어 한손 철퇴(물리 101% + 물리 5–11 추가 + 룬 소켓 "14% increased Physical Damage" = Lesser Iron Rune), 레어 거대 방패(생명력·힘·저항·기절 한계치), **Bronzebeard**(유니크 투구, 생명력 +100, 이동 속도 −10%), 레어 갑옷/장갑/장화(생명력·저항, 장화 이동 속도 15%), **Surefooted Sigil**(유니크 목걸이), 레어 반지 2·허리띠, 루비 주얼(토템 피해 14%), 생명력+마나 플라스크, Sapphire Charm. 즉 **레어 + 저렴한 유니크 2개**.
- 트리(29점): 근접 피해 소노드 ×8, Brutal, Smash, Ancestral Mending(토템 보유 시 재생), Totem Life/Damage, 주얼 소켓, 속성 노드 9개 중 8개 힘. 세트1 = Spike Pit·Perforation·Jagged Ground Effect ×2·Block·Bleed Chance. 세트2 = Ancestral Artifice(근접 공격 스킬 토템 +1)·Ancestral Unity·Totem Attack Speed·Totem Damage·Attack Damage ×2. PoB 트리 URL은 4.3.
- 수치: 생명력 733 · 막기 33% · 저항 −5/12/4/11(ninja −60 패널티 적용; 냉기 12는 Sapphire Charm +25 포함, 미발동 시 −13) · EHP 1,035. **저항이 가장 약하다** — 따라 하는 사람은 2막부터 룬(Desert/Storm/Glacial)으로 저항을 채울 것(가이드 11–20 팁).
- 스냅샷에 세트2 무기가 없다(사실). 가이드는 11레벨부터 세트2 양손 철퇴를 요구하고 세트2 트리를 찍었으니 착용 의도는 확실하다(추정) — 따라 하는 사람은 **세트2에 물리 높은 양손 철퇴**를 끼운다.

**0.2.3 로테이션 — 버튼 순서와 그 이유(가이드 팁 + GGPK/poe2db 스킬 원문 대조, 2026-09-05 적대검증 2렌즈 반영)**

가이드 팁은 순서만 주고 이유를 안 준다. 왜 그 순서여야 하는지는 스킬 원문에 있고, 그중 셋은 순서를 어기면 **아무 일도 안 일어난다**.

*세트와 스왑(사실).* 세트 2 전용으로 지정한 스킬을 누르면 그 세트로 즉시 스왑된다 — 0.5.5 L389가 "스왑 없이 대체 세트 스킬을 쓰던 버그"를 고쳐 스왑이 강제됐고, 스왑 자체는 0.3.0부터 즉시다(poe2db Version_0.3.0; 가이드 changelog 동일). **L393은 스왑 근거가 아니라 "비활성 세트의 오라·보조 젬이 계속 적용되던 버그" 수정이다 — 즉 세트 2에 있는 동안 세트 1 버프인 마그마 장벽은 꺼진다.** 세트 1 스킬(몰려오는 강타)이나 방패 부여 스킬(방패 들기)을 누르면 세트 1로 돌아온다(가이드 changelog "Perfect Strike → Raise Shield").

*무기 세트 패시브는 일반 포인트를 쪼개 만든다(가이드 11–20 원문).* "빨간 선이 세트 1, **초록 선이 세트 2** 패시브 포인트" / "트리에서 무기 세트 패시브를 찍으려면 먼저 **일반 패시브 포인트 1개가 남아 있어야 한다. 그것이 둘로 쪼개져 각 세트에 1개씩** 들어간다." 그래서 두 세트의 소비량은 항상 같다. 가이드의 잔여 포인트 표(밴드별 화면값)와 실캐릭이 정확히 맞는다.

| 밴드 | 일반(잔여/최대) | 세트 1 | 세트 2 | 소비 |
|---|---|---|---|---|
| 1–10 | 114 / 123 | 20 / 20 | 20 / 20 | 0 |
| 11–20 | 96 / 123 | 16 / 20 | 16 / 20 | 4 |
| 21–30 | 84 / 123 | 14 / 20 | 14 / 20 | 6 |
| 31–41 | 70 / 123 | 12 / 20 | 12 / 20 | 8 |

25레벨 실캐릭도 세트 1·2 각 6개다(0.2.2) — 21–30 밴드의 6과 일치한다. 세트 최대는 20이고, 퀘스트로도 들어온다(0.4.0 L1397 "Dark Mists 퀘스트가 **무기 세트 패시브 포인트 2개**를 주는 Mist-shrouded Tome 을 준다"). 실캐릭의 배분은 **세트 1 = 방패·요철 지대**(Spike Pit·Perforation·Jagged Ground Effect ×2·Block·Bleed Chance), **세트 2 = 토템**(Ancestral Artifice·Ancestral Unity·Totem Attack Speed·Totem Damage·Attack Damage ×2)로 갈린다 — 토템을 세트 2에서 깔기 때문이다.

*인내 충전은 하나짜리 예산이다(사실, 21레벨부터).* 충전 하나는 다음 중 **하나에만** 쓰인다.
- **지옥불 함성**: "This Skill's cooldown can be bypassed by expending an Endurance Charge"(GGPK ActiveSkills). 쿨(8초)이 **리셋되는 게 아니라** 충전을 소모해 무시한다. 막기·차단과의 상호작용은 없다.
- **요철 지대 I(Jagged Ground I)**: "Supported Skills consume 1 Endurance Charge on Use ... create Jagged Ground when consuming an Endurance Charge"(poe2db 0.5.5). **화산 균열 자체는 인내 충전과 무관하다** — 충전을 먹는 것도, 요철 지대를 만드는 것도 이 보조 젬이다. 충전이 없으면 화산 균열은 용암 균열만 남기고 요철 지대가 안 생겨 **토템이 터뜨릴 게 없다**.
충전 공급원은 마그마 장벽뿐이다: "켜져 있는 동안 막기 확률 25% increased(+25%p 아님), 8초에 걸쳐 방패에 용암을 채우고, 완전히 찬 뒤 **방패를 든 상태의 막기 1회**에 Magma Spray 발동 + 인내 충전 1"(GGPK ActiveSkills; poe2db 정신력 30, 방패 필요). 8초에 1개꼴이고 세트 1에서만 켜진다.

*요철 지대는 4초짜리 창이다(사실).* 지진 설명문: "기존 패치 위에는 못 깔고, 활성 패치가 최대치면 못 깐다", poe2db "Limit (2—4) Jagged Ground patches"(젬 레벨), "Jagged Ground duration is 4 seconds". 그래서 **깔고 → 세트 2로 넘어가 토템을 놓기까지가 4초 안**이어야 한다(Prolonged Duration I 30% more, Persistent Ground I 50% increased로 늘어난다). 충격파 토템: "Jagged Ground erupts when hit by this Slam ... **The Totem cannot create Jagged Ground**" — 토템은 터뜨리기만 하고 만들지 못한다.

| 구간 | 잡몹 | 보스 | 근거 |
|---|---|---|---|
| **10–20** | 몰려오는 강타(세트 1)로 기절 프라임 → 뼈 박살(세트 2)로 광역 → 세트 1 스킬로 방패 복귀 | 지진(세트 1)을 보스 밑 **다른 위치**에 여러 번 → 4초 안에 충격파 토템(세트 2) → 지옥불 함성 | 가이드 1–10·11–20 팁; 복귀 단계는 추정 |
| **21–30** | 위와 동일 + 공명하는 방패(실캐릭 추가분) | **① 방패 들기로 막아 충전 1 확보 → ② 화산 균열(요철 지대 I가 충전 소모 → 요철 지대) → ③ 그 위에 충격파 토템** | 가이드 21–30 팁 원문 순서. ④ 지진 추가는 11–20 팁 재사용(추정) |
| **31–41** | 위와 동일 | 지옥불 함성(격노하는 함성으로 격노 → Rageforged I이 10 격노 소모 35% more) → **대장간 망치** 투척 → 요철 지대는 **지진(세트 1)** → 충격파 토템 | 가이드 31–41 팁 + 스킬 원문 |

*대장간 망치는 **스킬 자체로는** 요철 지대를 만들지 않는다(사실). 단 요철 지대 I 을 꽂으면 만든다 — 실제로 그가 34레벨에 그렇게 했다(0.2.4).* "불타는 망치를 던져 땅에 박고, 박혀 있는 동안 다시 누르면 회수하며 쿨을 리셋한다. 또는 **박힌 망치 근처에서 함성을 쓰면 부서지며 용암 균열이 나선으로 퍼진다**"(GGPK ActiveSkills; poe2db 균열 5줄기, 망치 지속 12초, "박혀 있는 동안 쿨이 안 돈다"). 31–41 링크에 요철 지대 I이 없는 것과 일치한다. 즉 함성은 버프이자 **기폭제**다. 요철 지대는 스킬이 아니라 **보조 젬 요철 지대 I** 이 만들므로(인내 충전 1 소모), 그 보조를 어느 강타에 꽂느냐가 요철 지대의 출처를 정한다 — 가이드 31–41 링크는 대장간 망치에 안 꽂지만 **실캐릭은 34레벨에 꽂았다**(0.2.4). 인내 충전이 필요 없어지므로 그 충전은 지옥불 함성 우회로 돌아간다(가이드 "Don't need Endurance charge").

*방패 들기(사실).* "막은 직후 **적이 가까이 있을 때** 놓으면 방패 타격 — 피해와 기절"(GGPK). poe2db: 강타 기절 축적 600% more, 항상 경기절, **타워 방패면 현혹(Daze)**, 회피 불가. 조건은 "근접 타격을 막은 뒤"가 아니라 "막은 직후 + 적이 가까이"다. 반대로 **막는 피해가 너무 크면 본인이 강타 기절당한다**(같은 설명문). 0.5.0 L1652로 방패 들기는 스킬 사용/채널링으로 계산된다.

*스프린트(가이드 1–10 원문).* "구르는 **동안** 스페이스를 누르고 있으면" 직후 스프린트가 시작된다. 계속 누른 채 WASD를 놓으면 마우스 방향으로 달린다.

*지옥불 함성 lv3 고정의 유효 범위.* 가이드 "lvl 3, NEVER upgraded (마나 비용을 낮게)"는 **타락시키는 비명을 꽂기 전까지만** 참이다(0.6절). poe2db 마나 비용 lv3 = 24 / lv10 = 46 / lv20 = 85, 강화 효과는 추가 화염 피해 30%→49%. 실캐릭 24레벨도 L3이었다(0.2.2). 꽂는 순간 함성 젬 레벨이 곧 타락한 피 피해가 되어 규칙이 뒤집힌다(0.5.0 L1044) — 다만 제작자의 0.5.5 계획은 지옥불 함성이 아니라 **보강하는 함성**에 꽂는 것이다(0.4절).

*못 쓰는 것 두 가지(사실).* ① 24레벨 실캐릭은 **잿불의 예고를 못 켠다** — 정신력 30이 전부 마그마 장벽에 들어간다(4.1). 가이드 21–30이 세트 2에 배정한 것과 어긋난다. ② 실캐릭의 충격파 토템은 3소켓이라 **하위 주얼러 오브를 이미 썼다**(추정) — 31–41 팁의 "Corrupting Cry용으로 아껴라"와 충돌한다.

*골드(가이드).* 21–30에서 이미 후디드 원에게 일부 패시브를 골드로 리스펙해야 하고, 33레벨 또는 Corrupting Cry I 입수 시 트리 리스펙에도 든다 — "도박에 다 쓰지 말 것"(31–41 원문).

*미검증 1건.* "몰려오는 강타의 두 번째 슬램을 뼈 박살 등으로 취소할 수 있다"는 가이드 팁이고, 0.5.5 스킬 텍스트·GGPK에는 근거가 없다. 인게임 확인 대상.

**0.2.4 0.5.5 실캐릭 실측 — 25 → 34레벨 (2026-09-06 새벽, `scripts/track_poe2_character.py` 자동 추적)**

가이드는 [0.4]이고 2026-09-06 03:03 KST 재확인에도 **0.5·0.5.5 개정이 0줄**이다(변형 4개 전부 "(outdated)", Changelog 마지막 항목 2025-12-20). 그러니 0.5.5의 실제 답은 실캐릭뿐이다. 방송 2일차(01:27 KST 시작) 중 관측한 것:

| 시각(KST) | 레벨 | 바뀐 것 |
|---|---|---|
| 09-05 08:13 | 24 | 1일차 종료 |
| 09-06 01:43 | 25 | — |
| 09-06 02:13 | 29 | 공명하는 방패 +Armour Demolisher I · 화산 균열 +Persistent Ground I · 장화 Threaded Shoes → **Bronze Greaves**(순수 방어도) |
| 09-06 03:20 | 34 | **대장간 망치 등장(+요철 지대 I·Persistent Ground I)** · **몰려오는 강타 삭제** · 화산 균열은 보조 없이 남음 · 화염 저항 −5 → **+5** |

읽히는 것:
- **요철 지대의 출처가 화산 균열 → 대장간 망치로 옮겨갔다**(사실). 가이드 31–41 링크는 대장간 망치에 Fist of War I·Rageforged I 을 꽂지만 그는 **요철 지대 I·Persistent Ground I** 을 꽂았다 — 즉 "화산 균열 대체"가 아니라 **역할까지 통째로 이관**이다. 대장간 망치는 박아 두면 쿨이 안 돌고 함성으로 부술 수 있으므로, 요철 지대를 깔아 두는 축으로 쓰기에 화산 균열보다 유지가 낫다(추정).
- **몰려오는 강타를 버렸다**(사실). 가이드는 31–41 밴드에서도 세트 1 유지인데 뺐다. 기절 프라임 역할이 사라졌으니 루프가 바뀌었다는 뜻이다(추정 — 무엇으로 대체했는지는 다음 관측 대상).
- **세트 포인트 6/6 → 8/8**(사실). 세트 1 신규 2개는 전부 막기(Block 5% · Unstoppable Barrier 막기 10%↑/디버프 둔화 15%↓), 세트 2 신규 2개는 전부 공격 피해(Attack Damage 12% · **Crushing Verdict** 공속 −5%/기절 축적 30%↑/공격 피해 50%↑). Crushing Verdict 는 **가이드의 엔드게임 세트 2 목록에 이미 있는 노드**라, 이건 즉흥이 아니라 가이드 엔드게임 배치로의 수렴이다(사실).
- **키스톤은 34레벨까지도 0개**(사실). 선대의 유대·혈마법 둘 다 아직이다.
- 방어는 오르는 중이다: 생명력 745 → 903, 방어도 333 → 733, EHP 1,052 → 1,357, 화염 저항 −5 → +5. 문서 6.2가 지목한 "저항이 가장 약하다"를 그가 실제로 손대기 시작했다.

**0.2.4b 46레벨 전환 실측 — 계획이 실제로 켜졌다 (2026-09-06 06:34~07:44 KST 자동 관측)**

문서 0.4·0.5가 "제작자 발언, 전부 미검증"으로 적어 둔 것이 46레벨에서 실제로 켜졌다. 전부 사실(스냅샷 원본 `scratchpad/track/snapshots/lv{46,50,52}_*.json`).

| 시각(KST) | 레벨 | 사건 |
|---|---|---|
| 06:34 | 46 | **타락시키는 비명 I 을 보강하는 함성에 꽂았다** · **지옥불 함성 삭제** · 세트1 트리 전면 재편 · 무기·목걸이·장갑 교체 |
| 07:09 | 50 | 효율 I(뼈 박살)·효율 II(보강하는 함성)·Persistent Ground II(지진) 추가 |
| 07:44 | 52 | 패시브 67 · 정신력 111 |

**① 함성 링크가 그가 말한 그대로다(사실).** `보강하는 함성 + 타락시키는 비명 I + 포악함 II + Swift Affliction II + 효율 II` — 5링크. Discord 09-02 "instead of seismic and stacking strength, use fortifying"과 정확히 일치한다. 동시에 **지옥불 함성을 완전히 버렸다** — "lv3 고정, 절대 안 올린다"던 그 젬이 사라졌다. 0.6절의 "lv3 고정은 타락시키는 비명을 꽂기 전까지만"이 실측으로 확인됐다.

**② 2차 전직 = 전쟁 소집자의 고함(Warcaller's Bellow)**(사실, 트리 노드 `AscendancyWarrior2Notable4_`, "Ignore Warcry Cooldowns / Warcries Explode Corpses 25%"). 0.4.1절이 **1순위 확인 대상**으로 지목한 노드다. 이로써 보강하는 함성의 쿨다운 8초 문제가 인내 충전이 아니라 **전직으로** 해결됐다 — 즉 0.4.1이 예상한 "선대의 유대가 충전을 풀어 함성 쿨 우회로 보낸다"는 경로는 **불필요해졌다**. 전직 4점 = 응답받은 부름 + 전쟁 소집자의 고함 + 소노드(함성 속도 20%, 토템 생명력 20%).

**③ 세트 1 트리를 통째로 갈아엎었다(사실).** 44레벨까지의 "방패 + 요철 지대"가 46에서 "함성"으로 바뀌었다.

| | 세트 1 (16) | 세트 2 (16) |
|---|---|---|
| Lv44 | Spike Pit·Perforation·Jagged Ground Effect ×2·Bleed Chance·Block ×2·Unstoppable Barrier·Shield Block ×2·Shield Damage·Lay Siege | 토템 계열 12 |
| **Lv52** | **Bolstering Yell·Cacophony·Urgent Call·Warcry Damage ×2·Warcry Speed ×2·Warcry Cooldown Speed·Warcry Cooldown and Speed·Warcry Power Counted**·Empowered Attack Damage ×2·Shield Block ×2·Shield Damage·Lay Siege | 토템 계열 16(+Watchtowers·Totem Placement Speed ×4) |

요철 지대·막기 노드가 전부 빠졌다. 소스팩의 제작자 발언 "We have Warcry passives on set 1, while having totem passives on set 2"(엔드게임 배치)로 **수렴 완료**다.

**④ 막기가 0으로 읽힌다(사실 — 해석은 불확실).** 40 → 0. 세트1에서 막기 확률 노드(Block ×2·Unstoppable Barrier)를 리스펙으로 뺀 것은 확실하다(패시브 57 → 55). 다만 **Stone Tower Shield 를 여전히 착용 중이고 Shield Block 노드 2개도 남아 있다** — 0 이 실제 값인지, 활성 무기 세트 기준 계산 아티팩트인지는 미확인. 6.1 방어층 표의 "50%로 굴린다"는 전제가 흔들릴 수 있어 다음 관측 대상이다.

**⑤ 선대의 유대는 52레벨까지도 안 찍었다(사실).** 키스톤 0개. 혈마법도 없다. 0.5절이 그의 최종 형태로 적은 두 축(선대의 유대 + 혈마법)이 52레벨 시점에 **아직 하나도 안 들어왔다**. 대신 정신력을 30 → 111로 올려 마그마 장벽에 **활력 I + 명료함 II**를 얹었다 — 선대의 유대(토템당 정신력 75 예약)와 정면으로 경쟁하는 지출이다(추정).

**⑥ 세트 2 무기가 생겼다(사실).** 슬롯 15에 **Morning Star**(한손 철퇴, 레어). 가이드가 요구하던 양손 철퇴가 아니라 한손이다. 세트1 무기는 Brigand Mace. 장비도 대거 교체: 목걸이 Jade → **Solar Amulet**, 갑옷 Maraketh Cuirass → **Vaal Cuirass**, 장갑 → Detailed Mitts, 방패 → Stone Tower Shield.

**0.2.5 0.5.5에서 이 레벨링에 걸리는 변경(사실, 3장)** — Rolling Slam 첫 강타 피해 하향(0.5.0 L992), Boneshatter 퀄리티 공속 하향(L932), Brink I이 1레벨부터 컷(L1040), 화산 균열 상향(0.4.0 L713), Impact Shockwave가 진짜 여진(0.4.0 L487), 지진 여진 상향(0.5.0 L940), 마그마 장벽 6–8 → 5–7(L970). 루프 자체를 바꾸는 변경은 없다.

**0.2.6 교차 확인 — POEGuy의 워브링어 토템 레벨링(사실; 페이지는 0.5.0 태그·09-03 갱신, 0.5.5 표기는 그의 영상)** 〔https://www.poe-vault.com/poe2/warrior/warbringer/totems-leveling-build, 2026-09-03 갱신〕 1막은 양손 철퇴로 Rolling Slam → Boneshatter, "Once you reach Level 6, you will want to pick Shockwave Totem"(초반엔 어그로용; POEGuy 표기 6, GGPK 요구 레벨 7), 단일 대상 Mace Strike(Rage + Rapid Attacks I), 첫 정신력 젬은 Herald of Ash, 지진으로 요철 지대 추가; 2막부터 "Drop Shockwave Totem. Spam Volcanic Fissure.", "Drop Herald of Ash and use Magma Barrier", 화산 균열 전환 뒤 한손 철퇴 + 방패; 전직 "Take your first Ascendancy around level 22 in Act 2 (When you swap to Volcanic Fissure)" = **응답받은 부름**, 이어서 **나무 벽**("Complete the Trial of Chaos towards the end of Act 3"); "Around Level 52, right after defeating Act 4 Tavakai" 석궁 유탄 발리스타로 전환 〔`scratchpad/poevault_leveling.txt` 원문 대조〕. 겹치는 구간은 **1막~2막 초입**(Rolling Slam → Boneshatter, 충격파 토템, Herald of Ash, 1차 전직 응답받은 부름)까지다. 2막부터 POEGuy는 충격파 토템을 버리고 화산 균열 스팸 + **혈마법 키스톤**("Try to avoid + to Melee Skills on your weapon, gloves, and amulet in Act 2, since they will drain your life pretty quickly with the Blood Magic keystone allocated!"), 세트 스왑 없음이고, Skadoosh는 충격파 토템을 우선 레벨업하고 11레벨부터 2세트, 31레벨에 대장간 망치, 24레벨 실캐릭 키스톤 0이다(사실). 갈리는 지점은 52+가 아니라 **2막**이고, 52+에서 토템 종류(POEGuy = 유탄 발리스타·함성 없음 / Skadoosh = AWT + 함성)로 다시 갈린다. Skadoosh: "He did warbringer mortars / I'll be using ancestral warriors"(Discord 09-03 19:48).

### 0.3 전직 순서

| 차수 | 노드 | 라벨 | 근거 |
|---|---|---|---|
| 1차(2막 Sekhemas) | **Totem Life → 응답받은 부름(Answered Call)** — 토템 +1, 토템 소환 시 선대의 혼백 | **사실**(24레벨 스냅샷) | 4.3. 0.4 가이드의 "첫 전직 = Warcaller's Bellow"(E:82–84)와 다르다 |
| 2차 이후 | **전쟁 소집자의 고함(Warcaller's Bellow)**("Ignore Warcry Cooldowns / Warcries Explode Corpses 25%")은 함성 스팸 루프의 유일한 쿨다운 해제 수단이라 반드시 들어간다. 나머지 둘은 0.4 Endgame 세트(나무 벽 · 비취의 전승) | **추정**(순서 미확인) | 2장 3항, 5.3 트리. 다음 스냅샷의 노드 39411 형제로 확정(8.2 S1) |
| 시련 메모 | 0.5.0: 룬 수호 최대치가 Sekhemas 시작 Honour에 가산, 입구에 Reforging Bench(L532/L712). 0.5.5: Trial of Chaos는 중도 이탈·재개 가능, 방마다 보상 상자, 보상은 화폐 + 소울 코어만(L73/L77/L79) | 사실 | 3.3·3.5 |

### 0.4 33 → 46레벨 — 함성으로 전환

- **가이드(0.4)**: 33레벨 또는 Corrupting Cry I(등급 3 보조 젬) 입수 시 리스펙. Leveling 변형 = 세트1 **지옥불 함성(lv3) → Corrupting Cry I · Swift Affliction I · Brutality I**, 지진 → Encroaching Ground · Persistent Ground I; 세트2 충격파 토템 → Brutality I · Overabundance I, 대장간 망치 → Fist of War I · Elemental Armament I; Overwhelming Presence; 마그마 장벽(5.1, 사실).
- **그의 0.5.5 계획(제작자 발언)**: 지진 함성이 아니라 **보강하는 함성(Fortifying Cry)**에 Corrupting Cry I을 꽂고, **근접 스킬 레벨**을 다시 쌓는다("use fortifying and get melee levels again"). 보강하는 함성은 GGPK 요구 레벨 **32**, 태그 "Attack, AoE, Melee, Trigger, Physical, Duration, Nova", **"Requires: Armoured Shield"**(사실) — 세트1 = 한손 철퇴 + 방어구형 방패가 전제다. 젬링 포크와 같은 엔진이므로 그 세팅은 레포 `Docs/2026-09-02_SKADOOSH_CORRUPTING_WINGS_GEMLING_0_5_5_GUIDE_DOC.html` 2장이 참고가 된다(단 파콰테의 맹약은 레벨 65 라인리지 보조이고, 워브링어에 쓸지는 발언 없음 — 8.2 S6).
- **레벨 규칙이 뒤집힌다(사실, 결론 6)**: 타락한 함성 피해 = 소켓된 함성 젬 레벨(lv3 12.5/s · lv10 60.3/s · lv20 287/s). Corrupting Cry I을 꽂는 순간부터 **그 함성은 최대한 올린다**. "지옥불 함성 lv3 고정"은 타락시키는 비명을 꽂기 전(레벨링 단계)에만 맞는 말이다. 함성 비용은 lv1 19 → lv20 85 마나(혈마법이면 생명력) — 가이드가 Efficiency II를 Starter·Endgame·Uber 3개 변형에 두는 이유(6.2; Leveling 변형엔 없음).
- **지진 함성(Seismic Cry)**은 GGPK 요구 레벨 **42**라 4막 이후 이야기이고(0.4 Starter 변형), 그의 계획엔 없다. Corrupting Cry II(등급 5 보조, AoE 페널티 없음)는 나중이다.
- 장비(그의 말): "You don't need perfect jewels… Just warcry damage and global phys can go a long way. And you can craft global phys"(Discord 09-03 19:21, 젬링 문의에 답한 것 — 추정: 피해 엔진이 같다). 한손 철퇴 "+X to Level of all Melee Skills"는 0.5.0부터 T1 상한 +4(양손 +5)(L1202/L1206, 사실).
- **HC 규칙**: Titanrot Cataphract는 "You have no Life Regeneration" — 회복원 없이 입지 말 것(가이드 S:48–50, 6.2).

**0.4.1 46+ 계획을 0.5.5 스킬 원문과 대조한 결과(2026-09-06 재분석, 항목별 적대검증 통과)**

그가 말한 계획의 부품들을 1차 텍스트로 확인했다. 세 개가 계획의 해석을 바꾼다.

- **선대의 전사 토템에는 애초에 Limit 이 없다** → 선대의 유대의 "토템 한계 2배"는 **AWT 에는 무효**다(다른 토템 스킬에는 적용). 0.3.0 "Ancestral Warrior Totem: Now have no Limit … Now requires consuming 3 Endurance Charges to Raise", 0.3.1 "unable to have more than 10 … active at once"(하드 상한). 따라서 이 빌드에서 선대의 유대의 실효는 **인내 충전 3개 면제 ↔ 정신력 75 영구 예약** 이 거래 하나다. 이득 여부는 인내 충전 재생 속도로만 갈린다(그의 현재 최대 충전도 3).
- **보강하는 함성은 쿨다운 8초 + "방어도가 있는 방패" 요구**이고, 쿨다운은 **인내 충전을 소모해** 건너뛴다(GGPK ActiveSkills `fortifying_cry` 로 교차확인; 8초 값은 poe2db 단일 출처 — 추출본에 쿨다운 필드가 없다). 그래서 **두 키스톤이 짝이다**: 선대의 유대가 AWT 에서 인내 충전을 풀어 주면 그 충전이 함성 쿨 우회로 간다. 전직에서 **전쟁 소집자의 고함**(함성 쿨 무시)을 안 찍으면 함성이 8초에 한 번이 되므로, 그의 전직 선택에서 1순위 확인 대상이다.
- **가호(Guard)** 는 히트 피해를 생명력·에너지 보호막보다 먼저 흡수하는 버퍼이고 젬 레벨로 큰다. 다만 하나만 유지되며 **위세가 낮을 때의 재시전은 기존 가호를 대체하지 못한다**(더 큰 쪽이 남는다). 젬 20 + 위세 20 에서도 368 이라 후반 생명력 대비 비중은 작다(추정) — 6.1 표에서 **보조 버퍼이지 주력 방어층이 아니다**.
- **타락시키는 비명 I 은 무연마 보조 젬 3등급(드롭 33), II 는 5등급(드롭 55)**. 타락한 함성 피해표는 **I 과 II 가 40행 전부 동일**하고, II 의 유일한 차이는 I 에 붙은 "함성 범위 30% 감소" 페널티가 없다는 것뿐이다. 즉 **55레벨 전에 II 를 노리는 건 낭비**다. (그가 "45레벨 플러스쯤부터 쓴다"고 한 것과 드롭 33 은 어긋나지 않는다 — 33 은 젬이 나오는 레벨이고 45 는 그가 쓸 만하다고 본 시점이다.)

### 0.5 46+ · 맵 — 그가 말한 최종 형태(제작자 발언, 미검증)

| 축 | 계획 | 데이터(사실) |
|---|---|---|
| 세트2 토템 | **AWT + 지면 분쇄** (+ 0.4 Uber 소켓: Branching Fissures II · Urgent Totems III · Rage III), **선대의 유대** 키스톤으로 인내 충전 3개 요구 삭제 | AWT 요구 레벨 **53**, "Consume 3 Endurance Charges", 최대 10, "every 150% of socketed Attack time", 지속 8초. 선대의 유대 = "Your Totem Limit is doubled / No Charge requirement for placing Totems / **Totems reserve 75 Spirit each**"(0.5.0 L790) → 토템 수 × 75 정신력이 관문. 정신력 확보 경로는 그의 발언에 없다(미확인) |
| 세트1 함성 | 보강하는 함성 + Corrupting Cry(II) (+ 0.4 Endgame 소켓: Brutality II · Swift Affliction II · Efficiency II) — "corrupting cry to detonate Earthshatter spikes, and apply corrupted blood/crit weakness, regen hp" | 지면 분쇄 "Warcries performed near the spike will cause it to shatter"(사실). 재생 = 다급한 부름 "Recover 2% of maximum Life and Mana when you use a Warcry"(사실). 0.5.4b "Recover X% … when you use a Warcry" 수정의 대상은 다급한 부름이 아니라 Vorana's Carnage 접미로 보인다(8.1 Q10). "crit weakness" = **Howling Beast** "Warcries inflict 3 Critical Weakness on Enemies"(제작자 발언 0.0절 4:40:38 + poe2db) |
| 루프 | "At endgame it will be 2 [buttons]. Totem for rares, and corrupting cry to detonate" — 0.5.5 L389 이후 세트2 스킬을 누르면 **스왑이 실제로 일어나** 그 동안 방패가 없다(사실) | 6.2 "스왑 중 무방비" |
| 무기 소켓 | (발언 없음) 0.5.5 신규 소울 코어 **Rallying**(+1 함성 젬 레벨) / **Automation**(+1 토템 젬 레벨) / **Quaking**(+1 강타)이 같은 소켓을 두고 경쟁, 각 레벨 50 요구(poe2db), 출처 Trial of Chaos | 3.5(사실) |
| 전직 4개 | (발언 없음) 0.4 Endgame = 응답받은 부름 · 전쟁 소집자의 고함 · 비취의 전승 · 나무 벽 | 5.3(추정) |

### 0.6 하지 말 것 — 0.4 가이드의 낡은 규칙(사실, 3·5장)

1. "Keep Seismic Cry at lvl 11" / "Infernal Cry lvl 3 NEVER upgraded" — 타락시키는 비명을 꽂은 함성엔 정반대(0.4).
2. Second Wind III로 함성 회복 — 쿨다운 무시 함성엔 발동 조건이 없고 0.4.0에 1%로 반감(결론 8).
3. Uber 변형(Hateforge + Guatelitzi ×2) — 0.4.0(12-09)에 사망(결론 8).
4. 세트2 보조젬·오라 스냅샷, 스왑 없이 세트2 스킬 — 0.5.5 L389/L393로 종료. **G 메뉴 세트 배정 필수**.
5. 힘 스택으로 딜 — 0.5.0부터 힘은 타락한 피의 기본 입력이 아니다(결론 4). 힘은 생명력·요구치·선대의 혼백용.
6. 가이드 트리 export를 그대로 임포트 — 그가 "Guide is outdated"라고 했고, 실캐릭 트리(4.3)가 다르다.

### 0.7 그를 계속 따라가는 법

- **캐릭터**: https://poe.ninja/poe2/builds/forbiddenriteshc/character/ITheCon-2183/SkadooshShoutedHard — 하루 한 번 보면 젬·트리·장비가 그대로 보인다. 원본 JSON: `curl -A "Mozilla/5.0" "https://poe.ninja/poe2/api/builds/0615-20260905-10145/character?account=ITheCon-2183&name=SkadooshShoutedHard&overview=hc-forbidden-rites&timeMachine="` (스냅샷 id는 바뀔 수 있다). 09-05 13:28·14:17·18:06(KST) 재조회 모두 같은 24레벨 스냅샷(updatedUtc 23:16Z)이었고, ninja 자체 lastCheckedUtc 08:03Z(17:03 KST)에도 24레벨(사실) — 그가 로그아웃 상태거나 ninja 수집 주기 밖이면 페이지도 낡은 값을 보여 준다.
- **볼 것**(8.2): Corrupting Cry I을 어느 함성에 꽂는가(보강하는 함성?) · 세트2 양손 철퇴 · 2차 전직 노드 · 선대의 유대 · 53레벨 AWT · 무기 소울 코어.
- **가이드**: https://mobalytics.gg/poe-2/builds/corrupting-cry-warbringer-skadoosh — 태그가 [0.5.5]로 바뀌거나 Changelog에 0.5 항목이 붙으면 그때가 그의 "검증 끝". 그는 "play the character first before I make a guide out of it"(Discord 09-02 01:25).
- **디스코드** Skadoosh's Hideout #build-help(데스크톱 앱, 로그인됨) · **트위치** VOD v2865212551(1일차 4h42m) 및 이후 방송. 방송 제목 "!Build"는 채팅 명령이라 밖에서 안 보인다.

### 0.8 HC 체크리스트 (6장 요약)

- 저항을 먼저 채운다 — 24레벨 실캐릭의 가장 약한 지표(−5/12/4/11). 2막부터 룬 소켓 저항.
- 기본 막기 상한 50%(거북이 호신부 없으면), 마그마 장벽 +25% 증가. 0.5.2부터 Siora 사이클론은 못 막는다.
- 룬 수호를 방어구에 붙이는 **Verisium Anvil**이 0.5.5에선 4막 Runeseeker 퀘스트로 해금(L219; 룬 수호 자체는 0.5.0 L81/L83) — 캠페인 중엔 방어구 룬 수호가 없다(Svalinn +50–100 제외). 55레벨 미만 방어구는 무손실.
- 탈출: 0.5.1부터 로그아웃해도 강타 기절 유지, 0.5.4b부터 피격 중 포탈 불가.
- 0.5.5 캠페인은 **전 지역 Ritual + 막당 2회 보스 웨이브**(L33/L35). "Lost-men Zealots could be invulnerable when revived in ritual"은 오늘 핫픽스 4(4001331 L11)에서야 수정됐다.
- 1막 Burning Dead 피해 일부가 화염(0.5.0 L1358 "a portion of their damage as Fire") — 화염 저항 0인 초반 워리어에 해당.
- 함성 비용은 혈마법이면 생명력(lv20 85). Titanrot Cataphract 금지(재생 0).
- 세트2 스킬을 누르는 순간 스왑되어 방패가 사라진다(0.5.5 L389). 보스 앞에서 토템을 깔 때만.

### 0.9 설치본 — 인게임 플래너 5개 + 필터 3단계 (2026-09-05 설치)

**빌드 플래너** — 게임 폴더 `문서/My Games/Path of Exile 2/BuildPlanner/`, 정본 `build_planner/`.

**막 경계(GGPK `WorldAreas` 실측 — 마을·은신처·맵·디버그 지역 제외).** 레벨이 아니라 막으로 부른다: 인게임에서 사람이 아는 좌표가 막이다.

| 막 | 레벨 | 첫 지역 |
|---|---|---|
| 1막 | 1~15 | The Riverbank |
| 2막 | 16~31 | Vastiri Outskirts |
| 3막 | 33~45 | Sandswept Marsh |
| 4막 | 46~53 | Abandoned Prison |
| 잔혹 | 54~ | Ashen Forest |

가이드가 "3막 첫 지역 Sandswept Marsh"라고 쓴 것과 GGPK 의 Act 3 최저 레벨 33 이 일치하고, POEGuy 의 "Around Level 52, right after defeating Act 4 Tavakai"와 4막 상단 53 이 일치한다. **그가 타락시키는 비명으로 갈아탄 46레벨은 정확히 4막 진입 지점이다**(0.2.4b) — 임의의 레벨이 아니라 막 경계에 맞춘 전환이다.

| 파일 | 출처 | 쓰는 구간 |
|---|---|---|
| WB 가이드 Act1 | Mobalytics 원본 Lv1-10 | 1막 |
| WB 가이드 Act1말-Act2 | 원본 Lv11-20 | 1막 후반~2막 |
| WB 가이드 Act2 | 원본 Lv21-30 | 2막 |
| WB 가이드 Act3 | 원본 Lv31-41 | 3막 (가이드는 여기서 끝) |
| WB 실캐릭 Act3 | ninja `pathOfBuildingExport` Lv34 | 3막 — 21+ 는 실캐릭이 정본 |
| WB 실캐릭 Act4 | 동 Lv46 (타락시키는 비명 전환 직후) | 4막 |
| **WB 실캐릭 현재** | 추적기가 자동 갱신 | 지금 그가 있는 곳 |

`scripts/track_poe2_character.py` 가 막 진입(16·33·46·54·65)마다 `WB 실캐릭 <막> - Skadoosh` 보존본을 만들고, `WB 실캐릭 현재` 를 매 변화마다 덮어쓴다.

검증: 패시브 id 전부 tree.json stringId, 젬 경로 전부 GGPK 표와 일치(`scripts/import_poe2_planner_files.py`, pytest 8건). 인게임 로드 확인(2026-09-05, 사용자 — ninja export 정규화본 포함).

**ninja Build Planner 대화상자보다 `pathOfBuildingExport` 가 낫다(2026-09-06 확인).** 대화상자 export 는 `inventory_slots` 가 비어 있지만, 같은 API 응답의 `pathOfBuildingExport` 는 장비까지 실린 PoB XML 이라 레포 생성기로 13슬롯을 그대로 옮긴다. 디코드는 **base64url**(`-`/`_` → `+`/`/`) + zlib — 표준 base64 로 풀면 `invalid bit length repeat` 로 죽는다.

**방송 PoB 화면으로는 트리를 복원할 수 없다(한계).** 1일차 VOD 프레임은 트리 스펙 이름·레벨·점수(Default 96~97렙 118~120점 / Act 1 18렙 21점 / Act 2 22렙 25점 / Act 3 49렙 60점)와 호버된 노드 2개(Vigilance · Reverberating Impact)까지만 읽힌다. 어느 노드를 찍었는지는 픽셀에서 못 뽑는다 — 그의 96레벨 **계획** 트리는 그가 공개하기 전까지 미확보이고, 플래너에 담긴 것은 **실캐릭 현재 트리**다.

**필터** — 게임 루트에 3파일. NeverSink 0.10.3 위 Show-only 오버레이(Crimson 3축 문법, 젬링 필터와 같은 팔레트). 스펙 `data/filter_build_targets/poe2_warbringer_skadoosh_0_5_5_hc.json`(생성기 `scripts/make_hc_warbringer_spec.py`가 플래너 정본 + GGPK 에서 유도).

- `PathcraftAI_HC-Warbringer_1-Campaign_on_NeverSink-SOFT` 1~45 · `2-EarlyMaps_on_NeverSink-REGULAR` 46~64(Corrupting Cry·AWT 53·혈마법) · `3-Endgame_on_NeverSink-STRICT` 65+.
- 룰 19 · 베이스 193(GGPK 실재 190 + 0.5.5 패치노트 이름 3) · 스윕 3단계 REAL 회귀 0 · HIDDEN 0 · 무음에 소리 추가 0. 숨김은 못 쓰는 무기 클래스(활·석궁·육척봉·화살통·창·지팡이·부적·완드·버클러·포커스) 한 룰뿐 — 셉터는 정신력 확보 경로가 미확인(0.5절)이라 숨기지 않는다. 적대검증 2건(스펙 7항목·플래너 6항목) 반영: 플래너는 정본 형태(서포트마다 `level_interval`, 빈 `support_skills` 없음)로 재생성해 원본과 deep-equal, 스펙 주석의 발언 날짜·혈마법 시점 표기를 정정.
- 띄우는 것: 가이드·실캐릭 착용 철퇴/타워 방패/힘 방어구를 밴드별로, 45+ 철퇴·65+ 방어구는 레어만(제작자 "레어 장비만") · 장신구·저항 반지 · 호신부·생명력 플라스크 진행 · 루비 주얼 · 주얼러 오브 · 육체/상급 룬 · **0.5.5 소울 코어 Rallying/Automation/Quaking + Vorana's Carnage**.
- 한계(사실): 미가공 젬은 GemLevel 조건이 빌더에 없어 NeverSink 티어 그대로 — 함성 젬 레벨이 곧 피해라 미가공 스킬 젬 9(32)·11(42)·13(53)은 직접 챙길 것 · 신규 소울 코어 3종은 9/4 GGPK 추출본에 없어 패치노트 원문 이름으로 넣었다(인게임 표기가 다르면 그 룰만 조용히 무반응, GGPK 재추출 후 재확인) · 유니크(Bronzebeard·Surefooted Sigil)는 베이스 룰로만 잡힌다.
- 재생성: `python scripts/make_hc_warbringer_spec.py` → `python scripts/build_poe2_build_overlay.py --base data/filter_sources/neversink_poe2_soft.filter --spec <스펙> --out filters/<파일> --stage campaign --allow-drops`(maps/endgame 동일) → `python scripts/poe2_filter_sweep.py --spec <스펙>`.

---

## 1. 빌드 정체와 계보

| 시기 | 버전 | 소스 | 전직·스킬 핵심 | 무엇이 바뀌었나 |
|---|---|---|---|---|
| 2024-12 ~ 2025-03 | 0.1 | 영상 KsK6tNjh50s(엔드게임 개요 33:55), gWQNu6xddow(우버 29:20), Q1rQ7gdvTco(12월 초기 쇼케이스), 포럼 3732489(2025-03-06, "Totem weapon swap, 88% block chance, Perma stun all content") | 세트1 지진 함성(Corrupting Cry + Brutality + Swift Affliction + Inspiration) 스팸, 지옥불 함성(Raging Cry / Dazing Cry / Mobility)은 보스용; 세트2 **거인의 피(Giant's Blood)**로 양손 철퇴 2자루(+7 melee ×2 = "+14 total") + AWT + **지면 분쇄(Earthshatter)** + Upheaval; **스발린(Svalinn)** 럭키 막기(상한 64% "I have 64% chance" KsK [5:20] ~ 68% "can go up to 68%" gWQ [21:45] → 실효 "87.5% or maybe 87" KsK [5:20] · "to about 87%" [27:02] · "we block basically 90% of hits" gWQ [14:04]; 포럼 3732489 제목은 88%); **렌리의 훈련(Renly's Training)** + 거북이 호신부; 혈마법; 셉터 + Blasphemy(자막 "the curse of selectors feeble" KsK [15:36] — Enfeeble은 자막 훼손, 문맥 추정) | 원형. "swap totem swap back that's kind of our gamep[lay]" https://youtu.be/KsK6tNjh50s?t=1337 [22:17–22:20]. 쿨다운 무시는 영상에서 이름이 안 나온다. 당시엔 두 함성 노드(Warcaller's Bellow + Greatwolf's Howl)에 나뉘어 있었다(추정, GGPK 0.5에 Greatwolf's Howl이 [DNT-UNUSED]로 남아 stat 19721 공유) |
| 2025-04 | 0.2 | 가이드 0.2.0 노트(E:602–630), mas0ny1 업데이트 영상 RR4yjWrZrLU(제작자 커뮤니티 탭에서 추천), Maxroll Cptn Garbage 가이드(2025-04-04 최종) | 골격 동일 | Turtle Charm "25% less block (was 35%)", "Warcaller's Bellow scales with warcry stats now", "Seismic Cry lost up to 38% warcry speed", Brutality 25%/Swift Affliction 30%로 너프, Against the Darkness·Morior Invictus·Overcharge 사용 불가 판정(모두 제작자 노트) |
| 2025-08 ~ 09 | 0.3 | BLc0SguI0gk(개요 27:53), B8yBMkd-jsE(Day 1, 13:19), 포럼 BOTW 3848472(2025-09-09) | 두 함성 노드 통합 → 1차 전직만으로 타락시키는 비명 가동; AWT가 장비 무기 사용·제한 없음(0.3.1에 10개 상한)·인내 충전 3개 소모; 기본 막기 상한 50%; 스왑 즉시; 스타터/엔드게임은 AWT 대신 **충격파 토템 + 지진 요철 지대 + 대장간 망치**; 보강하는 함성 신설; 전직 = Warcaller's Bellow / Answered Call / Jade Heritage / Wooden Wall(렌리 탈락) | "We now use shockwave totems instead of [Ancestral Warriors] from last league" https://youtu.be/BLc0SguI0gk?t=70 [1:10]. Second Wind III 회복 "It's insanely OP. Definitely. It's not bugged. It's definitely not bugged" https://youtu.be/BLc0SguI0gk?t=513 [8:33–8:36](단락 시작은 [7:37]) → 0.3.1 노트 "Second Wind III no longer works with no cd warcrys"(E:684–685). Day 1엔 AWT를 "endurance charge generation is very difficult, especially without hate forge. So that's kind of tabled" https://youtu.be/B8yBMkd-jsE?t=46 [0:46–0:57]; 별도로 스왑 시 토템이 자기 삭제되는 버그 "if you weapon swap it swaps to your other set … it will delete itself … completely useless in our build" https://youtu.be/B8yBMkd-jsE?t=379 [6:19–6:43] |
| 2025-09-13 | 0.3 "Corrupting Army" | F6ou4sj0uZE(21:17), 우버 아비터 QTbO63lB1Sw | **Hateforge(증오의 탄생)**(최대 격노 시 충전 3개) + **격노하는 함성(Raging Cry)** + **포효하는 함성(Roaring Cries)**(From Nothing 주얼) + Redblade Banner(한국어명 미확인) + Guatelitzi 코어 2개 → AWT 연속 소환, 최대 10 | Uber Endgame 변형의 원형. 힘 800, 생명력 3,800 [3:25–3:46]; "We are still a corrupting cry build at heart, so we need to stack as much strength as possible" https://youtu.be/F6ou4sj0uZE?t=189 [3:09] |
| 2025-12 | 0.4 | CoskGFogxhA(업로드 2025-12-07, yt-dlp `uploadDate` — `extracts/subs_plans.md` L23; 7:21–12:03), 가이드 Changelog(05.12 / 09.12 / 20.12.2025) | 핵심 변경 없음. AWT 25% less AS 삭제 "about a 33% DPS buff" https://youtu.be/CoskGFogxhA?t=521 [8:41]; Constricting Command 포위 ≥1 | 12-09 Hateforge 너프로 Uber 사망. 그의 0.4 스타터는 Balrog(Bear Smith of Kitava)였다(VID-A [12:05]~). 이 빌드는 스타터가 아니었다 |
| 2026-05-25 | 0.5 판정 | Jj2eKr4Ez-A 13:06–15:38 | — | "I wouldn't recommend it honestly in the 3.5 [sic, 자막; 문맥상 0.5]" [13:50–13:53]; 젬링 아이디어 "considering it scales with levels. I'm guessing that gemling might be really good" https://youtu.be/Jj2eKr4Ez-A?t=925 [15:25]. 0.5 스타터 계획은 "probably … whirling assault most likely stun titan" [23:49](제작자 발언); 실제 0.5 스타터는 Discord 09-02 01:12 "Concussive was my league starter"(제작자 발언; 06-06 개요 영상 "Concussed Titan Ward Stacker") |
| 2026-06-09 ~ | 0.5 젬링 분기 | 가이드 "[0.5.5] Corrupting Wings"(changelog 시작 09.06.2026), 영상 a6sdEzBCrCY(06-14), JUFV_TaRXrM(06-21 탱크 업데이트) | 젬링 + 보강하는 함성 + 파콰테의 맹약, 근접 스킬 레벨 스택, 이후 스발린 86%+ 실효 막기 | 워브링어 가이드 헤더에 젬링 링크가 붙었다. 상세는 레포 `Docs/2026-09-02_SKADOOSH_CORRUPTING_WINGS_GEMLING_0_5_5_GUIDE_DOC.html` |
| 2026-09-05 | 0.5.5 HC 복귀 | Twitch v2865212551 "0.5.5 Launch! HC OG Warbringer Warcry Totems !Build Come and ask your questions!"(2026-09-04T18:30:05Z 시작 = 런칭 1.5h 전, 4h42m33s), poe.ninja `SkadooshShoutedHard` | 4장 | 직전 5개 VOD는 전부 Pathfinder(마지막 07-14) → 이어하기가 아닌 새 시작(사실). 복귀 이유·계획은 Discord #build-help(09-02, 09-03)와 방송 VOD 전사(0.0절)에 있다(결론 5): "leaguestart able version of corrupting cry / doesn't require any uniques", "my classic build with new coat of paint", 보강하는 함성 + 근접 레벨 + AWT + 선대의 유대(제작자 발언, "전부 미검증"). Discord #clips-and-highlights 09-05 01:30 KST "Starting stream, 0.5.5 launch! HC OG Warbringer Warcry Totems" |

하드코어 신호(사실): 7개 자막 파일에서 "hardcore"는 2회(BLc0SguI0gk [27:40] "maybe even hardcore at [skadoosh_c]", F6ou4sj0uZE [21:06] "who knows something else hardcore maybe") — 둘 다 "다음엔 하코 스트림을 할지도"라는 예고이고 이 빌드의 HC 적합성 발언은 아니다. "HC"/"SSF" 토큰은 0회. 그 밖의 HC 신호는 가이드의 `HC` 태그, 레벨링 가이드의 `HC`/`SSF` 태그, 오늘 스트림 제목, 그리고 Discord(09-02 01:29 "i'll be playing HC at least at teh start"; 09-03 19:40 "Current plan is hardcore trade, warbringer totem shouter"; 09-02 01:15 사망 시 리롤 질문에 "Yeah, I doubt I'd reroll in HC")다. 0.1 포럼 글에는 "Hardcore viable"이 있다(포럼 3732489).

---

## 2. 작동 원리 — 0.4 가이드 기준

가이드 "How it Works"(E:521–600)의 순서를 따르고, 각 항목에 0.5.5 현재 게임 데이터를 붙였다.

1. **타락한 피 적용.** 가이드: "Every time a warcry that is supported by Corrupting Cry affects and enemy, it apply's one stack of corrupted blood." / "Corrupted blood does 25% of our total strength as physical damage per second for 5 seconds. Corrupted blood can stack to a max of 10 on one enemy, meaning a total 250% of strength per second. Each additional stack refreshes all previous stacks."(E:523–533, 0.5 이전 서술). 0.5.5 사실: 지원 젬 문구는 "Supported Skills Trigger Corrupted Cry for each enemy in range"(https://poe2db.tw/us/Corrupting_Cry_I), 스택당 피해는 젬 레벨 표(결론 4), 최대 10 디버프, 5초. 갱신 규칙은 poe2db·패치노트 어디에도 없다(미확인). 타락시키는 비명 I은 "Supported Warcries have 30% less Area of Effect"(등급 3), II는 페널티 없음(등급 5). 트리거당 스택 수는 명시 없음 — 파콰테의 맹약의 **뒤틀린 맹약(Twisted Pact)**만 "Inflicts 5 Corrupted Blood Debuffs"라고 적혀 있어 1개로 추정.
2. **출혈이 아니다.** 가이드 "it is NOT bleed"(E:533) = poe2db "Corrupted Blood is not Bleeding and is not affected by any stats related to Bleeding"(https://poe2db.tw/us/Corrupted_Blood). 사실 일치.
3. **쿨다운과 전직.** 가이드: "Seismic Cry and Infernal Cry have a base cooldown of 8 seconds. … That's where our ascendancy comes in with Warcaller's Bellow, as it allows us to ignore the cooldown entirely."(E:535–542). 사실: 지진 함성 "Cooldown Time: 8.00 s / Use Time: 0.80 sec / Cost: (19—85) Mana", 지옥불 함성 동일, 두 함성 다 "This Skill's cooldown can be bypassed by expending an Endurance Charge"(0.3.0부터). Warcaller's Bellow는 "Ignore Warcry Cooldowns"(GGPK 0.5 Stat2Value 1). 워브링어에겐 인내 충전 우회가 무의미하다(추정).
4. **왜 지진 함성인가.** 가이드: "Lower cost, stuns enemies, does damage, knocks back and eventually breaks armour via Shattering Blow."(E:544–552). 사실: 0.3.0부터 "Heavy Stunning enemies that are Primed for Stun", "Knocks Back Enemies", 반경 4m, 물리 피해 (7—223)~(10—335). **격파의 일격(Shattering Blow)** = "Break 50% of Armour on Heavy Stunning an Enemy". 제작자 발언(0.3): 지진 함성 레벨은 "doesn't really have much of an impact … reduce the level to 11" https://youtu.be/BLc0SguI0gk?t=372 [6:12] — 0.5에선 결론 6대로 역전.
5. **마나 → 생명력.** 가이드: "we get Urgent Call and Blood Magic on the passive tree. As well as the new (unintended?) interaction with Second Wind III … Due to strength inherently giving 2 life per point, it means the relative life cost stays manageable"(E:554–562). 사실: **다급한 부름(Urgent Call)** "Recover 2% of maximum Life and Mana when you use a Warcry / 24% increased Warcry Speed / 18% increased Warcry Cooldown Recovery Rate"; 혈마법 "You have no Mana / Skill Mana Costs Converted to Life Costs"; Second Wind III "Cannot support Meta, instant, or Triggered Skills … When a Supported Skill is used and goes on cooldown, recover 1% of maximum Life per second of cooldown"(0.4.0에서 2%→1%). 쿨다운을 무시하는 함성은 "goes on cooldown"이 없으므로 회복이 발동할 수 없다(추정, 가이드 0.3.1 노트와 일치). 제작자 발언(0.3): "keep your seismic cry at level 11 … I lose like four HP per war cry" https://youtu.be/B8yBMkd-jsE?t=598 [9:58–10:10]. 0.1 우버에선 lv20 지진 함성 72 생명력 → lv11 49 → 보조 정리 후 42 https://youtu.be/gWQNu6xddow?t=408 [6:48].
6. **단일 대상 = 토템 + 무기 세트 패시브.** 가이드: "Corrupting Cry starts to fall off in single-target fights as we reach the endgame. That's where Shockwave Totem and weapon swapping gets into the picture. By using our weapon set points, we can take passives that relate to warcrys and shields on set 1, and passives related to totems on set 2."(E:564–567). 사실(export 트리, 0.5 GGPK 이름): 세트1 = Relentless, **공성 작전(Lay Siege)**, **근력(Beef)**, 다급한 부름, Defender's Resolve, Bolstering Yell, Cacophony, Guttural Roar, 격파의 일격, **경계(Vigilance)**; 세트2 = Ancestral Alacrity / Artifice / Unity / Reach / Mending, **감시 포탑(Watchtowers)**, Supportive Ancestors, Crushing Verdict(세트1·2 나머지 노드는 한국어명 미확인).
7. **충격파 토템 12초 + 자동 스왑.** 가이드: "Shockwave Totem has a base duration of 12 seconds … we can automatically weapon swap when putting down Shockwave Totem's, and weapon swap back via Seismic Cry to the safety of our shield. … our totems will be active even after we swap back to our shield."(E:569–576). 사실: "Totem duration is 12 seconds / Limit 1 Totems", 퀄리티 "Limit (0—1) Totems", 강타 "Attack Speed: 50% of base / Attack Damage: (25—66)% of base", "The Totem cannot create Jagged Ground", "Requires: Any Martial Weapon"(https://poe2db.tw/us/Shockwave_Totem). 가이드의 "4 Shockwave Totem's"(E:310)는 기본 1 + 퀄리티 1 + 응답받은 부름 1 + **과잉(Overabundance)** "+1 to Limit / 50% less Skill Effect Duration" = 4(세트1 기준)로 맞아떨어진다(추정); 충격파 토템은 Melee 태그(poe2db "Totem, AoE, Melee, Slam, Duration, Nova")라 세트2의 Ancestral Artifice "Melee Attack Skills have +1 to maximum number of Summoned Totems"가 활성이면 5 — 가이드의 "4"는 세트1에서 센 수치일 가능성(추정). 스왑 후 토템 잔존은 AWT만 0.3.0c 노트("no longer disappears if swapping to an invalid weapon or Weapon Set", poe2db Version_0.3.0c L47)로 확정, 충격파 토템은 명시 없음(미확인). 0.5.5 L389 "Fixed a bug which would allow Skills from an alternate Weapon Set to be used without the corresponding Weapon swap occurring" 이후 세트2 스킬을 쓰면 스왑이 실제로 일어난다 — 스왑 없이 세트2 스킬을 쓰던 편법 종료, G 메뉴 세트 배정 필수(사실). 제작자의 0.5.5 계획(Discord, 결론 5)은 충격파 토템이 아니라 AWT + **선대의 유대(Ancestral Bond)**("Your Totem Limit is doubled / No Charge requirement for placing Totems / Totems reserve 75 Spirit each", PN/3932540 L790)이므로 이 산식은 가이드 변형에만 해당한다.
8. **요철 지대 겹치기.** 가이드: "we need Jagged Ground via Earthquake. This jagged ground can overlap with the help of Encroaching Ground"(E:578–586). 사실: 지진 "Cannot create Jagged Ground on top of an existing patch", "Limit (2—4) Jagged Ground patches", 요철 지대 4초; **잠식하는 지대(Encroaching Ground)** "Ground Surfaces … gain 20% increased Area of Effect per second, up to a maximum of 100%". FAQ "Don't use Persistent Ground III with Earthquake, it disables Shockwave Totem explosion"(E:517–519)은 **유지되는 대지(Persistent Ground) III**의 "Ground Surfaces created by Supported Skills cannot be destroyed except by expiring"과 맞물린다(추정: 분출이 패치를 소모).
9. **대장간 망치.** 가이드: "Forge Hammer (detonated via Seismic Cry) … each Shockwave Totem triggers the fissures it creates, and it also "snapshots" with set 2."(E:587–600). 사실: "Cooldown Time: 8.00 s", "Hammer duration is 12 seconds", 함성으로 파쇄 시 "Creates 5 fissures", "Cooldown does not recover while the hammer is lodged". "snapshots with set 2"는 0.5.5 L389/L393 이후 성립하지 않는다(추정: 세트2에서 던지고 세트1 함성으로 터뜨리는 동작 자체는 남고, 세트2 보조젬 효과가 세트1에서 유지되는 부분이 사라진다). **리그월드의 흉포함(Rigwald's Ferocity)** 현재 문구 "Supported Skills deal 30% more Damage if used in Weapon Set II / 10% reduced Attack Speed if used in Weapon Set II" — 0.3 영상의 "30% more damage … if the skill is in set two" [11:29]와 일치(사실).
10. **방어층(0.3 개요 영상).** "We no longer go for block. Block now doesn't protect more than 50% by default. applies against all damage … Turtle charm … 20% of damage now goes through blocked hits and this is also the case for [Svalinn — 자막 "as it also got that stat"로 훼손, 문맥 추정] … So [Renly's] training isn't needed at all." https://youtu.be/BLc0SguI0gk?t=925 [15:25–16:09]; Wooden Wall "basically 20% less less damage taken as long as we have a totem out" [16:21–16:27]; Jade Heritage "10% damage reduction from physical" [16:29–16:31]. 사실: 거북이 호신부 "You take 20% of damage from Blocked Hits / Maximum Block chance is 75%", 나무 벽 "20% of Damage from Hits is taken from your nearest Totem's Life before you", 비취의 전승 "Gain a stack of Jade every second"(1% PDR × 최대 10), 마그마 장벽 "Grants 25% increased Block chance" + 완전 충전 후 방패를 든 상태의 다음 막기 1회에 Magma Spray 발동 + 인내 충전 1("When fully imbued, your next Block with your Shield raised will expend the lava to Trigger the Magma Spray skill and grant you an Endurance Charge"), **주운 판금(Scavenged Plating)** "4% more Armour per Scavenged Plating / Maximum 10".
11. **응답받은 부름의 혼백.** 제작자 발언(0.3): 고릴라(피해 50% 증가), 마녀(광역 Pin), 거북이("80% increased defense and 4% increased block chance"), 네 번째(자막 "warllar", "10 rage on hit … 20% increased skill speed") https://youtu.be/BLc0SguI0gk?t=160 [2:40–3:23]. 사실: poe2db Warcaller's Bellow 페이지의 버프 "You gain 10 Rage on Hit with Attacks and have 20% increased Skill Speed"(Ancestral Warhorn 미니언 버프) — 네 번째 혼백은 Warhorn으로 추정. **선대의 혼백(Ancestral Spirits)** 현재 문구 "Minions from this skill have 1% increased Damage per 1 of your Strength" — 힘이 여전히 피해에 닿는 유일한 경로(사실).
12. **Uber 엔진(0.3 CA 영상, 지금은 사망).** 포효하는 함성(최소 위세 10) → 격노하는 함성 "4 Rage per 5 Power" = 8 격노 → "Seismic Cry gives you double the power … 16 rage per war cry"(제작자 주장 버그) https://youtu.be/F6ou4sj0uZE?t=120 [2:00] → Hateforge(3충전, 최대 격노 22) 2회 함성마다 발동 → Redblade Banner "Enemies in your Presence count as having double Power"로 보스 옆 2회 발동 = 6충전 → Guatelitzi 코어 ×2로 배가 → AWT 3충전씩 소모, Perpetual Charge 환급. 0.4.0에서 Hateforge(1충전/3–6초)와 Guatelitzi(Limit 1)가 함께 죽었다(3장).

---

## 3. 0.4.0 → 0.5.5 변경 전수표

원문은 레포 캐시 파일 그대로(오타 포함). 판정 = 버프 / 너프 / 무관 / 미확인. "이 빌드에 미치는 것" 열은 별도 표시 없으면 추정이다. 0.4.0 노트의 "Updates for 9-12-2025" 같은 부록 날짜는 D-M-Y(12월)다.

### 3.1 0.4.0 (2025-12-05) + 핫픽스 + 0.4.0b ~ 0.4.0l (~2026-05-26)

| 버전 | 원문 | 이 빌드에 미치는 것 | 판정 |
|---|---|---|---|
| 0.4.0 L545 | "Ancestral Warrior Totem: No longer has 25% less Totem Attack Speed." | Uber 변형 핵심. 제작자 "33% DPS buff"(E:692–693) | 버프 |
| 0.4.0 L942 (=L1782, 12-09 추가) | "The Hateforge Unique now has "300-400% increased Armour" (previously 50-80%), existing items can be updated using a Divine Orb. Now has Gain a random charge on reaching maximum Rage, no more than once every 3-6 seconds (previously 1-3 charges). It now also rolls "Gain 3-6 Rage on Hit", this change does not affect existing versions of the item." | 우버 엔진의 "3충전 on max rage" 소멸. 제작자 로그 "It's killed"(E:698–700) | 너프 |
| 0.4.0 L1040 | "Guatelitzi's Soul Core of Endurance is now Limited to: 1." | 우버 "2 x Guatelitzi's Soul Core of Endurance"(U:15–16) 불가. 제작자는 기록 안 함 | 너프 |
| 0.4.0 L405/407/409 | "Second Wind I can no longer support Meta skills." / "Second Wind II can no longer support Meta skills." / "Second Wind III now has Restore 1% of maximum Life on use per one second cooldown of Supported Skills (previously 2%). Can no longer support Meta skills." | 이미 0.3.1에 죽은(제작자 changelog E:684–685 기준, GGG 문구 미확인) 회복 트릭을 반감. FAQ의 "until you get Second Wind III"(E:468–470)는 낡음 | 너프 |
| 0.4.0 L523 | "Fixed the following skills having modifiable Limits that were not described as Limits: Frozen Locus, Earthquake, Earthshatter, Shield Wall. These skills can also now be supported by Overabundance." | 지진/지면 분쇄에 과잉 가능. 가이드는 전 변형에서 과잉을 충격파 토템에만 둔다(미활용) | 버프 |
| 0.4.0 L126 (12-11 추가) | "Totem Placement speed now also scales the speed at which Totems emerge." | Urgent Totems III(배치 속도 100%) 가치 상승 | 버프 |
| 0.4.0 L182 | "The Ancestral Warhorn minion summoned by Warbringer's Answered Call notable now more consistently hits close-up enemies with the second part of its slam attack." | 응답받은 부름 혼백 | 버프 |
| 0.4.0 L180 | "Imploding Impacts now also grants Fully Broken Armour you inflict increases all Damage Taken from Hits instead." | 가이드 트리에 내파하는 충격 없음(export: Warcaller's/Answered/Jade/Wooden) | 무관 |
| 0.4.0 L108 | "Modifiers to the number of enemies required to be considered Surrounded can no longer reduce the required number of enemies below 1." | 우버 Constricting Command. 제작자 "you're not going to get the movement speed" https://youtu.be/CoskGFogxhA?t=606 [10:06–10:08](단락 시작은 [9:36]) | 너프 |
| 0.4.0 L435 | "Rigwald's Ferocity now has Supported Skills have 30% increased Attack Speed if used in Weapon Set I (previously 20% more Attack Speed)." | 대장간 망치는 세트2 배정이라 세트I 줄은 무관, 세트II "30% more Damage" 유지 | 무관 |
| 0.4.0 L483 | "Enraged Warcry and Rageforged Supports are now treated as spending Rage." | Rageforged II(대장간 망치)가 격노 소비 취급 | 미확인 |
| 0.4.0 L110/112/114 | "Rage regeneration now pauses rage decay…" / "All rage spending costs have been changed to 10 rage…" / "You now lose 5 rage per second if you have not taken damage or gained rage in the past 4 seconds (from 10 rage per second … 2 seconds)." | 격노하는 함성 → 30 격노 유지가 쉬워짐 | 버프 |
| 0.4.0 Hotfix 4 (3885885 L19) | "Fixed a bug where Raging Cry Support wasn't delaying Rage decay." | Starter/Endgame 보강하는 함성의 격노하는 함성 | 버프 |
| 0.4.0 L1014 | "Idol of Grold is now Limited to: 1, now grants Gloves: 20% increased total Power counted by Warcries (previously 15)." | 가이드 슬롯에 없음 | 무관 |
| 0.4.0 L755/757 | "Svalinn now has "You take 0-20% of Damage From Blocked Hits" (previously 15-20%)." / "Svalinn now has "200-300% Increased Armour" (previously 150 to 200%)." | 0.4 슬롯에 스발린 없음(0.1~0.3 유물). 젬링 포크 탱크판이 다시 씀 | 무관 |
| 0.4.0 L835 | "The Surrender now drops on the Vaal Tower Shield base-type (previously Stone Tower Shield) - Existing items will not have this change." | 슬롯에 없음 | 무관 |
| 0.4.0 L1176–1178 | "Perfect Essence of Battle now grants +3 to Level of all attack skills on one handed melee weapons and bows (from +4)." / "…+5 … on two handed melee weapons and crossbows (from +6)." | 세트2 양손 철퇴 근접 레벨 크래프트 | 너프 |
| 0.4.0 L1218–1219 | "Maps no longer scale pack size as you increase in tier, they instead increase non-unique monster Effectiveness. Effectiveness grants monsters increased life, increased experience granted and increased quantity of items dropped." | 제작자: 시체 폭발(생명력 25%)이 Effectiveness로 커진다 — "the corpse explosion scale with monster life, which is what's going to be scaled by the new effectiveness modifier" https://youtu.be/CoskGFogxhA?t=567 [9:27–9:33] | 버프 |
| 0.4.0 L1375–1379 / Hotfix 6 (3885965 L7) | "Bosses now have an Anti-Burst damage mechanic: … The damage reduction tapers down from full effect to no effect over the course of this duration." / "Boss Damage Reduction will now fall off faster" | DoT 램프 빌드엔 완충, 토템 오프너는 감쇄 구간에 걸림 | 미확인 |
| 0.4.0 L124 (12-08 추가) | "Sprinting no longer prevents heavy stun buildup decay." | HC 생존 소폭 | 버프 |
| 0.4.0 L1397 | "The Blind Beast no longer drops a Bile-soaked Tome. Instead, the Dark Mists quest now grants a Mist-shrouded Tome (which grants two Weapon Set Passive Skill Points) in addition to its existing rewards (Uncut Skill Gem and Gold)." | 두-세트 빌드에 세트 포인트 +2 | 버프 |
| 0.4.0 L1579 | "Fixed several bugs allowing stats affecting charge gain to effectively double dip. …" | 우버 인내 충전 계산에 영향 가능 | 미확인 |
| 0.4.0 L1527 | "Fixed a bug where Battershout Support wasn't working with Fortifying Cry nor Ancestral Cry." | Battershout(구타하는 고함)는 0.5 신규가 아니라 0.2.0g부터 존재(사실: poe2db Version_0.2.0g L101 "Battershout's triggered explosion now counts as a Warcry skill" — `SOURCES_MANIFEST.md`의 "0.5-era" 표기는 이 줄로 대체). 가이드에 없음 | 무관 |
| 0.4.0c L207 | "Fixed a bug where Warcries ignored Warcry speed while shapeshifting." | 변신 안 씀 | 무관 |
| 0.4.0 L399 (=L1624) | "Magnified Area II support gem no longer causes the supported Skill to deal less damage." | Endgame 지진·전쟁 깃발·선대의 혼백, Uber 혼백의 Magnified Area II | 버프 |
| 0.4.0 L713 | "Volcanic Fissure: Now deals 101-166% of Attack Damage (previously 88-145%) at Gem levels 7-20." | 레벨링 21–30 밴드·오늘 실캐릭의 **화산 균열(Volcanic Fissure)** L7 | 버프(레벨링) |
| 0.4.0 L487 / L489 | "Impact Shockwave support now actually makes aftershocks, allowing interaction with aftershock-specific area and damage modifiers. Previously it was actually a variant of Melee Splash, which did not benefit from those. This also allows a strike to cause both an Impact Shockwave aftershock, and melee splash, from the same hit." / "Impact Shockwave can now support non-strike Wind attacks." | 오늘 실캐릭 뼈 박살(Boneshatter)의 보조 | 버프(레벨링) |
| 0.4.0 L1092 / L1096 | "Oak Greathammer now has 16-30 damage (from 14-26) has 1 attacks per second (previously 1.05), this is a ~10% damage increase. Increased stun build up implicit has been lowered to 20-40% (previously 30-50%) to compensate." / "Cultist Greathammer now has 36-49 damage (from 32-43) and Fanatic Greathammer now has 101-137 damage (from 89-120)." | 세트2 양손 철퇴 베이스(Starter Oak / Leveling Cultist). Oak는 기절 축적 implicit 감소 → 격파의 일격 트리거 소폭 ↓ | 혼합 |
| 0.4.0 L393 / L395 / L397 + L1573 | "Ambrosia I is now a Tier II support (previously Tier III)." / "Added Ambrosia II as a Tier-III support, which consumes 35% of your Mana Flask's maximum charges, granting 1% of damage as extra Lightning damage per charge consumed." / "Ambrosia support is now Ambrosia I and consumes 14% of your Mana Flask's maximum charges, granting 2% of damage as extra Lightning damage per charge consumed (previously consumed 20% and granted 3% per charge consumed)." / "Fixed a bug where Ambrosia Support and Concoct Support were granting their full benefits when only a portion of their desired flask charge consumption could be fulfilled. Both supports now only consume flask charges if their desired amount can be fully fulfilled." | Endgame/Uber 대장간 망치의 암브로시아. 14%/2% 재편 + 충전 부족 시 효과 0(L1573) → 마나 플라스크 충전 관리 필수 | 너프(수정) |
| 0.4.0 L377 | "Perpetual Charge is now an Intelligence Support gem (previously Dexterity)." | Uber Perpetual Charge, Int 요구치에 반영 | 무관 |
| 0.4.0d (3905934 L115) | "Fixed Uhtred supports counting Meta gems as Support Gems when determining whether their effect applies or not." | Uber Charge Regulation → Uhtred's Exodus | 미확인 |
| 0.4.0 L184–L190 | Titan: "Surprising Strength has been removed." / "Crushing Impacts now also Grants 25% more Damage against Heavy Stunned Enemies." / "Added a new Mountain Splitter Ascendancy Passive Skill…" | 워브링어 아님(Breegin Titan 포크에만 해당) | 무관 |
| 0.4.0 L904 / L1086 | "The Anvil now has "+5-10% to Maximum Block Chance" (previously 3-5%). Existing items can be updated using a Divine Orb." / "Totemic Great Club now has "Warcries Empower an additional attack" (previously Crushes Enemies on Hit), and now has 77-105 damage (previously 73-99). Existing items will not have this implicit." | 막기 상한 옵션 / 세트2 베이스 옵션(함성 강화 implicit). 가이드 슬롯에 없음 | 무관(옵션) |
| 0.4.0 키워드 0회 | Corrupting Cry, Corrupted Blood, Seismic/Infernal Cry, Shockwave Totem, Warcaller's Bellow, Wooden Wall, Jade Heritage, Renly's Training, Turtle Charm, Blood Magic, Urgent Call, Titanrot, Meginord, Deidbell, Astramentis, From Nothing, Roaring Cries(0.4.0 + 핫픽스 10 + b~l 61개 파일 grep) | 함성 젬(Seismic/Infernal/Fortifying/Corrupting Cry) 자체의 밸런스 변경은 0줄. Fortifying Cry·Answered Call은 각 1회(L1527 Battershout 버그픽스, L182 Warhorn 혼백) — 위 표 참조. 워브링어 노드 변경은 L180(Imploding Impacts)·L182(Answered Call 혼백) 2줄뿐(사실) | 무관 |

### 3.2 0.5.0 "Return of the Ancients" (2026-05-22 게시, 05-29 런칭) — 스킬 / 보조 / 유니크 / 패시브

| 버전 | 원문 | 이 빌드에 미치는 것 | 판정 |
|---|---|---|---|
| 0.5.0 L1044 | "Corrupting Cry I, Corrupting Cry II: No longer causes the supported skill to inflict Corrupted Blood, but instead it triggers a skill which inflicts Corrupted Blood, scaled by the level of the gem it is socketed into." | 핵심 재설계. 힘 스택 → 함성 젬 레벨 스택. 저레벨 유지 규칙 역전 | 너프 (설계 변경) |
| 0.5.0 L1070 | "Paquate's Pact: No longer causes the supported skill to inflict Corrupted Blood, but instead it triggers a skill which inflicts Corrupted Blood, scaled by the level of the gem it is socketed into. No longer has Lose 2% of maximum Life per Corrupted Blood inflicted by Supported Skills. Instead, it now has Supported Skills Cost 10% of maximum Life for each time they've been used Recently, up to a maximum of 30%." | 워브링어 가이드에 없고 젬링 포크가 씀. 제작자: "Instead of killing you it now only costs 10% of your maximum life or up to 30%" https://youtu.be/Jj2eKr4Ez-A?t=883 [14:43]. KR 페이지는 "최근 4초 이내" | 버프(HC 안전) / 비용 |
| 0.5.0 L926 | "Ancestral Warrior Totem: No longer has a hidden 0.6 second delay between skill uses. Instead, this delay is now 50% of the skill's attack time and is described accordingly on the skill." | 현재 문구 "Conjures a spirit warrior every 150% of socketed Attack time". 구 간격을 T + 0.6초로 두면 손익분기 = 공격 시간 1.2초(0.6 ÷ 0.5). 단 poe2db 버전 이력 0.3.0 "Ancestral Warrior Totem: Now have no Limit. Socketed Mace Skills now have 50% less Attack Speed. Now requires consuming 3 Endurance Charges to Raise."의 "50% less"가 0.4까지 살아 있었는지 확인할 삭제 노트가 캐시에 없다(0.4.0 L545가 지운 것은 별개 스탯 "25% less Totem Attack Speed"; 현재 스탯 블록엔 less Attack Speed 줄 없음). 살아 있었다면 구 간격은 ~2T + 0.6이고 0.5.0은 모든 T에서 순수 버프 → 1.2초 손익분기는 그 전제에 걸린 조건부 | 미확인 |
| 0.5.0 L1574 | "Fixed an issue where Shockwave Totem was able to be socketed into Ancestral Warrior Totem." | 가이드 4개 변형 어디에도 그 조합 없음(사실, export) | 무관 |
| 0.5.0 L940 | "Earthquake: Aftershock now deals 184-666% of Attack damage at Gem levels 1-20 (previously 160-580%)." | 요철 지대 소스 | 버프 |
| 0.5.0 L950 | "Fortifying Cry: Now only consumes one stack when you detonate a shield wall to create a shockwave around each shield wall segment. Fortifying Cry Shockwaves from a single Shield Wall cannot hit the same enemy multiple times. Shield Wave now deals 5 to 7 Added Physical Damage per 15 Armour on Shield (previously 6 to 8)." | 워브링어판은 보강하는 함성을 격노/가호용으로만 씀 | 무관 |
| 0.5.0 L970 / L988 | "Magma Barrier: Now deals 5 to 7 Added Fire Damage per 15 Armour and Evasion on Shield (previously 6 to 8)." / "Resonating Shield: Now deals 5 to 7 Added Physical Damage per 15 Armour on Shield (previously 6 to 8)." | 마그마 장벽(전 변형), 공명하는 방패(오늘 실캐릭) 피해 소폭 | 너프(경미) |
| 0.5.0 L992 / L932 / L1040 | "Rolling Slam: Now has +1 second to total Attack time (previously +1.5 seconds). The First Slam now deals 75-272%… (previously 90-367%)…" / "Boneshatter: Quality now grants 0-20% increased Attack Speed (previously 0-30%…)." / "Brink I: Can now be Cut as a level 1 Support Gem (previously level 2)." | 1–33 레벨링 가이드의 스킬. 오늘 실캐릭이 **몰려오는 강타(Rolling Slam)** L6 + Brink I, **뼈 박살(Boneshatter)** L6 사용 중 | 너프(레벨링) |
| 0.5.0 L1084 / L1086 | "Uhtred's Augury: Now grants +2 to level of Supported Skills if exactly two other supports are modifying them (previously +3)." / "Uhtred's Omen: Now grants +2 … if exactly one other Support … (previously +3)." | 함성 젬 레벨이 곧 피해가 된 순간 잘린 레버 | 너프 |
| 0.5.0 L1202 / L1206 / L1216 / L1212 | "The plus to Level of all Melee Skills modifiers on Two Handed Attack Weapons now has a value of +5 at Tier 1 (previously +7)…" / "…One-handed … +4 at Tier 1 (previously +5)…" / "The Perfect Essence of Battle now provides +3 … Two Hand … (previously +5), and +2 … One Handed … (previously +3)." / "The plus to level all Gems on Attack Weapons can now only roll above level 18." | 세트2 "+4/+5 to Level of all Melee Skills" 목표는 T1 상한 안. 0.1의 "+7" 목표는 무효. 함성은 Melee 태그가 없어 근접 레벨은 타락한 함성에 안 닿는다(추정) | 너프 |
| 0.5.0 L790 | "The Ancestral Bond Keystone Passive now has: Your Totem Limit is doubled, No Charge requirement for placing Totems, Totems reserve 75 Spirit each. …" | 가이드 트리에 없음. AWT 인내 충전 3개 요구를 지우는 대안 — 제작자가 Discord 09-03 20:27 "I'll be using ancestral bond for ancestral warrior totem"으로 채택 예고(제작자 발언). 토템당 정신력 75 예약이 새 관문(레벨 24 실캐릭 정신력 30) | 미확인(채택 시 핵심) |
| 0.5.0 L818 / L820 / L886 / L802 | "The Core of the Guardian Notable Passive Skill now grants 30% increased Block chance and 20% reduced maximum Energy Shield…" / "The Covering Ward … 12% increased Block Chance…" / "The Wide Barrier Notable Passive Skill now grants 30% increased Block chance and 20% reduced Armour (previously 25% reduced Defences)." / "The Adamant Recovery Notable Passive Skill has been replaced by Fortified Aegis, which grants 100% increased Armour, Evasion and Energy Shield from Equipped Shield." | 막기 스택 옵션 확대. 가이드 트리에 이 노드들 없음(export) | 버프(옵션) |
| 0.5.0 L822 | "The Craving Slaughter Notable Passive Skill now provides +15 maximum Rage if you've used a Skill that Requires Glory in the past 20 seconds (previously +8 per Skill … up to 5 times)" | 가이드 트리에 없음 | 무관 |
| 0.5.0 L942 | "Eternal Rage: Can no longer be activated in specific weapon sets. It is now required to be active in both weapon sets…" | 젬 목록에 없음 | 무관 |
| 0.5.0 L938 / L1078 | "Defiance Banner, Dread Banner, and War Banner: No longer have a Movement Speed penalty during use. Now have a Banner Aura base radius of 6 metres (previously 4.5)." / "Refraction II: Now additionally causes supported Banner skills to grant Allies Deflection Rating equal to 20% of their Evasion Rating." | **전쟁 깃발(War Banner)** Starter/Endgame; 그 보조 Refraction II의 추가 효과(아군 Deflection)는 회피 0인 방어도 워리어엔 실효 ~0 | 버프 |
| 0.5.0 L1150 | "The Svalinn Unique Shield's Cast on Block Skill now has Supported Skills Cost nothing. It also now has +50-100 Runic Ward, existing items are not affected by this change." | 0.4 슬롯엔 없음. 0.3 영상의 "life cost" 걱정(BO [5:22])은 소멸 | 무관(옵션 버프) |
| 0.5.0 L382 | "The Hateforge Unique Gloves can now roll +16-30 maximum Rage if you've used a Skill that Requires Glory in the past 20 seconds (previously +8-12 … up to 5 times)." | 죽은 우버 변형의 Vaal Cultivation 결과만 | 무관 |
| 0.5.0 L1266 / L1278 / L1286 / L1300 | "Idol of Grold now is socketed into Boots. It now grants 50% increased total Power counted by Warcries (previously 20%). …" / "Boar Idol … 25% increased Warcry Cooldown Recovery Rate when socketed in Gloves (previously 15%)." / "Ox Idol now grants 15% increased Block chance when socketed in Shields and Bucklers (previously 10%)…" / "Maximum Rage on Ruby Jewels can now roll between +1-2 to Maximum Rage (previously +1)…" | 그롤드의 우상(위세 → 격노하는 함성/보강하는 함성 가호)이 크게 올랐고 슬롯이 장화로 이동. Boar Idol은 쿨다운 무시 워브링어에 무의미 | 버프(옵션) |
| 0.5.0 L1220 / L1224 / L1228 / L1238 / L1244 | "Body Runes now grant +30/45/60 Maximum Life… (previously +20/30/40)…" / "Rebirth Runes now grant Gain 15/25/35 Life per enemy killed … (previously 10/20/30)…" / "Stone Runes now Cause 20/30/40% increased Stun Buildup … (previously 20/25/30%)…" / "Robust Runes now grant +6/9/12 to Strength … (previously +6/8/10)." / "Standard Rune Bonded Modifiers now grant 20 Life and 20 Mana … (previously 10 Life and 10 Mana)." | 가이드의 "Greater Robust Rune"(E:174–176) = 현재 +12 힘. 킬당 생명력 룬은 Titanrot 회복원 | 버프 |
| 0.5.0 L1180 / L1190 | "The amount of Armour granted by items and modifiers has been increased … At level 65, you should have approximately 33% more Armour, tapering down to 15% at level 80+." / "…One-hand Maces now have a base Weapon Range of 1.3 (previously 1.1), 1.5 for Two-hand Maces (previously 1.3)…" | 방어도 워리어 전반 | 버프 |
| 0.5.0 L918 / L1590 | "Many Skills which had no cost now cost 0 Mana… This includes … any Triggered Skills from Support Gems and other sources." / "Fixed some cases of Skills that are inherently triggered not being considered triggered skills for other stats." | 타락한 함성 페이지(poe2db, 저장본·라이브)엔 Cost 줄이 없다; 같은 구조의 뒤틀린 맹약은 "Cost: 0 Mana"(`Paquates_Pact.us.txt` L50). L918의 "0 Mana" 규칙이 타락한 함성에 적용되는지 미확인 | 미확인 |
| 0.5.0 L546 / L530 / L1652 | "Parry, Shield Block and Resonating Shield no longer delay Heavy Stun buildup from decaying longer than expected." / "Bleed damage on players is no longer increased while the player is moving. …" / "Fixed a bug where Blink, Parry and Raise Shield were not counted as Skill uses. This also fixes a bug where using Parry or Raise Shield did not count as Channelling." | 방패 막기 워브링어 생존 소폭 ↑; 방패 들기가 "스킬 사용"으로 집계 | 버프 |
| 0.5.0 L1160 | "Lesser, Greater and Perfect Jeweller's Orbs can now be used on items with skills on them to increase the number of sockets on the item's granted skills…" | 스발린류 아이템 스킬 | 무관(옵션) |
| 0.5.0 L720–772 | Ascendancy Changes 소제목: Acolyte of Chayula, Blood Mage, Chronomancer, Gemling Legionnaire, Pathfinder, Witchhunter | 워브링어·Titan 소제목 없음. 전 노드 이름 grep 0회(사실) | 무관 |
| 0.5.0 L760 | "The Advanced Thaumaturgy Notable Passive Skill no longer grants the Thaumaturgical Dynamism Skill. It instead now grants Gem Quality grants Socketed Skills an additional effect. …" | 젬링 포크의 근거. 워브링어 무관 | 무관 |
| 0.5.0 L1558 | "Fixed a bug where Forge Hammer Slams would not count when tracking slams for the Titan's Ancestral Empowerment Notable Passive Skill." | 대장간 망치 언급은 이 1줄뿐, Titan 노드 전용 | 무관 |
| 0.5.0 키워드 0회 | Seismic Cry, Infernal Cry, Raging Cry, Earthshatter, Second Wind, Urgent Call, Blood Magic, Giant's Blood, Titanrot, Meginord, Deidbell, Astramentis, From Nothing, Constricting Command, Roaring Cries, Brutality, Swift Affliction, Scavenged Plating, Polymathy, Endurance Charge | 사실(grep 재확인) | 무관 |

### 3.3 0.5.0 — 시스템 (리그·캠페인·아틀라스·HC 규칙)

| 버전 | 원문 | 이 빌드에 미치는 것 | 판정 |
|---|---|---|---|
| 0.5.0 L83 / L81 | "Added new defence: Runic Ward. This defence kicks in once you reach 1 life allowing you to continue to survive while your Runic Ward takes damage. Runic Ward regenerates independently of your life." / "…Armours lower than level 55 gain Runic Ward with no downside. Armours above this level trade some of their regular base defences for Runic Ward." | HC용 새 생명줄. 55+ 방어구는 방어도와 교환 결정 필요. 0.5.5부터 Verisium Anvil은 4막 퀘스트로 해금(3.5) | 버프 |
| 0.5.0 L131 | "The Hardcore variations of Runes of Aldur are parented to their Standard Runes of Aldur equivalent, meaning if you die in Hardcore Runes of Aldur you can continue on in the Standard Runes of Aldur League." | HC 사망 모델 그대로(0.5.5 L53도 동일 문구) | 무관 |
| 0.5.0 L127 | "All of your old characters from the Early Access launch are still present but a free passive tree refund has been granted due to the changes." | 골드 리스펙 비용 변경 문구 없음(사실) | 무관 |
| 0.5.0 L436 / L154 / L156 / L158 | "…the Atlas has been reset. … in order to gain points for the Atlas Tree you will need to do the Origins of Divinity storyline." / "Maps inside the fortress grant one or more passive points for the Atlas Passive Tree. This entirely replaces the previous method…" / "…over 300 nodes. After completing all the maps inside the fortress, you will gain enough passive points to fully allocate the Atlas Tree." / "As the entire atlas tree can be fully allocated, there is no need to allow respecialisation for it any more." | 0.1 영상의 "only Breach points" 류 아틀라스 조언 전부 무효 | 무관 |
| 0.5.0 L444 / L168 / L174 | "There are now two versions of each pinnacle boss, the Quest version and the Infinite Farm version. As such Primary, Secondary and Tertiary Calamity Fragments can no longer be obtained." / "The Burning Monolith along with Arbiter of Ash has been moved into the Fortress." / "Added Arbiter of Divinity Pinnacle Boss" | 가이드 "Uber Arbiter kill" 링크는 0.3 영상. 아비터 접근 경로 변경 | 무관 |
| 0.5.0 L182–L194 | "…Masters of the Atlas introduces Ascendancy-style progression for the endgame. … Each master has 12 nodes of which 4 can be selected at the same time." | 신규 시스템, 가이드 언급 없음 | 무관 |
| 0.5.0 L514–L524 | "Removed the second dreadnaught area, "The Dreadnaught Vanguard". The Act 2 boss is now in "The Dreadnaught."" / "Area order in Act 3 has been somewhat rearranged…" / "Monster density in the second half of the campaign has been reduced, especially in the Interludes…" | "Warrior Leveling 1-33"(2026-01-06)의 지역 순서·"level 33 zone = Act 3 first zone" 가정은 재확인 필요 | 미확인 |
| 0.5.0 L328 | "Fate of the Vaal has been added to the Core Game. You first encounter a series of 6 Ancient Beacons in Act 3…" | 캠페인 중 추가 콘텐츠 | 무관 |
| 0.5.0 L448 | "Each empty tablet slot now contributes to the amount of random non-tablet spawned league content in the area. …" | HC 매핑: 빈 맵이 조용한 맵이 아니다 | 미확인 |
| 0.5.0 L162 / L1350 / L214 | "Added 40+ Ancient Modifiers that have a chance to appear on any map outside the fortress" / "Essence Monster Packs are now affected by modifiers to Pack Size." / "Map bosses in Delirium will always be 100% delirious." | HC 매핑 위험 상승 요소 셋(6.4) | 너프(HC) |
| 0.5.0 L468–L482 | "The following Modifiers can no longer roll on Waystones: Baron's, Beastly, Brambled, Doryani's, Enervating, Faridun's, Hallowed, of Nemeses, Perennial's, Rusted, and Sacrificial." / "…generally Prefixes are Modifiers that affect a monster output towards the player, and Suffixes are Modifiers that affect the player or monster defences." / "Modifiers to Pack Size now also provide a chance for an additional Rare Monster…" / "Monster Rarity is a new stat…" | 0.4 시절 "피해야 할 맵 모드" 목록 무효 | 미확인 |
| 0.5.0 L1164 / L1168 / L414 / L1174 | "Greater and Perfect currencies have been made somewhat rarer, with Transmutation and Augmentation being made significantly rarer." / "Divine Orbs are now more common." / "The Recombinator has been disabled. …" / "Omen of Corruption can no longer be obtained." | 0.3 영상의 세트1 철퇴 레시피(Perfect Transmutation/Augmentation)는 재료 희귀도 상승 | 너프(경미) |
| 0.5.0 L1176 / L1178 | "Martial Weapons and Flasks found in the campaign are now more likely to be of the highest base type available at that level." / "The overall number of Essences found in the campaign has been increased…" | 레벨링 무기 수급 | 버프 |
| 0.5.0 L1372 / L1376 | "You can no longer enter Plunder's Point until you have turned in all 4 Map Pieces in Kingsmarch." / "You no longer need to visit the Halani Gates in order to access Traitor's Passage if you have already freed Risu." | 캠페인 동선 | 무관 |
| 0.5.0 L1358 | "The Burning Dead in Ogham Village now deal a portion of their damage as Fire (previously purely Physical)." | 1막 HC, 화염 저항 0인 초반 워리어 | 너프(경미) |
| 0.5.0 L532 / L712 | "Your maximum Runic Ward is now added to your starting Honour when beginning a Trial of the Sekhemas." / "Added a Reforging Bench to the entrance of the Trial of the Sekhemas." | 전직 시련. 시련 구조·전직 포인트 변경 문구 없음(사실) | 버프 |
| 0.5.0 L1386 | "Added a dedicated keybind to perform a dodge roll, which will not cause the player to sprint when held down. …" | Day 1 루프 "두 번 함성 → 구르기 → 스프린트"(B8yBMkd-jsE [0:21]) 조작에 QoL | 버프 |
| 0.5.0 L536 / L538 | "Only a single Leech instance per resource … can apply at a time." / "There is now a limit on the maximum amount of damage a hit can be considered to deal for Leech. Hits that deal less than 40,000 total damage are unaffected…" | DoT 빌드라 흡수 의존 없음 | 무관 |

### 3.4 0.5.0 핫픽스 3 ~ 0.5.4f (2026-05-30 ~ 08-13)

| 버전 | 원문 | 이 빌드에 미치는 것 | 판정 |
|---|---|---|---|
| 0.5.0 Hotfix 3 (3934869 L7, 05-30) | "Fixed a bug that would cause most damage modifiers to not apply to Corrupted Blood inflicted by Corrupting Cry Support or Paquate's Pact Support." | 런칭 첫 24시간엔 재설계된 타락한 피가 피해 증가를 못 받았다. Skadoosh 5월 판정(05-25)은 이 수정 전, 게시 전 이론이다(사실+추정). "most"가 무엇인지는 미명시 | 버프(정상화) |
| 0.5.0 Hotfix 3 L9 | "Fixed a bug where the Ancestral Spirit minions from Warbringer's triggered skill took no actions." | 응답받은 부름이 런칭 당시 고장 | 버프(정상화) |
| 0.5.0b (3935437 L41) | "Fixed a bug where Charge Regulation's name would be displayed as "Charge Infusion" in some contexts." | 표시만 | 무관 |
| 0.5.0b Hotfix 10 (3942896 L7) | "Jewellers Orbs can now be applied to skills granted by items (such as Unique Items) via the Skill Gems panel interface…" | 스발린류 | 무관 |
| 0.5.1 (3949197 L53, 06-05) | "Logging out and in again now preserves your heavy stun buildup. Logging out while heavy stunned will now restart the heavy stun animation when you log in again, unless you log into a different place to where you logged out." | HC 탈출 수단 약화 | 너프(HC) |
| 0.5.1 L153 | "Fixed a bug where Second Wind Support could not support skills used by totems or clones of the player." | AWT에 꽂은 쿨다운 스킬에 Second Wind 가능(가이드는 그 조합 없음) | 버프(옵션) |
| 0.5.1 L159 | "Fixed a bug with Spell Totem where the modifier for more Totem life per Endurance Charge Consumed applied twice." | Spell Totem 미사용 | 무관 |
| 0.5.1 L85 | "Seismic Cry, Forge Hammer, and Shield Wall now display the Quality benefits they provide." | 젬링 Advanced Thaumaturgy 표시. 워브링어 무관 | 무관 |
| 0.5.1 L61 | "The Cold, Lightning and Fire Attunement Support Gems are no longer limited to supporting just Attacks.  These now grant Gain 25% of Damage as Extra Cold, Lightning or Fire Damage respectively." | Uber AWT 소켓의 Fire Attunement 문구 변경. 엔진 사망이라 실효 없음 | 미확인 |
| 0.5.1 L99 / L101 / L107 | "Elite Abyss Monsters have had their damage, loot, and experience lowered…" / "The Lightning Tendrils used by Shepherd of the Pit is now deals 70% less Damage." / "Harano, the Meat Carver now deals 28% less Damage… Their Slam overall now deals 50% less Damage." | HC 생존 일반 | 버프 |
| 0.5.2 (3960375 L199, 06-12) | "Fixed a bug where Warbringer's Warcaller's Bellow Ascendancy Passive Skill could sometimes explode the same corpse an unlimited number of times." | 0.5.0~0.5.1 시체 폭발 영상은 과대 | 너프(수정) |
| 0.5.2 L205 / L207 | "Fixed a bug where Support Gems that cause Skills to consume Charges, or Armour Break or Elemental Ailments on an enemy, were not mutually exclusive with other Support Gems that consume the same thing." / "Fixed a bug where a number of Support Gems that add Charge-consumption behaviour to Skills did not allow Support Gems that modify Charge consumption to be socketed into the Skill." | 가이드 링크에 소비 보조 중복 없음(요철 지대 I은 레벨링 가이드의 Volcanic Fissure에만) | 미확인 |
| 0.5.2 L69 / L81 / L107 | "Siora, Blade of the Mists … Their Cyclone skill is now unblockable (red flash), while the Chaos Strike can now be blocked. …" / "Significantly reduced the damage of Chaos Volatiles from Ritual Altar encounters and Monster Modifiers." / "Significantly reduced the damage of the Rage and Malice Delirium Monsters." | 막기 빌드: Siora 사이클론은 못 막는다. Ritual은 0.5.5 리그 메커닉 | 혼합(HC) |
| 0.5.2 L75 / L77 / L83 / L85 / L99 / L103 | "Reduced the damage of Veynar, the Frostbane's Cascading Slam skill…" / "Reduced the damage of the Cannon Barrage and both Slam skills used by Malgor, the Nautilord…" / "Reduced the damage of the Hand Slam skill used by the Tendril Sentinel Monster." / "Reduced the damage of the laser attack from the Cecaelian Ravager Runic Monster as well as reducing the damage of its Slam attack." / "Reduced the damage of the Slam and Lightning Strike skills used by the Strider of the Pit Abyss Monster." / "Reduced the damage of the triple Slam skill used by the Fury Delirium Monster." | 근접 강타 보스·몹 피해 감소 6건 | 버프(HC) |
| 0.5.3 (3968601 L31, 06-19) | "Previously attempted Maps now additionally have 50% reduced Experience earned on top of the already penalised Item Rewards." | 일반 | 무관 |
| 0.5.3 L139–143 | "Reduced the damage, area of effect and freeze build-up of Geonor, The Putrid Wolf's Moonbeam skill in all versions of this Boss Fight." / "Reduced the damage of Count Geonor's Reverse Cleave skill…" | 1막 보스 HC | 버프 |
| 0.5.4 (3975218 L59, 06-25) | "Unique Items that grant Skills now use the lowest level of the Skill that you meet the requirements of when equipped, scaling up to the maximum described level on the item…" | 스발린 Cast on Block 조기 착용 가능. Deidbell/The Surrender 스킬 부여 여부 미확인 | 미확인 |
| 0.5.4 L109 | "Fixed a bug where Omen of Refreshment and Omen of Resurgence were only consumed when current life was below 25% rather than actually on reaching low life like they describe." | HC 보험 징조 정상화 | 버프(HC) |
| 0.5.4 L77 | "The following Augments can no longer be socketed into Augment Sockets on Corrupted or Sanctified items…: Astrid's Creativity, … Vorana's Carnage." | 소울 코어는 목록에 없음 → 타락 아이템에 소울 코어 가능(추정) | 무관 |
| 0.5.4b (3980516 L187, 07-03) | "Fixed a bug where the Recover X% of maximum Life when you use a Warcry modifier was recovering life on all Skill uses instead of just Warcries." | 다급한 부름 문구("Recover 2% of maximum Life and Mana when you use a Warcry")가 이 패턴과 같다. 0.5.4b 이전엔 모든 스킬 사용에 회복됐을 가능성(추정, 소스 아이템 미확인) | 너프(수정) |
| 0.5.4b L171 | "Passive Skills allocated from using the From Nothing Unique Jewel are now properly reset when fully respeccing." | 우버 From Nothing | 무관 |
| 0.5.4b L183 | "Fixed a bug where you could create a Portal to Town while being hit. The animation is correctly interrupted again in this case." | HC 탈출: 피격 중 포탈 불가, 로그아웃만 남음 | 너프(HC) |
| 0.5.4b L9 | "Removed a majority of the stun and freeze immunity windows from all versions of the Tor Gul, the Defiler boss fight." | 강타 기절 빌드 | 버프 |
| 0.5.4f (3996513 L7, 08-13) | "Fixed a bug that could cause skills to target the wrong direction if you locked onto an enemy within a very short window of starting the skill. …" | 토템 배치·강타 방향 | 버프 |

### 3.5 0.5.5 (2026-09-03) + 핫픽스 1–5 (09-05)

| 버전 | 원문 | 이 빌드에 미치는 것 | 판정 |
|---|---|---|---|
| 0.5.5 L7–L25 (TOC) | 9개 섹션: "The Forbidden Rites Event League", "Ritual Changes", "Trial of Chaos Improvements", "Runes of Aldur Moving to Core", "Endgame Changes", "League Content Changes", "User Interface Changes", "Microtransaction Changes", "Bug Fixes" | **밸런스 섹션 없음.** Warcry/Totem(스킬)/Warbringer/Corrupting Cry/Corrupted Blood/Paquate/Seismic/Slam/Block/Mace 0회; Strength는 L169 Atmohua 소울 코어 요구치 1회뿐(아래 행)(사실) | 무관 |
| 0.5.5 L389 | "Fixed a bug which would allow Skills from an alternate Weapon Set to be used without the corresponding Weapon swap occurring." | 세트2 스킬을 쓰면 스왑이 실제로 일어난다 — 스왑 없이 세트2 스킬을 쓰던 편법 종료. G 메뉴 세트 배정이 필수 | 너프(수정) |
| 0.5.5 L393 | "Fixed a bug which would allow Auras and Support Gems from an inactive Weapon Set to still apply to the player." | 가이드 "snapshots with set 2"(E:592) 무효. 비활성 세트 보조젬 효과가 남던 PoB 수치 전부 낡음 | 너프(수정) |
| 0.5.5 L391 | "Fixed a bug where it was possible to snapshot the effects of the Prism of Belief and From Nothing Unique Jewels." | 우버 From Nothing(Roaring Cries) 스냅샷 불가 | 너프(수정) |
| 0.5.5 L395 | "Fixed a bug which would allow using a Unique item granted Skill with non-Unique Weapons which were equipped in another Weapon Set." | 스발린류 아이템 스킬은 부여 아이템이 활성 세트에 있어야 함 | 너프(수정) |
| 0.5.5 L423 | "Fixed a bug where Ferocious Roar's Increased Damage Modifiers had incorrect scaling at gem level 20 and above." | Ferocious Roar = 드루이드 곰 변신 함성 메타 젬(GGPK `ferocious_roar`). 이 빌드 아님 | 무관 |
| 0.5.5 L123–L157 | "Added the following new Soul Cores:" — Jiquani's Soul Core of Abundance / Automation / Malediction / Munitions / Quaking / Radiance / Rallying / Rippling / Severing / Snares / Squalls / Targeting / Thundering, Atziri's Soul Core of Devotion / Alacrity / Inoculation / Vitality | poe2db 효과(각 Limit 1, 무기 소켓): Rallying "+1 to Level of all Warcry Skill Gems", Quaking "+1 to Level of all Slam Skill Gems", Automation "+1 to Level of all Totem Skill Gems". 셋이 무기 소켓 하나를 두고 경쟁. 드롭 = Trial of Chaos(L79) | 버프 |
| 0.5.5 L169 / L175 / L177 / L183 / L185 | "The Soul Core of Atmohua now grants Convert 40% of Requirements to Strength (previously 20%)." / "The Soul Core of Jiquani now has a Limit of 1. It now grants Recover 5% of Maximum Life on Kill when socketed into a Martial Weapon (previously 2%), and 5% increased Maximum Life when socketed into Body Armour (previously 3%)." / "The Soul Core of Opiloti now has a Limit of 1. It now grants 40% increased Magnitude of Bleed when socketed into a Martial Weapon (previously 15% chance to cause Bleeding on Hit)…" / "The Soul Core of Ticaba now has a Limit of 1. It now grants Hits against you have 50% reduced Critical Damage Bonus when socketed into Body Armour or Shields (previously 20%)." / "The Soul Core of Topotante … 25% reduced Effect of Non-Damaging Ailments on you when socketed into Boots…" | 힘 스택 요구치 완화, 킬당 회복(Titanrot 보완), Opiloti는 Endgame 충격파 토템 Bleed IV와 맞물리나 무기 소켓을 Rallying/Quaking/Automation과 경쟁, 방패 슬롯 치명 피해 −50%(HC). 기존 소울 코어 변경 18줄(L159–L193) 중 나머지 13개(Atmohua's Retreat·Cholotl's War·Estazunti·Jiquani's Thesis·Uromoti·Cholotl·Citaqualotl·Puhuarte·Tacati·Tzamoto·Xopec·Zalatl·Zantipi)는 ES/마나/원소/독/투사체/타 속성 전용이라 제외 — Tacati "+13% to Chaos Resistance when socketed into Armour"만 HC 저항 옵션 | 버프 |
| 0.5.5 L29 / L49–L53 | "Start fresh in a new economy with the Forbidden Rites event league." / "…Standard, Hardcore and Solo Self-Found variations…" / "The Hardcore variations of Forbidden Rites are parented to their Standard Forbidden Rites equivalent, meaning if you die in Hardcore Forbidden Rites you can continue on in the Standard Forbidden Rites League." | 리그 구조. FAQ: 시작 09-05 05:00 KST, 1.0(12-11)까지 | 무관 |
| 0.5.5 L33 / L35 / L37 / L39 / L41 | "In each area of the campaign you'll find a Ritual encounter. Unlike their Endgame counterparts, these instead provide items useful for levelling…" / "Twice within each Act, and once within each Interlude, you'll find clusters of Ritual Effigies … on top of that area's boss fight." / "…the boss will then be carried forward and added to the next Ritual in the cluster in the next area…" / "Upon completing the series of boss encounters you'll be able to spend your tribute on Unique Items." / "Sacred Blooms can now be found as a Ritual reward, which can add the Viridian Wildwood to a cluster of Maps…" | 레벨링 중 유니크 수급 경로(Meginord's/Deidbell 등)와 HC 위험이 동시에 늘어남 | 혼합 |
| 0.5.5 L73 / L77 / L79 | "…Now you can leave the Trial of Chaos at any point and resume your run at a later time from the same room." / "There is now a reward chest at the end of each room in the Trial of Chaos. This makes dying less punitive…" / "The rewards for completing a Trial of Chaos run now consists of only Currency and Soul Cores. …" | 새 소울 코어의 유일 출처 | 버프 |
| 0.5.5 L199 / L201 / L219 / L221 | "Farrow, Dannig, and Expedition content is now available in the Atlas as a core mechanic… from Act 4 onwards." / "Expedition Tablets can now be found in Standard and in the new Forbidden Rites League. …" / "The Verisium Anvil is now unlocked by completing The Runeseeker quest in Act 4 outside of the Runes of Aldur League." / "Farrow can now be placed in your Hideout in all Leagues after you have unlocked the Verisium Anvil." | 룬 수호 Runeforging은 4막부터 | 버프 |
| 0.5.5 L239 | "The Arbiter of Ash no longer has All Elemental Resistances, they instead now have Fire Resistance and Cold Vulnerability." | 물리 DoT 빌드 | 무관 |
| 0.5.5 L349 | "Fixed a bug where the Invigorated Sacrifices Atlas Passive Skill was causing Ritual Monsters to grant much more Tribute than intended." | 리그 메커닉 | 무관 |
| 0.5.5 Hotfix 4 (4001331 L7 / L9 / L11, 09-05) | "Fixed a common client crash." / "Re-nabled Atzoatl Map Device that was disabled in Hotfix 2." / "Fixed a bug where Lost-men Zealots could be invulnerable when revived in ritual." | L11: 오늘 1막 Ritual HC 위험 요소였음 | 버프(HC) |
| 0.5.5 Hotfix 1/2/3/5 (4001250/4001277/4001313/4001365) | HF1 L7 "Fixed a client crash." / HF2 L7·L9·L11 "Fixed a client crash." · "Fixed an instance crash." · "Temporarily disabled Atzoatl Map Device that was causing buffer underflow crashes…" / HF3 L7·L9 "Fixed 2 client crashes." · "Fixed an instance crash." / HF5 L7 "Fixed 4 client crashes." | 함성·토템·무기 세트 관련 0줄(사실) | 무관 |

---

## 4. 오늘의 하코 캐릭터 실측 (레벨 24 스냅샷)

출처: `scratchpad/ninja_shoutedhard.json`(poe.ninja API 원본), 페이지 https://poe.ninja/poe2/builds/forbiddenriteshc/character/ITheCon-2183/SkadooshShoutedHard. `updatedUtc` 2026-09-04T23:16:14Z(= 런칭 20:00Z 후 3h16m), `lastSeenUtc` 23:13:01Z(= KST 09-05 08:13, 런칭 3h13m 후). 트리 `PassiveTree-0.5`, `useSecondWeaponSet` = False. **이 표는 그 순간의 것이고 지금은 이미 낡았다.**

### 4.1 스킬 (전부 사실)

| 액티브 젬 | 레벨 | 소켓 | 보조 | 비고(젬 텍스트) |
|---|---|---|---|---|
| **충격파 토템(Shockwave Totem)** | 7 | 3/3 | Rapid Attacks I(15% AS) · Urgent Totems I(배치 속도 80%) · **포악함(Brutality) II**(30% more 물리, 카오스/원소 불가) | 32 마나, 지속 12초, "Limit 1 Totem", 요철 지대 분출 144% |
| **지진(Earthquake)** | **1** | 2/2 | **잠식하는 지대(Encroaching Ground)** · **유지되는 대지(Persistent Ground) I** | 8 마나, 요철 지대 4초, 여진 184%. 레벨 1 유지 = 비용·요철 지대 목적(추정) |
| **공명하는 방패(Resonating Shield)** | 7 | 1/2 | Rage I(한국어명 미확인; 근접 명중 시 격노 3) | 채널링, 14.8 마나/s, "Hits Break 31 Armour", "Cannot be Empowered by Warcries" |
| **화산 균열(Volcanic Fissure)** | 7 | 1/2 | **요철 지대(Jagged Ground) I**(사용 시 인내 충전 1 소모 → 요철 지대) | 13 마나, 물리 80% 화염 전환 |
| **몰려오는 강타(Rolling Slam)** | 6 | 1/2 | Brink I(한국어명 미확인; 기절 축적 30% more, 100% 도달 불가) | 27 마나, "+1 second to Total Attack Time" |
| **뼈 박살(Boneshatter)** | 6 | 1/2 | Impact Shockwave(한국어명 미확인; 0.4.0 L487부터 실제 여진) | 17 마나 |
| **선대의 혼백(Ancestral Spirits)** | 7 | 0/2 | — | 트리 부여(`source="Tree:39411"` = 응답받은 부름) |
| **방패 들기(Raise Shield)** | — | 0/2 | — | 방패 부여 스킬 |
| **마그마 장벽(Magma Barrier)** | 4 | 0/2 | — | **정신력 30 예약** = 보유 정신력 전부 |
| **지옥불 함성(Infernal Cry)** | **3** | 0/2 | — | 24 마나, 쿨다운 8초, 반경 4m, 추가 화염 32% |

- 보조 젬 속성 요구 합계 Str 35 / Dex 5 / Int 5 — 레벨링 가이드 21–30 밴드의 "Str 35 / Dex 5 / Int 5"와 숫자가 같다(사실). 보조는 3개 추가·3개 제외로 다르다(Rapid Attacks I·Brutality II·Encroaching Ground 추가, Magnified Area I·Overabundance I·Prolonged Duration I 빠짐).
- 충격파 토템만 3소켓 → Lesser Jeweller's Orb를 이미 썼다(추정). 레벨링 가이드 31–41 팁 "Save your Lesser Jewelers orb for the Corrupting Cry build"와 어긋난다.
- 지진 함성, 타락시키는 비명, 대장간 망치, Mace Strike, Herald of Ash 없음. Herald of Ash는 정신력 30 전부가 마그마 장벽이라 불가능(사실).

### 4.2 아이템 (사실)

| 슬롯 | 아이템 | 핵심 옵션 |
|---|---|---|
| 무기 | **Cataclysm Roar** — Spiked Club(한국어명 미확인), ilvl 21 레어, 퀄리티 +20% | 101% 물리 증가 · 물리 5–11 추가 · 명중 +16 · 치명 +1.78% · 룬 소켓 "14% increased Physical Damage"(Iron Rune 추정) |
| 보조 | **Eagle Refuge** — Braced Tower Shield(한국어명 미확인), ilvl 27 레어 | 막기 26%, 방어도 56 · 생명력 +23 · 힘 +14 · 냉기 저항 +12% · 기절 한계치 +9 · 방어도 11% |
| 투구 | **Bronzebeard**(유니크, 한국어명 미확인) — Horned Crown | 생명력 +100 · 방어도/ES 84% · **이동 속도 −10%** · 냉각/점화/감전 효과 감소 · Storm Rune +10% 번개 저항 |
| 갑옷 | **Beast Cloak** — Maraketh Cuirass(마라케스 흉갑), ilvl 27 레어 | 생명력 +17 · 화염 17 / 냉기 14 / 번개 12 · Storm Rune +20% 번개 · 룬 소켓 2/1 사용 |
| 장갑 | **Behemoth Caress** — Ringmail Gauntlets, ilvl 9 레어 | 생명력 +32 · 공격 속도 5% · 화염 7% · 공격 명중당 생명력 2 |
| 장화 | **Onslaught Spur** — Threaded Shoes, ilvl 24 레어 | **이동 속도 15%** · 민첩 +14 · 냉기 11% · 초당 재생 3.5 |
| 목걸이 | **Surefooted Sigil**(유니크, 한국어명 미확인) — Jade Amulet | 생명력 +41 · 민첩 +13(+13 기본) · 회피 구르기 +1m · 구르기 후 회피 50% |
| 반지 1 | **Sorrow Grip** — Topaz Ring | 번개 저항 +22%(기본) · 희귀도 10% · 마나 재생 14% |
| 반지 2 | **Hypnotic Nail** — Amethyst Ring | 카오스 저항 +11%(기본) · 생명력 +14 · 마나 +27 · 지능 +7 · 화염 17% · 재생 3.3 |
| 허리띠 | **Storm Harness** — Rawhide Belt(생가죽 허리띠) | 생명력 +24 · 방어도 +12 · 화염 14% · 기절 한계치 +6 · 호신부 슬롯 1 |
| 플라스크 | Grand Mana Flask / Dense Grand Life Flask of the Practitioner | 생명력 260 회복 3.5초, 회복 속도 44% |
| 호신부 | Sapphire Charm(한국어명 미확인) | 냉기 피격 시 냉기 저항 +25%, 4초 |
| 주얼 | **Entropy Joy** — **루비(Ruby)**, 노드 26725 | 기절 축적 13% · **토템 피해 14%** · 출혈 크기 8% · 피격 시 격노 2 |

- 인벤토리 ID는 Weapon/Offhand/Helm/BodyArmour/Gloves/Boots/Amulet/Ring/Ring2/Belt 10개뿐. `Weapon2`/`Offhand2` 없음, JSON에 "swap" 0회, PoB 내보내기의 "Weapon 1 Swap / Weapon 2 Swap" itemId 0. **스왑 세트가 스냅샷에 없다**(사실). 미착용인지 캡처 누락인지는 판별 불가.
- 가이드 21–30 밴드 지침 대비: "Iron Rune is very good for weapons" ✓, 장화 이동 속도 ✓, 전 부위 생명력 ✓, "+ x to level of all melee skills"·공격 속도 ✗, 저항은 가이드의 "elemental minimum total 60-75%"(레벨링 변형)에 한참 못 미침(레벨 24라 예상 범위).

### 4.3 패시브 (사실, `data/_cache/tree_0_5.json`으로 이름 해석)

- `passiveCounts` = 29(일반 23 + 세트 분할 6), 전직 2, 키스톤 없음.
- **전직**: Totem Life(20% 토템 생명력) → **응답받은 부름(Answered Call, 39411)**. 전쟁 소집자의 고함 미할당.
- **메인**: Brutal(기절 축적 10% / 근접 피해 16% / 힘 +10), Smash(근접 20% / 강타 기절 적 상대 40%), **Ancestral Mending**(토템 보유 중 초당 생명력 1% 재생, 토템은 3%)(한국어명 미확인), 근접 피해 소노드 ×8, Totem Life 16%, Totem Damage 15%, 주얼 소켓, 속성 소노드 9개 중 **8개 힘**·1개 지능.
- **세트1(6)**: **가시 구덩이(Spike Pit)**("Enemies in Jagged Ground you create take 10% increased Damage"), Perforation(요철 지대 지속 40%, 출혈 격화)(한국어명 미확인), Jagged Ground Effect ×2(각 15%), Block 5%, Bleed Chance 5%.
- **세트2(6)**: **Ancestral Artifice**("Melee Attack Skills have +1 to maximum number of Summoned Totems", 배치 사거리 20%), **Ancestral Unity**(소환 토템당 토템 공격 속도 4%), Totem Attack Speed 4%, Totem Damage 15%, Attack Damage 12% ×2(한국어명 모두 미확인).
- PoB 트리 URL: `https://www.pathofexile.com/passive-skill-tree/AAAABgYCJQ5yD2AWTiGYOLM-s0FVQZBDskaZR_NKQ1m_ZuNoZWrtay95KXuigxSMu41DmcWZ86icqwKxM7T10J3WG9ix4WfkoPHn9JH2ivscAAA=`

### 4.4 방어·공격 수치 (사실, ninja 계산기 값)

| 항목 | 값 | 구성 |
|---|---|---|
| 생명력 | **733** | 기본 304 + Bronzebeard 100 + 장갑 32 + 갑옷 17 + 방패 23 + 허리띠 24 + 반지 14 + 목걸이 41 + 1막 Ogham Manor 20 + **힘 158**(79 Str) |
| 방어도 / 회피 / ES | 333 / 75 / 44 | 물리 DR 3%(979 기준 피해) |
| 막기 | **33%** | 방패 26 × (1 + 마그마 장벽 25% + 노드 5%) |
| 이동 속도 | 96% | 기본 −8(흉갑 −5, 방패 −3) → Bronzebeard −10%, 장화 +15% |
| Str / Dex / Int | **79 / 47 / 19** | 힘: 15 + 방패 14 + Brutal 10 + 속성 노드 40 |
| 저항 F/C/L/Ch | **−5 / 12 / 4 / 11** | 각 원소에 −60 패널티 적용됨(ninja 규약). 냉기는 Sapphire Charm +25%를 상시로 셈 |
| 정신력 | 30 | 1막 Freythorn +30 → 마그마 장벽 전부 |
| EHP / 최소 최대 피격 | 1,035 / 740(화염) | 물리 808 · 냉기 854 · 번개 785 · 카오스 848 |
| 퀘스트 영구 버프 | +20 생명력(Ogham Manor), +30 정신력(Freythorn), +10% 냉기(Clearfell) | 2막 이후 버프 없음 → 1막 완료, 2막 진행 중(추정). Venom Draught 선택 아직 |

### 4.5 가이드와의 차이표

| # | 항목 | 가이드 | 실캐릭(레벨 24) | 읽기 |
|---|---|---|---|---|
| D1 | 첫 전직 | Warcaller's Bellow — "That's also when you should have your first ascendancy: Warcaller's Bellow"(E:82–84); 영상 "war [caller's] bellow and the corrupting cry support gem" https://youtu.be/BLc0SguI0gk?t=1589 [26:29] | **Answered Call**(+Totem Life) | 사실. 전직이 함성 쿨다운 대신 토템 수·혼백을 산다. 그가 말한 "once you hit level 23 or whenever you get your first [ascendancy]" [27:10] 타이밍은 맞고 노드만 다르다 |
| D2 | 핵심 루프 | 21–30 밴드: 지진 ×N / Volcanic Fissure + 요철 지대 I(마그마 장벽 인내 충전) → 충격파 토템 분출 | 동일 삼합 + 세트1 요철 지대 노드 | 사실. 루프는 2025-09-02 changelog의 0.3 설계 그대로 |
| D3 | 충격파 토템 보조 | Overabundance I + Urgent Totems I(21–30) / Brutality I + Overabundance I(33 변형) | Rapid Attacks I + Urgent Totems I + **Brutality II**, 3소켓 | 과잉 없음. 응답받은 부름 +1, Ancestral Artifice +1(근접 공격 스킬)로 세트2 활성 시 최대 3개(추정) — 0.3 Day 1 "triple totem" https://youtu.be/B8yBMkd-jsE?t=62 [1:02]와 맞물림 |
| D4 | 지진 보조 | Prolonged Duration I + Persistent Ground I(21–30) | Encroaching Ground + Persistent Ground I(31–41 구성) | 사실 |
| D5 | Volcanic Fissure | Rage I + Jagged Ground I(21–30); 31–41에서 대장간 망치로 교체 | Jagged Ground I만; Rage I은 공명하는 방패로 | 격노 생성을 채널링 방패 스킬로 이전(추정) |
| D6 | 공명하는 방패 | 어느 밴드·변형에도 없음(grep 0) | L7 + Rage I | 0.4 계획 외 스킬. 젬링 포크에서도 "방어구 파괴 축 → 6/17 충격파 토템으로 대체"로 기록됨 |
| D7 | Mace Strike / Herald of Ash | 1–10·11–20·21–30 / 21–30·31–41 | 없음 / 없음 | Herald of Ash는 정신력 부족으로 불가(사실) |
| D8 | 지옥불 함성 | "kept at lvl 3, and NEVER upgraded" | **레벨 3, 보조 없음** | 가이드와 정확히 일치. 0.5.5에선 이 규칙이 타락한 함성 12.5/s 상한을 뜻한다(사실) |
| D9 | 33 전환 | "respec your tree upon reaching level 33 or when you get a Corrupting Cry I" | 아직 없음. 트리는 토템+근접+요철 지대, 함성 노드 0 | 세 갈래: (a) 33에서 가이드대로 리스펙 (b) 토템 탱크로 계속(자막 "The total tank is good though" [13:53], totem/total 음성 미확인 — 8.2 S4) (c) Discord 계획대로 보강하는 함성 + 근접 레벨 + AWT + 선대의 유대(제작자 발언, 결론 5). 스냅샷으론 판별 불가 |
| D10 | 무기 세트 | "Don't forget to equip a 2-handed mace in weapon set 2!"; 세트1 방패 / 세트2 양손 | 세트 아이템 없음, 그러나 세트1·2 패시브는 둘 다 할당 | 세트2 트리를 썼으니 양손 철퇴는 의도된 것(추정). 0.5.5 L389 이후 세트2 스킬을 쓰면 스왑이 실제로 일어난다(세트 배정 필수) |
| D11 | 유니크 | 1–33엔 없음; Meginord's/Deidbell은 거래 | Bronzebeard, Surefooted Sigil | 저렴한 초반 HC 생존 유니크(추정). Bronzebeard −10% MS는 장화로 상쇄 |
| D12 | 주얼 | "Ruby's with wacry speed and any damage stats"(S:40) | 토템 피해 14%, 함성 속도 없음 | 토템 우선 |
| D13 | 속성 노드 | "Strength (on everything that can have it)" | 8/9 힘 | 일치. 힘 → 생명력 +158, 선대의 혼백 "1% increased Damage per 1 of your Strength" |

한 문단 읽기(추정): 레벨 24의 실캐릭은 가이드 21–30 밴드의 *루프*를 그대로 쓰되 토템을 "초반 단일 대상 도구"에서 빌드의 척추로 올렸다 — 응답받은 부름 선취, 3소켓 Brutality II 토템, 세트2 토템 노터블, 토템 피해 루비, Ancestral Mending, 전 속성 노드 힘. 지옥불 함성 L3는 가이드 그대로지만 0.5.5에선 그 규칙이 레벨 스케일 타락한 함성의 발목을 잡으므로, 타락시키는 비명 I을 어느 함성에 꽂는지(본인 Discord 계획은 보강하는 함성, 결론 5)와 AWT + 선대의 유대의 등장 시점이 다음 스냅샷의 관찰 포인트다.

---

## 5. 변형별 세팅 (가이드 4개 변형) + 0.5.5 유효성

젬 목록은 mobalytics 캡처 + LIVE 접근성 트리 + GraphQL export(해시 검증)에서 그대로. 유효성 = 유효 / 수정 필요 / 사망 / 미확인. 보조 젬 한국어명은 확인된 것만 병기.

### 5.1 Leveling (outdated) — "Corrupting Cry I support gem required! (lvl 33)"

| 구분 | 내용 | 0.5.5 유효성 | 이유 |
|---|---|---|---|
| 세트1 스킬 | **지옥불 함성(lv3 유지)** → Corrupting Cry I · Swift Affliction I · Brutality I; **지진** → Encroaching Ground · Persistent Ground I | **수정 필요** | lv3 함성 = 타락한 함성 12.5/s(사실). Corrupting Cry I "30% less Area of Effect". 젬 레벨을 올리면 비용도 오른다(19→85 마나 = 혈마법 시 생명력) |
| 세트2 스킬 | **충격파 토템** → Brutality I · Overabundance I; **대장간 망치** → Fist of War I · Elemental Armament I | 유효 | 두 스킬 0.5.x 무변경. 세트2 스킬을 쓰면 스왑이 실제로 일어난다(0.5.5 L389) |
| 버프 | Overwhelming Presence(한국어명 미확인, 보조 없음); 마그마 장벽 | 유효 | 마그마 장벽 6–8→5–7 경미 너프 |
| 보조 요구 | Str 30 / Dex 10 / Int 5 | 미확인 | 0.5 요구치 미대조 |
| 장비 우선 | 힘 → 장화 이동 속도 → 원소 저항 합계 60–75% → 생명력. "Set 2 is a good two-hander with as much damage as possible" | 유효 | 힘은 이제 생명력·요구치 목적(추정) |
| 아이템 | **죽음의 종(Deidbell)**(투구), **메기노드의 허리띠(Meginord's Girdle)**, Brigand Mace(+13 힘 / 킬당 생명력 19), Cultist Greathammer(+2 근접 레벨 등), Braced Tower Shield(+13 힘 / 막기 15%), Bronze Greaves(+17 힘 / MS 15%) | 유효 | 죽음의 종 현재 "(20—30)% increased Warcry Speed / Warcries Explode Corpses dealing 10% of their Life / Warcry Skills have (20—30)% increased Area of Effect", 메기노드 "+(40—50) to Strength" — 둘 다 0.4–0.5.5 변경 없음(사실). 0.5.5 캠페인 Ritual이 유니크 수급 경로 |
| 퀘스트 | "Venoms(Quest reward): Stun/ailment threshold" | 미확인 | 0.5 캠페인 보상 목록 미대조(페이지의 퀘스트 블록은 전부 "Not Specified") |
| 트리 | Main 70/123 · Set1 10/20 · Set2 11/20(남은 포인트 표기). export: 전직 Warcaller's Bellow + Warcry Speed; Beef, Price of Freedom, Brutal, Deafening Cries; 세트1 Beef/Urgent Call/Cacophony/Guttural Roar; 세트2 Ancestral Artifice/Watchtowers/Ancestral Unity | 유효(구조) | 실캐릭은 첫 전직을 응답받은 부름으로 바꿨다(4장) |

### 5.2 Starter (outdated) — "For Acts 4+ and when you start mapping"

| 구분 | 내용 | 0.5.5 유효성 | 이유 |
|---|---|---|---|
| 세트1 함성 | **지진 함성(lv11 유지)** → Corrupting Cry II · Brutality II · Swift Affliction II · Efficiency II; **보강하는 함성** → Raging Cry · Efficiency II; **지옥불 함성**(보조 없음) | **수정 필요** | "Keep Seismic Cry at lvl 11 if possible, the damage is not worth the cost atm"(S:167–169)은 역전(lv11 = 71.6/s, lv20 = 287/s). Corrupting Cry II는 AoE 페널티 없음. 격노하는 함성 "4 Rage per 5 Power" 무변경 |
| 세트1 강타 | **지진** → Persistent Ground I · Encroaching Ground · Prolonged Duration II(지속시간 연장 II) | 유효 | 여진 상향 |
| 세트2 | **충격파 토템** → Rapid Attacks II · Urgent Totems III · Overabundance II; **대장간 망치** → Fire Penetration II · Rageforged II · Fist of War II · Elemental Armament II | 유효 | Rageforged가 "spending Rage" 취급(0.4.0 L483). Overabundance II의 +Limit 값은 미확인(I은 +1) |
| 버프 | 마그마 장벽 → Maim; **주운 판금** → Prolonged Duration II; **전쟁 깃발** → Refraction II · Prolonged Duration II; **선대의 혼백** → Meat Shield II · Elemental Army · Armour Break III | 유효 | 전쟁 깃발 반경 6m·이동 페널티 삭제(0.5.0 L938 버프); 혼백은 핫픽스 3 이후 정상 |
| 보조 요구 | Str 85 / Dex 20 / Int 10 | 미확인 | — |
| 장비 우선 | 저항 75%(카오스 0–35%) → 이동 속도 → 힘 → 생명력 → 방어도. "Set 2 needs to be the highest DPS two-hander" | 유효 | — |
| 아이템 | Redblade Banner(방패), Black Sun Crest(투구, 한국어명 미확인), 메기노드의 허리띠, Bandit Mace(+31 힘 / 킬당 생명력 29), Oak Greathammer(+3 근접 레벨 등; 베이스는 0.4.0 L1092에서 피해 ↑·APS 1.05→1·기절 축적 implicit ↓). 경고: "Don't equip Titanrot Cataphract unless you like living on the edge" | 유효 | Redblade Banner 현재 "Enemies in your Presence count as having double Power"(poe2db, 사실) → 보강하는 함성 가호 최대치. Black Sun Crest 속성 증가 5–15% |
| 각인 | Swift Blocking(재빠른 막기), Marathon Runner(한국어명 미확인) | 유효 | 재빠른 막기 현재 "12% increased Block chance / 1% increased Movement Speed for each time you've Blocked in the past 10 seconds" |
| 퀘스트 | Venoms 기절/이상 한계치, Tattoos "5 strength/5% cold res/5% lighting res", Pillars "5% all elemental resistance, it is NOT a permanent choice" | 미확인 | 0.5 캠페인 보상 미대조 |
| 트리 | Main 7/123 · Set1 −4 · Set2 −4. export: 전직 Warcaller's Bellow / Answered Call / Jade Heritage(나무 벽 없음); 키스톤 Resolute Technique + 혈마법; 세트1에 Flip the Script(상황 반전) · Admonisher, 세트2에 가시 구덩이 · Perforation | 유효(구조) | 상황 반전 "Recover 50% of maximum Life when you Heavy Stun a Rare or Unique Enemy" = Titanrot 회복원(FAQ E:473–487) |
| 지침 | "Fortifying Cry to 30 Rage … and Infernal Cry before casting Forge Hammer for singletarget"; "Earthquake for safe extra damage with Shockwave Totem" | 유효 | — |

### 5.3 Endgame (outdated) — "lvl 75+"

| 구분 | 내용 | 0.5.5 유효성 | 이유 |
|---|---|---|---|
| 세트1 함성 | **지진 함성** → Corrupting Cry II · Brutality II · Swift Affliction II · Efficiency II · **우주의 영사(Astral Projection)**; **보강하는 함성** → Raging Cry · **Second Wind III** · Mobility · Astral Projection; **지옥불 함성** → Magnified Area I · Execute II · Elemental Focus · Astral Projection | **수정 필요** | (1) "You can maybe level up Infernal Cry, Fortifying Cry, but NOT Seismic Cry"(E:266–271) 역전. (2) Second Wind III는 제작자 스스로 "Forgot to remove"(E:702–704)라 했는데 아직 소켓에 있고, 0.4.0에서 1%로 반감, "Cannot support … Triggered Skills", 쿨다운 무시 함성엔 발동 조건 자체가 없다(추정). (3) 우주의 영사 "25% less Area of Effect"는 유지, 지진 함성이 Nova 태그라 가능 |
| 세트1 강타 | **지진** → Magnified Area II · Encroaching Ground · Prolonged Duration II · Persistent Ground I · Rapid Attacks III | 유효 | "only use Persistent Ground I, not 2/3" 그대로 |
| 세트2 | **충격파 토템** → Overabundance I · Brutality III · Urgent Totems III · Bleed IV · Execute II; **대장간 망치** → Fire Penetration II · Rageforged II · Fist of War III · **리그월드의 흉포함(Rigwald's Ferocity)** · **암브로시아(Ambrosia)** | 유효 | 리그월드 세트II "30% more Damage / 10% reduced Attack Speed"(사실). 암브로시아는 0.4.0 L393–397에서 I(T2, 14%/2%)로 재편되고 L1573부터 충전 부족 시 효과 0, 가이드는 무표기. "Ultimate Mana Flask 63% increased Charges"가 그 연료 |
| 버프 | 마그마 장벽 → Charge Profusion II · Maim; 주운 판금 → Prolonged Duration II; 전쟁 깃발 → Refraction II · Prolonged Duration II · Daresso's Passion · Magnified Area II; 선대의 혼백 → Brutus' Brain · Magnified Area II · Maim · Pin III; **비취에 갇힘(Encase in Jade)** → Slow Potency · Inhibitor | 유효 | 혼백 현재 "1% increased Damage per 1 of your Strength" |
| 보조 요구 | Str 95 / Dex 60 / Int 50 | 미확인 | — |
| 장비 우선 | 저항 75%(카오스 45–75%) → 이동 속도 → 힘 → 방어도 → 생명력 | 유효 | 방어도 아이템 +33%@65(0.5.0 L1180) |
| 아이템(export 옵션) | Black Sun Crest; 세트1 Flanged Mace(공속 26% / 힘 +31 / 킬당 생명력 29 / **토템 보유 시 피해 41%**); 세트2 Massive Greathammer(물리 110% / **+4 근접 레벨** / 공속 14% / 토템 보유 시 피해 86%); Tawhoan Tower Shield(방어도 +226·80%, 힘 +31, 방어도의 38% 원소 적용); Warlord Cuirass(방어도 +191·80%, 생명력 +100, 힘 +28); Vaal Mitts(생명력 +100, 힘 +31, **+1 근접 레벨**); Vaal Greaves(MS 30%); **별의 목걸이(Stellar Amulet)**(모든 속성 +23, 생명력 +85, 힘 +31 + 속성 촉매); Amethyst Ring ×2(생명력 +100, 희귀도 20%, 힘 +31); Plate Belt(방어도 +187, 생명력 +100, 힘 +31, 카오스 +24%); Ultimate Life/Mana Flask; Silver/Thawing/Stone Charm; **루비 ×3**(전역 물리 ≥5%, 함성 피해 ≥10%, 함성 속도 ≥10%, 힘 % ≥1; 하나는 방어구 파괴 5%) | **미확인** | "increased Damage while you have a Totem"은 0.4 Abyss "Ulaman prefix"(E:148,152) — 0.5.5 이벤트 리그 수급 미확인(poe2db 가중치 비공개). 근접 레벨 T1 상한 +5(2H)/+4(1H)라 표기 값은 범위 안. 힘 +31 도배는 이제 생명력·요구치 목적(추정). 루비의 "increased Damage with Warcries"는 타락한 함성에 "modifiers to warcry damage also apply"로 닿는다(사실) |
| 각인 | Swift Blocking | 유효 | — |
| 트리 | Main −12/123 · Set1 −4 · Set2 −4(mobalytics 카운터, export 노드 수와 정합 안 됨 — 트리 뷰어 없인 총 포인트 산출 불가). export: 전직 4개(Warcaller's Bellow / Answered Call / Jade Heritage / Wooden Wall); 키스톤 Resolute Technique + 혈마법; 노터블 Relentless, Beef, Deafening Cries, Brute Strength, Sturdy Metal, **잔혹한 수법(Cruel Methods)**, The Molten One's Gift, Tactical Retreat, Prism Guard, Gem Enthusiast, Tempered Defences, **박식(Polymathy)**, **연장(Protraction)**; 세트1·2는 2장 6항 | 유효(구조) | 0.5.0 패시브 변경 목록에 이 노드들 없음(사실). 박식 7% 무변경. 노드 이름은 0.5 GGPK 매핑(0 unknown)이며 위치·수치는 0.5.5 미대조 |
| 지침 | "Pre-buff with Infernal Cry, Fortifying Cry (30 rage) before using Forge Hammer with 4 Shockwave Totem's"; "Quality priority: Magma Barrier, Shockwave Totem, Infernal Cry, Earthquake" | 유효 | 4 토템 산식은 2장 7항 |

### 5.4 Uber Endgame (outdated) — "lvl 90+", Hateforge 엔진

| 구분 | 내용 | 0.5.5 유효성 | 이유 |
|---|---|---|---|
| 엔진 | "utilises Hateforge + Raging Cry (Seismic Cry) + 2 x Guatelitzi's Soul Core of Endurance + Roaring Cries to create a LOT of Endurance charges for summoning back to back Ancestral Warrior Totem's. Max 10"(U:9–25) | **사망** | Hateforge 0.4.0 "no more than once every 3-6 seconds (previously 1-3 charges)"; Guatelitzi "Limited to: 1"; 제작자 "It's killed". 0.5.5 From Nothing 스냅샷 수정(L391)까지 겹침 |
| 세트1 함성 | 지진 함성 → Corrupting Cry II · Brutality II · Swift Affliction II · Efficiency II · **Raging Cry**; 보강하는 함성 → Raging Cry · Efficiency II · Mobility · Astral Projection · **물리 숙련(Physical Mastery)**; 지옥불 함성 → Magnified Area I · Execute II · Elemental Focus · Astral Projection · Fire Mastery | 수정 필요 | 레벨 역전 동일. 물리 숙련(+1 레벨)은 오히려 가치 상승(추정). "it seems to give double rage for some reason"(U:263–265) 버그의 잔존 여부 미확인 |
| 세트2 | **AWT** → **지면 분쇄(Earthshatter)** · Branching Fissures II · Fire Attunement · Urgent Totems III · Rage III; 대장간 망치 → Rakiata's Flow · Jagged Ground I · Fist of War III · Rigwald's Ferocity · Ambrosia; 충격파 토템 → Urgent Totems III · Armour Break III · Overabundance II · Rage III · Bleed IV | 유효(엔진 없이는 무의미) | AWT "Consume 3 Endurance Charges", 10개 상한, 0.5.0 "150% of socketed Attack time" 간격. 지면 분쇄 "Limit 6 Spikes", 함성으로 파쇄. Earthquake 없음. Fire Attunement는 0.5.1 L61로 "Gain 25% of Damage as Extra Fire Damage"로 문구 변경. 제작자의 0.5.5 계획(Discord)은 Hateforge 대신 **선대의 유대(Ancestral Bond)** "Your Totem Limit is doubled / No Charge requirement for placing Totems / Totems reserve 75 Spirit each"(0.5.0 L790)로 3충전 관문을 지우고 AWT + 지면 분쇄 + 함성 파쇄를 쓰는 것 — 관문은 토템당 정신력 75(제작자 발언 + 사실 텍스트, 조합 미검증) |
| 버프/기타 | 주운 판금 → Prolonged Duration II · Cannibalism I · Vitality I; Charge Regulation → Uhtred's Exodus; 선대의 혼백 → Brutus' Brain · Magnified Area II · Maim · Pin III · Blind II; 비취에 갇힘 → Physical Mastery · Prolonged Duration II · Mobility; 방패 들기 → Mobility · Steadfast II | 유효 | Charge Regulation은 0.4.0에서 Frenzy 줄이 "more → increased"로 |
| 아이템 | **Hateforge**(장갑), **목 죄이는 명령(Constricting Command)**("Require 5 fewer enemies … 4 fewer also works"), **별의 보석(Astramentis)**, **허무의 산물(From Nothing)**(Avatar of Fire 반경 → 포효하는 함성), **어둠 저항(Against the Darkness)**(poe2db/kr), 루비 ×2(재생 6%·방어도 15%·함성 속도·힘%), Flanged Mace(힘 +31 / 킬당 생명력 29 / 추가 물리 15% / 토템 보유 시 41%), Massive Greathammer(+5 근접 레벨 등), Tawhoan Tower Shield(막기 25%, 추가 물리 감소 8%), Warlord Cuirass(생명력 8%), Vaal Greaves(MS 35%), Amethyst Ring ×2(회피 +203, Iron Reflexes용), 유니크 호신부 **도끼의 추락(The Fall of the Axe)** / **통과의례(Rite of Passage)**(poe2db/kr 표기, 붙여 씀) / For Utopia(한국어명 미확인) | 사망/미확인 | Constricting Command 현재 롤 "Require (2—4) fewer enemies" → "5 fewer"는 범위 밖(사실). Hateforge 현재 "Gain a random Charge on reaching Maximum Rage, no more than once every (3—6) seconds / (-10—10) to Maximum Rage" |
| 각인 | Fortified Location(한국어명 미확인, "attack damage per summoned totem" — 제작자 발언) | 미확인 | — |
| 트리 | Main −24/123. export: 전직 4개; 키스톤 혈마법 + **Iron Reflexes**(Resolute Technique 없음); 세트1에 **포효하는 함성(Roaring Cries)**, Favourable Odds, Tactical Retreat; 노터블 Thrill of Battle, Paranoia, In the Thick of It, Titanic, Guts, Endurance, Skullcrusher, Overheating Blow 등 | 사망 | 포위 노드 묶음은 0.4.0 L108로 "최소 1명 필요". 포효하는 함성 poe2db "minimum of 10 Power"(GGPK 0.5 raw 20 — 표시 규칙 미해결) |
| 지침 | "hold in your Seismic Cry key and tap the Ancestral Warrior Totem key"; "Buy or craft any lvl Earthshatter gem with +1 level from corruption, then upgrade to level 20" | 사망 | — |

### 5.5 변형 공통 — 가이드 내부 모순(사실)

1. 개요 "Endgame variant utilises Ancestral Warrior Totem with Earthshatter"(E:66–69) ↔ Endgame 젬 목록에 AWT 없음(Uber만).
2. Second Wind III "removed"(20.12.2025) ↔ Endgame 보강하는 함성에 오늘도 소켓.
3. 어둠 저항 "no longer viable"(0.2.0 노트) ↔ Uber 주얼 슬롯에 존재.
4. 0.3.0과 0.3.1 블록 날짜가 둘 다 "24.08.2025".
5. Endgame 충격파 토템은 Overabundance I, Starter/Uber는 II — 설명 없음.
6. 세트2 아이템 거래 링크가 전 변형에서 한손 철퇴 검색으로 연결(mobalytics 링크 생성 문제).

---

## 6. 하드코어 관점

### 6.1 방어층 — 0.5.5 현재 텍스트(사실) 기준

| 층 | 현재 텍스트 / 값 | 빌드에서의 위치 | HC 메모 |
|---|---|---|---|
| 막기 상한 | 기본 50%(0.3.0 "Player, Minion and Monster base Maximum Block chance is now 50% (previously 75%)", poe2db Version_0.3.0 L212 — 레포 캐시는 0.4.0부터라 poe2db 버전 페이지가 근거); **거북이 호신부** "You take 20% of damage from Blocked Hits / Maximum Block chance is 75%" | 0.4 가이드 전직엔 거북이 호신부 없음(Warcaller's/Answered/Jade/Wooden). 0.3 영상 "We no longer go for block … it's quite easy to cap block. So [Renly's] training isn't needed" BO [15:25–16:09] | 50%로 굴린다는 뜻. 0.5.0 막기 노드 상향(Core of the Guardian 30%, Covering Ward 12%, Wide Barrier 30%)은 미사용 옵션 |
| 렌리의 훈련 | "Gain 35% Base Chance to Block from Equipped Shield instead of the Shield's value" | 0.1 사용, 0.3부터 탈락 | 0.5 워브링어 Paquate 변형(Xeph)은 다시 채택 |
| 스발린 | 막기 26%, "Chance to Block Damage is Lucky", "You take (0—20)% of damage from Blocked Hits", "+(50—100) to maximum Runic Ward"(0.5.0 신규 드롭만), Cast on Block "Supported Skills Cost nothing" | 0.1~0.3 핵심, 0.4 슬롯엔 없음. 젬링 포크 탱크판이 채택 | 0.5 AWT 워브링어 Sesul: "the block … is at 82% with that lucky block shield" https://youtu.be/uNiZjFMe5EM?t=306 [5:06] |
| 나무 벽 | "20% of Damage from Hits is taken from your nearest Totem's Life before you" | Endgame/Uber 전직 | 토템이 없으면 0. 토템 생명력 = 젬 레벨(FAQ E:493–497) + Hardy Totems II "50% more maximum Life" |
| 비취의 전승 | Jade 1스택/초, 스택당 물리 추가 감소 1%, 최대 10 | Starter+ 전직 | 제작자(0.3): "Unlike armor, this always applies no matter how big the hit" BO [4:56–4:59] |
| 마그마 장벽 | "Grants 25% increased Block chance" + 완전 충전 후 방패를 든 상태의 다음 막기 1회에 Magma Spray 발동 + 인내 충전 1(매 막기가 아님) | 전 변형 | 정신력 30. 레벨 24 실캐릭은 이것 하나로 정신력 소진 |
| 주운 판금 | "4% more Armour per Scavenged Plating / Maximum 10", 방어구 완전 파괴 시 스택 | Starter+ | 지진 함성 강타 기절 → 격파의 일격 50% 파괴 → 스택(제작자 설명 BO [13:48]) |
| 방어도 | 0.5.0 L1180 "approximately 33% more Armour [at 65], tapering down to 15% at level 80+" | Endgame "Armour" 우선순위 4위 | 상향 |
| 룬 수호 | 0.5.0 L83 "kicks in once you reach 1 life … regenerates independently of your life"; 55 미만 방어구는 무손실 | 가이드 무언급(0.4 시절) | 0.5.5는 4막 Runeseeker 퀘스트로 해금(L219). 레포 TANGJEONG/ARSERINA 문서가 "룬 수호"로 표기(젬링 문서엔 없음) |
| 가호(Guard) | 보강하는 함성 "Grants (2—92) Guard for every 5 enemy Power in range, counting up to 20 Power", 4초 | Starter+ | Redblade Banner로 위세 2배 → 백몹에도 최대 가호(제작자 D1 [10:39]) |
| 생명력 회복 | 다급한 부름 2%/함성; 상황 반전 50%(레어/유니크 강타 기절); 킬당 생명력(세트1 철퇴, Rebirth Rune 15/25/35); Ancestral Mending 1%/s(토템 보유); Second Wind III **불가**; 0.5.5 Soul Core of Jiquani "Recover 5% of Maximum Life on Kill"(무기) | FAQ "How do you recover life with Titanrot Cataphract?"(E:473–487) | 0.5.4b L187의 수정 대상은 Vorana's Carnage 접미("Recover (4—5)% … when you use a Warcry")이고, 다급한 부름(2%)은 문구가 달라 해당 없음으로 보인다(강한 추정, 8.1 Q10). Skadoosh는 둘을 합쳐 "7% every time you warcry"를 노린다(0.0절 1:21:06) |

### 6.2 HC 특유 위험 — 근거 붙임

- **Titanrot Cataphract(거신부패 비늘 갑옷).** "(400—500)% increased Armour / (15—30)% increased Strength / 10% reduced Dexterity / 10% reduced Intelligence / **You have no Life Regeneration**"(0.1.1 이후 무변경, 사실). 가이드 "Don't equip Titanrot Cataphract unless you like living on the edge or until you can sustain life via the ways mentioned in the FAQ"(S:48–50). 0.3의 사용 근거였던 Second Wind III 회복은 죽었다. 힘은 0.5에서 타락한 피의 기본 피해 입력이 아니다(사실, 결론 4); 힘 파생 증가가 닿는지는 Q1(미확인). 따라서 HC에서 이 갑옷의 확실한 가치는 생명력(힘×2, 거인의 피면 ×1)과 방어도다(추정). HC FR 11시간 래더에서 Titanrot 착용 22명, 0.5.5 SC 180명(사실).
- **함성의 생명력 비용.** 혈마법 아래 지진 함성 lv20 = 85 마나 상당, lv11 = 49(poe2db 표; lv10 = 46. 0.1 영상의 "49 life"와 일치). 0.5는 레벨을 올려야 하므로 비용이 함께 오른다. Efficiency II(비용 감소; 0.1 영상의 "Inspiration"과 같은 자리이나 개명 근거는 팩에 없음)는 그래서 Starter/Endgame/Uber 3개 변형에 있다(Leveling 변형의 지옥불 함성 링크엔 없음). 0.1 우버 수치 "72 → 49 → 42 life" gWQ [6:48].
- **파콰테의 맹약 비용.** "Supported Skills Cost 10% of maximum Life for each time they have been used or Triggered Recently, up to a maximum of 30%"(KR: 최근 4초). 워브링어 가이드엔 없지만 0.5 워브링어 변형 대부분이 쓴다(7장). 제작자: 예전엔 "basically killed you instantly"(Lich 우회), 지금은 "the cost is something you have to pay" https://youtu.be/Jj2eKr4Ez-A?t=908 [15:08–15:11].
- **스왑 중 무방비.** 0.1 "we don't have a shield which means we're not tanking anymore" https://youtu.be/KsK6tNjh50s?t=1328 [22:08–22:12]; 0.3 CA "We want to ideally be as little time as possible in weapon set two" https://youtu.be/F6ou4sj0uZE?t=421 [7:01]. 0.5.5 L389/L393로 "스왑 없이 세트2 스킬" 편법은 없다 — 세트2 스킬을 쓰면 스왑이 실제로 일어나고 그 시간은 노출된다.
- **탈출 수단 약화.** 0.5.1 "Logging out and in again now preserves your heavy stun buildup…"; 0.5.4b "Fixed a bug where you could create a Portal to Town while being hit." → 강타 기절 상태에선 로그아웃도 답이 아니고, 피격 중 포탈도 안 된다.
- **못 막는 것.** 0.5.2 "Siora, Blade of the Mists … Their Cyclone skill is now unblockable (red flash)". 0.1 거북이 호신부의 "block AoE" 특권은 0.3부터 기본이 됐다(제작자 BO [15:31–15:43] "applies against all damage instead of just projectiles … even the AoE ground effects … now we also get by default").
- **리그 메커닉.** 0.5.5 캠페인 전 지역 Ritual + 막당 2회 보스 효과 군집(L33/L35) — 오늘 핫픽스 4에서야 "Lost-men Zealots could be invulnerable when revived in ritual" 수정. 0.5.0 "Each empty tablet slot now contributes to the amount of random non-tablet spawned league content"(L448).
- **HC 사망 사례(제작자 발언).** Sesul(0.5 AWT+지면 분쇄+Cast on Block 워브링어): "was running a lot of Simulacrums on hardcore with this. I did just die, so now I'm on softcore" https://youtu.be/uNiZjFMe5EM?t=396 [6:36], 사망 1건은 "200 delirium map with the expedition mechanic". mattsu "HCSSF Corrupting Cry/Totems Warbringer - Zero to Hero Ep 1"(2025-10-01, 0.3)은 Ep 2 미업로드(이유 미확인).
- **레벨 24 실측의 약점(사실).** 최소 최대 피격 740(화염), 저항 −5/12/4/11(패널티 적용치), 막기 33%, EHP 1,035. 가이드 레벨링 변형의 "Resistance (elemental minimum total 60-75%)"까지 거리가 가장 크다.

### 6.3 Skadoosh가 HC에 대해 말한 것

- 7개 자막 파일에서 "hardcore"는 2회(아래 두 인용, 둘 다 스트림 예고), "HC"/"SSF" 토큰은 0회(사실). 자막 영상에서 방어 우선 발언은 두 곳: 0.4 "you have to be in [bear] form with a talisman. And is that better than having a shield? I don't think so. Defensively anyway." https://youtu.be/CoskGFogxhA?t=484 [8:04]; 0.5 "The total tank is good though" [13:53]. 방송 1일차 전사(0.0절)엔 더 있다: 0:40:03 "Problem is the defenses … I don't think that's enough, I think I need much more armour", 0:15:50 "it's a bit more hardcore-oriented. It's slower", 1:26:23 "I'm playing hardcore, which I'm definitely not prepared for", 1:32:00 "I think I've yet to play hardcore to the endgame".
- 0.3 개요 끝: "I'm streaming this and possibly my next future build or maybe even hardcore at [skadoosh_c]" https://youtu.be/BLc0SguI0gk?t=1652 [27:32–27:40]; CA 끝: "I'll be streaming this build and maybe my next build or who knows something else hardcore maybe" https://youtu.be/F6ou4sj0uZE?t=1261 [21:01–21:06].
- Discord #build-help(제작자 발언): 09-02 01:29 "technically it's all untested, and i'll be playing HC at least at teh start. I'll probrably stream it though but semi-casually"; 09-02 01:15(HC에서 죽으면 우버 엔드게임까지 밀 거냐는 질문에) "Yeah, I doubt I'd reroll in HC. Unless I get another idea for a build"; 09-03 19:40 "Current plan is hardcore trade, warbringer totem shouter. So my classic build with new coat of paint"; 09-03 20:30 "Should be really tanky and have really good damage"; 09-03 19:47 "the build won't be meta... trust me lol. It's going to be too slow I think."
- 커뮤니티 탭(10개월 전, PoE1 3.27): "Since it's HC, defence and slow gameplay will be more important" — PoE1 하코 트레이드 스타트 경험(사실).
- 가이드 태그 `HC`, 레벨링 가이드 태그 `HC`/`SSF`, 0.1 포럼 "Hardcore viable". 오늘 스트림 제목 "HC OG Warbringer Warcry Totems".
- 0.5.5 복귀 이유·HC 선택 이유는 Discord 발언(위·결론 5)과 방송 1일차 전사(0.0절: 3:57:19 "a league starter version … focuses more on totems … especially Ancestral Bond", 4:39:49 "I'm playing hardcore … to beat the game, do all the challenges on hardcore")에 있다. 그의 HC 경험은 본인 말로 얕다("yet to play hardcore to the endgame") — 6장의 HC 판단을 그의 검증으로 읽지 말 것.

### 6.4 0.5.x 몬스터·리그 변경 중 HC 방향(사실, 3장 요약)

↓ 위험: 룬 수호(0.5.0 L83), 이동 중 출혈 증폭 삭제(L530), 캠페인 후반 밀도 감소(L524), 강타 기절 축적 감쇠 정상화(L546), Geonor 너프(0.5.3), Elite Abyss/Harano 너프(0.5.1), Tor Gul 면역 창 삭제(0.5.4b), Omen of Resurgence 정상화(0.5.4), Ticaba 코어 치명 피해 −50%(0.5.5).
↑ 위험: 1막 Burning Dead 화염 피해(L1358), 빈 태블릿 슬롯 랜덤 콘텐츠(L448), Ancient Modifiers 40+(L162), 에센스 팩 팩 크기 적용(L1350), Delirium 보스 항상 100%(L214), 로그아웃 강타 유지(0.5.1), 피격 중 포탈 불가(0.5.4b), 캠페인 Ritual 보스 웨이브(0.5.5 L37).

---

## 7. 다른 제작자 변형과 래더

### 7.1 제작자별 변형 (시간순)

| 제작자 | 시기 / 소스 | 골격 | 이 빌드와의 관계 |
|---|---|---|---|
| **Steelmage** | 2024-12-13/14, evMdvGmK-aI · 2gVDTaShOko | 0.1 Skadoosh 판 그대로 | Skadoosh 0.1 포럼·영상이 "Steelmage's explanation video with better audio"로 링크. Skadoosh: "steel Mage a streamer who's also running this build does not have this Jewel [어둠 저항] and he's doing just fine" https://youtu.be/KsK6tNjh50s?t=1242 [20:42–20:47](주얼 소개는 [20:15]) |
| **Cptn Garbage (Maxroll)** | 최종 2025-04-04, 0.2.0 — https://maxroll.gg/poe2/build-guides/corrupting-cry-warbringer-guide | 세트I 지진 함성 + Corrupting Cry + Magnified Effect; 세트II AWT + 지면 분쇄 + Bloodlust; 전직 Warcaller's Bellow → Greatwolf's Howl → Renly's Training → Turtle Charm; "functional at Level 41"; HC "Not explicitly evaluated" | 0.1/0.2 설계의 스냅샷. 0.3 이후 미갱신. Skadoosh: "Max roll have taken over and now highlighted my build on their website" https://youtu.be/KsK6tNjh50s?t=17 [0:17–0:21] |
| **mas0ny1** | 2025-04-10/13, RR4yjWrZrLU · zhu72GQ7SGQ (0.2) | Corrupting Cry Rolling Slam Totem; Battershout 실험("Exploit Weakness does in fact not work with battershout") | Skadoosh 커뮤니티 탭이 직접 추천한 0.2 업데이트 |
| Cestarix | 2025-01-11, Y5o1W7dp0Z0 "[SSF HC] Corrupting Cry + Totems Warbringer - Arbiter of Ash +4" | "build stolen from Skadoosh (@SkadooshPoE) and Steelmage" | 0.1 SSF HC 실증(제작자 발언) |
| mattsu | 2025-10-01, -_F80kwPK_U "HCSSF Corrupting Cry/Totems Warbringer - Zero to Hero Ep 1" (0.3) | — | Ep 2 없음 |
| Kris Droverson | 2026-02-01, kFO8ad8FsS8 "Infinite Warcries \| Warbringer Build (0.4)", PoB poe.ninja/poe2/pob/18f24 | — | 0.4 함성 워브링어 |
| Palsteron | 2025-12-22, VH6K2LVUfvk "Ancestral Warrior is Worse Than it Seems / How a Hidden Stat Ruined a Build" (0.4) | AWT 숨은 딜레이 분석 | 0.5.0 L926(0.6초 → 공격 시간 50%)의 배경(추정) |
| **Xeph** | 2026-06-21 GuXt751YR1M(25:41) · 07-11 4wjm9Wt-ySM; PoB pobb.in/fle8R39Dmmhh, Maxroll 8iac0r0w; 0.1부터 매 리그 Corrupted Blood 워브링어 | 워브링어 lv95: **보강하는 함성 L20 + 파콰테의 맹약 + Swift Affliction II + Brutality II + Rageforged II + Physical Mastery**; 지진 함성 L11(격노용); 공명하는 방패(방어구 파괴); 거인의 피; 전직 Warcaller's Bellow > Renly's Training > Turtle Charm > Jade Heritage; Prism of Belief(믿음의 분광기), Undying Hate, Reverie; **토템 없음** | "not the strongest build … Skadoosh and Josiah Yeet have both done versions on gemling" https://youtu.be/GuXt751YR1M?t=177 [2:57]. 버그 주장: 뒤틀린 맹약이 호스트 젬보다 1레벨 낮음("doesn't count the plus one level from corruption") https://youtu.be/GuXt751YR1M?t=810 [13:26–13:30]; 07-11 재확인 https://youtu.be/4wjm9Wt-ySM?t=294 [4:54]. "Every time you apply a stack of corrupted blood, it refreshes the duration of all stacks of corrupted blood" https://youtu.be/GuXt751YR1M?t=844 [14:01–14:06](제작자 발언 — 갱신 규칙의 유일한 언급) |
| **Larrymoreorless** | 2026-06-10, 257IVqU-2jg "Yell Damage Warbringer Build Guide 0.5", PoB maxroll lnuae0pp | **지진 함성 L21 + 파콰테의 맹약 + Magnified Area II + 메아리치는 함성(Echoing Cry) + 구타하는 고함(Battershout) + Swift Affliction II**; 지옥불 함성 + Raging Cry + Echoing Cry + Battershout; 단일 대상 Shield Wall + Nebuloch(세트2); 전직 Warcaller's/Renly's/Anvil's Weight | 지진 함성 스팸 계보의 0.5 후손. 피해 = 시체 폭발 + Battershout + gain-as-extra. "Since none of our war cry damage engines really scale meaningfully off gem level, I value huge gain as extra roles" https://youtu.be/257IVqU-2jg?t=770 [12:50]; "Corrupting cry doesn't benefit from this [gain-as-extra] because that is a debuff and not a hit" [13:31]; "delirium mobs don't leave corpse behind" [24:01] |
| TomorinZ (태국) | 2026-06-16, i-5PFopgcpo; Maxroll 2i4l1e0y | 보강하는 함성 L22c + 파콰테의 맹약 + Inspiration II + Brutality II + Swift Affliction II + Physical Mastery; 공명하는 방패 방어구 파괴 | Xeph와 같은 엔진 |
| Macsen | 2026-06-07, uYCmXw_CQj0(63초) | "big enjoyer of Skadoosh's build but didn't like playing with Totems so I tried to find other options for Single target"(설명란); Battershout | 자막은 무관한 디스코드 대화. 채널 유일 PoE 영상 |
| **Sesul** | 2026-07-11, uNiZjFMe5EM "POE2 0.5 Ancestral Warrior Totem COB Grim pillars Warbringer HC viable" | AWT + 지면 분쇄 + Cast on Block(스발린) + Grim Pillars; 함성은 스파이크/기둥 파쇄용; Flesh Crucible로 선대의 유대(Ancestral Bond); 거인의 피 | 0.5에서 AWT+지면 분쇄+지진 함성을 워브링어에 올린 유일한 제작자 — 타락시키는 비명 없음, HC에서 사망 후 SC(6.2). "Couldn't find anything online" [17:54] |
| Zepyh | 2026-06-24, d7OOXi-WdgM; Maxroll l1b2if0h | **Smith of Kitava** AWT L18 + Sunder + Urgent Totems III + Rapid Attacks II + Brutality III + Heavy Swing | AWT는 살아 있으나 Smith·Sunder로 |
| **POEGuy** | 2026-05-27, OH2MM7RlrWA "0.5 GRENADE TOTEM WARBRINGER STARTER"; **0.5.5**: Tck6oxQ_qEQ(09-02, "POEGUY's 0.5.5 STARTER // CHEAP, LAZY, TANKY"), obkVjAMTaHk(09-04, "Cheap, Tanky, One-button 0.5.5 league-starter // A well-tested build since Patch 0.3", 자막 `subs_txt/poeguy_obkVjAMTaHk.txt`), 11.7h·9h 연습 VOD; 문서 poe-vault "Grenade Ballista Totems Warbringer Endgame Build"(0.4.0 태그, 06-18) · "Totems Warbringer Leveling Build"(0.5.0 태그, **09-03**) | 유탄 발리스타 토템(Mortar Cannon + Cluster Grenade, Voltaic Grenade), **함성 없음**("pure one-button"); 전직 응답받은 부름 → 나무 벽 → 비취의 전승 → 모루의 무게; 혈마법·방어도·나무 벽·Time of Need; 52레벨(4막 Tavakai 후) 석궁 전환 | 0.5 워브링어 다수파(7.2). **캠페인 레벨링 경로가 Skadoosh와 같다**(0.2.4). Skadoosh: "Ah, right. He did warbringer mortars / I'll be using ancestral warriors"(Discord 09-03 19:48) |
| Mirine (KR) | 2025-12-21/28, 2026-06-06/07 "Corrupting cry Warbringer 15T mapping" | 젬 목록 없음 | 0.4·0.5 1주차에 CC 워브링어를 굴린 한국 플레이어. 설명·링크 없음 |
| Breegin | 2024-12-13, 포럼 3628612 | Titan판(Hammer of the Gods + 출혈) | 0.1부터 포크된 기록 |
| 기타 0.5 스타터 리스트 | LexD 9FXJsaO-tFY(05-28), KaidGames2 ZpNDVdpL4co(06-05), Perra RRD-rkD1UnY(06-16; "Build 6: Evade Corrupting Blood Gemling by @SkadooshPoE"), Path of Dan, Massify | — | 어느 리스트에도 Corrupting Cry 워브링어 없음(사실) |

### 7.2 래더 (poe.ninja protobuf API 디코드, 2026-09-05 06:52 UTC, 사실)

| 리그 | 스냅샷 | 총원 | 워브링어 | 이 빌드 젬 | 읽기 |
|---|---|---|---|---|---|
| **HC Forbidden Rites** | 0646-20260905-31717(런칭 ~11h) | 2,658 | **13**(0.5%), 레벨 23–51, 생명력 500–1,482 | Corrupting Cry I/II · 파콰테의 맹약 · AWT **0**(젬 사전에 이름 자체가 없음); 지진 함성 5(워브링어 1); 충격파 토템 64; 대장간 망치 12; 지면 분쇄 13 | 워브링어 메인 스킬: Shield Wall 6, 보강하는 함성 4, 대장간 망치 2, 충격파 토템 2, 지면 분쇄 1. 전직: Warcaller's Bellow 8, Answered Call 4, Anvil's Weight 3, Renly's 1. 지진 함성을 낀 워브링어 1명(lv41, 생명력 1,006)은 지면 분쇄 + 대장간 망치 + Titanrot + 메기노드 + Warcaller's/Anvil's — Skadoosh 레시피를 따르는 타인(BehemothRage 또는 simadenuevomazas). **SkadooshShoutedHard 24 · 733 · EHP 1.0k**가 사이트 정렬(레벨순) 기준 13명 중 11위(레벨 24 동률 Ingrid_BC 500보다 생명력 233 높음, 뒤에 PEPEGATOR_ABOBA 23) |
| Forbidden Rites SC | 0645-20260905-25043 | 35,141 | 250(0.7%) | Corrupting Cry I 6 · II 2(워브링어 2·1) · 파콰테 0 · 지진 함성 15 | 워브링어 메인: Shield Wall 103, Volcanic Fissure 68, 보강하는 함성 48, 충격파 토템 39 |
| SSF FR / HC SSF FR | — | 3,296 / 1,138 | 17 / 14 | 지진 함성 4 / 3; HC SSF에 Corrupting Cry II 1(워브링어) | — |
| **Runes of Aldur (0.5 SC, 14주)** | 0521-20260905-08347 | 124,199 | 516(0.4%) | Corrupting Cry II 581(워브링어 29) · I 13(워브링어 1) · 파콰테 641(워브링어 26) · AWT 250(워브링어 16) · 지진 함성 1,276 · Hateforge 446 · Svalinn 3,617 | CC II 581명은 대부분 젬링(Colossal Capacity/Hulking Form 188). 워브링어 29명의 메인: 지옥불 22 / 보강 16 / 지진 10; Answered Call 7/29; AWT 2/29. AWT 워브링어 16명은 Ancestral Spirits 14 / Sunder 11 메인, 지면 분쇄 4. 전체 워브링어 516명 중 Ancestral Spirits 346 · Cluster Grenade 312 → 2/3가 수류탄 토템 |
| HC Runes of Aldur | 0527-20260905-33685 | 12,372 | 100 | CC II 13(메인 보강하는 함성 12) · 파콰테 8 · AWT 9 · 지면 분쇄 6 | HC 0.5 워브링어 CC = 보강하는 함성 + 파콰테/CC II, Answered Call 1/13 |

래더 결론(추정): "지진 함성 + 타락시키는 비명 + AWT 스왑"은 0.5 본 리그에서도 발자국이 거의 없고 0.5.5 HC 11시간엔 0이다. 살아남은 두 갈래 — (a) 보강하는/지옥불 함성 + 파콰테의 맹약/CC II + 근접 레벨 스택 워브링어, (b) 타락시키는 비명 없는 AWT/Sunder·수류탄 토템 워브링어. Skadoosh는 타락시키는 비명 + AWT 스왑을 워브링어에 다시 올리는 유일한 공개 제작자인데, 본인 Discord 발언으로는 (a)의 엔진(보강하는 함성 + 근접 레벨)을 (b)의 토템(AWT + 선대의 유대)과 합치는 형태이지 0.4 가이드의 지진 함성·힘 스택 원형이 아니다(제작자 발언, 미검증).

### 7.3 커뮤니티 판정(사실: 인용)

- 공식 포럼 3938368 "Corrupting cry is dead"(2026-05-31 → 08-30, 11개 글). OP MightyMouth-DFT: "it scales (barely) with gem level … aside from fortifying cry none of the warcries have tags that you can scale their gem level … there's no way to check its damage increases". Cacheperl(06-05): "you might as well ignore corrupting cry completely and just use the lineage version (Paquate's Pact) … **Either way, the multiple-warcries-per-second build is dead. Maybe intentionally so.**" Erexonvayne(08-30): "The 287 base damage at level 20 is already 40% more than before, assuming you get a reasonable 830 strength … makes me want to try it for 0.5.5 as my sole clear + explodes, then use the good Totem + Forge Hammer combo." Taistelija(08-30): 지진 함성 최대 레벨 계산 "Base gem = 20 / corruption = +1 / prism of belief = +3 / amulet desecration = +1 / dialla's desire = +1 / physical mastery … = +1 / Total = 27".
- 포럼 3908963(2026-01-28, 0.4.0d 시기 버그 리포트 — 0.4.0c 12-19, 0.4.0d 01-15, 0.4.0e 02-10): "The modifier 'Damage with Warcries' only affects corrupted blood applied by corrupting cry if the warcry itself can deal damage … When Fortifying Cry … inflict corrupted blood, the modifier does not apply." — 0.5 발동형에도 이어지는지 아무도 검증 안 함.
- 포럼 3822078(Early Access Feedback, Binary_Undead, 2025-08-03, 0.2/0.3 경계): "warcry corrupting cry build on Warbringer ... the damage is about 20,000 a second. this turns most the end game bosses(t16 and above) and some tough rares into battles of attrition ... the problem stems from a lack of base damage given from the support gem" — 0.5 재설계 전의 단일 대상 불만(`community_raw/forum_3822078.txt`).
- Maxroll 0.5.5 League Starter tier list(2026-09-03): 워브링어 항목은 "Shield Wall Warbringer"(A) 하나. Corrupting Cry 워브링어 없음. Maxroll 0.5.5 패치노트 페이지도 함성/토템/워브링어 언급 0.
- Skadoosh 커뮤니티 탭: 최신 글이 ~8개월 전(0.4 런칭: "I am going to start stream over at @Skadoosh_c on twitch a bit before league start"). 0.5/0.5.5/워브링어 복귀 글 없음. 0.4 땐 커뮤니티 탭에도 예고했으나 0.5.5는 YouTube 글 없이 Discord 핑(09-05 01:30 KST) + Twitch 방송(런칭 1.5h 전)뿐이다.
- Reddit: 봇 차단(403)으로 수집 실패 — "없다"가 아니라 "못 봤다".

---

## 8. 미확인 · 열린 질문 · 다음 확인 포인트

### 8.1 게임 데이터에서 못 닫은 것

| # | 질문 | 현재 근거 | 확인 방법 |
|---|---|---|---|
| Q1 | 타락한 함성이 힘으로도 스케일하는가 | 스탯 블록에 힘 없음(poe2db); "modifiers to warcry damage also apply"; 핫픽스 3 "most damage modifiers"; Skadoosh "Maybe"; 포럼 3908963(0.4.0d 시기)은 함성 자체가 피해를 줄 때만 "Damage with Warcries" 적용 | 인게임 툴팁 비교(힘 장비 탈착) 또는 GGPK 0.5.5 `triggered_corrupting_cry` ActiveSkillTypes [8,30,36,49,82,114,26,34] 디코드 |
| Q2 | 타락한 피 갱신 규칙(새 스택이 기존 스택 지속을 갱신하는가) | 가이드 "Each additional stack refreshes all previous stacks"(제작자 발언); Xeph "it refreshes the duration of all stacks"(제작자 발언); poe2db·패치노트 무언급 | 인게임 테스트 |
| Q3 | 타락한 함성 트리거당 스택 수 | 뒤틀린 맹약만 "Inflicts 5"; 타락한 함성 무표기 → 1 추정 | 인게임 |
| Q4 | Xeph의 "1레벨 낮게 발동" 버그(뒤틀린 맹약)가 0.5.5에 남았는가 / 타락한 함성도 같은가 | 0.5.5 노트에 언급 없음 | 인게임 |
| Q5 | "Seismic Cry gives double the power" 버그 잔존 | 0.4.0–0.5.5 캐시에 수정 문구 없음; 가이드 Uber "it seems to give double rage" | 인게임 |
| Q6 | 충격파 토템이 세트1로 돌아가도 남는가 / 세트2 패시브(+1 토템)로 올린 개수가 유지되는가 | AWT만 0.3.0c 노트(poe2db Version_0.3.0c L47)로 잔존 확정; 0.5.5 L389/L393 이후 세트 경계가 엄격해짐 | 인게임 |
| Q7 | AWT 소켓 강타의 실제 공격 시간(0.5.0 L926 손익 1.2초 — 0.3.0 "Socketed Mace Skills now have 50% less Attack Speed"가 0.4까지 남아 있었다면 손익분기 자체가 없고 순수 버프) | 지면 분쇄 80% AS × 양손 철퇴 기본 APS; 0.4 시점 AWT 스탯 블록(50% less 유무) | PoB 계산 + poe2db 0.4 시점 스냅샷/Palsteron 영상 대조 |
| Q8 | 거북이 호신부 30%→20% 변경 패치 | 라이브·GGPK 0.5 모두 20; 0.3.0b/c·0.3.1·0.4.0–0.5.5 캐시에 없음 | poe2db 버전 이력 재조회 |
| Q9 | 포효하는 함성 최소 위세 10(poe2db) vs GGPK 0.5 raw 20 | 표시 규칙 미해결 | Stats 테이블 |
| Q10 | 0.5.4b "Recover X% of maximum Life when you use a Warcry" 수정의 소스 아이템 | **강한 귀속(추정)**: Vorana's Carnage(투구 Augment, "Can roll Berserking modifiers")의 접미 "Recover (4—5)% of maximum Life when you use a Warcry"(Lv75; Lv45 티어는 (2—3)%)가 poe2db에서 이 문구를 가진 유일한 항목이나, poe2db가 유일성을 단언하진 않고 GGPK 추출본엔 스탯 텍스트가 없다. 다급한 부름은 별개 문구("Recover 2% of maximum Life and Mana"). Skadoosh 방송 1:21:06가 이 접미를 이 빌드에 원한다고 밝힘(0.0절) | 인게임 툴팁으로 0.5.4b 이후 "함성에만" 작동 확인 |
| Q11 | Overabundance II의 +Limit 값 | I만 조회(+1 / 50% less duration) | poe2db |
| Q12 | "increased Damage while you have a Totem"(Ulaman abyss prefix)와 루비 "2% increased Strength"의 0.5.5 이벤트 리그 수급 | poe2db 가중치 비공개 | 트레이드 검색 |
| Q13 | 0.5 캠페인 퀘스트 보상(Venoms/Tattoos/Pillars)이 가이드 문구대로인가 | 가이드 퀘스트 블록 전부 "Not Specified", 0.5.0 노트 캠페인 재편 | 인게임 |

### 8.2 Skadoosh 본인에 대해 못 닫은 것

| # | 질문 | 다음 확인 포인트 |
|---|---|---|
| S1 | Corrupting Cry I 입수 시점에 어느 함성에 꽂는가 — 제작자 답: "Guide is outdated / I'll be using fortifying like Gemling"(Discord 09-02 01:25, 미검증). 가이드대로 지진 함성 + Warcaller's Bellow 리스펙은 본인 계획이 아니다 | poe.ninja 재스냅샷: `passiveSelection`에서 노드 39411의 형제(Warcaller's Bellow / Wooden Wall / Renly's Training), 젬 목록에 보강하는 함성·Corrupting Cry I·근접 레벨 장비 등장 여부 |
| S2 | 스왑 세트에 양손 철퇴가 있는가 | 재스냅샷 `items[]`에 `Weapon2` 존재 여부 |
| S3 | 5월 "wouldn't recommend" 판정을 뒤집고 HC로 이 빌드를 고른 이유 — **해소(제작자 발언)**: Discord 09-02/03("leaguestart able version of corrupting cry / doesn't require any uniques", "only rare gear and the build won't be meta") + 방송 3:57:19("a league starter version … focuses more on totems … especially Ancestral Bond") + 0:56:56("[Ancestral] Bond allows me to do this, because the build didn't really work") + 4:39:49(최종 형태). Rallying 코어는 그가 Corrupting Wings 맥락에서 칭찬한 것이라 복귀 이유엔 안 넣는다. 남는 것은 실제 성능 | 0.0절; 이후 방송·ninja |
| S4 | "total tank" vs "totem tank" | https://youtu.be/Jj2eKr4Ez-A?t=833 음성 확인 |
| S5 | mobalytics 가이드가 [0.5.5]로 재태깅되는가 / 변경 로그에 0.5 항목이 붙는가 | 프로필 "Updated on" 감시(현재 Sep 5, 2026인데 내용 무변경) |
| S6 | 젬링 포크 지식(보강하는 함성 + 레벨 스택)을 워브링어에 이식하는가 — 제작자 답: 그렇다("use fortifying and get melee levels again", "I'll be using ancestral bond for ancestral warrior totem", Discord 09-02/03, 미검증). 파콰테의 맹약 여부는 발언 없음 | 재스냅샷에서 보강하는 함성·근접 레벨 장비·AWT·선대의 유대(키스톤)·거인의 피·Prism of Belief 등장 여부; 정신력(토템당 75) 확보 경로 |
| S7 | Rallying/Quaking/Automation 소울 코어 채택 여부 | 재스냅샷 무기 룬 소켓 |
| S8 | 메아리치는 함성(Echoing Cry)을 워브링어에도 쓰나(1:02:25는 젬링 문의 답), Howling Beast를 트리로 가나 각인하나, Vorana's Carnage 투구·혈마법 시점 | 재스냅샷 젬 목록·키스톤·투구 Augment; 다음 방송 |

### 8.3 이 문서의 한계

- mobalytics 페이지 텍스트에는 패시브 트리가 없다. 트리는 export payload(SHA-256 검증)에서 복원했고 노드 이름은 **0.5 GGPK**로 매핑했다(0 unknown). 0.4 트리 위치·0.5.5 수치는 대조 안 됨. mobalytics의 "Main: −12 / 123" 카운터는 export 노드 수와 정합하지 않아 총 포인트를 산출하지 않았다.
- 제작자 본인의 PoB 링크는 어느 소스에도 없다. 실캐릭 PoB는 poe.ninja가 생성한 것이다.
- 0장은 본문 완성 후 별도 적대검증(1 high · 2 medium · 12 low)을 받아 전부 반영했다(2026-09-05): POEGuy와 "캠페인 루프 동일" 과장 → 1~2막 초입까지로 축소, 1–10 밴드 세트 배정은 가이드에 없음, Efficiency II는 3개 변형만.
- 영상 인용은 전부 자동 자막이다. 고유명사는 GGPK/가이드로 교정했고, 수치는 자막 그대로다.
- 한국어명은 poe2db.tw/kr 제목과 레포 문서에서만 가져왔다. 미확인 표기가 붙은 이름은 번역하지 않았다.
- 4h42m VOD는 자막이 없어 채팅 리플레이 + 0:00–1:32 연속 전사 + 이후 질문 구간 국소 전사(Whisper large-v3-turbo, 로컬)로 읽었다(0.0절, `scratchpad/twitch_findings.md`); 1:32 이후 게임플레이 잡담은 대부분 전사하지 않았다. 전사문은 읽기 쉽게 다듬은 것이라 축자 인용이 아니다. Reddit·mobalytics 타 제작자 페이지(Cloudflare 403)는 읽지 못했다.

---

## 출처

| 출처 | URL / 파일 | 날짜 | 용도 |
|---|---|---|---|
| mobalytics 가이드 [0.4] | https://mobalytics.gg/poe-2/builds/corrupting-cry-warbringer-skadoosh — 캡처 `scratchpad/mobalytics/warbringer_{endgame_full,starter_section,leveling_section,uber_section}.txt`, export digest `extracts/_mob_export_digest.txt` | 캡처 2026-09-05 | 변형별 젬·장비·트리·FAQ·How it Works·Changelog |
| mobalytics 레벨링 가이드 | https://mobalytics.gg/poe-2/builds/skadoosh-warbringer-leveling-41 — `scratchpad/mobalytics/leveling_1_33_full.txt` 외 4밴드 | 2026-01-06 갱신 | 1–33 밴드별 스킬·팁 |
| mobalytics 젬링 포크 | https://mobalytics.gg/poe-2/builds/corrupting-cry-gemling-skadoosh; 레포 `Docs/2026-09-02_SKADOOSH_CORRUPTING_WINGS_GEMLING_0_5_5_GUIDE_DOC.html` | 2026-06-09 생성 | 계보·한국어 용어 |
| poe.ninja 실캐릭 | https://poe.ninja/poe2/builds/forbiddenriteshc/character/ITheCon-2183/SkadooshShoutedHard — `scratchpad/ninja_shoutedhard.json`, `extracts/_pob_export.xml` | 2026-09-04T23:16Z | 4장 전체 |
**7.2a poe.ninja 래더 API 의 조용한 함정(2026-09-06 실측).** `class`/`allskills`/`skills`/`keypassives` 에 **그 스냅샷 사전에 없는 값**을 넘기면 HTTP 200 으로 **에러 없이 필터를 무시하고 리그 전체를 돌려준다**. 실측: `hc-ssf-forbidden-rites&allskills=Paquate's Pact` → total 1,592 = 같은 오버뷰 무필터 total 1,592. "1,592명이 이걸 쓴다"로 오독하기 딱 좋다. **카운트를 적기 전에 무필터 total 과 같은지 반드시 볼 것.** 사전에 있는 값은 정상 동작한다(hc-forbidden-rites: `allskills=Shockwave Totem` → 72, `Corrupting Cry I` → **3**, 소프트코어 `Paquate's Pact` → 12).

**7.2b 문서 7.2의 '지진 함성 워브링어' 신원 확정.** lv41·생명력 1,006 은 **simadenuevomazas(Sima0-0979)** 다(고정본 `community_raw/ninja_q_hc-forbidden-rites_…Seismic%2520Cry.bin`, 메인 Forge Hammer+Earthshatter, Titanrot Cataphract + Meginord's Girdle, keypassives Warcaller's Bellow + Anvil's Weight). 지진 함성 워브링어는 있어도 **타락시키는 비명은 아무도 안 쓴다** — 두 계보가 이 리그에서 갈라져 있다.

| poe.ninja 래더 API | `https://poe.ninja/poe2/api/builds/<snapshot>/search?overview=<league>[&class=Warbringer]`(예: `0527-20260905-33685/search?overview=hc-runes-of-aldur`), 실캐릭은 `0615-20260905-10145/overview?overview=hc-forbidden-rites` — protobuf 디코드(`community_raw/`) | 2026-09-05 06:52 UTC | 7.2 |
| Twitch VOD | https://www.twitch.tv/videos/2865212551 — 채팅 리플레이 `scratchpad/twitch/chat_2865212551.json`(GQL VideoCommentsByOffsetOrCursor, 175건), 음성 전사 `scratchpad/twitch/audio/{ans_*,pre_*}.txt`(Whisper large-v3-turbo), 프레임 `scratchpad/twitch/frames/sec_*.jpg`(25분 간격, 0:45·2:00 결측) | 2026-09-04T18:30Z, 4h42m | 0.0절 제작자 발언·PoB 화면·타임라인 |
| Skadoosh 영상 자막 | `scratchpad/subs_txt/skadoosh_{KsK6tNjh50s,gWQNu6xddow,BLc0SguI0gk,B8yBMkd-jsE,F6ou4sj0uZE,CoskGFogxhA,Jj2eKr4Ez-A}.txt` | 0.1 ~ 2026-05-25 | 1·2·6장 제작자 발언 |
| Skadoosh 포럼 | https://www.pathofexile.com/forum/view-thread/3732489 (0.1, 2025-03-06) · /3848472 (BOTW, 2025-09-09) | — | 계보 |
| 커뮤니티 포럼 | /view-thread/3938368 ("Corrupting cry is dead") · /3908963 (0.4.0d 시기 버그) · /3822078 (0.2/0.3 피드백) · /3628612 (Breegin Titan) — `community_raw/forum_*.txt` | 2024-12 ~ 2026-08 | 7.1·7.3 |
| Skadoosh Discord | "Skadoosh's Hideout"(초대 D4Qh3fUbzH) #build-help·#clips-and-highlights — 데스크톱 클라이언트 스크린샷 전사 `scratchpad/discord_findings.md`, 요약 `ROUND2_ADDENDUM.md` §A. 검색 "warbringer" 18건·"ancestral bond" 2건·"fortifying" 93건; 고정 세팅·PoB 없음 | 2026-09-02 ~ 09-05 KST | 결론 5·1장·6.3·8.2 |
| 패치노트 캐시 | `D:/Pathcraft-AI/data/_cache/patchnotes/poe2/` — 3883495(0.4.0), 3885885(0.4.0 HF4), 3893204(0.4.0c), 3932540(0.5.0), 3934869(0.5.0 HF3), 3935437(0.5.0b), 3942896, 3949197(0.5.1), 3960375(0.5.2), 3968601(0.5.3), 3975218(0.5.4), 3980516(0.5.4b), 3996513(0.5.4f), 4000864(0.5.5), 4001250/4001277/4001313/4001331/4001365(0.5.5 HF1–5); `_cache/patchnotes/poe2_0_5_5_faq.txt` | 2025-12-05 ~ 2026-09-05 | 3장 원문 |
| poe2db (0.5.5 라이브) | https://poe2db.tw/us/Corrupted_Cry · /Corrupting_Cry_I · /Corrupting_Cry_II · /Corrupted_Blood · /Paquates_Pact · /Twisted_Pact · /Seismic_Cry · /Infernal_Cry · /Fortifying_Cry · /Raging_Cry · /Battershout · /Ancestral_Warrior_Totem · /Shockwave_Totem · /Earthshatter · /Earthquake · /Forge_Hammer · /Ancestral_Spirits · /Warbringer · /Warcallers_Bellow · /Urgent_Call · /Roaring_Cries · /Giants_Blood · /Second_Wind_III · /Overabundance_I · /Hateforge · /Titanrot_Cataphract · /Meginords_Girdle · /Deidbell · /Svalinn · /The_Surrender · /Astramentis · /From_Nothing · /Constricting_Command · /Guatelitzis_Soul_Core_of_Endurance · /Idol_of_Grold · /Rigwalds_Ferocity · /Ambrosia · /Magma_Barrier · /Scavenged_Plating · /War_Banner · /Jiquani's_Soul_Core_of_Rallying 등(KR = /kr/…) — 저장본 `scratchpad/poe2db_txt/`(버전 페이지 Version_0.2.0g/0.3.0/0.3.0c/0.3.1 포함). 라이브만 확인·미저장: /Redblade_Banner("Enemies in your Presence count as having double Power", Heraldric Tower Shield) · /Ancestral_Bond · /Jiquani's_Soul_Core_of_Automation("+1 to Level of all Totem Skill Gems", Limit 1, 무기) · /kr/Against_the_Darkness(어둠 저항) · /kr/Rite_of_Passage(통과의례) · /kr/Ancestral_Bond(선대의 유대) · /kr/Rolling_Slam(몰려오는 강타) · /kr/Boneshatter(뼈 박살) · /kr/Volcanic_Fissure(화산 균열) | 2026-09-05 fetch | 현재 텍스트·한국어명 |
| GGPK 0.5 추출 | `D:/Pathcraft-AI/data/game_data_poe2/{ActiveSkills,PassiveSkills,BaseItemTypes,Words,Mods}.json`, `data/_cache/tree_0_5.json` | 2026-09-04 | 이름 존재·노드 매핑(0.5.5 아님) |
| Maxroll | https://maxroll.gg/poe2/build-guides/corrupting-cry-warbringer-guide (2025-04-04) · /poe2/tierlists/league-starter-build-tier-list (2026-09-03) · planners.maxroll.gg profiles 8iac0r0w, lnuae0pp, 2i4l1e0y, l1b2if0h | — | 7장 |
| POEGuy 0.5.5 | https://www.youtube.com/watch?v=obkVjAMTaHk (09-04) · /watch?v=Tck6oxQ_qEQ (09-02); https://www.poe-vault.com/poe2/warrior/warbringer/totems-build-guide (0.4.0 태그, 06-18) · /totems-leveling-build (0.5.0 태그, 09-03); 채널 UCvICZHerbUEr3eM6q3kISIg — 자막 `scratchpad/subs_txt/poeguy_obkVjAMTaHk.txt`, 요약 `ROUND2_ADDENDUM.md` §B | 2026-09-02 ~ 09-04 | 0.2.4 레벨링 교차 확인 · 7.1 |
| 타 제작자 영상 | Xeph GuXt751YR1M · 4wjm9Wt-ySM; Larrymoreorless 257IVqU-2jg; Sesul uNiZjFMe5EM; Macsen uYCmXw_CQj0; Zepyh d7OOXi-WdgM; POEGuy OH2MM7RlrWA; Steelmage evMdvGmK-aI · 2gVDTaShOko; mas0ny1 RR4yjWrZrLU — 자막 `scratchpad/subs_extra/` | 2024-12 ~ 2026-08 | 7.1 |
| 파이프라인 추출물 | `scratchpad/extracts/{mob_guide,leveling_vs_live,subs_v01,subs_v03,subs_plans,patch_040,patch_050_skills,patch_050_systems,patch_05x,gamedata,community}.md`, `SOURCES_MANIFEST.md` | 2026-09-05 | 이 문서의 1차 입력 |
| 레포 참고 | `Docs/2026-09-01_TANGJEONG_POE2_CURSEMASTER_SHIELDWALL_ANALYSIS.md`(형식), `.claude/status/poe2_hardcore_sources.md`(0.5.5 버그픽스 = 기능 변경) | — | 형식·교차 확인 |

