# The Research Horizon

## Stability versus plasticity

<!-- include: diagrams/tradeoff.svg -->

The frontier itself is the object of study: spectral radius and Lyapunov exponents on one axis, adaptation speed on the other. A system that is only fast is not a result.

## The resource vector

`C = (compute, memory, energy, latency, plastic-state capacity)`

Reported per run. Never collapsed into a scalar, because the collapse is where physical constraints get to hide.

## Physics-ready by construction

Local credit, explicit settling, and energy terms are ontology-level constraints, not retrofits. Substrates available today: <!-- gen:substrate_list -->.

> No physical-hardware superiority is claimed. Neuromorphic, memristive, and photonic paths are validated in simulation until they run on silicon.

## Research paths — a grid of open directions

Each path below is a self-contained research program with its own slides, specifications, and progress tracking.

<div class="research-grid">
  <a class="research-card" href="#/about/proof-research" data-research="proof">
    <span class="research-icon">📐</span>
    <h3>Formal Proof Research</h3>
    <p>Rocq-verified theorems for Computronium's ontology, plasticity mechanisms, and Z3-inspired universality. Machine-checked computational guarantees.</p>
    <span class="research-link">Open →</span>
  </a>

  <a class="research-card" href="#/about/consortium-research" data-research="consortium">
    <span class="research-icon">🤝</span>
    <h3>Evaluation Consortium</h3>
    <p>A community-led effort to make evidence about learning mechanisms easier to inspect, compare, reproduce, and improve. Fairness contracts, identity cards, corrections log.</p>
    <span class="research-link">Open →</span>
  </a>

  <a class="research-card" href="#/about/z3-research" data-research="z3">
    <span class="research-icon">🎯</span>
    <h3>Z3 Benchmark & Plasticity</h3>
    <p>The Z3-inspired benchmark: frozen weights (θ), evolving fast state (ψ). Can a network achieve universal multi-task behavior purely through plastic-state dynamics?</p>
    <span class="research-link">Open →</span>
  </a>

  <a class="research-card" href="#/about/metadynamics-research" data-research="metadynamics">
    <span class="research-icon">🌀</span>
    <h3>Metadynamics & Credit</h3>
    <p>State-dependent credit assignment, coupled dynamics stability, and the expressive hierarchy of plasticity primitives — routing, fast weights, rule-state, temporal.</p>
    <span class="research-link">Open →</span>
  </a>

  <a class="research-card" href="#/about/substrate-research" data-research="substrate">
    <span class="research-icon">⚡</span>
    <h3>Substrate & Hardware</h3>
    <p>Quantization error bounds, neuromorphic/photonic/memristive refinement, noise robustness, and resource-aware complexity for physical deployment.</p>
    <span class="research-link">Open →</span>
  </a>

  <a class="research-card" href="#/about/learning-theory-research" data-research="learning-theory">
    <span class="research-icon">📈</span>
    <h3>Learning Theory & Guarantees</h3>
    <p>Online adaptation bounds, distribution-shift response, task interference, and plasticity-vs-no-plasticity separation under declared resource budgets.</p>
    <span class="research-link">Open →</span>
  </a>
</div>

<!-- notes -->
The trade-off is the deep question: stability without adaptation is a frozen model, adaptation without stability is a system that forgets. The instrument's job is to place each system on the frontier with error bars.

Be explicit about the simulation caveat. The substrate axis exists so that locality and energy are first-class from the start; it does not yet prove anything about a device.

The research grid is a living map — each card links to a dedicated slide deck with specifications, milestones, and current progress. We expect this set to grow.
<!-- /notes -->
