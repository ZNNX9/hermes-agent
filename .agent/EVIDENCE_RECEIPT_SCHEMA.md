# Evidence Receipt Schema

Status: prepared
Last updated: 2026-06-12

Every completed task should produce a receipt. Until a validator exists, this
schema is the manual gate.

## Receipt Template

```yaml
task_id:
status: completed | partial | blocked | failed
agent:
model_or_surface:
repo_path:
branch:
commit:

scope:
  requested:
  completed:
  out_of_scope_not_done:

files:
  read:
  changed:
  created:
  deleted:
  not_touched_unrelated:

commands:
  - command:
    purpose:
    result: passed | failed | skipped
    evidence:

security:
  secrets_read: false
  secrets_printed: false
  env_files_touched: false
  network_exposure_changed: false
  deployment_changed: false
  destructive_git_used: false

policy:
  sensitivity_level:
  risk_level:
  richard_approval_required: false
  approval_reference:

validation:
  tests:
  lint:
  build:
  smoke:
  receipt_check:

remaining_risks:
next_recommended_task:
```

## Minimum Acceptance

A receipt is incomplete if it omits:

- Files changed.
- Commands run and results.
- Whether secrets or network exposure were touched.
- Remaining risks.
- Whether Richard approval was required.

## Evidence Honesty

Use precise labels:

- `live`: command or API call actually ran in the current environment.
- `local-file`: verified from local files only.
- `browser-context`: visible in browser or shared chat, not terminal-verified.
- `memory-derived`: recalled from Codex memory, may be stale.
- `advisory`: model recommendation without execution evidence.
- `skipped`: not run, with reason.
