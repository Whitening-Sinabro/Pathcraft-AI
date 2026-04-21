import { BuildIcon, SyndicateIcon, PassiveIcon, OverlayIcon } from "./icons";
import type { ComponentType } from "react";
import { openOverlay } from "../../overlay/toggle";

export const TAB_IDS = ["build", "syndicate", "passive"] as const;
export type TabId = typeof TAB_IDS[number];

export function isTabId(v: unknown): v is TabId {
  return typeof v === "string" && (TAB_IDS as readonly string[]).includes(v);
}

interface IconCmpProps { size?: number; strokeWidth?: number; className?: string; }

interface TabDef {
  id: TabId;
  label: string;
  Icon: ComponentType<IconCmpProps>;
}

const TABS: TabDef[] = [
  { id: "build",     label: "빌드 분석",   Icon: BuildIcon     },
  { id: "syndicate", label: "Syndicate",  Icon: SyndicateIcon },
  { id: "passive",   label: "패시브 트리", Icon: PassiveIcon   },
];

interface Props {
  activeTab: TabId;
  onSwitchTab: (tab: TabId) => void;
}

export function Sidebar({ activeTab, onSwitchTab }: Props) {

  return (
    <aside className="app-sidebar">
      <nav className="app-sidebar__nav" aria-label="메인 탭">
        {TABS.map(({ id, label, Icon }) => (
          <button
            key={id}
            type="button"
            className={`app-sidebar__nav-item${activeTab === id ? " is-active" : ""}`}
            onClick={() => onSwitchTab(id)}
            aria-current={activeTab === id ? "page" : undefined}
          >
            <span className="app-sidebar__nav-icon" aria-hidden="true">
              <Icon size={16} />
            </span>
            <span className="app-sidebar__nav-label">{label}</span>
          </button>
        ))}
      </nav>

      <div className="app-sidebar__footer">
        <button
          type="button"
          className="app-sidebar__action"
          onClick={openOverlay}
          title="오버레이 모드 (Ctrl/Cmd+Shift+O)"
        >
          <span className="app-sidebar__nav-icon" aria-hidden="true">
            <OverlayIcon size={16} />
          </span>
          <span className="app-sidebar__nav-label">오버레이 모드</span>
        </button>
      </div>
    </aside>
  );
}
