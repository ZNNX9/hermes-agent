# Hermes OS Project State

Status: P0.1 completed
Last updated: 2026-06-12
Owner: Richard
Active topic: Hermes runtime health baseline

## Purpose

This `.agent` directory is the workflow source of truth for Richard's local
Hermes/Codex operating model. It records scoped task state, decisions, evidence
requirements, approval gates, and model/agent roles before runtime code is
changed.

## Current Slice

Ticket: P0.1 Runtime Health Baseline
Status: completed
Scope: `hermes doctor --json` runtime health diagnostics
Runtime changes: `doctor` CLI now has a read-only JSON health-report fast path
Tests/dependencies/CI changes: none
Secrets/app config changes: no files changed; API server key value was read
from existing config only to perform authenticated smoke checks

Evidence:

- `scripts/run_tests.sh tests/hermes_cli/test_doctor_json.py tests/hermes_cli/test_doctor.py tests/hermes_cli/test_doctor_command_install.py tests/hermes_cli/test_gateway_runtime_health.py`
  passed 78 tests.
- `.venv/bin/python ./hermes doctor --json` returned JSON with
  `api_models=ok`, `chat_smoke=ok`, `gateway_runtime=ok`,
  `listener_exposure=ok`, `secret_scan=ok`, and `receipt_validator=ok`.
- The same smoke returned `launchd_definition=warn` because the installed local
  launchd plist is not current.

## Current Chat Re-Sync

Ticket: P0.0a Current Chat Review And Handoff
Status: completed
Reviewed sources:

- Current Codex chat through Richard's instruction to review the update and
  continue with `$richard-ai-workflow`.
- Previously supplied ChatGPT shared chat URL via public shared-page extract.
- Local `.agent` project state and task queue.

Access honesty:

- ChatGPT shared content was reviewed as a public shared-page extract, not as a
  live browser session.
- No ChatGPT branch, project, folder, memory, or new session was created.
- No browser feedback was pasted or captured in a live ChatGPT UI during this
  slice.

Drift result:

- The plan remains an upgrade on top of the existing Hermes system, not a
  rewrite.
- GPT chat remains an advisory strategy/review source, not the authority or
  executor.
- P0.1 remains queued as a separate runtime-health ticket.

## Source-Of-Truth Order

1. Latest explicit Richard instruction.
2. Accepted `.agent` decision/task packet.
3. Verified repo state, git diff, and test output.
4. Older `.agent` project notes.
5. Browser LLM plans or shared-chat advice.
6. Memory or summaries.

Browser LLMs may advise, but local files, repo state, system/developer
instructions, and Richard approvals remain authoritative.

## Operating Boundary

Hermes coordinates, routes, reviews, and records evidence.
Codex executes repo changes, verifies locally, and owns git/PR handoff.
Richard approves high-risk actions.

## Known Repo State At Start

- Repo path: `/Users/richardzhang/.hermes/hermes-agent`
- Branch observed at start of P0.0: `main`
- Local branch was behind `origin/main` by 30 commits.
- Existing untracked files were present before P0.0 and must not be modified by
  this workflow slice.

## Next Bounded Step

P1 Deterministic Model Router should stay policy-driven: LLMs may advise route
choices, but deterministic policy code must enforce the final route.
