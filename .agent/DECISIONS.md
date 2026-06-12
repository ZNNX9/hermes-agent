# Hermes OS Decisions

Status: prepared
Last updated: 2026-06-12

## Accepted Decisions

### D-001: Hermes Is Control Plane, Not Main Executor

Hermes coordinates intake, routing, review, context packs, task state, and
evidence receipts. Codex remains the primary repo executor and local verifier.

### D-002: Discussion Happens Through Artifacts

Agents do not hold unbounded group chats. They exchange structured artifacts:
task cards, proposals, critiques, adjudication notes, execution receipts, and
approval records.

### D-003: Deterministic Policy Beats Model Preference

A model may suggest a route, but deterministic policy decides whether data may
leave the machine, which model/tool may receive it, and whether Richard must
approve.

### D-004: Context Packs Are Bounded And Sanitized

Every serious agent call should receive a task-specific context pack. Raw logs,
secrets, browser profiles, and oversized transcripts must not be copied into a
prompt by default.

### D-005: Evidence Receipts Are Required For Acceptance

Work is not accepted just because an agent says it is done. A receipt must list
files read, files changed, commands run, results, risks, and whether sensitive
surfaces were touched.

### D-006: Browser LLM Output Is Advisory

ChatGPT, Claude, Gemini, DeepSeek, and other browser LLM plans are review or
planning inputs. They are not authoritative unless captured into `.agent`,
checked against repo state, and accepted by Richard or Codex under policy.

### D-007: This Is An Existing-System Upgrade

The Hermes OS effort upgrades the existing Hermes repository and runtime
ecosystem. It does not replace Hermes with a new agent system. New workflow,
diagnostics, routing, and evidence layers should integrate with existing CLI,
gateway, profile, kanban, skill, and plugin surfaces wherever practical.

### D-008: GPT Chat Is A Review Source, Not A Controller

The shared GPT chat can supply strategy, critique, and prompts. Its useful
parts must be converted into durable `.agent` records before they guide work.
GPT chat does not directly control Hermes, approve high-risk actions, or prove
local execution.

### D-009: Runtime Work Starts As A Separate Ticket

P0.1 may touch runtime behavior, tests, CLI surface, diagnostics, or app config.
It must start from its own task card, approved file set, and verification plan.

## Open Decisions

- Exact P0.1 file set and CLI surface.
- Whether P0.1 should live entirely inside existing CLI command modules or add
  a small diagnostics module.
- Whether evidence validation begins as manual CLI only or also gets a git hook.

## Rejected For Now

- Free-form multi-agent group chat as the main coordination mechanism.
- Letting DeepSeek or Gemini receive private, confidential, secret, or regulated
  payloads without policy enforcement and redaction.
- Building dashboard UI before the CLI/task/receipt loop works.
