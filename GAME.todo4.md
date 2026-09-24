# GAME.todo4.md — True, complete usability ("Doorstep")

**Status:** Planned — not started.
**Scope:** Everything a user touches: the dashboard, its panels, copy, navigation, first-run path, accessibility, and the evidence that it works for humans.
**Predecessors:** todo → todo2 → todo3 finished the engineering (locks green, budgets gated, honesty gaps closed). This plan starts from a different question: not "is it verified?" but "can a person actually use it?"

## 0. The standard (read first)

A green test suite is not usability. This plan measures outcomes with **people**, and treats every user-facing gap as a defect — there is no "informational" disposition here, no waiver-by-default, no counting locks as done. Verification posture is **empirical and human-judged** (repo taxonomy L5 plus structured human rating); for usability questions that is the correct level, stated openly rather than apologetically.

Definition of done for the whole plan: **three representative users, none of whom built the system, each complete the core task flow below unaided, rate SUS ≥ 75, and encounter zero dead ends.** Anything short of that is progress, not completion.

Core task flow (the thing the dashboard exists for):

1. Cold start → first insight in under 5 minutes (a stranger goes from `comp dashboard` to "I can see which cells learned and which failed").
2. Diagnose a campaign: find the Pareto front, identify the defect funnel's top issue, and explain one structural void — using only on-screen copy.
3. Recover from confusion: every empty, loading, or error state tells the user what happened and what to do next.

## 1. Honest baseline (verified, not assumed)

- 23 panels registered; the engineering renders all of them populated-or-empty without crashing (C2).
- 5+ shipped panels are **permanent dead ends**: workshop, probe analytics, genome health, mutation explorer, veto log always render empty — their data producer (Auto-Evolve event log) does not exist. todo3 documented the emptiness; documentation is not usability.
- axe automated scan green, tokens green; the manual keyboard crawl has never been run — keyboard-only use is uncertified, not merely uncertified-on-paper.
- No usability study of any kind has ever been run; no SUS score, no task timing, no user has been watched using this.
- First-run path: onboarding tour + quiz exist in code; unknown whether anyone can actually reach insight through them.
- Explorer copy was judged by a script whose heuristic fails on short labels ("Continuous diffusion" → grade 20.6); no human has edited the copy for comprehension.
- Backend medians are fast (snapshot ~124 ms, adapter ~47 ms @5k), but **first paint, interaction latency, and large-root behavior as experienced** were never measured.

## 2. Work items

| ID | Item | Acceptance | Size |
|----|------|------------|------|
| **U1** | **Run a real usability study, then act on it** — recruit 3+ representative non-builder users; scripted tasks = the core flow (§0); record task success, time-to-first-insight, SUS; file every friction point as a defect; fix or scope the top findings in the same plan | Study report with scores + video/notes; SUS ≥ 75 on re-test after fixes; every critical friction fixed or explicitly cut | L |
| **U2** | **End permanent dead ends** — each always-empty panel gets one of three fates: (a) build the real data producer, (b) remove it from navigation until the producer exists, (c) convert it to an honest preview that says what it will do and when. "Empty with a documented reason" is an engineering note, not a user experience | Zero shipped panels that a user can open and find permanently nothing; each fate recorded per panel | M |
| **U3** | **Keyboard accessibility for real** — run the manual crawl end-to-end against the live dashboard, fix every finding, then record the cert. Automated axe stays green throughout | Crawl checklist 100% pass on the record; fixes committed, not waived | S–M |
| **U4** | **First-run to first insight** — instrument and optimize the cold path: measure wall time from `comp dashboard` to a stated insight on a seeded demo root; make the tour actually carry a stranger there; empty states must guide action ("run X to produce Y"), never just report absence | Median stranger time-to-first-insight < 5 min, measured not asserted; tour completion wired to the insight, not to clicking through | M |
| **U5** | **Navigation & information architecture audit** — 23 panels is a maze. Group, order, and progressively disclose: what a newcomer needs first vs power tools; Explorer/Lab registers must read as one coherent product, not two vocabularies | A stranger finds front/funnel/voids without guidance (study task); panel count the user *sees* first drops without deleting capability | S–M |
| **U6** | **Copy review by a human** — editorial pass over every user-facing string (panel explanations, empty states, toasts, errors, tour) for comprehension by a non-builder. Retire the FK-grade gate as a quality signal; keep the script as a spell-check-grade tripwire only | Every string a study participant stumbled on is rewritten; re-test shows no copy-driven failures | M |
| **U7** | **State visibility & recovery** — loading, polling-only-vs-daemon, error, and stale-data states must announce themselves and offer the next action. Includes the toast path (a crash was found there as recently as todo3) and daemon-disconnect behavior | Fault-injection walkthrough (kill daemon, empty root, corrupt artifact, slow UMAP): every state legible, every recovery one action away | S–M |
| **U8** | **Performance as experienced** — measure first paint, panel-switch latency, and ≥20k-cell behavior from the browser's perspective; fix what a user would feel, gate what matters | First paint < 10 s on the reference root; interaction p95 recorded and published in the dashboard doc; gates added only where users feel them | M |

## 3. Session plan

1. **Session A — see clearly (U1 study design + U3 crawl + U8 measurement).** Write the study script, run the keyboard crawl, instrument first paint. No fixes yet — produce the honest defect list first.
2. **Session B — cut the dead ends (U2) + fix crawl/study blockers.** Panel fates decided and executed; U3 fixes; first U1 findings triaged.
3. **Session C — guide the stranger (U4 + U5 + U6).** Tour, nav, and copy reworked against study evidence; re-test with fresh participants.
4. **Session D — harden the experience (U7 + U8 fixes) and re-run the study.** SUS ≥ 75 + unaided core flow = done.
5. Human users are the critical path from Session A onward — recruit before Session A ends.

## 4. Anti-excuses (binding on this plan)

- No user-facing gap may be dispositioned "informational," "wontfix," or "documented" without a dated re-review trigger and a named owner. todo3's engineering dispositions do not transfer.
- Test counts, lock counts, and budget numbers are supporting evidence, never acceptance. U1's human scores are the gate.
- Do not add panels, gamification, or features during this plan. Usability comes from removing friction and dead ends, not surface area.
- If a finding requires a producer that doesn't exist (Auto-Evolve log, daemon features), the default is to **cut the dependent UI**, not to spec the producer. Building new backends is a different plan.

## 5. Notes for implementers

- The study in U1 is the highest-leverage item and the one most easily faked — real strangers, real tasks, recorded sessions, written report. A hallway chat with a teammate does not count.
- `tests/ui/test_dashboard_render.py` + `test_dashboard_interactions.py` are the regression net for U2/U5 rework; extend them with every new empty/loading/error state from U7.
- Keep the targeted-test discipline: human sessions are expensive, machine runs are cheap — never spend a participant on something a script could have caught.
- On U2 option (a): a real Auto-Evolve event-log producer is new measurement surface and belongs in its own plan with its own locks — prefer (b)/(c) here.

*End of GAME.todo4.md — usability is when a stranger succeeds, not when the suite glows.*
