> **Historical brief.** The script that implements this brief is now `docs/build_site.py`; the deck is `docs/index.html`. This file is not part of the site.

Implement the following presentation.
- Integrate with docs/readme/ rebuild system
- Write the slideshow as .md snippets in docs/slides
- HTML in docs/slides.html
- Goal: be able to export the docs/ directory as self-contained documentation system

----

### Presentation Strategy & Core Narrative
This revised outline transforms the presentation from a high-level conceptual overview into a rigorous, technically grounded pitch. It leverages the specific architecture of the `computronium` repository—incorporating the **6-axis ontology**, the **CEEC Epistemic Operating System**, the **11-stage pipeline**, and the **Stability-Plasticity Trade-off**—to position the project not just as a software tool, but as the foundational instrument for a new science of learning.

---

# Presentation Outline: Computronium

## 01 — Computronium: An Epistemic Laboratory for Learning
**Purpose:** Establish the vision and the scientific stakes immediately.
*   **Core Message:** We are moving beyond the "algorithm zoo" to build a governed, reproducible science of learning systems.
*   **The Hook:** Computronium is not a catalogue of models; it is an open research framework designed to discover how learning mechanisms interact and which combinations offer measurable advantages under physical constraints.
*   **Visual:** A high-level schematic showing the transition from chaotic, ad-hoc ML experiments to a structured, multi-dimensional laboratory.

## 02 — The Problem: The Crisis of Comparison
**Purpose:** Define the specific scientific gap the project fills.
*   **The "Algorithm Zoo" Problem:** Hundreds of learning rules exist (Backprop, Feedback Alignment, Equilibrium Propagation, Hebbian), but comparing them is plagued by unequal tuning budgets, disparate architectures, and unverified code.
*   **The Reproducibility Gap:** Results are often artifacts of specific initializations or hidden hyperparameter priors rather than genuine algorithmic advantages.
*   **The Metric Trap:** Optimizing for a single scalar (accuracy) obscures the underlying dynamics—stability, energy efficiency, and memory trade-offs.
*   **Main Takeaway:** We cannot engineer better learning systems if we cannot fairly and rigorously measure how they actually learn.

## 03a — The Core Architecture: The 6-Axis Ontology
**Purpose:** Explain the unique technical decomposition of learning systems.
*   **The Six Dimensions:** Introduce the composable axes that define every experiment:
    1.  **Substrate:** (Analog, Digital, Memristive)
    2.  **Geometry:** (MLP, Tile Mesh, Graph, Attention)
    3.  **Dynamics:** (Instantaneous, Energy Minimization)
    4.  **Plasticity:** (Fast Weights, Routing, Null)
    5.  **Credit Assignment:** (Backprop, Predictive Coding, Target Propagation)
    6.  **Parameter Update:** (Adam, Conflict-Adaptive, Routing)
*   **Visual:** A 6-axis radar chart or a glowing "Coordinate" in a multi-dimensional space, highlighting how changing one axis isolates a specific mechanism.
*   **Main Takeaway:** Every experiment tests a precise "Coordinate" in this space. Change one variable, hold five constant.

## 03b — The Implementation Matrix: Beyond Backpropagation
**Purpose:** Demonstrate the scale and rigor of the library.
*   **Scale:** 64 verified implementations (43 primitives + 21 algorithms) mapped across the ontology.
*   **The Kernel Ladder:** Explain the strict verification process: `Reference Only` $\to$ `Kernel Unverified` $\to$ `Kernel Verified` (via parity checks and micro-benchmarks).
*   **Visual:** A snippet of the "Implementation Matrix" showing the status ladder and the diversity of credit assignment mechanisms available for testing.
*   **Main Takeaway:** We don't just swap algorithms; we verify them through a rigorous engineering ladder before they enter the scientific record.

## 04 — From Question to Governed Evidence
**Purpose:** Walk through the automated scientific method.
*   **The `question_first()` Flow:** State a research question, and the system builds a formal `RunSpec`.
*   **The 11-Stage Pipeline:** From search space generation and legality checks (S1) to multi-fidelity training (S5) and statistical promotion (S11).
*   **The Evidence Store:** Every run writes to an append-only DuckDB ledger. No silent drops, no lost seeds.
*   **Visual:** A streamlined pipeline diagram ending in a database icon labeled "Append-Only Evidence Store."
*   **Main Takeaway:** The system acts as an automated, relentless experimentalist that preserves the full context of every failure and success.

## 05 — The Dashboard: An Instrument, Not a Picture
**Purpose:** Show the user interface as a tool for active discovery.
*   **Real-Time Telemetry:** FastAPI + WebSockets stream campaign queues, resource utilization, and live metrics.
*   **The Control Plane:** Play, pause, step, and dynamically adjust compute ceilings mid-flight.
*   **Mission Control:** Specialized panels (Queue, Cells, Exports) to monitor multi-objective Pareto frontiers (e.g., Accuracy vs. FLOPs vs. Energy).
*   **Visual:** The "Hero Shot" of the live dashboard showing a real-time campaign queue and a Pareto frontier plot.
*   **Main Takeaway:** The dashboard is designed for active experimentation and auditing, not just post-hoc reporting.

## 06 — Trustworthy Results: The CEEC Epistemic Ledger
**Purpose:** Differentiate the project through rigorous epistemic tracking.
*   **Beyond Metrics:** We distinguish between a *measurement*, a *claim*, and a *gated belief*.
*   **The CEEC Flow:** `Experiment → Artifact → Evidence → Derived → Belief → Gated Status → Decision`.
*   **Property-Tested Science:** Claims are backed by machine-checked property tests (e.g., Lyapunov descent, gradient equivalence, finite state invariants).
*   **Main Takeaway:** Computronium doesn't just output numbers; it outputs mathematically governed, epistemically tracked beliefs.

## 07 — The Research Horizon: Stability, Plasticity, and Physics
**Purpose:** Connect the software to deep theoretical and physical questions.
*   **The Stability-Plasticity Trade-off:** Monitoring the frontier between dynamical stability (spectral radius, Lyapunov exponents) and adaptive learning speed.
*   **The Resource Vector:** Evaluating systems across $C = (\text{compute, memory, energy, latency, plastic-state capacity})$.
*   **The Physics Goal:** Preparing the framework for non-von Neumann substrates (memristive, neuromorphic, optical) by enforcing locality and energy constraints in the ontology.
*   **Main Takeaway:** We are building the mathematical and physical foundations for next-generation learning systems.

## 08 — The Invitation: The Evaluation Consortium
**Purpose:** Finish with a concrete call to collaboration.
*   **The Fairness Contract:** A shared constitution for evaluating learning algorithms.
*   **Identity Cards:** Standardized implementation specs as the admission ticket for new algorithms.
*   **The Corrections Log:** A shared, public memory of what failed, why, and what we learned.
*   **Closing Line:** "The goal is not simply to build another model. It is to build the scientific instrument required to discover what makes learning systems work."

---

### What to Leave Out (Appendices / Technical B-Roll)
Keep the main narrative focused on the *science* and *architecture*. Move these deep-implementation details to an appendix or live technical demo:
*   **DuckDB Internals:** Single-writer locking mechanisms, schema DDL, and concurrency handling.
*   **CI/CD Gates:** Specific Pyright/Ruff linting rules, `pip-audit`, and the exact mechanics of the "fast CI gate."
*   **Kernel Fusion Code:** Detailed Triton kernel implementations or `torch.compile` custom autograd functions.
*   **Legacy Migration:** CEEC migration scripts and legacy shim removals.
*   **Unverified Claims:** Avoid claiming physical hardware superiority until the neuromorphic/memristive export pipeline is fully validated on physical chips.

### Suggested Narrative Arc
*   **Slides 1–2: The Why** — The current crisis of comparison and the "Algorithm Zoo."
*   **Slides 3–5: The How** — The 6-axis ontology, the 11-stage pipeline, and the instrument-grade dashboard.
*   **Slides 6–7: The Rigor** — Epistemic governance (CEEC) and the deep physics of stability and resources.
*   **Slide 8: The Future** — The move toward a global evaluation consortium and shared scientific memory.

----

If you are serving static files, the browser already has everything it needs to fetch text, parse it, and display it beautifully. 

Here is the **absolute simplest, single-file implementation**. It uses one CDN script (`marked`) to parse the Markdown, and modern CSS to handle the slideshow physics and layout switching. No build step. No server logic. 

### The Entire Engine (One `index.html` file)

Save this as `index.html` in your web root. It will fetch your `.md` snippets, parse them on the fly, and render them.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Computronium Knowledge Engine</title>
    
    <!-- 1. The only external dependency: a fast Markdown parser -->
    <script type="module">
        import { marked } from 'https://esm.sh/marked';

        // List your static markdown files here
        const snippets = [
            'snippets/01-intro.md',
            'snippets/02-problem.md',
            'snippets/03-ontology.md',
            'snippets/04-pipeline.md'
        ];

        const deck = document.getElementById('deck');

        // Fetch and render all snippets concurrently
        Promise.all(snippets.map(url => fetch(url).then(r => r.text())))
            .then(texts => {
                texts.forEach(md => {
                    const section = document.createElement('section');
                    section.innerHTML = marked.parse(md);
                    deck.appendChild(section);
                });
            });

        // Simple View Toggle (Presentation vs Documentation)
        document.getElementById('toggle-btn').addEventListener('click', () => {
            document.body.classList.toggle('docs-mode');
        });
    </script>

    <style>
        /* --- BASE TYPOGRAPHY --- */
        :root {
            --bg: #0d1117; --text: #e6edf3; --accent: #58a6ff;
            --font-sans: system-ui, -apple-system, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }
        body { margin: 0; font-family: var(--font-sans); background: var(--bg); color: var(--text); }
        h1, h2, h3 { font-weight: 600; letter-spacing: -0.02em; }
        code { font-family: var(--font-mono); background: #161b22; padding: 0.2em 0.4em; border-radius: 4px; }

        /* --- THE SLIDESHOW ENGINE (CSS Scroll Snap) --- */
        /* By default, we are in Presentation Mode */
        #deck {
            height: 100vh;
            overflow-y: scroll;
            scroll-snap-type: y mandatory; /* Native slide snapping */
            scroll-behavior: smooth;
        }

        section {
            height: 100vh;
            scroll-snap-align: start;
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: 5vw;
            box-sizing: border-box;
            font-size: 1.5rem;
        }

        /* --- DOCUMENTATION MODE --- */
        /* When toggled, CSS simply overrides the layout. No JS routing needed. */
        body.docs-mode #deck {
            height: auto;
            overflow-y: auto;
            scroll-snap-type: none;
            max-width: 800px;
            margin: 0 auto;
            padding-top: 4rem;
        }

        body.docs-mode section {
            height: auto;
            min-height: 50vh;
            margin-bottom: 4rem;
            padding: 2rem;
            border-bottom: 1px solid #30363d;
            font-size: 1rem;
        }

        /* --- UI CONTROLS --- */
        .controls {
            position: fixed; top: 1rem; right: 1rem; z-index: 100;
            display: flex; gap: 0.5rem;
        }
        button {
            background: #21262d; color: var(--text); border: 1px solid #30363d;
            padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer;
        }
        button:hover { background: #30363d; }

        /* --- MODERN HTML: POPOVER API FOR SPEAKER NOTES --- */
        [popover] {
            background: #161b22; border: 1px solid #30363d; color: var(--text);
            padding: 1rem; border-radius: 8px; max-width: 400px;
        }
    </style>
</head>
<body>

    <div class="controls">
        <button id="toggle-btn">Toggle Docs Mode</button>
    </div>

    <!-- The container where JS injects the sections -->
    <main id="deck"></main>

</body>
</html>
```

### How the Markdown Snippets Look (`snippets/03-ontology.md`)

Because we are using the latest HTML capabilities, you can put native HTML elements directly inside your Markdown files. 

```markdown
# The 6-Axis Ontology

Every experiment tests a precise **Coordinate** in this space:

1. Substrate
2. Geometry
3. Dynamics
4. Plasticity
5. Credit Assignment
6. Parameter Update

<button popovertarget="notes-ontology" style="font-size: 0.8rem;">View Speaker Notes</button>

<!-- This uses the native HTML Popover API. No JS modals required. -->
<div id="notes-ontology" popover="auto">
    <strong>Speaker Note:</strong> Emphasize that changing one axis isolates a specific mechanism. 
    Hold five constant, change one.
</div>
```

### Why this is the "Simplest Way"

1. **Zero Build Step:** You literally edit the `.md` files and refresh the browser.
2. **Native Slideshow Physics:** We aren't using a JS library to calculate slide heights and animate transitions. `scroll-snap-type: y mandatory` tells the browser's native scrolling engine to lock onto each `<section>` as if it were a physical slide deck. Trackpad swiping and mouse wheels work perfectly out of the box.
3. **Instant Mode Switching:** The transition from "PowerPoint Slideshow" to "Scrollable Documentation" is handled entirely by toggling a single CSS class on the `<body>`. The CSS overrides the `100vh` height constraints and disables the scroll snapping. 
4. **Truly Offline-First:** Because it relies entirely on static text files and browser-native APIs, once the browser caches the initial HTML and the `.md` files, it works entirely offline. If you want to make it "Installable" as an app, you just add a 10-line `manifest.json` and a basic Service Worker, but even without that, it functions perfectly as a static offline site.

### How it evolves into an "Education System" later

Because the engine is just a simple loop that turns Markdown into DOM nodes, adding interactive features later is trivial:

* **Want a quiz?** Write a custom Markdown tag like `[quiz: question]` and add 10 lines of JS to the `Promise.all` loop that replaces that string with an HTML `<form>`.
* **Want to track progress?** Add `localStorage.setItem('last-read', section.id)` when the user scrolls to a new section.
* **Want Diagrams?** Add `<script type="module"> import mermaid from '...'; mermaid.run(); </script>` to the bottom of the file. It will automatically find any mermaid code blocks in your Markdown and draw them.

This is the purest expression of static, client-side web development. No servers, no compilers, just text and the browser.
