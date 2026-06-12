# Browser LLM Requests

Status: updated
Last updated: 2026-06-12

## P1 Deterministic Model Router Review

Status: superseded-by-captured-chatgpt-response
Target: ChatGPT or Claude advisory review
Source packet:

- `.agent/RESUME_PACKETS/2026-06-12-p1-deterministic-model-router.md`

Access honesty:

- This specific prepared request was not pasted into a browser LLM.
- Richard supplied an existing ChatGPT conversation URL instead.
- Codex captured the response from that existing thread and recorded it in
  `.agent/browser-loop/RESPONSES.md`.
- Browser LLM output remains advisory until reconciled with `.agent` state and
  verified repo evidence.

Superseded copy/paste prompt:

```text
Review this Hermes OS P1 deterministic model router plan as an advisory reviewer only. Do not claim local execution, do not approve runtime changes, and do not request secrets. The source of truth is the `.agent` workflow state summarized below:

- Hermes is the control plane; Codex executes repo changes and verifies locally.
- P0.1 is complete at commit `c7979d945`, adding `hermes doctor --json` with gateway runtime, authenticated `/v1/models`, chat smoke, listener exposure, launchd freshness, secret-safety, and receipt checks.
- P1 is not started. It should design deterministic route policy where model suggestions are advisory and policy code enforces final routes.
- Required constraints: no S3/S4 data to DeepSeek or low-trust cloud lanes; no secrets/raw logs/browser profiles; no service/deploy/network exposure changes; evidence receipts required.

Please critique the P1 task card and propose a minimal implementation sequence, expected file boundaries, tests, stop conditions, and risk controls. Keep the answer in structured sections: concerns, recommended scope, tests, non-goals, and acceptance criteria.
```

## P1.0 Offline Router Safety Core Follow-Up

Status: prepared-not-sent
Target: ChatGPT or Claude advisory review

Copy/paste prompt:

```text
Review this Hermes OS P1.0 offline router safety core plan as an advisory reviewer only. Do not claim local execution, do not approve runtime changes, and do not request secrets. The source of truth is the local `.agent` workflow state summarized below:

- Hermes is the control plane; Codex executes repo changes and verifies locally.
- P0.1 is complete at commit `c7979d945`, adding `hermes doctor --json` with gateway runtime, authenticated `/v1/models`, chat smoke, listener exposure, launchd freshness, secret-safety, and receipt checks.
- P1 is not started. Captured ChatGPT advice split P1 into P1.0 offline router safety core and deferred P1.1 provider adapters.
- P1.0 should include deterministic secret scanner before local LLM classifier, local classifier wrapper, S0-S4/R0-R4 policy engine, pre-call budget ledger, route explanation, and tests.
- P1.1 should add provider adapters only after P1.0 passes.
- Required constraints: no S3/S4 data to DeepSeek or low-trust cloud lanes; no secrets/raw logs/browser profiles; no service/deploy/network exposure changes; no external provider calls; evidence receipts required.
- Gemini model IDs/pricing are not accepted unless official docs or live `models.list` verifies them.

Please critique the P1.0 task card and propose minimal file boundaries, tests, stop conditions, and risk controls. Keep the answer in structured sections: concerns, recommended scope, tests, non-goals, and acceptance criteria.
```
