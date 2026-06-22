from __future__ import annotations

from hermes_cli.task_policy import evaluate_task_policy, load_policy, load_starter_policy


def test_policy_blocks_forbidden_file_patterns(tmp_path):
    policy_path = tmp_path / "tradebot.yaml"
    policy_path.write_text(
        """
project: TradeBot
forbidden_actions:
  - broker access
forbidden_files:
  - ".env"
  - "config/secrets*.yaml"
""",
        encoding="utf-8",
    )

    policy = load_policy(policy_path)
    decision = evaluate_task_policy(
        policy,
        {
            "project": "TradeBot",
            "title": "Refactor dashboard",
            "allowed_files": ["config/secrets-prod.yaml"],
        },
    )

    assert decision.allowed is False
    assert "config/secrets*.yaml" in decision.reason


def test_policy_blocks_forbidden_actions_from_title(tmp_path):
    policy_path = tmp_path / "tradebot.yaml"
    policy_path.write_text(
        """
project: TradeBot
forbidden_actions:
  - live trading
  - auto-merge
forbidden_files: []
""",
        encoding="utf-8",
    )

    policy = load_policy(policy_path)
    decision = evaluate_task_policy(
        policy,
        {"project": "TradeBot", "title": "Enable live trading from Hermes"},
    )

    assert decision.allowed is False
    assert "live trading" in decision.reason


def test_policy_allows_when_no_rule_matches(tmp_path):
    policy_path = tmp_path / "handypro.yaml"
    policy_path.write_text(
        """
project: HandyPro
forbidden_actions:
  - production deploy
forbidden_files:
  - ".env"
""",
        encoding="utf-8",
    )

    decision = evaluate_task_policy(
        load_policy(policy_path),
        {
            "project": "HandyPro",
            "title": "Add local QA checklist",
            "allowed_files": ["docs/qa-checklist.md"],
        },
    )

    assert decision.allowed is True
    assert decision.reason == "allowed: no policy violations"


def test_starter_configs_encode_tradebot_and_kidsagents_safety_rules():
    tradebot = load_starter_policy("TradeBot")
    tradebot_decision = evaluate_task_policy(
        tradebot,
        {
            "project": "TradeBot",
            "title": "Add broker live trading shortcut",
            "allowed_files": ["config/secrets.yaml"],
        },
    )
    assert tradebot_decision.allowed is False
    assert any(
        marker in tradebot_decision.reason.lower()
        for marker in ("broker", "live trading", "secrets", "auto-merge")
    )

    kidsagents = load_starter_policy("KidsAgents")
    kidsagents_decision = evaluate_task_policy(
        kidsagents,
        {
            "project": "KidsAgents",
            "title": "Install dependencies with raw shell in parent workspace",
            "allowed_files": ["../parent-workspace/package.json"],
        },
    )
    assert kidsagents_decision.allowed is False
    assert (
        "raw shell" in kidsagents_decision.reason.lower()
        or "parent workspace" in kidsagents_decision.reason.lower()
    )
