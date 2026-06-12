# Review Checklist

Status: prepared
Last updated: 2026-06-12

Use this checklist before accepting any Hermes/Codex workflow or runtime ticket.

## Scope

- [ ] The task has one bounded objective.
- [ ] Approved files are listed.
- [ ] Forbidden areas are listed.
- [ ] Runtime/test/dependency/CI/config/secrets scope is explicit.
- [ ] Existing unrelated user changes are preserved.

## Policy

- [ ] Sensitivity level is assigned.
- [ ] Risk level is assigned.
- [ ] Allowed model lanes are compatible with sensitivity.
- [ ] Human approval requirement is clear.
- [ ] Browser LLM advice is labeled as advisory unless locally verified.

## Context

- [ ] Context pack is bounded.
- [ ] Secrets/raw logs/browser profiles are excluded unless explicitly approved.
- [ ] Latest repo state was checked before execution.
- [ ] Drift from older packets is recorded.

## Verification

- [ ] Required commands are listed before execution.
- [ ] Commands were run or skipped with reason.
- [ ] For Hermes Python tests, `scripts/run_tests.sh` is used when tests are in
  scope.
- [ ] Docs-only changes verify diff scope and content consistency.

## Receipt

- [ ] Files read/changed are listed.
- [ ] Commands and results are listed.
- [ ] Security fields are filled.
- [ ] Remaining risks are stated.
- [ ] Next bounded step is listed.

## Git

- [ ] Commit includes only intended files.
- [ ] Untracked or unrelated files are not accidentally staged.
- [ ] Push/PR follows active authorization and repo policy.
