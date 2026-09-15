To achieve a **broad focus** with **useful preliminary results** and a **crystallizing high-dimensional visualization**, we need to temporarily pivot the AutoScientist from *intelligent search* to *stratified mapping*. 

The current sweep is trapped in the `energy_minimization` (em) slice due to the product-order bug and the broken surrogate model. To build a compelling visualization (like t-SNE/UMAP), you need data points from **all 7 dynamics families** and across the topological spectrum. A t-SNE of only `em` and `ps` will just show a single blob; a t-SNE of the whole space will reveal the "islands" of viable algorithms and the "voids" of structural incompatibility.

Here is the strategic execution plan to deliver this demonstration.

---

### Phase 1: The "Broad Map" Data Generation (Bypassing the Trap)
Do not waste time fixing the surrogate model or the coverage driver right now. Instead, write a **Stratified Random Sampler** that forces the execution of cells across the entire 6-D ontology. 

**The Script: `scripts/broad_mapping_sweep.py`**
1. **Stratify by Dynamics:** Ensure you pull an equal number of random configurations from all 7 dynamics families (`em`, `ps`, `error_predictive_coding`, `spike_integration`, `instantaneous`, `diffusion`, `lazy`).
2. **Use the Dry-Run Gate:** Since random sampling will generate thousands of structurally impossible combinations (e.g., `em` + `attention`), rely heavily on the `compose.dry_run_system` gate. 
   * *Crucial Epistemic Rule:* Do not log dry-run failures to the CEEC ledger as "experiments." Log them to a separate `structural_voids.jsonl` file. These voids are actually a massive scientific finding: they define the physical boundaries of the Computronium space.
3. **Shallow Budget:** Stick to the 1-epoch rapid protocol. You want 500–1,000 diverse data points, not 50 deeply trained ones.
4. **Record to CEEC:** Every cell that *passes* the dry-run gate gets pre-registered, executed, and logged to the ledger as usual. 

*Result:* Within a few hours, you will have a dataset containing representatives from SNNs (`spike_integration`), standard MLPs (`instantaneous`), and energy models (`em`/`ps`), complete with their `credit_trace` and `settle_horizon` instrument readings.

---

### Phase 2: Feature Engineering for High-Dimensional Visualization
To make t-SNE/UMAP work on categorical algorithmic configurations, you must translate the 6-D ontology into a continuous/vector space.

Create a script `scripts/visualize_atlas.py` that processes the SQLite/JSONL ledger:
1. **One-Hot Encode the Axes:** Convert Dynamics, Credit, Update, and Topology into binary vectors.
2. **Calculate Derived "Physics" Metrics:**
   * **BP-Deficit:** `Ruler_Ceiling - Measured_Accuracy`. (How far is this local rule from the global optimum?)
   * **Compute Efficiency:** `Accuracy / Training_Time`.
   * **Stability Margin:** Use the `spectral_radius` ($\rho$) or `settle_horizon` from the instrument logs.
   * **Gradient Alignment:** The cosine similarity from the `credit_trace` instrument.
3. **Concatenate:** Combine the one-hot vectors and the continuous physics metrics into a single high-dimensional feature vector for each cell.

---

### Phase 3: The "Crystallizing" Visualizations
Generate an interactive HTML dashboard (using Plotly or Streamlit) featuring these three specific views. This will serve as your primary demonstration artifact.

#### 1. The "Islands and Voids" Map (UMAP / t-SNE)
* **What it is:** A 2D scatter plot of the UMAP embedding of your feature vectors.
* **How to style it:** 
  * Color points by **BP-Deficit** (Red = high deficit/failure, Blue = low deficit/success).
  * Shape points by **Dynamics Family** (e.g., Circles for `em`, Triangles for `ps`, Stars for `spike_integration`).
* **The "Wow" Factor:** You will visually see distinct "islands" of algorithmic families. More importantly, you will see massive empty spaces. You can overlay the `structural_voids.jsonl` data as faint grey dots to show the "ghost topology" of the space—the combinations that the ontology allows but physics/geometry forbids.

#### 2. The "River of Computation" (Parallel Coordinates Plot)
* **What it is:** A Plotly Parallel Coordinates chart where each vertical axis represents an ontology dimension (Dynamics $\rightarrow$ Credit $\rightarrow$ Update $\rightarrow$ Topology $\rightarrow$ Accuracy).
* **The "Wow" Factor:** This visually crystallizes the *interaction effects*. You will literally see the "rivers" of high performance. For example, you might see a thick blue river flowing from `predictive_settling` $\rightarrow$ `thermodynamic_contrast` $\rightarrow$ `lion` $\rightarrow$ `feedforward`, while a red river shows `instantaneous` $\rightarrow$ `local_goodness` dying out at depth 8.

#### 3. The Instrument Radar (Spider Charts)
* **What it is:** Select the top 3 "Pareto-optimal" cells discovered in the broad sweep. Plot their instrument readings (`credit_trace` alignment, `settle_horizon`, $\rho(J_F)$, BP-Deficit) on a radar chart.
* **The "Wow" Factor:** This proves that the system isn't just finding high accuracy by luck; it proves *why* they work based on the physical instruments you built in Phase 0.

---

### Phase 4: Packaging the Demonstration
Wrap this into a single CLI command to make it reproducible and presentable.

```bash
comp gallery --generate-broad-demo --epochs 1 --sample-size 500
```

**The Narrative for your Demo/Paper:**
When presenting this, lean into the unique philosophy of Computronium:
1. **The Map is the Result:** "We didn't just find a new algorithm; we mapped the physical constraints of local learning. The voids in our t-SNE are just as important as the islands—they represent structural impossibilities."
2. **Instruments over Black Boxes:** "Notice how the UMAP clusters aren't just grouped by accuracy, but by their *gradient alignment* and *settling horizons*. Our instruments prove that `predictive_settling` forms a distinct physical regime compared to `energy_minimization`."
3. **The BP-Deficit Frontier:** "By mapping the BP-Deficit across 500 random coordinates, we have empirically defined the exact boundary where local, biologically plausible credit assignment can compete with global backpropagation."

### Immediate Next Steps for You:
1. Write the `broad_mapping_sweep.py` script using `random.choice` over the registries, stratified by Dynamics.
2. Ensure the `dry_run_gate` catches the shape mismatches so you don't pollute your CEEC ledger with execution errors.
3. Install `umap-learn` and `plotly` in your `uv` environment.
4. Run the sweep, export the data to a Pandas DataFrame, and generate the UMAP. 

This approach bypasses the current engineering blockers, respects the project's rigorous epistemic standards, and delivers exactly the kind of high-impact visual proof-of-concept you are looking for.
