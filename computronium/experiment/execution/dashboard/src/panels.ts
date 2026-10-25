/** Simple panel registry. */

import { registry } from "./components/registry.js";
import type { Component } from "./components/registry.js";

export interface Panel {
  id: string;
  label: string;
  glyph: string;
  key?: string;
  toggle(): void;
  isOpen(): boolean;
}

export class PanelRegistry {
  private readonly panels = new Map<string, Panel>();
  private readonly listeners = new Set<() => void>();

  register(panel: Panel): void {
    this.panels.set(panel.id, panel);
    this.notify();
  }

  get(id: string): Panel | undefined {
    return this.panels.get(id);
  }

  list(): Panel[] {
    return [...this.panels.values()];
  }

  toggle(id: string): void {
    const panel = this.panels.get(id);
    if (!panel) return;
    panel.toggle();
    this.notify();
  }

  isOpen(id: string): boolean {
    const panel = this.panels.get(id);
    return panel ? panel.isOpen() : false;
  }

  openIds(): string[] {
    return this.list().filter((p) => p.isOpen()).map((p) => p.id);
  }

  byKey(key: string): Panel | undefined {
    return this.list().find((p) => p.key === key);
  }

  onChange(listener: () => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notify(): void {
    for (const l of this.listeners) l();
  }
}

export const panels = new PanelRegistry();

export const HIDDEN_CLASS = "panel-hidden";

export function setPanelHidden(el: HTMLElement | null, hidden: boolean): void {
  if (!el) return;
  el.classList.toggle(HIDDEN_CLASS, hidden);
}

export function closeButton(onClose: () => void): HTMLButtonElement {
  const btn = document.createElement("button");
  btn.className = "panel-close";
  btn.setAttribute("aria-label", "close");
  btn.textContent = "×";
  btn.style.cssText = `
    background: none; border: none; color: var(--text-secondary);
    font-size: 16px; line-height: 1; cursor: pointer; padding: 4px 8px;
  `;
  btn.addEventListener("click", (e) => { e.stopPropagation(); onClose(); });
  return btn;
}

export function registerPanel(
  id: string, label: string, glyph: string,
  toggle: () => void, isOpen: () => boolean, key?: string
): void {
  panels.register({ id, label, glyph, key, toggle, isOpen });
}

export function getPanelElement(id: string): HTMLElement | null {
  return document.getElementById(id);
}

export function registerDisplayPanel(
  id: string, label: string, glyph: string,
  element: () => HTMLElement | null, key?: string
): void {
  registerPanel(id, label, glyph,
    () => { const p = element(); if (p) setPanelHidden(p, !p.classList.contains(HIDDEN_CLASS)); },
    () => { const p = element(); return p ? !p.classList.contains(HIDDEN_CLASS) : false; },
    key);
}