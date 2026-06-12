# Hermes OS Task Queue

Status: prepared
Last updated: 2026-06-12

## Queue Rules

One Codex thread equals one bounded ticket.

Each implementation ticket must include:

- Objective.
- Approved file set.
- Forbidden areas.
- Sensitivity level.
- Risk level.
- Required context pack.
- Required verification commands.
- Required evidence receipt.
- Approval requirement.
- Stop conditions.

## Active

No active implementation ticket.

## Completed

### P0.0 Hermes/Codex Workflow Backbone

Status: completed
Owner: Codex
Scope: `.agent/` workflow docs only
Allowed files:

- `.agent/PROJECT_STATE.md`
- `.agent/TASK_QUEUE.md`
- `.agent/DECISIONS.md`
- `.agent/INTELLIGENCE_ROUTING.md`
- `.agent/HERMES_OS_POLICY.md`
- `.agent/AGENT_ROLES.md`
- `.agent/EVIDENCE_RECEIPT_SCHEMA.md`
- `.agent/REVIEW_CHECKLIST.md`
- `.agent/APPROVALS.md`

Forbidden areas:

- Runtime code.
- Tests.
- Dependencies.
- CI.
- `.env`, auth files, API keys, secrets, browser profiles, keychains.
- LaunchAgent or service config.

Acceptance:

- Workflow-only files exist and are internally consistent.
- No runtime/test/dependency/CI/secrets files changed.
- Git diff is limited to `.agent/`.
- Local commit records P0.0 if verification passes.

### P0.0a Current Chat Review And Handoff

Status: completed
Owner: Codex
Scope: `.agent/` re-sync metadata and handoff packet only
Allowed files:

- `.agent/PROJECT_STATE.md`
- `.agent/TASK_QUEUE.md`
- `.agent/DECISIONS.md`
- `.agent/APPROVALS.md`
- `.agent/BRANCH_LOG.md`
- `.agent/CHAT_HANDOFFS/2026-06-12-current-chat-review.md`
- `.agent/browser-loop/FEEDBACK_PACKETS.md`

Review result:

- Current chat clarified that the work is an existing-system upgrade, not a
  rebuild.
- GPT chat is advisory strategy/review context, not the master planner.
- P0.1 should stay a separate runtime-health ticket.

Acceptance:

- Current-chat drift is recorded.
- Browser/GPT access honesty is explicit.
- No runtime/test/dependency/CI/secrets files changed.

### P0.1 Runtime Health Baseline

Status: completed
Owner: Codex
Scope: Hermes runtime health and safety diagnostics
Risk: R3
Sensitivity: S4, because API server config/secret values were inspected for
authenticated smoke checks

Goal:

Implement a safe, diagnosable Hermes baseline before adding multi-model routing.

Candidate deliverables:

- `hermes doctor --json`
- Authenticated `/v1/models` check.
- Real chat smoke check.
- Launchd freshness check.
- Listener exposure check.
- Secret-scan helper.
- Evidence receipt validator.

Acceptance:

- `hermes doctor --json` emits a machine-readable runtime health report.
- Authenticated `/v1/models` and chat smoke checks run when API server config
  is available.
- API key values are used only for Authorization headers and are not emitted in
  the JSON report.
- Listener exposure, launchd freshness, gateway runtime, secret-safety, and
  receipt schema checks are represented.
- Related `doctor` and gateway runtime tests pass.

Observation:

- Current local launchd plist reports `current: false`; this was recorded as a
  `warn` and not repaired in P0.1.

## Next

### P1 Deterministic Model Router

Status: queued
Owner: Codex after P0.1 acceptance
Scope: deterministic policy engine, sensitivity/risk classifier, route explain,
provider-adapter boundary, and cache rules
Risk: R3

Hard rule:

LLMs may recommend routes. Policy code must enforce routes.
