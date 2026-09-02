# POE2 빌드 가이드 · 필터 파이프라인

> 코드만 봐서는 알 수 없는 것만 적는다. 완료 기록은 git log 가 갖고 있다.

## 산출물 위치

| 무엇 | 어디 |
|---|---|
| 가이드 원고(정본) | `Docs/*_GUIDE_DOC.html` — 구글 닥은 여기서 생성한 파생물 |
| 기준 템플릿 스펙 | `~/.claude/projects/D--Pathcraft-AI/POE2_BUILD_GUIDE_TEMPLATE.md` |
| 필터 스펙(정본) | `data/filter_build_targets/poe2_*.json` — `filters/*.filter` 는 재생성 산출물(gitignore) |
| NeverSink 베이스 | 커밋 안 됨. `_meta.bases` 의 URL+SHA-256 핀, `scripts/fetch_neversink_poe2_bases.py` 로 복원 |
| 공용 캐시 | `data/_cache/` (gitignore) — 자막·PoB XML·영상 길이. 에이전트는 받기 전에 여기부터 볼 것 |
| 디스코드 빌드 카드 | `D:/discord-admin/templates/build-cards-poe2/` (POE1 퍼블리셔의 `templates/build-cards` 와 분리 — 2시간 주기 자동 게시에 끼어들지 않게) |

## 발행된 구글 닥

커스마스터 `1hc7WGAfvgqyrmHfwpKqp_mNvSL-n6wMNnZgNJuGb124` · Fartfinder `1XK5Vpoeka4Ad6JqeLwAf34ivW8z2RA4gGQw4mz7Wtt8` ·
젬링 `1kIJRvBvBvIo8DsBtJaB2E8mjQeQRL6iDSqR28JCSybs` · 키타바 `1GS5amNLoi3ZHYpS-uxDgfOoZC0E-n_ntmekasORPK9M` ·
점화 `12dxZp3qdQJvihAi3HSMcYISnUfe6oVOJVg6_b1juBdY`

5종 모두 "링크가 있는 모든 사용자 = 뷰어, 로그인 불필요". 공유 링크는 `?usp=sharing` 형식으로 건다.

## 검사 도구 (에이전트에게 반드시 먼저 돌리게 할 것)

```
python scripts/check_guide_contract.py <guide> --baseline HEAD   # 장 띠·이미지 마커·3열 표·필수 장·부록 번호
python scripts/guide_evidence_check.py <guide> --baseline HEAD   # 딥링크 산술·영상 길이 초과·중첩 앵커·사라진 본문
python scripts/poe2_filter_sweep.py --spec <filter spec>.json    # 오버레이 회귀 (3단계 15초)
```

가이드 6종 기계 검사 1.2초, 필터 3단계 스윕 15초. 검증 에이전트가 이걸 손으로 하다가 26분을 쓴 적이 있다.

## 밟은 지뢰 (같은 걸 또 밟지 말 것)

- **생성기가 배정 안 된 섹션을 조용히 버린다.** `v4_*.json` 의 `tabs`/`merge` 에 없는 장은 발행본에서 통째로 사라진다. Fartfinder 출처 장이 이렇게 빠질 뻔했다. 장을 새로 만들면 설정에도 넣어야 한다.
- **`linkifyPlain` 은 키워드 바로 뒤 스탬프 하나만 링크한다.** `영상 8:24 · 11:41` 같은 연쇄는 두 번째부터 발행본에서도 평문이다. 소스에 직접 앵커를 박는 편이 안전하다.
- **용어 사전을 부록 번호로 찾으면 안 된다.** `make_v4_config.mjs` 가 `부록 2` 고정이라, 번호를 바꾸는 순간 빈 사전이 조용히 나갔다. 제목의 "용어 사전"으로 찾도록 고쳤다.
- **`v4_gemling.json` 의 merge 는 "부록"으로 시작하는 첫 띠 하나만 렌더한다.** 템플릿대로 부록을 쪼개면 거래 링크 표가 사라진다.
- **본문 이름을 고치면 `names`·`glossary` 도 같이 고쳐야 한다.** 안 그러면 구글 닥에서 그 이름만 색이 빠지고 용어 사전이 구식으로 남는다.
- **poe2db 는 POE2, `data/merged_translations.json` 은 POE1.** 후자로 POE2 한국어명을 판정하면 안 된다.
- **mobalytics·pathofexile·cafe.naver 는 봇에 403 을 준다.** 죽은 링크가 아니다. 브라우저로 확인할 것.
- **필터 오버레이는 앞에 붙어 first-match-wins.** NeverSink 가 더 크게 알리던 것을 덮으면 회귀다. 유니크 룰은 `rarity: ["Unique"]` 로 스코프를 걸고, BaseType 은 정확 일치를 쓴다.

## 검증에서 반복적으로 잡히는 실패 유형

1. **출처 날조** — 결과값은 맞는데 "어떻게 알았는지"를 지어낸다(PoB 빈 칸 주장 등). 기계 검사로 안 걸린다.
2. **과일반화** — "전 스냅샷에서 동일" 처럼 반례가 문서 자기 표에 있는 단정.
3. **관찰은 맞고 설명이 틀림** — 주얼이 유니크가 아니라는 관찰은 맞았는데 "미장착"이라 설명.

적대검증도 틀릴 수 있다. 녹아내린 존재/상징 건은 1차 검증(자막·설명란만 확인)이 틀리고 2차(게임 데이터 원본까지)가 맞았다.
