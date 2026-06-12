# Hermes OS Project State

Status: P1.0 prepared and locked, not started
Last updated: 2026-06-12
Owner: Richard
Active topic: P1.0 offline router safety core planning

## Purpose

This `.agent` directory is the workflow source of truth for Richard's local
Hermes/Codex operating model. It records scoped task state, decisions, evidence
requirements, approval gates, and model/agent roles before runtime code is
changed.

## Current Slice

Ticket: P1 ChatGPT Router Review Capture
Status: completed
Scope: workflow-only browser response capture and P1.0/P1.1 planning split
Runtime changes: none in this slice
Tests/dependencies/CI changes: none
Secrets/app config changes: none in this slice

Evidence:

- P0.1 was committed as `c7979d945 Add Hermes runtime health JSON doctor`.
- `scripts/run_tests.sh tests/hermes_cli/test_doctor_json.py tests/hermes_cli/test_doctor.py tests/hermes_cli/test_doctor_command_install.py tests/hermes_cli/test_gateway_runtime_health.py`
  passed 78 tests during P0.1.
- `.venv/bin/python ./hermes doctor --json` returned JSON with
  `api_models=ok`, `chat_smoke=ok`, `gateway_runtime=ok`,
  `listener_exposure=ok`, `secret_scan=ok`, and `receipt_validator=ok` during
  P0.1.
- The same smoke returned `launchd_definition=warn` because the installed local
  launchd plist is not current.
- P1 has a workflow-only resume packet at
  `.agent/RESUME_PACKETS/2026-06-12-p1-deterministic-model-router.md`.
- P1 has a prepared, not-sent browser review request at
  `.agent/browser-loop/REQUESTS.md`.
- P1 preparation metadata was committed as
  `37b36b6e2 Prepare P1 router workflow packet`.
- P1 browser responses and UI issue ledgers exist and explicitly record that no
  browser response has been captured in this slice.
- `.agent/LOCKS.json` records that P1 runtime implementation remains blocked
  until Richard explicitly starts it.
- Codex captured a read-only ChatGPT response from Richard's supplied URL and
  recorded it in `.agent/browser-loop/RESPONSES.md`.
- Captured browser advice split P1 into offline `P1.0 Router Safety Core` and
  deferred `P1.1 Provider Adapter Layer`.
- Browser claims about Gemini model IDs/prices remain unverified and must not
  drive implementation until checked against official docs or live model
  availability.

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

Richard can explicitly start P1 when ready. Until then, no deterministic router
runtime code, tests, config, or provider behavior should be changed.
