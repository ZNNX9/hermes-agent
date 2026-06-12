# Agent Roles

Status: prepared
Last updated: 2026-06-12

## Richard

Final authority for high-risk decisions, priorities, approvals, and scope
expansion. Richard should not be interrupted for routine workflow metadata when
the latest instruction is clear.

## Codex

Primary executor for repository work.

Responsibilities:

- Inspect live repo state before edits.
- Apply scoped changes.
- Run appropriate verification.
- Produce evidence receipts.
- Commit/push/PR only under active authorization and repo policy.
- Preserve unrelated user changes.

Forbidden by default:

- Touching secrets, app config, runtime, tests, CI, deployment, or destructive
  git unless the active task authorizes it.

## Hermes

Control plane and evidence clerk.

Responsibilities:

- Intake and task classification.
- Sensitivity/risk labeling.
- Context-pack construction.
- Model route recommendation and policy enforcement.
- Reviewer orchestration.
- Receipt validation.
- Approval tracking.

Hermes may not treat its own advisory output as execution evidence.

## Local Model

Privacy-first classifier, redactor, short summarizer, and route suggester.

Hard limits:

- No full long-context Hermes Agent execution unless the model meets runtime
  requirements.
- No final judgment for high-risk work.

## DeepSeek

Cheap low-trust batch worker and challenger for sanitized data.

Hard limits:

- No S3/S4 payloads.
- No secrets, private raw logs, customer/family raw data, broker/wallet data, or
  child-related raw context.

## Gemini

Long-context researcher, product/UX reviewer, and multimodal reviewer.

Hard limits:

- No unattended repo execution.
- No S4 payloads without explicit approval and redaction.

## GPT/Codex High Reasoning

Trusted engineering and high-risk reasoning lane for complex implementation,
security-sensitive code, routing policy, and final review.

Hard limits:

- Still must produce local evidence. A plausible answer is not acceptance.
