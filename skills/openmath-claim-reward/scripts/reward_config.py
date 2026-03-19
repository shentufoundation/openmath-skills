#!/usr/bin/env python3
"""Shared config helpers for OpenMath reward queries and withdrawals."""

from __future__ import annotations

import json
import os
from pathlib import Path


ENV_CONFIG_FILENAME = "openmath-env.json"
PROJECT_CONFIG_DIRNAME = ".openmath-skills"
GLOBAL_CONFIG_DIR = Path.home() / ".openmath-skills"
GLOBAL_ENV_CONFIG_PATH = GLOBAL_CONFIG_DIR / ENV_CONFIG_FILENAME


class RewardConfigError(ValueError):
    """Raised when reward setup is missing or invalid."""


def project_env_config_path() -> Path:
    return Path.cwd() / PROJECT_CONFIG_DIRNAME / ENV_CONFIG_FILENAME


def default_config_path() -> Path:
    explicit = os.environ.get("OPENMATH_ENV_CONFIG")
    if explicit:
        return Path(explicit).expanduser()
    return project_env_config_path()


DEFAULT_CONFIG_PATH = default_config_path()


def candidate_env_config_paths() -> tuple[Path, Path]:
    return (project_env_config_path(), GLOBAL_ENV_CONFIG_PATH)


def setup_doc_path() -> Path:
    return Path(__file__).resolve().parent.parent / "references" / "init-setup.md"


def find_env_config() -> Path | None:
    explicit = os.environ.get("OPENMATH_ENV_CONFIG")
    if explicit:
        p = Path(explicit).expanduser()
        return p if p.exists() else None

    for path in candidate_env_config_paths():
        if path.exists():
            return path
    return None


def reward_onboarding_text(config_path: Path | None = None) -> str:
    project_config, global_config = candidate_env_config_paths()
    setup_doc = setup_doc_path()
    target = config_path or DEFAULT_CONFIG_PATH
    return "\n".join(
        [
            f"Reward config: {target}",
            "",
            "Auto-discovery only checks these locations:",
            f"- {project_config}",
            f"- {global_config}",
            "",
            f"Init setup guide: {setup_doc}",
            "",
            "To get the OpenMath Wallet Address:",
            "1. Open https://openmath.shentu.org",
            "2. Connect the wallet and enter Profile",
            "3. Copy Wallet Address",
            "4. Save that address as `prover_address` in openmath-env.json, or pass it directly to the rewards query command",
            "",
            "For reward withdrawal, a local os-keyring key must control the same address.",
            "Do not create a new random key for withdrawal unless it is the same wallet that owns the rewards.",
        ]
    )


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RewardConfigError(reward_onboarding_text(path)) from exc
    except json.JSONDecodeError as exc:
        raise RewardConfigError(f"Invalid JSON in config file: {path}: {exc}") from exc


def load_reward_address(config_path: str | os.PathLike[str] | None = None) -> tuple[str, Path]:
    if config_path is not None:
        path = Path(config_path).expanduser()
    else:
        detected = find_env_config()
        path = detected if detected else DEFAULT_CONFIG_PATH.expanduser()

    data = _read_json(path)
    address = str(data.get("prover_address", "")).strip()
    if not address or address.startswith("<"):
        raise RewardConfigError(
            f"Config file {path} is missing a real value for `prover_address`.\n\n{reward_onboarding_text(path)}"
        )
    return address, path
