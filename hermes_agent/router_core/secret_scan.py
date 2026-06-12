import hashlib
import math
import re
from typing import Iterable, List, Sequence, Tuple

from hermes_agent.router_core.types import ScanFinding, ScanResult, Sensitivity


_PATTERNS: Sequence[Tuple[str, re.Pattern[str]]] = (
    ("openai_project_key", re.compile(r"\bsk-proj-[A-Za-z0-9_-]{20,}\b")),
    ("openai_key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b")),
    ("github_pat", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("github_token", re.compile(r"\bghp_[A-Za-z0-9_]{20,}\b")),
    (
        "pem_private_key",
        re.compile(
            r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----",
            re.DOTALL,
        ),
    ),
    ("telegram_bot_token", re.compile(r"\b\d{8,12}:[A-Za-z0-9_-]{30,}\b")),
)

_ENV_PAIR = re.compile(
    r"\b([A-Z][A-Z0-9_]{1,80})=([^\s'\"#]{16,})"
)
_SECRET_KEY_NAME = re.compile(
    r"(KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL|PRIVATE|SEED)", re.IGNORECASE
)
_TOKEN = re.compile(r"(?<![A-Za-z0-9_./+=-])([A-Za-z0-9_./+=-]{32,})(?![A-Za-z0-9_./+=-])")
_UUID = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
_PLACEHOLDER = re.compile(r"^\[REDACTED:[a-z0-9_]+:[0-9a-f]{8}\]$")

_BIP39_WORDS = {
    "abandon",
    "ability",
    "able",
    "about",
    "above",
    "absent",
    "absorb",
    "abstract",
    "absurd",
    "abuse",
    "access",
    "accident",
    "account",
    "accuse",
    "achieve",
    "acid",
    "acoustic",
    "acquire",
    "across",
    "act",
    "action",
    "actor",
    "actress",
    "actual",
    "adapt",
    "add",
    "addict",
    "address",
    "adjust",
    "admit",
    "adult",
    "advance",
    "advice",
    "aerobic",
    "affair",
    "afford",
    "afraid",
    "again",
    "age",
    "agent",
    "agree",
    "ahead",
    "aim",
    "air",
    "airport",
    "aisle",
    "alarm",
    "album",
    "alcohol",
    "alert",
    "alien",
    "all",
    "alley",
    "allow",
    "almost",
    "alone",
    "alpha",
    "already",
    "also",
    "alter",
    "always",
    "amateur",
    "amazing",
    "among",
    "amount",
    "amused",
    "analyst",
    "anchor",
    "ancient",
    "anger",
    "angle",
    "angry",
    "animal",
    "ankle",
    "announce",
    "annual",
    "another",
    "answer",
    "antenna",
    "antique",
    "anxiety",
    "any",
    "apart",
    "apology",
    "appear",
    "apple",
    "approve",
    "april",
    "arch",
    "arctic",
    "area",
    "arena",
    "argue",
    "arm",
    "armed",
    "armor",
    "army",
    "around",
    "arrange",
    "arrest",
    "arrive",
    "arrow",
    "art",
    "artefact",
    "artist",
    "artwork",
}


def _fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _finding(finding_type: str, value: str, start: int, end: int) -> ScanFinding:
    return ScanFinding(
        type=finding_type,
        value=value,
        start=start,
        end=end,
        fingerprint=_fingerprint(value),
    )


def shannon_entropy(value: str) -> float:
    if not value:
        return 0.0
    counts = {}
    for char in value:
        counts[char] = counts.get(char, 0) + 1
    total = len(value)
    return -sum((count / total) * math.log2(count / total) for count in counts.values())


def _char_class_count(value: str) -> int:
    classes = 0
    classes += any(char.islower() for char in value)
    classes += any(char.isupper() for char in value)
    classes += any(char.isdigit() for char in value)
    classes += any(not char.isalnum() for char in value)
    return classes


def _looks_like_high_entropy_secret(value: str) -> bool:
    if _PLACEHOLDER.match(value) or _UUID.match(value):
        return False
    if re.fullmatch(r"[0-9a-fA-F-]{32,}", value):
        return False
    if _char_class_count(value) < 3:
        return False
    return shannon_entropy(value) >= 4.2


def _find_pattern_secrets(text: str) -> Iterable[ScanFinding]:
    for finding_type, pattern in _PATTERNS:
        for match in pattern.finditer(text):
            yield _finding(finding_type, match.group(0), match.start(), match.end())


def _find_env_secrets(text: str) -> Iterable[ScanFinding]:
    for match in _ENV_PAIR.finditer(text):
        key = match.group(1)
        value = match.group(2)
        if _SECRET_KEY_NAME.search(key) or _looks_like_high_entropy_secret(value):
            yield _finding("env_secret", match.group(0), match.start(), match.end())


def _find_bip39_sequences(text: str) -> Iterable[ScanFinding]:
    words = [
        (match.group(0).lower(), match.start(), match.end())
        for match in re.finditer(r"\b[a-zA-Z]{3,8}\b", text)
    ]
    for size in (24, 12):
        for index in range(0, len(words) - size + 1):
            window = words[index : index + size]
            if all(word in _BIP39_WORDS for word, _, _ in window):
                start = window[0][1]
                end = window[-1][2]
                yield _finding("bip39_phrase", text[start:end], start, end)


def _find_entropy_tokens(text: str) -> Iterable[ScanFinding]:
    for match in _TOKEN.finditer(text):
        value = match.group(1)
        if _looks_like_high_entropy_secret(value):
            yield _finding("high_entropy_token", value, match.start(1), match.end(1))


def _overlaps(span: Tuple[int, int], existing: Sequence[ScanFinding]) -> bool:
    start, end = span
    for finding in existing:
        if start < finding.end and end > finding.start:
            return True
    return False


def _collect_findings(text: str) -> List[ScanFinding]:
    candidates: List[ScanFinding] = []
    candidates.extend(_find_pattern_secrets(text))
    candidates.extend(_find_env_secrets(text))
    candidates.extend(_find_bip39_sequences(text))
    candidates.extend(_find_entropy_tokens(text))

    findings: List[ScanFinding] = []
    for finding in sorted(candidates, key=lambda item: (item.start, -(item.end - item.start))):
        if not _overlaps((finding.start, finding.end), findings):
            findings.append(finding)
    return findings


def _redacted_text(text: str, findings: Sequence[ScanFinding]) -> str:
    redacted = text
    for finding in sorted(findings, key=lambda item: item.start, reverse=True):
        placeholder = f"[REDACTED:{finding.type}:{finding.fingerprint[:8]}]"
        redacted = redacted[: finding.start] + placeholder + redacted[finding.end :]
    return redacted


def scan_text(text: str) -> ScanResult:
    findings = _collect_findings(text)
    implied = Sensitivity.S4_SECRET if findings else Sensitivity.S0_PUBLIC
    return ScanResult(
        redacted_text=_redacted_text(text, findings),
        findings=findings,
        implied_sensitivity=implied,
    )


def redact(text: str) -> str:
    return scan_text(text).redacted_text
