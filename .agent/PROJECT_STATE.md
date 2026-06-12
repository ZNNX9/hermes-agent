# Hermes OS Project State

Status: prepared
Last updated: 2026-06-12
Owner: Richard
Active topic: Hermes/Codex control-plane workflow backbone

## Purpose

This `.agent` directory is the workflow source of truth for Richard's local
Hermes/Codex operating model. It records scoped task state, decisions, evidence
requirements, approval gates, and model/agent roles before runtime code is
changed.

## Current Slice

Ticket: P0.0 Hermes/Codex Workflow Backbone
Status: completed
Scope: workflow-only docs under `.agent/`
Runtime changes: none
Tests/dependencies/CI changes: none
Secrets/app config changes: none

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

P0.1 Runtime Health Baseline should implement `hermes doctor --json`, an
authenticated `/v1/models` check, a real chat smoke, launchd/listener safety
checks, secret scanning, and a receipt validator. P0.1 is runtime work and must
start from a fresh task card and verification plan.
