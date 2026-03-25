#!/usr/bin/env python3
"""Check full environment readiness for OpenMath submissions.

Validates: openmath-env.json config exists, shentud CLI available, local
agent key present, RPC reachable, authz grants on-chain, feegrant on-chain.
Run this as a single pre-flight check before any submission or reward claim.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from submission_config import (
    ENV_CONFIG_FILENAME,
    GLOBAL_ENV_CONFIG_PATH,
    KEYRING_BACKEND,
    SubmissionConfig,
    SubmissionConfigError,
    authz_onboarding_text,
    find_env_config,
    load_submission_config,
    project_env_config_path,
)

AUTHZ_OUTER_WRAPPER_MESSAGES = {"/cosmos.authz.v1beta1.MsgExec"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check full environment readiness for OpenMath submissions.",
    )
    parser.add_argument(
        "--config",
        default=None,
        help=f"Config path (default: auto-detect {ENV_CONFIG_FILENAME})",
    )
    return parser


def run_command(args: list[str]) -> str:
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "command failed"
        raise RuntimeError(f"{' '.join(args)}: {message}")
    return result.stdout.strip()


def run_json(args: list[str]) -> dict:
    output = run_command(args)
    try:
        return json.loads(output)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{' '.join(args)}: expected JSON output") from exc


def print_status(kind: str, label: str, detail: str | None = None) -> None:
    suffix = f" - {detail}" if detail else ""
    print(f"[{kind}] {label}{suffix}")


def collect_values(payload: object, key: str) -> list[object]:
    values: list[object] = []
    if isinstance(payload, dict):
        for k, v in payload.items():
            if k == key:
                values.append(v)
            values.extend(collect_values(v, key))
    elif isinstance(payload, list):
        for v in payload:
            values.extend(collect_values(v, key))
    return values


def flatten_strings(values: list[object]) -> list[str]:
    out: list[str] = []
    for v in values:
        if isinstance(v, list):
            out.extend(str(i) for i in v)
        else:
            out.append(str(v))
    return out


def extract_authz_messages(payload: object) -> set[str]:
    return {
        msg.strip()
        for msg in flatten_strings(collect_values(payload, "msg"))
        if msg.strip()
    }


def check_config_exists(config_arg: str | None) -> Path | None:
    """Check whether the environment config file exists."""
    if config_arg:
        p = Path(config_arg).expanduser()
        if p.exists():
            print_status("ok", "config file", str(p))
            return p
        print_status("missing", "config file", str(p))
        return None
    found = find_env_config()
    if found:
        print_status("ok", "config file", str(found))
        return found
    print_status(
        "missing",
        "config file",
        f"checked {project_env_config_path()} and {GLOBAL_ENV_CONFIG_PATH}",
    )
    return None


def check_shentud() -> bool:
    try:
        version = run_command(["shentud", "version"])
        print_status("ok", "shentud CLI", version)
        return True
    except RuntimeError as exc:
        print_status("missing", "shentud CLI", str(exc))
        return False


def check_local_key(config: SubmissionConfig) -> tuple[bool, bool]:
    try:
        address = run_command([
            "shentud", "keys", "show", config.agent_key_name,
            "-a", "--keyring-backend", KEYRING_BACKEND,
        ])
    except RuntimeError as exc:
        print_status("missing", "local agent key", str(exc))
        return False, False
    print_status("ok", "local agent key", f"{config.agent_key_name} -> {address}")
    if address != config.agent_address:
        print_status("mismatch", "agent address",
                     f"config={config.agent_address}, local={address}")
        return True, False
    print_status("ok", "agent address matches config", config.agent_address)
    return True, True


def check_rpc(config: SubmissionConfig) -> bool:
    """Verify the configured RPC endpoint is reachable."""
    try:
        run_command(["shentud", "status", "--node", config.shentu_node_url])
        print_status("ok", "RPC reachable", config.shentu_node_url)
        return True
    except RuntimeError as exc:
        print_status("error", "RPC unreachable", f"{config.shentu_node_url} - {exc}")
        return False


def check_authz_grants(config: SubmissionConfig) -> bool:
    try:
        payload = run_json([
            "shentud", "query", "authz", "grants",
            config.prover_address, config.agent_address,
            "--node", config.shentu_node_url, "-o", "json",
        ])
    except RuntimeError as exc:
        print_status("missing", "authz grants", str(exc))
        return False

    granted_messages = extract_authz_messages(payload)
    if granted_messages:
        print_status("ok", "authz grants found", ", ".join(sorted(granted_messages)))
    else:
        print_status("missing", "authz grants found", "no granted message types returned")

    ready = True
    for msg_type in config.authz_messages:
        if msg_type in AUTHZ_OUTER_WRAPPER_MESSAGES:
            print_status(
                "warn",
                f"authz grant for {msg_type}",
                "outer wrapper message; check this under feegrant_messages instead",
            )
            continue
        if msg_type in granted_messages:
            print_status("ok", f"authz grant for {msg_type}")
        else:
            print_status("missing", f"authz grant for {msg_type}")
            ready = False
    return ready


def check_feegrant(config: SubmissionConfig) -> tuple[bool, bool]:
    try:
        payload = run_json([
            "shentud", "query", "feegrant", "grant",
            config.fee_granter_address, config.agent_address,
            "--node", config.shentu_node_url, "-o", "json",
        ])
    except RuntimeError as exc:
        print_status("missing", "feegrant grant", str(exc))
        return False, False
    print_status("ok", "feegrant grant",
                 f"{config.fee_granter_address} -> {config.agent_address}")
    allowed = set(flatten_strings(collect_values(payload, "allowed_messages")))
    if not allowed:
        print_status("warn", "feegrant allowed_messages",
                     "no AllowedMsgAllowance filter; appears unrestricted")
        return True, True
    print_status("ok", "feegrant allowed_messages found", ", ".join(sorted(allowed)))
    ready = True
    for msg_type in config.feegrant_messages:
        if msg_type in allowed:
            print_status("ok", f"feegrant message {msg_type}")
        else:
            print_status("missing", f"feegrant message {msg_type}")
            ready = False
    return True, ready


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv or sys.argv[1:])

    config_file = check_config_exists(args.config)
    if not config_file:
        print()
        print("Run the first-time setup flow:")
        print("  See references/init-setup.md")
        print(f"  Create {project_env_config_path()} or {GLOBAL_ENV_CONFIG_PATH}")
        return 1

    try:
        config = load_submission_config(str(config_file))
    except SubmissionConfigError as exc:
        print(exc, file=sys.stderr)
        return 1

    print()
    print(f"Chain ID:     {config.shentu_chain_id}")
    print(f"RPC:          {config.shentu_node_url}")
    print(f"Prover:       {config.prover_address}")
    print(f"Agent Key:    {config.agent_key_name}")
    print(f"Agent Addr:   {config.agent_address}")
    print(f"Fee Granter (derived): {config.fee_granter_address}")
    print()

    ready = True

    print("--- CLI ---")
    if not check_shentud():
        print("\nInspect shentud availability first: python3 scripts/ensure_shentud.py --check-only")
        print("Only with explicit user approval, install it: python3 scripts/ensure_shentud.py --install [--persist-path]")
        return 1

    print("\n--- Local Key ---")
    key_exists, key_matches = check_local_key(config)
    ready = ready and key_exists and key_matches

    print("\n--- Chain / RPC ---")
    rpc_ok = check_rpc(config)
    ready = ready and rpc_ok

    print("\n--- Authz Grants ---")
    authz_ok = check_authz_grants(config)
    ready = ready and authz_ok

    print("\n--- Feegrant ---")
    fg_exists, fg_ready = check_feegrant(config)
    ready = ready and fg_exists and fg_ready

    print()
    if ready:
        print("Status: ready")
        return 0

    print("Status: not ready")
    print()
    print(authz_onboarding_text(config_file))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
