# LiteX HarmonyOS PC Porting Project Plan

## First-Phase Scope

The first phase covers native Python installation, LiteX/Migen imports,
portable core tests, and export-only minimal SoC generation on HarmonyOS PC.

### Core acceptance

- Native CPython and pip are available.
- LiteX and Migen install without broken Python dependencies.
- The 24 portable baseline tests pass.
- The minimal SoC generates Verilog, CSR CSV/JSON, and software headers.
- The procedure is reproducible from a clean directory.

### Toolchain extensions

- CPU cross compiler and BIOS build.
- Verilator simulation.
- Serial-port or remote-bus integration.
- Physical FPGA synthesis, programming, and boot.

### Out of scope for the first phase

- Porting CPython, GCC, LLVM, Verilator, or a vendor FPGA suite from scratch.
- Rewriting LiteX algorithms unrelated to operating-system compatibility.
- Requiring a vendor bitstream before the Python core baseline passes.

## Work Items

| Owner | Branch | First-week output | Status |
|---|---|---|---|
| 1 - lead/integration | `feature/baseline-integration` | baseline, core flow, minimal SoC, acceptance runner | PR #2 merged; PR #8 native final acceptance complete 2026-10-10 |
| 2 - environment/dependencies | `feature/harmony-environment` | environment probe, dependency matrix, setup instructions | PR #1 merged 2026-10-07 |
| 3 - core compatibility | `feature/core-compatibility` | platform audit, minimal fixes, compatibility notes | PR #4 merged; week-two supplemental checks and native runner prepared 2026-10-11; member-3 native session pending device access |
| 4 - tests/documentation | `feature/tests-docs`; `feature/final-acceptance` | HarmonyOS test results, comparisons, report structure | PR #3 merged; integrated native/Windows validation complete 2026-10-08; follow-up evidence awaits review |

All feature branches submit pull requests to `port/harmonyos-pc`. The `master`
branch remains close to upstream LiteX.

Integrated candidate `ed0c556c3` passed 5/5 required steps, 24 portable tests,
and 6 focused regressions on both Windows and native HarmonyOS PC. The lead's
current candidate `fe3261f0e` also passed the hardened 5/5 native acceptance,
24 portable tests, and minimal SoC generation. See the
[report](PORTING_REPORT.md) for artifact differences and extension limits.

## Risk Register

| ID | Risk | Evidence required | Owner | Response |
|---|---|---|---|---|
| R1 | No native CPython/pip on HarmonyOS PC | version commands and full error log | 2 | request an official runtime or scope decision; do not silently switch to a VM |
| R2 | Migen name inference differs by Python version | minimal traceback and Python version | 1/3 | compare with the Windows baseline and explicit-name workarounds |
| R3 | Path, encoding, or temporary-file differences | normalized output diff and reproduction | 3/4 | patch only the narrow platform boundary and add regression coverage |
| R4 | Optional CPU/core package unavailable | package name, version, install/import log | 2 | keep it outside core acceptance and document the limitation |
| R5 | Verilator or cross GCC unavailable | executable/version checks | 2/4 | mark simulation/firmware as an extension; retain export-only acceptance |
| R6 | Limited HarmonyOS PC access | booking record and prepared one-shot commands | 1 | prepare scripts before using the machine and collect logs in one session |
| R7 | Feature work targets the wrong branch | PR base branch and protection check | 1 | require PRs into `port/harmonyos-pc` |

## Daily Sync Template

Each member reports:

1. Completed since the previous sync.
2. Planned before the next sync.
3. Blocking issue, including command, environment version, full log, and a
   minimal reproduction.

The lead updates the risk register and decides whether a blocker affects core
acceptance or only a toolchain extension.

## First-Week Exit Criteria

- [x] Fork, integration branch, and feature branches exist.
- [x] Baseline commit and reference environment are fixed.
- [x] Windows LiteX/Migen installation and portable tests are recorded.
- [x] LiteX core flow and porting boundaries are documented.
- [x] Export-only minimal SoC example is implemented and verified.
- [x] Automated acceptance runner is implemented and verified.
- [x] Four GitHub Issue templates are ready for the project members.
- [x] Environment setup and matrix submitted in merged PR #1; native evidence linked from the validation report.
- [ ] All four work items exist as GitHub Issues with owners (Issues disabled; lead must decide whether PR tracking is sufficient).
- [x] Baseline pull request is merged into `port/harmonyos-pc` (PR #2).
- [x] Lead records personal clean-directory replay, accepts comparison exceptions and final scope, and reviews the follow-up validation PR.

## Second-Week Status

| Day | Lead/integration result | Status |
|---|---|---|
| 6 | Synced `feature/baseline-integration` to the green `port/harmonyos-pc` baseline and reviewed the integrated compatibility work | Complete |
| 7 | Hardened the acceptance runner so command start failures and timeouts retain logs and appear in the JSON report | Complete |
| 8 | Replayed the required acceptance checks from an empty Windows directory and compared the outputs with the saved native HarmonyOS evidence | Reference side complete |
| 9 | Repeated minimal SoC generation from the clean environment; all eight compared artifacts matched | Complete |
| 10 | Ran the hardened acceptance command on the current commit on the HarmonyOS PC, retrieved the report over HDC USB, and prepared PR #8 evidence | Complete |

Current native lead checkpoint: `fe3261f0e8becf83018fc387416fa1be321708b8`.
The clean Windows replay and final HarmonyOS PC run both passed 5/5 required
steps and 24/24 portable tests. The native run generated all 9 recorded minimal
SoC artifacts without a required-step failure.
`litex_sim` remains an optional extension blocked at the missing LiteEth import;
Verilator, cross-GCC, firmware, and board execution remain outside core acceptance.
See `docs/evidence/2026-10-10/lead-week2-reference.json` for the Windows
reference and `docs/evidence/2026-10-10/lead-week2-harmonyos.json` for the
auditable native summary and hashes of the locally retained raw reports.
