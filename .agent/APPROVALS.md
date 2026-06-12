# Approvals

Status: prepared
Last updated: 2026-06-12

This file records explicit human approvals for high-risk actions. Absence of an
approval means no approval has been granted.

## Standing Approvals

### A-001: P0.0 Workflow Backbone

Approved by: Richard
Date: 2026-06-12
Scope:

- Create workflow-only `.agent/` scaffolding for Hermes/Codex coordination.
- Use `richard-ai-workflow` for questions and feedback.

Not approved:

- Runtime code changes.
- Tests/dependencies/CI changes.
- Secrets or app config changes.
- Deployment or network exposure changes.
- Destructive git operations.

### A-002: P0.0a Current Chat Review And Handoff

Approved by: Richard
Date: 2026-06-12
Scope:

- Review the P0.0 update against the current Codex chat and previously supplied
  GPT shared-chat context.
- Continue with `$richard-ai-workflow`.
- Record drift, access honesty, and the next bounded handoff under `.agent`.

Not approved:

- Runtime code changes.
- Tests/dependencies/CI changes.
- Secrets or app config changes.
- Deployment or network exposure changes.
- Claiming a browser LLM response was captured unless a live browser action
  actually happened.

### A-003: P0.1 Runtime Health Baseline

Approved by: Richard
Date: 2026-06-12
Trigger:

- Richard sent `P0.1` after the task queue identified P0.1 as the next
  approval-gated slice.

Scope:

- Add `hermes doctor --json` as a read-only health-report path.
- Add tests for parser support, config-missing skip behavior, authenticated API
  smoke behavior, and secret-safe output.
- Use existing API server config only to perform local authenticated
  `/v1/models` and chat smoke checks.

Not approved:

- Editing `.env`, `config.yaml`, auth files, provider keys, browser profiles,
  or keychains.
- Changing service binding, Tailscale/LAN exposure, LaunchAgent definitions,
  deployment, or production runtime config.
- Adding multi-model routing behavior.

## Required Future Approvals

Richard approval is required before:

- P1 changes deterministic routing, provider selection, or model policy.
- Any task touches secrets, `.env`, auth, provider keys, broker/wallet data, or
  browser profiles.
- Any service binding, Tailscale/LAN exposure, LaunchAgent, deploy, release, or
  production config changes.
- Any live trading, money movement, kids/family permissions, or outbound
  customer/family/public communication.
- Any destructive git operation or force-push.
