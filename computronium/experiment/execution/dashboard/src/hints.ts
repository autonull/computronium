/** Global keyboard hint overlay — shows shortcuts when holding Shift. */

import { allBindings } from "./bindings.js";

let hintOverlay: HTMLElement | null = null;
let visible = false;
let hideTimer: number | null = null;

export function initHints(): void {
  // Create overlay
  hintOverlay = document.createElement("div");
  hintOverlay.id = "keyboard-hints";
  hintOverlay.style.cssText = `
    position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
    background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px;
    padding: 12px 16px; z-index: 200; display: none;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    max-width: calc(100vw - 40px); overflow-x: auto;
  `;
  hintOverlay.setAttribute("role", "status");
  hintOverlay.setAttribute("aria-live", "polite");
  document.body.appendChild(hintOverlay);

  // Build hint content
  const groups = new Map<string, { key: string; desc: string }[]>();
  for (const b of allBindings()) {
    const k = b.chord ? `Shift+${b.chord.split("+")[1].toUpperCase()}` : b.key?.toUpperCase();
    if (!k) continue;
    const g = b.group;
    if (!groups.has(g)) groups.set(g, []);
    groups.get(g)!.push({ key: k, desc: b.label });
  }
  const order = ["Navigation", "Panels", "Charts", "Run Control", "Cell Actions", "Stage", "General"];
  const html = order.map((t) => {
    const items = groups.get(t) ?? [];
    if (!items.length) return "";
    return `<div style="margin-bottom: 8px;">
      <div style="font-size: 9px; font-weight: 600; letter-spacing: 0.08em; color: var(--text-secondary); margin-bottom: 4px; text-transform: uppercase;">${t}</div>
      <div style="display: flex; flex-wrap: wrap; gap: 12px;">
        ${items.map((i) => `<span style="display: flex; align-items: center; gap: 6px; font-size: 11px;"><kbd style="font-family: monospace; font-size: 9px; padding: 1px 5px; background: var(--bg); border: 1px solid var(--border-bright); border-radius: 3px; color: var(--text-primary);">${i.key}</kbd><span style="color: var(--text-secondary);">${i.desc}</span></span>`).join("")}
      </div>
    </div>`;
  }).join("");

  hintOverlay.innerHTML = html;

  // Show on Shift hold
  let shiftDown = false;
  window.addEventListener("keydown", (e) => {
    if (e.key === "Shift") {
      shiftDown = true;
      if (hideTimer) { clearTimeout(hideTimer); hideTimer = null; }
      showHints();
    }
  });
  window.addEventListener("keyup", (e) => {
    if (e.key === "Shift") {
      shiftDown = false;
      hideTimer = window.setTimeout(hideHints, 300);
    }
  });
  window.addEventListener("blur", () => { shiftDown = false; hideHints(); });
}

function showHints(): void {
  if (visible || !hintOverlay) return;
  visible = true;
  hintOverlay.style.display = "block";
}

function hideHints(): void {
  if (!visible || !hintOverlay) return;
  visible = false;
  hintOverlay.style.display = "none";
}