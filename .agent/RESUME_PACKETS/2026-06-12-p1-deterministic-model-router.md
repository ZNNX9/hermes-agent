# LLM Session Resume Packet

## Target LLM Platform
Unknown / ChatGPT / Claude / Gemini / Grok / DeepSeek / Perplexity / Other

## Platform Capability Notes
- Branching: unknown; do not claim native branch support without browser evidence.
- Projects/Folders: unknown; local `.agent/` is the durable source of truth.
- File Upload: optional; use sanitized excerpts only.
- Durable Memory: do not rely on hidden memory.
- Pinned Instructions: unknown.
- Browser Automation Status: prepared packet only; not browser-applied.

## Re-Sync Status
- Last Packet Reviewed: `.agent/PROJECT_STATE.md`, `.agent/TASK_QUEUE.md`, `.agent/BRANCH_LOG.md`, `.agent/CODEX_REPORT.md`
- Latest Previous-Chat Source Reviewed: local `.agent` files and current Codex chat context only
- Previous-Chat Review Status: previous-chat-reviewed for local `.agent`; browser ChatGPT tail not reviewed in this slice
- Context Drift Detected: yes; P0.1 is now committed as `c7979d945`
- Packet Updated: yes
- Remaining Conflicts: none for workflow prep; P1 runtime still requires explicit Richard start

## Project / Topic
Hermes OS / P1 Deterministic Model Router

## Session Purpose
Prepare an implementation-ready design review for deterministic model routing
without authorizing code changes yet.

## Current State
- Repo: `/Users/richardzhang/.hermes/hermes-agent`
- Branch: `codex/hermes-os-p0-workflow-backbone`
- Latest relevant commit: `c7979d945 Add Hermes runtime health JSON doctor`
- P0.1 added `hermes doctor --json` and verified authenticated local API smoke.
- P1 is prepared in `.agent/TASK_QUEUE.md` but not started.

## Non-Negotiable Constraints
- Existing Hermes system upgrade, not a rebuild.
- Codex is the executor; Hermes/GPT/Claude can advise or review.
- LLM route suggestions are advisory. Deterministic policy must enforce final routing.
- No secrets, `.env`, auth files, provider keys, browser profiles, keychains, broker/wallet data, or child/family raw data go to low-trust lanes.
- No runtime/test/dependency/CI/config/service/deploy changes until Richard explicitly starts P1.
- Browser LLM output is not execution evidence.

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

## Changes Since Last Packet
- Added: P0.1 commit `c7979d945`.
- Added: P1 detailed queue card and this resume packet.
- Changed: P0.1 report now records the real commit hash.
- Removed / Rejected: starting P1 runtime implementation from vague approval.
- Still Valid: P1 must be policy-driven and receipt-gated.

## Open Decisions
- Exact P1 route policy schema and file set.
- Whether P1 starts with policy-only dry-run/explain mode before enforcement.
- Whether P1 router evidence validation remains manual CLI first or later gains hooks.
- Which existing Hermes config/provider modules are in scope for P1.

## Conflict Log
- Conflict: none.
- Older Packet Said: P1 was only queued.
- Latest Richard Update Said: "Go ahead with some updates" plus `$richard-ai-workflow`.
- Resolution: workflow-only preparation is allowed; P1 runtime is not started.
- Needs Richard Decision: explicit start of P1 runtime implementation.

## Next Best Action
Ask a reviewer model for a design critique of the P1 deterministic router task
card, then have Codex implement only after Richard explicitly starts P1.

## Do Not Repeat
- Do not re-open P0.1 as if it is uncommitted.
- Do not treat browser LLM advice as approval.
- Do not send secrets or raw config payloads to browser/cloud reviewers.
- Do not make dashboard UI before CLI/task/receipt loop is accepted.
- Do not push this branch until the queued batch policy says to push.

## Exact First Prompt for New Session
Review this Hermes OS P1 deterministic model router plan as an advisory reviewer only. Do not claim local execution, do not approve runtime changes, and do not request secrets. The source of truth is the `.agent` workflow state summarized below:

- Hermes is the control plane; Codex executes repo changes and verifies locally.
- P0.1 is complete at commit `c7979d945`, adding `hermes doctor --json` with gateway runtime, authenticated `/v1/models`, chat smoke, listener exposure, launchd freshness, secret-safety, and receipt checks.
- P1 is not started. It should design deterministic route policy where model suggestions are advisory and policy code enforces final routes.
- Required constraints: no S3/S4 data to DeepSeek or low-trust cloud lanes; no secrets/raw logs/browser profiles; no service/deploy/network exposure changes; evidence receipts required.

Please critique the P1 task card and propose a minimal implementation sequence, expected file boundaries, tests, stop conditions, and risk controls. Keep the answer in structured sections: concerns, recommended scope, tests, non-goals, and acceptance criteria.
