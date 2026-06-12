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

Status: prepared, awaiting explicit Richard start
Owner: Codex after Richard approval
Scope: deterministic policy engine, sensitivity/risk classifier, route explain,
provider-adapter boundary, and cache rules
Risk: R3
Sensitivity: S3/S4 possible; treat as S4 until the approved file set and data
surfaces are narrowed

Objective:

Add deterministic routing so Hermes can recommend and enforce which model or
agent lane may receive a task, based on sensitivity, risk, context size,
provider capability, and approval requirements.

Hard rule:

LLMs may recommend routes. Policy code must enforce routes.

Not started:

- No runtime router code is approved by this workflow update.
- No tests, dependencies, CI, provider config, API keys, LaunchAgent/service
  config, or model routes are approved by this workflow update.

Required context before implementation:

- `.agent/PROJECT_STATE.md`
- `.agent/DECISIONS.md`
- `.agent/INTELLIGENCE_ROUTING.md`
- `.agent/HERMES_OS_POLICY.md`
- `.agent/AGENT_ROLES.md`
- `.agent/EVIDENCE_RECEIPT_SCHEMA.md`
- `.agent/REVIEW_CHECKLIST.md`
- `.agent/RESUME_PACKETS/2026-06-12-p1-deterministic-model-router.md`
- P0.1 commit `c7979d945`

Candidate acceptance gates:

- Router decisions are explainable without exposing secret values.
- S3/S4 tasks cannot route to DeepSeek or other low-trust cloud lanes.
- Local/Qwen/Ollama can provide short classification hints but cannot override
  policy.
- GPT/Codex remains the primary high-risk engineering lane.
- Hermes advisory output is never accepted as local execution evidence.
- Tests use `scripts/run_tests.sh` if implementation touches Python tests.

Stop conditions:

- P1 needs secrets, `.env`, auth files, provider keys, browser profiles, or
  keychains.
- P1 changes network exposure, service binding, deployment, LaunchAgent, or
  production runtime config.
- P1 requires provider behavior changes outside the approved file set.
- P1 conflicts with unrelated uncommitted files.
