# P1.0 Router Safety Core

This package is an offline-only safety core under `hermes_agent/router_core/`.
It does not create provider adapters, network clients, service hooks, runtime
configuration, or dependency changes.

## Pipeline Contract

The routing pipeline is:

1. `secret_scan.scan_text(raw_input)`
2. pass only `ScanResult.redacted_text` to a `LocalClassifier`
3. clamp classifier sensitivity upward with scanner-implied sensitivity
4. apply `policy.decide(sensitivity, risk, target_provider)`
5. optionally reserve budget in `ledger.BudgetLedger`
6. emit `explain.build_explanation(...)`

Scanner output is authoritative for secrets. A classifier may raise sensitivity
or risk, but may never lower scanner-implied sensitivity. Classifier error or
timeout fails closed with `Decision.REQUIRE_LOCAL_ONLY`.

## Policy Matrix

Unknown sensitivity enum, risk enum, or provider returns `DENY`.

Known providers:

- Cloud: `deepseek`, `gemini`, `openai`, `openai_codex`
- Local: `local`

Decision order:

| Condition | Decision |
| --- | --- |
| `R4_CRITICAL` | `REQUIRE_HUMAN_APPROVAL` |
| `S4_SECRET` | `REQUIRE_LOCAL_ONLY` |
| `S3_CONFIDENTIAL` and provider `deepseek` | `DENY` |
| `R3_HIGH` and cloud provider other than `openai_codex` | `DENY` |
| `S3_CONFIDENTIAL` and other cloud provider | `REQUIRE_HUMAN_APPROVAL` |
| `S2_INTERNAL` and provider `deepseek` | `REQUIRE_REDACTION` |
| `S0_PUBLIC`, `S1_LOW`, or remaining allowed local/cloud cases | `ALLOW` |

The `R4_CRITICAL` rule is evaluated before `S4_SECRET` because it requires a
human gate regardless of provider choice.

## Secret Scanner

`secret_scan.py` deterministically detects and redacts:

- OpenAI keys beginning `sk-` or `sk-proj-`
- AWS access keys beginning `AKIA`
- Google API keys beginning `AIza`
- GitHub `ghp_` and `github_pat_` tokens
- PEM private key blocks
- Telegram bot tokens
- `.env` style `KEY=value` pairs with secret-looking key names or high-entropy values
- BIP39-style 12/24 word seed phrases
- standalone high-entropy tokens, excluding prose, UUIDs, and plain hex-like IDs

Redaction replaces findings with:

```text
[REDACTED:<type>:<sha256_hex_prefix_8>]
```

Redaction is idempotent. Downstream components should not receive raw input
after scanning.

## Explanation Schema

`explain.build_explanation(...)` returns a dict with these keys:

```json
{
  "input_hash": "sha256 hex of raw input",
  "sensitivity": "S0_PUBLIC",
  "risk": "R0_TRIVIAL",
  "decision": "ALLOW",
  "target_provider": "openai",
  "reasons": ["policy reason"],
  "redaction_count": 0,
  "clamp_applied": false,
  "budget": {
    "estimated_cost": 0.0,
    "daily_spent": 0.0,
    "monthly_spent": 0.0,
    "caps": {}
  },
  "timestamp": "caller supplied timestamp"
}
```

The explanation must never include raw input text, raw secrets, or provider
payloads. The caller supplies the timestamp so tests and receipts can remain
deterministic.

## Budget Ledger

`ledger.BudgetLedger` stores only provider, model, period, estimated cost,
actual cost, status, and timestamp in sqlite3. It does not store prompt text or
redacted prompt text.

`estimate_cost(...)` uses a `len(text) / 4` token heuristic plus
`max_output_tokens`, with prices supplied through an injected table. The bundled
`prices_placeholder.PRICE_TABLE` is marked `UNVERIFIED_PLACEHOLDER`; real prices
require official pricing docs plus live `models.list` verification before P1.1.
