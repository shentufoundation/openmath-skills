#!/usr/bin/env python3
"""Shared configuration helpers for authz-based OpenMath submissions."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_SHENTU_CHAIN_ID = os.environ.get("SHENTU_CHAIN_ID", "shentu-2.2")
DEFAULT_SHENTU_NODE_URL = os.environ.get("SHENTU_NODE_URL", "https://rpc.shentu.org:443")
KEYRING_BACKEND = "os"
DEFAULT_AGENT_KEY_NAME = "agent-prover"

ENV_CONFIG_FILENAME = "openmath-env.json"
PROJECT_CONFIG_DIRNAME = ".openmath-skills"
GLOBAL_CONFIG_DIR = Path.home() / ".openmath-skills"
GLOBAL_ENV_CONFIG_PATH = GLOBAL_CONFIG_DIR / ENV_CONFIG_FILENAME


def project_env_config_path() -> Path:
    """Return the project-local config path for the current working directory."""
    return Path.cwd() / PROJECT_CONFIG_DIRNAME / ENV_CONFIG_FILENAME


def default_config_path() -> Path:
    """Return the default config path used in CLI help and fallbacks."""
    explicit = os.environ.get("OPENMATH_ENV_CONFIG")
    if explicit:
        return Path(explicit).expanduser()
    return project_env_config_path()


DEFAULT_CONFIG_PATH = default_config_path()

DEFAULT_AUTHZ_MESSAGES = (
    "/shentu.bounty.v1.MsgCreateTheorem",
    "/shentu.bounty.v1.MsgSubmitProofHash",
    "/shentu.bounty.v1.MsgSubmitProofDetail",
    "/shentu.bounty.v1.MsgWithdrawReward",
)
DEFAULT_FEEGRANT_MESSAGES = ("/cosmos.authz.v1beta1.MsgExec",)
REQUIRED_IDENTITY_FIELDS = ("prover_address", "agent_address", "agent_key_name")
FIELD_LABELS = {
    "preferred_language": "preferred theorem language",
    "prover_address": "OpenMath wallet address",
    "agent_address": "agent address",
    "agent_key_name": f"local agent key name (default: {DEFAULT_AGENT_KEY_NAME})",
}


class SubmissionConfigError(ValueError):
    """Raised when the authz submission config is missing or invalid."""


@dataclass(frozen=True)
class SubmissionConfig:
    config_path: Path
    prover_address: str
    agent_key_name: str
    agent_address: str
    fee_granter_address: str
    authz_messages: tuple[str, ...]
    feegrant_messages: tuple[str, ...]
    shentu_chain_id: str
    shentu_node_url: str


def example_config_path() -> Path:
    """Return path to the unified env example config (recommended)."""
    return Path(__file__).resolve().parent.parent / "references" / "openmath-env.example.json"


env_example_config_path = example_config_path


def setup_doc_path() -> Path:
    return Path(__file__).resolve().parent.parent / "references" / "init-setup.md"


def candidate_env_config_paths() -> tuple[Path, Path]:
    """Return the two auto-discovery locations for openmath-env.json."""
    return (project_env_config_path(), GLOBAL_ENV_CONFIG_PATH)


def find_env_config() -> Path | None:
    """Return the first existing env config from project-local or ~/.openmath-skills."""
    explicit = os.environ.get("OPENMATH_ENV_CONFIG")
    if explicit:
        p = Path(explicit).expanduser()
        return p if p.exists() else None

    for p in candidate_env_config_paths():
        if p.exists():
            return p
    return None

def _get_real_value(data: dict, *keys: str) -> str:
    for key in keys:
        value = str(data.get(key, "")).strip()
        if value and not value.startswith("<"):
            return value
    return ""


def _has_real_value(data: dict, key: str) -> bool:
    return bool(_get_real_value(data, key))


def missing_identity_fields(data: dict) -> tuple[str, ...]:
    return tuple(key for key in REQUIRED_IDENTITY_FIELDS if not _has_real_value(data, key))


def authz_onboarding_text(
    config_path: Path,
    *,
    config_exists: bool = False,
    missing_fields: tuple[str, ...] = (),
) -> str:
    env_example = env_example_config_path()
    setup_doc = setup_doc_path()
    project_config, global_config = candidate_env_config_paths()
    lines = [
        f"Environment config: {config_path}",
        "",
        "Auto-discovery only checks these locations:",
        f"- {project_config}",
        f"- {global_config}",
        "",
        f"Init setup guide: {setup_doc}",
        f"Copy and edit the example config: {env_example}",
        "",
    ]

    if not config_exists:
        lines.extend(
            [
                "No config file exists yet.",
                "",
                "Stop and ask the user where to create it:",
                f"- ./{PROJECT_CONFIG_DIRNAME}/{ENV_CONFIG_FILENAME} (recommended for project-specific settings)",
                "- ~/.openmath-skills/openmath-env.json (recommended for reusable settings)",
                "",
                "Then create openmath-env.json there from the example config.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                f"Existing config detected: {config_path}",
                "Do not create a second config file. Update this file in place.",
                "",
            ]
        )
        if missing_fields:
            lines.append("Missing required authz identity fields:")
            lines.extend(f"- {key}: {FIELD_LABELS.get(key, key)}" for key in missing_fields)
            lines.extend(
                [
                    "",
                    "Ask only for the missing fields, then update the existing config.",
                    "",
                ]
            )

    lines.extend(
        [
            "Required authz identity fields:",
            "- preferred_language: optional shared preference for theorem discovery (`lean` or `rocq`)",
            "- prover_address: the user's OpenMath Wallet Address from Profile",
            "- agent_address: the bech32 address for the agent used by authz exec",
            f"- agent_key_name: the local key name used with `shentud tx authz exec --from` (default: {DEFAULT_AGENT_KEY_NAME})",
            "- fee granter is derived automatically from prover_address",
            f"- Shentu chain ID comes from SHENTU_CHAIN_ID or defaults to {DEFAULT_SHENTU_CHAIN_ID}",
            f"- Shentu RPC URL comes from SHENTU_NODE_URL or defaults to {DEFAULT_SHENTU_NODE_URL}",
            "",
            "Before asking for `prover_address`, guide the user:",
            "1. Open https://openmath.shentu.org",
            "2. Connect the wallet and enter Profile",
            "3. Copy Wallet Address",
            "4. Save that address as `prover_address`",
            "",
            f"Then resolve the local agent key using the default name `{DEFAULT_AGENT_KEY_NAME}`:",
            f"  shentud keys show {DEFAULT_AGENT_KEY_NAME} -a --keyring-backend {KEYRING_BACKEND}",
            f"If the key exists, save `agent_key_name` as `{DEFAULT_AGENT_KEY_NAME}` and use the returned address as `agent_address`.",
            "",
            "If the key does not exist, stop and ask the user whether to create a new local key or recover an existing one.",
            "Only after explicit approval should you run one of these commands:",
            f"  shentud keys add {DEFAULT_AGENT_KEY_NAME} --keyring-backend {KEYRING_BACKEND}",
            f"  shentud keys add {DEFAULT_AGENT_KEY_NAME} --recover --keyring-backend {KEYRING_BACKEND}",
            f"Then save `agent_key_name` as `{DEFAULT_AGENT_KEY_NAME}` and save the resulting address as `agent_address`.",
            "Tell the user to securely store any mnemonic or recovery material shown during key creation or recovery.",
            "",
            "When `prover_address` and `agent_address` are both known, and authz/feegrant is still missing:",
            "1. Open https://openmath.shentu.org/OpenMath/Profile",
            "2. Scroll to the bottom and find `AI Agent Authorization`.",
            "3. Enter `agent_address`.",
            "4. Click `Authorize` and confirm the wallet transaction(s).",
            f"5. Re-run `python3 scripts/check_authz_setup.py --config {config_path}` to verify chain state.",
            "",
            "Manual fallback: see references/authz_setup.md for CLI authz + feegrant commands.",
        ]
    )
    return "\n".join(lines)


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SubmissionConfigError(authz_onboarding_text(path, config_exists=False)) from exc
    except json.JSONDecodeError as exc:
        raise SubmissionConfigError(f"Invalid JSON in config file: {path}: {exc}") from exc


def _require_string(data: dict, key: str, path: Path) -> str:
    value = _get_real_value(data, key)
    if not value or value.startswith("<"):
        raise SubmissionConfigError(
            f"Config file {path} is missing a real value for `{key}`.\n\n{authz_onboarding_text(path)}"
        )
    return value


def _read_messages(
    data: dict,
    key: str,
    default: tuple[str, ...],
    path: Path,
) -> tuple[str, ...]:
    raw = data.get(key)
    if raw is None:
        return default
    if not isinstance(raw, list) or not raw:
        raise SubmissionConfigError(f"Config file {path} must define `{key}` as a non-empty array.")
    values = tuple(str(item).strip() for item in raw if str(item).strip())
    if not values:
        raise SubmissionConfigError(f"Config file {path} must define `{key}` as a non-empty array.")
    return values


def _resolve_network() -> tuple[str, str]:
    """Resolve Shentu chain_id and node_url from environment or defaults."""
    return DEFAULT_SHENTU_CHAIN_ID, DEFAULT_SHENTU_NODE_URL


def load_submission_config(config_path: str | os.PathLike[str] | None = None) -> SubmissionConfig:
    if config_path is not None:
        path = Path(config_path).expanduser()
    else:
        detected = find_env_config()
        path = detected if detected else DEFAULT_CONFIG_PATH.expanduser()

    data = _read_json(path)
    missing_fields = missing_identity_fields(data)
    if missing_fields:
        fields = ", ".join(missing_fields)
        raise SubmissionConfigError(
            f"Config file {path} is missing required authz identity fields: {fields}.\n\n"
            f"{authz_onboarding_text(path, config_exists=True, missing_fields=missing_fields)}"
        )

    prover_address = _require_string(data, "prover_address", path)
    agent_key_name = _require_string(data, "agent_key_name", path)
    agent_address = _require_string(data, "agent_address", path)
    fee_granter_address = prover_address

    shentu_chain_id, shentu_node_url = _resolve_network()
    return SubmissionConfig(
        config_path=path,
        prover_address=prover_address,
        agent_key_name=agent_key_name,
        agent_address=agent_address,
        fee_granter_address=fee_granter_address,
        authz_messages=_read_messages(data, "authz_messages", DEFAULT_AUTHZ_MESSAGES, path),
        feegrant_messages=_read_messages(
            data,
            "feegrant_messages",
            DEFAULT_FEEGRANT_MESSAGES,
            path,
        ),
        shentu_chain_id=shentu_chain_id,
        shentu_node_url=shentu_node_url,
    )
