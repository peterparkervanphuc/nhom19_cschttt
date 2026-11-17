# Round 4 execution plan

The active objective is full independent C01–C12 implementation, integration, experiments and evaluation. The authoritative method is the paper plus Round 3.6 decisions in ../round4_preflight/decision_closure/. P0 fixtures establish software behavior. P1 runs require verified datasets and complete coverage. Round 5 extensions remain deferred.

Initial audit on 2026-11-17 found main at 63b0ec745f13e89fe678b346fc1883ea56755d64 with existing untracked .agents/, .github/, .idea/, docs/. There was no Python implementation, test suite, venv, dataset or checkpoint in the independent repository. The sibling author repository remains a read-only reference at 494b315a555e713bdd61f0edd7d033c31d5850bf with clean status. No baseline tests existed to execute.

| Stage | Deliverable and acceptance | Status |
|---|---|---|
| S0 | Exact uv 3.11.15 project venv, hash lock, imports and CPU optimizer smoke, resource inventory | CPU smoke and independent cold recreation verified; 50 tests in second venv |
| S1 / C01 | CSV/XES adapters, filters, manifest/split/vocab/prefix, CLI prepare, 5/3 fixture and provenance gates | Fixture, Sepsis and BPIC13-CP prepared; official raw files/counts verified for seven log variants; remaining five dataset identities unresolved |
| S2 / C02–C04 | ProcessTransformer, training, checkpoint/resume, prediction and attention, numerical/gradient/mask tests | Fixture exact epoch resume; full Sepsis and BPIC13-CP baseline training/prediction executed |
| S3 | Numerical primitives, directed graph projection/pruning, serialization and hand-computed tests | Tests and GraphML round-trip passed; SVG inspected; paired AE–BE descriptive comparison implemented |
| S4 / C05–C07 | Independently callable E1, E2-FC/AC/UNI, E3-PAPER/AUTHOR, fixture tests and actual runs | Primary fixture complete; E2/E3 durable streaming tested; real runs tracked in EXPERIMENTAL_RESULTS.md |
| S5 / C08–C09 | BE and exhaustive AE with signed votes, occurrence IDs, coverage/resume and integration | Full fixture ledger/cache/resume verified; Sepsis exhaustive AE computationally infeasible under locked protocol |
| S6 / C10–C12 | Nine XAI outputs, predictive metrics, graph export, complete fixture pipeline and dataset pilot/full runs | Full nine-stage fixture complete; real-data evaluation, plot/report coverage and remaining datasets incomplete |

Execute S0 then S1, S2 and S3, numerical gates before integrated S4/S5 and S6. Maintain exact data/config/checkpoint identities across experiments. Each failed test requires diagnosis and rerun before advancing the affected gate. CPU reference uses torch 2.6.0+cpu. CUDA is a separate future environment profile after CPU acceptance. Explicit FPT authorization remains required for paid resources.

## Verification and experiment gates

Run `.venv/Scripts/python.exe -m pytest` with JUnit evidence under artifacts/. Run package dependency validation and build/import checks after changes. Fixture acceptance includes reference arithmetic, axes/masks, frozen parameters separately from uniformity, repeated activities, exact threshold boundaries, nulls and signed normalization. Every primary run needs immutable configuration, data/split/class hashes, checkpoint identity, seeds, expected/completed records, wall/resource counters, failure reasons and outputs. Store large data/checkpoints under ignored data/ and artifacts/.

Discover official acquisition routes for the twelve logs in the existing inventory. Verify terms, exact versions, hashes and preprocessing before each benchmark. Helpdesk public candidate differs from paper counts. Synthetic smoke fixtures cannot support real-data reproduction claims. Planned full schedule is 16 training jobs per log, with separate diagnostic run IDs. Determine AE workload from actual k before full runs. Keep partial runs resumable and explicitly incomplete.

## Decisions

- Use established Round 3.6 architecture and namespace nhom19_process_xai without importing author modules.
- Use project-local CPU venv from the exact uv interpreter. Dependencies compiled with hashes using installed uv and the official PyTorch CPU index plus PyPI.
- Dataset loader and preprocessing APIs retain event ordinals before filtering. Any identified missing contract remains pending until implemented and tested.
- Follow ECC verification-loop proportionately to Python research code. Target claims require executed evidence, and coverage percentages never replace numerical/behavioral acceptance.

Update PROGRESS.md after each milestone. REQUIREMENTS_TRACEABILITY.md maps all components. EXPERIMENTAL_RESULTS.md records only actual executions. Final technical report and Round 5 handoff are due after feasible implementation and experiments finish.

## Current continuation order

1. Complete feasible streaming E2/E3 real-data runs with sealed per-prefix coverage. Preserve source snapshots when code changes so a partial run can resume with its exact code identity.
2. Extend bounded/durable execution to E1 and the XAI orchestration. The current in-memory `run_study` and `pipeline` commands are fixture-oriented; use `--streaming` for large E2/E3. Do not launch full real-data `pipeline` without an AE work estimate.
3. Finish BE separately on real logs; report exhaustive AE infeasibility without substituting capped pilot graphs. Pilot Sepsis observed k=174, requiring 2^175 contexts for one prefix alone. A cap or sampled AE is a separate diagnostic/future decision, not primary compliance.
4. Complete adapter/resource/provenance manifest audit, required figures and published-result comparison, independent review and final handoff. Resolve exact Helpdesk and four synthetic datasets through legitimate sources; do not fabricate substitute benchmark identities.

Round 4 remains incomplete. No full twelve-log reproduction, author-runtime parity, BPMN ground-truth validation or human-interpretability validation has been established.
