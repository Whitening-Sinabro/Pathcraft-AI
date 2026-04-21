import type { CoachResult, NormalizationTraceEntry } from "../types";

/** L4 terminal block — normalizer가 allowlist 밖 젬을 drop 했으면 결과를 신뢰할 수 없음.
 *
 * 판정 기준: `_normalization_trace` 에 `match_type === "dropped"` 엔트리가 하나라도 있음.
 * L2가 drop한 젬은 LLM이 존재하지 않는 이름을 추천한 증거. 반쪽 결과를 UI에 띄우느니
 * 차단하고 재분석 유도하는 쪽이 안전.
 */
export function isCoachBlocked(coaching: CoachResult | null | undefined): boolean {
  if (!coaching) return false;
  const trace = coaching._normalization_trace;
  if (!trace || trace.length === 0) return false;
  return trace.some((t) => t.match_type === "dropped");
}

interface Props {
  droppedEntries: NormalizationTraceEntry[];
  onReanalyze: () => void;
  analyzing: boolean;
}

export function CoachBlockedBanner({ droppedEntries, onReanalyze, analyzing }: Props) {
  return (
    <div className="coach-blocked-overlay" role="alertdialog" aria-modal="true">
      <div className="coach-blocked-modal">
        <div className="coach-blocked__title">
          ⛔ 코치 출력 검증 실패
        </div>
        <p className="coach-blocked__lead">
          LLM이 존재하지 않는 젬 <strong>{droppedEntries.length}개</strong>를 추천해서
          결과 전체를 차단했습니다. 재시도(L3)까지 실패한 상태입니다.
        </p>
        <ul className="coach-blocked__list">
          {droppedEntries.map((t, i) => (
            <li key={i}>
              <code>{t.from}</code>
              <span className="coach-blocked__field">({t.field})</span>
            </li>
          ))}
        </ul>
        <div className="coach-blocked__actions">
          <button
            type="button"
            className="ui-button ui-button--primary coach-blocked__btn"
            onClick={onReanalyze}
            disabled={analyzing}
          >
            {analyzing ? "재분석 중..." : "재분석"}
          </button>
        </div>
        <p className="coach-blocked__note">
          반복되면 alias 맵(`data/gem_aliases.json`) 또는 valid_gems 업데이트 필요.
        </p>
      </div>
    </div>
  );
}
