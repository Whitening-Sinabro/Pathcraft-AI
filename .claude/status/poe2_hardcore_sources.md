# POE2 하드코어 소스 명부

> 하코 문서를 **크리에이터 원본** 기반으로 쓰기 위한 소스 목록.
> 2026-09-04 조사 → 같은 날 **채널 열거로 전면 재작성**.
> 래더 통계(poe.ninja)는 "성숙한 리그에서 살아남은 사람들"을 말할 뿐,
> "이 빌드를 하코로 굴리면 어떤가"에 답하지 않는다. 그 답은 여기 사람들이 갖고 있다.

## 왜 이 파일이 있나

하코 보조 문서 2종을 래더 집계로 채웠다가 사용자에게 "허접하다"는 지적을 받았다.
질문은 "탱정 빌드를 하코로 하면 어떠냐"였는데 남 458명 통계로 답했다. 질문 바꿔치기다.
아래는 그 실수를 반복하지 않기 위한 1차 소스 명부다.

## 조사 방법 — 검색하지 말고 열거하라

1차 조사를 **제목 키워드 검색**("hardcore", "하드코어", "HCSSF")으로 했다가 ds lily·lexdtv 를
통째로 놓쳤다. 제목 기준 "하코 비율 %" 지표를 만들어 호진·겜창의삶을 0%로 찍기까지 했다.

2차는 **채널 영상 목록을 통째로 열거**했다. 결과가 완전히 달랐다.

```
python -m yt_dlp --flat-playlist --playlist-end 60 \
  --print "%(id)s|%(duration)s|%(title)s" "https://www.youtube.com/@<handle>/videos"
```

- 핸들을 모르면 `ytsearch6:<이름> <빌드명>` 에 `--print "%(channel)s|%(channel_url)s|%(title)s"`
  로 **채널 URL 부터 확정**하고 그 URL 을 열거한다. `@sargetwo`·`@Z3mos` 는 존재하지 않는
  핸들이었고("does not have a videos tab"), 실제 채널은 `UCXFZF8jhpIzOHVRSOScgY3w` ·
  `UCPuFjk05I4n2kM7ZKR3MoNg` 였다.
- **콘솔 인코딩에 속지 말 것.** `PYTHONIOENCODING=utf-8` 없이 열거하면 한국어 제목이 전부
  깨져 나온다. 디넬 채널을 한 번 그렇게 읽고 "제목을 못 읽겠다"로 넘길 뻔했다.
- 열거 결과는 제목 검색이 절대 못 주는 것을 준다 — **한 채널이 같은 빌드를 몇 번 갈아엎었는지**.
  그게 아래 "방패벽은 하나의 빌드가 아니다"를 드러낸 경로다.

**교훈:** 사람을 찾을 때는 제목이 아니라 ① 채널 정체성 ② 커뮤니티 연결(팟캐스트 게스트·
합방 제목의 @핸들) ③ **빌드 이름**으로 판다. 하코를 하는 사람이 제목에 하코를 안 쓴다.

## 자동 자막은 고유명사를 망가뜨린다 (인용 전 필수 확인)

받아둔 자막은 대부분 YouTube 자동 생성이다. 게임 고유명사가 통째로 다른 단어가 된다.

| 자막에 찍힌 것 | 실제 |
|---|---|
| `Smite of the Cathar` | Smith of Kitava (Z3mos `NgZ7T2AvqWA` 0:01) |
| `Smith of Gitawa` | Smith of Kitava (Gressoul `acQnYvisJow` 0:02) |
| `path of XL 2` · `power of XL2` | Path of Exile 2 (Sarge2 `ggC5mxG5wgo` 0:05) |
| `Barathis` | 바라시타 (임성빈 채널 본인 영어 제목 `E8A6HbzPQjM`) |

**이름은 자막에서 뽑지 말고 영상 제목 · PoB · GGPK 에서 뽑는다.** 자막은 *주장과 수치*의
근거로만 쓴다. 수치도 자막이 흐리면(`25 armor` 가 25,000 인 경우 등) 앞뒤 문맥으로 복원한다.

## 정정 — 이전 명부의 틀린 서술

**"Gressoul: 스미스 오브 키타바로 하코 전 피너클 클리어"를 방패벽 근거로 쓰면 안 된다.**
자막을 열어보니 그 캐릭터는 **롤링 슬램/지진** 축이다("my Smith of Kitava earthquake rolling
slam character", `gres_acQnYvisJow` 0:02). 같은 어센던시지 같은 빌드가 아니다.
Gressoul 은 *키타바 어센던시가 하코에서 피너클을 뚫는다*는 근거이지 *방패벽*의 근거가 아니다.

---

## 발견 1 — "방패벽"은 하나의 빌드가 아니다

빌드 이름으로 열거하니 **어센던시부터 갈린다**. 한 명만 보고 쓰면 그 사람의 선택을
"이 빌드의 정답"으로 적게 된다. 실제로 탱정 하나로 쓴 문서가 그랬다.

| 크리에이터 | 어센던시 | 딜/방어 축 | 핵심 |
|---|---|---|---|
| **탱정** | 스미스 오브 키타바 | 한손 철퇴+방패, 생명력·방어도(ES 0) | 아탈루이의 사열 + 운명의 저항. 제작자 본인이 "마나가 메인인 생존"이라 설명 |
| **LexD** | 스미스 오브 키타바 | **Avatar of Fire** — 전 피해를 화염으로 | `lmgCL7idCpg` 54:24 최종본. 별도로 Winter Warbringer(Vestige of Darkness) · Fire Titan 변형도 갖고 있다 |
| **Z3mos** | 스미스 오브 키타바 | **크릿** — 90% 원소 저항 + Nebuloch | "Nebuloch 가 인듀런스 차지를 소모해 방패벽 크릿을 보장한다". 1500만 크릿. **너프됨** |
| **Kris Droverson** | 스미스 오브 키타바 | **갑옷 = 딜** | "방패가 주 딜 소스다. 갑옷이 높을수록 딜이 올라간다"(1:10). 폭발 방패벽 + 무한 신전 |
| **Angormus** | 스미스 오브 키타바 | 워리어 레이서 관점 | 4:55 짧은 가이드. 액트 스피드런 세계기록 보유자 |
| **Big Ducks** | 스미스 오브 키타바 | **시체 폭발 온-히트** | "나는 보스 얼굴 앞에 그냥 서 있을 수 있는 탱키한 걸 한다. PoE2 에서 죽는 건 PoE1 보다 더 기분이 나쁘니까"(0:03~0:12) |
| **Sarge2** | **인보커** | ES + Protect Me From Harm | 어센던시가 아예 다르다. HCSSF 프레시 스타트 17.5시간 |

Kris Droverson 만 해도 채널 안에 **Immortal(폭발 방패벽+무한 신전, 0.4)** 과
**Demon Bear(Fury of the King · Ash Bark Talisman, 0.5)** 두 판이 따로 있다.
Z3mos 는 Great Wall / Grape Wall / Resonating Shield / Detonate Dead / Self Detonation 으로
계속 갈아엎었다. **"방패벽 키타바 빌드"라고 단수로 부르면 안 된다.**

## 발견 2 — 0.5.5 현행 패치 커버리지가 빌드마다 다르다

이게 어느 문서부터 쓸지의 실질 기준이다. 하코 문서는 지금 리그에서 쓰이므로,
0.5 자료만 있는 빌드는 "0.5.5에서도 그런가"를 우리가 판정할 수 없다.

| 빌드 | 0.5.5 소스 | 0.5 이하 소스 |
|---|---|---|
| **바라시타(디사이플 오브 바라시타 / 켈라리)** | **5명** — 임성빈(ko) · 디넬(ko) · MisoxShiru(en) · Blazeworks(en) · Skadutch(en, 0.5) | — |
| **화염파(Flameblast) 젬링** | **2명** — 임성빈(ko, HCSSF Verified) · ds lily(en) | MisoxShiru 크로노맨서 변형(HCSSF) |
| **방패벽 키타바** | **0명** | 탱정 · LexD · Z3mos · Kris Droverson · Angormus · Big Ducks (전부 0.5 또는 0.4) |

**방패벽 키타바를 0.5.5 에서 다룬 사람을 6개 채널을 전수 열거하고도 못 찾았다.**
그 채널들의 0.5.5 콘텐츠는 전부 다른 빌드다 — LexD 는 Spear & Shield Bleed Titan
(`vQibmfLbKFE`), Big Ducks 는 Explosive Witchhunter(`fXdNmYE5t9Q`).

**패치가 죽인 게 아니다 — 확인했다.** `data/_cache/patchnotes/poe2_0_5_5.txt`(29.5KB, TOC 와
섹션 9개가 일치하는 온전한 본문)에 **밸런스/스킬 섹션 자체가 없다.** 목차는 이벤트 리그 ·
의식 · 혼돈의 시련 · 알두르의 룬 코어 편입 · 엔드게임 · 리그 콘텐츠 · UI · MTX · 버그 수정뿐이다.
`Shield Wall` 0건, `Kitava` 0건, `Block` 0건. 디넬이 "0.5.5 에서 버프·너프가 없을 예정"이라고
한 것과 일치한다. **크리에이터들이 옮겨간 것이지 빌드가 죽은 게 아니다.**

## 발견 3 — 0.5.5 는 밸런스 섹션이 없지만 "버그 수정"이 기능을 바꿨다

밸런스 섹션이 없다고 "변경 없음"으로 읽으면 안 된다. **버그 수정 안에 빌드를 깨는 변경이
섞여 있다.** 캐시한 자막 중 일부가 이것 때문에 이미 낡았다.

| 0.5.5 버그 수정 원문 | 무엇을 깨나 |
|---|---|
| "Fixed a bug which would allow Skills from an alternate Weapon Set to be used without the corresponding Weapon swap occurring." | **무기 세트 스냅샷.** LexD `lex_svv8OBfJI_8`(워리어 테크 Ep.3)이 정확히 이 테크를 가르친다 — **그 영상의 해당 구간은 0.5.5 에서 무효**다. 인용하면 안 된다 |
| "Fixed a bug which would allow Auras and Support Gems from an inactive Weapon Set to still apply to the player." | 비활성 세트 오라·보조 젬. 구 PoB 를 그대로 쓰면 저항이 빠진다 |
| "Fixed a bug where it was possible to snapshot the effects of the Prism of Belief and From Nothing Unique Jewels." | 주얼 스냅샷 |
| "Fixed a bug which would allow using a Unique item granted Skill with non-Unique Weapons which were equipped in another Weapon Set." | 유니크 부여 스킬 우회 |
| "Fixed a bug where Ignites that deal Chaos Damage wouldn't ignite Oil Ground." | **점화 × 기름 지면.** ds lily 의 화염파+기름유탄 젬링(`lily_ds5aPwrmH6c`)이 이 상호작용 위에 있다 — 0.5.5 에서 **버프 방향** |
| "…Quality bonus granted to Flash Grenade by the Gemling Legionnaire's Advanced Thaumaturgy Passive Skill only showed the extra Lightning Damage…" | 젬링 유탄 표기 |
| "…the Lead me through Grace… Invoker Ascendancy Passive Skill was not preventing the gain of Spirit Modifiers granted by Medved's Tending." | Sarge2 의 **방패벽 인보커** 축 |

**규칙:** 자막을 인용하기 전에 그 주장이 0.5.5 버그 수정에 걸리는지 위 표로 대조한다.
0.5 영상은 대부분 유효하지만 **무기 세트 스냅샷 계열은 통째로 무효**다.

## 발견 4 — 사설 하드코어 리그가 커뮤니티 축이다

하코 크리에이터들이 공용 리그가 아니라 **초대제 사설 리그**에서 논다. 여기서 나온 캐릭터가
"하코에서 실제로 검증됐다"의 근거가 된다.

- **Timmy's Hardcore League (THC)** — Oscrix 가 `IauNVXcS4TQ` 0:08 에서 "Timmy Hardcore
  Private League" 라고 밝힌다. 그 캐릭터는 **JungRoan 이 만든 기름 유탄 위치헌터**를 패스파인더로
  옮긴 것. MisoxShiru 팟캐스트 Ep.55 가 `@Timmy_P_onTwitch` 게스트편이다.
- **릴리리그** — ds lily 가 운영하는 사설 HC GSF 리그. 한국 참가자 VOD 존재.

**JungRoan** 은 아직 채널을 안 텄다. 기름 유탄 계열의 원작자로 보이므로 화염파/기름 축
문서를 쓸 거면 1차 소스다.

## 발견 5 — 용어

- **화염파 = Flameblast.** 임성빈 본인이 영어 제목에 그렇게 쓴다(`i6_tfxyQfeQ`:
  "0.5.5 Flameblast Gemling Build Guide | Hardcore SSF Verified"). 추측 음차 금지.
- **바라시타**는 채널마다 영문 표기가 흔들린다 — `Varashta`(Skadutch·Blazeworks) ·
  `Varashita`(임성빈) · `Barathis`(임성빈 다른 영상). 우리 문서 파일명은 `VARASHTA` 다.

---

## 확보한 자막 (`data/_cache/subs/`, gitignore)

```
PYTHONIOENCODING=utf-8 python scripts/read_subs.py <file.json3>              # 전문
PYTHONIOENCODING=utf-8 python scripts/read_subs.py <file.json3> armor 9,000  # 검색어 주변만
```

`PYTHONIOENCODING=utf-8` 을 빼면 한국어 자막이 깨져 나온다. 테스트는
`python/tests/test_read_subs.py`(11건) — 인용 스탬프가 어긋나면 여기서 잡힌다.

### 한국어

| 파일 | 채널 | 내용 | 길이 |
|---|---|---|---|
| `lsb_i6_tfxyQfeQ.ko` | 임성빈 | **0.5.5 화염파 젬링 — 하드코어 SSF 검증** | 9:23 |
| `lsb_NVQRpuUbtqM.ko` | 임성빈 | 금단의 의식 리그 스타터 선택(=잼링) | 4:46 |
| `lsb_PBWgtjN4Amw.ko` | 임성빈 | **하코 100렙 바라시타 엔드게임 풀가이드** | 13:01 |
| `lsb_E8A6HbzPQjM.ko` | 임성빈 | 하코 초보 바라시타 빌드업 | 8:46 |
| `lsb_wmcxUiGjSdA.ko` | 임성빈 | 하코 SSF Zero-to-Hero | 11:52 |
| `lsb_x5ZIzjnVGtc.ko` | 임성빈 | **경로석 정규식 — 원인불명 사망 99% 차단** | 2:54 |
| `lsb_3UtpsH81z4A.ko` | 임성빈 | 99렙 시간당 1300만 경험치 레벨링 | 4:10 |
| `lsb_tSoJlIwCw-I.ko` · `lsb_5ljmPCbXXtQ.ko` · `lsb_HdJE5-CA4jg.ko` · `lsb_u-ICSDdAGfY.ko` | 임성빈 | 왜 하코를 · 어느 리그로 · 0.5.5 실망? · 시즌 준비 | 3:26 / 4:51 / 3:54 / 1:35 |
| `dinel_xUy9qUSTr1k.ko` | 디넬 | **하드코어 입문 가이드.** 본인 이력이 여기 있다 — "시즌 1부터 쭉 하드코어", 이번 시즌 **전체 36등 · 리치 1등**(1:21~1:30) | 13:43 |
| `dinel_ktg8phbLQw8.ko` | 디넬 | **0.5.5 최고의 스타터 바라시타 1렙~100렙.** "0.5.5에서 버프·너프가 없을 예정", "켈라리 바라시타는 엔드 세팅까지 가면 바퀴벌레 같은 생존력"(0:09~0:26) | 12:03 |
| `dinel_HYVmAyhHYCg.ko` | 디넬 | 하코 랭커의 안 죽는 크산테 전기불꽃 리치 A~Z(저자본~하이엔드) | 13:05 |
| `dinel_lsJOXOoCHNs.ko` | 디넬 | 죽기 싫은 사람의 하코 100렙 크산테 전기불꽃 리치 | 9:09 |
| `dinel_RzS-hsyy65M.ko` | 디넬 | **0.5.5 위치 스타터 가이드.** "위치는 얼리엑세스부터 지금까지 국밥 같은 선택지 — 어센던시 4개를 가진 유일한 클래스고 적어도 넷 중 하나는 매 시즌 메타픽"(0:00~0:17) | 16:09 |
| `dinel_L208yOpJ_D0.ko` | 디넬 | 0.5 직업 티어리스트 | 24:08 |

### 영어 — 하코 일반 (빌드 무관, 문서 공통 기반)

| 파일 | 채널 | 내용 | 길이 |
|---|---|---|---|
| `sarge_ggC5mxG5wgo.en` | Sarge2 | **HCSSF 100렙 달성 후 방어에 대해 배운 것.** 갑옷 공식 `갑옷/(갑옷+10×피격)`, T15 원숭이 슬램 **9,000 물리**, 절반 경감에 **10만 갑옷** 필요(1:14~2:42) | 29:40 |
| `gres_0WeokvPIunQ.en` | Gressoul | **EHP 브레이크포인트.** 엔드게임 목표 = 물리 **6~10k** · 원소 **30k** · 카오스 **12~15k**(3:18~3:29, 6:36). 30k 를 넘겨야 4~5모드 맵을 편히 돈다(7:17~8:28) | 14:58 |
| `skadu_vUImi-jDdEE.en` | Skadutch | HC 초보가 반복하는 실수 10가지 | 6:04 |
| `skadu_vZWD5hX149E.en` | Skadutch | 3분 안에 하코 SSF 팁 3가지 | 2:35 |
| `blaze_UTdyt6wkHJE.en` | Blazeworks | 0.4 HCSSF 리그 스타터 3선 | 12:01 |
| `blaze_1-sKhCgt1Xg.en` | Blazeworks | **HCSSF 유탄 택티션 — 97렙 랭크 1**(0:28~0:30). 하코 랭커 본인 세팅 | 17:17 |
| `sarge_O6_UMaQWhYY.en` | Sarge2 | 하드코어 랭크 1 빌드 오버뷰 — 패스파인더 독 활 | 6:16 |

### 영어 — 방패벽 키타바 (전부 0.5 이하)

| 파일 | 채널 | 내용 | 길이 |
|---|---|---|---|
| `lex_lmgCL7idCpg.en` | LexD | **0.5 방패벽 키타바 최종 업데이트 — Avatar of Fire** | 54:24 |
| `lex_goJd3U20VzQ.en` | LexD | 0.5 방패벽 키타바 빌드 업데이트("딜이 카오틱하다") | 36:14 |
| `lex_9FXJsaO-tFY.en` | LexD | 0.5 워리어 전 어센던시 리그 스타터 — "방패벽은 안 죽었다" | 16:58 |
| `lex_svv8OBfJI_8.en` | LexD | 워리어 테크 Ep.3 — 무기 세트 스냅샷 · 애니메이션 캔슬 | 13:48 |
| `lex_sO1tLA52AYA.en` | LexD | **막기(Block)에 뭔가 잘못됐다** — 메커니즘 비판 | 8:42 |
| `lex_yyxhJCoPnic.en` | LexD | 방패벽은 죽었나? 0.5 패치노트 + 방패 빌드 총평 | 17:34 |
| `lex_EEzXEyF8BgI.en` | LexD | **0.5 방패 빌드용 철퇴 제작법** | 15:58 |
| `lex_vQibmfLbKFE.en` | LexD | **0.5.5** 창+방패 출혈 타이탄 리그스타터 (방패벽 아님 — 0.5.5 에서 뭘 하고 있는지의 근거) | 37:14 |
| `z3mos_NgZ7T2AvqWA.en` | Z3mos | **그레이프 월 — 1500만 크릿 방패벽 90% 저항(너프됨).** Nebuloch 로 크릿 보장 | 31:14 |
| `z3mos_uPx_MQyBAqM.en` | Z3mos | 그레이트 월 — "내가 해본 가장 빠른 워리어" | 31:21 |
| `z3mos_990mKQ6T7rA.en` | Z3mos | 시체 폭발 + 공명 방패 스미스 빌드 가이드 | 19:37 |
| `z3mos_bP_co0GgM6Q.en` | Z3mos | 자가 기폭 방패벽 테크 | 5:52 |
| `kris_o-k5cZJ5VcI.en` | Kris Droverson | **불멸 키타바 — 폭발 방패벽 + 무한 신전. "갑옷이 곧 딜"**(0.4) | 28:31 |
| `kris_2qUcf1rjTa0.en` | Kris Droverson | **데몬 베어 키타바(0.5) — Fury of the King · Ash Bark Talisman.** 같은 채널의 다른 판 | 40:26 |
| `kris_IOdgcT-JmK8.en` | Kris Droverson | 방패벽 & 키타바 레벨링 가이드(0.4) | 33:41 |
| `duck_kc7ko5pBeP8.en` | Big Ducks | **시체 폭발 온-히트 방패벽 키타바 리그 스타트**(0.4) | 11:02 |
| `duck_fXdNmYE5t9Q.en` | Big Ducks | 0.5.5 폭발 위치헌터 리그스타터 (방패벽 아님) | 5:11 |
| `ango_7VCsAVI_Hvc.en` | Angormus | 0.5 방패벽 키타바 빌드 가이드 | 4:55 |
| `blaze_G-dKXtf0Ap4.en` | Blazeworks **w/ LexD** | "다들 PoE2 에서 방패를 자고 있나?" — 방패 좌담 | 1:43:19 |
| `sarge_zfU0YTibkpI.en` | Sarge2 | **방패벽 인보커** HCSSF 프레시 스타트(17.5시간) | 14:20 |
| `gres_acQnYvisJow.en` | Gressoul | 0.5 하코 전 피너클 클리어 — **롤링 슬램/지진 키타바(방패벽 아님)** | 18:48 |
| `gres_ENCI15tWM7I.en` | Gressoul | 아탈루이의 사열 2.7배 너프 분석 | 2:55 |
| `gres_D5XuObZNZ1E.en` | Gressoul | "내 하코 캐릭터를 이 슬램 빌드에 맡긴다" | 11:09 |
| `kitava20_kS80oF3VbJI.ko` | 탱정 | 키타바 2.0 (본 가이드 원본) | — |

### 영어 — 바라시타 (0.5.5 현행)

| 파일 | 채널 | 내용 | 길이 |
|---|---|---|---|
| `blaze_d2QbaO-sJ3o.en` | Blazeworks | **0.5.5 바라시타 SSF 캠페인 완주 가이드** | 31:02 |
| `miso_JvSbR8V9EtQ.en` | MisoxShiru | **0.5.5 나비라의 균열 디사이플 오브 바라시타 — "역대 가장 매끄러운 리그 스타터"** | 6:07 |
| `skadu_ph4cQGdnm70.en` | Skadutch | 0.5 30만 DPS 바라시타 진 소서리스 | 12:41 |
| `skadu_mZMpuKjtlVo.en` | Skadutch | 0.5 나비라의 균열 진 엔드게임 업데이트 | 12:19 |
| `miso_XsU9hhN2p00.en` | MisoxShiru | 0.5.5 최상위 메타 리그 스타터 총정리 | 39:59 |

### 영어 — 화염파(Flameblast) 젬링 (0.5.5 현행)

| 파일 | 채널 | 내용 | 길이 |
|---|---|---|---|
| `lily_ds5aPwrmH6c.en` | ds lily | **0.5.5 화염파+기름유탄 젬링 — 나쁜 장비로도 다 부순다.** "챌린지 레이스를 이 빌드로 우승했고 캠페인 장비만으로 전 보스를 잡았다"(0:09~0:17). 단 **"가장 센 스타터라고는 안 하겠다 — 훨씬 느리다"**(0:18~0:23) | 10:11 |
| `miso_A6K1I8PU_2s.en` | MisoxShiru | **HCSSF 크로노맨서 — "이 크로노맨서는 절대 안 죽는다"** | 20:52 |
| `lily_rDwXsj17K-8.en` | ds lily | 0.5.5 계획 — 기름 연사 무술가(다른 빌드) | 8:56 |
| `lily_2H4cpcz4Lco.en` · `lily_FUDmptONDlM.en` | ds lily | HC SSF 런 시작 · 소프트코어 마지막 날. **하이라이트 VOD라 정보 밀도가 낮다** | 9:28 / 8:22 |

### 영어 — 하코 전용 빌드 (Oscrix, 소환수·기름 축)

| 파일 | 내용 | 길이 |
|---|---|---|
| `oscrix_IauNVXcS4TQ.en` | **기름 패스파인더 — ".4 에서 내가 한 것 중 최강".** Timmy 사설 하코 리그(THC)용이고 **JungRoan 의 기름 유탄 위치헌터**를 옮긴 것이라고 본인이 밝힌다(0:08~0:15) | 9:50 |
| `oscrix_edI1rDFP3vw.en` | 코이어 오라클 for HC | 14:50 |
| `oscrix_iW9A5L8-vTI.en` | HC 홀리 스트라이크 | 3:57 |

### 받아봤지만 인용 근거로는 못 쓰는 것

| 파일 | 왜 |
|---|---|
| `rip_4rUTdihINB4.en`(Day 5) · `rip_ejIhqVVDxik.en`(Day 20) | RIP Clips 하코 사망 모음. **자막이 스트리머 리액션 욕설뿐이라 인용할 서술이 없다** ("I don't even know what to do that I just died", `[ __ ]` 검열). 죽는 정황(얼음 · 시야에 안 보이는 투사체 · 보스 탱킹 실패)은 영상으로 봐야 나온다. **나머지 12편은 받지 말 것** — 같은 성질이다 |
| `lily_2H4cpcz4Lco.en` · `lily_FUDmptONDlM.en` | ds lily 하이라이트 VOD. 잡담 비중이 높다 |

---

## 아직 안 받은 것 (다음 보강 대상)

1차·2차 보강으로 우선순위는 다 받았다. 남은 건 필요할 때만.

| 대상 | 채널 URL | 왜 필요한가 |
|---|---|---|
| **eltriki** 하드코어 액트 완주 #1~#29 (스페인어) | `UC1543074v44JJ959q6ckzyQ` | 캠페인 구간을 액트 단위로 쪼갠 유일한 연재. 빌드 문서엔 안 쓰이고 **캠페인 문서를 쓸 때만** 값어치가 있다 |
| **JungRoan** | 미확정 | 기름 유탄 위치헌터 원작자(Oscrix 증언). 화염파/기름 축 문서의 1차 소스 |
| RIP Clips 나머지 12편 | `UCUomM5JOVsd9YMctOzLqfBQ` | **받지 말 것** — 위 "인용 근거로는 못 쓰는 것" 참조 |
| Sarge2 스파크 토템 인보커 · 스톰버스트 | `UCXFZF8jhpIzOHVRSOScgY3w` | Sarge2 는 POE1/POE2 를 섞어 올린다. **제목의 리그명(Mirage=POE1)으로 게임을 먼저 가른 뒤** 받을 것 |

**핸들 정정** — 아래는 `@핸들`이 없거나 틀려서 열거가 실패했던 채널이다. 채널 URL 로 접근한다.

| 이름 | 잘못된 핸들 | 실제 채널 URL |
|---|---|---|
| Sarge2 | `@sargetwo` (videos 탭 없음) | `https://www.youtube.com/channel/UCXFZF8jhpIzOHVRSOScgY3w` |
| Z3mos | `@Z3mos` (videos 탭 없음) | `https://www.youtube.com/channel/UCPuFjk05I4n2kM7ZKR3MoNg` |
| Big Ducks | `@BigDucksGaming` (404) | `https://www.youtube.com/channel/UC8XfFGnTEJH1CXjucYDA5ng` |
| eltriki | — | `https://www.youtube.com/channel/UC1543074v44JJ959q6ckzyQ` |
| RIP Clips | — | `https://www.youtube.com/channel/UCUomM5JOVsd9YMctOzLqfBQ` |
| 임성빈 · 디넬 | — | `UCvj_myZNbqdHBBFT2IjKJWw` · `UC2Rbd4Wz9MC8yt8xQQtJe_g` |

## 확인만 되고 자막 없는 사람들

| 이름 | 메모 |
|---|---|
| **Ben_** | PoE 하드코어의 대명사. PoE2 HCSSF 플레이(다른 채널 리액션 클립으로 확인) |
| **PhazePlays** | *"World First Arbiter +4 HCSSF"* 는 검색 요약에서만 본 것 — **1차 확인 안 됨** |
| **Kripparrian** | HC 래더 1위 구간 사망 클립이 별도 채널에 있다. 상시 하코는 아님 |
| **혜미 Ham**(2만) · **호진**(18.1만) · **겜창의삶** | 한국어. SSFHC 입문 · 하코 생존 전략 단발 |
| **Woolie** · **skr1mps** · **DarthMicrotransaction** · **barricadettv** · **Augvald**(HCSSF 100렙 랭크 8) | Blazeworks 팟캐스트 게스트로 전원 교차 확인됨 |
| **KrushR**(독) · **PietSmiet**(독) · **AlphaReplay**(프) · **Rakin**(포) | 그 외 언어 |

---

## 이 명부를 쓸 때

- 하코 문서의 서술은 **이 사람들의 발언**을 근거로 달고, 래더는 보조 수치로만 쓴다.
- 같은 주제를 두 소스가 다르게 말하면 둘 다 적고 차이를 드러낸다. 어느 쪽이 맞는지 우리가
  판정할 수 없을 때도 **"여기서 갈린다"는 사실 자체가 독자에게 쓸모 있다.**
  예: 화염파 젬링을 임성빈은 0.5.5 리그 스타터 1순위로 고르는데, ds lily 는 같은 빌드를
  "센 건 맞지만 훨씬 느리다"고 한다. 둘 다 하코 기준 발언이다.
- 빌드당 **여러 명을 대조해** 쓴다. 어센던시 노드 순서 · 방어 축 · 핵심 유니크 · 딜 소스가
  갈린다. 갈리는 지점은 감추지 말고 표로 드러낸다.
- 채널이 하코 전용인지는 제목 문자열이 아니라 **채널 정체성**으로 판단한다. 제목에
  "하드코어"를 안 써도 전부 하코인 채널이 있다.
