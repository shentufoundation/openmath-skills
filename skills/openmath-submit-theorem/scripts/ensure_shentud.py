#!/usr/bin/env python3
"""Ensure a working shentud binary is installed and reachable."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen


LATEST_RELEASE_API = "https://api.github.com/repos/shentufoundation/shentu/releases/latest"
DEFAULT_INSTALL_DIR = Path.home() / "bin"
DEFAULT_TIMEOUT_SECONDS = 20
USER_AGENT = "openmath-submit-theorem/1.0"


def shell_rc_path() -> Path | None:
    shell_name = Path(os.environ.get("SHELL", "")).name
    if shell_name == "zsh":
        return Path.home() / ".zshrc"
    if shell_name == "bash":
        return Path.home() / ".bashrc"
    return None


def status(message: str) -> None:
    print(message, flush=True)


def binary_check(path: Path) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            [str(path), "version"],
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, OSError) as exc:
        return False, str(exc)

    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "unknown error"
        return False, message

    version = result.stdout.strip() or result.stderr.strip() or "unknown version"
    return True, version


def candidate_paths(install_dir: Path) -> list[Path]:
    candidates: list[Path] = []

    env_bin = os.environ.get("OPENMATH_SHENTUD_BIN")
    if env_bin:
        candidates.append(Path(env_bin).expanduser())

    which_path = shutil.which("shentud")
    if which_path:
        candidates.append(Path(which_path))

    candidates.append(install_dir / "shentud")

    seen: set[str] = set()
    unique: list[Path] = []
    for candidate in candidates:
        key = str(candidate)
        if key in seen:
            continue
        seen.add(key)
        unique.append(candidate)
    return unique


def working_binary(install_dir: Path) -> tuple[Path | None, str]:
    errors: list[str] = []
    for candidate in candidate_paths(install_dir):
        ok, message = binary_check(candidate)
        if ok:
            return candidate, message
        errors.append(f"{candidate}: {message}")
    return None, "\n".join(errors)


def asset_token_groups() -> list[tuple[str, ...]]:
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "darwin":
        if machine in {"arm64", "aarch64"}:
            return [("arm64", "macos"), ("arm64", "darwin")]
        if machine in {"x86_64", "amd64"}:
            return [("amd64", "macos"), ("x86_64", "macos"), ("amd64", "darwin")]
    if system == "linux":
        if machine in {"x86_64", "amd64"}:
            return [("linux", "amd64"), ("linux", "x86_64")]
        if machine in {"arm64", "aarch64"}:
            return [("linux", "arm64"), ("linux", "aarch64")]

    raise RuntimeError(f"Unsupported platform: system={system}, machine={machine}")


def fetch_latest_release(timeout_seconds: int) -> dict:
    request = Request(LATEST_RELEASE_API, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout_seconds) as response:
        return json.load(response)


def select_asset(release: dict) -> dict:
    assets = release.get("assets") or []
    token_groups = asset_token_groups()

    for tokens in token_groups:
        for asset in assets:
            name = str(asset.get("name", "")).lower()
            if all(token in name for token in tokens):
                return asset

    asset_names = ", ".join(str(asset.get("name", "?")) for asset in assets) or "none"
    raise RuntimeError(f"No matching shentud asset found in latest release. Assets: {asset_names}")


def download_asset(asset: dict, destination: Path, timeout_seconds: int) -> None:
    url = asset.get("browser_download_url")
    if not url:
        raise RuntimeError("Release asset is missing browser_download_url")

    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout_seconds) as response, destination.open("wb") as handle:
        shutil.copyfileobj(response, handle)


def install_binary(asset: dict, install_dir: Path, timeout_seconds: int) -> Path:
    install_dir.mkdir(parents=True, exist_ok=True)
    target = install_dir / "shentud"

    if target.is_symlink() or target.exists():
        target.unlink()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / str(asset.get("name", "shentud"))
        status(f"Downloading {asset.get('name', 'shentud')} ...")
        download_asset(asset, temp_path, timeout_seconds)
        temp_path.chmod(temp_path.stat().st_mode | stat.S_IEXEC)
        shutil.move(str(temp_path), str(target))

    target.chmod(target.stat().st_mode | stat.S_IEXEC)
    return target


def append_path_export(install_dir: Path) -> Path | None:
    current_path_entries = os.environ.get("PATH", "").split(os.pathsep)
    if str(install_dir) in current_path_entries:
        return None

    rc_path = shell_rc_path()
    if not rc_path:
        return None

    export_line = f'export PATH="{install_dir}:$PATH"'
    existing = rc_path.read_text(encoding="utf-8") if rc_path.exists() else ""
    if export_line not in existing:
        prefix = "" if existing.endswith("\n") or not existing else "\n"
        rc_path.write_text(f"{existing}{prefix}{export_line}\n", encoding="utf-8")
    return rc_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ensure a working shentud binary is installed and reachable."
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="Download and install shentud if it is missing or broken. Without this flag, the script only reports status.",
    )
    parser.add_argument(
        "--install-dir",
        default=str(DEFAULT_INSTALL_DIR),
        help=f"Directory to install shentud into (default: {DEFAULT_INSTALL_DIR})",
    )
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="Download and reinstall even if a working shentud binary already exists.",
    )
    parser.add_argument(
        "--persist-path",
        action="store_true",
        help="Append the install directory to the active shell rc file after a successful install.",
    )
    parser.add_argument(
        "--no-persist-path",
        action="store_true",
        help="Deprecated: path persistence is disabled by default unless --persist-path is passed.",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only report whether a working shentud binary is available; do not download.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"Network timeout in seconds for release metadata and asset download (default: {DEFAULT_TIMEOUT_SECONDS})",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv or sys.argv[1:])
    install_dir = Path(args.install_dir).expanduser()
    expected_binary = install_dir / "shentud"
    install_requested = args.install or args.force_download

    current_binary, version = working_binary(install_dir)
    if current_binary is not None and not args.force_download:
        print("Shentud status: usable")
        print("Using existing shentud:", current_binary)
        print("Version:", version)
        return 0

    print("Shentud status: unavailable")
    print("Expected install path:", expected_binary)
    print("Binary present:", "yes" if expected_binary.exists() else "no")
    if current_binary is None and version:
        print("Discovery details:")
        print(version)

    if args.check_only or not install_requested:
        if not args.check_only and not install_requested:
            print("No installation requested. Re-run with `--install` to download and write a shentud binary.")
            print("Pass `--persist-path` only if you explicitly want to append the install directory to your shell rc file.")
        return 1

    try:
        status("Fetching latest Shentu release metadata ...")
        release = fetch_latest_release(args.timeout_seconds)
        asset = select_asset(release)
        status(f"Selected release: {release.get('tag_name', 'unknown')}")
        status(f"Selected asset: {asset.get('name', 'unknown')}")
        installed_binary = install_binary(asset, install_dir, args.timeout_seconds)
        version_ok, version_message = binary_check(installed_binary)
        if not version_ok:
            raise RuntimeError(f"Installed shentud failed verification: {version_message}")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print("Shentud status: installed")
    print("Installed shentud:", installed_binary)
    print("Release:", release.get("tag_name", "unknown"))
    print("Asset:", asset.get("name", "unknown"))
    print("Version:", version_message)

    if args.no_persist_path or not args.persist_path:
        print(f"Add this directory to PATH if needed: {install_dir}")
    else:
        rc_path = append_path_export(install_dir)
        if rc_path is not None:
            print("Updated PATH in:", rc_path)
            print(f"Reload your shell or run: export PATH=\"{install_dir}:$PATH\"")
        else:
            print("Install directory is already in PATH or no shell rc file was detected.")

    print(f"You can also set OPENMATH_SHENTUD_BIN={installed_binary} if you prefer an explicit path.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
