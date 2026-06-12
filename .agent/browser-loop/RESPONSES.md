# Browser LLM Responses

Status: response-captured
Last updated: 2026-06-12

## P1 Deterministic Model Router Review

Status: response-captured
Request file:

- `.agent/browser-loop/REQUESTS.md`
Source URL:

- `https://chatgpt.com/g/g-p-6a25c0156164819199b96293b59e675a-codex-and-system/c/6a2c5eea-87dc-83ea-b2f3-2fbd5a80e316`

Access honesty:

- Codex claimed and read the matching ChatGPT tab in Chrome.
- Codex did not send a new prompt in this slice.
- The captured response came from an existing Richard-provided ChatGPT
  conversation URL.
- Browser LLM output remains advisory until reconciled with `.agent` state and
  verified repo evidence.

Captured responses:

- ChatGPT recommended splitting P1 into `P1.0 Router Safety Core, offline only`
  before any provider adapters.
- P1.0 recommended scope: deterministic secret scanner, local LLM sensitivity
  classifier wrapper, S0-S4/R0-R4 policy engine, local budget ledger, route
  explanation, and tests.
- P1.1 recommended scope: provider adapters, model availability probe, rate
  limiter, cache telemetry, and no bypass around scanner/policy/budget.
- Security recommendation accepted as advisory: deterministic regex/entropy
  secret scanning must run before any local LLM classifier.
- Budget recommendation accepted as advisory: pre-call budget estimation and
  enforcement should happen before any provider call.
- Model/pricing claims about Gemini versions, batch pricing, and context
  caching are not locally verified in this slice. Treat them as requiring
  official Google documentation or live `models.list` verification before
  implementation.
- ChatGPT's final advisory decision: accept deterministic scanner before local
  LLM, accept batch/cache as budget multipliers, accept Gemini 3.5 Flash as a
  possible stable escalation lane only after verification, do not switch to
  `gemini-3.1-pro` until `models.list` confirms it, keep preview fallback until
  verified, and build scanner/classifier/policy/budget ledger offline before
  Gemini adapter.
