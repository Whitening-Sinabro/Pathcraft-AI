# -*- coding: utf-8 -*-
"""Contract audit for recommendation inputs and build compatibility."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

STYLE_ORDER = {
    "0_button": 0,
    "1_click": 1,
    "1_click_plus_movement": 2,
    "2_button": 3,
    "multi_button": 4,
}

AI_FORBIDDEN_OVERRIDES = [
    "patch_guard",
    "character_guard",
    "input_guard",
    "availability_guard",
    "budget_guard",
    "representative_build_status",
    "leveling_confidence",
]


def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def _confidence_lane(profile: dict) -> str:
    confidence = profile.get("confidence", {})
    progression = profile.get("progression", {})
    evidence = profile.get("evidence", [])

    rep_status = confidence.get("representative_build_status")
    leveling_conf = progression.get("leveling_confidence")
    source_count = int(confidence.get("source_count") or len(evidence))

    if rep_status == "confirmed" and leveling_conf in {"confirmed", "near_confirmed"} and source_count >= 2:
        return "stable"
    if rep_status in {"confirmed", "near_confirmed"} and leveling_conf != "inferred":
        return "watch"
    return "fragile"


def _guard_entry(guard: str, status: str, reason: str) -> dict:
    return {
        "guard": guard,
        "status": status,
        "reason": reason,
    }


def _build_deterministic_guards(
    profile: dict,
    user_state: dict,
    hard_blocks: list[str],
    soft_flags: list[str],
    budget_fit_ratio: float,
) -> list[dict]:
    identity = profile.get("identity", {})
    playstyle = profile.get("playstyle", {})
    availability = profile.get("availability", {})
    confidence = profile.get("confidence", {})
    progression = profile.get("progression", {})

    character = user_state.get("character_state", {})
    preferences = user_state.get("preferences", {})
    constraints = user_state.get("constraints", {})

    desired_skill = constraints.get("must_use_skill") or preferences.get("desired_main_skill")
    guards: list[dict] = []

    if "patch_mismatch" in hard_blocks:
        guards.append(_guard_entry("patch_guard", "block", "user patch and build patch do not match"))
    else:
        guards.append(_guard_entry("patch_guard", "pass", f"patch={identity.get('patch') or 'unknown'}"))

    if "character_lock_conflict" in hard_blocks:
        guards.append(_guard_entry("character_guard", "block", "locked character cannot switch class or ascendancy"))
    else:
        lock_reason = "character not locked"
        if character.get("character_locked"):
            lock_reason = "class/ascendancy compatible with locked character"
        guards.append(_guard_entry("character_guard", "pass", lock_reason))

    if desired_skill and desired_skill != identity.get("main_skill"):
        guards.append(_guard_entry("skill_guard", "proxy", "exact skill mismatch; same-class proxy only"))
    else:
        guards.append(_guard_entry("skill_guard", "pass", "exact skill matched or no hard skill lock"))

    if "input_style_conflict" in hard_blocks:
        guards.append(_guard_entry("input_guard", "block", "build input style exceeds user maximum"))
    else:
        guards.append(_guard_entry("input_guard", "pass", f"input_style={playstyle.get('input_style') or 'unknown'}"))

    if "ssf_conflict" in hard_blocks:
        guards.append(_guard_entry("availability_guard", "block", "requested SSF but build has low SSF viability"))
    else:
        guards.append(_guard_entry("availability_guard", "pass", f"ssf_viable={availability.get('ssf_viable') or 'unknown'}"))

    if "underfunded" in hard_blocks:
        guards.append(_guard_entry("budget_guard", "block", f"budget_fit_ratio={budget_fit_ratio:.2f} exceeds Plan C ceiling"))
    elif "budget_tight" in soft_flags:
        guards.append(_guard_entry("budget_guard", "soft", f"budget_fit_ratio={budget_fit_ratio:.2f} requires near-budget handling"))
    else:
        guards.append(_guard_entry("budget_guard", "pass", f"budget_fit_ratio={budget_fit_ratio:.2f}"))

    if constraints.get("require_confirmed_leveling") and progression.get("leveling_confidence") != "confirmed":
        guards.append(_guard_entry("confidence_guard", "block", "confirmed leveling was required but not available"))
    elif confidence.get("representative_build_status") == "hold":
        guards.append(_guard_entry("confidence_guard", "soft", "representative build is still hold-status"))
    else:
        guards.append(
            _guard_entry(
                "confidence_guard",
                "pass",
                f"representative={confidence.get('representative_build_status') or 'unknown'}, leveling={progression.get('leveling_confidence') or 'unknown'}",
            )
        )

    return guards


def _build_ai_policy(profile: dict, compatibility: dict) -> dict:
    hard_blocks = set(compatibility.get("hard_blocks", []))
    selected_plan = compatibility.get("selected_plan")
    lane = _confidence_lane(profile)

    if hard_blocks and hard_blocks != {"skill_mismatch"}:
        mode = "disabled"
        allowed_slots = ["rejection_reason_summary", "next_required_inputs"]
        reason = "hard deterministic conflict exists"
    elif selected_plan == "C":
        mode = "proxy_only"
        allowed_slots = ["same_class_proxy_options", "starter_phase_bridge", "respec_vs_reroll_explanation"]
        reason = "exact build is blocked but proxy path is allowed"
    elif lane == "stable":
        mode = "explain_only"
        allowed_slots = ["ranking_explanation", "upgrade_ordering", "content_tradeoff_summary"]
        reason = "deterministic recommendation is stable; AI may explain but not decide"
    elif lane == "watch":
        mode = "bounded_fill"
        allowed_slots = ["progression_summary", "upgrade_ordering", "missing_evidence_summary"]
        reason = "deterministic core passed but some structured fields remain weak"
    else:
        mode = "verification_only"
        allowed_slots = ["missing_evidence_summary", "verification_todo_list", "abstain_reason_summary"]
        reason = "confidence is fragile; AI may only surface gaps and verification tasks"

    return {
        "mode": mode,
        "reason": reason,
        "allowed_slots": allowed_slots,
        "forbidden_overrides": AI_FORBIDDEN_OVERRIDES,
    }


def _build_verification_loop(
    profile: dict,
    compatibility: dict,
    deterministic_guards: list[dict],
) -> dict:
    confidence = profile.get("confidence", {})
    progression = profile.get("progression", {})
    evidence = profile.get("evidence", [])

    hard_blocks = set(compatibility.get("hard_blocks", []))
    soft_flags = set(compatibility.get("soft_flags", []))
    selected_plan = compatibility.get("selected_plan")
    lane = _confidence_lane(profile)
    source_types = sorted({item.get("type") for item in evidence if item.get("type")})

    if hard_blocks and hard_blocks != {"skill_mismatch"}:
        loop_state = "abstain"
    elif selected_plan == "C":
        loop_state = "escalate_to_proxy"
    elif lane == "fragile":
        loop_state = "needs_verification"
    else:
        loop_state = "satisfied"

    steps = [
        {
            "step": "deterministic_guard_replay",
            "status": "failed" if hard_blocks and hard_blocks != {"skill_mismatch"} else "passed",
            "detail": [entry["guard"] for entry in deterministic_guards if entry["status"] in {"block", "proxy"}],
        },
        {
            "step": "representative_evidence_check",
            "status": "passed" if lane == "stable" else "watch" if lane == "watch" else "failed",
            "detail": {
                "representative_build_status": confidence.get("representative_build_status"),
                "source_types": source_types,
            },
        },
        {
            "step": "leveling_route_check",
            "status": "passed" if progression.get("leveling_confidence") in {"confirmed", "near_confirmed"} else "watch",
            "detail": progression.get("leveling_confidence"),
        },
        {
            "step": "budget_floor_check",
            "status": "failed" if "underfunded" in hard_blocks else "watch" if "budget_tight" in soft_flags else "passed",
            "detail": compatibility.get("budget_fit_ratio"),
        },
        {
            "step": "plan_resolution",
            "status": "passed" if selected_plan in {"A", "B"} else "watch" if selected_plan == "C" else "failed",
            "detail": selected_plan,
        },
    ]

    promotion_requirements: list[str] = []
    if confidence.get("representative_build_status") == "hold":
        promotion_requirements.append("collect a second independent evidence source before exact recommendation")
    if progression.get("leveling_confidence") == "inferred":
        promotion_requirements.append("obtain leveling transition evidence before claiming campaign certainty")
    if "budget_tight" in soft_flags or "underfunded" in hard_blocks:
        promotion_requirements.append("split starter entry package or raise budget floor")
    if "skill_mismatch" in hard_blocks:
        promotion_requirements.append("allow same-class proxy or remove exact-skill hard lock")
    if "patch_mismatch" in hard_blocks:
        promotion_requirements.append("verify patch survival before re-entering recommendation pool")

    next_actions: list[str] = []
    if selected_plan == "B":
        next_actions.append("keep exact candidate but expose only soft-relaxed differences")
    if selected_plan == "C":
        next_actions.append("route to same-class proxy or earlier starter phase")
    if selected_plan == "D":
        next_actions.append("abstain and return the smallest blocking constraint set")
    if lane in {"watch", "fragile"}:
        next_actions.append("queue evidence upgrade before promoting confidence labels")

    return {
        "confidence_lane": lane,
        "loop_state": loop_state,
        "recommended_plan": selected_plan,
        "steps": steps,
        "promotion_requirements": promotion_requirements,
        "next_actions": next_actions,
    }


def _badge(kind: str, label: str, tone: str) -> dict:
    return {
        "kind": kind,
        "label": label,
        "tone": tone,
    }


def _plan_label(plan: str | None) -> str:
    return {
        "A": "확정 추천",
        "B": "조건부 추천",
        "C": "대체 후보",
        "D": "추천 보류",
    }.get(plan or "", "판정 대기")


def _lane_label(lane: str | None) -> str:
    return {
        "stable": "신뢰도 높음",
        "watch": "관찰 필요",
        "fragile": "위험 신호",
        "unknown": "신뢰도 미기록",
    }.get(lane or "", lane or "신뢰도 미기록")


def _ai_mode_label(mode: str | None) -> str:
    return "AI 설명 전용" if (mode or "disabled") == "disabled" else "AI 보조 설명"


def _build_message_template(profile: dict, compatibility: dict) -> dict:
    hard_blocks = set(compatibility.get("hard_blocks", []))
    soft_flags = set(compatibility.get("soft_flags", []))
    selected_plan = compatibility.get("selected_plan")
    identity = profile.get("identity", {})

    if selected_plan == "A":
        return {
            "template_id": "plan_a_exact",
            "title": "바로 따라갈 수 있는 후보",
            "summary": "현재 조건을 통과한 동일 계열 후보입니다. 레벨링, 예산, 패치 위험을 같이 확인하면서 진행하면 됩니다.",
            "bullets": [
                "동일 스킬과 클래스 경로를 우선 표시합니다.",
                "레벨링과 전환 포인트를 먼저 확인합니다.",
                "AI는 진행 경로와 위험 설명만 보조합니다.",
            ],
        }

    if selected_plan == "B":
        if "hold_status" in soft_flags:
            return {
                "template_id": "plan_b_hold_exact",
                "title": "연습은 가능하지만 검증 필요",
                "summary": "빌드 방향은 유지할 수 있지만, 확정 추천으로 올리기에는 근거가 부족합니다.",
                "bullets": [
                    "같은 스킬과 클래스 경로는 유지합니다.",
                    "추가 PoB, 가이드, 최근 poe.ninja 사례가 필요합니다.",
                    "검증 전에는 고비용 전환을 미룹니다.",
                ],
            }
        if "budget_tight" in soft_flags:
            return {
                "template_id": "plan_b_budget_tight",
                "title": "예산을 먼저 맞춰야 하는 후보",
                "summary": "방향은 맞지만 현재 예산에서는 초반 체감이 나쁠 수 있습니다.",
                "bullets": [
                    "저가 스타터 구간과 최종 전환 구간을 분리합니다.",
                    "필수 장비와 링크 시점을 먼저 확인합니다.",
                    "필수 조건을 건너뛸 수 있다고 말하지 않습니다.",
                ],
            }
        if any(flag.startswith("low_") for flag in soft_flags):
            return {
                "template_id": "plan_b_soft_content_miss",
                "title": "목표 콘텐츠와 일부 맞지 않음",
                "summary": "스킬과 클래스는 유지할 수 있지만, 선택한 콘텐츠에서는 성능이나 편의성이 부족할 수 있습니다.",
                "bullets": [
                    "약한 콘텐츠 축을 명확히 표시합니다.",
                    "파밍 전략은 빌드가 강한 콘텐츠 중심으로 조정합니다.",
                    "약한 콘텐츠에서 최고 성능처럼 말하지 않습니다.",
                ],
            }
        return {
            "template_id": "plan_b_watch_exact",
            "title": "가능성은 높지만 관찰 필요",
            "summary": "기본 조건은 맞지만, 시즌 초반 데이터가 더 쌓여야 확정 추천으로 올릴 수 있습니다.",
            "bullets": [
                "관찰 후보로 표시합니다.",
                "리그 스타트와 최근 소스 확인을 요구합니다.",
                "승격 조건 없이 확정 추천으로 올리지 않습니다.",
            ],
        }

    if selected_plan == "C":
        if "skill_mismatch" in hard_blocks:
            return {
                "template_id": "plan_c_skill_proxy",
                "title": "같은 계열의 대체 경로 필요",
                "summary": "요청한 스킬 그대로는 추천하기 어렵고, 같은 클래스나 플레이 방식의 대체 후보를 봐야 합니다.",
                "bullets": [
                    "대체 후보를 원래 빌드처럼 표시하지 않습니다.",
                    "원래 스킬로 돌아갈 조건을 같이 보여줍니다.",
                    "레벨링은 안정적인 스타터를 먼저 둡니다.",
                ],
            }
        return {
            "template_id": "plan_c_proxy_bridge",
            "title": "브릿지 빌드가 필요한 상태",
            "summary": "현재 조건에서는 최종 빌드로 바로 가기 어렵습니다. 먼저 안정적인 중간 경로를 잡아야 합니다.",
            "bullets": [
                "중간 빌드를 최종 빌드와 구분합니다.",
                "막힌 조건과 전환 조건을 명확히 보여줍니다.",
                "AI가 보류 판정을 직접 추천처럼 완화하지 않습니다.",
            ],
        }

    if "patch_mismatch" in hard_blocks:
        skill_name = identity.get("main_skill") or "the requested build"
        return {
            "template_id": "plan_d_patch_block",
            "title": "패치 확인 전까지 보류",
            "summary": f"{skill_name}는 현재 패치 기준 생존성이 확인되지 않았습니다. 최신 패치와 실제 사례 확인 전까지 추천을 보류합니다.",
            "bullets": [
                "핵심 젬, 전직, 유니크 변경 여부를 확인합니다.",
                "최근 poe.ninja 분포와 실제 PoB를 대조합니다.",
                "검증 전에는 연습 후보 또는 관찰 후보로만 둡니다.",
            ],
        }
    if "underfunded" in hard_blocks:
        return {
            "template_id": "plan_d_budget_block",
            "title": "현재 예산으로는 보류",
            "summary": "현재 예산에서는 안정적으로 시작하기 어렵습니다. 더 싼 스타터나 전환형 경로가 필요합니다.",
            "bullets": [
                "필수 아이템 가격을 먼저 확인합니다.",
                "초반 스타터와 최종 빌드를 분리합니다.",
                "예산이 맞기 전에는 고비용 전환을 피합니다.",
            ],
        }
    if "in_place_proxy_conflict" in hard_blocks:
        return {
            "template_id": "plan_d_proxy_scope_block",
            "title": "대체 후보 범위를 벗어남",
            "summary": "현재 조건에서는 같은 클래스/전직 안에서 자연스럽게 이어지는 후보를 찾기 어렵습니다.",
            "bullets": [
                "같은 클래스 안의 전환 후보를 먼저 확인합니다.",
                "전직 변경이나 리롤 허용 여부가 필요합니다.",
                "조건이 풀리면 후보군을 다시 넓힙니다.",
            ],
        }
    if "character_lock_conflict" in hard_blocks:
        return {
            "template_id": "plan_d_character_lock",
            "title": "현재 캐릭터로는 맞지 않음",
            "summary": "클래스나 전직 조건이 맞지 않아 그대로 추천할 수 없습니다. 리롤 허용 여부가 필요합니다.",
            "bullets": [
                "현재 캐릭터 유지 여부를 먼저 정합니다.",
                "같은 클래스 안에서 가능한 대체 후보를 확인합니다.",
                "리롤이 가능하면 더 넓은 후보군으로 다시 봅니다.",
            ],
        }
    if "input_style_conflict" in hard_blocks:
        return {
            "template_id": "plan_d_input_block",
            "title": "조작 난도 기준 초과",
            "summary": "요청한 난도 기준을 넘습니다. 더 단순한 플레이 방식의 후보를 먼저 보는 편이 좋습니다.",
            "bullets": [
                "버튼 수와 유지해야 하는 버프를 확인합니다.",
                "초반에는 단순한 맵핑 후보를 우선합니다.",
                "익숙해진 뒤 고난도 버전으로 전환합니다.",
            ],
        }
    if "leveling_conflict" in hard_blocks:
        return {
            "template_id": "plan_d_leveling_block",
            "title": "레벨링 경로가 부족함",
            "summary": "최종 빌드 정보만으로는 시작 루트를 안전하게 만들기 어렵습니다. 레벨링 PoB나 빌더의 캠페인 루트가 필요합니다.",
            "bullets": [
                "레벨링 PoB, 액트 구간 젬, 전환 레벨을 확인합니다.",
                "최종 PoB만 있으면 연습 후보로만 취급합니다.",
                "같은 빌더의 스타터/전환 영상을 우선 확인합니다.",
            ],
        }
    return {
        "template_id": "plan_d_abstain_generic",
        "title": "아직 확정 추천 없음",
        "summary": "현재 입력만으로는 바로 추천할 후보가 없습니다. 리서치 큐에서 후보를 고르거나 추가 근거를 넣어 다시 확인해야 합니다.",
        "bullets": [
            "후보 빌드, 레벨링 경로, 예산 조건 중 빠진 항목을 채웁니다.",
            "poe.ninja와 빌더 영상에서 최근 사례를 먼저 확인합니다.",
            "검증 전에는 추천이 아니라 관찰 후보로 둡니다.",
        ],
    }


def _build_response_layers(profile: dict, compatibility: dict) -> dict:
    deterministic_guards = compatibility.get("deterministic_guards", [])
    ai_policy = compatibility.get("ai_policy", {})
    verification_loop = compatibility.get("verification_loop", {})
    selected_plan = compatibility.get("selected_plan")

    blocked_guards = [entry["guard"] for entry in deterministic_guards if entry["status"] == "block"]
    warning_guards = [entry["guard"] for entry in deterministic_guards if entry["status"] in {"soft", "proxy"}]
    confidence_lane = verification_loop.get("confidence_lane", "unknown")

    if selected_plan == "A":
        decision_state = "exact_active"
        candidate_path = "exact"
    elif selected_plan == "B":
        decision_state = "exact_with_warnings"
        candidate_path = "exact"
    elif selected_plan == "C":
        decision_state = "proxy_only"
        candidate_path = "proxy"
    else:
        decision_state = "abstain"
        candidate_path = "none"

    badges = [
        _badge("plan", _plan_label(selected_plan), {"A": "success", "B": "warning", "C": "info", "D": "danger"}.get(selected_plan, "muted")),
        _badge("lane", _lane_label(confidence_lane), {"stable": "success", "watch": "warning", "fragile": "danger"}.get(confidence_lane, "muted")),
        _badge("ai_mode", _ai_mode_label(ai_policy.get("mode", "disabled")), "muted"),
    ]
    for entry in deterministic_guards:
        if entry["status"] == "pass":
            continue
        tone = "danger" if entry["status"] == "block" else "warning" if entry["status"] == "soft" else "info"
        badges.append(_badge("guard", f"{entry['guard']}:{entry['status']}", tone))

    return {
        "decision": {
            "plan": selected_plan,
            "decision_state": decision_state,
            "candidate_path": candidate_path,
            "confidence_lane": confidence_lane,
            "blocking_guards": blocked_guards,
            "warning_guards": warning_guards,
        },
        "user_message": _build_message_template(profile, compatibility),
        "ui_panels": {
            "show_deterministic_guards": True,
            "show_ai_policy": True,
            "show_verification_loop": True,
        },
        "ai_explanation": {
            "mode": ai_policy.get("mode", "disabled"),
            "instruction": "AI는 결정론적 결과를 설명만 할 수 있으며, 선택/가드/신뢰도 라벨을 바꾸면 안 된다.",
            "allowed_slots": ai_policy.get("allowed_slots", []),
            "forbidden_overrides": ai_policy.get("forbidden_overrides", []),
        },
        "badges": badges,
    }



def audit_build_profile(profile: dict) -> dict:
    issues: list[str] = []
    warnings: list[str] = []

    playstyle = profile.get("playstyle", {})
    availability = profile.get("availability", {})
    budget = profile.get("budget_curve", {})
    progression = profile.get("progression", {})
    confidence = profile.get("confidence", {})
    evidence = profile.get("evidence", [])

    source_types = {item.get("type") for item in evidence if item.get("type")}
    input_style = playstyle.get("input_style")
    manual_buttons = playstyle.get("manual_buttons", 0)

    if input_style == "0_button" and manual_buttons > 0:
        issues.append("playstyle claims 0_button but manual_buttons is greater than 0")

    if (
        availability.get("league_start_viable") is True
        and budget.get("entry_cost_divines", 0) > 3
    ):
        warnings.append("league_start_viable is true but entry_cost_divines exceeds recommended starter range")

    if (
        availability.get("ssf_viable") == "high"
        and availability.get("mandatory_uniques")
    ):
        warnings.append("ssf_viable is high despite mandatory_uniques being present")

    if progression.get("leveling_confidence") == "confirmed" and not progression.get("transition_points"):
        issues.append("confirmed leveling requires transition_points")

    if confidence.get("representative_build_status") == "confirmed" and len(source_types) < 2:
        issues.append("confirmed representative status requires at least two distinct evidence source types")

    if confidence.get("source_count", 0) != len(evidence):
        warnings.append("confidence.source_count does not match evidence item count")

    return {
        "issues": issues,
        "warnings": warnings,
        "source_types": sorted(source_types),
    }


def audit_user_state(user_state: dict) -> dict:
    issues: list[str] = []
    warnings: list[str] = []

    character = user_state.get("character_state", {})
    currency = user_state.get("currency_state", {})
    preferences = user_state.get("preferences", {})
    constraints = user_state.get("constraints", {})

    if character.get("level", 1) < 1:
        issues.append("character level must be at least 1")

    if currency.get("liquid_divines", 0) < 0 or currency.get("liquid_chaos", 0) < 0:
        issues.append("currency values cannot be negative")

    max_input_style = preferences.get("max_input_style")
    if max_input_style not in STYLE_ORDER:
        issues.append("unknown max_input_style")

    must_use_skill = constraints.get("must_use_skill")
    forbidden = set(constraints.get("forbidden_skills", []))
    if must_use_skill and must_use_skill in forbidden:
        issues.append("must_use_skill conflicts with forbidden_skills")

    if constraints.get("forbid_reroll") and not character.get("character_locked", False):
        warnings.append("forbid_reroll is set while character_locked is false")

    return {
        "issues": issues,
        "warnings": warnings,
    }


def evaluate_compatibility(profile: dict, user_state: dict) -> dict:
    hard_blocks: list[str] = []
    soft_flags: list[str] = []
    fallback_actions: list[str] = []

    identity = profile.get("identity", {})
    playstyle = profile.get("playstyle", {})
    budget = profile.get("budget_curve", {})
    availability = profile.get("availability", {})
    progression = profile.get("progression", {})
    confidence = profile.get("confidence", {})

    character = user_state.get("character_state", {})
    currency = user_state.get("currency_state", {})
    preferences = user_state.get("preferences", {})
    constraints = user_state.get("constraints", {})

    same_class = character.get("class_name") == identity.get("class_name")
    same_asc = character.get("ascendancy") == identity.get("ascendancy")

    desired_skill = constraints.get("must_use_skill") or preferences.get("desired_main_skill")
    if desired_skill and desired_skill != identity.get("main_skill"):
        hard_blocks.append("skill_mismatch")

    if character.get("patch") and character.get("patch") != identity.get("patch"):
        hard_blocks.append("patch_mismatch")

    if character.get("character_locked"):
        if not same_class or not same_asc:
            hard_blocks.append("character_lock_conflict")
    elif "skill_mismatch" in hard_blocks and (not same_class or not same_asc):
        hard_blocks.append("in_place_proxy_conflict")

    profile_style = playstyle.get("input_style")
    max_style = preferences.get("max_input_style")
    if profile_style in STYLE_ORDER and max_style in STYLE_ORDER:
        if STYLE_ORDER[profile_style] > STYLE_ORDER[max_style]:
            hard_blocks.append("input_style_conflict")

    trade_mode = preferences.get("trade_mode")
    if trade_mode == "ssf" and availability.get("ssf_viable") == "low":
        hard_blocks.append("ssf_conflict")

    if constraints.get("require_confirmed_leveling") and progression.get("leveling_confidence") != "confirmed":
        hard_blocks.append("leveling_conflict")

    liquid_divines = float(currency.get("liquid_divines", 0))
    entry_cost = float(budget.get("entry_cost_divines", 0))
    budget_fit_ratio = 0.0 if liquid_divines <= 0 else entry_cost / liquid_divines
    if liquid_divines <= 0 and entry_cost > 0:
        budget_fit_ratio = 999.0

    if budget_fit_ratio > 1.8:
        hard_blocks.append("underfunded")
    elif budget_fit_ratio > 1.35:
        soft_flags.append("budget_tight")

    for content in preferences.get("target_contents", []):
        content_score = profile.get("suitability", {}).get(content)
        if isinstance(content_score, int) and content_score < 60:
            soft_flags.append(f"low_{content}_score")

    if confidence.get("representative_build_status") == "hold":
        soft_flags.append("hold_status")
        fallback_actions.append("prefer confirmed or near_confirmed alternatives first")

    if hard_blocks:
        if set(hard_blocks) == {"skill_mismatch"}:
            selected_plan = "C"
            fallback_actions.append("offer same-class proxy or earlier starter phase")
        else:
            selected_plan = "D"
            fallback_actions.append("do not recommend until hard constraint conflict is resolved")
    elif soft_flags:
        selected_plan = "B"
        fallback_actions.append("relax soft constraints in ranked order only")
    else:
        selected_plan = "A"

    if selected_plan == "B" and any(flag.startswith("low_") for flag in soft_flags):
        fallback_actions.append("lower minimum content score threshold before changing skill or class")

    deterministic_guards = _build_deterministic_guards(
        profile,
        user_state,
        hard_blocks,
        soft_flags,
        budget_fit_ratio,
    )

    compatibility = {
        "selected_plan": selected_plan,
        "hard_blocks": hard_blocks,
        "soft_flags": soft_flags,
        "fallback_actions": fallback_actions,
        "budget_fit_ratio": round(budget_fit_ratio, 2),
    }
    compatibility["deterministic_guards"] = deterministic_guards
    compatibility["ai_policy"] = _build_ai_policy(profile, compatibility)
    compatibility["verification_loop"] = _build_verification_loop(
        profile,
        compatibility,
        deterministic_guards,
    )
    compatibility["guardrails"] = {
        "deterministic_guards": compatibility["deterministic_guards"],
        "ai_policy": compatibility["ai_policy"],
        "verification_loop": compatibility["verification_loop"],
    }
    compatibility["response_layers"] = _build_response_layers(profile, compatibility)
    return compatibility


def build_recommendation_audit(
    profile_path: Path | None = None,
    user_state_path: Path | None = None,
) -> dict:
    profile_path = profile_path or ROOT / "data" / "build_profile.example.json"
    user_state_path = user_state_path or ROOT / "data" / "user_state.example.json"

    profile = _load_json(profile_path)
    user_state = _load_json(user_state_path)

    return {
        "dataset_kind": "poe1_recommendation_contract_audit",
        "profile_audit": audit_build_profile(profile),
        "user_state_audit": audit_user_state(user_state),
        "compatibility": evaluate_compatibility(profile, user_state),
    }


if __name__ == "__main__":
    print(json.dumps(build_recommendation_audit(), ensure_ascii=False, indent=2))
