/** The control panel: the options that do not belong on a bar (TODO70, refactored for TODO71 Phase 1).
 *
 * Four sections, and each one replaces something that needed a terminal:
 *
 * **New run** — the profile picker, what the profile declares, the
 * reader's edits, and Start. Without a campaign queue the panel says so
 * and gives the command to type: the dashboard must never appear to have
 * a control it does not have.
 *
 * **This run** — the run's declaration as it stands. A run's declaration is
 * frozen once it has begun, so the panel shows it and says so rather than
 * offering an editor that would lie.
 *
 * **The queue** — the campaigns waiting and running, with cancel and
 * preempt, and the queue's own ceilings.
 *
 * **Cells** — the three cell verbs, reachable without clicking a cell in
 * the 3D scene.
 *
 * **Exports** — the narration script, the run's report, and the records as
 * JSON: the dashboard is the whole instrument, and a reader can take the
 * picture away.
 */

import { registry } from "./components/registry.js";
import { CONTROL_KEYS } from "./keys.js";
import { panels, registerDisplayPanel, setPanelHidden, closeButton } from "./panels.js";
import { createPanelShell } from "./shell.js";
import { runSelection } from "./run-selection.js";
import type { Component } from "./components/registry.js";

/** One profile, as the server offers it. */
interface Profile {
  name: string;
  description: string;
  stages: string[];
  fidelity: string;
  task: string;
  n_seeds: number;
  epochs: number;
  batch_limit: number;
  budget_seconds: number | null;
  param_budget: number;
  objectives: string[];
  policy: string;
  axes: { axis: string; primitives: string[] }[];
}

/** One axis, as the server offers it. */
interface Axis {
  axis: string;
  primitives: {
    name: string;
    description: string;
    available: boolean;
    unavailable_reason: string | null;
  }[];
}

/** One campaign, as the queue holds it. */
interface Campaign {
  campaign_id: string;
  name: string;
  status: string;
  priority: string;
}

/** The six axes a cell names, in the order the ontology declares them. */
const CELL_AXES = [
  "substrate",
  "geometry",
  "dynamics",
  "plasticity",
  "credit",
  "update",
] as const;

function createControlPanelBody(): string {
  return `
    <style>
      #control-panel h4 {
        margin: 14px 0 6px;
        font-size: 11px;
        letter-spacing: 0.08em;
        color: var(--text-primary);
      }
      #control-panel table.kv, #control-panel table.list {
        width: 100%;
        border-collapse: collapse;
        font-size: 11px;
      }
      #control-panel table.kv th, #control-panel table.list th {
        text-align: left;
        font-weight: 500;
        color: var(--text-secondary);
        padding: 2px 6px 2px 0;
        vertical-align: top;
      }
      #control-panel table.kv td, #control-panel table.list td {
        color: var(--text-primary);
        padding: 2px 6px 2px 0;
        vertical-align: top;
      }
      #control-panel .note {
        color: var(--text-secondary);
        margin: 4px 0 8px;
        line-height: 1.4;
      }
      #control-panel .row {
        display: flex;
        gap: 8px;
        align-items: center;
        margin: 4px 0;
      }
      #control-panel input, #control-panel select {
        background: var(--bg-tertiary);
        color: var(--text-primary);
        border: 1px solid var(--border);
        border-radius: 4px;
        font-size: 11px;
        padding: 2px 4px;
        min-width: 0;
      }
      #control-panel button.mini {
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: 4px;
        color: var(--text-primary);
        font-size: 11px;
        padding: 2px 8px;
        cursor: pointer;
      }
      #control-panel button.action {
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: 4px;
        color: var(--text-primary);
        font-size: 11px;
        padding: 4px 10px;
        cursor: pointer;
        transition: all 0.1s ease;
      }
      #control-panel button.action:hover:not(:disabled) {
        background: var(--border);
        border-color: var(--border-bright);
      }
      #control-panel button.action:disabled {
        opacity: 0.4;
        cursor: not-allowed;
      }
      #control-panel .cell-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        align-items: center;
      }
      #control-panel .cell-row label {
        display: flex;
        flex-direction: column;
        gap: 2px;
        font-size: 10px;
        color: var(--text-secondary);
        white-space: nowrap;
      }
      #control-panel .cell-row select {
        font-size: 10px;
        padding: 2px 6px;
      }
    </style>
    <div id="control-panel-header" style="display: flex; align-items: center; gap: 8px;">
      <span style="font-weight: 600; color: var(--text-primary); letter-spacing: 0.08em;">CONTROL</span>
      <div style="flex: 1;"></div>
    </div>

    <h4>NEW RUN</h4>
    <div class="row">
      <select class="profile"></select>
      <select class="device">
        <option value="auto">auto</option>
        <option value="cpu">cpu</option>
        <option value="cuda">cuda</option>
      </select>
    </div>
    <div class="note profile-note"></div>
    <div class="row">
      <label>seeds</label><input class="seeds" type="number" min="1" />
      <label>epochs</label><input class="epochs" type="number" min="1" />
      <label>budget</label><input class="budget" type="number" min="1" />
      <select class="fidelity">
        <option value="L0">L0</option>
        <option value="L1">L1</option>
        <option value="L2">L2</option>
      </select>
    </div>
    <div class="row">
      <button class="action start">Start run</button>
    </div>
    <div class="note new-run-note"></div>

    <h4>THIS RUN</h4>
    <div class="run-section"></div>

    <h4>THE QUEUE</h4>
    <div class="queue-section"></div>

    <h4>CELLS</h4>
    <div class="row cell-row"></div>
    <div class="row">
      <button class="action replicate">Replicate</button>
      <button class="action preregister">Preregister</button>
      <button class="action quest">Quest</button>
    </div>
    <div class="note cell-note"></div>

    <h4>EXPORTS</h4>
    <div class="row">
      <button class="action export-script">Narration script</button>
      <button class="action export-report">Run report</button>
      <button class="action export-records">Records as JSON</button>
    </div>
    <div class="note export-note"></div>
  `;
}

export class ControlPanel implements Component {
  name = "ControlPanel";

  private container: HTMLElement | null = null;
  private profiles: Profile[] = [];
  private axes: Axis[] = [];
  private newRunSection: HTMLElement | null = null;
  private runSection: HTMLElement | null = null;
  private queueSection: HTMLElement | null = null;
  private cellSection: HTMLElement | null = null;
  private exportSection: HTMLElement | null = null;
  private profileSelect: HTMLSelectElement | null = null;
  private seedsInput: HTMLInputElement | null = null;
  private epochsInput: HTMLInputElement | null = null;
  private budgetInput: HTMLInputElement | null = null;
  private deviceSelect: HTMLSelectElement | null = null;
  private fidelitySelect: HTMLSelectElement | null = null;
  private profileNote: HTMLElement | null = null;
  private newRunNote: HTMLElement | null = null;
  private cellSelects = new Map<string, HTMLSelectElement>();
  private cellNote: HTMLElement | null = null;
  private exportNote: HTMLElement | null = null;

  /** Scroll a section into view (for palette deep links). */
  showSection(sectionId: string): void {
    if (!this.container) return;
    const headings = this.container.querySelectorAll("h4");
    for (const h of headings) {
      if (h.textContent?.toLowerCase().includes(sectionId.toLowerCase().replace("-", " "))) {
        h.scrollIntoView({ behavior: "smooth", block: "start" });
        // Briefly highlight
        h.style.transition = "background 0.3s ease";
        h.style.background = "var(--gradient)22";
        setTimeout(() => (h.style.background = ""), 800);
        break;
      }
    }
  }

  async init(): Promise<void> {
    this.container = createPanelShell({
      id: "control-panel",
      title: "Control Panel",
      glyph: "⚙",
      key: CONTROL_KEYS.panel,
      body: createControlPanelBody(),
      dock: "floating",
      defaultOpen: false,
    });

    this.bindElements();
    this.bindEvents();

    registerDisplayPanel(
      "control-panel",
      "control panel",
      "⚙",
      () => this.container,
      CONTROL_KEYS.panel,
    );
    await this.loadCatalogue();
    void this.refresh();
  }

  async destroy(): Promise<void> {
    this.container?.remove();
  }

  private bindElements(): void {
    if (!this.container) return;
    this.newRunSection = this.container.querySelector(".new-run-note");
    this.runSection = this.container.querySelector(".run-section");
    this.queueSection = this.container.querySelector(".queue-section");
    this.cellSection = this.container.querySelector(".cell-section");
    this.exportSection = this.container.querySelector(".export-note");
    this.profileSelect = this.container.querySelector(".profile");
    this.profileNote = this.container.querySelector(".profile-note");
    this.newRunNote = this.container.querySelector(".new-run-note");
    this.cellNote = this.container.querySelector(".cell-note");
    this.exportNote = this.container.querySelector(".export-note");
    this.seedsInput = this.container.querySelector(".seeds");
    this.epochsInput = this.container.querySelector(".epochs");
    this.budgetInput = this.container.querySelector(".budget");
    this.deviceSelect = this.container.querySelector(".device");
    this.fidelitySelect = this.container.querySelector(".fidelity");

    const cellRow = this.container.querySelector<HTMLElement>(".cell-row")!;
    for (const axis of CELL_AXES) {
      const label = document.createElement("label");
      label.textContent = axis;
      const select = document.createElement("select");
      select.className = `cell-${axis}`;
      label.appendChild(select);
      cellRow.appendChild(label);
      this.cellSelects.set(axis, select);
    }

    this.container
      .querySelector<HTMLElement>("#control-panel-header")!
      .appendChild(closeButton(() => panels.toggle("control-panel")));
  }

  private bindEvents(): void {
    if (!this.container) return;
    this.profileSelect?.addEventListener("change", () => this.renderProfileNote());
    this.container
      .querySelector<HTMLButtonElement>(".start")!
      .addEventListener("click", () => void this.startRun());
    this.container
      .querySelector<HTMLButtonElement>(".replicate")!
      .addEventListener("click", () => void this.cellAction("replicate"));
    this.container
      .querySelector<HTMLButtonElement>(".preregister")!
      .addEventListener("click", () => void this.cellAction("preregister"));
    this.container
      .querySelector<HTMLButtonElement>(".quest")!
      .addEventListener("click", () => void this.cellAction("quest"));
    this.container
      .querySelector<HTMLButtonElement>(".export-script")!
      .addEventListener("click", () => void this.export("script"));
    this.container
      .querySelector<HTMLButtonElement>(".export-report")!
      .addEventListener("click", () => void this.export("report"));
    this.container
      .querySelector<HTMLButtonElement>(".export-records")!
      .addEventListener("click", () => void this.export("records"));
  }

  /** The profiles and the axes the form offers. */
  private async loadCatalogue(): Promise<void> {
    try {
      const [profiles, axes] = await Promise.all([
        fetch("/api/profiles").then((r) => r.json()),
        fetch("/api/axes").then((r) => r.json()),
      ]);
      this.profiles = (profiles.profiles ?? []) as Profile[];
      this.axes = (axes.axes ?? []) as Axis[];
    } catch {
      this.profiles = [];
      this.axes = [];
    }
    this.renderProfileOptions();
    this.renderCellOptions();
  }

  /** What the reader can change, and what the run is doing now. */
  private async refresh(): Promise<void> {
    await Promise.all([
      this.refreshRuns(),
      this.refreshQueue(),
      this.refreshStatus(),
    ]);
  }

  /** The runs the store holds, and the declaration of each. */
  private async refreshRuns(): Promise<void> {
    if (!this.runSection) return;
    try {
      const response = await fetch("/api/runs");
      const body = (await response.json()) as {
        runs?: {
          run_id: string;
          status: string;
          records: number;
          seeds_owed?: number;
          declaration?: Record<string, unknown>;
        }[];
      };
      const runId = this.currentRunId();
      const run = (body.runs ?? []).find((r) => r.run_id === runId);
      this.runSection.innerHTML = this.renderRun(run);
    } catch {
      this.runSection.innerHTML = `<div class="note">the store did not answer</div>`;
    }
  }

  /** The queue's campaigns, and its own ceilings. */
  private async refreshQueue(): Promise<void> {
    if (!this.queueSection) return;
    try {
      const [campaigns, queue] = await Promise.all([
        fetch("/api/campaigns").then((r) => r.json()),
        fetch("/api/queue").then((r) => r.json()),
      ]);
      this.queueSection.innerHTML = this.renderQueue(
        (campaigns.campaigns ?? []) as Campaign[],
        queue as Record<string, unknown>,
      );
      this.queueSection
        .querySelectorAll<HTMLButtonElement>("[data-cancel]")
        .forEach((button) =>
          button.addEventListener("click", () => {
            void this.cancelCampaign(button.dataset.cancel ?? "");
          }),
        );
      this.queueSection
        .querySelectorAll<HTMLButtonElement>("[data-preempt]")
        .forEach((button) =>
          button.addEventListener("click", () => {
            void this.preemptCampaign(button.dataset.preempt ?? "");
          }),
        );
    } catch {
      this.queueSection.innerHTML = `<div class="note">the queue did not answer</div>`;
    }
  }

  /** The run's own account of itself, from the control plane. */
  private async refreshStatus(): Promise<void> {
    if (!this.newRunSection) return;
    try {
      const response = await fetch("/api/control");
      const body = (await response.json()) as {
        control?: { paused: boolean; cancel: boolean };
        status?: { stage: string; cells_done: number; in_flight: number } | null;
        readable: boolean;
        error: string | null;
      };
      if (!body.readable) {
        this.newRunNote!.textContent =
          body.error ?? "the control plane could not be read";
        return;
      }
      const status = body.status;
      this.newRunNote!.textContent = status
        ? `The run is in ${status.stage} with ${status.cells_done} cells measured.`
        : "No run is reporting. The panel can still start one.";
    } catch {
      this.newRunNote!.textContent = "the server did not answer";
    }
  }

  /** The run the panel is about. */
  private currentRunId(): string | null {
    return runSelection.selectedId ?? null;
  }

  private renderProfileOptions(): void {
    if (!this.profileSelect) return;
    this.profileSelect.innerHTML = "";
    for (const profile of this.profiles) {
      const option = document.createElement("option");
      option.value = profile.name;
      option.textContent = profile.name;
      this.profileSelect.appendChild(option);
    }
    this.renderProfileNote();
  }

  /** What the chosen profile declares, before the reader edits anything. */
  private renderProfileNote(): void {
    if (!this.profileNote || !this.profileSelect) return;
    const profile = this.profiles.find(
      (candidate) => candidate.name === this.profileSelect!.value,
    );
    if (!profile) {
      this.profileNote.textContent = "";
      return;
    }
    this.profileNote.textContent = [
      profile.description,
      `fidelity ${profile.fidelity} · ${profile.n_seeds} seeds · ${profile.epochs} epochs`,
      profile.budget_seconds ? `budget ${profile.budget_seconds}s` : "no budget",
      `policy ${profile.policy}`,
      `axes ${profile.axes.map((a) => a.axis).join(", ") || "all"}`,
    ].join(" · ");
    if (this.seedsInput) this.seedsInput.value = String(profile.n_seeds);
    if (this.epochsInput) this.epochsInput.value = String(profile.epochs);
    if (this.budgetInput) {
      this.budgetInput.value = profile.budget_seconds
        ? String(profile.budget_seconds)
        : "";
    }
    if (this.fidelitySelect) this.fidelitySelect.value = profile.fidelity;
  }

  /** One select per axis, so a cell can be named without the 3D scene. */
  private renderCellOptions(): void {
    for (const axis of CELL_AXES) {
      const select = this.cellSelects.get(axis);
      if (!select) continue;
      const available = this.axes.find((a) => a.axis === axis);
      select.innerHTML = "";
      for (const primitive of available?.primitives ?? []) {
        const option = document.createElement("option");
        option.value = primitive.name;
        option.textContent = primitive.available
          ? primitive.name
          : `${primitive.name} (unavailable)`;
        option.disabled = !primitive.available;
        select.appendChild(option);
      }
      const first = select.querySelector<HTMLOptionElement>(
        "option:not([disabled])",
      );
      if (first) select.value = first.value;
    }
  }

  private renderRun(
    run:
      | {
          run_id: string;
          status: string;
          records: number;
          seeds_owed?: number;
          declaration?: Record<string, unknown>;
        }
      | undefined,
  ): string {
    if (!run) {
      return `<div class="note">no run is selected</div>`;
    }
    const declaration = run.declaration ?? {};
    const rows: [string, string][] = [
      ["run", run.run_id],
      ["status", String(run.status)],
      ["profile", String(declaration.profile ?? "—")],
      ["tasks", (declaration.tasks as string[] ?? []).join(", ") || "—"],
      ["fidelity", String(declaration.fidelity ?? "—")],
      ["objectives", (declaration.objectives as string[] ?? []).join(", ") || "—"],
      ["mode", String(declaration.mode ?? "—")],
      ["declared cells", String(declaration.declared_cells ?? "—")],
      ["records", String(run.records)],
      ["seeds still owed", String(run.seeds_owed ?? "—")],
    ];
    return [
      `<div class="note">A run's declaration is frozen once it has begun; the panel shows it rather than offering an editor that would lie.</div>`,
      `<table class="kv">${rows
        .map(([key, value]) => `<tr><th>${key}</th><td>${value}</td></tr>`)
        .join("")}</table>`,
    ].join("");
  }

  private renderQueue(
    campaigns: Campaign[],
    queue: Record<string, unknown>,
  ): string {
    const rows = campaigns
      .map(
        (campaign) => `<tr>
          <td>${campaign.campaign_id}</td>
          <td>${campaign.name}</td>
          <td>${campaign.status}</td>
          <td>
            <button data-cancel="${campaign.campaign_id}" class="mini">cancel</button>
            <button data-preempt="${campaign.campaign_id}" class="mini">preempt</button>
          </td>
        </tr>`,
      )
      .join("");
    const ceilings: [string, string][] = [
      ["max concurrent", String(queue.max_concurrent ?? "—")],
      ["max cpus", String(queue.max_cpus ?? "—")],
      ["max gpus", String(queue.max_gpus ?? "—")],
    ];
    return [
      `<table class="kv">${ceilings
        .map(([key, value]) => `<tr><th>${key}</th><td>${value}</td></tr>`)
        .join("")}</table>`,
      rows
        ? `<table class="list"><tr><th>id</th><th>name</th><th>status</th><th></th></tr>${rows}</table>`
        : `<div class="note">the queue is empty</div>`,
    ].join("");
  }

  /** Start the run the reader described. */
  private async startRun(): Promise<void> {
    if (!this.profileSelect) return;
    const overrides: Record<string, unknown> = {};
    if (this.seedsInput?.value) overrides.n_seeds = Number(this.seedsInput.value);
    if (this.epochsInput?.value) overrides.epochs = Number(this.epochsInput.value);
    if (this.budgetInput?.value) {
      overrides.budget_seconds = Number(this.budgetInput.value);
    }
    if (this.fidelitySelect?.value) {
      overrides.fidelity = this.fidelitySelect.value;
    }
    try {
      const response = await fetch("/api/runs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          profile: this.profileSelect.value,
          overrides,
          device: this.deviceSelect?.value ?? undefined,
        }),
      });
      const body = (await response.json()) as {
        started?: boolean;
        error?: string;
        command?: string;
        campaign_id?: string;
      };
      if (body.started) {
        this.newRunNote!.textContent = `The run is queued as ${body.campaign_id}.`;
      } else {
        this.newRunNote!.textContent = `${body.error ?? "the run was refused"}. ${
          body.command ?? ""
        }`;
      }
    } catch {
      this.newRunNote!.textContent = "the dashboard could not reach the server";
    }
  }

  /** The cell the reader named, as the cell verbs want it. */
  private cellCoordinate(): Record<string, string> {
    const coordinate: Record<string, string> = {};
    for (const axis of CELL_AXES) {
      coordinate[axis] = this.cellSelects.get(axis)?.value ?? "";
    }
    return coordinate;
  }

  /** One of the three cell verbs, without a click in the 3D scene. */
  private async cellAction(action: "replicate" | "preregister" | "quest"): Promise<void> {
    const runId = this.currentRunId();
    if (!runId) {
      this.cellNote!.textContent = "no run is selected";
      return;
    }
    try {
      const response = await fetch(`/api/cells/${runId}/${action}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ coordinate: this.cellCoordinate() }),
      });
      const body = (await response.json()) as { error?: string; message?: string };
      this.cellNote!.textContent =
        body.error ?? body.message ?? `${action} was refused`;
    } catch {
      this.cellNote!.textContent = "the dashboard could not reach the server";
    }
  }

  private async cancelCampaign(campaignId: string): Promise<void> {
    await fetch(`/api/campaigns/${campaignId}/cancel`, { method: "POST" });
    await this.refreshQueue();
  }

  private async preemptCampaign(campaignId: string): Promise<void> {
    await fetch(`/api/campaigns/${campaignId}/preempt`, { method: "POST" });
    await this.refreshQueue();
  }

  /** Take the picture away: the script, the report, or the records. */
  private async export(what: "script" | "report" | "records"): Promise<void> {
    const runId = this.currentRunId();
    if (!runId) {
      this.exportNote!.textContent = "no run is selected";
      return;
    }
    try {
      if (what === "script") {
        const body = (await fetch("/api/narration").then((r) => r.json())) as {
          script?: string;
        };
        this.download("narration.txt", body.script ?? "");
        this.exportNote!.textContent = "the narration script was taken";
        return;
      }
      const endpoint = what === "report" ? "report" : "records";
      const body = (await fetch(`/api/runs/${runId}/${endpoint}`).then((r) =>
        r.json(),
      )) as { report?: string; records?: unknown[]; error?: string };
      if (body.error) {
        this.exportNote!.textContent = body.error;
        return;
      }
      const text =
        what === "report"
          ? (body.report ?? "")
          : JSON.stringify(body.records ?? [], null, 2);
      this.download(`${runId}-${endpoint}.${what === "report" ? "txt" : "json"}`, text);
      this.exportNote!.textContent = `the ${what} was taken`;
    } catch {
      this.exportNote!.textContent = "the dashboard could not reach the server";
    }
  }

  /** Hand a file to the reader. */
  private download(name: string, text: string): void {
    const blob = new Blob([text], { type: "text/plain" });
    const link = document.createElement("a");
    link.download = name;
    link.href = URL.createObjectURL(blob);
    link.click();
    URL.revokeObjectURL(link.href);
  }
}

export const controlPanel = new ControlPanel();
registry.register(controlPanel);