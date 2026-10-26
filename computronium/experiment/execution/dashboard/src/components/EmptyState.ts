/** Unified EmptyState component — single component for all empty states (TODO75 S4). */

export interface EmptyStateConfig {
  /** Icon to display (emoji or text). */
  icon?: string;
  /** Title text. */
  title: string;
  /** Descriptive message. */
  message: string;
  /** Primary CTA button config. */
  cta?: {
    label: string;
    onClick: () => void;
    variant?: "primary" | "secondary" | "danger";
  };
  /** Additional CSS class for custom styling. */
  className?: string;
}

/** Create an empty state element. */
export function createEmptyState(config: EmptyStateConfig): HTMLElement {
  const el = document.createElement("div");
  el.className = `empty-state ${config.className ?? ""}`;
  el.style.cssText = `
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 24px 16px;
    color: var(--text-muted);
    font-size: 11px;
    gap: 8px;
  `;

  if (config.icon) {
    const icon = document.createElement("div");
    icon.className = "empty-state-icon";
    icon.style.cssText = "font-size: 24px; opacity: 0.5;";
    icon.textContent = config.icon;
    el.appendChild(icon);
  }

  const title = document.createElement("div");
  title.className = "empty-state-title";
  title.style.cssText = "font-size: 13px; font-weight: 600; color: var(--text-primary);";
  title.textContent = config.title;
  el.appendChild(title);

  const message = document.createElement("div");
  message.className = "empty-state-message";
  message.style.cssText = "font-size: 11px; color: var(--text-secondary); max-width: 280px; line-height: 1.5;";
  message.textContent = config.message;
  el.appendChild(message);

  if (config.cta) {
    const cta = config.cta;
    const btn = document.createElement("button");
    btn.className = `empty-state-cta ${cta.variant === "primary" ? "primary" : cta.variant === "danger" ? "danger" : "secondary"}`;
    btn.textContent = cta.label;
    btn.style.cssText = `
      padding: 10px 20px;
      font-size: 12px;
      font-weight: 600;
      border-radius: 6px;
      border: 1px solid var(--border);
      cursor: pointer;
      transition: background 0.1s, border-color 0.1s, color 0.1s;
    `;

    // Apply variant styles
    if (cta.variant === "primary") {
      btn.style.background = "var(--gradient)22";
      btn.style.borderColor = "var(--gradient)66";
      btn.style.color = "var(--gradient)";
    } else if (cta.variant === "danger") {
      btn.style.background = "var(--error)22";
      btn.style.borderColor = "var(--error)66";
      btn.style.color = "var(--error)";
    } else {
      btn.style.background = "var(--bg-tertiary)";
      btn.style.borderColor = "var(--border)";
      btn.style.color = "var(--text-primary)";
    }

    btn.addEventListener("mouseenter", () => {
      if (cta.variant === "primary") {
        btn.style.background = "var(--gradient)33";
        btn.style.borderColor = "var(--gradient)";
      } else if (cta.variant === "danger") {
        btn.style.background = "var(--error)33";
        btn.style.borderColor = "var(--error)";
      } else {
        btn.style.background = "var(--bg-primary)";
        btn.style.borderColor = "var(--border-bright)";
      }
    });
    btn.addEventListener("mouseleave", () => {
      if (cta.variant === "primary") {
        btn.style.background = "var(--gradient)22";
        btn.style.borderColor = "var(--gradient)66";
      } else if (cta.variant === "danger") {
        btn.style.background = "var(--error)22";
        btn.style.borderColor = "var(--error)66";
      } else {
        btn.style.background = "var(--bg-tertiary)";
        btn.style.borderColor = "var(--border)";
      }
    });

    btn.addEventListener("click", cta.onClick);
    el.appendChild(btn);
  }

  return el;
}

/** Show/hide an empty state element. */
export function setEmptyStateVisible(el: HTMLElement | null, visible: boolean): void {
  if (!el) return;
  el.style.display = visible ? "flex" : "none";
}

/** Create a chart-specific empty state with standard hint. */
export function createChartEmptyState(
  chartId: "pareto" | "ablation" | "variability",
  glyph: string,
  title: string,
  key: string
): HTMLElement {
  const hints: Record<string, string> = {
    pareto: "Run with multiple credit arms to populate the frontier. Pick a profile with credit axis variety.",
    ablation: "Add credit-axis groups to see ablation. Profiles with credit axis variety enable this chart.",
    variability: "Add seeds in the control panel (seeds > 1) to see seed-to-seed spread.",
  };

  return createEmptyState({
    icon: glyph,
    title,
    message: hints[chartId] ?? "Select a run from the legend to populate this chart.",
    className: "chart-empty-state",
  });
}