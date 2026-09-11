# Publication Venue & Frozen Claim Set (T21.1.1)

Status: DECIDED 2026-09-11. This file is the authority for what the
manuscript may claim. Changing it requires re-running the claim-discipline
audit (T21.1.4).

## Venue decision

- **Primary target:** ICLR 2027 workshop track — a local-learning /
  biologically-plausible-learning or scientific-ML workshop (final CFP name
  to be confirmed when workshop lists publish, ~Dec 2026; deadline expected
  ~Jan–Feb 2027).
- **Page budget:** assume 4–6 pages + references + appendix (typical
  workshop limits; verify against the actual CFP before submission).
- **Fallback ladder:** (1) another ICLR/NeurIPS 2027 workshop on local
  learning or scientific ML; (2) arXiv preprint + a methods venue (e.g. a
  machine-learning methods journal) — same manuscript, same claim set.
- **Format:** workshop paper; the governance/CEEC framing is the
  differentiator, so the venue must tolerate a methods+governance hybrid.

## Mechanisms in scope (frozen)

| # | Mechanism | Package | Evidence | In scope |
|---|---|---|---|---|
| 1 | Temporal-ψ task switching | psi-peft | X-TPC-001/002/003, X-TAC-001 (E-000022..E-000026) | YES |
| 2 | Adaptive local feedback | local-feedback | X-ALI-001 (E-000018), X-ALI-002 (E-000027) | YES |
| 3 | Role-split muon readout | computronium-lab | X-USU-001 | BOUNDARY ONLY |
| 4 | Stable transient amplification | stability + lab | X-STA-001, X-STA-002 (E-000028) | YES |

Mechanism 3 appears only as a heterogeneous-update boundary (X-USU-001
win + FF×Muon collapse at width 32). The X-USU-002 defect hunt (T21.2.2)
and X-RSE baseline (T21.2.3) are **cut** unless the boundary-only framing
proves insufficient during drafting — re-open via a pre-registered
experiment first (G-RELEASE-5), never by relaxing scope silently.

## Frozen claim set

Claims are exactly the four scoped claims in `PUBLICATION_DRAFT.md`
(§Claims), verbatim in substance; `MANUSCRIPT.md` may rephrase but not
strengthen. Every number in the manuscript must trace to a command in
`REPRODUCIBILITY.md` and an evidence id or registered artifact.

## Constraints carried into the manuscript

- Threats-to-validity from `PUBLICATION_DRAFT.md` appear verbatim.
- Non-claims from `PUBLICATION_DRAFT.md` appear verbatim.
- Hardware blueprint is discussed as design-level, simulation-only.
- Banned-phrase scan (`tests/platform/test_release_docs.py`) covers the
  manuscript; negation-prefixed lines only.
