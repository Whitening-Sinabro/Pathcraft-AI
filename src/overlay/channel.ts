/**
 * 오버레이 창 ↔ 메인 창 동기 채널 (Tauri 이벤트 래퍼).
 *
 * 메인: coaching 변경 시 `snapshot` emit.
 * 오버레이: mount 시 `request` emit → 메인이 현재 스냅샷 즉시 재전송.
 */
import { emit, listen, type UnlistenFn } from "@tauri-apps/api/event";
import type { CoachResult, NormalizationTraceEntry } from "../types";

export const EVT_SNAPSHOT = "pathcraftai://overlay/snapshot";
export const EVT_REQUEST  = "pathcraftai://overlay/request";

/** 오버레이 창에서 보여줄 최소 슬라이스. 전체 coaching 전송은 과함. */
export interface OverlaySnapshot {
  buildKey: string;
  buildName: string;
  tier: string;
  levelingGuide: CoachResult["leveling_guide"];
  /** 추천 스킬명 + 젬 링크 진행(Lv 1-12: Cleave - Bleed Chance - Ruthless ...). 없으면 undefined */
  levelingSkills?: {
    damage_type: string;
    recommended_name: string;
    links_progression: CoachResult["leveling_skills"]["recommended"]["links_progression"];
  };
  skillTransitions: CoachResult["leveling_skills"]["skill_transitions"];
  mapDeadly: string[];
  dangerZones: string[];
  validationWarnings?: string[];
  normalizationTrace?: NormalizationTraceEntry[];
  ts: number; // 디버깅용 타임스탬프
}

export async function sendSnapshot(snap: OverlaySnapshot): Promise<void> {
  await emit(EVT_SNAPSHOT, snap);
}

/** 메인: 오버레이 준비 신호 수신. 즉시 스냅샷 재전송 용. */
export function onOverlayRequest(handler: () => void): Promise<UnlistenFn> {
  return listen<void>(EVT_REQUEST, () => handler());
}

/** 오버레이: 스냅샷 수신. */
export function onSnapshot(handler: (snap: OverlaySnapshot) => void): Promise<UnlistenFn> {
  return listen<OverlaySnapshot>(EVT_SNAPSHOT, (e) => handler(e.payload));
}

/** 오버레이: mount 시 메인에 현재 스냅샷 재전송 요청. */
export async function requestSnapshot(): Promise<void> {
  await emit(EVT_REQUEST);
}

/** coaching → snapshot 변환 (메인 측 헬퍼). */
export function buildSnapshot(params: {
  buildKey: string;
  buildName: string;
  coaching: CoachResult;
}): OverlaySnapshot {
  const { buildKey, buildName, coaching } = params;
  const rec = coaching.leveling_skills?.recommended;
  return {
    buildKey,
    buildName,
    tier: coaching.tier,
    levelingGuide: coaching.leveling_guide,
    levelingSkills: rec ? {
      damage_type: coaching.leveling_skills?.damage_type ?? "",
      recommended_name: rec.name,
      links_progression: rec.links_progression ?? [],
    } : undefined,
    skillTransitions: coaching.leveling_skills?.skill_transitions ?? [],
    mapDeadly: coaching.map_mod_warnings?.deadly ?? [],
    dangerZones: coaching.danger_zones ?? [],
    validationWarnings: coaching._validation_warnings,
    normalizationTrace: coaching._normalization_trace,
    ts: Date.now(),
  };
}
