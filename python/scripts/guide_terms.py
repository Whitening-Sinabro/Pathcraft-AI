# -*- coding: utf-8 -*-
"""게임 용어 오역 치환 규칙표.

규칙 하나 = (틀린 표현, 바른 표현, 영문 근거, 사유). **같은 문단의 영문에 근거가
걸릴 때만** 치환한다. 이 근거 조건이 이 도구의 안전장치 전부다 — `손상` 하나가
corrupt(타락)와 damage(피해) 양쪽에서 나오므로, 근거 없이 고치면 반드시 절반이 틀린다.

적용 순서가 의미를 가진다. 긴 표현을 먼저 둬야 짧은 규칙이 그 안을 잘라먹지 않는다.

문장이 아니라 단어만 다룬다. 어순이 무너진 문단은 `guide_retranslations` 가 맡는다.
"""

from __future__ import annotations

from typing import NamedTuple


class Rule(NamedTuple):
    """(틀린 표현 → 바른 표현), 단 같은 문단 영문이 `evidence` 에 걸릴 때만 적용."""

    wrong: str
    right: str
    evidence: str
    reason: str


# 적용 순서가 의미를 가진다 — 긴 표현을 먼저 둬야 짧은 규칙이 그 안을 잘라먹지 않는다.
RULES: tuple[Rule, ...] = (
    # --- 저항(resistance) ---
    Rule("All Elemental 해상도", "모든 원소 저항", r"All Elemental res", "미번역 + res 오역"),
    Rule("All Elemental Res", "모든 원소 저항", r"All Elemental Res", "미번역"),
    Rule("입술 문신", "저항 문신", r"res tattoo", "res 를 '입술'로 오역"),
    Rule("화염 입술", "화염 저항", r"[Ff]ire res", "res 를 '입술'로 오역"),
    Rule("화염 res", "화염 저항", r"[Ff]ire res", "res 미번역"),
    Rule("해상도", "저항", r"\bres\b|\bRes\b|resist", "resistance 를 '해상도'로 오역"),

    # --- 생명력(Life) / 막기(Block) ---
    Rule("블록당 750 라이프", "막기당 생명력 750", r"750 life", "Life 음차"),
    Rule("블록에서 % 생명력 회복", "막기 시 생명력 % 회복", r"Life on Block", "Block 음차"),
    Rule("블록 수명", "막기 시 생명력", r"life-on-block", "life-on-block 오역"),
    Rule("블록을 제한하면", "막기를 최대치로 올리면", r"cap block", "cap block 오역"),
    Rule("블록도 없고", "막기도 없고", r"[Nn]o block", "Block 음차"),
    Rule("Block Chance", "막기 확률", r"Block Chance", "미번역"),
    Rule("라이프 캐릭터", "생명력 캐릭터", r"life character", "Life 음차"),
    Rule("수명", "생명력", r"\bLife\b|\blife\b", "Life 를 '수명'으로 오역"),

    # --- 재조합(Recombinator) ---
    Rule("재결합", "재조합", r"recomb", "Recombinator 는 '재조합'"),

    # --- 분열(Fractured) ---
    # 공식 한국어에서 균열 = Breach 다. Fractured 를 '균열'로 옮기면 두 메커니즘이 겹친다.
    Rule("골절", "분열", r"[Ff]racture", "Fracture 오역. Fractured=분열, 균열은 Breach"),

    # --- 타락(Corrupted) vs 피해(Damage) — 둘 다 '손상'으로 뭉개져 있었다 ---
    Rule("이중으로 손상된 고유 아이템", "이중 타락 고유 아이템", r"[Dd]ouble corrupt", "corrupt 를 '손상'으로 오역"),
    Rule("손상된 카옴의 심장", "타락한 카옴의 심장", r"corrupted Kaom", "corrupted 를 '손상'으로 오역"),
    Rule("이중 손상됨", "이중 타락", r"[Dd]ouble corrupt", "corrupt 를 '손상'으로 오역"),
    Rule("좋은 손상이", "좋은 타락이", r"corruption", "corruption 을 '손상'으로 오역"),
    Rule("AOE 손상", "AOE 피해", r"AOE damage", "damage 를 '손상'으로 오역"),
    Rule("데미지", "피해", r"damage", "damage 음차"),

    # --- 엑잘트 슬램(Exalt slam) / 제작(craft) ---
    Rule("보트 승영 강타", "보트 엑잘트 슬램", r"Exalt Slam|Exalt slam", "Exalt 를 '승영'으로 오역"),
    Rule("보트 승영 슬램", "보트 엑잘트 슬램", r"Exalt slam|Exalt Slam", "Exalt 를 '승영'으로 오역"),
    Rule("보트 승강 슬램", "보트 엑잘트 슬램", r"Exalt slam|Exalt Slam", "Exalt 를 '승강'으로 오역"),
    Rule("보트 승강 강타", "보트 엑잘트 슬램", r"Exalt Slam|Exalt slam", "Exalt 를 '승강'으로 오역"),
    Rule("Ducat 공예", "Ducat 제작", r"Ducat craft", "craft 를 '공예'로 오역"),
    Rule("보트 공예", "보트 제작", r"[Bb]oat craft", "craft 표기가 갈림"),
    Rule("공예를 사용", "제작을 사용", r"craft", "craft 를 '공예'로 오역"),

    # --- 기타 게임 어휘 ---
    Rule("강도 문신", "힘 문신", r"Strength tattoo", "Strength 를 '강도'로 오역"),
    Rule("전쟁도 없습니다", "전투의 함성도 없습니다", r"warcr", "warcries 를 '전쟁'으로 오역"),
    Rule("나무를 구부리는 방법", "트리를 어떻게 배분하는지", r"flex your tree", "tree 를 '나무'로 오역"),
    Rule("다목적 Combatant", "유연한 전투원", r"Versatile Combatant",
         "Versatile Combatant = 유연한 전투원 (레포 poe_translations). '다재다능한 전투가' 는 지어낸 말이었다"),
    Rule("무형성", "비실체화", r"ntangib", "intangibility 직역"),
    Rule("무형", "비실체화", r"ntangib", "intangibility 직역"),

    # --- 배신(Betrayal) 배치 지시 ---
    # 이 문서에서 가장 실행에 직결되는 정보 = "누구를 어느 부서에 넣느냐" 인데 전부 영문이었다.
    # 멤버 한국어명은 레포 번역 데이터의 공식 문자열("X's Veiled" → "X의 장막의")에서 얻었다.
    # 음차를 지어내지 않았다 — Guff=거프, Jorgin=요르긴, Vagan=베이건, It That Fled=달아난 그것.
    # 부서명은 영문을 괄호로 남긴다. 인게임 언어가 무엇이든 보드에서 찾을 수 있어야 한다.
    Rule("수송 또는 개입을 위해 도망친 것",
         "달아난 그것(It That Fled) → 운송(Transportation) 또는 개입(Intervention) 부서",
         r"It That Fled to Transport", "멤버명 'It That Fled' 를 문장으로 오역"),
    Rule("Riker에서 Research OR Forti OR Transport로",
         "라이커(Riker) → 연구(Research) / 요새(Fortification) / 운송(Transportation) 중 하나로",
         r"Riker to Research", "배치 지시 미번역"),
    Rule("고대 오브 30개 충돌 연구입니다",
         "고대의 오브 30개를 슬램하기 위한 연구(Research) 부서입니다",
         r"Research for 30 Ancient Orbs slamming", "slam 을 '충돌'로 오역"),
    Rule("Vorici와 It that Fled를 개입시키도록 하십시오",
         "보리치(Vorici)와 달아난 그것(It That Fled)을 개입(Intervention) 부서에 배치하세요",
         r"Vorici and It that Fled into Intervention", "부서 배치를 '개입시키다'로 오역"),
    Rule("Cameria를 운송 수단에 넣으세요",
         "카메리아(Cameria)를 운송(Transportation) 부서에 배치하세요",
         r"Cameria in Transportation", "Transportation 부서를 '운송 수단'으로 오역"),
    Rule("언덕을 어디든지 갈 수 있습니다", "힐록(Hillock) → 아무 부서에나 배치",
         r"Hillock to anywhere", "배신 멤버 Hillock 을 '언덕'으로 오역"),
    Rule("Vagan to Transportation", "베이건(Vagan) → 운송(Transportation) 부서",
         r"Vagan to Transportation", "배치 지시 미번역"),
    Rule("Gravicius to Transport", "그라비시우스(Gravicius) → 운송(Transportation) 부서",
         r"Gravicius to Transport", "배치 지시 미번역"),
    Rule("Janus to Research", "야누스(Janus) → 연구(Research) 부서",
         r"Janus to Research", "배치 지시 미번역"),
    Rule("Leo에서 Forti까지", "레오(Leo) → 요새(Fortification) 부서",
         r"Leo to Forti", "배치 지시 미번역"),
    Rule("Rin to Forti", "린(Rin) → 요새(Fortification) 부서",
         r"Rin to Forti", "배치 지시 미번역"),
    Rule("6월 찬스 100%", "준(Jun) 확률 100%", r"Jun chance", "배신 마스터 Jun 을 '6월'로 오역"),
    Rule("머: ", "용병(Merc): ", r"Merc:", "'Merc' 가 '머' 로 잘림"),

    # --- 갑충석 / 균열 ---
    # 레포 번역 데이터 확인: Scarab = 갑충석 (예: "Betrayal Scarab" → "배신 갑충석").
    # 문서 안에서 '풍뎅이' 와 '갑충석' 이 뒤섞여 있었다.
    Rule("풍뎅이", "갑충석", r"[Ss]carab", "Scarab 의 공식 한국어명은 갑충석"),
    # Breach = 균열. '위반'(violation)은 완전히 다른 뜻이다.
    Rule("위반", "균열", r"Breach", "Breach 를 '위반'으로 오역"),
    Rule("상인 라비쉬 5:1", "화려한 생명의 결실 5개를 상인에게 판매(5→1 교환)",
         r"Vendor Lavish 5 to 1", "Lavish 를 'Ravish' 로 오독한 음차"),
    Rule("41레벨 도박", "41레벨 셉터 도박", r"level 41 gambling", "닉타의 등불 요구 레벨 41 셉터 도박"),
    # === 4·6·7·8장 추가분 =======================================================
    # 표 셀에서 같은 오역이 수십 번 반복된다. 문단 재번역보다 규칙이 맞는 자리다.

    # --- 아이템 종류 ---
    Rule("방탄복", "갑옷", r"Body Armo", "Body Armour 의 공식 한국어명은 갑옷"),
    Rule("본문 방어도", "갑옷", r"Body Armour", "Body 를 '본문'으로 오역"),
    Rule("몸통 방어도", "갑옷", r"Body Armour", "표기 통일"),
    Rule("내장 내장 칼", "내장 제거용 단도", r"Gutting Kni", "Gutting Knife 공식명"),
    Rule("내장 칼", "내장 제거용 단도", r"Gutting Kni", "Gutting Knife 공식명"),
    Rule("보석 포일", "보석이 박힌 펜싱 검", r"Jewelled Foil", "Jewelled Foil 공식명"),
    Rule("시냅틱 링", "시냅스 반지", r"Synaptic Ring", "Synaptic Ring 공식명"),
    Rule("버밀리온 반지", "주색 반지", r"Vermillion [Rr]ing", "Vermillion Ring 공식명"),
    Rule("Vermillion Rings", "주색 반지", r"Vermillion Rings", "미번역"),
    Rule("쉴드", "방패", r"[Ss]hield", "Shield 음차"),

    # --- 젬 vs 주얼. 영문에서 Gem 과 Jewel 이 갈리는데 둘 다 '보석'이 됐다 ---
    Rule("스킬 보석", "스킬 젬", r"Skill Gem", "Gem 은 젬"),
    Rule("보조 보석", "보조 젬", r"Support Gem", "Gem 은 젬"),
    Rule("화염 보석", "화염 젬", r"Fire [Gg]em", "Gem 은 젬"),
    Rule("지속시간 보석", "지속시간 젬", r"Duration gem", "Gem 은 젬"),
    Rule("오라 보석", "오라 젬", r"Aura gem", "Gem 은 젬"),
    Rule("장착 보석", "장착된 젬", r"Socketed Gem", "Gem 은 젬"),
    Rule("살인적인 심연 보석", "살인적인 눈 주얼", r"Murderous", "Murderous Eye Jewel 공식명"),
    Rule("심연 보석", "심연 주얼", r"[Aa]byss [Jj]ewel", "Jewel 은 주얼"),
    Rule("독특한 보석", "고유 주얼", r"Unique Jewel", "Jewel 은 주얼"),
    # Gem 이 같은 문단에 없을 때만 — 있으면 어느 쪽 '보석'인지 규칙으로 못 가른다.
    # Jewelled Foil(보석이 박힌 펜싱 검)은 주얼이 아니라 무기 베이스라 함께 제외한다.
    Rule("보석", "주얼", r"(?s)\A(?!.*(Gem|Jewelled)).*Jewel", "Jewel 은 주얼"),

    # --- 목걸이 vs 부적. Talisman 도 '부적'이라 같은 문단에 있으면 손대지 않는다 ---
    Rule("부적", "목걸이", r"(?s)\A(?!.*Talisman).*Amulet", "Amulet 의 공식 한국어명은 목걸이"),

    # --- 막기(Block) ---
    Rule("차단할 확률 감소", "막기 확률 감소", r"chance to block", "Block 을 '차단'으로 오역"),
    Rule("차단 확률", "막기 확률", r"[Bb]lock [Cc]hance", "Block 을 '차단'으로 오역"),
    Rule("차단 기회", "막기 확률", r"Chance to Block", "Block 을 '차단'으로 오역"),
    Rule("차단 시", "막기 시", r"on [Bb]lock", "Block 을 '차단'으로 오역"),
    Rule("블록 확률", "막기 확률", r"[Bb]lock chance", "Block 음차"),
    Rule("블록의 생명력", "막기 시 생명력", r"life on block", "Block 음차"),
    Rule("블록을 제한", "막기를 최대치로", r"[Cc]ap.{0,10}block", "cap block 오역"),
    Rule("블록", "막기", r"[Bb]lock", "Block 음차"),

    # --- 상태·효과 ---
    Rule("맹공격", "맹공", r"Onslaught", "Onslaught 의 공식 한국어명은 맹공"),
    Rule("컬링", "마무리 타격", r"[Cc]ulling", "Culling Strike 는 마무리 타격"),
    Rule("고급 섬뜩한 불씨", "우수한 섬뜩한 불씨", r"Grand Eldritch Ember", "Grand 는 '우수한'"),
    Rule("발사체", "투사체", r"[Pp]rojectile", "Projectile 의 공식 한국어명은 투사체"),
    Rule("평면 회피", "고정 회피", r"Flat Evasion", "flat 을 '평면'으로 오역"),
    Rule("밋밋한 냉기", "고정 냉기 피해", r"[Ff]lat cold", "flat 을 '밋밋한'으로 오역"),
    Rule("플랫 냉기", "고정 냉기 피해", r"[Ff]lat [Cc]old", "flat 음차"),
    Rule("플랫 번개", "고정 번개 피해", r"[Ff]lat [Ll]ightning", "flat 음차"),
    Rule("내화성", "화염 저항", r"fire resistance", "fire resistance 를 '내화성'으로 오역"),

    # --- 메커니즘 이름 ---
    Rule("브리치 트리", "균열 트리", r"Breach [Tt]ree", "Breach 음차"),
    Rule("Breach 트리", "균열 트리", r"Breach [Tt]ree", "미번역"),
    Rule("Breach Tree", "균열 트리", r"Breach Tree", "미번역"),
    Rule("브리치 링", "균열 반지", r"Breach Ring", "Breach Ring 공식명"),
    Rule("Breach 링", "균열 반지", r"Breach [Rr]ing", "미번역"),
    Rule("브리치", "균열", r"Breach", "Breach 음차"),
    Rule("습격", "강탈", r"Heist", "Heist 의 공식 한국어명은 강탈"),
    Rule("강타의 수호자 기동", "징벌의 수호자 기동", r"Animate Guardian of Smiting|AGoS",
         "Animate Guardian of Smiting 공식명"),
    Rule("기름 부음", "성유", r"[Aa]noint", "Anoint 의 공식 표기는 성유"),
    Rule("기름부음", "성유", r"[Aa]noint", "Anoint 의 공식 표기는 성유"),
    Rule("타락한 정수", "타락한 에센스", r"[Cc]orrupted [Ee]ssence", "Essence 는 에센스"),
    Rule("정수", "에센스", r"[Ee]ssence", "Essence 의 공식 표기는 에센스"),
    Rule("함정", "덫", r"[Tt]rap", "Trap 의 공식 한국어명은 덫"),
    Rule("이중 부패한 방", "이중 타락 방", r"double corrupt room", "corrupt 는 타락"),
    Rule("이중 부패", "이중 타락", r"[Dd]ouble corrupt", "corrupt 는 타락"),
    Rule("부패 방", "타락 방", r"corrupt room", "corrupt 는 타락"),
    Rule("부패의 장소", "타락의 현장", r"Locus of Corruption", "Locus of Corruption"),
    Rule("부패 Locus", "타락의 현장", r"Locus of Corruption", "미번역"),

    # --- 잡다한 직역 ---
    Rule("어떤 쓰레기도 드물다", "아무 잡템 희귀 아이템", r"trash rare", "'Any trash rare' 어순 붕괴"),
    Rule("i레벨", "아이템 레벨", r"ilevel|ilvl", "ilevel 표기"),
    Rule("ilevel", "아이템 레벨", r"ilevel", "미번역"),
    Rule("ilvl", "아이템 레벨", r"ilvl", "미번역"),
    Rule("카오스 res", "카오스 저항", r"[Cc]haos res", "res 미번역"),
    Rule("Chaos res", "카오스 저항", r"Chaos res", "미번역"),
    Rule("Fire Res", "화염 저항", r"Fire Res", "미번역"),
    Rule("Fire res", "화염 저항", r"Fire res", "미번역"),
    Rule("Ele res", "원소 저항", r"Ele res", "미번역"),
    Rule("최대 res", "최대 저항", r"Max res", "res 미번역"),
    Rule("Light/냉기 res", "번개/냉기 저항", r"Light/Cold res", "Light 를 '빛'축으로 오독"),
    Rule("Life/화염 저항", "생명력/화염 저항", r"Life/Fire [Rr]es", "Life 미번역"),
    Rule("통화", "화폐", r"currenc", "currency 를 '통화'로 오역"),
    Rule("기어", "장비", r"gear", "gear 음차"),
    Rule("가슴", "갑옷", r"chest", "chest(몸통 방어구)를 '가슴'으로 직역"),
    Rule("다시 빗어보세요", "재조합하세요", r"[Rr]ecomb", "recomb 을 '빗다'로 오독"),
    Rule("다시 빗은", "재조합한", r"[Rr]ecomb", "recomb 을 '빗다'로 오독"),
    Rule("다시 결합", "재조합", r"[Rr]ecomb", "recomb 은 재조합"),

    # === 적대검증 반영: 레포 공식 표기로 문서 전체를 맞춘다 =======================
    # 아래 왼쪽 표기들은 레포 번역 데이터에 0회 등장한다(= 인게임에서 검색되지 않는다).
    # 받침이 사라지므로 조사까지 함께 바꾼다 — 안 그러면 "투구은" 이 된다.
    Rule("헬멧은", "투구는", r"[Hh]elmet", "Helmet 의 공식 한국어명은 투구"),
    Rule("헬멧이", "투구가", r"[Hh]elmet", "Helmet 의 공식 한국어명은 투구"),
    Rule("헬멧을", "투구를", r"[Hh]elmet", "Helmet 의 공식 한국어명은 투구"),
    Rule("헬멧과", "투구와", r"[Hh]elmet", "Helmet 의 공식 한국어명은 투구"),
    Rule("헬멧", "투구", r"[Hh]elmet", "Helmet 의 공식 한국어명은 투구"),
    Rule("심연 소켓", "심연 홈", r"Abyssal [Ss]ocket", "Socket 의 공식 한국어명은 홈"),
    Rule("소켓", "홈", r"[Ss]ocket", "Socket 의 공식 한국어명은 홈"),
    Rule("접두사", "접두어", r"[Pp]refix", "Prefix 의 공식 한국어명은 접두어"),
    Rule("접미사", "접미어", r"[Ss]uffix", "Suffix 의 공식 한국어명은 접미어"),
    Rule("최후통첩", "결전", r"Ultimatum", "Ultimatum 의 공식 한국어명은 결전"),
    Rule("적중 시 회피 불가’를", "무조건 명중’을", r"cannot be [Ee]vaded|Cannot Be Evaded",
         "제작 속성 'Hits can't be Evaded' 의 공식 문구는 '무조건 명중'"),
    Rule("적중 시 회피 불가’가", "무조건 명중’이", r"cannot be [Ee]vaded|Cannot Be Evaded",
         "제작 속성 'Hits can't be Evaded' 의 공식 문구는 '무조건 명중'"),
    Rule("적중 시 회피 불가", "무조건 명중", r"cannot be [Ee]vaded|Cannot Be Evaded",
         "제작 속성 'Hits can't be Evaded' 의 공식 문구는 '무조건 명중'"),
    # 근거를 'Memory of Trauma' 로 좁히면 원문이 "22 Trauma's" 처럼 줄여 쓴 자리를 놓친다.
    # 라틴 문자 뒤에는 조사가 붙지 않으므로 조사를 띄워 준다.
    Rule("고통의 기억을", "외상의 기억을", r"Trauma",
         "Memory of Trauma = 외상의 기억 (poedb.tw/kr)"),
    Rule("고통의 기억", "외상의 기억", r"Trauma",
         "Memory of Trauma = 외상의 기억 (poedb.tw/kr)"),


    # === poedb.tw/kr 회수분 =====================================================
    # 레포 번역 데이터에 없어 영문으로 두었던 이름들. 출처 명시: poedb.tw/kr.
    # 받침 유무가 바뀌므로 조사가 붙은 형태를 먼저 둔다.

    # 조사가 붙어 있는 형태 — 받침이 바뀌므로 함께 교정한다.
    Rule("Combatant를", "전투원을", r"Combatant", "Combatant = 전투원 (poedb.tw/kr)"),
    Rule("Golden Glory를", "황금의 영광을", r"Golden Glory", "poedb.tw/kr"),
    Rule("Golden Glory의", "황금의 영광의", r"Golden Glory", "poedb.tw/kr"),
    # 용병 유형
    Rule("Infamous Combatant", "Infamous 전투원", r"Infamous Combatant",
         "용병 유형 Combatant = 전투원 (poedb.tw/kr). 등급 Infamous 는 확인 불가라 유지"),
    Rule("Infamous Eruptor", "Infamous 분출자", r"Infamous Eruptor",
         "용병 유형 Eruptor = 분출자 (poedb.tw/kr)"),
    Rule("Blade Ambusher 를", "칼날 매복자를", r"Blade Ambusher", "Blade Ambusher = 칼날 매복자 (poedb.tw/kr)"),
    Rule("Blade Ambusher 와", "칼날 매복자와", r"Blade Ambusher", "Blade Ambusher = 칼날 매복자 (poedb.tw/kr)"),
    Rule("Blade Ambusher 가", "칼날 매복자가", r"Blade Ambusher", "Blade Ambusher = 칼날 매복자 (poedb.tw/kr)"),
    Rule("Blade Ambusher", "칼날 매복자", r"Blade Ambusher", "Blade Ambusher = 칼날 매복자 (poedb.tw/kr)"),
    Rule("Combatant 를", "전투원을", r"Combatant", "Combatant = 전투원 (poedb.tw/kr)"),
    Rule("Combatant 가", "전투원이", r"Combatant", "Combatant = 전투원 (poedb.tw/kr)"),
    Rule("Combatant 의", "전투원의", r"Combatant", "Combatant = 전투원 (poedb.tw/kr)"),
    Rule("Combatant 와", "전투원과", r"Combatant", "Combatant = 전투원 (poedb.tw/kr)"),
    Rule("Combatant", "전투원", r"Combatant", "Combatant = 전투원 (poedb.tw/kr)"),

    # 루미너리 전직 노드
    Rule("Golden Glory", "황금의 영광", r"Golden Glory", "poedb.tw/kr"),
    Rule("Arkhon's Tools", "기록관의 도구", r"Arkhon",
         "The Arkhon's Tools = 기록관의 도구 (레포 poe_translations)"),
    Rule("Noble Blood 를", "귀족 피를", r"Noble Blood", "조사 흡수 (poedb.tw/kr)"),
    Rule("Noble Blood", "귀족 피", r"Noble Blood", "poedb.tw/kr"),
    # '충성 서약' 은 받침으로 끝나므로 원문의 ' 를' 을 '을' 로 바꿔 받는다.
    Rule("Oath of Fealty 를", "충성 서약을", r"Oath of Fealty", "조사 흡수 (poedb.tw/kr)"),
    Rule("Oath of Fealty", "충성 서약", r"Oath of Fealty", "poedb.tw/kr"),
    # 3.29 접두어 Foulborn. 짧은 표 셀 세 자리가 재번역을 못 타고 음차로 남았다.
    Rule("파울본", "삿된", r"Foulborn", "Foulborn 의 공식 접두사는 '삿된'"),

    # 아틀라스 패시브
    Rule("Unwavering Vision 이", "변함없는 시각이", r"Unwavering Vision", "poedb.tw/kr"),
    Rule("Unwavering Vision", "변함없는 시각", r"Unwavering Vision", "poedb.tw/kr"),
    Rule("Altered Prophecy 를", "변질된 예언을", r"Altered Prophecy", "poedb.tw/kr"),
    Rule("Altered Prophecy", "변질된 예언", r"Altered Prophecy", "poedb.tw/kr"),
    Rule("'Votive Hoard' 를", "'봉헌된 비축물' 을", r"Votive Hoard", "poedb.tw/kr"),
    Rule("Votive Hoard", "봉헌된 비축물", r"Votive Hoard", "poedb.tw/kr"),

    # 아이템·화폐
    Rule("Scrying orb 가", "예지의 오브가", r"[Ss]cry", "poedb.tw/kr"),
    Rule("Scrying orb 로", "예지의 오브로", r"[Ss]cry", "poedb.tw/kr"),
    Rule("Scrying orb", "예지의 오브", r"[Ss]cry", "poedb.tw/kr"),
    Rule("휘발성 바알 오브", "폭발성 바알 오브", r"Volatile Vaal Orb", "poedb.tw/kr"),
    Rule("Croaker Talisman", "물렁이 부적", r"Croaker Talisman", "poedb.tw/kr"),
    Rule("Gargantuan Talisman", "가르강튀아 부적", r"Gargantuan Talisman", "poedb.tw/kr"),

    # 기억 — 레포엔 없고 poedb 에 있다. 앞서 '원문 유지' 로 판단한 것을 정정한다.
    Rule("Memory of Trauma 를", "외상의 기억을", r"Trauma", "Memory of Trauma = 외상의 기억 (poedb.tw/kr)"),
    Rule("Memory of Trauma", "외상의 기억", r"Trauma", "Memory of Trauma = 외상의 기억 (poedb.tw/kr)"),

    # 보스
    Rule("공포의 화신", "두려움의 화신", r"Incarnation of Fear", "poedb.tw/kr"),
    Rule("Incarnation of Fear", "두려움의 화신", r"Incarnation of Fear", "poedb.tw/kr"),
    Rule("Incarnation of Neglect", "방치의 화신", r"Incarnation of Neglect", "poedb.tw/kr"),
    Rule("Incarnation of Dread", "불안의 화신", r"Incarnation of Dread", "poedb.tw/kr"),
    Rule("안개 속의 왕", "연무 속의 왕", r"King in the Mists", "poedb.tw/kr"),

    # 스킬
    Rule("Frost Blink", "서리점멸", r"Frost Blink", "poedb.tw/kr"),

    # 지역
    Rule("Kingsmarch 에서", "킹스마치에서", r"Kingsmarch", "poedb.tw/kr"),
    Rule("Kingsmarch", "킹스마치", r"Kingsmarch", "poedb.tw/kr"),
    Rule("Control Blocks 에서", "관리 구역에서", r"Control Blocks", "poedb.tw/kr"),
    Rule("Control Blocks 에", "관리 구역에", r"Control Blocks", "poedb.tw/kr"),
    Rule("Control Blocks", "관리 구역", r"Control Blocks", "poedb.tw/kr"),
    Rule("The Sceptre of God", "신의 셉터", r"Sceptre of God", "poedb.tw/kr"),
    Rule("The Grand Arena", "대 투기장", r"Grand Arena", "poedb.tw/kr"),
    Rule("The Ridge", "산등성이", r"The Ridge", "poedb.tw/kr"),
    Rule("The Hidden Underbelly", "숨겨진 취약 지점", r"Hidden Underbelly", "poedb.tw/kr"),
    Rule("Harbour Bridge", "항구 다리", r"Harbour Bridge", "poedb.tw/kr"),

)
