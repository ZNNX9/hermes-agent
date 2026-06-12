# LLM Session Resume Packet

## Target LLM Platform
Unknown / ChatGPT / Claude / Gemini / Grok / DeepSeek / Perplexity / Other

## Platform Capability Notes
- Branching: unknown; do not claim native branch support without browser evidence.
- Projects/Folders: unknown; local `.agent/` is the durable source of truth.
- File Upload: optional; use sanitized excerpts only.
- Durable Memory: do not rely on hidden memory.
- Pinned Instructions: unknown.
- Browser Automation Status: ChatGPT tab read-only captured on 2026-06-12; no prompt sent.

## Re-Sync Status
- Last Packet Reviewed: `.agent/PROJECT_STATE.md`, `.agent/TASK_QUEUE.md`, `.agent/BRANCH_LOG.md`, `.agent/CODEX_REPORT.md`, `.agent/browser-loop/RESPONSES.md`
- Latest Previous-Chat Source Reviewed: local `.agent` files, current Codex chat context, and Richard-supplied ChatGPT URL
- Previous-Chat Review Status: previous-chat-reviewed for local `.agent`; response-captured from ChatGPT browser tab
- Context Drift Detected: yes; P1 should split into offline P1.0 and deferred P1.1
- Packet Updated: yes
- Remaining Conflicts: none for workflow prep; P1 runtime still requires explicit Richard start and Gemini model facts require official verification

## Project / Topic
Hermes OS / P1.0 Offline Router Safety Core

## Session Purpose
Prepare an implementation-ready design review for offline router safety core
implementation without authorizing code changes yet.

## Current State
- Repo: `/Users/richardzhang/.hermes/hermes-agent`
- Branch: `codex/hermes-os-p0-workflow-backbone`
- Latest relevant commits: `c7979d945`, `37b36b6e2`, `509771ae8`
- P0.1 added `hermes doctor --json` and verified authenticated local API smoke.
- P1 is prepared and locked in `.agent/TASK_QUEUE.md` and `.agent/LOCKS.json`,
  but not started.
- ChatGPT browser review recommends P1.0 offline safety core first, with
  provider adapters deferred to P1.1.

## Non-Negotiable Constraints
- Existing Hermes system upgrade, not a rebuild.
- Codex is the executor; Hermes/GPT/Claude can advise or review.
- LLM route suggestions are advisory. Deterministic policy must enforce final routing.
- No secrets, `.env`, auth files, provider keys, browser profiles, keychains, broker/wallet data, or child/family raw data go to low-trust lanes.
- No runtime/test/dependency/CI/config/service/deploy changes until Richard explicitly starts P1.
- Browser LLM output is not execution evidence.
- Deterministic secret scanning must run before any local LLM classifier.
- Browser claims about Gemini model IDs/prices need official docs or live
  `models.list` verification before use.

## Active Files / Repo / Branch
- `.agent/PROJECT_STATE.md`
- `.agent/TASK_QUEUE.md`
- `.agent/DECISIONS.md`
- `.agent/INTELLIGENCE_ROUTING.md`
- `.agent/HERMES_OS_POLICY.md`
- `.agent/AGENT_ROLES.md`
- `.agent/EVIDENCE_RECEIPT_SCHEMA.md`
- `.agent/REVIEW_CHECKLIST.md`
- `.agent/CODEX_REPORT.md`
- Branch: `codex/hermes-os-p0-workflow-backbone`

## Verification / Tests
- P0.1 verification passed: `scripts/run_tests.sh tests/hermes_cli/test_doctor_json.py tests/hermes_cli/test_doctor.py tests/hermes_cli/test_doctor_command_install.py tests/hermes_cli/test_gateway_runtime_health.py`
- Result: 78 passed, 0 failed.
- P0.1 live smoke passed via `.venv/bin/python ./hermes doctor --json`.
- Current P1 prep is workflow-only; verify by diff scope and `git diff --check`.

## Decisions Already Made
- Hermes is the control plane, not the main executor.
- Agents exchange structured artifacts, not unbounded group chat.
- Deterministic policy beats model preference.
- Context packs are bounded and sanitized.
- Evidence receipts are required for acceptance.
- Browser LLM output is advisory.
- Hermes OS is an existing-system upgrade.
- GPT chat is a review source, not a controller.
- P0.1 health baseline is the router gate.
- P1 starts with P1.0 offline router safety core.
- Provider adapters are deferred to P1.1.

## Changes Since Last Packet
- Added: P0.1 commit `c7979d945`.
- Added: P1 prep commit `37b36b6e2` and P1 lock commit `509771ae8`.
- Added: ChatGPT browser response capture from Richard's supplied URL.
- Changed: P1 is now split into P1.0 offline router safety core and deferred
  P1.1 provider adapters.
- Removed / Rejected: starting provider adapters before offline scanner/policy/
  budget tests pass.
- Still Valid: P1 must be policy-driven and receipt-gated.

## Open Decisions
- Exact P1.0 route policy schema and file set.
- Whether route explanation starts as a CLI command or fixture helper.
- Whether P1 router evidence validation remains manual CLI first or later gains hooks.
- Which existing Hermes modules are in scope for P1.0.
- Official provider model/pricing verification source before P1.1.

## Conflict Log
- Conflict: none.
- Older Packet Said: P1 was deterministic model router as one broad task.
- Latest Richard Update Said: continue with `$richard-ai-workflow` and supplied ChatGPT conversation URL.
- Resolution: captured ChatGPT response, split P1 into P1.0 offline safety core and P1.1 provider adapters; P1 runtime is still not started.
- Needs Richard Decision: explicit start of P1 runtime implementation.

## Next Best Action
Use the captured browser review to prepare P1.0 offline router safety core.
Codex should implement only after Richard explicitly starts P1.0 and approved
files are listed.

## Do Not Repeat
- Do not re-open P0.1 as if it is uncommitted.
- Do not treat browser LLM advice as approval.
- Do not send secrets or raw config payloads to browser/cloud reviewers.
- Do not make dashboard UI before CLI/task/receipt loop is accepted.
- Do not push this branch until the queued batch policy says to push.
- Do not adopt new Gemini model IDs/prices without official verification.
- Do not build provider adapters in P1.0.

## Exact First Prompt for New Session
Review this Hermes OS P1.0 offline router safety core plan as an advisory reviewer only. Do not claim local execution, do not approve runtime changes, and do not request secrets. The source of truth is the `.agent` workflow state summarized below:

- Hermes is the control plane; Codex executes repo changes and verifies locally.
- P0.1 is complete at commit `c7979d945`, adding `hermes doctor --json` with gateway runtime, authenticated `/v1/models`, chat smoke, listener exposure, launchd freshness, secret-safety, and receipt checks.
- P1 is not started. Captured browser advice split P1 into P1.0 offline router safety core and deferred P1.1 provider adapters.
- P1.0 should include deterministic secret scanner before local LLM classifier, local classifier wrapper, S0-S4/R0-R4 policy engine, pre-call budget ledger, route explanation, and tests.
- P1.1 should add provider adapters only after P1.0 passes.
- Required constraints: no S3/S4 data to DeepSeek or low-trust cloud lanes; no secrets/raw logs/browser profiles; no service/deploy/network exposure changes; evidence receipts required.
- Gemini model IDs/pricing are not accepted unless official docs or live `models.list` verifies them.

Please critique the P1.0 task card and propose minimal file boundaries, tests, stop conditions, and risk controls. Keep the answer in structured sections: concerns, recommended scope, tests, non-goals, and acceptance criteria.
