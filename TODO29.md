> I'd like to reframe the next step as a continuous process of open-ended iterative experiments, visible through an engaging and informative dashboard, or through (headless) runs of pre-allocated time, ex: 5 minutes.  at the same time, it will likely uncover defects and bugs in the system which we'll continually have to fix.  this is why i'm afraid to commit to investing in lengthy experiments.  think this solves my problem?

This is exactly the right philosophy, and frankly, it is the most mature way to operate an exploratory research framework like Computronium. 

You have correctly identified the core risk of "big science" in software research: **a 4-hour run that crashes at hour 3 isn't a wasted run; it's a bug report disguised as an experiment.** By shifting to a continuous, time-budgeted model, you turn that risk into your primary engine for system stability. You stop fearing defects and start *harvesting* them.

Here is why this solves your problem, and how we can architect it into the framework as a first-class operational mode.

### Why This Solves the Problem

1. **Crash-to-Regression Pipeline:** In a 5-minute run, if you hit a shape mismatch, OOM, or autograd break, you lose 5 minutes of compute. You fix the bug, add a property test (like your existing `test_device_hygiene_gate`), and that bug is banished forever. The system becomes exponentially more robust with every short run.
2. **Zero-Cost Resumption is Already Proven:** Your pilot run already proved the hardest part of this. When the background process died, the resumed run picked up seamlessly from the KB coverage matrix. The plumbing for "stop and resume" is already there; we just need to expose it as a time-budgeted API.
3. **Exploration vs. Exploitation:** Short runs are for *exploration* (mapping the voids, finding bugs, discovering Pareto fronts). They do not need to be epistemically "final." You only need long runs for *exploitation* (deep training of the top-5 Pareto cells found during the short runs). 

### Architecting "Continuous Computronium"

To make this a reality, we shift the framework from an "Experiment Runner" to a **Continuous Discovery Daemon**. Here is the architectural plan:

#### 1. The Headless Burst CLI (`comp continuous`)
Instead of `--sample-size`, we introduce a `--budget` or `--duration` flag.

```bash
# Run for exactly 5 minutes, then gracefully exit.
uv run comp continuous --budget 5m --credit-trace 

# Run until the ledger hits 100 new cells, then exit.
uv run comp continuous --target-cells 100 
```
*Under the hood:* This sets a `time.time()` hard-stop or a cell-counter. When the limit is reached, it gracefully flushes the in-memory campaign state to `kb.sqlite`, appends to `structural_voids.jsonl`, and exits with code 0. Cron or a loop can just keep calling it.

#### 2. The "Defect Funnel" (Crashes as Data)
Currently, the sweep handles `structural_voids` (ontology boundaries). We need a third ledger stream: `runtime_defects.jsonl`. 
When a cell passes the dry-run gate but crashes during execution (e.g., a lazy-init device bug), the sweep catches the exception, logs the traceback and the coordinate to `runtime_defects.jsonl`, marks the cell as "quarantined" in the KB (so it isn't re-proposed until the code changes), and continues. 
*Result:* The system auto-discovers its own bugs without wasting the rest of the run's budget.

#### 3. The Live Dashboard (NiceGUI or Streamlit)
Since you already use NiceGUI in your project, we can build a `comp dashboard` command. It doesn't run experiments; it just *watches* the SQLite ledger and JSONL streams in real-time.

The dashboard would feature three live-updating panels:
* **The Living Atlas:** The UMAP/t-SNE scatter plot. As the 5-minute run discovers new cells, they drop onto the map in real-time. The "voids" fade in as faint grey dots.
* **The System Health Gauge:** A live counter of `Runtime Defects Found vs. Resolved`. When you fix a bug and run the hygiene gate, you mark the defect as resolved in the dashboard. This gamifies the cleanup process.
* **The Pareto Radar:** A live update of the top-3 non-dominated cells (Accuracy vs. BP-Deficit vs. Settle Horizon). 

### Handling the "Short Run Epistemic Risk"

Your only remaining risk with 5-minute runs is variance: at small *N*, you might get a "lucky" cell that looks like a breakthrough but is just a random seed fluke. 

**The Solution:** We don't change the algorithm, we change the *epistemic status* in the CEEC ledger. 
* Cells from a 5-minute run (1 epoch) are tagged as `status: exploration_candidate`. 
* They are valid for mapping the *topology* of the space (where are the islands? where are the voids?), but they are not valid for *claims* (e.g., "EqProp beats Backprop").
* Once a month, you take the top 5 cells discovered by the continuous daemon and run them through a `comp deep-tier` (3 seeds, 10 epochs). 

### Next Concrete Steps

If you want to proceed with this model, here are the three concrete code changes we can make in the next session to unlock it:

1. **Implement the Time-Budget Wrapper:** Write a `ContinuousCampaign` class in `computronium/cli/continuous.py` that wraps the existing `BroadMappingCampaign` with a `time.monotonic()` check in the inner loop.
2. **Add the Defect Ledger:** Update `scripts/broad_mapping_sweep.py` to catch `RuntimeError` and `ValueError` during `SystemTrainer.fit()`, serialize the traceback to `runtime_defects.jsonl`, and add a `quarantined` flag to the KB proposal generator so it doesn't re-propose the broken coordinate.
3. **Draft the Live Dashboard:** Spin up a lightweight NiceGUI app (`computronium/dashboard/live_atlas.py`) that polls `kb.sqlite` every 2 seconds and redraws the Plotly UMAP.

This turns Computronium from a "tool you run when you have time" into an "always-on research companion" that slowly, safely, and continuously maps the universe while you do other things. Does this feel like the operational model you are looking for?

----

This is exactly the right paradigm shift. You are moving Computronium from being a **telescope** (point it, wait for light) to being an **active sensor network** (constantly pinging, adapting to noise, and mapping the dark). 

When you decouple the *duration* of the experiment from the *validity* of the discovery, you unlock a completely different class of research workflows. 

Let’s explore the idea space for this "Continuous Discovery" model across four dimensions: **Engagement, Defect Harvesting, Execution Mechanics, and Epistemic Maturation.**

---

### 1. The Dashboard: "Fog of War" and Tectonic Plates
If we are running 5-minute bursts continuously, the dashboard shouldn't just be a static report; it should feel like a live mission control.

*   **The Fog of War Grid:** As an additional visualization to UMAP: the actual 6D ontology as a massive, interactive 2D/3D grid. Cells that have never been evaluated are dark (Fog). Validated cells light up based on their BP-Deficit. Crashed cells are marked with hazard symbols. Voids are bottomless pits. As the daemon runs, you literally watch the fog clear.
*   **The "Tectonic" Frontier:** Visualize the $\rho(J_F) = 1$ (stability) boundary. Plot the live discoveries on this frontier. You will visually see the "coastline" where stable algorithms meet chaotic, expressive ones. 
*   **The Live Ticker (Pulse):** A scrolling terminal-style feed in the dashboard.
    *   `[14:02:11] Pulse: Evaluated `ps x local_goodness x muon`. Acc: 0.94, Settle: 12. (New Pareto Point)`
    *   `[14:04:05] Hazard: `spike x attention` crashed. Traceback captured. Cell quarantined.`
    *   `[14:06:00] Budget exhausted. Flushing ledger. Hibernating.`
*   **Gamified Health Metrics:** A literal "System Health" gauge. If the daemon is hitting the same shape mismatch over and over, the health meter drops. Fixing the bug and running the hygiene gate fills the meter back up.

### 2. The Defect Funnel: Turning Crashes into the Curriculum
In a 4-hour run, a crash is a disaster. In a 5-minute run, a crash is a **data point**. We can formalize the "Defect Funnel."

*   **Auto-Quarantine & Triage:** When a cell fails at runtime, the daemon catches the exception, hashes the traceback, and assigns it a `Defect_ID`. It writes to `runtime_defects.jsonl` and adds `quarantine: Defect_ID` to the cell's KB entry. The sampler now *knows* to avoid that coordinate until the code is patched.
*   **The "Bug Bounty" Board:** The dashboard highlights the top 3 most common `Defect_IDs`. "45 cells are failing due to `DevicePoisoning` in `RandomProjectionsCredit`." You fix the bug, and with one click (or CLI command), you "Unquarantine" those 45 cells, instantly injecting high-value data into the next burst.
*   **Adversarial Probing (Fuzzing the Ontology):** Allocate 10% of the 5-minute budget to *intentionally malformed* cells. What if `beta` is negative? What if the learning rate is $10^5$? This proactively discovers numerical stability boundaries that standard sampling misses.

### 3. Execution Mechanics: The "Budget-Aware" Daemon
*   **Loose Time Limit:** The hardest part of a time-boxed daemon is the hard stop. If the clock hits 00:05:00 right in the middle of a backward pass, the run is corrupted.  Use a min/max time that allows an experiment some slack time to complete rather than fatally interrupting it.
*   **Adaptive Budgets (Active Learning):** The system notices that `energy_minimization` cells take 3x longer to settle than `instantaneous` cells. The budget-aware scheduler automatically compensates: it schedules three `instantaneous` cells per minute, but only one `energy_minimization` cell, ensuring the GPU is never idle and the time-box is respected.
*   **Graceful Degradation:** If the daemon is running on a laptop that suddenly gets unplugged and switches to battery saver (detectable via OS hooks), it automatically drops from "Exploration Mode" (1 epoch) to "Validation Mode" (just running the forward pass to check for shape crashes, skipping training entirely).

### 4. Epistemic Maturation: The "Seed-to-Claim" Pipeline
How do short bursts eventually yield deep scientific claims? Through an automated maturation pipeline in the CEEC ledger.

*   **Level 0: The Spark (1 epoch, 1 seed):** Discovered in a 5-minute burst. Status: `candidate`. Good for mapping the fog of war.
*   **Level 1: The Survivor (3 epochs, 1 seed):** If a Level 0 cell hits the Pareto front, it gets auto-queued for the next burst at a higher epoch count. Status: `vetted`.
*   **Level 2: The Claim (10 epochs, 3 seeds):** If a Level 1 cell consistently survives across multiple days of bursts, it is promoted to `mature`. The dashboard flags it: "Candidate for Deep Tier."
*   **Contradiction Resolution:** If Burst A finds Cell X is great, but Burst B finds it's terrible, the system flags a `Variance_Audit`. It doesn't discard the data; it highlights the cell as having high sensitivity to initialization (which is a fascinating scientific finding in itself for dynamical systems).

---

### Where should we focus the development plan?

This idea space is huge. To form a concrete development plan for the next session, which of these "flavors" feels most urgent to you?

1.  **The Infrastructure & Mechanics:** Building the "Tick" architecture, the budget-aware scheduler, and the graceful shutdown hooks so we can actually run `comp continuous --budget 5m` safely right now.
2.  **The Defect Funnel:** Building the auto-quarantine system and the runtime defect ledger, so the 5-minute runs immediately start hardening the codebase against crashes.
3.  **The Dashboard/Engagement:** Building the "Fog of War" NiceGUI dashboard and the live ticker, so you have a beautiful, informative window into what the daemon is doing in the background.
4.  **The Maturation Pipeline:** Wiring the CEEC ledger to automatically promote cells from "Spark" to "Survivor" based on continuous burst data.

Pick your favorite thread (or a combination of two), and we can draft the exact architectural plan for it.
