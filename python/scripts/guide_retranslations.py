# -*- coding: utf-8 -*-
"""문단 단위 재번역 표 — 용어 치환으로 고칠 수 없는 문단만 담는다.

왜 용어 규칙과 분리하나:
    `fix_guide_translation.RULES` 는 (틀린 표현 → 바른 표현) 치환이다. 그런데
    "고유 아이템에 대한 스팸 고대 생명의 결실입니다"(Spam Ancient Wombgift for uniques)
    처럼 어순 자체가 무너진 문장은 어떤 치환 조합으로도 문장이 되지 않는다. 단어를
    아무리 고쳐도 읽는 사람이 무엇을 해야 하는지 알 수 없다. 이런 문단은 통째로
    다시 쓰는 수밖에 없고, 그건 치환 규칙과 다른 작업이라 표도 분리한다.

키가 영문 원문인 이유:
    문단 번호를 키로 잡으면 원본이 한 줄만 늘어도 전부 어긋난다. 영문 원문을 키로 쓰면
    "대조 근거"와 "키"가 같은 것이 되어, 원본이 바뀌면 조용히 틀린 자리에 붙는 대신
    미적용으로 보고된다.

한국어 용어 출처:
    레포 번역 데이터(`data/merged_translations.json`, `poe_translations.json`,
    `awakened_translations.json`)에서 확인한 공식 문자열만 쓴다. 이번 표에서 확인한 것:
    Shrine=성소, Eater of Worlds=세계 포식자, Searing Exarch=작열의 총주교,
    Wombgift=생명의 결실, Hivebrain Gland=벌레집 두뇌 분비선, Synaptic Ring=시냅스 반지,
    Breach Ring=균열 반지, Kaom's Binding=카옴의 속박, Grasping Mail=탐욕스러운 사슬옷,
    Covered in Ash=재로 뒤덮임, Fertile Catalyst=풍요의 기폭제, Foulborn=삿된,
    Blue Zanthimum=푸른도꼬마리, Immutable Dogma=불변의 교리, Crop Rotation=윤작,
    Orb of Scouring=정제의 오브, An Audience With The King=왕 알현.

    확인하지 못한 이름은 영문 그대로 둔다 — 아틀라스 패시브 노드(Unwavering Vision,
    Altered Prophecy), 3.29 신규 오브(Scrying orb), 용병 유형(Blade Ambusher, Combatant),
    지명·NPC(Kingsmarch, Raulf, Ngakanu, Pondium, Gamba, Vruun, Azadi).
    음차를 지어내면 인게임에서 찾을 수 없는 이름이 된다.
"""

from __future__ import annotations

import html
import re
from typing import NamedTuple


class Retranslation(NamedTuple):
    """영문 원문 문단 전체를 키로, 한국어 문단 전체를 값으로 갖는 재번역 한 건.

    `korean` 이 문자열이면 문단의 교체 대상 run 이 정확히 하나일 때만 쓰인다.
    문장 중간에 링크가 박힌 문단(`... go to the [Post-uber section] for his gear`)은
    링크 좌우가 별개 run 이라 하나로 합칠 수 없다. 그때는 `korean` 을 run 개수만큼의
    튜플로 준다 — 링크 run 은 건드리지 않고 좌우만 각각 다시 쓴다.
    """

    english: str
    korean: str | tuple[str, ...]
    reason: str
    # 링크 안 텍스트까지 다시 쓸 때만 True. 기본이 False 인 이유는 링크 문구가 URL 인
    # 문단이 대부분이라, 무심코 갈면 주소가 한국어로 덮여 안 보이게 되기 때문이다.
    # 링크 문구가 URL 이 아니라 오역된 문장인 자리에서만 켠다.
    include_links: bool = False
    # 링크 run 이 그대로 들고 남을 문구를 사람이 눈으로 확인해 적어둔 자리.
    # 재번역은 링크 밖 run 만 다시 쓰므로, 링크가 옛 오역(`럭셔리 업그레이드`)을 들고
    # 있으면 새 문장 옆에 유령 문구가 붙는다. 기계는 그게 살려둘 라벨인지 갈아야 할
    # 오역인지 구분할 수 없어서, 선언과 실물이 어긋나면 적용을 거부한다.
    # 링크가 없는 문단은 빈 문자열 그대로 두면 된다.
    link_label: str = ""


# 곱슬 따옴표·대시는 문서마다 흔들린다. 키 비교 전에 ASCII 로 눕혀서 그 흔들림을 없앤다.
_TYPOGRAPHY = str.maketrans({
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "–": "-", "—": "-", " ": " ",
})


def normalize_english(text: str) -> str:
    """엔티티 해제 + 활자 기호 평탄화 + 공백 정규화. 키와 원문을 같은 자리에 세운다."""
    return re.sub(r"\s+", " ", html.unescape(text).translate(_TYPOGRAPHY)).strip()


# 5장(아틀라스 트리 진행 & 파밍 루트) 전체. 사용자가 실제로 손을 움직이는 절이라
# 어순이 무너지면 그대로 실행 불가가 된다.
RETRANSLATIONS: tuple[Retranslation, ...] = (
    # --- 5.1 첫 아틀라스 트리 ---
    Retranslation(
        "How to Run", "운영 방법",
        "'Run'을 '달리다'로 직역해 '달리는 방법'이 됐다",
    ),
    Retranslation(
        "Progression for first Atlas tree:", "첫 번째 아틀라스 트리 진행 순서:",
        "Progression 을 '진행 상황'(status)으로 오역 — 여기서는 찍는 순서다",
    ),
    Retranslation(
        "5.1 First Atlas tree: Low tier uniques - https://poeplanner.com/a/65kJ",
        "5.1 첫 번째 아틀라스 트리: 저티어 고유 아이템 - ",
        "'낮은 계층 고유' — tier 를 '계층'으로 옮기고 아이템이라는 말이 빠졌다",
    link_label="https://poeplanner.com/a/65kJ"),
    Retranslation(
        "https://poeplanner.com/a/6ZbQ for Unwavering Vision ->",
        " — Unwavering Vision 확보용 →",
        "링크가 무엇을 위한 것인지(for ...)가 통째로 빠졌다",
    link_label="https://poeplanner.com/a/6ZbQ"),
    Retranslation(
        "https://poeplanner.com/a/6Zb4 for 100% Merc chance ->",
        " — 용병(Merc) 조우 확률 100% 확보용 →",
        "'100% Merc 확률' — 무엇의 확률인지 안 읽힌다",
    link_label="https://poeplanner.com/a/6Zb4"),
    Retranslation(
        "https://poeplanner.com/a/65Ct for 100% Jun chance ->",
        " — 준(Jun) 조우 확률 100% 확보용 →",
        "확률의 대상이 빠져 있었다",
    link_label="https://poeplanner.com/a/65Ct"),
    Retranslation(
        "https://poeplanner.com/a/65kJ for Breach and Div cards wheel",
        " — 균열 + 점술 카드 구간 확보용",
        "설명이 통째로 누락됐다",
    link_label="https://poeplanner.com/a/65kJ"),
    Retranslation(
        "Mercenary: target Azadi house for Blade Ambusher & Combatant",
        "용병: Blade Ambusher 와 Combatant 를 노리고 Azadi 가문을 집중 공략한다.",
        "house 를 '집'으로 직역",
    ),
    Retranslation(
        "Betrayal: Experience, T4-T5 uniques and Trarthan scarabs",
        "배신: 경험치, T4~T5 고유 아이템, 트라탄 갑충석.",
        "'T4-T5 고유' — 아이템 등급이 빠져 무엇의 T4~T5 인지 안 읽힌다",
    ),
    Retranslation(
        "Breach: Uniques & Rares from Wombgifts, Hivebrain Glands and (optional) Rare Breach Rings "
        "for Grasping mail vendor recipe.",
        "균열: 생명의 결실과 벌레집 두뇌 분비선에서 고유·희귀 아이템을 얻는다. "
        "(선택) 탐욕스러운 사슬옷 상인 조합식에 쓸 희귀 균열 반지도 함께 노린다.",
        "뒷문장이 통째로 영문으로 남아 있었다",
    ),
    Retranslation(
        "Div card wheel: For Light and Truth div card farming in Palace.",
        "점술 카드 구간: 궁전에서 '빛과 진실' 점술 카드를 파밍하기 위한 것이다.",
        "farming 을 '농사를 짓는 데'로 직역",
    ),
    Retranslation(
        "What uniques you can target from this tree:",
        "이 트리로 노릴 수 있는 고유 아이템:",
        "제목인데 의문문('무엇입니까?')이 됐다",
    ),
    Retranslation(
        "3. Kaom's binding & Ceinture of Benevolence",
        "3. 카옴의 속박 & 관대함의 띠",
        "Kaom's Binding 의 공식 한국어명은 '카옴의 속박'",
    ),
    Retranslation(
        "11. (Merc - Blade Ambusher) Vulconus",
        "11. (용병 - Blade Ambusher) 불커누스",
        "'머크' 음차",
    ),

    # --- 5.1 용병 / 배신 지시 ---
    Retranslation(
        "Look for a better Blade Ambusher/Combatant.",
        "더 나은 Blade Ambusher / Combatant 를 계속 찾는다.",
        "문장 자체는 통했으나 아래 항목들과 어투를 맞춘다",
    ),
    Retranslation(
        "Steal any usable rares/uniques",
        "쓸 만한 희귀·고유 아이템은 전부 훔친다.",
        "'사용 가능한' — usable 을 직역해 '쓸 만한'이라는 뜻이 흐려졌다",
    ),
    Retranslation(
        "Look out for Infamous Combatant (for Random Projectile Speed Gloves) and Infamous Eruptor "
        "(for Cover in Ash Helmet) for later recomb.",
        "나중에 재조합에 쓸 Infamous 전투원(무작위 투사체 속도 장갑용)과 "
        "Infamous Eruptor(재로 뒤덮임 투구용)를 노려둔다.",
        "'재 투구 커버용' — Cover in Ash 를 어절 단위로 잘라 옮겼다",
    ),
    Retranslation(
        "Betrayal: In priority order", "배신: 아래 우선순위 순서대로",
        "'우선순위' 만 남아 순서 지시라는 게 안 읽힌다",
    ),
    Retranslation(
        "Rin to Forti: Unique maps to unlock metamods crafting.",
        "린(Rin) → 요새(Fortification) 부서: 메타모드 제작을 열어줄 고유 지도가 나온다.",
        "unique maps 를 '독특한 지도'로 오역",
    ),
    Retranslation(
        "Janus to Research: Cadiro can offer a wide range of uniques. Not as OP as Cadiro anomalies, "
        "but great for early unique acquisition.",
        "야누스(Janus) → 연구(Research) 부서: 카디로(Cadiro)가 폭넓은 고유 아이템을 판다. "
        "카디로 변칙(Anomaly)만큼 강력하지는 않지만 초반 고유 아이템 수급에는 좋다.",
        "'고유 제품' — product 가 아니라 아이템이다",
    ),
    Retranslation(
        "Riker to Research OR Forti OR Transport: All 3 options are unique related. "
        "Strongest one is Research for 30 Ancient Orbs slamming.",
        "라이커(Riker) → 연구(Research) / 요새(Fortification) / 운송(Transportation) 중 하나: "
        "세 선택지 모두 고유 아이템과 연결된다. 가장 강한 건 고대의 오브 30개를 슬램할 수 있는 "
        "연구(Research)다.",
        "'3가지 옵션은 모두 고유하게 관련되어 있습니다' — unique related 를 부사로 오독",
    ),
    Retranslation(
        "Vagan to Transportation: Trarthan scarab chest. Whenever you have a pair of (1) Infamy and "
        "(2) Renown, do a white T1/T2 map to fish for uniques. Might have to wait until you unlock "
        "2nd Atlas tree though. Since this one has Unwavering Vision.",
        "베이건(Vagan) → 운송(Transportation) 부서: 트라탄 갑충석 상자가 나온다. "
        "(1) 악명(Infamy)과 (2) 명성(Renown)이 한 쌍씩 모일 때마다 흰색 T1/T2 맵을 돌려 "
        "고유 아이템을 낚는다. 다만 두 번째 아틀라스 트리를 열 때까지 기다려야 할 수 있다. "
        "그 트리에 Unwavering Vision 이 있기 때문이다.",
        "마지막 두 문장이 '흔들리지 않는 비전을 가지고 있기 때문입니다'로 뭉개져 "
        "무엇이 무엇을 가졌는지 사라졌다",
    ),
    Retranslation(
        "Leo to Forti: Double corrupted uniques. Even if they are not the uniques you are looking for, "
        "always check GLOVES and HELMET since they can roll (1) Curse on hit and (2) Light Radius "
        "implicits respectively.",
        "레오(Leo) → 요새(Fortification) 부서: 이중 타락 고유 아이템이 나온다. "
        "원하던 고유 아이템이 아니더라도 장갑과 투구는 항상 확인한다. "
        "각각 (1) 적중 시 저주, (2) 시야 반경 고정 속성이 붙을 수 있기 때문이다.",
        "'GLOVES 및 HELMET' 미번역 + '시야 반경 암시적' — implicit 을 형용사로 오역",
    ),
    Retranslation(
        "Gravicius to Transport: I got a full stack of King's Heart div cards in 3.29.",
        "그라비시우스(Gravicius) → 운송(Transportation) 부서: "
        "3.29 에서 '왕의 심장' 점술 카드를 한 스택 통째로 얻었다.",
        "'왕의 심장 div 카드 전체 스택을 얻었습니다' — 어색한 직역",
    ),
    Retranslation(
        "It That Fled to Transport OR Intervention: Transport for Foulborn uniques. Intervention for "
        "random Eye of Terror card (nerfed), and also for Breach scarabs.",
        "달아난 그것(It That Fled) → 운송(Transportation) 또는 개입(Intervention) 부서: "
        "운송은 삿된(Foulborn) 고유 아이템용. 개입은 무작위 '공포의 눈' 점술 카드(너프됨)와 "
        "균열 갑충석용이다.",
        "'Foulborn 고유의 수송' — 부서명과 용도가 뒤엉켰다",
    ),
    Retranslation(
        'Hillock to anywhere: "The Finishing Touch" for Fertile Catalysts.',
        "힐록(Hillock) → 아무 부서에나: 풍요의 기폭제를 주는 '화룡점정(The Finishing Touch)' 때문이다.",
        "'비옥한 촉매제' — Fertile Catalyst 의 공식명은 '풍요의 기폭제'",
    ),
    Retranslation(
        "Breach: Do not spec to only Hive or only Unstable Breach until you unlock all Breach passives.",
        "균열: 균열 패시브를 전부 열기 전에는 Hive 한쪽이나 Unstable Breach 한쪽만 찍지 마라.",
        "'로만 지정하지 마세요' — 무엇을 하지 말라는 건지 안 읽힌다",
    ),
    Retranslation(
        "Do Unstable Breach for Vruun.",
        "Vruun 을 노린다면 Unstable Breach 를 돌린다.",
        "'수행하십시오' — 목적과 수단이 뒤집혀 있었다",
    ),
    Retranslation(
        "Spam Ancient Wombgift for uniques.",
        "고유 아이템을 노린다면 고대 생명의 결실을 도배한다.",
        "'고유 아이템에 대한 스팸 고대 생명의 결실입니다' — 어순 붕괴",
    ),
    Retranslation(
        "Spam Provisioning Wombgift for rares.",
        "희귀 아이템을 노린다면 베푸는 생명의 결실을 도배한다.",
        "'희귀한 경우 스팸베푸는 생명의 결실을 보냅니다' — 어순 붕괴",
    ),
    Retranslation(
        "Spam Mysterious Wombgift with INFREQUENTLY found items for Hivebrain Gland "
        "(Breach twin bosses).",
        "벌레집 두뇌 분비선(균열 쌍둥이 보스)을 노린다면 '드물게 발견되는 아이템'을 넣은 "
        "수수께끼의 생명의 결실을 도배한다.",
        "'항목이 드물게 발견된 스팸 수수께끼의...' — 어순 붕괴",
    ),

    # --- 5.2 두 번째 아틀라스 트리 ---
    Retranslation(
        "5.2 Second Atlas Tree: Kaom's Heart + Trauma & Ritual window shopping - "
        "https://poeplanner.com/a/65eL",
        "5.2 두 번째 아틀라스 트리: 카옴의 심장 + Memory of Trauma·의식은 곁다리로 - ",
        "window shopping 을 '보상 확인'으로 옮겨 '주 목적이 아니다'라는 뉘앙스가 사라졌다",
    link_label="https://poeplanner.com/a/65eL"),
    Retranslation(
        "Note: Drop Abyss or Breach if you don't like to have Unwavering Vision blocking your "
        "scarabs drop.",
        "참고: Unwavering Vision 때문에 갑충석 드롭이 막히는 게 싫다면 "
        "심연(Abyss)이나 균열(Breach)을 빼라.",
        "'흔들리지 않는 시야가 ... 삭제하세요' — 주어와 조치가 뒤엉켰다",
    ),
    Retranslation(
        "Altered Prophecy: Div card wheel.",
        "Altered Prophecy: 점술 카드 구간.",
        "'점술 카드 바퀴' — wheel(트리 구간)을 직역. 노드명은 확인 불가라 원문 유지",
    ),
    Retranslation(
        "Merc: Not related to the strat. But we always need to hunt for better mercs.",
        "용병(Merc): 이 전략과 직접 관련은 없다. 다만 더 나은 용병은 항상 찾아다녀야 한다.",
        "Merc 미번역",
    ),
    Retranslation(
        "Breach: Unstable Breaches for more monsters. Hivebrain Glands. Ancient Wombgifts. "
        "Synaptic Rings.",
        "균열(Breach): 몬스터를 늘리려면 Unstable Breach. 그리고 벌레집 두뇌 분비선, "
        "고대 생명의 결실, 시냅스 반지.",
        "'하이브브레인 땀샘 / 고대 자궁선물 / 시냅스 고리' — 셋 다 공식명이 있는데 음차·직역",
    ),
    Retranslation(
        "Abyss: More monsters. Stygian Vise. Abyssal socketed gear (via Votive Hoard) for recomb "
        "later for Merc's gears. I don't do Delve, no hate just preference.",
        "심연(Abyss): 몬스터를 늘린다. 명계의 조임쇠. 나중에 용병 장비 재조합에 쓸 "
        "심연 홈 장비(Votive Hoard 경유). 나는 델브를 하지 않는데, 싫어서가 아니라 취향이다.",
        "'몬스터가 더 많아졌습니다' — 효과 설명이 과거 관찰문이 됐다",
    ),
    Retranslation(
        "Shrines: More monsters. More power for us and our mercs.",
        "성소(Shrine): 몬스터를 늘린다. 우리와 용병 모두 강해진다.",
        "Shrine 을 '신사'(일본식 신사)로 오역. 공식명은 '성소'",
    ),
    Retranslation(
        "Ritual: More monsters. Nameless Ritual hunting for King's invitation. This is for Untouched "
        "Soul and Light of Meaning (Life version). Pick up Pragmatism in your hidden loot filter too, "
        "if you do not have a better chest at this stage.",
        "의식(Ritual): 몬스터를 늘린다. 왕 알현을 얻기 위해 '이름 없는 의식'을 노린다. "
        "손길이 닿지 않은 영혼과 의미의 빛(생명력 버전)을 얻기 위한 것이다. "
        "이 시점에 더 나은 갑옷이 없다면 숨겨진 전리품 필터에서 실용주의도 주워둔다.",
        "'(생활 버전)' — Life version 을 '생활'로 오역. chest 를 '상자'로 오역",
    ),
    Retranslation(
        "Eater altars: More quant. Div card dup. Div card for unique armor/weapon.",
        "세계 포식자 제단: 아이템 수량 증가. 점술 카드 복제. 고유 방어구·무기용 점술 카드.",
        "'먹는 사람 제단' — Eater of Worlds 의 공식명은 '세계 포식자'",
    ),
    Retranslation(
        "Memory block: Less chance for Neglect and Dread. This is to get Memory of Trauma for "
        "Enmity's Embrace.",
        "기억 차단(Memory block): 방치와 불안이 뜰 확률을 낮춘다. "
        "원한의 품에 쓸 Memory of Trauma 를 얻기 위한 것이다.",
        "'방치와 공포' — 기억 이름을 일반명사로 옮겨 무엇을 막는지 안 읽힌다",
    ),
    Retranslation(
        "Honorable mention: You can switch your tree to Beyond and spec K'tash for more Div Card drop. "
        "But I don't need anything from Beyond in my run. Hence the above choices.",
        "덧붙이자면: 트리를 Beyond 쪽으로 바꾸고 K'tash 를 찍으면 점술 카드 드롭을 더 늘릴 수 있다. "
        "다만 내 진행에서는 Beyond 에서 필요한 게 없었다. 그래서 위와 같이 골랐다.",
        "'입상' — Honorable mention 을 시상 용어로 직역",
    ),
    Retranslation(
        "1. Spec Altered Prophecy in Atlas Skill Tree for Scrying orb drop chance (T14+).",
        "1. 아틀라스 패시브 트리에서 Altered Prophecy 를 찍어 Scrying orb 드롭 확률을 올린다(T14 이상).",
        "'아틀라스 패시브 트리의 사양 변경된 예언' — spec 을 '사양'으로 오역",
    ),
    Retranslation(
        "2. Farm Caldera until Scrying orb drops. Unspec Altered Prophecy to free point.",
        "2. Scrying orb 가 드롭할 때까지 칼데라를 파밍한다. 그다음 Altered Prophecy 를 해제해 "
        "포인트를 회수한다.",
        "'점술 구체' — 확인되지 않은 번역명. 원문 그대로 둔다",
    ),
    Retranslation(
        "3. Scry Caldera to either City Square (recommended - for Cadiro anomaly) or Jungle Valley "
        "(no boss altars).",
        "3. Scrying orb 로 칼데라를 도시 광장(권장 — 카디로 변칙이 나온다) 또는 "
        "밀림 계곡(보스 제단 없음)으로 바꾼다.",
        "'점술 칼데라를 ... 이동합니다' — scry 를 명사로 오독. '정글 밸리'는 음차",
    ),
    Retranslation(
        "4. Farm your scry-ed map with Eater of World influence.",
        "4. 바꾼 맵을 세계 포식자 영향력으로 돌린다.",
        "'점술 지도를 관리하세요' — farm 을 '관리'로 오역",
    ),
    Retranslation(
        "5. If City Square, rush to boss to eliminate boss altars.",
        "5. 도시 광장이라면 보스에게 먼저 달려가 보스 제단을 없앤다.",
        "'시티스퀘어' 음차 — 앞 문단의 '도시 광장'과 표기가 갈렸다",
    ),
    Retranslation(
        "6. Always pick the following Altars: Quantity/Div card duplicate/Div card for unique armour.",
        "6. 제단은 항상 다음을 고른다: 아이템 수량 / 점술 카드 복제 / 고유 방어구용 점술 카드.",
        "'고유 갑옷의 경우 수량/...' — 슬래시 목록의 수식 관계가 뒤집혔다",
    ),
    Retranslation(
        "7. Do all mechanics EXCEPT for Ritual. You will only do Ritual if it is Nameless.",
        "7. 의식을 제외한 모든 메커니즘을 처리한다. 의식은 '이름 없는 의식'일 때만 한다.",
        "'Nameless인 경우에만' — 앞 문단에서 이미 '이름 없는 의식'으로 번역한 대상",
    ),
    Retranslation(
        "8. Don't forget to visit Gamba box and Cadiro whenever you have Anomalies in the map.",
        "8. 맵에 변칙(Anomaly)이 있으면 Gamba 상자와 카디로를 반드시 들른다.",
        "'Anomalies가 나타날 때마다' — 앞에서 '변칙'으로 옮긴 것과 표기가 갈렸다",
    ),
    Retranslation(
        'Ritual Note: If you do find Nameless Rituals, try to defer all Audience with the King. '
        'Then immediately spec to "Immutable Dogma" and 2 small nodes for "Favours deferred reappears '
        '20% sooner". This is to get all of the Invitations out in the next map or two.',
        "의식 참고: 이름 없는 의식을 만나면 '왕 알현'을 전부 미뤄둔다. 그런 다음 곧바로 "
        "'불변의 교리'와 '미뤄둔 호의가 20% 더 빨리 다시 나타남' 작은 노드 2개를 찍는다. "
        "다음 한두 맵 안에 초대장을 몰아서 받기 위한 것이다.",
        "'연기된 즐겨찾기' — Favour 를 UI 즐겨찾기로 오역",
    ),
    Retranslation(
        "Kingsmarch: You should also start setting up your Kingsmarch around this point too. "
        "Reroll at Raulf and get:",
        "Kingsmarch: 이 시점쯤에는 Kingsmarch 세팅도 시작해야 한다. Raulf 에서 리롤해 다음을 맞춘다:",
        "'재등록하면 다음을 얻을 수 있습니다' — reroll 을 '재등록'으로 오역",
    ),
    Retranslation(
        "18x level 4/5 Farmers: I did all Blue Zanth for easy management.",
        "레벨 4/5 농부 18명: 관리가 편하도록 전부 푸른도꼬마리로 돌렸다.",
        "'Blue Zanth를 모두 만들었습니다' — 작물명 미번역 + did 를 '만들다'로 오역",
    ),
    Retranslation(
        "9x level 4/5 Sailors: Send 4,200 Blue Zanth (or 100,000 shipment value) to Ngakanu to fish "
        "for Fire Res & Attack Block tattoos. Send 19,000 Blue Zanth (or 450,000 shipment value) to "
        "Pondium to fish for Runegraft of the Warp.",
        "레벨 4/5 선원 9명: 화염 저항과 공격 막기 문신을 낚으려면 Ngakanu 로 푸른도꼬마리 4,200개"
        "(또는 운송 가치 100,000)를 보낸다. 왜곡의 룬 접목을 낚으려면 Pondium 으로 19,000개"
        "(또는 450,000)를 보낸다.",
        "'공격 피해 막기' — Attack Block 은 '공격 막기'. 작물명 미번역",
    ),
    Retranslation(
        "3x level 4/5 Enchanters: Throw the shields & belts you got from above shipping and any trash "
        "uniques here. Need a lot of dusts for recomb.",
        "레벨 4/5 마법부여사 3명: 위 항해에서 얻은 방패·허리띠와 잡템 고유 아이템을 전부 여기 넣는다. "
        "재조합에는 가루가 많이 든다.",
        "'배송 위에서 얻은' — from above shipping 을 어절 순서대로 옮겼다",
    ),
    Retranslation(
        "<Don't do this when you are short on gold> As many level 4+ Mappers as you can: Feed them "
        "scour/white Shaper and Elder Guardian maps for (1) Fragments, (2) Shaper shields and "
        "(3) Elder gloves.",
        "<골드가 부족할 때는 하지 마라> 레벨 4 이상 지도 제작자를 가능한 한 많이: "
        "정제한/흰색 쉐이퍼·엘더 가디언 지도를 먹여 (1) 조각, (2) 쉐이퍼 방패, "
        "(3) 엘더 장갑을 얻는다.",
        "'수세미' — scour 를 세제로 오역(Orb of Scouring=정제의 오브)",
    ),

    # --- 5.3 대안 트리: 수확 ---
    Retranslation(
        "5.3 Alternative Second Atlas Tree: Harvest - https://poeplanner.com/a/65kf",
        "5.3 대안 두 번째 아틀라스 트리: 수확 - ",
        "'아틀라스 패시브 트리' 표기를 절 제목에서 통일한다",
    link_label="https://poeplanner.com/a/65kf"),
    Retranslation(
        "Harvest is mandatory in SSF. Even though this has been offloaded a whole lot by AllFlame boat "
        "crafting in 3.29. You will still need this for:",
        "SSF 에서 수확은 필수다. 3.29 에서 올플레임 보트 제작이 상당 부분을 대신해주긴 하지만, "
        "다음은 여전히 수확이 필요하다:",
        "'다음과 같은 경우에도 이 정보가 필요합니다' — this 를 '정보'로 오독",
    ),
    Retranslation(
        "And of course, gambling div cards.",
        "그리고 물론 점술 카드 도박도 있다.",
        "'도박용 div 카드' — 수식 방향이 뒤집혔다",
    ),
    Retranslation(
        "This planner is only the barebone of Harvest. You can couple in any mechanic that you prefer. "
        "I always do Crop Rotation for the juice that I'm missing. But that requires some luck and a "
        "tiny bit of knowledge, thus I'll leave it out from this tree. You can watch DSLily guide for "
        "crop rotation if you are into it.",
        "이 플래너는 수확의 뼈대만 담았다. 원하는 메커니즘은 얼마든지 얹어도 된다. "
        "나는 부족한 주스를 채우려고 항상 윤작을 돌린다. 다만 운과 약간의 지식이 필요해서 "
        "이 트리에서는 뺐다. 관심 있으면 DSLily 의 윤작 가이드를 보면 된다.",
        "'자르기 회전' — crop rotation 을 두 번째 언급에서 다르게 옮겼다(앞은 '윤작')",
    ),
    Retranslation(
        "1. Run T16s City Square with either Eater or Exarch influence. They both have Quant altars "
        "now. Juice scaled with higher the map tier, so don't run this in low level maps.",
        "1. T16 도시 광장을 세계 포식자 또는 작열의 총주교 영향력으로 돌린다. "
        "이제 양쪽 모두 수량 제단이 나온다. 주스는 맵 티어가 높을수록 커지므로 "
        "저티어 맵에서는 돌리지 마라.",
        "'City Square' 미번역 + Exarch 의 공식명은 '작열의 총주교'",
    ),
    Retranslation(
        "2. Rush boss to eliminate boss altars.",
        "2. 보스로 먼저 달려가 보스 제단을 없앤다.",
        "'보스를 서둘러 제거하여 보스 제단을 제거하세요' — 동사가 중복되고 순서가 뒤집혔다",
    ),
    Retranslation(
        "3. Get all quantity altars.",
        "3. 수량 제단은 전부 먹는다.",
        "'모든 수량의 제단' — quantity altar 를 '수량의 제단'으로 분해",
    ),
    Retranslation(
        "4. Do Harvest last.", "4. 수확은 가장 마지막에 처리한다.",
        "지시문 어투를 절 안에서 통일한다",
    ),

    # --- 5.4 세 번째 트리: 우버 조각 ---
    Retranslation(
        "5.4 Third Atlas Tree: Uber fragments for Hallowed Monarch - https://poeplanner.com/a/65eQ",
        "5.4 세 번째 아틀라스 트리: 거룩한 국왕용 우버 조각 - ",
        "'거룩한 국왕을 위한 Uber 조각' — 표기 통일",
    link_label="https://poeplanner.com/a/65eQ"),
    Retranslation(
        "We need to chase our BIS helment - Hallowed Monarch. Helmet drops from Uber Dread -> "
        "need Reverent Fragment -> gotta farm Sanctuary.",
        "우리의 BIS 투구인 거룩한 국왕을 노려야 한다. 이 투구는 우버 드레드에서 드롭 → "
        "숭배의 조각이 필요 → 성역을 파밍해야 한다.",
        "'Sanctuary를 농장에 두어야 합니다' — farm 을 '농장'으로 오역",
    ),
    Retranslation(
        "Tree is all about boosting character power so you can handle the boss easily. Just pick up "
        "those nodes and run straight to boss. They nerfed Nightmare/T17 a lot. This place is no longer "
        "the best place to farm everything anymore.",
        "이 트리는 보스를 쉽게 잡도록 캐릭터 파워를 올리는 데 집중한다. 해당 노드만 찍고 "
        "보스로 직행하면 된다. 악몽/T17 은 크게 너프됐다. 여기는 더 이상 아무거나 파밍하기 "
        "좋은 곳이 아니다.",
        "'모든 것을 재배하기에' — farm 을 '재배'로 오역",
    ),
    Retranslation(
        "2. Run Sanctuary with either Eater or Exarch influence",
        "2. 성역을 세계 포식자 또는 작열의 총주교 영향력으로 돌린다.",
        "'Sanctuary를 운영하세요' — run 을 '운영'으로 오역",
    ),
    Retranslation(
        "3. Scarab slot = 4 Sacrifice Fragment (5% quant each).",
        "3. 갑충석 슬롯 = 희생 조각 4개(각각 아이템 수량 5%).",
        "'각 5% 퀀트' — quant 음차",
    ),
    Retranslation(
        '4. (OPTIONAL) Add in a "Influencing Scarab of Inteference", only if you can handle it.',
        "4. (선택) 감당할 수 있을 때만 '간섭의 영향력 갑충석'을 추가한다.",
        "'간섭의 영향 갑충석' — 공식 계열명은 '영향력 갑충석'",
    ),
    Retranslation(
        "5. (OPTIONAL) Pick Quantity Altar. Also only if you can handle it.",
        "5. (선택) 수량 제단을 고른다. 이것도 감당할 수 있을 때만.",
        "'또한 처리할 수 있는 경우에만 가능합니다' — 앞 항목과 어투가 갈렸다",
    ),
    Retranslation(
        "6. Pick up all power boosting mechanic: Shrines, Delves, and Huck companion from contract.",
        "6. 파워를 올려주는 요소는 전부 챙긴다: 성소, 델브, 계약에서 나오는 Huck 동료.",
        "Shrine 을 '신사'로 오역",
    ),
    Retranslation(
        "7. Skip trash mobs. Run straight to boss.",
        "7. 잡몹은 건너뛴다. 보스로 직행한다.",
        "'쓰레기 몹' — trash mob 직역",
    ),
    Retranslation(
        "Always go for Cadiro Anomaly. Lots of T2+ uniques can be obtained from here. Try to stick with "
        "City Square, Mesa, or any of your favourite map in the bottom left quadrant.",
        "항상 카디로 변칙을 노려라. 여기서 T2 이상 고유 아이템이 많이 나온다. "
        "도시 광장, 메사, 또는 좌하단 사분면에서 자기가 선호하는 맵 하나로 고정하는 게 좋다.",
        "'좋아하는 지도를 붙여보세요' — stick with 를 '붙이다'로 오역",
    ),

    # === 4장: 장비 세팅 =========================================================
    # 표 셀이라 짧지만, 짧아서 더 안 읽힌다. "생명과 카오스 저항에서는 희귀합니다"
    # (Rare with Life and Chaos Res) 처럼 형용사 rare 를 서술어로 옮긴 자리가 많다.
    Retranslation(
        "Cast: You, Blade Ambusher, Animate Guardian (AG). If you really hate the Trapper and are "
        "looking for Combatant's gearing, go to the Post-uber section for his gear.",
        ("구성: 본인, Blade Ambusher, 수호자 기동(AG). 트래퍼가 정 싫어서 Combatant 장비를 "
         "찾는 거라면 ",
         " 절(4.4)로 가서 그 장비를 봐라."),
        "Cast(등장 구성)를 '시전'으로 오역",
    link_label="우버 이후"),
    Retranslation("You", "본인", "대명사 You 를 '너'로 직역 — 표 머리글이다"),
    Retranslation("Same 3 characters: You, Blade Ambusher, AG.",
                  "구성은 그대로 셋: 본인, Blade Ambusher, AG.",
                  "'동일한 3자' — character 를 '자'로 축약"),
    Retranslation("Still You, Blade Ambusher, AG - this is the gear that got 10/10 Ubers down.",
                  "구성은 여전히 본인, Blade Ambusher, AG — 우버 10종을 전부 잡은 장비다.",
                  "'Still You' 미번역"),
    Retranslation("No update", "그대로 유지", "'업데이트 없음' — 게임 패치로 읽힌다"),
    Retranslation("Shared between mercs", "용병끼리 돌려 쓴다", "'용병 간에 공유됨' 수동태"),

    # 무기·방어구 셀
    Retranslation("1x Nycta's Lantern and 1x rare Shield with Life/Res",
                  "닉타의 등불 1개 + 생명력·저항이 붙은 희귀 방패 1개",
                  "'희귀 방패(생명/저항 포함)' — 등급 용어 오역"),
    Retranslation(
        "Any rare dagger/claw with (1) Crit chance -> (2) Crit damage -> (3) Accuracy -> "
        "(4) Elemental damage with attack",
        "(1) 치명타 확률 → (2) 치명타 피해 배율 → (3) 정확도 → (4) 공격 시 원소 피해 순으로 "
        "붙은 아무 희귀 단검/클로",
        "우선순위 목록이 수식어로 뭉쳐 '무엇을 고르라'가 사라졌다",
    ),
    Retranslation("Rare with Life and Light Radius", "생명력 + 시야 반경 희귀 아이템",
                  "'Rare with Life' 가 통째로 미번역"),
    Retranslation(
        "Corrupted Unique Helmet with 25-30% Light Radius implicit from Leo in Fortification",
        "시야 반경 25~30% 고정 속성이 붙은 타락 고유 투구 — ",
        "'25-30% 시야 반경 암시적 요새의 레오에게서' — 명사구가 통째로 무너졌다",
    link_label="요새의 레오에게서"),
    Retranslation(
        'Steal a Helmet from Infamous Eruptor for "Your Warcries cover Enemies in Ash for 5 seconds"',
        "Infamous 분출자에게서 투구를 훔친다 — '전투의 함성이 5초 동안 적을 재로 뒤덮음' 때문이다.",
        "'악명 높은 Eruptor' — 용병 유형명을 형용사로 오역",
    ),
    Retranslation("Evasion based rare: Life/Fire Res", "회피 기반 희귀 아이템: 생명력 / 화염 저항",
                  "등급 용어 통일"),
    Retranslation("(to prepare for Enmity's Embrace swap)", "(원한의 품으로 교체할 것을 대비해)",
                  "'교환을 준비하기 위해' 어색"),
    Retranslation("Rare with Life and Chaos Res.", "생명력 + 카오스 저항 희귀 아이템.",
                  "'생명과 카오스 저항에서는 희귀합니다' — rare 를 서술어로 오역"),
    Retranslation("Rare with Movement Speed/Life/Res/Attribute",
                  "이동 속도 / 생명력 / 저항 / 능력치 희귀 아이템",
                  "'재질' — Res 를 '재질'로 오역"),
    Retranslation("Evasion based rare: Movement Speed", "회피 기반 희귀 아이템: 이동 속도", "등급 용어 통일"),
    Retranslation("Rare with Life/Res", "생명력 / 저항 희귀 아이템",
                  "'생명/생명력으로 레어' — Res 가 생명력으로 뭉개졌고 등급 표기도 음차다"),
    Retranslation("Stygian Vise with Life + Fire Res early on",
                  "초반에는 생명력 + 화염 저항이 붙은 명계의 조임쇠",
                  "'명계의 조임쇠 라이프 + 화염 저항 초기' — 조사가 하나도 없다"),
    Retranslation("1x Voideye for +5 Flame Link level & 1x Lori's Lantern",
                  "공허의 눈 1개(화염의 연결 레벨 +5용) + 로리의 등불 1개",
                  "'+5 화염의 연결 레벨의 경우' — for 를 '경우'로 오역"),
    Retranslation("Turquoise Amulet with Life/Chaos Res/Attributes",
                  "생명력 / 카오스 저항 / 능력치가 붙은 터키석 목걸이",
                  "조사가 빠져 수식 관계가 안 보인다"),
    Retranslation(
        "Ignomon (Light Radius + blinded to help out with the lack of accuracy on your merc early game)",
        "이그노몬 (시야 반경 + 실명 유발. 초반 용병의 정확도 부족을 메워준다)",
        "'눈이 멀었습니다' — 적을 실명시키는 효과인데 착용자가 눈먼 것으로 읽힌다",
    ),
    Retranslation("Any rare with following mods, in priority order:",
                  "아래 속성이 붙은 아무 희귀 아이템. 우선순위 순서대로:",
                  "'모드를 사용하는 레어' — mod 는 속성이고, 등급 표기도 음차다"),
    Retranslation("% Max life -> Chance to block -> Dex/Int -> Max res",
                  "최대 생명력 % → 막기 확률 → 민첩/지능 → 최대 저항",
                  "Dex/Int 미번역 + block 을 '차단'으로 오역"),

    # 4.2
    Retranslation(
        "Nycta's + a rare crafted Ezomyte Tower Shield with (1) High block chance, (2) Maximum life "
        "and (3) Reduced Damage from Crits/Additional phys reduction [View Crafting Guide]",
        "닉타의 등불 + (1) 높은 막기 확률, (2) 최대 생명력, (3) 치명타 피해 감소 / 추가 물리 피해 "
        "감소를 제작해 붙인 희귀 에조미어 거대 방패 ",
        "베이스 이름(Ezomyte Tower Shield)이 통째로 사라졌다",
    link_label="[제작 가이드 보기]"),
    Retranslation(
        'Rare Armour based Helmet with (1) Maximum Life, (2) Light Radius and (3) "Your Warcries '
        'cover Enemies in Ash for 5 seconds" [View Crafting Guide]',
        ("(1) 최대 생명력, (2) 시야 반경, (3) '전투의 함성이 5초 동안 적을 재로 뒤덮음' 이 "
         "붙은 방어도 기반 희귀 투구 [",
         "]"),
        "수식어가 뒤로 밀려 '무엇을 만들라'가 문장 끝에 왔다",
    link_label="제작 가이드 보기"),
    Retranslation("Evasion based with (1) +1 Abyssal socket and (2) Fire res [View Crafting Guide]",
                  "회피 기반, (1) 심연 홈 +1 + (2) 화염 저항 ",
                  "'회피 (1) +1 심연 홈' — 조사가 없다", link_label="[제작 가이드 보기]"),
    Retranslation("Evasion based with (1) +1 Abyssal socket and (2) Fire res",
                  "회피 기반, (1) 심연 홈 +1 + (2) 화염 저항",
                  "'회피는 ...를 기반으로 합니다' — 주어가 뒤집혔다"),
    Retranslation("Pragmatism (put 1L Flame Link here)", "실용주의 (여기에 1링크 화염의 연결을 넣는다)",
                  "'1L' 미번역"),
    Retranslation(
        "Leviathan Gauntlets with Life/Chaos res. Add (Implicit) Mine Throwing Speed "
        "[View Crafting Guide]",
        "생명력 / 카오스 저항이 붙은 레비아탄 건틀릿. 고정 속성으로 지뢰 투척 속도를 추가한다 ",
        "'(암시적) 지뢰 투사 속도' — implicit 은 고정 속성, Add 가 사라졌다",
    link_label="[제작 가이드 보기]"),
    Retranslation("Evasion based gloves with Fire res and crafted AOE/AOE damage",
                  "화염 저항 + 제작한 효과 범위 / 범위 피해가 붙은 회피 기반 장갑",
                  "'장갑과 화염 저항' — with 를 '과'로 옮겨 병렬이 됐다"),
    Retranslation("Leviathan Greaves with Movement Speed/Life/Chaos res [View Crafting Guide]",
                  "이동 속도 / 생명력 / 카오스 저항이 붙은 레비아탄 각반 ",
                  "'with' 와 'res' 가 미번역으로 남았다", link_label="[제작 가이드 보기]"),
    Retranslation("Rare Turquoise Amulet with +1 to Fire Skill Gem & Maximum Life",
                  "화염 스킬 젬 +1 과 최대 생명력이 붙은 희귀 터키석 목걸이",
                  "'화염 스킬 젬 및 최대 생명력에 +1' — +1 의 대상이 둘로 잘못 걸렸다"),
    Retranslation("Foulborn Hinekora's Sight (up to 50% Light Radius)",
                  "삿된 히네코라의 통찰력 (시야 반경 최대 50%)",
                  "Foulborn 의 공식 접두사는 '삿된'"),
    Retranslation("Cheap Anoint: Combat Stamina (1x Clear, 1x Verdant & 1x Black)",
                  "저렴한 성유: 전투 지구력 (투명한 성유 1 + 신록빛 성유 1 + 검은빛 성유 1)",
                  "기름 이름이 '클리어/신록/블랙' 으로 음차됐다"),
    Retranslation("Eternal Struggle (15% culling)", "영원한 투쟁 (마무리 타격 15%)", "culling 음차"),

    # 4.3
    Retranslation(
        "2x Crafted Gutting Knives with (1) Crit Chance + (2) Crit Damage + (3) Multimodded Hit "
        "Cannot Be Evaded & Attack Penetrate Elements/Inc Fire damage/Trap damage "
        "[View Crafting Guide]",
        "(1) 치명타 확률 + (2) 치명타 피해 배율 + (3) 멀티모드로 '무조건 명중' 와 "
        "'공격이 원소 저항 관통' / 화염 피해 증가 / 덫 피해를 붙인 제작 내장 제거용 단도 2개 ",
        "베이스 이름(Gutting Knives)과 개수가 통째로 사라졌다",
    link_label="[제작 가이드 보기]"),
    Retranslation('"Random projectile speed" evasion based gloves [View Crafting Guide]',
                  "'무작위 투사체 속도'가 붙은 회피 기반 장갑 ",
                  "발사체 → 투사체, 수식 관계 정리", link_label="[제작 가이드 보기]"),
    Retranslation("Legacy of Fury from Maven", "광분의 유산 (메이븐에게서)",
                  "'Maven의 광분의 유산' — 소유격으로 오독"),
    Retranslation("Stygian Vise with Fire Res and Elemental damage with attack.",
                  "화염 저항 + 공격 시 원소 피해가 붙은 명계의 조임쇠.",
                  "'명계의 조임쇠는 ... 피해를 입힙니다' — 아이템이 공격하는 문장이 됐다"),
    Retranslation(
        "Note: In 3.29 there's a BIS mod using Rotmother's Ducat craft for \"Throw up to one "
        "additional trap if dual wielding\". Huge chance it will be gone in 3.30 [View Crafting Guide].",
        ("참고: 3.29 에는 부패모의 두캇(Rotmother's Ducat) 제작으로 붙이는 BIS 속성 "
         "'쌍수 장착 시 덫을 최대 1개 추가 투척' 이 있다. 3.30 에서는 사라질 가능성이 매우 높다. ",
         ""),
        "'3.30 [제작 가이드 보기]에 사라질 가능성' — 링크가 문장 안으로 끼어들었다",
    link_label="[제작 가이드 보기]"),
    Retranslation("2x Vermillion rings ilvl 82+ - Life, Chaos Res, Light Radius [View Crafting Guide]",
                  ("아이템 레벨 82 이상 주색 반지 2개 — 생명력, 카오스 저항, 시야 반경 ",
                   "[제작 ", "가이드 보기]"),
                  "링크 문구가 '[보다 제작가이드]' 로 어순이 뒤집혀 있었다 — 링크 안까지 고친다",
                  True),
    Retranslation("Anoint: Discipline And Training (1x Black & 2x Silver)",
                  "성유: 수양과 훈련 (검은빛 성유 1 + 은빛 성유 2)", "기름 이름 음차"),
    Retranslation(
        "Untouched Soul (Remember to bench craft to make all white sockets in other pieces)",
        "손길이 닿지 않은 영혼 (다른 부위 홈을 전부 흰색으로 만드는 벤치 제작을 잊지 마라)",
        "'모든 흰색 홈을 다른 조각으로 만들기' — 목적어와 장소가 뒤바뀌었다",
    ),
    Retranslation("Anoint = High Explosives (2x Verdant * 1x Silver)",
                  "성유 = 고성능 폭약 (신록빛 성유 2 + 은빛 성유 1)",
                  "'고폭탄' — 공식명은 고성능 폭약"),

    # 4.4
    Retranslation(
        "4.4 Post-Ubers (Week 2+) - Combatant added, Switch to AGoS if you want to",
        "4.4 우버 이후(2주 차 이상) — Combatant 합류, 원하면 AGoS 로 교체",
        "'Post-Ubers' 미번역",
    ),
    Retranslation(
        "Cast expands to 4: You, Blade Ambusher, Combatant (new - mapping merc), and AGoS "
        "(Animate Guardian of Smiting) to abuse Hallowed Monarch. Note: you can see me crafting all "
        "Evasion gear only. This is for sharing between the 2 mercs.",
        "구성이 넷으로 늘어난다: 본인, Blade Ambusher, Combatant(신규 — 맵 도는 용병), 그리고 "
        "거룩한 국왕을 활용하기 위한 AGoS(징벌의 수호자 기동). 참고: 내가 회피 장비만 제작하는 걸 "
        "보게 될 텐데, 용병 둘이 돌려 쓰기 위해서다.",
        "'시전는 4' — Cast 를 스킬 시전으로 오역",
    ),
    Retranslation(
        "Nycta's + a rare Shaper Shield with (1) High block chance, (2) Maximum life and "
        "(3) 5% Life on block",
        "닉타의 등불 + (1) 높은 막기 확률, (2) 최대 생명력, (3) 막기 시 생명력 5% 회복이 붙은 "
        "희귀 쉐이퍼 방패",
        "'Nycta의' 소유격만 남고 아이템명이 사라졌다",
    ),
    Retranslation(
        "2x Jewelled Foils with (1) Crafted Hit Cannot Be Evaded -> (2) Crit Chance -> "
        "(3) Attack Speed -> (4) Flat cold → (5) Crit Multi -> (6) Elemental damage with attack",
        "(1) 제작 '무조건 명중' → (2) 치명타 확률 → (3) 공격 속도 → (4) 고정 냉기 피해 → "
        "(5) 치명타 피해 배율 → (6) 공격 시 원소 피해 순으로 붙인 보석이 박힌 펜싱 검 2개",
        "'밋밋한 냉기' — flat 을 '밋밋한'으로 오역",
    ),
    Retranslation(
        "Luxury!!: 2x Paradoxica (Attack Speed + Elemental Penetration). Will need to trade the "
        "unique-amulet slot for a crafted Simplex Amulet/Reflected Amulet to compensate for the "
        "Fire Res loss.",
        "사치!!: 모순 2개 (공격 속도 + 원소 저항 관통). 화염 저항 손실을 메우려면 고유 목걸이 "
        "자리를 제작한 평범한 목걸이 / 반사 목걸이로 바꿔야 한다.",
        "'부적' — Amulet 의 공식 한국어명은 목걸이(Talisman 이 부적)",
    ),
    Retranslation("(or Foulborn Frostbreath)", "(또는 삿된 서리 숨결)",
                  "Foulborn 의 공식 접두사는 '삿된'"),
    Retranslation(
        "Note: If you have Kingmaker, please don't switch. Stick with Animate Guardian as an aura bot.",
        "참고: 실세가 있다면 교체하지 마라. 수호자 기동을 오라 봇으로 계속 쓰는 게 낫다.",
        "'수호자 기동을 아우라 봇으로 활용하세요' — Stick with(바꾸지 말라)가 사라졌다",
    ),
    Retranslation(
        "Evasion base with: (1) Onslaught for 6 seconds when hit - Essence of Insanity + "
        "(2) Fire res + (3) Abyssal socket",
        "회피 베이스: (1) 피격 시 6초 동안 맹공 — 광기의 에센스 + (2) 화염 저항 + (3) 심연 홈",
        "when hit 을 '적중 시'(공격 시)로 오역 — 피격 시가 맞다",
    ),
    Retranslation(
        'Luxury!!: Evasion base with "Crit chance is equal to overcapped Lightning res" (You will '
        "need to sell 60 Synaptic rings for Esh's mod on a Grasping mail and still only have 10% to "
        "get this specific mod. Given how unrealistic this goal is for most people, I would recommend "
        "NOT to target this even as your end goal. Unless you are Ben) [View Crafting Guide]",
        "사치!!: '치명타 확률이 초과된 번개 저항만큼 증가' 가 붙은 회피 베이스 "
        "(탐욕스러운 사슬옷에 Esh 속성을 띄우려면 시냅스 반지 60개를 상인에게 팔아야 하고, "
        "그러고도 이 속성이 뜰 확률은 10% 뿐이다. 대부분에게 얼마나 비현실적인 목표인지 생각하면 "
        "최종 목표로도 잡지 말라고 권하고 싶다. 당신이 Ben 이 아니라면) ",
        "'초과된 번개 res와 동일합니다' — 문장이 끊겨 조건이 안 읽힌다",
    link_label="[제작 가이드 보기]"),
    Retranslation(
        "Evasion based with (1) Fire Res -> (2) Attack Speed -> (3) +1 Abyssal Socket "
        "[View Crafting Guide]",
        "회피 기반, (1) 화염 저항 → (2) 공격 속도 → (3) 심연 홈 +1 ",
        "조사 누락",
    link_label="[제작 가이드 보기]"),
    Retranslation("Stygian Vise with (1) Elemental Damage with Attack and (2) Fire res via recomb",
                  "재조합으로 (1) 공격 시 원소 피해와 (2) 화염 저항을 붙인 명계의 조임쇠",
                  "'공격를 사용한 원소 피해' — 조사 오류 + via recomb 위치가 틀렸다"),
    Retranslation(
        "Enmity's Embrace + Call of the Void (This Uber Uber Elder ring is AMAZING for mapping!)",
        "원한의 품 + 공허의 부름 (이 우버 우버 엘더 반지는 맵 돌 때 정말 좋다!)",
        "'맵핑에게 정말 놀랍습니다' — 어색",
    ),
    Retranslation("Rotmother's Mutiny (Most likely will be gone in 3.30)",
                  "부패모의 반란 (3.30 에서는 사라질 가능성이 높다)", "어투 통일"),
    Retranslation(
        "Crafted rare +2 Gem Level Amulet on either a +1 to level of all skill gem Croaker Talisman "
        "base, or a 15% Maximum Life Gargantuan Talisman base [View Crafting Guide]:",
        ("젬 레벨 +2 를 제작한 희귀 목걸이. 베이스는 '모든 스킬 젬 레벨 +1' 이 붙은 "
         "Croaker Talisman 이나 '최대 생명력 15%' 가 붙은 Gargantuan Talisman 중 하나 ",
         " :"),
        "'민어 부적' — 야수 부적 베이스명은 공식 한국어 확인 불가라 원문 유지",
    link_label="[제작 가이드 보기]"),
    Retranslation("Untouched Soul (not shared with the Trapper due to different anointment)",
                  "손길이 닿지 않은 영혼 (성유가 달라서 트래퍼와는 돌려 쓰지 못한다)",
                  "'다른 기름부음으로 인해' 직역"),
    Retranslation(
        "A crafted Simplex Amulet with Fire Res and All Elemental Res (only if you go Paradoxica "
        "route for him)",
        ("화염 저항 + 모든 원소 저항을 제작해 붙인 평범한 목걸이 (그 용병을 ",
         "로 갈 때만)"),
        "'모순 경로를 사용하는 경우에만' 어색",
    link_label="모순 경로"),
    Retranslation("Anoint options:", "성유 선택지:", "'기름부음 옵션'"),
    Retranslation("<early> Ambidexterity (1x Amber, 1x Azure & 1x Black)",
                  "<초반> 양손잡이 (호박빛 성유 1 + 담청빛 성유 1 + 검은빛 성유 1)",
                  "기름 이름이 '호박색/하늘색/검정색'으로 음차됐다(양손잡이는 공식명이라 유지)"),
    Retranslation(
        "<mid> Lethality (1x Sepia, 1x Violet & 1x Silver) - Yes, this one will apply to all 3 "
        "elements of WildStrike as the anointment only checks the gem/skill tags",
        "<중반> 치명상 (적갈빛 성유 1 + 보랏빛 성유 1 + 은빛 성유 1) — 그렇다, 성유는 젬/스킬 "
        "태그만 보기 때문에 사나운 타격의 원소 3종 모두에 적용된다",
        "'<mid>' 미번역 + '3가지 요소' — element 를 '요소'로 오역",
    ),
    Retranslation("<late> Veteran's Wrath (1x Violet & 2x Golden)",
                  "<후반> Veteran's Wrath (보랏빛 성유 1 + 금빛 성유 2)",
                  "기름 이름 음차 — Veteran's Wrath 는 공식명 확인 불가라 원문 유지"),
    Retranslation("LUXURY:", "사치:", "표기 통일"),
    Retranslation("Unique Jewels", "고유 주얼", "'독특한 보석'"),
    Retranslation(
        "Foulborn The Red Dream (from Breach tree/ Twin bosses) + 7 Fire res tattoos from Kingsmarch",
        "삿된 붉은 꿈 (균열 트리 / 쌍둥이 보스) + Kingsmarch 에서 얻은 화염 저항 문신 7개",
        "Foulborn 미번역 + '브리치' 음차",
    ),
    Retranslation("Light of Meaning (life) (from Ritual boss) to combo with Unnatural Instinct",
                  "의미의 빛(생명력 버전) (의식 보스) — 기이한 본능과 조합",
                  "'(생명)' — Life version 은 생명력 버전"),
    Retranslation(
        "Bound By Destiny (from 3 Incarnations) - random 2x-influence can roll +10-15% max Life with "
        "2 Elder influenced gears.",
        "운명의 속박 (화신 3종) — 무작위 2중 영향력이 뜨면 엘더 영향 장비 2개로 최대 생명력 "
        "+10~15% 를 굴릴 수 있다.",
        "'무작위 2배 영향력' — 2x-influence 를 배수로 오독",
    ),
    Retranslation(
        "Dissolution of the Flesh (from Exarch)- (20-30)% MORE Maximum Life. Note that now instead of "
        "losing life on hit, your life will instead be reserved until you go 2 seconds without taking "
        "Damage. Cap block before slotting this in.",
        "살점의 융해 (작열의 총주교) — 최대 생명력 (20~30)% 증폭. 이제는 피격 시 생명력을 잃는 "
        "대신, 2초 동안 피해를 받지 않을 때까지 그만큼이 점유된다. 이걸 끼우기 전에 막기부터 "
        "최대치로 올려라.",
        "'이것을 슬롯에 넣기 전의 캡 블록입니다' — 명령문이 명사구가 됐다",
    ),
    Retranslation(
        "Luxury: Tecrod's Gaze (Note: will have to update all of your abyss jewel to Murderous now - "
        "look for Attack speed/Attack speed if crit recently/Fire Res)",
        "사치: 테크로드의 응시 (참고: 이제 심연 주얼을 전부 살인적인 눈 주얼로 바꿔야 한다 — "
        "공격 속도 / 최근 치명타 시 공격 속도 / 화염 저항을 노려라)",
        "'살인으로 업데이트' — Murderous Eye Jewel 을 형용사로 오역",
    ),


    # === 6장: 고티어 고유 아이템 & 사치 업그레이드 ===================================
    Retranslation(
        "You should already had Berek's Grip and Berek's Pass since they drop like flies.",
        "베렉의 손아귀와 베렉의 길은 워낙 흔하게 떨어지니 이미 갖고 있을 것이다.",
        "'파리처럼 떨어지기 때문에' — drop like flies 를 직역",
    ),
    Retranslation(
        "Vendor recipe the 3 Berek's rings and pray for max roll.",
        "베렉의 반지 3개를 상인 조합식에 넣고 최대 굴림이 뜨길 빌어라.",
        "'상인은 ... 제조하고' — 주어가 상인이 됐다",
    ),
    Retranslation(
        "Gamba all your leftover Pride Before the Fall div cards once you are done farming Taming.",
        "조련 파밍이 끝나면 남은 '몰락 직전의 긍지' 점술 카드는 전부 도박에 써라.",
        "'감바는 길들이기 파밍을 마친 후' — Gamba 를 주어로 오독",
    ),
    Retranslation(
        "A lot of people claimed the \u201cAdjacent Unique Amulet conversion\u201d mod do not work on this "
        "strat. I would still go for the Voyage setup though, as no official source confirming "
        "otherwise. RNG is RNG, just try your best to increase the chance.",
        "많은 사람이 '인접한 고유 목걸이 변환' 속성은 이 전략에서 안 먹는다고 주장했다. "
        "그래도 나는 Voyage 세팅으로 간다 — 반대를 확인해주는 공식 출처가 없기 때문이다. "
        "RNG 는 RNG 다. 확률을 올리는 데 최선을 다할 뿐이다.",
        "'부적' — Amulet 의 공식 한국어명은 목걸이",
    ),
    Retranslation(
        "Also try to roll your Clam Infested Shelf to have both Quant and Rarity. Having IIR in your "
        "gears will definitely help too.",
        "Clam Infested Shelf 도 아이템 수량과 희귀도가 둘 다 붙도록 굴려라. "
        "장비에 아이템 희귀도(IIR)가 있으면 확실히 도움이 된다.",
        "Quant/Rarity/IIR 미번역",
    ),
    Retranslation(
        "Hivebrain Gland - twin bosses: they have a fair chance to drop both (1) Foulborn The Red "
        "Dream/Nightmare and (2) Flesh of Xhest - the currency to flex between the 2 version of the "
        "jewel. Greywind is exclusive from this boss. But only has like 2-3% drop rate.",
        "벌레집 두뇌 분비선 — 쌍둥이 보스: (1) 삿된 붉은 꿈 / 악몽과 (2) Flesh of Xhest"
        "(주얼 두 버전을 오가는 재화)를 꽤 괜찮은 확률로 떨어뜨린다. Greywind 는 이 보스 전용이지만 "
        "드롭률은 2~3% 정도다.",
        "'공정한 기회를 갖습니다' — fair chance 직역",
    ),
    Retranslation(
        "For Foulborn The Red Dream only, you can also target birthing it from Breach Tree: Inc chance "
        "for Jewels -> Roll additional rarest outcome -> 50% inc chance for Breach/Foulborn -> 85% "
        "less chance for intel/dex/strength.",
        "삿된 붉은 꿈만 노린다면 균열 트리에서 탄생시키는 방법도 있다: 주얼 확률 증가 → "
        "가장 희귀한 결과 추가 굴림 → 균열/삿된 확률 50% 증가 → 지능/민첩/힘 확률 85% 감소.",
        "'인텔/덱스/강도' — 능력치 약어를 음차·오역",
    ),
    Retranslation(
        "To utilize this jewel, you will need 6-7 Fire res tattoos depending on how you flex your "
        "tree. Send 4200 Blue Zanth to Ngakanu. It will guaranteed at least 1 Strength tattoo. You "
        "would look for Fire res and Block chance tatts for this build.",
        "이 주얼을 쓰려면 트리를 어떻게 배분하느냐에 따라 화염 저항 문신이 6~7개 필요하다. "
        "Ngakanu 로 푸른도꼬마리 4,200개를 보내라. 최소 힘 문신 1개는 보장된다. "
        "이 빌드에서 노릴 문신은 화염 저항과 막기 확률이다.",
        "'Blue Zanth' 미번역 + 'Block Chance tatts' 미번역",
    ),
    Retranslation("9% Drop rate from Venarius (Cortex)", "베나리우스(코텍스 지도 보스)에서 드롭률 9%",
                  "Venarius 는 Cortex 지도의 보스인데 괄호가 지도명인지 보스명인지 안 읽힌다"),
    Retranslation(
        "To get Cortex, spam Synthesis Maps. It is a 25% drop rate from any of the 4.",
        "코텍스를 얻으려면 결합된 지도를 계속 돌려라. 4종 중 어디서든 25% 확률로 나온다.",
        "'합성 맵' — Synthesised Map 의 공식 한국어명은 결합된 지도",
    ),
    Retranslation(
        "Go farm any T1 map (or any level 68 area) -> pick up a chance-able 2x2 shield.",
        "T1 지도(또는 레벨 68 지역)를 파밍해서 기회의 오브를 쓸 수 있는 2x2 방패를 주워라.",
        "'확률적으로 2x2 방패를 획득' — chance-able 은 '기회의 오브 대상'이라는 뜻",
    ),
    Retranslation(
        "Chance orb plus reroll rarity using bench craft -> until you have a 2x2 Unique Shield with "
        "ilevel 68+ (the closer the better) for Ancient Orb-ing.",
        "기회의 오브를 쓰고 벤치 제작으로 희귀도를 다시 굴린다 → 고대의 오브를 쓸 "
        "아이템 레벨 68 이상(높을수록 좋다) 2x2 고유 방패가 나올 때까지.",
        "'기회 구' — Orb of Chance 의 공식명은 기회의 오브",
    ),
    Retranslation("Boat Ancient Orb = 4 outcomes without any intangibility.",
                  "보트 고대의 오브 = 결과 4개. 비실체화가 전혀 쌓이지 않는다.",
                  "'비실체화이 없는 결과 4개' 조사 오류"),
    Retranslation(
        "I got lucky with mine in 29 Ancient Orbs, which equals to ~7 boat craft.",
        "나는 고대의 오브 29개 만에 운 좋게 떴다. 보트 제작 7회쯤에 해당한다.",
        "'29개의 고대 오브를 얻었는데' — 소모한 것을 얻은 것으로 오역",
    ),
    Retranslation(
        "Go to Act 8 Harbour Bridge (or any level 58 area) -> pick up a chance-able pair of gloves.",
        "액트 8 Harbour Bridge(또는 레벨 58 지역)로 가서 기회의 오브를 쓸 수 있는 장갑을 주워라.",
        "'기회가 있는 장갑' — chance-able 오역",
    ),
    Retranslation(
        "Chance orb plus reroll rarity using bench craft -> until you have a pair of Unique Gloves "
        "with ilevel 58+ (the closer the better) for Ancient Orb-ing.",
        "기회의 오브를 쓰고 벤치 제작으로 희귀도를 다시 굴린다 → 고대의 오브를 쓸 "
        "아이템 레벨 58 이상(높을수록 좋다) 고유 장갑이 나올 때까지.",
        "'고대의 오브-ing' 미번역",
    ),
    Retranslation("6.9. Bound by Destiny", "6.9. 운명의 속박", "'운명에 묶여' — 고유 주얼 이름이다"),
    Retranslation(
        "Exclusive drop from 3 Incarnations. You should have a lot of these Memories while farming for "
        "Enmity's Embrace. Also should have a lot of redundant fragment for Uber Fear and Uber Neglect "
        "while farming for Hallowed Monarch.",
        "화신(Incarnation) 3종 전용 드롭이다. 원한의 품을 파밍하는 동안 이 기억들이 많이 쌓였을 "
        "것이다. 거룩한 국왕을 파밍하는 동안에는 Uber Fear 와 Uber Neglect 용 조각도 남아돌게 된다.",
        "'이런 추억이 많이 쌓였을 겁니다' — Memory(기억 아이템)를 '추억'으로 오역",
    ),
    Retranslation(
        'Look for "15% Maximum Life if 2 Elder influenced gears equipped" mod.',
        "'엘더 영향 장비 2개 장착 시 최대 생명력 15%' 속성을 노려라.",
        "'기어가 장착된 경우' — gear 음차",
    ),
    Retranslation(
        "Exclusive drop from Exarch. Low drop rate of only 2%. Up to 30% MORE Life. A very strong "
        "boost to your damage, but be very careful with how your defence works now. Your bare minimum "
        "is capping your blocks before using this jewel.",
        "작열의 총주교 전용 드롭. 드롭률은 2% 밖에 안 된다. 최대 생명력이 최대 30% 증폭된다. "
        "피해가 크게 오르지만, 이제 방어가 어떻게 도는지 매우 조심해야 한다. "
        "최소한 막기를 최대치로 올린 다음에 이 주얼을 써라.",
        "'최소한으로 블록을 제한해야 합니다' — cap block 오역",
    ),
    Retranslation(
        "In the Abyss Depth's wheel in Atlas skill tree, get all the small nodes for Amanamu and "
        "Ulaman.",
        "아틀라스 패시브 트리의 Abyss Depths 구간에서 아마나무와 울라만 관련 작은 노드를 전부 찍어라.",
        "'휠' 음차",
    ),
    Retranslation(
        "Run map with (1) Abyss scarab and (2) Abyss Scarab of Descending to guarantee boss fight. "
        "Without scarabs, just get the Depth chance in Atlas skill tree and alch & go.",
        "(1) 심연 갑충석과 (2) Abyss Scarab of Descending 을 넣고 맵을 돌려 보스전을 확정지어라. "
        "갑충석이 없으면 아틀라스 패시브 트리에서 심연 등장 확률만 챙기고 연금술의 오브만 발라서 돌면 된다.",
        "'연금술을 받으세요' — alch & go 오역",
    ),
    Retranslation("It is a 3% chance to drop from either boss.", "어느 보스에서든 3% 확률로 떨어진다.",
                  "어투 통일"),
    Retranslation(
        "Note: will have to update all of your abyss jewel to Murderous now - look for Attack "
        "speed/Attack speed if crit recently/Fire Res. Best way is to Harvest reforge speed.",
        "참고: 이제 심연 주얼을 전부 살인적인 눈 주얼로 바꿔야 한다 — 공격 속도 / 최근 치명타 시 "
        "공격 속도 / 화염 저항을 노려라. 가장 좋은 방법은 수확 재련 속도다.",
        "'살인으로 업데이트' — Murderous Eye Jewel 을 형용사로 오역",
    ),
    Retranslation(
        "This ring enables Flame Link flat fire damage to chill and apply to your Combatant's Herald "
        "of Ice too. Thus makes the clear much more enjoyable regardless of the skill your Combatant "
        "has.",
        "이 반지가 있으면 화염의 연결의 고정 화염 피해가 냉각을 일으키고, Combatant 의 얼음의 "
        "전령에도 적용된다. 덕분에 Combatant 가 어떤 스킬을 쓰든 클리어가 훨씬 쾌적해진다.",
        "'플랫 화염 피해를 식혀서' — chill(냉각)을 '식히다'로 직역",
    ),
    Retranslation("Spam Intervention Safehouses.", "개입(Intervention) 은신처를 반복해서 돌려라.",
                  "'스팸 개입 안전 가옥' — 명사 나열이 됐다"),
    Retranslation(
        "Best unveils = Elemental Penetration & Attack Speed. We have a lot of flat fire from Flame "
        "Link. There's no need for Phys mod like normal unveil.",
        "가장 좋은 봉인 해제 = 원소 저항 관통 & 공격 속도. 화염의 연결에서 고정 화염 피해가 많이 "
        "나온다. 보통의 봉인 해제처럼 물리 속성을 챙길 필요가 없다.",
        "'화염의 연결에서 불이 많이 붙었습니다' — flat fire 를 '불이 붙다'로 오역",
    ),
    Retranslation(
        "You will need to take care of 2 things for your Combatant merc before switching to dual "
        "Paradoxica's:",
        "모순 쌍수로 넘어가기 전에 Combatant 용병 쪽에서 두 가지를 처리해야 한다:",
        "'듀얼 모순로 전환하기 전에' 음차",
    ),
    Retranslation(
        "Get either a Simplex Amulet (Heist) to craft Fire res and All Elemental res. Or a very good "
        "reflected Fire res amulet. This is to compensate the Fire res loss when you stop using "
        "Untouched Soul.",
        "화염 저항과 모든 원소 저항을 제작해 붙일 평범한 목걸이(강탈)를 구하거나, 아주 좋은 반사 "
        "화염 저항 목걸이를 구해라. 손길이 닿지 않은 영혼을 빼면서 잃는 화염 저항을 메우기 위한 것이다.",
        "'강탈'/'부적' 표기 혼용",
    ),
    Retranslation(
        "Get accuracy in every other piece of gear: Helmet, Gloves and Murderous Abyss Jewels since "
        "you no longer have \u201cHit cannot be evaded\u201d craft anymore.",
        "'무조건 명중' 제작을 더는 쓸 수 없으므로, 투구·장갑·살인적인 눈 주얼 등 나머지 "
        "장비 전부에서 정확도를 챙겨라.",
        "'정확도를 높이세요' — 원인절이 뒤로 밀렸다",
    ),
    Retranslation(
        "Superb trapper belt from normal Incarnation of Neglect. If it's not that we have to combo "
        "Enmity's Embrace and Untouched Soul due to the restriction of the build allowing our merc to "
        "only wear 2 uniques, this is on-par with the +1 Additional Trap belt from Voyage.",
        "일반 Incarnation of Neglect 에서 나오는 최상급 트래퍼 허리띠. 용병이 고유 아이템을 2개만 착용할 "
        "수 있다는 빌드 제약 때문에 원한의 품과 손길이 닿지 않은 영혼을 조합해야 하는 상황만 "
        "아니라면, Voyage 의 '덫 +1' 허리띠와 동급이다.",
        "'최고급 사냥꾼 벨트' — trapper 를 '사냥꾼'으로 오역",
    ),
    Retranslation(
        "A very high drop rate of 38%. Farm this while you are struggling with obtaining Enmity's "
        "Embrace or Untouched Soul.",
        "드롭률이 38% 로 매우 높다. 원한의 품이나 손길이 닿지 않은 영혼이 안 나와 고생하는 동안 "
        "이걸 파밍해라.",
        "어투 통일",
    ),
    Retranslation(
        '6.15. Grasping Mail with "Critical Strike Chance is increased by Overcapped Lightning '
        'Resistance" (Both Mercs)',
        "6.15. '치명타 확률이 초과된 번개 저항만큼 증가' 가 붙은 탐욕스러운 사슬옷 (용병 둘 다)",
        "'탐욕스러운 사슬옷은 ... 증가합니다' — 제목이 서술문이 됐다",
    ),
    Retranslation("Warning: This is a super tedious farm.", "경고: 극도로 지루한 파밍이다.",
                  "'지루한 농장' — farm 을 '농장'으로 오역"),
    Retranslation(
        "This Grasping Mail can only be acquired by vendor recipe 60 Breach Rings.",
        "이 탐욕스러운 사슬옷은 균열 반지 60개 상인 조합식으로만 얻을 수 있다.",
        "'상인 레시피 60 브리치 링' 음차",
    ),
    Retranslation(
        "A random rare Breach Ring is guaranteed to be dropped from Vruun (Unstable Breach Boss).",
        "Vruun(Unstable Breach 보스)에게서 무작위 희귀 균열 반지가 반드시 떨어진다.",
        "어순 정리",
    ),
    Retranslation(
        "The mod we are looking for is an Esh mod. You will want to sell 60 Synaptic Rings for 100% "
        "Esh mod. You can certainly mix in other Breach ring, but it will pollute your mod pool in the "
        "final Grasping Mail output. Your call here. I filter only Synaptic Rings and ignore all the "
        "rest.",
        "우리가 노리는 건 Esh 속성이다. Esh 속성을 100% 로 만들려면 시냅스 반지 60개를 팔아야 한다. "
        "다른 균열 반지를 섞어도 되지만, 최종 탐욕스러운 사슬옷의 속성 풀이 오염된다. 판단은 각자 "
        "알아서. 나는 시냅스 반지만 필터에 띄우고 나머지는 전부 무시한다.",
        "'여기로 전화하세요' — Your call 을 전화로 오역",
    ),
    Retranslation(
        "Get the node for (1) Only Unstable Breach and (2) Chance for double Breach bosses in Atlas "
        "Skill Tree.",
        "아틀라스 패시브 트리에서 (1) Unstable Breach 만 나오게 하는 노드와 (2) 균열 보스 2마리 "
        "확률 노드를 찍어라.",
        "노드 이름이 영문 그대로 남아 무엇을 찍으라는 건지 안 읽힌다",
    ),
    Retranslation(
        "Use (1) Breach scarabs and (2) Breach scarab of Marshal to guarantee Boss fight. Put It That "
        "Fled in Intervention for Breach scarab chest to stock up your scarabs.",
        "(1) 균열 갑충석과 (2) Breach Scarab of the Marshal 을 써서 보스전을 확정지어라. "
        "달아난 그것(It That Fled)을 개입(Intervention) 부서에 배치하면 균열 갑충석 상자가 나와 "
        "갑충석을 비축할 수 있다.",
        "'갑충석 상자를 파괴하여' — 배신 배치 지시가 통째로 사라지고 없는 동작이 들어갔다",
    ),
    Retranslation(
        'The mod we are looking for "Critical Strike Chance is increased by Overcapped Lightning '
        'Resistance" is a super low weight mod even with 60 Synaptic Rings. It\'s only a 10% to hit.',
        "우리가 노리는 '치명타 확률이 초과된 번개 저항만큼 증가' 는 시냅스 반지 60개를 써도 가중치가 "
        "극도로 낮은 속성이다. 적중 확률이 10% 밖에 안 된다.",
        "'초경량 모드' — low weight(가중치)를 무게로 오역",
    ),
    Retranslation(
        "You will then have to win the recomb with your Syndicate's Garb because none of your merc can "
        "wear a Grasping Mail.",
        "그다음에는 연합의 의복으로 재조합을 성공시켜야 한다. 용병 중 누구도 탐욕스러운 사슬옷을 "
        "입을 수 없기 때문이다.",
        "'귀하는' 존대 혼용",
    ),
    Retranslation(
        "Boat Fracture Orb and hope it hits the mod if you somehow succeeded all of the above.",
        "위를 다 성공했다면 보트 Fracture Orb 를 써서 그 속성에 걸리길 빌어라.",
        "조건절이 뒤로 밀려 순서가 뒤집혔다",
    ),
    Retranslation(
        'If Fracture hits -> Boat Resonator using "Hollow Fossil" (Abyssal socket) and "Glyphic '
        'Fossil" (random Corrupted Essence mod) to hit "Onslaught 6 seconds on hit" and an Abyssal '
        "Socket.",
        "분열이 걸리면 → '공허의 화석'(심연 홈)과 '상형 문자 화석'(무작위 타락한 에센스 속성)으로 "
        "보트 공명기를 돌려 '피격 시 6초 동안 맹공' 과 심연 홈을 노린다.",
        "'적중 시 맹공격 6초' — on hit(피격 시) 오역",
    ),
    Retranslation("6.16. Tailoring Orb & Volatile Vaal Orb on Kaom's Heart",
                  "6.16. 카옴의 심장에 재단 오브 + 휘발성 바알 오브",
                  "'카옴의 심장의 휘발성 바알 오브' — 소유격이 겹쳤다"),
    Retranslation("Tailoring Orb can be farmed in Heist (Blueprint reward).",
                  "재단 오브는 강탈(청사진 보상)에서 파밍할 수 있다.", "'습격' 표기"),
    Retranslation("Boat craft your Kaom's with a Tailoring Orb.",
                  "카옴의 심장을 재단 오브로 보트 제작해라.",
                  "'Kaom을 보트로 제작' — 아이템명이 사람 이름이 됐다"),
    Retranslation(
        'The Enchantment you are looking for is "15% increased Explicit Life modifier & -3 to Maximum '
        'Sockets". Can settle with "8% Increased Explicit Life" too.',
        "노리는 마법부여는 '명시 생명력 속성 15% 증가 & 최대 홈 -3' 이다. "
        "'명시 생명력 8% 증가' 로 타협해도 된다.",
        "'당신이 찾고 있는 마법' — Enchantment 를 '마법'으로 오역",
    ),
    Retranslation("You can then push it further by throwing a Volatile Vaal Orb on top of it.",
                  "그 위에 휘발성 바알 오브를 더 던져서 한 번 더 밀어붙일 수 있다.", "조사 정리"),
    Retranslation(
        "Volatile Vaal Orb is now an exclusive reward in Forbidden Sanctum. I got 2 out of 5 runs. "
        "Pretty common in Floor 4.",
        "휘발성 바알 오브는 이제 금단의 지성소 전용 보상이다. 나는 5회 돌아서 2개를 얻었다. "
        "4층에서는 꽤 흔하다.",
        "'5점 만점에 2점' — 5회 중 2회를 점수로 오독",
    ),
    Retranslation("It cannot be boat crafted. So just yolo and win the gamble.",
                  "이건 보트 제작이 안 된다. 그냥 욜로로 질러서 도박에 이겨라.", "어투 통일"),
    Retranslation(
        "The maximum ceiling of this combination is: 1000 (base) * 1.15 (Tailoring Orb) * 1.22 "
        "(Maximum roll on Volatile Vaal Orb) = 1403 Life.",
        "이 조합의 상한은 1000(기본) × 1.15(재단 오브) × 1.22(휘발성 바알 오브 최대 굴림) = "
        "생명력 1403 이다.",
        "'휘발성의 최대 굴림 바알 오브' — 수식어가 잘렸다",
    ),
    Retranslation(
        "Note: This is definitely something you SHOULD gamba in end game. All of these are "
        "deterministic farming. I got a +1140 Kaom's (equal to 1 more piece of gear with T1 Maximum "
        "Life) and it already boosted my total Life to +700.",
        "참고: 이건 엔드게임에서 반드시 질러볼 만하다. 여기 나오는 건 전부 확정적 파밍이다. "
        "나는 +1140 카옴의 심장(최대 생명력 T1 이 붙은 장비를 한 부위 더 낀 것과 같다)을 얻었고, "
        "그것만으로 총 생명력이 +700 늘었다.",
        "'결정론적 농업' — farming 을 '농업'으로 오역",
    ),
    Retranslation("6.17. Vaal Orb on Ceinture of Benevolence", "6.17. 관대함의 띠에 바알 오브",
                  "'관대함의 띠의 바알 오브' — 소유격 오역"),
    Retranslation("Pick a better visual for Cloth Belt Uniques in your Filter.",
                  "필터에서 헝겊 허리띠 고유 아이템이 더 잘 보이도록 설정해라.",
                  "'헝겊 허리띠개의 고유 아이템' — 수량사가 잘못 붙었다"),
    Retranslation(
        "Can also farm Alva's temple for double corrupt room (Tier 3 Locus of Corruption) if you have "
        "some to spare. I would save these for Nycta's Lantern and Hallowed Monarch.",
        "여유가 있으면 알바의 사원에서 이중 타락 방(타락의 현장(3등급))을 파밍해도 된다. "
        "나라면 이건 닉타의 등불과 거룩한 국왕에 아껴두겠다.",
        "'Tier 3 부패 Locus' 미번역",
    ),
    Retranslation("Mods that you are looking for are:", "노리는 속성은 다음과 같다:",
                  "'당신이 찾고 있는 모드' — mod 는 속성"),
    Retranslation("% Rarity of Items found", "발견하는 아이템 희귀도 %", "'발견된 아이템의 희귀도(%)'"),
    Retranslation("Bleeding cannot be inflicted on you", "출혈에 걸리지 않음",
                  "'출혈은 당신에게 가해질 수 없습니다' — 수동태 직역"),
    Retranslation("Cannot be poisoned", "중독되지 않음", "어투 통일"),
    Retranslation("Movement/Attack Speed during flasks", "플라스크 효과 중 이동/공격 속도",
                  "'플라스크 중' — during flask effect"),
    Retranslation(
        "Farm Alva's temple for double corrupt room (Tier 3 Locus of Corruption).",
        "알바의 사원을 파밍해서 이중 타락 방(타락의 현장(3등급))을 노려라.",
        "'농장 Alva의 사원' — 어순 붕괴",
    ),
    Retranslation("+1 to All Fire Skill gem (Best - only 1.5% chance to hit though)",
                  "모든 화염 스킬 젬 +1 (최고 — 다만 적중 확률은 1.5% 뿐이다)",
                  "'모두 +1 화염 스킬 젬' 어순"),
    Retranslation(
        "Attack speed (yes, local attack speed in weapon does affect your Shield Charge)",
        "공격 속도 (그렇다, 무기의 로컬 공격 속도는 방패 돌진에도 영향을 준다)",
        "어투 통일",
    ),
    Retranslation("6.19. Double corrupt on Hallowed Monarch", "6.19. 거룩한 국왕 이중 타락",
                  "'거룩한 국왕의 이중 부패' — corrupt 는 타락"),
    Retranslation("A lot of good corruptions on helmets:", "투구에는 좋은 타락 결과가 많다:",
                  "'좋은 타락이 많이 있습니다'"),
    Retranslation("+2 Socketed AOE gem (for Purity of Elements/Vitality/Precision)",
                  "장착된 AOE 젬 +2 (원소의 순수함 / 활력 / 정밀함용)", "'+2 홈 AOE 젬' 어순"),
    Retranslation("+2 Socketed Aura gem (for Purity of Elements/Vitality/Precision)",
                  "장착된 오라 젬 +2 (원소의 순수함 / 활력 / 정밀함용)", "'오라 보석' — Gem 은 젬"),
    Retranslation("+2 Socketed Duration gem (for Flame Link)",
                  "장착된 지속시간 젬 +2 (화염의 연결용)", "'홈에 장착된 지속시간 보석 +2개' 어순"),
    Retranslation("+2 Socketed Fire gem (for Flame Link)",
                  "장착된 화염 젬 +2 (화염의 연결용)", "'홈에 장착된 화염 보석 +2개' 어순"),

    # === 7장: 필터에 띄울 베이스 ================================================
    Retranslation(
        "Leviathan Greaves (ilvl 81+/86) - Can settle with 81. Base 86 is for 35% movement speed.",
        "레비아탄 각반 (아이템 레벨 81+ / 86) — 81 로 타협해도 된다. 86 베이스라야 이동 속도 35% 가 뜬다.",
        "'81로 정착할 수 있습니다' — settle 을 '정착'으로 오역",
    ),
    Retranslation(
        "Elder-influenced Gloves (by throwing Guardian maps to your Kingsmarch mappers)",
        "엘더 영향 장갑 (Kingsmarch 지도 제작자에게 가디언 지도를 먹여서)",
        "'매퍼에게 던짐' 음차",
    ),
    Retranslation("Crafting - Your Merc(s)", "제작 — 용병 장비", "'귀하의 용병' 존대 혼용"),
    Retranslation("Crafting - Your character", "제작 — 본인 장비", "'당신의 캐릭터'"),
    Retranslation(
        "Jewelled Foil (ilevel 77+) for T1 attack speed, T1 crit chance, and T1 crit multi",
        "보석이 박힌 펜싱 검 (아이템 레벨 77+) — T1 공격 속도, T1 치명타 확률, T1 치명타 피해 배율용",
        "for 가 사라져 용도가 안 읽힌다",
    ),
    Retranslation(
        "Gutting Knife (ilevel 73+) for T1 crit chance and T1 crit multi",
        "내장 제거용 단도 (아이템 레벨 73+) — T1 치명타 확률, T1 치명타 피해 배율용",
        "for 가 사라져 용도가 안 읽힌다",
    ),
    Retranslation(
        "Majestic Pelt, Syndicate's Garb, Velour Gloves and Velour Boots (ilevel 84+) for T1 Fire res. "
        "Note: Evasion base only so you can switch between your mercs.",
        "압도적인 가죽모, 연합의 의복, 벨루어 장갑, 벨루어 장화 (아이템 레벨 84+) — T1 화염 저항용. "
        "참고: 회피 베이스만 쓴다. 그래야 용병끼리 돌려 쓸 수 있다.",
        "'회피 베이스만 사용하므로' — 인과가 뒤집혔다",
    ),

    # === 8장: 제작 =============================================================
    Retranslation(
        "AllFlame benchcraft is extremely powerful since it can return 2-4 outcomes for you to choose "
        "from, depending on the currency used.",
        "올플레임 벤치 제작은 매우 강력하다. 사용한 화폐에 따라 고를 수 있는 결과를 2~4개 돌려주기 "
        "때문이다.",
        "'통화' — currency 는 화폐",
    ),
    Retranslation(
        "Exception: does NOT work with Vaal Orb and Volatile Vaal Orb. Mirror of Kalandra is pointless "
        "(outcome always 1). Scouring will technically work but is pointless too.",
        "예외: 바알 오브와 휘발성 바알 오브에는 안 통한다. 칼란드라의 거울은 의미가 없다"
        "(결과가 항상 1개다). 정제의 오브는 원리상 되긴 하지만 역시 의미가 없다.",
        "'수색은 기술적으로는 효과가' — Scouring 을 '수색'으로 오역",
    ),
    Retranslation(
        "Downside - Intangibility: you can't \u201cspam\u201d AllFlame crafting too much on a single item. "
        "Ghostly items gain \u201cintangibility\u201d after each Boat craft. More intangibility means higher "
        "chance for only 1 outcome.",
        "단점 — 비실체화: 한 아이템에 올플레임 제작을 무한정 반복할 수는 없다. 유령 아이템은 보트 "
        "제작을 할 때마다 '비실체화'가 쌓인다. 비실체화가 높을수록 결과가 1개만 나올 확률이 올라간다.",
        "'너무 많은 것을 제작하여 AllFlame \"스팸\"을 보낼 수 없습니다' — 어순 붕괴",
    ),
    Retranslation(
        "This does not apply to Ancient Orb, since Ancient Orb converts the item into a completely "
        "different base entirely rather than modifying it in place. We can abuse it to get our "
        "Rathpith and Gravebind.",
        "고대의 오브에는 이게 적용되지 않는다. 고대의 오브는 아이템을 그 자리에서 고치는 게 아니라 "
        "완전히 다른 베이스로 바꿔버리기 때문이다. 이 점을 이용해 래스피스 구체와 무덤의 속박을 "
        "얻을 수 있다.",
        "'항목을 제자리에서 수정' — item 을 '항목'으로 오역",
    ),
    Retranslation(
        "The plan is to recomb a shield with (1) T1 Maximum Life + (2) T2+ Attack Block Chance, and "
        "pray for a Shaper slam to hit (3) Recover 3-5% life on block.",
        "계획은 (1) T1 최대 생명력 + (2) T2 이상 공격 막기 확률이 붙은 방패를 재조합한 뒤, "
        "쉐이퍼 슬램으로 (3) 막기 시 생명력 3~5% 회복이 뜨길 비는 것이다.",
        "'블록의 생명력을 3~5% 회복합니다' 가 별개 문장으로 잘렸다",
    ),
    Retranslation(
        "Base = Ezomyte Tower Shield i81 (i86 is best but it will take ages to farm this base).",
        "베이스 = 에조미어 거대 방패 아이템 레벨 81 (86 이 가장 좋지만 그 베이스를 파밍하는 데 "
        "한참 걸린다).",
        "'Base =' 미번역",
    ),
    Retranslation("Recomb T1 Maximum Life & T2+ Chance to Block.",
                  "T1 최대 생명력과 T2 이상 막기 확률을 재조합한다.",
                  "'T2+ 차단 기회' — Block 을 '차단'으로 오역"),
    Retranslation(
        "Lock prefix → either Harvest Reforge Critical (for \u201cReduced Damage from Critical Strike\u201d) OR "
        "Harvest Reforge Physical (for \u201cPhys Reduction\u201d).",
        "접두어 잠금 → 수확 재련 치명타('치명타 피해 감소'를 노릴 때) 또는 수확 재련 물리"
        "('물리 피해 감소'를 노릴 때) 중 하나.",
        "'수확 재련 [Critical|치명타]' — 번역 메모가 본문에 남았다",
    ),
    Retranslation(
        "Your call. \u201cReduce damage from Crit\u201d will be redundant once your AG wear Garb of Ephemeral. "
        "But choosing Refore Phys has a huge chance to add \u201cReflect # phys\u201d which is a super trash mod "
        "into your open prefix. I leave this 3rd prefix empty to have a chance to craft \u201c+2 Level of "
        "Socketed Support Gem\u201d for our Flame Link + Empower combo.",
        "판단은 각자 알아서. AG 가 덧없는 자의 의복을 입으면 '치명타 피해 감소'는 남아돌게 된다. "
        "하지만 재련 물리를 고르면 빈 접두어 자리에 '물리 피해 # 반사' 라는 최악의 속성이 붙을 "
        "확률이 크다. 나는 화염의 연결 + 강화 보조 조합을 위해 '장착된 보조 젬 레벨 +2' 를 제작할 "
        "여지를 남기려고 이 세 번째 접두어를 비워 둔다.",
        "'당신의 전화' — Your call 을 전화로 오역",
    ),
    Retranslation(
        "If suffixes are filled, yolo Annul and pray - need at least 1 empty suffix for the next step.",
        "접미어가 꽉 찼으면 소멸의 오브를 욜로로 지르고 빌어라 — 다음 단계에 빈 접미어가 "
        "최소 1개 필요하다.",
        "'yolo 무효화하고' 미번역",
    ),
    Retranslation(
        "Boat craft Shaper Exalted Orb for 2 outcomes, looking for Recover % Life on Block (Shaper "
        "slam hits this at 800/8000 ≈ 10%, vs Warlord's 250/5250 ≈ 4.7%). With AllFlame/Boat craft you "
        "effectively get a ~20% chance to hit it.",
        "쉐이퍼 엑잘티드 오브로 보트 제작해 결과 2개를 받고, '막기 시 생명력 % 회복' 을 노린다"
        "(쉐이퍼 슬램은 800/8000 ≈ 10%, 전쟁군주는 250/5250 ≈ 4.7%). 올플레임/보트 제작을 쓰면 "
        "실질 적중 확률이 20% 정도가 된다.",
        "'2개의 결과에 대해 ... 찾습니다' 어순",
    ),
    Retranslation("If successful", "성공했다면", "어투 통일"),
    Retranslation(
        'With open prefix: Benchcraft "+2 to level of Socketed Support Gem" (only if you have Empower '
        "-> Put your Flame Link/Empower here).",
        "빈 접두어가 있으면: '장착된 보조 젬 레벨 +2' 를 벤치 제작한다 (강화 보조가 있을 때만 → "
        "화염의 연결 / 강화 보조를 여기에 넣는다).",
        "'개방형 접두사 포함' — open prefix 오역",
    ),
    Retranslation("With open suffix: Benchcraft anything phys reduction/attribute/res.",
                  "빈 접미어가 있으면: 물리 피해 감소 / 능력치 / 저항 중 아무거나 벤치 제작한다.",
                  "'개방형 접미사 사용' 오역"),
    Retranslation("WHAT IF YOU DON'T HIT YOUR SHAPER SLAM:", "쉐이퍼 슬램이 안 떴다면:",
                  "'어떻게 되나요?' — 제목인데 의문문이 됐다"),
    Retranslation("(Recommended) Settle with it - still a very good shield, upgrade later.",
                  "(권장) 그냥 만족해라 — 그것만으로도 아주 좋은 방패다. 업그레이드는 나중에.",
                  "'방어막' — shield 는 방패"),
    Retranslation("OR lock prefix → Harvest Reforge Life again (~8% chance).",
                  "또는 접두어를 잠그고 → 수확 재련 생명력을 다시 돌린다(확률 8% 정도).",
                  "'수확 재련 생명력 회복' — Reforge Life 오역"),
    Retranslation(
        "OR start fresh, treating it as just another Shaper-influenced base, Harvest Reforge Life "
        "until both T3+ Life and Recover % Life on Block hit, then multimod whatever.",
        "또는 그냥 쉐이퍼 영향 베이스 하나로 치고 처음부터 다시 — T3 이상 생명력과 '막기 시 생명력 "
        "% 회복' 이 둘 다 뜰 때까지 수확 재련 생명력을 돌린 다음, 멀티모드로 나머지를 채운다.",
        "'Life를 유지한 다음 multimod를 사용합니다' — 원문 구조가 무너졌다",
    ),
    Retranslation(
        "Allow me to post Ben's shield and another example here. Both of these are not from me since "
        "I used Svalinn since day 2 (my bad).",
        "여기에 Ben 의 방패와 다른 예시를 올려둔다. 둘 다 내 것이 아니다 — 나는 2일 차부터 "
        "스발린을 썼다(내 잘못이다).",
        "'나쁜 일입니다' — my bad 직역",
    ),
    Retranslation("8.2 Your Helmet (cheap)", "8.2 본인 투구 (저렴한 버전)", "'투구(저렴함)'"),
    Retranslation(
        "Need an Armour based helmet with (1) Maximum Life and (2) Light Radius. The plan is to birth "
        "well-rolled rares via the (nerfed) Breach tree, then recomb it with a Giantslayer Helmet with "
        'T1 "Light Radius/Global Accuracy" mod.',
        "(1) 최대 생명력과 (2) 시야 반경이 붙은 방어도 기반 투구가 필요하다. 계획은 (너프된) 균열 "
        "트리로 잘 굴린 희귀 아이템을 탄생시킨 다음, T1 '시야 반경 / 전역 정확도' 가 붙은 거인 처형자 "
        "투구와 재조합하는 것이다.",
        "'글로벌 정확도' 음차",
    ),
    Retranslation("With Giantslayer Helmet i81:", "거인 처형자 투구 아이템 레벨 81 쪽:",
                  "'i81 사용:' 미번역"),
    Retranslation(
        "Harvest Reforge Attack T1 %Inc 15% Light Radius/Global Accuracy - cheap to spam since only 2 "
        "Attack-tagged mods exist besides Accuracy Rating.",
        "수확 재련 공격으로 T1 '시야 반경 / 전역 정확도 15% 증가' 를 노린다 — 정확도 등급 말고는 "
        "공격 태그 속성이 2개뿐이라 반복 비용이 싸다.",
        "'스팸에 저렴합니다' 직역",
    ),
    Retranslation('Alternative: alteration spam (suffix is called "Of Radiance").',
                  "대안: 변화의 오브 반복 (접미어 이름은 'Of Radiance' 다).",
                  "'변형 스팸' — alteration 은 변화의 오브"),
    Retranslation('Alternative: Alteration spam (suffix is called "Of Radiance").',
                  "대안: 변화의 오브 반복 (접미어 이름은 'Of Radiance' 다).",
                  "'변형 스팸' — alteration 은 변화의 오브"),
    Retranslation(
        "With Breach tree, birth with Provisioning Wombgifts, targeting rares with T2+ Life, Res, "
        "Dex/Int. Breach tree setup: increased chance for Helmet, increased chance for Strength "
        "requirement, reduced chance for Phys mod, increased chance for any Chaos/Fire/Cold/Lightning, "
        "increased chance for Attack (to fish for the Light Radius mod), increased chance for Life.",
        "균열 트리 쪽은 베푸는 생명의 결실로 탄생시키되, T2 이상 생명력·저항·민첩/지능이 붙은 "
        "희귀 아이템을 노린다. 균열 트리 세팅: 투구 확률 증가, 힘 요구치 확률 증가, 물리 속성 확률 감소, "
        "카오스/화염/냉기/번개 확률 증가, 공격 확률 증가(시야 반경 속성을 낚기 위해), 생명력 확률 증가.",
        "'Provisioning Wombgifts' 미번역",
    ),
    Retranslation("Recomb the two - pray it hits the Giantslayer base.",
                  "둘을 재조합한다 — 거인 처형자 투구 베이스로 나오길 빌어라.",
                  "'Giantslayer 기지' — base 를 '기지'로 오역"),
    Retranslation("Boat Exalt or benchcraft for remaining mods.",
                  "남은 속성은 보트 엑잘트나 벤치 제작으로 채운다.", "어순"),
    Retranslation(
        "8.3 Your Helmet (Cover in Ash version) - Credit to my friend POELLINGO#3427",
        "8.3 본인 투구 (재로 뒤덮임 버전) — 친구 POELLINGO#3427 에게 공을 돌린다",
        "'Ash 버전 커버' — Cover in Ash 를 어절 단위로 잘랐다",
    ),
    Retranslation("Start with white base Giantslayer Helmet i81:",
                  "흰색(일반) 거인 처형자 투구 아이템 레벨 81 로 시작한다:",
                  "'흰색 바탕' — white base 는 일반 등급"),
    Retranslation(
        'Farm Infamous Eruptor for "Warcries cover enemies in Ash for 5 seconds".',
        "'전투의 함성이 5초 동안 적을 재로 뒤덮음' 을 노리고 Infamous 분출자를 파밍한다.",
        "'Infamous Eruptor를 농장에서' — farm 을 '농장'으로 오역",
    ),
    Retranslation("Recomb the 2.", "둘을 재조합한다.", "'2를 재결합한다'"),
    Retranslation(
        "If clean with 2 mods, lock suffixes -> Harvest reforge Chaos to guarantee Chaos res.",
        "속성 2개만 깔끔하게 남았으면 접미어를 잠그고 → 수확 재련 카오스로 카오스 저항을 확정한다.",
        "'2개의 모드로 정리하는 경우' — clean 오역",
    ),
    Retranslation("If not clean (like in image)", "깔끔하지 않다면 (이미지처럼)", "어투 통일"),
    Retranslation("Lock suffixes -> Harvest reforge Life for Maximum Life.",
                  "접미어 잠금 → 최대 생명력을 노리고 수확 재련 생명력.",
                  "'수확 재련 최대 생명력의 생명력입니다' — 어순 붕괴"),
    Retranslation(
        "You technically can Boat Eldritch Annul here but it is not worth it. This helmet will be "
        "replaced by Hallowed Monarch anyway.",
        "여기서 보트 섬뜩한 소멸을 쓸 수는 있지만 그럴 값어치가 없다. 이 투구는 어차피 거룩한 "
        "국왕으로 교체된다.",
        "어투 통일",
    ),
    Retranslation("Boat Exalt Slam and Bench craft the rest.",
                  "보트 엑잘트 슬램을 넣고 나머지는 벤치 제작으로 채운다.",
                  "'Bench가 나머지를 제작합니다' — Bench 를 주어로 오독"),
    Retranslation(
        "Breach tree can no longer craft weapons and off-hands. But for every other piece, it still "
        "births a lot of good fodder for our recomb.",
        "균열 트리로는 이제 무기와 보조 장비를 만들 수 없다. 하지만 나머지 부위는 여전히 재조합에 "
        "쓸 좋은 재료를 많이 뽑아준다.",
        "'보조 손' — off-hand 오역, '사료' — fodder 직역",
    ),
    Retranslation(
        "Alteration spam for your desired mod - Life for gloves, Life/Movespeed for boots.",
        "원하는 속성이 뜰 때까지 변화의 오브를 반복한다 — 장갑은 생명력, 부츠는 생명력/이동 속도.",
        "'원하는 모드에 대한 스팸 변경' — 어순 붕괴",
    ),
    Retranslation(
        "Base = Leviathan Gauntlets i81 & Leviathan Greaves i81 (i86 needed for 35ms boots)",
        "베이스 = 레비아탄 건틀릿 아이템 레벨 81 + 레비아탄 각반 아이템 레벨 81 "
        "(이동 속도 35% 부츠는 86 이 필요하다)",
        "'35ms 부팅' — 35% movement speed 를 밀리초와 부팅으로 오역",
    ),
    Retranslation("Use well-rolled rares from the Breach tree.", "균열 트리에서 잘 굴린 희귀 아이템을 쓴다.",
                  "'브리치' 음차"),
    Retranslation("Recomb, then AllFlame Exalt + benchcraft if needed.",
                  "재조합한 뒤, 필요하면 올플레임 엑잘트 + 벤치 제작으로 마무리한다.",
                  "'다시 빗은 다음' — recomb 오역"),
    Retranslation(
        "If recombining into the Leviathan base fails, the item is still fine to use until you can "
        "afford another attempt.",
        "레비아탄 베이스로 재조합하는 데 실패해도, 다시 시도할 여유가 생길 때까지 그 아이템을 "
        "그냥 써도 된다.",
        "어투 통일",
    ),
    Retranslation(
        "8.5. Your Amulet (Section reserved for 3.30 mostly. In 3.29 farm your Clam Amulet instead)",
        "8.5. 본인 목걸이 (대부분 3.30 을 위한 절이다. 3.29 에서는 대신 조개 목걸이를 파밍해라)",
        "'농장으로 만드세요' — farm 오역",
    ),
    Retranslation(
        "Target is an ammy with +2 Gem levels (for Flame Link) and Maximum Life. Best base is either a "
        "+1 All Skill Gem level Croaker Talisman (from Craicic Croaker, also happens to be the Imprint "
        "Beast) or a 15% Maximum Life Gargantuan Talisman (from Farric Gargantuan). Spec your Einhar "
        'Atlas nodes to "The Deep" and "The Wilds" to farm them.',
        "목표는 젬 레벨 +2(화염의 연결용)와 최대 생명력이 붙은 목걸이다. 가장 좋은 베이스는 "
        "'모든 스킬 젬 레벨 +1' 이 붙은 Croaker Talisman(Craicic Croaker 에서 — 각인용 야수이기도 "
        "하다) 또는 '최대 생명력 15%' 가 붙은 Gargantuan Talisman(Farric Gargantuan 에서)이다. "
        "파밍하려면 아인하르 아틀라스 노드를 'The Deep' 과 'The Wilds' 로 찍어라.",
        "'아미' 음차 + '페룰 가르강튀아' 근거 없는 음차",
    ),
    Retranslation(
        "Alt-spam for +1 to Level of All Skill Gems (prefix) - takes roughly 2,500 - 4,000 "
        "alterations. Imprint here if you have 1.",
        "'모든 스킬 젬 레벨 +1'(접두어)이 뜰 때까지 변화의 오브를 반복한다 — 대략 2,500~4,000개가 "
        "든다. 각인이 있으면 여기서 찍어둬라.",
        "'1이 있으면 여기에 각인하세요' — Imprint 아이템이 숫자가 됐다",
    ),
    Retranslation("AllFlame/Boat Regal Orb.", "올플레임 / 보트 제왕의 오브.", "표기 통일"),
    Retranslation(
        "If you don't hit Maximum Life (or the tier is too low):",
        "최대 생명력이 안 떴거나 티어가 너무 낮으면:",
        "'등급이 너무 낮은 경우' 어색",
    ),
    Retranslation(
        "Use AllFlame a second time with Kishara's Ducat to split the item and retrieve the rare "
        "amulet with +1 All Skill Gems. This split ducat does NOT guarantee a return of the +1 to "
        "Level of All Skill Gems. But you must be super unlucky to have 4 losing outcomes at once.",
        "Kishara's Ducat 으로 올플레임을 한 번 더 써서 아이템을 쪼개고, '모든 스킬 젬 +1' 이 붙은 "
        "희귀 목걸이를 되찾는다. 이 분할 두캇이 '모든 스킬 젬 레벨 +1' 을 반드시 돌려주지는 않는다. "
        "다만 네 결과가 한꺼번에 다 꽝이려면 어지간히 운이 없어야 한다.",
        "'4번의 패배를 당한다면' — outcome 을 승패로 오역",
    ),
    Retranslation("8.6. Your Vermillion Rings", "8.6. 본인 주색 반지", "'당신의 버밀리온 반지' 음차"),
    Retranslation(
        "Lori's Lantern x2 work for a long time. But our end goal is a pair of Vermillion Rings (80+) "
        "with (1) Maximum Life, (2) Light Radius and (3) Chaos Res/Dex/Int.",
        "로리의 등불 2개로도 한참 버틴다. 다만 최종 목표는 (1) 최대 생명력, (2) 시야 반경, "
        "(3) 카오스 저항/민첩/지능이 붙은 아이템 레벨 80 이상 주색 반지 한 쌍이다.",
        "'로리의 등불 x2가 오랫동안 작업했습니다' — work 를 '작업하다'로 오역",
    ),
    Retranslation(
        'Spam Harvest Reforge Chaos for guaranteed Chaos Res until you hit the suffix "15% Light '
        'Radius/Global Accuracy"',
        "접미어 '시야 반경 / 전역 정확도 15%' 가 뜰 때까지 수확 재련 카오스를 반복한다"
        "(카오스 저항은 확정으로 붙는다).",
        "'스팸 수확 재련 카오스' — 어순 붕괴",
    ),
    Retranslation(
        "Boat Exalt Slam looking for Life or another good suffix (Attribute/Ele res).",
        "생명력이나 다른 좋은 접미어(능력치 / 원소 저항)을 노리고 보트 엑잘트 슬램을 넣는다.",
        "'Boat Exalt 강타는 ... 찾고 있습니다' — 도구가 주어가 됐다",
    ),
    Retranslation(
        "If outcome is 3 good suffixes -> Suffixes cannot be changed -> Harvest Reforge Life until "
        "T2+ Maximum Life. If outcome is T2+ Life -> Bench craft last suffix -> Boat Exalt Slam the "
        "rest.",
        "좋은 접미어가 3개 나왔으면 → '접미어 변경 불가' 를 걸고 → T2 이상 최대 생명력이 "
        "뜰 때까지 수확 재련 생명력. 결과가 T2 이상 생명력이면 → 마지막 접미어를 벤치 제작하고 "
        "→ 나머지는 보트 엑잘트 슬램.",
        "'수확 재련 T2+ 최대 생명력까지의 생명력입니다' — 어순 붕괴",
    ),
    Retranslation(
        'Alternative: Alteration spam for T1 Maximum Life ("Virile") to recomb with T1 Light Radius '
        '("Of Radiance") -> Pray -> Boat Exalt slams.',
        "대안: T1 최대 생명력('Virile')이 뜰 때까지 변화의 오브를 반복해서 T1 시야 반경"
        "('Of Radiance')과 재조합 → 빌고 → 보트 엑잘트 슬램.",
        "'변형 스팸' — alteration 은 변화의 오브",
    ),
    Retranslation(
        'Remember to have Hillock in your Betrayal board and do NOT filter his card "The Finishing '
        'Touch" for Fertile Catalyst.',
        "을 올려두는 걸 잊지 마라. 그리고 풍요의 기폭제를 주는 그의 카드 "
        "'화룡점정(The Finishing Touch)' 은 필터에서 숨기지 마라.",
        "'필터링하지 마십시오' — filter out(숨김)을 '필터링'으로 옮겨 뜻이 뒤집혔다",
    link_label="배신 보드의 힐록"),
    Retranslation(
        "8.7. Merc's Helmet/Body Armour/Boots (with +1 Abyssal Socket)",
        "8.7. 용병 투구 / 갑옷 / 부츠 (심연 홈 +1)",
        "'몸통 방어도' — Body Armour 는 갑옷",
    ),
    Retranslation(
        "Abyssal socket in gear for double fire resistances roll. Target: (1) Abyssal socket and "
        "(2) Fire resistance for every piece. You can certainly do this with a Hollow Fossil if you "
        "are into Delve. I am not. So here is what I did:",
        "화염 저항을 두 번 굴리려고 장비에 심연 홈을 넣는 것이다. 목표: 모든 부위에 "
        "(1) 심연 홈과 (2) 화염 저항. 델브를 한다면 공허의 화석으로도 된다. 나는 안 한다. "
        "그래서 내가 한 방법은 이렇다:",
        "'두 배의 화재 저항 굴림을 위한 기어' — fire resistance 를 '화재 저항'으로 오역",
    ),
    Retranslation(
        'Farm Abyss with "Votive Hoard" for a 25% chance to drop rares with an Abyssal socket from '
        "Abyss chests. Annul if you want a clean suffix with only the Abyssal socket.",
        "'Votive Hoard' 를 켜고 심연을 파밍하면 심연 상자에서 심연 홈이 붙은 희귀 아이템이 25% 확률로 "
        "나온다. 심연 홈만 남은 깔끔한 접미어를 원하면 소멸의 오브를 쓴다.",
        "'무효화하세요' — Annul 은 소멸의 오브",
    ),
    Retranslation(
        "Craft your main bases - Majestic Pelt (84+), Syndicate's Garb (84+), Velour Boots (84+) - "
        "for T1 fire res.",
        "주력 베이스 — 압도적인 가죽모(84+), 연합의 의복(84+), 벨루어 장화(84+) — 에 T1 화염 저항을 "
        "제작한다.",
        "'주요 기지' — base 를 '기지'로 오역",
    ),
    Retranslation("Recomb the above for +1 Abyssal socket & Fire Res.",
                  "위 둘을 재조합해서 심연 홈 +1 과 화염 저항을 함께 붙인다.",
                  "'위의 내용을 다시 조합하세요' 어색"),
    Retranslation("Pray that it's clean. Or you will have to Boat Annul, or Eldritch Annul.",
                  "깔끔하게 나오길 빌어라. 아니면 보트 소멸이나 섬뜩한 소멸을 써야 한다.",
                  "'Boat Annul 또는 Eldritch Annul을 선택해야 합니다' 미번역"),
    Retranslation(
        "Craft Hybrid Fire/Chaos res - this gets you very high fire resistance boots/chest/helmet for "
        "Enmity's Embrace.",
        "화염/카오스 복합 저항을 제작한다 — 원한의 품을 쓰기 위한 고화염 저항 부츠·갑옷·투구가 "
        "이렇게 나온다.",
        "'내화성 부츠/가슴/투구' — chest 를 '가슴'으로 직역",
    ),
    Retranslation("Boat Exalt Slam the prefix. Mods to look for:",
                  "접두어에 보트 엑잘트 슬램을 넣는다. 노릴 속성:",
                  "'Boat Exalt 강타 접두사입니다' — 서술어가 사라졌다"),
    Retranslation("Body Armour: % Evasion and Flat Evasion", "갑옷: 회피 % 와 고정 회피",
                  "'본문 방어도' + '평면 회피' 오역"),
    Retranslation("8.8. Double Fire res Abyss Jewels", "8.8. 화염 저항 2개짜리 심연 주얼",
                  "'더블 화염 저항 심연 보석' 음차"),
    Retranslation(
        "What to look for on the Abyss Jewels: (1) Fire res and (2) Hybrid Fire res (can also settle "
        "with All Elemental res). Either Harvest Reforge Fire OR plain alteration-spam for Fire res "
        "-> then Boat Augment/Regal/Exalt for the other.",
        "심연 주얼에서 노릴 것: (1) 화염 저항과 (2) 복합 화염 저항(모든 원소 저항으로 타협해도 된다). "
        "수확 재련 화염을 돌리거나 그냥 변화의 오브를 반복해서 화염 저항을 띄운 다음 → 나머지 하나는 "
        "보트 증강/제왕/엑잘트로 붙인다.",
        "'다른 하나에 대한 Boat Augment/Regal/Exalt입니다' 미번역",
    ),
    Retranslation(
        "Best bases for hitting Fire res, ranked by odds (per CraftOfExile): Ghastly Eye Jewel "
        "(16.66%) → Hypnotic Eye Jewel (11.46%) → everything else (9.8%).",
        "화염 저항이 뜰 확률이 높은 베이스 순서(CraftOfExile 기준): 무시무시한 눈 주얼(16.66%) → "
        "최면 거는 눈 주얼(11.46%) → 나머지 전부(9.8%).",
        "출처 표기가 빠졌다",
    ),
    Retranslation(
        "New: Merrick's Ducat - This 3.29 Ducat adds a 5th mod to a jewel. The jewel comes out "
        "Corrupted, but doesn't appear to risk removing/bricking existing mods based on live testing. "
        "Worth trying if you want to push for a triple-resistance jewel.",
        "신규: Merrick's Ducat — 3.29 의 이 두캇은 주얼에 다섯 번째 속성을 추가한다. 주얼은 타락 "
        "상태로 나오지만, 실측상 기존 속성을 지우거나 못 쓰게 만들 위험은 없어 보인다. "
        "저항 3개짜리 주얼을 노린다면 시도해 볼 만하다.",
        "'벽돌화할 위험' — brick 직역",
    ),
    Retranslation("8.9. Blade Ambusher's Weapons - 2x Gutting Knives",
                  "8.9. Blade Ambusher 무기 — 내장 제거용 단도 2개",
                  "'내장 내장 칼' 중복 오역"),
    Retranslation("BUDGET:", "저예산:", "'예산'"),
    Retranslation("Get 2x ilvl 73+ Gutting Knives", "아이템 레벨 73 이상 내장 제거용 단도 2개를 구한다",
                  "베이스명 오역"),
    Retranslation("Either: Harvest Reforge Crit until T1 Crit Chance and T2+ Crit Damage.",
                  "하나: T1 치명타 확률과 T2 이상 치명타 피해 배율이 뜰 때까지 수확 재련 치명타.",
                  "'수확 재련 T1 ... 까지 치명타' — 어순 붕괴"),
    Retranslation(
        "Annul down to a clean base with only (1) Crit Chance + (2) Crit Damage and a maximum of "
        "1 prefix.",
        "소멸의 오브로 깎아서 (1) 치명타 확률 + (2) 치명타 피해 배율만 남고 접두어는 최대 "
        "1개인 깨끗한 베이스로 만든다.",
        "'깨끗한 기반으로 무효화합니다' — Annul 오역",
    ),
    Retranslation(
        "Craft: Multimod → Hit Cannot Be Evaded → Attack Penetrate Elements/Inc Fire Damage & Ignite.",
        "제작: 멀티모드 → '무조건 명중' → '공격이 원소 저항 관통' / 화염 피해 증가 & 점화.",
        "표기 통일",
    ),
    Retranslation("SLIGHTLY MORE EXPENSIVE:", "조금 더 비싼 방법:", "'약간 더 비쌉니다'"),
    Retranslation("Get A LOT OF ilvl 73+ Gutting Knives",
                  "아이템 레벨 73 이상 내장 제거용 단도를 잔뜩 모은다", "베이스명 오역"),
    Retranslation(
        'Recomb T1 Crit Chance ("Incision") with T1 Crit Multi ("Of Destruction").',
        "T1 치명타 확률('Incision')과 T1 치명타 피해 배율('Of Destruction')을 재조합한다.",
        "'절개' — 접미어 이름은 인게임 검색용이라 원문 유지",
    ),
    Retranslation(
        'Regex to use is: "Incision|Destruction|Gutting Knife$". Last bit is meant for an open suffix. '
        "When it lights up during Alt spamming, switch to Augment instead. Will save you some "
        "Alterations.",
        "쓸 정규식: \"Incision|Destruction|Gutting Knife$\". 마지막 조각은 빈 접미어를 잡기 위한 "
        "것이다. 변화의 오브를 반복하다 그게 켜지면 증강의 오브로 바꿔라. 변화의 오브를 아낄 수 있다.",
        "정규식 안의 영문을 번역해 검색이 안 되게 만들었다",
    ),
    Retranslation("Craft: Multimod & Suffixes Cannot Be Changed.",
                  "제작: 멀티모드 + '접미어 변경 불가'.", "표기 통일"),
    Retranslation("Boat Veiled Orb to force a betrayal mod on prefix.",
                  "보트 Veiled Orb 로 접두어에 배신 속성을 강제로 붙인다.",
                  "'보트 베일드 오브(Boat Veiled Orb)는 ... 적용합니다' — 도구가 주어가 됐다"),
    Retranslation(
        'Look for a clean outcome. Or if you are lucky, one with a veiled mod plus "Elemental damage '
        'with attack".',
        "깔끔한 결과를 고른다. 운이 좋으면 봉인 속성에 '공격 시 원소 피해' 까지 붙은 결과가 나온다.",
        "'모드도 있습니다' — 문장이 끊겼다",
    ),
    Retranslation(
        'Bench craft "% Physical" to avoid Betrayal %Phys mod BEFORE you unveil.',
        "봉인을 풀기 전에 벤치 제작으로 '물리 %' 를 미리 걸어 배신 물리 % 속성이 나오는 걸 막아라.",
        "'피하기 위해 ... 사용하세요' — BEFORE 의 순서 지시가 약해졌다",
    ),
    Retranslation(
        "Unveil and look for the following, in priority order: (1) Increased Fire Damage & Ignite "
        "Chance -> (2) Elemental Penetration -> (3) Extra Fire damage as chaos.",
        "봉인을 풀고 우선순위대로 노린다: (1) 화염 피해 증가 & 점화 확률 → (2) 원소 저항 관통 → "
        "(3) 화염 피해의 일부를 추가 카오스 피해로.",
        "'카오스로 인한 추가 화염 피해 증가' — 방향이 뒤집혔다",
    ),
    Retranslation(
        "Bench craft: Multimod (again) & Hit cannot be evaded & any of the above 3 mods.",
        "벤치 제작: 멀티모드(다시) + '무조건 명중' + 위 3개 중 아무거나.", "표기 통일",
    ),
    Retranslation(
        "Why no attack speed? - These Blade Traps spin duration and hit frequency are fixed by the "
        "skill itself.",
        "왜 공격 속도가 없나? — 칼날 덫의 회전 지속시간과 타격 빈도는 스킬 자체에 고정돼 있다.",
        "'블레이드 트랩의' — 소유격 위치 오류",
    ),
    Retranslation("Why Inc Fire Damage better than Ele pen and Extra as chaos?",
                  "왜 화염 피해 증가가 원소 관통이나 추가 카오스 변환보다 나은가?",
                  "'Ele 펜과 Extra보다 카오스보다' — 비교 대상이 뒤엉켰다"),
    Retranslation(
        "Ele pen has diminishing return, assuming you already stacked a lot of them for Enmity's.",
        "원소 관통은 이미 원한의 품 때문에 잔뜩 쌓아둔 상태라 수확 체감이 온다.",
        "'Enmity를 위해' — 아이템명이 사라졌다",
    ),
    Retranslation(
        "Extra as chaos is 7-10% MORE. Inc Fire Damage is 50-70% INCREASED. In a normal scenario, "
        "MORE always win since we have a bunch of INCREASED nodes in our passive tree. But for our "
        "Merc, who has no source of Increased Damage, the INCREASED actually win by a lot in this "
        "case.",
        "추가 카오스 변환은 7~10% 증폭(MORE)이고, 화염 피해 증가는 50~70% 증가(INCREASED)다. "
        "보통은 패시브 트리에 증가 노드가 잔뜩 있어서 증폭이 항상 이긴다. 하지만 피해 증가 소스가 "
        "전혀 없는 우리 용병에게는 이 경우 증가 쪽이 훨씬 크게 이긴다.",
        "'혼돈이 7-10% 더 많아지면 추가됩니다' — 문장이 통째로 무너졌다",
    ),
    Retranslation("8.10. Blade Ambusher's Belt", "8.10. Blade Ambusher 허리띠", "표기 통일"),
    Retranslation(
        'The new 3.29 prefix "Throw up to one additional trap if dual wielding" is craftable via the '
        'Rotmother\'s Ducat, dropped from "Hazardous Depths" charts in The Sovereign, or obtained by '
        "converting a Changeling's Ducat.",
        "3.29 신규 접두어 '쌍수 장착 시 덫을 최대 1개 추가 투척' 은 Rotmother's Ducat 으로 "
        "제작할 수 있다. 이 두캇은 The Sovereign 의 'Hazardous Depths' 해도에서 나오거나, "
        "Changeling's Ducat 을 변환해서 얻는다.",
        "'차트에서 삭제되거나' — dropped 를 '삭제'로 오역",
    ),
    Retranslation(
        "Alteration spam your Stygian Vise to have either (1) Elemental damage with attack or "
        "(2) Fire res",
        "명계의 조임쇠에 변화의 오브를 반복해서 (1) 공격 시 원소 피해 또는 (2) 화염 저항을 띄운다",
        "'스팸을 스팸으로 보내는 변경' — 어순 붕괴",
    ),
    Retranslation(
        "If you have spare bases, recomb the 2. If not, Boat Exalt slam and look for the other mod. "
        "It is okay to hit Light/Cold res too since we can harvest swap later.",
        "여분 베이스가 있으면 둘을 재조합한다. 없으면 보트 엑잘트 슬램을 넣고 나머지 속성을 노린다. "
        "나중에 수확 교환이 가능하므로 번개/냉기 저항이 떠도 괜찮다.",
        "'다시 빗어보세요' — recomb 오역",
    ),
    Retranslation("Bench craft Hybrid Fire/Chaos res to try to fill all suffixes",
                  "화염/카오스 복합 저항을 벤치 제작해서 접미어를 전부 채워본다",
                  "'하이브리드 화염/카오스 모든 접미사를' — 목적어가 잘렸다"),
    Retranslation("Leave an open prefix for Rotmother's Ducat slam.",
                  "Rotmother's Ducat 슬램을 위해 접두어 한 자리를 비워둬라.",
                  "'열린 접두사를 남겨주세요' 직역"),
    Retranslation(
        'About 1/20 chance you will hit "Throw up to one additional trap if dual wielding".',
        "'쌍수 장착 시 덫을 최대 1개 추가 투척' 이 뜰 확률은 20분의 1 정도다.",
        "'칠 수 있습니다' — hit 직역",
    ),
    Retranslation(
        "Other trap mods are actually usable too. Settle with Trap AOE or Trap Trigger Radius until "
        "you have more juice to craft your BIS belt.",
        "다른 덫 속성도 사실 쓸 만하다. BIS 허리띠를 제작할 여유가 생길 때까지는 덫 효과 범위나 "
        "덫 발동 반경으로 타협해라.",
        "'주스가 더 많아질 때까지' — juice 직역",
    ),
    Retranslation("8.11. Blade Ambusher's Gloves", "8.11. Blade Ambusher 장갑", "표기 통일"),
    Retranslation(
        'Farm Infamous Combatant for "Random Projectile Speed" infamy gloves.',
        "'무작위 투사체 속도' 악명 장갑을 노리고 Infamous 전투원을 파밍한다.",
        "'악명 높은 장갑을 위한 Farm Infamous Combatant' — 어순 붕괴",
    ),
    Retranslation(
        "Alteration spam your Evasion based Velour Gloves for T1 Fire Res (need ilevel 84 for T1).",
        "회피 기반 벨루어 장갑에 변화의 오브를 반복해서 T1 화염 저항을 띄운다"
        "(T1 이 뜨려면 아이템 레벨 84 가 필요하다).",
        "'변경 사항은 ... 스팸합니다' — 주어가 뒤바뀌었다",
    ),
    Retranslation(
        "Recomb the 2. Pray that the outcome is the pair of Velour Gloves with 2 mods survived.",
        "둘을 재조합한다. 결과가 속성 2개를 살린 벨루어 장갑이길 빌어라.",
        "'2개의 모드가 있는 ... 살아남기를' 어색",
    ),
    Retranslation(
        "Alternative: Use Boat craft on a pair of Velour Gloves with Cyaxan's Ducat for 3 random "
        "infamy mods.",
        "대안: 벨루어 장갑에 Cyaxan's Ducat 으로 보트 제작을 걸어 무작위 악명 속성 3개를 받는다.",
        "어순 정리",
    ),
    Retranslation(
        'If there is an open suffix -> Bench craft hybrid "Fire/Chaos res" -> Boat Exalt slam the rest.',
        "빈 접미어가 있으면 → '화염/카오스 복합 저항' 을 벤치 제작 → 나머지는 보트 엑잘트 슬램.",
        "미번역 잔재",
    ),
    Retranslation(
        'If there is no open suffix -> Boat Exalt slam -> Bench craft "Area of Effect/ Area Damage".',
        "빈 접미어가 없으면 → 보트 엑잘트 슬램 → '효과 범위 / 범위 피해' 를 벤치 제작.",
        "'Area Damage' 미번역",
    ),
    Retranslation("Eldritch Ichor/Ember for implicits as in image.",
                  "고정 속성은 이미지처럼 섬뜩한 영액 / 섬뜩한 불씨로 붙인다.",
                  "'암시적 표현을 위한' — implicit 오역"),
    Retranslation("8.11. Combatant's Weapons - 2x Jewelled Foils",
                  "8.11. Combatant 무기 — 보석이 박힌 펜싱 검 2개", "'보석 포일' 오역"),
    Retranslation("Collect A LOT of Jewelled Foils (i77+).",
                  "보석이 박힌 펜싱 검(아이템 레벨 77+)을 잔뜩 모은다.", "'보석 포일' 오역"),
    Retranslation('Alt-spam one foil for T1 Crit Chance (suffix "Incision").',
                  "펜싱 검 하나에 변화의 오브를 반복해서 T1 치명타 확률(접미어 'Incision')을 띄운다.",
                  "'대체 스팸 포일 1개' — 어순 붕괴"),
    Retranslation('Alt-spam another foil for T1 Attack Speed (suffix "Celebration").',
                  "다른 펜싱 검에는 T1 공격 속도(접미어 'Celebration')를 띄운다.",
                  "'또 다른 포일을 대체 스팸으로 보냅니다' — 어순 붕괴"),
    Retranslation(
        'Regex: "Incision|Celebration|Jewelled Foil$". Last bit is for open suffix. So when it lights '
        "up, Augment it instead of Alteration.",
        "정규식: \"Incision|Celebration|Jewelled Foil$\". 마지막 조각은 빈 접미어용이다. "
        "그게 켜지면 변화의 오브 대신 증강의 오브를 써라.",
        "정규식 안의 영문을 번역해 검색이 안 되게 만들었다",
    ),
    Retranslation("Recomb the two, then pray.", "둘을 재조합하고 빌어라.",
                  "'다시 모으고 기도하십시오' — recomb 오역"),
    Retranslation("Suffix Cannot Be Changed → Harvest Reforge Crit to guarantee Crit Multi.",
                  "'접미어 변경 불가' → 치명타 피해 배율을 확정하려고 수확 재련 치명타.",
                  "'치명적입니다' — 어순 붕괴"),
    Retranslation(
        "If crit multi is low, either (1) use this failed one for another yolo recomb or (2) restart "
        "from step 1.",
        "치명타 피해 배율이 낮으면 (1) 실패작을 다른 욜로 재조합 재료로 쓰거나 (2) 1단계부터 다시 한다.",
        "어투 통일",
    ),
    Retranslation(
        "Boat Exalt slam & Bench Craft if prefixes are already good. OR Lock Suffixes + Boat craft "
        "Veiled Orb looking for either (1) Elemental Penetration or (2) Inc Fire Damage. Remember to "
        "bench craft Phys % to block mod before Unveiling.",
        "접두어가 이미 좋으면 보트 엑잘트 슬램 + 벤치 제작. 아니면 접미어를 잠그고 보트 "
        "Veiled Orb 로 (1) 원소 저항 관통이나 (2) 화염 피해 증가를 노린다. 봉인을 풀기 전에 "
        "'물리 %' 를 벤치 제작해서 원치 않는 속성을 막는 것을 잊지 마라.",
        "'모드를 차단하려면 벤치 크래프트 Phys %를 기억하세요' 어순",
    ),
    Retranslation(
        "Boat Exalt slam for Flat Cold/Lightning (for Taming abuse). Note: You need at least 1 Foil "
        "with Flat Cold as he should already had Wrath as an aura, unless there are other sources in "
        "his gear with Flat Cold (Gloves/Abyss Jewels). If it is the latter, pick Flat Lightning for "
        "more Shock value.",
        "고정 냉기/번개 피해를 노리고 보트 엑잘트 슬램(조련을 활용하기 위해서다). 참고: 그는 이미 "
        "진노를 오라로 켜고 있으므로 고정 냉기 피해가 붙은 펜싱 검이 최소 1개는 필요하다. "
        "다만 장비 다른 곳(장갑/심연 주얼)에 고정 냉기 피해가 있다면, 감전 수치를 더 키우려고 "
        "고정 번개 피해를 고르는 게 낫다.",
        "'플랫 냉기가 있는 포일 1개 이상이 필요합니다' — 조건절 순서가 뒤집혔다",
    ),
    Retranslation("8.12. Combatant's Gloves", "8.12. Combatant 장갑", "표기 통일"),
    Retranslation("Harvest Reforge Fire until T2+ Attack speed in a Velour Gloves base.",
                  "벨루어 장갑 베이스에 T2 이상 공격 속도가 뜰 때까지 수확 재련 화염을 돌린다.",
                  "'수확 재련 화염 벨루어 장갑 기반에서' — 어순 붕괴"),
    Retranslation("Alternative: Alteration spam T1 Fire Res & T1 Attack speed -> Recomb.",
                  "대안: 변화의 오브를 반복해 T1 화염 저항과 T1 공격 속도를 각각 띄운 뒤 → 재조합.",
                  "'스팸 변경' 어순"),
    Retranslation("Cheap: Boat Exalt Slam and Bench craft the rest like in image.",
                  "저렴한 방법: 보트 엑잘트 슬램을 넣고 나머지는 이미지처럼 벤치 제작한다.",
                  "'저렴한:' 어색"),
    Retranslation("Slightly more expensive:", "조금 더 비싼 방법:", "'약간 더 비쌉니다'"),
    Retranslation(
        "Suffixes cannot be changed -> Boat craft Veiled Orb. Look for one that hits Prefix. Bench "
        "craft Mana to block mod before Unveiling.",
        "'접미어 변경 불가' → 보트 Veiled Orb 제작. 접두어에 걸린 결과를 고른다. 봉인을 풀기 "
        "전에 마나를 벤치 제작해서 원치 않는 속성을 막아라.",
        "'모드를 차단하기 위해 벤치 제작 마나를 사용하세요' 어순",
    ),
    Retranslation(
        "Unveil for either (1) Projectile Speed/Dmg -> (2) Area/Area Dmg -> (3) Melee Strike Range. "
        "Boat Exalt slam and Bench craft the rest.",
        "봉인을 풀어 (1) 투사체 속도/피해 → (2) 효과 범위/범위 피해 → (3) 근접 타격 범위 순으로 "
        "노린다. 나머지는 보트 엑잘트 슬램과 벤치 제작으로 채운다.",
        "'Bench가 나머지 작업을 수행합니다' — Bench 를 주어로 오독",
    ),
    Retranslation(
        'IMPORTANT: Spam Grand Eldritch Ember for "+3 target strike skill when Pinnacle in your '
        'presence". Can settle with Greater Eldritch Ember for +2 like in image.',
        "중요: '정점 존재 시 대상 타격 스킬 +3' 을 노리고 우수한 섬뜩한 불씨를 반복해서 써라. "
        "이미지처럼 상급 섬뜩한 불씨로 +2 에 타협해도 된다.",
        "'스팸 고급 섬뜩한 불씨을 보내세요' — 어순 붕괴 + Grand 는 '우수한'",
    ),
    Retranslation(
        "Q: Why there is no Fire Exposure eldritch in these gloves? - A: This is my gear at end game. "
        "I have another source of Fire Exposure through Animate Guardian wearing Elemental Army "
        "Support.",
        "Q: 왜 이 장갑에는 화염 노출 섬뜩한 속성이 없나? — A: 이건 엔드게임 시점의 내 장비다. "
        "원소의 군단 보조를 낀 수호자 기동으로 화염 노출을 따로 넣고 있다.",
        "'엘드리치' 음차",
    ),
    Retranslation("8.13. Luxury - AGoS Pseudo-6L (Essence of Horror & Elder base)",
                  "8.13. 사치 — AGoS 유사 6링크 (경악의 에센스 + 엘더 베이스)",
                  "'엘더 기지' — base 를 '기지'로 오역"),
    Retranslation("For a pseudo-six-link for your Animate Guardian of Smiting:",
                  "징벌의 수호자 기동을 유사 6링크로 만들려면:", "'의사 6-링크' 음차"),
    Retranslation(
        "Base = Elder influence Gloves. Feed your Guardian maps to your Kingsmarch mappers. Note: You "
        "can Elder Exalt orb into your Leviathan Gauntlets, but given the intangibility per craft and "
        "how many failures these may occur, I would not recommend doing so.",
        "베이스 = 엘더 영향 장갑. Kingsmarch 지도 제작자에게 가디언 지도를 먹여라. 참고: 레비아탄 "
        "건틀릿에 엘더 엑잘티드 오브를 써도 되지만, 제작마다 붙는 비실체화와 실패 횟수를 생각하면 "
        "권하지 않는다.",
        "'공예당 비실체화' — craft 를 '공예'로 오역",
    ),
    Retranslation(
        "Farm Essence of Horror using the two Essence-related Atlas notables (one near the start for "
        "+1 essence tier per map, one in the middle for +1 tier higher). Run Essence Scarabs if you "
        "have any.",
        "에센스 관련 아틀라스 주요 노드 2개를 찍고 경악의 에센스를 파밍한다(시작 근처 하나는 맵당 "
        "에센스 티어 +1, 중간의 하나는 티어를 한 단계 더 올린다). 에센스 갑충석이 있으면 같이 써라.",
        "'두 개의 정수 관련 아틀라스 주요 항목' — notable 오역",
    ),
    Retranslation(
        "When you see any purple essence, stack Vaal Orbs in your inventory and corrupt it for a "
        "chance of corrupted essences. Any of the 4 corrupted essences will work, since you can always "
        "Harvest swap them later to Essence of Horror. Can also keep Essence of Insanity if that's "
        "your choice for the Merc's body armour craft.",
        "보라색 에센스를 보면 인벤토리에 바알 오브를 쌓아두고 타락시켜 타락한 에센스를 노려라. "
        "타락한 에센스 4종 중 무엇이든 상관없다. 나중에 수확 교환으로 경악의 에센스로 바꿀 수 "
        "있기 때문이다. 용병 갑옷 제작을 그쪽으로 정했다면 광기의 에센스를 남겨둬도 된다.",
        "'에센스가 오염될 가능성이 있습니다' — corrupt 오역",
    ),
    Retranslation("Apply the essence via the AllFlame boat craft method for 2 outcomes.",
                  "에센스는 올플레임 보트 제작 방식으로 발라서 결과 2개를 받는다.", "어순 정리"),
    Retranslation('Look for "Socketed Gem supported by level 18/20 Faster Attack"',
                  "'장착된 젬이 18/20 레벨 공격 속도 증가 보조를 받음' 을 노려라",
                  "'더 빠른 공격에서 지원되는 장착 보석' — Faster Attack Support 오역"),
    Retranslation("If prefixes are full, Boat Annul and pray. You need at least one open prefix here.",
                  "접두어가 꽉 찼으면 보트 소멸을 쓰고 빌어라. 여기서는 빈 접두어가 최소 "
                  "1개 필요하다.",
                  "'보트를 취소하고' — Annul 을 '취소'로 오역"),
    Retranslation(
        "If there is open suffixes, either Boat slam looking for attribute or Lock suffixes + Harvest "
        "reforge Chaos for Chaos res.",
        "빈 접미어가 있으면, 능력치를 노리고 보트 슬램을 넣거나 접미어를 잠그고 수확 재련 "
        "카오스로 카오스 저항을 붙인다.",
        "'접미사 + 수확 재련 카오스를 잠급니다' — 어순 붕괴",
    ),
    Retranslation("Suffixes cannot be changed -> Harvest reforge Life for Maximum Life.",
                  "'접미어 변경 불가' → 최대 생명력을 노리고 수확 재련 생명력.",
                  "'수확 재련 최대 생명력의 생명력입니다' — 어순 붕괴"),
    Retranslation(
        'Note: The 3rd mod "70% to crit multi" in image does nothing to your AG since AG doesn\'t have '
        'an attack tag. There is also another Elder mod for "supported by level xx Additional '
        'Accuracy". However, unlike our merc, minions no long miss their attack anymore since 3.27.',
        "참고: 이미지의 세 번째 속성 '치명타 피해 배율 70%' 는 AG 에게 아무 의미가 없다. AG 에는 "
        "공격 태그가 없기 때문이다. '레벨 xx 정확도 추가 보조를 받음' 이라는 엘더 속성도 있지만, "
        "우리 용병과 달리 소환수는 3.27 부터 공격을 빗나가지 않는다.",
        "'70% 치명타 멀티' 음차",
    ),


    # === 6·7·8장 2차: 링크가 낀 문단과 남은 어순 붕괴 ============================
    Retranslation("6. HIGH TIER UNIQUES & LUXURY UPGRADES:", "6. 고티어 고유 아이템 & 사치 업그레이드",
                  "'고등급' — high tier 는 고티어. 'LUXURY UPGRADES' 가 통째로 빠졌다"),
    Retranslation(
        "8% drop rate from Incarnation of Fear - already covered in 5.2. Second Atlas Tree.",
        ("공포의 화신(Incarnation of Fear)에서 드롭률 8% — 이미 ", " 에서 다뤘다."),
        "문장 어투 통일",
    link_label="5.2. 두 번째 아틀라스 패시브 트리"),
    Retranslation(
        "Farm Berek's Respite by spamming Volcano map for The Spark and The Flame div card, as this "
        "map also drops Pride Before the Fall (div card for corrupted Kaom's Heart). Use the same "
        "scrying tactic as in Atlas Tree #2. Since we already scry Caldera to City Square, the other "
        "options to scry into are (1) Mesa -> (2) Cemetery -> (3) Jungle's Valley.",
        ("'불꽃과 화염' 점술 카드를 노리고 화산 지도를 계속 돌려 베렉의 유예를 파밍해라. 이 지도는 "
         "'몰락 직전의 긍지'(타락한 카옴의 심장용 점술 카드)도 함께 떨어뜨린다. ",
         " 에서 쓴 것과 같은 Scrying 전술을 쓴다. 칼데라는 이미 도시 광장으로 바꿔 쓰고 있으니, "
         "그 밖에 바꿔볼 만한 곳은 (1) 메사 → (2) 공동묘지 → (3) 밀림 계곡이다."),
        "'The 전기불꽃 및 The Flame' — 점술 카드 이름이 반만 번역됐고 괄호도 안 닫혔다",
    link_label="아틀라스 패시브 트리 #2"),
    Retranslation(
        "Use Turbulent Catalyst x 20. If you do not farm Ultimatum (which is absolutely the right "
        "thing to do), harvest swap other Catalysts to get them. Source of other Catalysts are from "
        "either (1) Hillock in Betrayal or (2) Kingsmarch mappers.",
        ("격동의 기폭제 20개를 쓴다. 결전을 파밍하지 않는다면(그게 지극히 정상이다) 다른 "
         "기폭제를 수확 교환으로 얻어라. 다른 기폭제가 나오는 곳은 (1) ",
         "배신의 힐록",
         " 또는 (2) Kingsmarch 지도 제작자다."),
        "'배신당한 힐록' — Hillock in Betrayal 을 수동태로 오역",
        True,
    ),
    Retranslation("6.3. Rotmother's Mutiny", "6.3. 부패모의 반란(Rotmother's Mutiny)",
                  "이름이 미번역이라 무엇인지 안 읽힌다. 한국어명은 poedb.tw/kr 에서 회수"),
    Retranslation(
        "Watch my 2 minute video [POE 3.29] How to target farm Rotmother's Mutiny - new unique clam "
        "amulet.",
        ("내 2분짜리 영상 ",
         "[POE 3.29] How to target farm Rotmother's Mutiny - new unique clam amulet",
         " 을 보면 된다."),
        "'농장 지정 방법' — target farm 을 어절 단위로 잘랐다. 영상 제목은 검색용이라 원문 유지",
        True,
    ),
    Retranslation("6.4. Greywind (for AGoS) & Foulborn The Red Dream",
                  "6.4. Greywind (AGoS 용) & 삿된 붉은 꿈", "'for AGoS' 미번역"),
    Retranslation("6.5. Untouched Soul, Pragmatism & Light of Meaning (life)",
                  "6.5. 손길이 닿지 않은 영혼, 실용주의 & 의미의 빛(생명력 버전)",
                  "'(생명)' — Life version 은 생명력 버전"),
    Retranslation("6.6. Garb of the Ephemeral (for AGoS)", "6.6. 덧없는 자의 의복 (AGoS 용)",
                  "'(AGoS의 경우)' 어색"),
    Retranslation("6.7. Rathpith Globe (for AGoS)", "6.7. 래스피스 구체 (AGoS 용)",
                  "'(AGoS의 경우)' 어색"),
    Retranslation(
        "Save your Elder Exalted Orbs to slam into the pair of rings. Can also craft a pair of Elder "
        "Gloves [View Crafting Guide] if you are investing in your Animate Guardian of Smiting.",
        ("엘더 엑잘티드 오브는 아껴뒀다가 반지 한 쌍에 슬램해라. 징벌의 수호자 기동에 투자할 "
         "생각이면 엘더 장갑을 제작해도 된다 ",
         "."),
        "'한 쌍의 고리에 부딪치세요' — ring 을 '고리'로, slam 을 '부딪치다'로 오역",
    link_label="[제작 가이드 보기]"),
    Retranslation("Put Cameria in Transportation if you want to target Abyss scarabs",
                  "심연 갑충석을 노린다면 카메리아(Cameria)를 운송(Transportation) 부서에 배치해라",
                  "'Abyss 갑충석' 미번역"),
    Retranslation(
        "Very common drop from Uber Uber Elder (one of the easiest Uber bosses) with fragments come "
        "from Fortress (the easiest Nightmare map). Use Atlas tree #3 for those Decaying Fragment "
        "farm.",
        ("우버 우버 엘더(가장 쉬운 우버 보스 중 하나)에서 아주 흔하게 떨어진다. 입장 조각은 "
         "요새 지도(가장 쉬운 악몽 지도)에서 나온다. 그 쇠퇴의 조각을 파밍할 때는 ",
         " 를 쓴다."),
        "'Uber'/'Nightmare' 미번역",
    link_label="아틀라스 패시브 트리 #3"),
    Retranslation(
        "Try to force Vorici and It that Fled into Intervention while you are farming these. They "
        "give Harvest and Breach scarabs respectively.",
        "이걸 파밍하는 동안 보리치(Vorici)와 달아난 그것(It That Fled)을 개입(Intervention) 부서로 "
        "몰아넣어라. 각각 수확 갑충석과 균열 갑충석을 준다.",
        "'Harvest와 Breach 갑충석' 미번역",
    ),
    Retranslation("6.14. Arkhon's Tools (Blade Ambusher)",
                  "6.14. 기록관의 도구 (칼날 매복자용)", "'(Blade Ambusher)' 용도 표기 누락 + 이름 미번역"),
    Retranslation("NOTE:", "참고:", "'메모:' — 이 문서의 다른 Note 와 표기가 갈렸다"),
    Retranslation(
        "If Fracture fails -> Either gamba with another recomb (Don't do this) or just accept your "
        "fate and Boat Exalt Slam or Suffixes cannot be changed -> Harvest Reforge Fire for some Fire "
        "res and call it a day. I have not tested with Kishara's Ducat, but it should work exactly "
        'the same as split beast and cannot "delete" the fractured modifier.',
        "분열이 실패하면 → 재조합을 한 번 더 질러 도박하거나(권하지 않는다), 그냥 운명을 받아들이고 "
        "보트 엑잘트 슬램이나 '접미어 변경 불가' 를 걸고 → 수확 재련 화염으로 화염 저항이나 "
        "챙기고 마무리해라. Kishara's Ducat 으로는 테스트해보지 않았지만, 야수 분할과 똑같이 "
        "동작할 것이고 분열된 속성을 '지우지는' 못한다.",
        "'하루로 미루세요' — call it a day 를 직역",
    ),
    Retranslation("6.18. Double corrupt on Nycta's Lantern", "6.18. 닉타의 등불 이중 타락",
                  "'등불에서 이중 타락' 조사 오류"),

    # 7장 베이스 목록 — ilvl 표기 통일
    Retranslation("7. BASES TO FILTER (@FilterBlade)", "7. 필터에 띄울 베이스 (@FilterBlade)",
                  "'표시할' 보다 필터 용어에 맞춘다"),
    Retranslation("Chancing", "기회의 오브 대상", "'챈싱' 음차"),
    Retranslation("Crystal Sceptre (ilvl 1+)", "수정 셉터 (아이템 레벨 1+)", "ilvl 표기 통일"),
    Retranslation("Prismatic Ring (ilvl 1+)", "분광 반지 (아이템 레벨 1+)", "ilvl 표기 통일"),
    Retranslation("Copper Plate (ilvl 1+)", "구리 판금 갑옷 (아이템 레벨 1+)", "ilvl 표기 통일"),
    Retranslation("Giantslayer Helmet (ilvl 81+)", "거인 처형자 투구 (아이템 레벨 81+)", "ilvl 표기 통일"),
    Retranslation("Leviathan Gauntlets (ilvl 81+)", "레비아탄 건틀릿 (아이템 레벨 81+)", "ilvl 표기 통일"),
    Retranslation("Vermillion Ring (ilvl 80+)", "주색 반지 (아이템 레벨 80+)", "ilvl 표기 통일"),
    Retranslation("Ezomyte Tower Shield (ilvl 81+)", "에조미어 거대 방패 (아이템 레벨 81+)",
                  "ilvl 표기 통일"),
    Retranslation("Stygian Vise (ilvl 68+)", "명계의 조임쇠 (아이템 레벨 68+)", "ilvl 표기 통일"),

    # 8장 남은 자리
    Retranslation("NEW - AllFlame/Boat Crafting", "신규 — 올플레임 / 보트 제작", "표기 통일"),
    Retranslation("8.1 Your Shield", "8.1 본인 방패", "'당신의' 존대 혼용"),
    Retranslation("8.4. Your Gloves & Boots", "8.4. 본인 장갑 & 부츠", "표기 통일"),
    Retranslation(
        "If you hit Maximum Life (prefix): settle with the tier you get, then benchcraft (1) Multimod "
        "+ (2) Cannot Roll Attack + (3) Prefixes Cannot Be Changed → Harvest AUGMENT Fire (the "
        "expensive one, not Reforge) for guaranteed +1 to Level of All Fire Skill Gems → pray that "
        "Prefixes Cannot Be Changed survived so you do not have to waste another 2 divines here -> "
        "Harvest Reforge Chaos for guaranteed Chaos Res → AllFlame Exalt slam → benchcraft whatever's "
        "left.",
        "최대 생명력(접두어)이 떴다면: 나온 티어에 만족하고, 벤치 제작으로 (1) 멀티모드 + "
        "(2) '공격 속성 부여 불가' + (3) '접두어 변경 불가' 를 건다 → 모든 화염 스킬 젬 레벨 +1 을 "
        "확정하려면 수확 증강 화염(재련이 아니라 비싼 쪽)을 쓴다 → '접두어 변경 불가' 가 살아남길 "
        "빌어라. 그래야 여기서 신성한 오브 2개를 더 안 버린다 → 카오스 저항을 확정하려면 수확 재련 "
        "카오스 → 올플레임 엑잘트 슬램 → 남은 자리는 벤치 제작으로 채운다.",
        "'2개의 신성을 낭비' — divine(신성한 오브)을 종교 용어로 오역",
    ),
    Retranslation(
        "Then: benchcraft Multimod + Cannot Roll Attack + Prefixes Cannot Be Changed → Harvest "
        "AUGMENT Fire for guaranteed +1 All Fire Skills → if successful, Prefix Cannot Be Changed → "
        "Harvest Reforge Life for any tier of Maximum Life → another Prefix Cannot Be Changed → "
        "Harvest Reforge Chaos for Chaos Res → AllFlame Exalt → finish with a benchcraft.",
        "그다음: 벤치 제작으로 멀티모드 + '공격 속성 부여 불가' + '접두어 변경 불가' → 모든 화염 "
        "스킬 +1 을 확정하려면 수확 증강 화염 → 성공하면 다시 '접두어 변경 불가' → 최대 생명력은 "
        "티어 상관없이 수확 재련 생명력 → 또 '접두어 변경 불가' → 카오스 저항은 수확 재련 카오스 "
        "→ 올플레임 엑잘트 → 마지막은 벤치 제작으로 마무리.",
        "'수확 재련 최대 생명력의 모든 티어에 대한 생명력' — 어순 붕괴",
    ),


    # === 0장: 빌드 이론 =========================================================
    # 목차 항목. 앞 조각이 링크(본문 절로 점프)라 링크 문구까지 같이 고쳐야 한다 —
    # 링크를 남겨두면 화면에 '럭셔리 업그레이드사치 업그레이드 …' 로 겹쳐 나온다.
    Retranslation("LUXURY UPGRADES & EXCLUSIVE UNIQUES",
                  ("사치 업그레이드", " & 전용 고유 아이템"),
                  "'럭셔리 업그레이드 및 독점 고유' — exclusive 는 '전용', 목차 문구가 잘렸다", True),
    Retranslation("BASES TO FILTER", "필터에 띄울 베이스",
                  "목차 항목 전체가 링크 안이라 링크 문구를 직접 고친다", True),
    Retranslation(
        "This is not a theorycrafted guide. Every PoB, almost every unique item acquisition, every "
        "rare craft, and every Atlas strategy used below was from my own SSF journey in 3.29. My PoB "
        "at week 2, where I stopped playing: https://pobb.in/4NT9nBVNFSgJ",
        "이 가이드는 탁상공론이 아니다. 아래에 나오는 모든 PoB, 거의 모든 고유 아이템 수급, 모든 희귀 "
        "제작, 모든 아틀라스 전략은 3.29 에서 내가 직접 SSF 로 겪은 것이다. 플레이를 멈춘 2주 차 "
        "시점의 내 PoB: ",
        "'이론으로 만들어진 가이드' + '내 PoB 2주차에 플레이를 중단했습니다' — 문장이 끊겼다",
        # 주소는 링크 run 이 이미 화면에 들고 있다. 새 번역에 또 적으면 두 번 나온다.
        link_label="https://pobb.in/4NT9nBVNFSgJ",
    ),
    Retranslation("FAQ - AMA section:", "FAQ — 무엇이든 물어보세요:", "'AMA 섹션' 미번역"),
    Retranslation("Q: I heard you need a lot of uniques early game?",
                  "Q: 초반에 고유 아이템이 많이 필요하다던데?", "어투 통일"),
    Retranslation(
        "A: The build functions unique-less. Focus Maximum Life first, Light Radius after. Of course, "
        "Light Radius gear will boost your power by a lot. I cleared 2 Voidstones with a Lori's "
        "Lantern, and then 4 Voidstones with a Nycta's + Solaris Lorica.",
        "A: 이 빌드는 고유 아이템이 하나도 없어도 돌아간다. 최대 생명력을 먼저 챙기고 시야 반경은 그 "
        "다음이다. 물론 시야 반경 장비가 있으면 위력이 크게 오른다. 나는 로리의 등불 하나로 공허석 "
        "2개를, 그다음 닉타의 등불 + 솔라리스 흉갑으로 공허석 4개를 클리어했다.",
        "'빌드 기능은 고유 아이템 없이도 작동합니다' — function 을 '기능'으로 오역",
    ),
    Retranslation(
        "Q: Do you need to start a different class and warrant a good merc in first?",
        "Q: 다른 클래스로 먼저 시작해서 좋은 용병부터 확보해야 하나?",
        "'다른 수업을 시작하고' — class 를 '수업'으로 오역",
    ),
    Retranslation(
        "A: No. I league-started directly as a Luminary and farmed a usable merc in white T1/T2 maps "
        "with Merc encounter chance Atlas nodes. Should be even better now that GGG added a patch "
        "with Act 10 Merc in Control Blocks.",
        "A: 아니다. 나는 루미너리로 바로 리그를 시작했고, 용병 조우 확률 아틀라스 노드를 찍은 상태로 "
        "흰색 T1/T2 맵에서 쓸 만한 용병을 파밍했다. GGG 가 액트 10 Control Blocks 에 용병을 넣는 "
        "패치를 했으니 지금은 더 쉬울 것이다.",
        "'I는 루미너리로' — 대명사가 그대로 남았다",
    ),
    Retranslation("Q: Do you need a Rotmother's Mutiny?", "Q: 부패모의 반란이 꼭 필요한가?",
                  "'이(가)' 조사 오류"),
    Retranslation(
        "A: No. A rare amulet with +1 Fire Skill Gem level (Harvest Reforge Fire/alt-spam) + T1/T2 "
        "life via recomb can work for early game. Also most likely this Clam Amulet will be gone in "
        "3.30.",
        "A: 아니다. '화염 스킬 젬 레벨 +1'(수확 재련 화염 또는 변화의 오브 반복)에 재조합으로 T1/T2 "
        "생명력을 붙인 희귀 목걸이면 초반은 충분하다. 게다가 이 조개 목걸이는 3.30 에서 사라질 "
        "가능성이 높다.",
        "'생명력이 +1인 희귀 목걸이은' — +1 의 대상이 틀렸고 조사도 깨졌다",
    ),
    Retranslation("Q: Do you need a Kaom's Heart?", "Q: 카옴의 심장이 꼭 필요한가?", "어투 통일"),
    Retranslation(
        "A: No. Foulborn Solaris Lorica (25% light radius + 25% Ele taken as Chaos) or Pragmatism are "
        "your go-to early body armours. Kaom's is your end-game target, not a gate.",
        "A: 아니다. 초반 갑옷은 삿된 솔라리스 흉갑(시야 반경 25% + 받는 원소 피해의 25%를 카오스로 "
        "전환)이나 실용주의가 무난하다. 카옴의 심장은 엔드게임 목표지 통과 조건이 아니다.",
        "'실용주의은' 조사 오류 + Foulborn 미번역",
    ),
    Retranslation("Q: Do you need a Svalinn?", "Q: 스발린이 꼭 필요한가?", "어투 통일"),
    Retranslation(
        "Do you need link mastery \u201cLink skills link to 1 additional random target\u201d after Hallowed "
        "Monarch?",
        "거룩한 국왕을 끼고 나면 연결 숙련 '연결 스킬이 무작위 대상 1명에게 추가로 연결' 이 필요한가?",
        "'링크 마스터리' 음차",
    ),
    Retranslation(
        "A: No. The \u201cMaximum 1 Link from any source per target\u201d written in any Link skill meant to "
        "tell you that you cannot have MULTIPLE links to the SAME target. Not the other way around.",
        "A: 아니다. 연결 스킬에 적힌 '대상 하나당 모든 출처를 합쳐 연결 최대 1개' 는 같은 대상에게 "
        "연결을 여러 개 걸 수 없다는 뜻이다. 그 반대가 아니다.",
        "'모든 소스에서 최대 1 연결' — 조사가 빠져 뜻이 안 잡힌다",
    ),
    Retranslation(
        "Why all the Eldritch implicits in your Merc gear have \"While a Unique Enemy/a Pinnacle Atlas "
        "Boss is in your Presence\" condition?",
        "용병 장비의 섬뜩한 고정 속성이 전부 '고유 적 / 정점 아틀라스 보스가 존재하는 동안' 조건이 "
        "붙어 있는 이유는?",
        "'고유한 적/a 아틀라스 최종 보스이(가)' — 관사가 그대로 남고 조사가 깨졌다",
    ),
    Retranslation(
        "A: You are considered a Pinnacle Boss to your merc. Remember that you will need Tier 2 "
        "(Greater Eldritch ichor/ember) to roll Unique mod. And you need Tier 3 (Grand) to roll "
        "Pinnacle Boss mod.",
        "A: 용병 입장에서는 당신이 정점 보스로 취급된다. 고유 조건 속성을 굴리려면 2티어"
        "(상급 섬뜩한 영액/불씨)가, 정점 보스 조건 속성을 굴리려면 3티어(우수한)가 필요하다는 걸 "
        "기억해라.",
        "'귀하는 ... 간주됩니다' 존대 혼용 + 'Greater Eldritch icor' 오타 그대로",
    ),
    Retranslation("How to change my merc gear sockets to all White?",
                  "용병 장비 홈을 전부 흰색으로 바꾸는 방법은?", "어투 통일"),
    Retranslation(
        "A: Assuming most of your gears have Abyssal sockets, which leaves the maximum sockets to be "
        "3 for Boots/Gloves/Helmet. Chrome orb until 2 White + 1 Color. Bench craft it to 2 socket. "
        "Then Bench craft it back to full sockets.",
        "A: 장비 대부분에 심연 홈이 있다고 치면 부츠/장갑/투구의 최대 홈은 3개다. 흰색 2 + 유색 "
        "1 이 나올 때까지 색채의 오브를 돌린다. 벤치 제작으로 홈을 2개로 줄인다. 그다음 벤치 "
        "제작으로 다시 최대 홈까지 올린다.",
        "'2 화이트 + 1 컬러까지 크롬 오브' — 동사가 없고 색상명이 음차됐다",
    ),
    Retranslation(
        "There are a lot of unused Life Masteries, should I use RuneGrafts on them?",
        "안 쓰는 생명력 숙련이 많은데 거기에 룬 접목을 써도 되나?",
        "'라이프 마스터리' 음차",
    ),
    Retranslation(
        "A: No. Applying a RuneGraft onto any Life Mastery will break the condition for our most "
        "important one \u201c10% more Maximum Life if you have at least 6 Life Masteries allocated\u201d.",
        "A: 안 된다. 생명력 숙련에 룬 접목을 바르면 가장 중요한 '생명력 숙련을 6개 이상 할당한 경우 "
        "최대 생명력 10% 증폭' 의 조건이 깨진다.",
        "'최대 생명력 10% 더 많은' — more 를 서술어 없이 옮겼다",
    ),

    # === 1장: PoB 진행 ==========================================================
    Retranslation("1. POB PROGRESSION", "1. PoB 진행 단계", "표기 통일"),
    Retranslation("PoB Link", "PoB 링크", "'PoB 연결' — 여기서는 URL 이다"),
    Retranslation("Level & Description", "레벨 & 설명", "표기 통일"),
    Retranslation("Level 54 - Campaign with Sunder", "레벨 54 — 산산조각으로 캠페인",
                  "'캠페인 및 산산조각' — with 를 '및'으로 옮겨 관계가 사라졌다"),
    Retranslation(
        "Level 76 - Farm a Blade Ambusher/Wild Strike Combatant in Control Blocks Act 10, "
        "transitioning to bot",
        "레벨 76 — 액트 10 Control Blocks 에서 Blade Ambusher / 사나운 타격 Combatant 를 파밍하고 "
        "봇 형태로 전환",
        "'농사하고' — farm 을 '농사'로 오역",
    ),
    Retranslation(
        "Level 90 - No block, no warcries. Just life for scaling merc's damage. Lightning coil is "
        "whatever I gathered during the run. Not your go-to chest even for early game.",
        "레벨 90 — 막기도 없고 전투의 함성도 없다. 오직 생명력만으로 용병 피해를 키운다. "
        "번개 도선은 진행하다 주운 것일 뿐이다. 초반에도 권할 만한 갑옷은 아니다.",
        "'초기 게임에서도 갑옷에 들어갈 수 없습니다' — go-to chest 를 반대로 옮겼다",
    ),
    Retranslation("Level 93 - 2 Voidstones", "레벨 93 — 공허석 2개", "표기 통일"),
    Retranslation("Level 97 - 4 Voidstones", "레벨 97 — 공허석 4개", "표기 통일"),
    Retranslation(
        "Level 100 - Day 9 when I down 10/10 Uber bosses. Iron Reflexes is to abuse my Merc's Grace "
        "aura.",
        "레벨 100 — 우버 보스 10종을 전부 잡은 9일 차. 철의 반사신경은 용병의 은총 오라를 "
        "활용하려고 찍은 것이다.",
        "'Uber 상사를 10/10명 쓰러뜨렸습니다' — boss 를 '상사'로 오역",
    ),
    Retranslation("Level 100 - Week 2 where I stopped playing", "레벨 100 — 플레이를 멈춘 2주 차",
                  "표기 통일"),

    # === 2장: 용병 선택 & 보조 스킬 =============================================
    Retranslation("Blade Ambusher (Mapping = D-, Bossing = S+)",
                  "Blade Ambusher (맵 클리어 = D-, 보스전 = S+)", "'맵핑' 음차"),
    Retranslation("Combatant (Mapping = B+, Bossing = B+)",
                  "Combatant (맵 클리어 = B+, 보스전 = B+)", "'맵핑' 음차"),
    Retranslation(
        "Jungroan's merc during the 3.26 gauntlet. Trap-based bosser - much better survivability "
        "compared to a melee Combatant early game. SUPER easy for gearing. I would recommend to get "
        "him first, since early game you won't have juiced maps to clear.",
        "3.26 건틀릿에서 Jungroan 이 쓰던 용병. 덫 기반 보스 딜러로, 초반 근접 Combatant 보다 "
        "생존력이 훨씬 낫다. 장비 맞추기도 아주 쉽다. 초반에는 어차피 주스를 두른 맵을 돌 일이 "
        "없으니 이쪽을 먼저 확보하길 권한다.",
        "'덫 기반 보스 — 근접전 Combatant 게임 초반에 비해' — 비교 대상이 잘렸다",
    ),
    Retranslation("Very popular in 3.29. There are 2 versions:",
                  "3.29 에서 아주 인기가 많다. 두 가지 버전이 있다:", "어투 통일"),
    Retranslation(
        "1- Frost Blades/Static Strike is superb for clearing but will struggle with single target "
        "early on. Do NOT plan your voidstones progression around him.",
        "1 — 서리 칼날 / 정전기 타격은 클리어가 훌륭하지만 초반 단일 대상이 약하다. 공허석 진행을 "
        "이 용병 기준으로 계획하지 마라.",
        "'공극석' 오타",
    ),
    Retranslation(
        "2- Wild Strike/Static Strike is only somewhat okay for clearing, but has much better single "
        "target. A good choice for starting merc if you hate the trapper merc.",
        "2 — 사나운 타격 / 정전기 타격은 클리어는 그럭저럭이지만 단일 대상이 훨씬 낫다. 덫 용병이 "
        "싫다면 시작 용병으로 좋은 선택이다.",
        "'사냥꾼 용병' — trapper 를 '사냥꾼'으로 오역",
    ),
    Retranslation("Key skill(s) & support priority", "핵심 스킬 & 보조 젬 우선순위",
                  "'지원 우선순위' — support 는 보조 젬"),
    Retranslation("Static Strike: whatever.", "정전기 타격: 아무거나 붙여도 된다.",
                  "'뭐든지' — 문장이 아니다"),
    Retranslation(
        "Stay away from Helix, he will pop Helix even when mobs are not around.",
        "영체 나선은 피해라 — 주변에 몹이 없어도 계속 터뜨린다.",
        "'Helix에서 멀리 떨어지십시오' — 스킬 채택을 피하라는 뜻인데 물리적 거리로 읽힌다",
    ),
    Retranslation("Utility kit", "유틸리티 구성", "'키트' 음차"),
    Retranslation(
        "Summon Skitterbot is mandatory for free Shock and for abusing Taming later.",
        "원격 기폭 장치 소환은 필수다. 감전을 공짜로 깔아주고, 나중에 조련을 활용하는 데도 쓰인다.",
        "'Skitterbot 소환' 미번역 + 'Taming 남용' 미번역",
    ),
    Retranslation("For the other utility slot, here's the priority order:",
                  "남은 유틸리티 자리는 아래 우선순위로 고른다:", "어투 통일"),
    Retranslation(
        "Grace (defensive): you can spec Iron Reflexes to get free 5000 flat armour from his aura.",
        "은총(방어형): 철의 반사신경을 찍으면 이 오라에서 고정 방어도 5000을 공짜로 얻는다.",
        "'무료로 5000 플랫 아머' — flat armour 음차",
    ),
    Retranslation(
        "Bear Trap (offensive): solely for Pinnacle Bosses fight since it will slow him down mapping "
        "wise. But it's 25% increased damage taken for other traps.",
        "곰 덫(공격형): 맵을 돌 때는 용병 속도를 떨어뜨리므로 정점 보스전 전용이다. 대신 다른 덫에 "
        "대해 받는 피해를 25% 올려준다.",
        "'맵핑의 속도가 느려지므로' — 주어가 맵이 됐다",
    ),
    Retranslation("Flame Dash: acceptable.", "화염 질주: 무난하다.", "'허용됩니다' 직역"),
    Retranslation("Smoke Mine: bricks the build. Do not ever get this.",
                  "연막 지뢰: 빌드를 망가뜨린다. 절대 고르지 마라.",
                  "'빌드를 벽돌로 만듭니다' — brick 직역"),
    Retranslation(
        "Wrath plus Dash. Movement skill is actually perfect for melee merc, no need for double auras "
        "here.",
        "진노 + 질주. 이동 스킬은 근접 용병에게 오히려 딱 맞는다. 여기서 오라를 둘씩 켤 필요는 없다.",
        "'근접 공격에 적합합니다. 용병 여기서는' — 어절이 밀려 문장이 끊겼다",
    ),
    Retranslation("Notes", "참고", "'메모' — 문서 내 다른 Note 와 표기가 갈렸다"),
    Retranslation(
        "But of course, small ring also equals to missing target once it moves.",
        "물론 고리가 작다는 건 대상이 움직이면 빗나간다는 뜻이기도 하다.",
        "'작은 고리도 일단 움직이면 목표를 놓치는 것과 같습니다' — 주어가 뒤집혔다",
    ),
    Retranslation(
        "Why NO Multistrike on both versions? - This merc is mainly for mapping. Multistrike will "
        "lock him in place. When you have enough damage to clear a pack, this will be a problem. "
        "Also, there's no \u201cmore damage per repeat\u201d like the player version.",
        "왜 두 버전 모두 연속타격 보조를 안 쓰나? — 이 용병은 주로 맵을 도는 용도다. 연속타격 "
        "보조는 그를 제자리에 묶어버린다. 한 무리를 정리할 만한 피해가 나오는 시점부터는 그게 "
        "문제가 된다. 게다가 플레이어 버전과 달리 '반복당 피해 증폭' 이 없다.",
        "'충분한 피해를 입으면' — 피해를 입는 쪽이 뒤바뀌었다",
    ),
    Retranslation(
        "Why NO Return on Frost Blades? - For Frost Blades to actually return, you will need A LOT of "
        "projectile speed. Most of the popular map layouts have walls for it to bounce. Try open "
        "layout and you will not see it returns at all.",
        "왜 서리 칼날에 회귀 보조를 안 쓰나? — 서리 칼날이 실제로 되돌아오게 하려면 투사체 속도가 "
        "아주 많이 필요하다. 인기 있는 맵 구조는 대부분 튕길 벽이 있어서 그렇게 보일 뿐이다. "
        "개활지 구조에서 돌려보면 아예 안 돌아온다.",
        "'반환이 없는 이유' — Return Support 를 '반환'으로 오역",
    ),
    Retranslation(
        "Why no Chain or GMP for Wild Strike? - Wild Strike rotates between Fire (AOE), Cold "
        "(Projectile) and Lightning (Chaining). So Inc AoE will only support Fire, GMP will only "
        "support Cold, and Chain will only support Lightning. Any of the above will NOT break the "
        "build. They are just not in high priorities.",
        "왜 사나운 타격에 연쇄 보조나 GMP 를 안 쓰나? — 사나운 타격은 화염(범위), 냉기(투사체), "
        "번개(연쇄)를 번갈아 낸다. 그래서 효과 범위 증가는 화염에만, GMP 는 냉기에만, 연쇄 보조는 "
        "번개에만 붙는다. 셋 중 무엇을 써도 빌드가 망가지진 않는다. 우선순위가 높지 않을 뿐이다.",
        "'그들은 단지 높은 우선순위에 있지 않습니다' 직역",
    ),

    # === 3장: 캠페인 ============================================================
    Retranslation("Act / Level", "액트 / 레벨", "표기 통일"),
    Retranslation("What To Do", "할 일", "'해야 할 일' 어색"),
    Retranslation("Act 1", "액트 1", "'1막' — 이 문서의 다른 표기와 갈렸다"),
    Retranslation("Act 2", "액트 2", "표기 통일"),
    Retranslation("Act 3 - Mercenary Milestone", "액트 3 — 용병 분기점", "'마일스톤' 음차"),
    Retranslation("Act 5 - Sceptre Gamba", "액트 5 — 셉터 도박", "표기 통일"),
    Retranslation(
        "Add Herald of Ash, Blood Rage, Melee Physical Damage, Close Combat. Bandit: Kill All or "
        "(my personal choice) Oak. Tree checkpoint: pick up some 2-handed wheel, go towards the "
        "Marauder area first. Remember to gamble for a better Axe whenever you have gold.",
        "재의 전령, 피의 격노, 근접 물리 피해 보조, 근접 전투 보조를 추가한다. 도적단: 전원 처치 "
        "또는 (내 선택은) 오크. 트리 체크포인트: 양손 무기 구간을 일부 챙기면서 머라우더 쪽으로 "
        "먼저 간다. 골드가 생길 때마다 더 좋은 도끼를 도박으로 노리는 걸 잊지 마라.",
        "'Bandit: Kill All 또는 Oak' 미번역 + '금이 있을 때마다' — gold 를 '금'으로 오역",
    ),
    Retranslation(
        "Add Vulnerability, swap Haste/Pride as needed. Mercenary duels become available. Guaranteed "
        "spawns confirmed at league launch in The Sceptre of God (Act 3), The Grand Arena (Act 4), "
        "The Ridge (Act 6), The Hidden Underbelly (Act 8) and Control Blocks (Act 10). Zone-reset "
        "technique: leave and re-enter the same area via waypoint/portal to reroll the Mercenary.",
        "취약성을 추가하고 가속 / 자부심은 필요에 따라 바꿔 낀다. 이때부터 용병 결투가 열린다. "
        "리그 출시 시점 기준으로 확정 등장이 확인된 곳은 The Sceptre of God(액트 3), "
        "The Grand Arena(액트 4), The Ridge(액트 6), The Hidden Underbelly(액트 8), "
        "Control Blocks(액트 10)이다. 구역 초기화 요령: 웨이포인트나 포털로 같은 지역을 나갔다 "
        "다시 들어가면 용병이 다시 굴려진다.",
        "'The 셉터 of God' — 지명이 반만 번역돼 인게임에서 못 찾는다",
    ),
    Retranslation("Save your gold. And start doing Charts/Voyage from here.",
                  "골드를 모아둬라. 그리고 이 시점부터 해도 / 항해를 돌리기 시작한다.",
                  "'금을 저장하십시오' — gold 오역"),
    Retranslation(
        "Rest of the act follows Havoc's guide on Maxroll or just freestyle from here. Your tree "
        "should look like this at 54 https://pobb.in/09QzQ1VfCdXR",
        "이후 진행은 Maxroll 의 Havoc 가이드를 따르거나 그냥 알아서 해도 된다. 레벨 54 시점의 트리는 "
        "이런 모습이어야 한다: ",
        "'나머지 행위는' — act(액트)를 '행위'로 오역, 마지막 문장이 끊겼다",
        link_label="https://pobb.in/09QzQ1VfCdXR",
    ),
    Retranslation("3.2 Lab Timing & Ascendancy Order", "3.2 미궁 진행 시점 & 전직 순서",
                  "'실습 시간' — Lab 을 실습으로 오역"),
    Retranslation("Lab", "미궁", "'랩' 음차"),
    Retranslation("Normal Lab", "일반 미궁", "표기 통일"),
    Retranslation("Cruel Lab", "잔혹한 미궁", "표기 통일"),
    Retranslation("Merciless Lab", "무자비한 미궁", "표기 통일"),
    Retranslation("Uber Lab", "영원의 미궁", "표기 통일"),
    Retranslation("Take Noble Blood for permanent Mercenary.",
                  "영구 용병을 위해 Noble Blood 를 찍는다.",
                  "'영구 용병에는 ... 사용합니다' — Take(찍다)가 사라졌다"),
    Retranslation(
        "Take Oath of Fealty for permanent Flame Link (available in Act 4). Also cancels out the "
        "double death condition of Flame Link.",
        "영구 화염의 연결을 위해 Oath of Fealty 를 찍는다(액트 4부터 가능). 화염의 연결의 "
        "동반 사망 조건도 함께 없애준다.",
        "'이중 사망 조건을 취소합니다' 직역",
    ),
    Retranslation(
        "Take Legendary Items. Not important for campaign. Flex between 2 unique slots later "
        "depending on your drops.",
        "Legendary Items 를 찍는다. 캠페인에서는 중요하지 않다. 나중에 드롭 상황에 따라 고유 아이템 "
        "2자리를 바꿔 끼면 된다.",
        "'상품에 따라' — drop 을 '상품'으로 오역",
    ),
    Retranslation("3.3 Full Bot Respec Checkpoint", "3.3 완전 봇 전환 재분배 시점",
                  "'재규격 체크포인트' — respec 오역"),
    Retranslation("3.4 Post-respec Gem Links:", "3.4 재분배 이후 젬 링크:",
                  "'사양 변경 후 Gem 링크' — respec 을 '사양 변경'으로 오역"),
    Retranslation("This guide runs Blood Magic throughout. I will not cover the Aura bot version here.",
                  "이 가이드는 처음부터 끝까지 혈마법으로 간다. 오라 봇 버전은 여기서 다루지 않는다.",
                  "'Blood Magic을 실행합니다' 미번역"),
    Retranslation("AURA: 2L Purity of Elements - Eternal Blessing.",
                  "오라: 2링크 원소의 순수함 — 영원한 축복 보조.", "'아우라' 음차 + '2L' 미번역"),
    Retranslation(
        "AURA: 2L Precision - Generosity early (mostly for the extra Accuracy since your mercs do not "
        "have \u201cHit cannot be evaded\u201d early on). Switch to 1L Precision & 1L Vitality later.",
        "오라: 초반에는 2링크 정밀함 — 관대함 보조(용병이 아직 '무조건 명중' 를 못 갖췄으니 "
        "주로 추가 정확도 때문이다). 나중에 1링크 정밀함 + 1링크 활력으로 바꾼다.",
        "'추가 정확도에 대한 경우가 많습니다' — 문장이 무너졌다",
    ),
    Retranslation(
        "MOVEMENT: 3L Shield Charge - Momentum/Pyre Support - Faster Attack & 1L Frost Blink (swap in "
        "Pyre Support only for Pinnacle Bosses for free Cover in Ash).",
        "이동기: 3링크 방패 돌진 — 기세 보조 / Pyre Support — 공격 속도 증가 보조, 그리고 1링크 "
        "Frost Blink (Pyre Support 는 정점 보스전에서만 끼운다. 재로 뒤덮임을 공짜로 걸기 위해서다).",
        "'(장작 보조에서 교체) Ash의 무료 커버' — 괄호가 문장 중간에서 끊겼다",
    ),
    Retranslation("CURSE: Flammability early. Assassin's Mark later.",
                  "저주: 초반에는 인화성, 나중에 암살자의 징표.",
                  "'인화성 일찍. 암살자의 징표 나중에.' — 부사만 남았다"),
    Retranslation(
        "MINE: Bossing only. For all options below, do NOT detonate/use Automation for detonation. "
        "You just throw the mine and leave it there to trigger the effect of the mine aura.",
        "지뢰: 보스전 전용. 아래 선택지는 전부, 기폭시키지 말고 자동화 보조로 기폭시키지도 마라. "
        "지뢰를 던져놓고 그대로 두면 지뢰 오라 효과가 발동한다.",
        "'광산' — Mine(지뢰)을 광산으로 오역",
    ),
    Retranslation(
        "Early Game: 1L Pyroclast Mine/Pyroclast Mine of Sabotage: 1-link wonder for 15-25% Fire "
        "Exposure. Drop once you have Exposure from other sources like Eldritch implicit on merc's "
        "gloves or AG's Elemental Army. Note: AG's Elemental Army will only provide Fire Exposure "
        "once you have Flame Link on him, which is NOT recommended before Hallowed Monarch.",
        "초반: 1링크 화산탄 지뢰 / 방해 공작의 화산탄 지뢰 — 화염 노출 15~25%를 1링크로 뽑는 알짜다. "
        "용병 장갑의 섬뜩한 고정 속성이나 AG 의 원소의 군단처럼 다른 데서 노출이 생기면 빼라. "
        "참고: AG 의 원소의 군단은 AG 에게 화염의 연결을 걸어야만 화염 노출을 주는데, 거룩한 국왕 "
        "이전에는 권하지 않는다.",
        "'1링크 원더' 음차 + '노출이 있으면 드롭하세요' — drop(빼다)을 '드롭'으로 오역",
    ),
    Retranslation("ANIMATE GUARDIAN: AG - Meat Shield - Elemental Army - Minion Life.",
                  "수호자 기동: AG — 육탄 방어 보조 — 원소의 군단 보조 — 소환수 생명력 보조.",
                  "'애니메이션 수호자' — Animate 를 '애니메이션'으로 오역"),
    Retranslation("OR ANIMATE GUARDIAN OF SMITING: AGoS - Meat Shield - Elemental Army - Multistrike.",
                  "또는 징벌의 수호자 기동: AGoS — 육탄 방어 보조 — 원소의 군단 보조 — 연속타격 보조.",
                  "'애니메이션 강타의 수호자' — 이름이 두 번 틀렸다"),
    Retranslation(
        "If you start linking your AG with Flame Link, you will not be protected by Oath of Fealty. "
        "Do not let your AG die.",
        "AG 에게 화염의 연결을 걸기 시작하면 Oath of Fealty 의 보호를 못 받는다. AG 가 죽지 않게 "
        "해라.",
        "'당신의 AG이 죽게 두지 마세요' 조사 오류",
    ),
    Retranslation(
        "Meat Shield and Elemental Army are not just defensive gem. They both have conditional damage "
        "multiplier. Also Meat Shield will fix the silly AI movement of your AG by keeping him close.",
        "육탄 방어 보조와 원소의 군단 보조는 단순한 방어용 젬이 아니다. 둘 다 조건부 피해 배율을 "
        "갖고 있다. 게다가 육탄 방어 보조는 AG 를 가까이 붙여둬서 멍청한 AI 이동을 잡아준다.",
        "'방어 보석' — Gem 은 젬",
    ),
    Retranslation("You can craft a pseudo 6L using Elder Gloves for him [View Crafting Guide].",
                  " — AG 용 유사 6링크는 엘더 장갑으로 제작할 수 있다.",
                  "'[제작 가이드 보기]에게 엘더 장갑을 사용하여' — 링크가 문장 맨 앞이라 "
                  "링크는 그대로 두고 뒤 문장만 다시 쓴다", link_label="[제작 가이드 보기]"),
    Retranslation(
        "WARCRIES (Optional and completely based on preference - remember to take the Warcries cluster "
        "with \u201cMinimum 10 powers\u201d mastery): 3L Enduring Cry - Urgent Orders Support - Pick 1 from More "
        "Duration Support/Ancestral Cry/Battle Mage Cry.",
        "전투의 함성(선택, 순전히 취향이다 — '최소 위력 10' 숙련이 붙은 함성 군집을 찍는 걸 잊지 "
        "마라): 3링크 인내의 함성 — 긴급 명령 보조 — 지속시간 증폭 보조 / 선대의 함성 / "
        "전투마법사의 함성 중 1개 선택.",
        "'WARCRIES' 미번역 + 'Battle Mage Cry' 미번역",
    ),
    Retranslation(
        "CONVOCATION (Optional): 2L Convocation - Automation. You will most likely have to drop this "
        "late game since we are super socket starving.",
        "소집(선택): 2링크 소집 — 자동화 보조. 홈이 극심하게 부족해서 후반에는 결국 뺄 가능성이 "
        "높다.",
        "'이 늦은 게임을 중단해야' — drop this late game 을 어절 순서대로 옮겼다",
    ),

    # === 2차 보수: 표 안에 기계번역으로 남아 있던 문단 =============================
    # 1차 작업이 본문 위주로 돌면서 표 셀 일곱 자리가 그대로 남았다. 문서 나머지가
    # 해라체라 이 자리만 '합니다'체로 튀고, 두 자리는 조사까지 깨져 있었다.
    Retranslation(
        "The “Slower Projectile” roll matters so much for single target damage, especially for "
        "your cookie cutter Spectral Helix of Trarthus trap. The blades go in a spiral, start at the "
        "center of the ring and fan out at the end. It has to rotate a fix amount of time (4.25 "
        "rotations). That means with Slower Projectile, it forces the ring of blades to be clustered "
        "right in the middle where it starts, instead of travelling fast to the end of the spiral. "
        "This skill has a 0.3s internal cooldown per tick. This cooldown keeps resetting while the "
        "blades circle around the boss, resulting in enormous damage. You would want to combo this "
        "with the Infamous Combatant mod — “Each Projectile created by Attacks you make with a "
        "Melee Weapon has between 50% more and 50% less Projectile Speed at random.”",
        "'투사체 속도 감소 보조' 가 붙었는지는 단일 대상 피해를 좌우한다. 정석 구성인 트라투스의 영체 "
        "나선 덫이라면 더 그렇다. 칼날은 나선을 그리며 고리 중심에서 출발해 끝에서 퍼진다. 회전 횟수는 "
        "4.25회로 고정돼 있다. 그래서 투사체 속도 감소 보조를 붙이면 칼날 고리가 나선 끝까지 빠르게 "
        "빠져나가는 대신, 출발 지점인 한가운데에 뭉친 채로 돈다. 이 스킬은 틱마다 0.3초의 내부 재사용 "
        "대기시간이 있는데, 칼날이 보스 주위를 도는 동안 이 대기시간이 계속 초기화되면서 피해가 "
        "폭발한다. 여기에 Infamous 전투원의 속성 '근접 무기로 하는 공격이 생성한 각 투사체의 투사체 "
        "속도가 무작위로 50% 증폭 ~ 50% 감소 사이' 를 겹치면 좋다.",
        "'쿠키 커터'·'블레이드'·'클러스터되도록' — 기계번역이 통째로 남았고 문체도 혼자 존댓말이었다",
    ),
    Retranslation(
        "Spectral Throw from the start; pick up Leap Slam around level 10. Sunder unlocks at level 12, "
        "after Fairgraves. Tree checkpoint: path toward the Marauder-side 2-Handed Weapon / melee "
        "physical damage cluster nearest Scion’s start, picking up Life nodes along the way. Pick up "
        "a Decoy Totem and level it up — you’ll need it for dueling Mercs later. Remember to gamble "
        "for a better Axe whenever you have gold.",
        "처음부터 환영 무기 투척으로 간다. 10레벨쯤 도약 강타를 챙기고, 페어그레이브즈를 끝내면 "
        "12레벨에 산산조각이 열린다. 트리 체크포인트: 사이온 시작점에서 가장 가까운 머라우더 쪽 양손 "
        "무기 / 근접 물리 피해 군집으로 길을 내면서 생명력 노드를 함께 챙긴다. 미끼 토템을 받아 "
        "레벨을 올려둬라 — 나중에 용병과 결투할 때 쓴다. 골드가 생길 때마다 더 좋은 도끼를 도박으로 "
        "노리는 걸 잊지 마라.",
        "이 셀만 존댓말이라 같은 표의 액트 2·3 칸과 문체가 어긋났다",
    ),
    Retranslation(
        "A very important checkpoint is at level 41. Charts/Voyages can earn you a ton of gold. You "
        "will use it to gamba for a Sceptre, looking for Nycta’s Lantern. Can also do this with an alt.",
        "41레벨이 아주 중요한 분기점이다. 해도 / 항해로 골드를 잔뜩 벌 수 있고, 그 골드로 셉터를 "
        "도박해 닉타의 등불을 노린다. 부 캐릭터로 해도 된다.",
        "이 셀만 존댓말이라 바로 아래 칸과 문체가 어긋났다",
    ),
    Retranslation(
        "Take Golden Glory. Can get this before Legendary Items if you have no luck for uniques. Take "
        "“Energy Shield Mastery” and “Light of Divinity” in your Passive tree for a total of 40% "
        "Light Radius early on.",
        "황금의 영광을 찍는다. 고유 아이템 운이 없었다면 Legendary Items 보다 먼저 찍어도 된다. "
        "패시브 트리에서 '에너지 보호막 숙련' 과 '신성의 빛' 을 찍으면 초반에 시야 반경을 합쳐 "
        "40% 확보한다.",
        "같은 표의 다른 미궁 칸은 해라체인데 이 칸만 존댓말이었다",
    ),
    Retranslation(
        "1. Nycta’s Lantern: Could have gotten this at level 41 gambling (Check Campaign). If you did "
        "not, farm Light and Truth div card in Palace (natural Tier 9) or Ivory Temple (natural tier 13, "
        "much better map layout). Also, add card into a higher tier in your filter.",
        ("1. 닉타의 등불: 41레벨 셉터 도박으로 이미 얻었을 수도 있다(",
         " 절 참고). 못 얻었다면 궁전(기본 9티어)이나 상아 사원(기본 13티어, 맵 구조가 훨씬 낫다)에서 "
         "'빛과 진실' 점술 카드를 파밍한다. 필터에서 이 카드를 더 높은 티어로 올려두는 것도 잊지 마라."),
        "존댓말 + 'natural Tier' 를 '기본 등급' 으로 옮겨 문서의 티어 표기와 어긋났다",
        link_label="캠페인",
    ),
    Retranslation(
        "This tree is to target farming King’s Heart divination card for our Kaom’s Heart. The key is "
        "monster density. The other goal is to random drop Memory of Trauma (for Enmity’s Embrace) and "
        "Ritual Nameless hunt.",
        "이 트리는 카옴의 심장에 쓸 '왕의 심장' 점술 카드를 표적 파밍하기 위한 것이다. 핵심은 몬스터 "
        "밀도다. 곁가지 목표는 원한의 품에 쓸 Memory of Trauma 무작위 드롭과 이름 없는 의식 사냥이다.",
        "존댓말 + '의식의 무명 몬스터 조우' — Ritual Nameless 를 몬스터 이름으로 오해했다",
    ),
    Retranslation(
        "1. Roll your Nightmare maps to item quantity 90%+. Use https://poe.re/#/maps to find your own "
        "regex since there are too many janky mods bricking your build. I would definitely want to stay "
        "away from “Reduced chance to block”, “Cannot regen” and “Extra Maximum Life as Energy "
        "Shield”.",
        ("1. 악몽 지도는 아이템 수량 90% 이상으로 굴린다. 빌드를 망가뜨리는 고약한 속성이 너무 많으니 ",
         " 에서 자기 정규식을 만들어 써라. 나라면 '막기 확률 감소', '재생 불가', '추가 최대 생명력을 "
         "에너지 보호막으로' 는 무조건 피한다."),
        "'버벅거리는 모드'(janky mods 오역) + '최대 생명력를 에너지 보호막로' 조사 붕괴",
        link_label="https://poe.re/#/maps",
    ),

    # === 3차 보수: 본문에 남은 존댓말 기계번역 =====================================
    # 이 문서는 통째로 영문 기계번역이 원본이다. 그러니 "사람이 합니다체로 쓴 문단"
    # 같은 건 없다 — 읽을 만하게 나온 기계번역일 뿐이다. 문서 문체(해라체)로 맞춘다.
    Retranslation(
        "Luminary (new Scion ascendancy in 3.29) for permanent merc.",
        "루미너리(3.29 신규 사이온 전직)로 영구 용병을 운용한다.",
        "문체 불일치 — 이 문단만 존댓말",
    ),
    Retranslation(
        "You are playing as a support character for your merc, stacking life and light radius to "
        "scale Flame Link's flat fire damage.",
        "플레이어는 용병을 받쳐 주는 서포터다. 생명력과 시야 반경을 쌓아 화염의 연결이 주는 고정 "
        "화염 피해를 키운다.",
        "존댓말 + flat 을 '플랫' 으로 음차 — 문서 다른 곳은 전부 '고정'",
    ),
    Retranslation(
        "Every point of life → becomes flat fire damage for the merc (via Flame Link) → multiplied "
        "by Link Effect (from Luminary ascendancy node Golden Glory).",
        "생명력 1당 → 화염의 연결을 거쳐 용병의 고정 화염 피해가 되고 → 루미너리 전직 노드 황금의 "
        "영광의 연결 효과로 증폭된다.",
        "존댓말 + '플랫' 음차",
    ),
    Retranslation(
        "In 3.29, my character has 16k Maximum Life and 235% Light Radius. That means a casual level "
        "25 Flame Link will give our merc 3621 - 4090 flat fire damage.",
        "3.29 에서 내 캐릭터는 최대 생명력 16,000, 시야 반경 235% 다. 대충 굴린 25레벨 화염의 "
        "연결만으로 용병에게 고정 화염 피해 3,621~4,090 이 들어간다.",
        "존댓말 + '플랫' 음차",
    ),
    Retranslation(
        "A: It's an 8% drop. Treat this as an end-game goal only. I got 4 Voidstones and ran all "
        "needed Atlas strats without it. I did get the ring though, after 22 Trauma's. Every merc "
        "should have alternatives before the Enmity's Embrace & Untouched Soul combo. This guide uses "
        "a Blade Ambusher as your main merc earlier since he can have some very strong alternatives: "
        "Arkhon's Tools belt (farm-able from Neglect) and Vulconus (global drop - t3 unique weapons).",
        "A: 드롭률 8% 다. 엔드게임 목표로만 잡아라. 나는 이 반지 없이 공허석 4개를 먹고 필요한 "
        "아틀라스 전략을 전부 돌렸다. 반지는 외상의 기억을 22번 돌리고 나서야 나왔다. 원한의 품 + "
        "손길이 닿지 않은 영혼 조합을 갖추기 전까지는 용병마다 대체재가 있어야 한다. 이 가이드가 "
        "초반 주력 용병으로 칼날 매복자를 쓰는 이유도 그것이다 — 방치에서 파밍되는 기록관의 도구 "
        "허리띠, 그리고 전역 드롭 T3 고유 무기인 불커누스라는 아주 강한 대체재가 있다.",
        "존댓말 + 'Arkhon's Tools' 미번역",
    ),
    Retranslation(
        "A: No. A rare 5% life-on-block Shaper shield is actually better once you cap block via "
        "Versatile Combatant. That's a 750 life per block on a 15k life character.",
        "A: 아니다. 유연한 전투원으로 막기를 최대치까지 올리고 나면 '막기 시 생명력 5% 회복' 이 "
        "붙은 희귀 쉐이퍼 방패가 오히려 낫다. 생명력 15,000 캐릭터 기준 막기 한 번에 생명력 750 이다.",
        "존댓말 + Versatile Combatant 를 '다재다능한 전투가' 로 지어냈다 (공식 = 유연한 전투원)",
    ),
    Retranslation(
        "A: The cap on Enmity's is local. There is no global cap for Elemental pen. Of course there "
        "is Diminishing Return, you can always craft Inc Fire damage/Ignite instead.",
        "A: 원한의 품에 적힌 상한은 그 아이템 안에서만 적용되는 로컬 상한이다. 원소 저항 관통 "
        "자체에는 전역 상한이 없다. 물론 수확 체감은 있으니 대신 화염 피해 증가나 점화를 제작해도 된다.",
        "문체 불일치 — 이 문단만 존댓말",
    ),
    Retranslation(
        "Why you care so much about “Hit cannot be evaded”. I never seen any of the build in trade "
        "focusing on accuracy?",
        "Q: 왜 '무조건 명중' 을 그렇게 중요하게 보나? 거래 리그 빌드에서 정확도에 신경 쓰는 걸 본 "
        "적이 없는데?",
        "문체 불일치 — 이 문단만 존댓말",
    ),
    Retranslation(
        "A: Mercs do need accuracy. If you take a look at any Marauder melee merc, almost every single "
        "one of them has Resolute Technique in their profile stats. That is a hint showing that they "
        "do need accuracy. You can compensate with T1/T2 accuracy on helmet, gloves and abyss jewels "
        "for your merc. But early on in the league, “Hit cannot be evaded” solves a lot of the "
        "gearing problems for attack-based mercs.",
        "A: 용병에게도 정확도가 필요하다. 머라우더 근접 용병의 프로필 능력치를 보면 거의 전부 확고한 "
        "기술을 달고 있는데, 그게 정확도가 필요하다는 증거다. 용병의 투구·장갑·심연 주얼에서 T1/T2 "
        "정확도를 채워 메울 수도 있다. 다만 리그 초반에는 '무조건 명중' 하나가 공격형 용병의 장비 "
        "문제를 대부분 해결해 준다.",
        "문체 불일치 — 이 문단만 존댓말",
    ),
    Retranslation(
        "My choices in SSF are Blade Ambusher and Combatant. Both let you craft “Hit Cannot Be "
        "Evaded” onto their weapons, solving a lot of issues early on without caring much about "
        "accuracy on helmet/abyss jewels. Also, they are from the same house - Azadi. This will let "
        "you target farm both of them more efficiently. Early game you would not have any juiced map "
        "to clear, I would recommend going with a good Blade Ambusher first to get your Voidstones. "
        "But if you cannot stand the delay playstyle of trappers, stick with a Combatant with Wild "
        "Strike/Static Strike.",
        "SSF 에서 내 선택은 칼날 매복자와 전투원이다. 둘 다 무기에 '무조건 명중' 을 제작할 수 있어서, "
        "투구나 심연 주얼의 정확도를 크게 신경 쓰지 않고도 초반 문제가 많이 풀린다. 게다가 둘 다 "
        "Azadi 가문 소속이라 함께 표적 파밍하기도 좋다. 초반에는 어차피 주스를 두른 맵을 돌 일이 "
        "없으니, 먼저 좋은 칼날 매복자를 잡아 공허석부터 확보하길 권한다. 덫 특유의 지연 플레이를 "
        "못 견디겠다면 사나운 타격 / 정전기 타격을 쓰는 전투원으로 가라.",
        "문체 불일치 — 이 문단만 존댓말",
    ),
    Retranslation(
        "Act 10. Farm your merc in Act 10 Control Blocks. Whichever merc you go with is entirely up "
        "to you. This guide will be written based on my own preference. I will stick with a good (1) "
        "Blade Ambusher first → then farm for a mapping (2) Combatant.",
        "액트 10. 액트 10 관리 구역에서 용병을 파밍한다. 어떤 용병을 고르든 전적으로 네 자유다. 이 "
        "가이드는 내 취향대로 쓴다 — 먼저 좋은 (1) 칼날 매복자를 확보하고, 그다음 맵용 (2) 전투원을 "
        "파밍한다.",
        "존댓말 + 맨 앞 'Act 10.' 이 통째로 빠졌다",
    ),
    Retranslation(
        "LINK: 2L Flame Link + Empower Support (no more More Duration Support needed due to Oath of "
        "Fealty ascendancy).",
        "연결: 2링크 화염의 연결 + 강화 보조 (충성 서약 전직 덕분에 지속시간 증폭 보조는 더 이상 "
        "필요 없다).",
        "존댓말 + More Duration Support = 지속시간 증폭 보조(증가 아님)",
    ),
    Retranslation(
        "2L Stormblast Mine + Minefield Support: 3% increased damage taken per mine, caps at 150 - "
        "forget the cap, without much throw-speed investment ~10 mines is realistically achievable, "
        "which is still a ~30% more DPS increase.",
        "2링크 태풍 파열 지뢰 + 지뢰밭 보조: 지뢰 하나당 받는 피해 3% 증가, 상한은 150 이다 — 상한은 "
        "잊어라. 투척 속도에 크게 투자하지 않아도 현실적으로 10개쯤은 깔리고, 그것만으로 DPS 가 약 "
        "30% 증폭된다.",
        "존댓말 + 'forget the cap' 이 빠지고 more/increased 구분이 사라졌다",
    ),
    Retranslation(
        "We can Flame Link our AGoS to abuse the late-game Hallowed Monarch with its built-in mod - "
        "“Link skills can target damageable minions”. Note that you will NOT need “Link skills link "
        "to 1 additional random target” from Link mastery.",
        "후반에 거룩한 국왕을 쓰면 내장 속성 '연결 스킬이 피해를 받을 수 있는 소환수를 대상으로 지정 "
        "가능' 덕분에 AGoS 에도 화염의 연결을 걸 수 있다. 연결 숙련의 '연결 스킬이 무작위 대상 "
        "1명에게 추가로 연결' 은 필요 없다는 걸 기억해라.",
        "문체 불일치 — 이 문단만 존댓말",
    ),
    Retranslation(
        "Ritual - The King in the Mists - already covered in 5.2. Second Atlas Tree.",
        ("의식 — 연무 속의 왕 — 이미 ", "에서 다뤘다."),
        "문체 불일치 — 이 문단만 존댓말",
        link_label="5.2. 두 번째 아틀라스 패시브 트리",
    ),

    # Q 문단 두 자리가 '~하나요?' 로 남았다. 같은 FAQ 의 다른 Q 는 전부 해라체다.
    Retranslation(
        "Q: I do not have enough luck farming an Enmity's Embrace for my merc, thoughts?",
        "Q: 용병 줄 원한의 품이 도무지 안 나온다. 어떻게 봐야 하나?",
        "문체 불일치 — 같은 FAQ 안에서 이 Q 만 '~하나요?'",
    ),
    Retranslation(
        "Q: Why do you craft Fire/Elemental penetration in your weapons when there is a hard cap in "
        "Enmity's Embrace?",
        "Q: 원한의 품에 상한이 박혀 있는데 왜 무기에 화염 / 원소 저항 관통을 제작하나?",
        "문체 불일치 — 같은 FAQ 안에서 이 Q 만 '~하나요?'",
    ),

)


def retranslation_index(
    table: tuple[Retranslation, ...] = RETRANSLATIONS,
) -> dict[str, Retranslation]:
    """정규화된 영문 → 재번역. 키 충돌은 조용히 덮어쓰지 않고 즉시 터뜨린다."""
    index: dict[str, Retranslation] = {}
    for entry in table:
        key = normalize_english(entry.english)
        if key in index:
            raise ValueError(f"재번역 키 중복: {key!r}")
        index[key] = entry
    return index
