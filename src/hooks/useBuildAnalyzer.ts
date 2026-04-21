import { useCallback, useEffect, useRef, useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import type { BuildData, CoachResult } from "../types";
import { logger } from "../utils/logger";
import { useBuildHistory, type SavedBuild } from "./useBuildHistory";

// 간단 hash (POB raw JSON → 32-bit int) — coach 캐시 키 생성용
function hashString(s: string): string {
  let h = 0;
  for (let i = 0; i < s.length; i++) {
    h = ((h << 5) - h + s.charCodeAt(i)) | 0;
  }
  return h.toString(36);
}

/** 코치 캐시 스키마 버전 — SYSTEM_PROMPT/validator 변경 시 bump.
 * v1 → v2: POE1 제약 + support 젬 화이트리스트 + validator 젬 검증 추가 (2026-04-20)
 * 기존 `pathcraftai_coach_<hash>` 엔트리는 prefix 불일치로 자동 무시됨. */
const COACH_CACHE_VERSION = "v2";

export interface SyndicateRec {
  layout_id: string;
  reason: string;
}

/** 리그 플레이 모드 — 필터/Syndicate 프리셋 필터링에 공유. 기본 SC(트레이드). */
export type LeagueMode = "sc" | "ssf" | "hcssf";
export const LEAGUE_MODES: LeagueMode[] = ["sc", "ssf", "hcssf"];
export const LEAGUE_MODE_LABEL: Record<LeagueMode, string> = {
  sc: "SC (Trade)",
  ssf: "SSF",
  hcssf: "HCSSF",
};

/** 코치 모델 선택 — 속도 vs 디테일 축. 기본 Haiku(빠름). */
export type CoachModel =
  | "claude-haiku-4-5-20251001"
  | "claude-sonnet-4-6"
  | "claude-opus-4-7";
export const COACH_MODEL_STORAGE_KEY = "pathcraftai_coach_model";
export const COACH_MODEL_LABEL: Record<CoachModel, string> = {
  "claude-haiku-4-5-20251001": "빠름",
  "claude-sonnet-4-6": "느리지만 디테일",
  "claude-opus-4-7": "심층 분석",
};

export function useBuildAnalyzer() {
  const { history, latest, addOrUpdate, remove: removeFromHistory, getById } = useBuildHistory();

  // 새로고침 복원: 최신 빌드가 있으면 rawJson에서 즉시 파싱 (parse_pob/coach 호출 없이).
  const initial = latest;
  function parseOrNull<T>(raw?: string): T | null {
    if (!raw) return null;
    try { return JSON.parse(raw) as T; } catch { return null; }
  }

  const [pobLink, setPobLink] = useState(initial?.pobLink ?? "");
  const [buildData, setBuildData] = useState<BuildData | null>(() => parseOrNull<BuildData>(initial?.rawBuildJson));
  const [coaching, setCoaching] = useState<CoachResult | null>(() => parseOrNull<CoachResult>(initial?.rawCoachJson));
  const [rawBuildJson, setRawBuildJson] = useState(initial?.rawBuildJson ?? "");
  const [rawCoachJson, setRawCoachJson] = useState(initial?.rawCoachJson ?? "");
  const [loading, setLoading] = useState("");
  const [error, setError] = useState("");

  // Multi-POB 확장 — 보조 빌드 링크 (필터 생성 시 union/stage 자동 분기)
  const [extraPobLinks, setExtraPobLinks] = useState<string[]>(initial?.extraPobLinks ?? []);
  const [extraBuildJsons, setExtraBuildJsons] = useState<string[]>(initial?.extraBuildJsons ?? []);
  // Stage 모드 기본 ON — 2+ POB 시 Lv 차이로 레벨링/엔드게임 자동 분기
  const [stageMode, setStageMode] = useState(initial?.stageMode ?? true);
  // 2-POB 전환 AL (기본 67 = Kitava 후). 사용자가 실제 전환 시점에 맞게 조절 가능.
  const [alSplit, setAlSplit] = useState(initial?.alSplit ?? 67);

  // Syndicate 레이아웃 AI 추천 (휴리스틱, <1초) — 런타임 파생이라 영속 대상 아님
  const [syndicateRec, setSyndicateRec] = useState<SyndicateRec | null>(null);

  // 리그 플레이 모드 — FilterPanel + SyndicateBoard 공유. 기본 SC(트레이드).
  // FilterPanel.mode + Syndicate 프리셋 필터 단일 진실원.
  const [mode, setMode] = useState<LeagueMode>(initial?.mode ?? "sc");

  // 코치 모델 — 비용 민감도 높은 dev 환경이라 기본 Haiku. localStorage 지속.
  const [coachModel, setCoachModelState] = useState<CoachModel>(() => {
    try {
      const saved = localStorage.getItem(COACH_MODEL_STORAGE_KEY);
      if (
        saved === "claude-haiku-4-5-20251001" ||
        saved === "claude-sonnet-4-6" ||
        saved === "claude-opus-4-7"
      ) return saved;
    } catch { /* ignore */ }
    return "claude-haiku-4-5-20251001";
  });
  const setCoachModel = (m: CoachModel) => {
    setCoachModelState(m);
    try { localStorage.setItem(COACH_MODEL_STORAGE_KEY, m); } catch { /* quota */ }
  };

  // race-condition 가드: 진행 중 호출에 대해 unmount 또는 새 호출 시 setState 차단
  // (Tauri invoke는 AbortSignal 미지원, sentinel flag로 대신)
  const runIdRef = useRef(0);
  useEffect(() => () => { runIdRef.current = -1; }, []);

  /** 분석 성공 끝단에서 히스토리에 add/update — 캐시 hit / fresh coach 경로 공통. */
  const saveToHistory = useCallback((
    parsed: BuildData,
    parsedCoach: CoachResult,
    rawBuild: string,
    rawCoach: string,
    parsedExtras: string[],
  ) => {
    const trimmed = pobLink.trim();
    if (!trimmed) return;
    addOrUpdate({
      pobLink: trimmed,
      buildName: parsed.meta?.build_name || "이름 없는 빌드",
      tier: parsedCoach.tier || "-",
      rawBuildJson: rawBuild,
      rawCoachJson: rawCoach,
      extraPobLinks: extraPobLinks.map((l) => l.trim()).filter(Boolean),
      extraBuildJsons: parsedExtras,
      mode,
      stageMode,
      alSplit,
      coachModel,
    });
  }, [pobLink, extraPobLinks, mode, stageMode, alSplit, coachModel, addOrUpdate]);

  /** 히스토리에서 저장된 빌드 선택 → state 전체 복원 (API 호출 없음). */
  const selectBuild = useCallback((id: string) => {
    const b: SavedBuild | null = getById(id);
    if (!b) return;
    runIdRef.current++; // 진행 중 분석이 있다면 결과 폐기
    setPobLink(b.pobLink);
    setRawBuildJson(b.rawBuildJson);
    setRawCoachJson(b.rawCoachJson);
    try { setBuildData(JSON.parse(b.rawBuildJson) as BuildData); } catch { setBuildData(null); }
    try { setCoaching(JSON.parse(b.rawCoachJson) as CoachResult); } catch { setCoaching(null); }
    setExtraPobLinks(b.extraPobLinks);
    setExtraBuildJsons(b.extraBuildJsons);
    setMode(b.mode);
    setStageMode(b.stageMode);
    setAlSplit(b.alSplit);
    setCoachModel(b.coachModel);
    setError("");
    setLoading("");
    addOrUpdate({
      pobLink: b.pobLink,
      buildName: b.buildName,
      tier: b.tier,
      rawBuildJson: b.rawBuildJson,
      rawCoachJson: b.rawCoachJson,
      extraPobLinks: b.extraPobLinks,
      extraBuildJsons: b.extraBuildJsons,
      mode: b.mode,
      stageMode: b.stageMode,
      alSplit: b.alSplit,
      coachModel: b.coachModel,
    });
  }, [getById, addOrUpdate]);

  async function analyzeBuild() {
    const runId = ++runIdRef.current;
    const isStale = () => runIdRef.current !== runId;

    setError("");
    setBuildData(null);
    setCoaching(null);
    setRawBuildJson("");
    setRawCoachJson("");
    setExtraBuildJsons([]);

    const trimmed = pobLink.trim();
    if (!trimmed) return;

    try {
      setLoading("1번 POB 파싱 중...");
      const raw = await invoke<string>("parse_pob", { link: trimmed });
      if (isStale()) return;
      const parsed: BuildData = JSON.parse(raw);
      setBuildData(parsed);
      setRawBuildJson(raw);

      // 보조 POB 자동 파싱 (있으면, 병렬)
      const extras = extraPobLinks.map((l) => l.trim()).filter(Boolean);
      let parsedExtras: string[] = [];
      if (extras.length > 0) {
        setLoading(`2단계 POB ${extras.length}개 병렬 파싱 중...`);
        parsedExtras = await Promise.all(
          extras.map((link) => invoke<string>("parse_pob", { link }))
        );
        if (isStale()) return;
        setExtraBuildJsons(parsedExtras);
      }

      // AI 코치에 4-stage 전체 progression 전달 — 1단계 + 2단계 POB의 skills/gears를 함께 보게 함
      const coachInput = JSON.stringify({
        ...parsed,
        __extra_builds__: parsedExtras.map((j) => JSON.parse(j)),
      });

      // Coach 캐시 — 전체 입력(extras 포함) hash + 스키마 버전 키.
      // 모델 선택도 키에 포함 (Haiku/Sonnet/Opus 결과 분리 캐시).
      const cacheKey = `pathcraftai_coach_${COACH_CACHE_VERSION}_${coachModel}_${hashString(coachInput)}`;
      const cached = localStorage.getItem(cacheKey);
      if (cached) {
        setLoading("캐시 적중 — 이전 분석 결과 로드 중...");
        try {
          if (isStale()) return;
          const cachedCoach: CoachResult = JSON.parse(cached);
          setCoaching(cachedCoach);
          setRawCoachJson(cached);
          saveToHistory(parsed, cachedCoach, raw, cached, parsedExtras);
          setLoading("");
          return;
        } catch {
          // 캐시 파싱 실패 시 새로 요청
        }
      }

      // POB 개수별 예상 시간 (경험적 수치)
      const totalPobs = parsedExtras.length + 1;
      const estMin = 20 + totalPobs * 15;  // 1 POB=35s, 2=50s, 3=65s, 4=80s
      const estMax = 40 + totalPobs * 25;
      setLoading(
        `AI 코치 분석 중 (POB ${totalPobs}개 통합) — 예상 ${estMin}~${estMax}초. ` +
        `POB가 많을수록 컨텍스트가 커져 오래 걸립니다. 창 닫지 말고 대기하세요.`
      );
      const coachStartTs = Date.now();
      const coachRaw = await invoke<string>("coach_build", {
        buildJson: coachInput,
        model: coachModel,
      });
      if (isStale()) return;
      const coachSec = Math.round((Date.now() - coachStartTs) / 1000);
      logger.info(`[coach] ${totalPobs} POB(s) completed in ${coachSec}s`);
      const parsedCoach: CoachResult = JSON.parse(coachRaw);
      setCoaching(parsedCoach);
      setRawCoachJson(coachRaw);
      try {
        localStorage.setItem(cacheKey, coachRaw);
      } catch { /* quota, ignore */ }
      saveToHistory(parsed, parsedCoach, raw, coachRaw, parsedExtras);

      // Syndicate 레이아웃 추천 (휴리스틱, <1초)
      try {
        const synRaw = await invoke<string>("syndicate_recommend", { buildJson: raw });
        if (isStale()) return;
        const synParsed = JSON.parse(synRaw);
        if (synParsed.layout_id) {
          setSyndicateRec({ layout_id: synParsed.layout_id, reason: synParsed.reason });
        }
      } catch { /* Syndicate 추천 실패는 무시 (선택 기능) */ }

      setLoading("");
    } catch (e) {
      if (isStale()) return;
      setError(String(e));
      setLoading("");
    }
  }

  /** 코치 분석 정지 — Rust subprocess 킬 + 프론트 runId 뒤엎어 결과 폐기 */
  async function cancelAnalyze() {
    runIdRef.current++;  // isStale() → true, 진행 중 호출 결과 버림
    setLoading("");
    try {
      await invoke<boolean>("cancel_coach");
    } catch (e) {
      logger.warn("[cancelAnalyze] cancel_coach 실패:", e);
    }
  }

  return {
    pobLink, setPobLink,
    buildData,
    coaching,
    rawBuildJson,
    rawCoachJson,
    loading,
    error,
    extraPobLinks, setExtraPobLinks,
    extraBuildJsons,
    stageMode, setStageMode,
    alSplit, setAlSplit,
    syndicateRec,
    analyzeBuild,
    cancelAnalyze,
    mode, setMode,
    coachModel, setCoachModel,
    // 빌드 히스토리 Phase A
    history,
    selectBuild,
    removeBuild: removeFromHistory,
  };
}
