import { useEffect, useMemo, useRef, useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import {
  computeRecommendations,
  summarizeBoardDelta,
  EMPTY_BOARD,
  type DivisionBoard,
  type Rank,
} from "../../utils/syndicateEngine";
import { logger } from "../../utils/logger";
import {
  DIVISIONS,
  type Division,
  type SyndicateMember,
  type SyndicateData,
  type SyndicateLayout,
  type LayoutData,
  type VisionResult,
} from "./types";

const STORAGE_KEY = "pathcraftai_syndicate";

interface Options {
  recommendation?: { layout_id: string; reason: string } | null;
}

export function useSyndicateBoard({ recommendation }: Options) {
  const [members, setMembers] = useState<SyndicateMember[]>([]);
  const [layouts, setLayouts] = useState<SyndicateLayout[]>([]);

  const [board, setBoard] = useState<Record<Division, string[]>>({
    Transportation: [],
    Fortification: [],
    Research: [],
    Intervention: [],
  });
  const [selectedLayoutId, setSelectedLayoutId] = useState<string>("");
  const [selectedMember, setSelectedMember] = useState<SyndicateMember | null>(null);
  const [currentBoard, setCurrentBoard] = useState<DivisionBoard>(EMPTY_BOARD);

  // 데이터 로드 (동적 import) — 실패 시 빈 배열 + 경고 로그
  useEffect(() => {
    import("../../../data/syndicate_members.json")
      .then((mod) => setMembers((mod.default as unknown as SyndicateData).members))
      .catch((e) => {
        logger.warn("[syndicate] syndicate_members.json load failed", e);
        setMembers([]);
      });
    import("../../../data/syndicate_layouts.json")
      .then((mod) => setLayouts((mod.default as unknown as LayoutData).layouts))
      .catch((e) => {
        logger.warn("[syndicate] syndicate_layouts.json load failed", e);
        setLayouts([]);
      });
  }, []);

  // localStorage 복원 — quota/corrupt 시 경고
  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (!saved) return;
      const parsed = JSON.parse(saved);
      if (parsed.board) setBoard(parsed.board);
      if (parsed.layoutId) setSelectedLayoutId(parsed.layoutId);
      if (parsed.currentBoard) setCurrentBoard(parsed.currentBoard);
    } catch (e) {
      logger.warn("[syndicate] localStorage restore failed", e);
    }
  }, []);

  // localStorage 저장 — quota 초과 시 경고 (데이터 손실 방지)
  useEffect(() => {
    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({ board, layoutId: selectedLayoutId, currentBoard }),
      );
    } catch (e) {
      logger.warn("[syndicate] localStorage save failed (quota?)", e);
    }
  }, [board, selectedLayoutId, currentBoard]);

  const memberMap = useMemo(
    () => Object.fromEntries(members.map((m) => [m.id, m])) as Record<string, SyndicateMember>,
    [members],
  );

  const recommendedLayout = useMemo(
    () => (recommendation ? layouts.find((l) => l.id === recommendation.layout_id) ?? null : null),
    [recommendation, layouts],
  );

  const targetBoard = useMemo(
    () => ({
      Transportation: board.Transportation,
      Fortification: board.Fortification,
      Research: board.Research,
      Intervention: board.Intervention,
    }),
    [board],
  );

  const recs = useMemo(
    () => (members.length > 0 ? computeRecommendations(currentBoard, targetBoard, members) : []),
    [currentBoard, targetBoard, members],
  );

  const delta = useMemo(
    () => summarizeBoardDelta(currentBoard, targetBoard),
    [currentBoard, targetBoard],
  );

  // ---- 프리셋 핸들러 ----
  function applyLayout(id: string) {
    const layout = layouts.find((l) => l.id === id);
    if (!layout) return;
    setBoard({
      Transportation: [...(layout.board.Transportation || [])],
      Fortification: [...(layout.board.Fortification || [])],
      Research: [...(layout.board.Research || [])],
      Intervention: [...(layout.board.Intervention || [])],
    });
    setSelectedLayoutId(id);
  }

  function clearBoard() {
    setBoard({ Transportation: [], Fortification: [], Research: [], Intervention: [] });
    setSelectedLayoutId("");
  }

  // ---- 현재 보드 핸들러 ----
  function addOrMoveCurrentMember(div: Division, memberId: string) {
    setCurrentBoard((prev) => {
      const next = { ...prev };
      for (const d of DIVISIONS) {
        next[d] = next[d].filter((s) => s.memberId !== memberId);
      }
      if (next[div].length >= 4) return prev;
      next[div] = [...next[div], { memberId, rank: "Member" }];
      return next;
    });
  }

  function setCurrentRank(div: Division, memberId: string, rank: Rank) {
    setCurrentBoard((prev) => ({
      ...prev,
      [div]: prev[div].map((s) => (s.memberId === memberId ? { ...s, rank } : s)),
    }));
  }

  function removeCurrentSlot(div: Division, memberId: string) {
    setCurrentBoard((prev) => ({
      ...prev,
      [div]: prev[div].filter((s) => s.memberId !== memberId),
    }));
  }

  function clearCurrentBoard() {
    setCurrentBoard(EMPTY_BOARD);
  }

  function copyTargetToCurrent() {
    const next: DivisionBoard = { ...EMPTY_BOARD };
    for (const div of DIVISIONS) {
      next[div] = board[div].map((id, i) => ({ memberId: id, rank: i === 0 ? "Leader" : "Member" }));
    }
    setCurrentBoard(next);
  }

  function promoteCurrentToTarget() {
    // Leader가 slot 0로 오도록 안정 정렬. 사용자 수동/Vision 저장 흐름.
    const nextTarget: Record<Division, string[]> = {
      Transportation: [], Fortification: [], Research: [], Intervention: [],
    };
    for (const div of DIVISIONS) {
      const sorted = [...currentBoard[div]].sort((a, b) => {
        if (a.rank === b.rank) return 0;
        return a.rank === "Leader" ? -1 : 1;
      });
      nextTarget[div] = sorted.map((s) => s.memberId);
    }
    setBoard(nextTarget);
    setSelectedLayoutId("custom");
    setCurrentBoard(EMPTY_BOARD);
  }

  // ---- Vision (스크린샷 → currentBoard) ----
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [visionLoading, setVisionLoading] = useState(false);
  const [visionStatus, setVisionStatus] = useState<{ kind: "ok" | "warn" | "err"; msg: string } | null>(null);

  // race-condition 가드 — 새 호출/unmount 시 stale 응답 차단
  const visionRunIdRef = useRef(0);
  useEffect(() => () => { visionRunIdRef.current = -1; }, []);

  async function fileToBase64(file: File | Blob): Promise<string> {
    const buffer = await file.arrayBuffer();
    let binary = "";
    const bytes = new Uint8Array(buffer);
    const chunk = 0x8000;
    for (let i = 0; i < bytes.length; i += chunk) {
      binary += String.fromCharCode(...bytes.subarray(i, i + chunk));
    }
    return btoa(binary);
  }

  async function analyzeImage(file: File | Blob) {
    const runId = ++visionRunIdRef.current;
    const isStale = () => visionRunIdRef.current !== runId;

    setVisionLoading(true);
    setVisionStatus(null);
    try {
      const b64 = await fileToBase64(file);
      if (isStale()) return;
      const raw = await invoke<string>("analyze_syndicate_image", { imageBase64: b64 });
      if (isStale()) return;
      const parsed = JSON.parse(raw) as VisionResult;
      if (parsed.error) {
        setVisionStatus({ kind: "err", msg: parsed.error });
        return;
      }
      const next: DivisionBoard = { ...EMPTY_BOARD };
      for (const div of DIVISIONS) {
        const slots = parsed.divisions[div] || [];
        next[div] = slots.map((s) => ({ memberId: s.member_id, rank: s.rank }));
      }
      setCurrentBoard(next);
      const filled = DIVISIONS.reduce((sum, d) => sum + next[d].length, 0);
      const unknownCount = parsed.diagnostics?.unknown_members?.length ?? 0;
      const conf = parsed.confidence;
      const kind = conf === "high" && unknownCount === 0 ? "ok" : "warn";
      const parts = [`${filled}명 인식 (신뢰도: ${conf})`];
      if (unknownCount > 0) parts.push(`미식별 ${unknownCount}건`);
      if (parsed.notes) parts.push(parsed.notes);
      setVisionStatus({ kind, msg: parts.join(" · ") });
    } catch (e) {
      if (isStale()) return;
      logger.error("[syndicate.vision] analyze_syndicate_image failed", e);
      setVisionStatus({ kind: "err", msg: e instanceof Error ? e.message : String(e) });
    } finally {
      if (!isStale()) setVisionLoading(false);
    }
  }

  function onFileSelected(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) void analyzeImage(file);
    e.target.value = "";
  }

  async function onPasteFromClipboard() {
    try {
      const items = await navigator.clipboard.read();
      for (const item of items) {
        const imgType = item.types.find((t) => t.startsWith("image/"));
        if (imgType) {
          const blob = await item.getType(imgType);
          await analyzeImage(blob);
          return;
        }
      }
      setVisionStatus({ kind: "err", msg: "클립보드에 이미지가 없습니다 (PrtScr 또는 캡처툴 후 다시 시도)" });
    } catch (e) {
      setVisionStatus({ kind: "err", msg: `클립보드 접근 실패: ${e instanceof Error ? e.message : String(e)}` });
    }
  }

  return {
    // data
    members, layouts, memberMap,
    // state
    board, selectedLayoutId, selectedMember, currentBoard,
    // derived
    recommendedLayout, recs, delta,
    // setters
    setSelectedMember,
    // preset handlers
    applyLayout, clearBoard,
    // current board handlers
    addOrMoveCurrentMember, setCurrentRank, removeCurrentSlot, clearCurrentBoard,
    copyTargetToCurrent, promoteCurrentToTarget,
    // vision
    fileInputRef, visionLoading, visionStatus, onFileSelected, onPasteFromClipboard,
  };
}
