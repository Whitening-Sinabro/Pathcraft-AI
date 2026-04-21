import { useState } from "react";
import type { NormalizationTraceEntry } from "../types";

interface Props {
  warnings: string[] | undefined;
  trace?: NormalizationTraceEntry[] | undefined;
  compact?: boolean;
}

/**
 * 코치 출력 품질 피드백 배지 (Phase H).
 *   - warnings: coach_validator/normalizer 의 매칭 실패 경고 (원본 유지)
 *   - trace:    coach_normalizer 가 자동 교정한 이력 (원본 → canonical)
 *
 * 양쪽 모두 없으면 렌더 안 함. 기본 접힘, 클릭 시 펼침.
 * warnings 는 `[카테고리] 메시지` 형식 — 카테고리별 그룹핑.
 */
export function ValidationWarningsBanner({ warnings, trace, compact }: Props) {
  const [open, setOpen] = useState(false);
  const hasWarnings = !!warnings && warnings.length > 0;
  const hasTrace = !!trace && trace.length > 0;
  if (!hasWarnings && !hasTrace) return null;

  const groups = hasWarnings ? groupByCategory(warnings!) : {};
  const total = (warnings?.length ?? 0) + (trace?.length ?? 0);
  const variant = hasWarnings ? "ui-alert--warning" : "ui-alert--info";
  const rootClass = `ui-alert ${variant} validation-banner${compact ? " validation-banner--compact" : ""}`;

  return (
    <div className={rootClass} data-testid="validation-warnings-banner">
      <button
        type="button"
        className="validation-banner__toggle"
        onClick={() => setOpen(!open)}
        aria-expanded={open}
      >
        <span className="validation-banner__title">
          AI 품질 리포트 — 총 {total}건
          {hasWarnings && <> · 경고 {warnings!.length}</>}
          {hasTrace && <> · 자동 교정 {trace!.length}</>}
        </span>
        <span className="validation-banner__hint">
          (클릭으로 {open ? "접기" : "보기"})
        </span>
      </button>

      {open && (
        <div className="validation-banner__body">
          {hasWarnings && (
            <div className="validation-banner__section">
              <div className="validation-banner__section-title">
                ⚠ 검증 경고 (원본 유지, 수동 확인 필요)
              </div>
              {Object.entries(groups).map(([cat, msgs]) => (
                <div key={cat} className="validation-banner__group">
                  <div className="validation-banner__group-title">
                    {cat} · {msgs.length}건
                  </div>
                  <ul className="validation-banner__list">
                    {msgs.map((m, i) => <li key={i}>{m}</li>)}
                  </ul>
                </div>
              ))}
            </div>
          )}

          {hasTrace && (
            <div className="validation-banner__section">
              <div className="validation-banner__section-title">
                ✎ 자동 교정 이력 (원본 → 정식 이름)
              </div>
              <ul className="validation-banner__trace-list">
                {trace!.map((t, i) => (
                  <li key={i} className="validation-banner__trace-item">
                    <code className="validation-banner__trace-from">{t.from}</code>
                    <span className="validation-banner__trace-arrow">→</span>
                    <code className="validation-banner__trace-to">{t.to}</code>
                    <span className="validation-banner__trace-type">
                      ({t.match_type})
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function groupByCategory(warnings: string[]): Record<string, string[]> {
  const groups: Record<string, string[]> = {};
  for (const w of warnings) {
    const m = w.match(/^\[([^\]]+)\]\s*(.*)$/);
    const cat = m ? m[1] : "기타";
    const msg = m ? m[2] : w;
    if (!groups[cat]) groups[cat] = [];
    groups[cat].push(msg);
  }
  return groups;
}
