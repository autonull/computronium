/** Style imports and CSS variable setup (TODO68). */

// Import generated palette (CSS variables)
import "../templates/static/css/palette.css";

// Import TypeScript palette for three.js usage
import {
  PALETTE,
  ARM_COLORS,
  SUBSTRATE_COLORS,
  type ArmName,
  type SubstrateName,
} from "./palette.js";

// Re-export for other modules
export {
  PALETTE,
  ARM_COLORS,
  SUBSTRATE_COLORS,
  type ArmName,
  type SubstrateName,
};

// Inject CSS variables into document for HTML overlays
if (typeof document !== "undefined") {
  const root = document.documentElement;
  for (const [key, value] of Object.entries(PALETTE)) {
    root.style.setProperty(`--${key.replace(/_/g, "-")}`, value);
  }
}

// Global styles injected once
const styleSheet = document.createElement("style");
styleSheet.textContent = `
  :root {
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
  }

  * {
    box-sizing: border-box;
  }

  body {
    margin: 0;
    background: var(--bg);
    color: var(--text-primary);
    overflow: hidden;
  }

  #dashboard-canvas {
    display: block;
    width: 100vw;
    height: 100vh;
  }

  #ui-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 100;
  }

  #ui-overlay > * {
    pointer-events: auto;
  }

  /* Scrollbar styling */
  ::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }
  ::-webkit-scrollbar-track {
    background: var(--bg-secondary);
  }
  ::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 4px;
  }
  ::-webkit-scrollbar-thumb:hover {
    background: var(--border-bright);
  }
`;
document.head.appendChild(styleSheet);
