from hermes_agent.router_core.secret_scan import redact, scan_text


SECRET_FIXTURES = {
    "openai_key": "sk-abcdefghijklmnopqrstuvwxyzABCDEF123456",
    "openai_project_key": "sk-proj-abcdefghijklmnopqrstuvwxyzABCDEF1234567890",
    "aws_access_key": "AKIAIOSFODNN7EXAMPLE",
    "google_api_key": "AIzaSyA1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p",
    "github_token": "ghp_abcdefghijklmnopqrstuvwxyzABCDEF123456",
    "github_pat": "github_pat_11AAAAAAA0abcdefghijklmnopqrstuvwxyzABCDEF1234567890",
    "pem_private_key": (
        "-----BEGIN PRIVATE KEY-----\n"
        "MIIEvQIBADANBgkqhkiG9w0BAQEFAASC\n"
        "-----END PRIVATE KEY-----"
    ),
    "telegram_bot_token": "123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi",
    "env_secret": "PAYMENT_API_TOKEN=qzW9XkLmN8pQrStUvWxYz123456789AB",
    "bip39_phrase": (
        "abandon ability able about above absent absorb abstract absurd abuse access accident"
    ),
}


def test_all_pattern_fixtures_detected_and_redacted():
    for expected_type, secret in SECRET_FIXTURES.items():
        result = scan_text(f"before {secret} after")

        assert any(finding.type == expected_type for finding in result.findings)
        assert secret not in result.redacted_text
        assert f"[REDACTED:{expected_type}:" in result.redacted_text


def test_redaction_is_idempotent():
    text = (
        f"{SECRET_FIXTURES['openai_key']} "
        f"{SECRET_FIXTURES['github_token']} "
        f"{SECRET_FIXTURES['env_secret']}"
    )

    once = redact(text)
    twice = redact(once)

    assert twice == once


def test_entropy_detector_flags_high_entropy_tokens_but_not_prose_or_uuids():
    token = "qW8zR4tYpL9mN2bVcX7sA1dFhJ6kU3eG"
    uuid = "550e8400-e29b-41d4-a716-446655440000"
    prose = "this sentence is ordinary prose with repeated human words"

    result = scan_text(f"{token} {uuid} {prose}")

    assert any(f.type == "high_entropy_token" and f.value == token for f in result.findings)
    assert uuid not in [f.value for f in result.findings]
    assert prose not in [f.value for f in result.findings]


def test_no_full_secret_value_in_redacted_output():
    for secret in SECRET_FIXTURES.values():
        redacted = redact(secret)

        assert secret not in redacted
        assert "[REDACTED:" in redacted
