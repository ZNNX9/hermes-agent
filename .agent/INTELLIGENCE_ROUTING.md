# Intelligence Routing

Status: prepared
Last updated: 2026-06-12

## Default Rule

Use the lowest sufficient intelligence only when the task is deterministic,
workflow-only, and verifiable. Use higher reasoning for runtime behavior,
security, privacy, deployment, trading, kids/family permissions, database/model
behavior, provider routing, tests, CI, dependencies, merge conflicts, or unclear
architecture.

## Model And Agent Lanes

| Lane | Use For | Do Not Use For |
|---|---|---|
| Local/Qwen/Ollama | short classification, redaction, routing hints, local summaries | full Hermes Agent execution, long context, secrets adjudication |
| DeepSeek | cheap sanitized batch critique, boilerplate review, low-trust summaries | S3/S4 data, raw logs with tokens, kids/family raw data, customer data, secrets |
| Gemini | long-context research, product synthesis, UX review, multimodal review | unattended repo execution, S4 payloads without explicit approval |
| GPT/Codex | real engineering, high-risk reasoning, security-sensitive code, final implementation | bulk low-risk summarization that can be safely delegated |
| Hermes | moderator, policy router, context-pack builder, evidence clerk, reviewer coordinator | pretending advisory output is local execution evidence |
| Richard | final authority for high-risk approvals | routine deterministic workflow metadata |

## Sensitivity Labels

| Level | Label | Cloud Rule |
|---|---|---|
| S0 | Public | Cloud allowed |
| S1 | Internal low-risk | Cloud allowed selectively |
| S2 | Private | GPT/Codex or Gemini only after minimization/redaction |
| S3 | Confidential | Local or GPT/Codex only; no DeepSeek |
| S4 | Secret/regulated | Local only unless Richard explicitly approves a redacted exception |

## Risk Labels

| Level | Examples | Required Route |
|---|---|---|
| R0 | rewrite, translate, summarize | local or DeepSeek if data allows |
| R1 | docs, simple tests, non-critical UI | DeepSeek/local, Codex if needed |
| R2 | normal app feature | Codex primary, optional reviewer |
| R3 | security, auth, routing, TradeBot validation, KidsAgents permissions | Codex/GPT primary plus independent review and receipt |
| R4 | deployment, secrets, live trading, customer/family outbound action | Richard approval mandatory |

## Escalation Rule

Escalate only when allowed by both sensitivity policy and risk policy.

```text
Local -> DeepSeek -> Gemini/GPT -> Codex -> Richard
```

The ladder is not automatic. S3/S4 or R4 constraints can skip or block cheaper
lanes.
