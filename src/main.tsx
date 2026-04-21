import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { OverlayApp } from "./overlay/OverlayApp";
import { ActiveGameProvider } from "./contexts/ActiveGameContext";
import "./styles/global.css";
import "./overlay/overlay.css";

// ?mode=overlay → 오버레이 창, 아니면 메인 앱
const params = new URLSearchParams(window.location.search);
const isOverlay = params.get("mode") === "overlay";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <ActiveGameProvider>
      {isOverlay ? <OverlayApp /> : <App />}
    </ActiveGameProvider>
  </React.StrictMode>,
);
