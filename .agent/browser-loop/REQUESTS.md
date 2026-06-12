# Browser LLM Requests

Status: prepared
Last updated: 2026-06-12

## P1 Deterministic Model Router Review

Status: prepared-not-sent
Target: ChatGPT or Claude advisory review
Source packet:

- `.agent/RESUME_PACKETS/2026-06-12-p1-deterministic-model-router.md`

Access honesty:

- This request has not been pasted into a browser LLM in this slice.
- No browser response has been captured for P1 in this slice.
- Browser LLM output, if captured later, remains advisory until reconciled with
  `.agent` state and verified repo evidence.

Copy/paste prompt:

```text
Review this Hermes OS P1 deterministic model router plan as an advisory reviewer only. Do not claim local execution, do not approve runtime changes, and do not request secrets. The source of truth is the `.agent` workflow state summarized below:

- Hermes is the control plane; Codex executes repo changes and verifies locally.
- P0.1 is complete at commit `c7979d945`, adding `hermes doctor --json` with gateway runtime, authenticated `/v1/models`, chat smoke, listener exposure, launchd freshness, secret-safety, and receipt checks.
- P1 is not started. It should design deterministic route policy where model suggestions are advisory and policy code enforces final routes.
- Required constraints: no S3/S4 data to DeepSeek or low-trust cloud lanes; no secrets/raw logs/browser profiles; no service/deploy/network exposure changes; evidence receipts required.

Please critique the P1 task card and propose a minimal implementation sequence, expected file boundaries, tests, stop conditions, and risk controls. Keep the answer in structured sections: concerns, recommended scope, tests, non-goals, and acceptance criteria.
```
