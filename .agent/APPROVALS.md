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

## Required Future Approvals

Richard approval is required before:

- P0.1 changes runtime or CLI behavior.
- Any task touches secrets, `.env`, auth, provider keys, broker/wallet data, or
  browser profiles.
- Any service binding, Tailscale/LAN exposure, LaunchAgent, deploy, release, or
  production config changes.
- Any live trading, money movement, kids/family permissions, or outbound
  customer/family/public communication.
- Any destructive git operation or force-push.
