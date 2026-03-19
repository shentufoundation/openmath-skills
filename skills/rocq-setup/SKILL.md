---
name: rocq-setup
version: 0.2.0
description: >
  Use when installing Rocq, setting up a development environment, managing
  opam switches and compiler versions, installing the Rocq Platform, configuring
  rocq-lsp with VSCode or Proof General with Emacs, pinning Rocq versions for a
  project, and troubleshooting toolchain issues. Use rocq-dune for build system
  setup after the environment is established.
tags: [rocq, coq, setup, opam, toolchain, rocq-platform, rocq-lsp, proof-general, environment]
agent-support: [claude-code, cursor, gemini-cli, codex, cline]
---

# Rocq Development Environment Setup

This skill covers installing Rocq, managing opam switches, configuring editors,
and establishing a reproducible per-project toolchain. For build system
configuration (`_CoqProject`, `dune`) see the `rocq-dune` skill.

> **Current stable**: Rocq 9.1.0 (September 15, 2025) — Platform 2025.08.2 (February 24, 2026)

## Rocq 9.x Package Structure

Rocq 9.0 introduced a new package layout. Understand these before installing:

| opam package | Contents |
|---|---|
| `rocq-runtime` | `rocq` CLI binary, plugins, tools — no Gallina code |
| `rocq-core` | Corelib (extended prelude) + Ltac2 library + primitive type bindings |
| `rocq-stdlib` | Standard library (maintained separately from the main repo since 9.0) |
| `rocq-prover` | Meta-package that installs `rocq-runtime` + `rocq-core` + `rocq-stdlib` |
| `coq` | Legacy name — covers Rocq 8.x only |

**MUST** use `rocq-prover` (not `coq`) for new Rocq 9.x installations.

### Stdlib Import Prefix Migration

In Rocq 9.x, the standard library prefix changed:

```coq
(* Rocq 8.x style — still works in 9.x with a deprecation warning *)
From Coq Require Import Arith List.

(* Rocq 9.x style — preferred for new code *)
From Stdlib Require Import Arith List.
```

Silence the deprecation warning in `_CoqProject` while maintaining 8.x compatibility:
```
-arg -w -arg -deprecated-from-Coq
```

When dropping support for Rocq ≤ 8.20, replace all `From Coq` with `From Stdlib`.

## Method 1: Rocq Platform (Recommended)

The **Rocq Platform** is the official distribution — it bundles Rocq with a
curated, version-compatible set of packages (MathComp, Equations, VST, Flocq,
etc.). Use this for new projects unless you need a very specific version mix.

### Installation

```bash
# 1. Install opam (the OCaml package manager — required)
#    macOS:
brew install opam

#    Ubuntu/Debian:
sudo apt-get install opam

#    Windows: use the opam Windows installer or WSL2 + Ubuntu method above

# 2. Initialise opam (first-time only)
opam init --bare -y

# 3. Install the Rocq Platform bundle for a specific release
#    See https://rocq-prover.org/releases for available platform tags
#    Platform 2025.08.2 (Feb 2026) is the current release for Rocq 9.0
opam pin add rocq-platform https://github.com/rocq-prover/platform.git#2025.08.2
opam install rocq-platform
```

After installation, verify:

```bash
rocq --version      # The Rocq Proof Assistant, version 9.x.y
# or for older installs:
coqc --version
```

## Method 2: Manual opam Install (Version Control)

Use this when you need a specific Rocq version, or the Platform bundle is too
large for your use case.

### Install opam (if not already done)

```bash
# macOS
brew install opam

# Ubuntu/Debian
sudo apt-get update && sudo apt-get install -y opam

# Verify
opam --version   # must be >= 2.1
```

### Create a Dedicated opam Switch

**MUST** create a project-specific opam switch. Never install Rocq into the
default switch — version conflicts across projects are inevitable.

```bash
# Create a switch with OCaml 5.2 (required for Rocq 9.1)
opam switch create rocq-9.1 ocaml-base-compiler.5.2.0
eval $(opam env --switch=rocq-9.1)

# Install Rocq 9.1 (new package name for 9.x)
opam install rocq-prover.9.1.0

# Or install Rocq 8.20 (legacy name still used for 8.x)
opam install coq.8.20.0
```

**MUST** always run `eval $(opam env)` after switching — without it the shell
still references the previous switch's binaries.

### Persisting the Switch in a Project

Pin the switch for everyone who works in the directory:

```bash
# Create .opam-switch in the project root
echo "rocq-9.1" > .opam-switch

# Or add to direnv (.envrc) for automatic activation
echo 'eval $(opam env --switch=rocq-9.1 --set-switch)' >> .envrc
direnv allow
```

## Installing Common Packages

```bash
# MathComp (core + algebra + analysis) — works with Rocq 9.x and 8.20
opam install coq-mathcomp-ssreflect coq-mathcomp-algebra

# Hierarchy Builder (required for MathComp 2.3.x)
opam install coq-hierarchy-builder

# Equations (well-founded recursion)
opam install coq-equations

# Stdpp (Iris base library)
opam install coq-stdpp

# VST (C verification)
opam install coq-vst

# Flocq (floating-point)
opam install coq-flocq

# Search available packages (use rocq- prefix for 9.x, coq- for 8.x)
opam search coq-
opam search rocq-
```

**SHOULD** pin package versions in an `opam` file at the project root for
reproducibility (see the Project Opam File section below).

## Editor Setup: VSCode + rocq-lsp

`rocq-lsp` is the recommended interactive proof environment for new projects —
it provides incremental checking, goal display, and error highlighting.

Current version: `0.2.5+9.1` (for Rocq 9.1) / `0.2.5+9.0` (for Rocq 9.0).

### Installation

```bash
# Install rocq-lsp in the active opam switch
opam install rocq-lsp

# Verify the binary is available
which rocq-lsp   # should resolve inside the opam switch prefix
rocq-lsp --version
```

In VSCode:

1. Install the **"Rocq LSP"** extension (publisher: `ejgallego`, id: `ejgallego.coq-lsp`)
2. Open a `.v` file — the extension auto-detects `rocq-lsp` in the PATH
3. Use `Ctrl+Alt+C Ctrl+Alt+C` to open the **Goals** panel

**MUST** ensure the terminal used to launch VSCode has `eval $(opam env)` in
effect — otherwise VSCode cannot find `rocq-lsp` in PATH.

### Workspace Settings

Add to `.vscode/settings.json` in the project root:

```json
{
  "coq-lsp.path": "rocq-lsp",
  "coq-lsp.eager_diagnostics": false,
  "coq-lsp.show_coq_info_messages": false,
  "[coq]": {
    "editor.tabSize": 2,
    "editor.insertSpaces": true
  }
}
```

Set `eager_diagnostics: false` for large files — it defers checking to
save tokens and reduce lag.

For Dune-managed projects, use `dune exec -- rocq-lsp` as the server command:

```json
{
  "coq-lsp.server_command": "dune exec -- rocq-lsp"
}
```

## Editor Setup: Proof General (Emacs)

Proof General is the mature Emacs interface; use it if you work primarily in
Emacs or need `coqdoc` integration.

### Installation

```bash
# Install Proof General via MELPA (add to your Emacs init.el):
(use-package proof-general
  :ensure t
  :custom
  (proof-splash-enable nil)
  (proof-three-window-mode-policy 'hybrid))

# Install Company-Coq for completion and snippets:
(use-package company-coq
  :ensure t
  :hook (coq-mode . company-coq-mode))
```

**MUST** set `coq-prog-name` to the switch-specific binary if Emacs does not
pick up the opam environment automatically:

```elisp
(setq coq-prog-name
      (string-trim
       (shell-command-to-string "opam exec --switch=rocq-9.1 -- which coqtop")))
```

### Key Bindings (Proof General)

| Key | Action |
|---|---|
| `C-c C-n` | Step forward one command |
| `C-c C-u` | Step backward one command |
| `C-c C-Enter` | Process to cursor position |
| `C-c C-b` | Process whole buffer |
| `C-c C-r` | Retract (undo) whole buffer |
| `C-c C-.` | Show current goals |

## Editor Setup: CoqIDE

CoqIDE is the bundled GUI; install it alongside Rocq:

```bash
opam install coqide
coqide &
```

CoqIDE is suitable for beginners but lacks LSP-quality incremental feedback.
**SHOULD** prefer `rocq-lsp` + VSCode for new projects.

## Project Opam File

For reproducibility, add an `opam` file at the project root.

### For Rocq 9.x projects

```opam
opam-version: "2.0"
name: "my-rocq-project"
version: "0.1.0"
maintainer: "you@example.com"
authors: ["Your Name"]
license: "Apache-2.0"
depends: [
  "ocaml"          { >= "4.14.0" }
  "rocq-prover"    { >= "9.1.0" & < "9.3" }
  "coq-mathcomp-ssreflect" { >= "2.3.0" }
  "coq-equations"  { >= "1.3" }
]
build: [
  ["dune" "build" "-p" name "-j" jobs]
]
```

### For projects supporting Rocq 8.x and 9.x

Use a disjunction to cover both package names:

```opam
depends: [
  "ocaml"          { >= "4.14.0" }
  ( "coq"          { >= "8.20" & < "9.0" }
  | "rocq-prover"  { >= "9.0" & < "9.3" } )
  "coq-mathcomp-ssreflect" { >= "2.2.0" }
]
```

Install the pinned environment from this file:

```bash
opam install . --deps-only
```

## Version Matrix

| Rocq Version | OCaml | MathComp | HB | Notes |
|---|---|---|---|---|
| 9.1.0 | 5.2 / 4.14 | 2.3.x | ≥ 1.8 | Current stable (Sept 2025) |
| 9.0.0 | 5.1 / 4.14 | 2.3.x | ≥ 1.8 | First Rocq-branded release (Mar 2025) |
| 8.20.0 | 5.1 / 4.14 | 2.2.x | ≥ 1.6 | Previous stable |
| 8.19.x | 4.14 | 2.1.x | ≥ 1.5 | LTS-style, widely used |
| 8.18.x | 4.14 | 1.19.x | ≥ 1.4 | Legacy, avoid for new projects |

**MUST** check compatibility: MathComp releases are pinned to specific Rocq
minor versions. `opam install` will report conflicts if versions are
incompatible — do not force-install.

## Checking Installation Health

After setup, run this sanity check:

```bash
# Check Rocq version
rocq --version     # The Rocq Proof Assistant, version 9.1.0

# Check load path with stdlib (Rocq 9.x)
rocq -e 'From Stdlib Require Import Arith. Check Nat.add_comm.'

# Check Corelib (Ltac2 etc.) — always available in rocq-core
rocq -e 'From Corelib Require Import Ltac2.Ltac2. Check Ltac2.exact.'

# Check a library is available
rocq -e 'From mathcomp Require Import all_ssreflect. Check leq_add.'

# Check rocq-lsp is in PATH
rocq-lsp --version
```

All commands MUST succeed before proceeding to proof development.

For Rocq 8.x installations, use `coqc` and `coqc --version` instead of `rocq`.

## Troubleshooting

### `rocq: command not found` after `opam install`

```bash
# Re-source the opam environment
eval $(opam env)

# If that does not help, check which switch is active
opam switch list
opam switch set <your-switch-name>
eval $(opam env)
```

### `Inconsistent assumptions` error when loading a library

This means the `.vo` files (compiled Rocq objects) were compiled with a
different Rocq version than the one currently active. Fix:

```bash
# Recompile the affected library from source
opam reinstall coq-mathcomp-ssreflect

# Or nuke and rebuild the project's own .vo files
find . -name '*.vo' -o -name '*.vos' -o -name '*.vok' | xargs rm -f
dune build   # or: make
```

### `rocq-lsp` Goals panel is blank / not updating

1. Check that the terminal used to launch VSCode had `eval $(opam env)` active
2. Run `which rocq-lsp` in that terminal — it must be inside the opam switch
3. Check the VSCode Output panel (`View → Output → Rocq LSP`) for error messages
4. As a fallback, set `"coq-lsp.path"` in settings to the absolute path:

   ```bash
   opam exec -- which rocq-lsp   # get the absolute path
   ```

### opam dependency conflicts

```bash
# Use opam's built-in conflict explainer
opam install coq-X --dry-run

# Or use opam-depext to install OS-level dependencies first
opam depext coq-X
opam install coq-X
```

### `Error: Cannot find library Foo in loadpath`

The library is either not installed or not in the Rocq load path. Check:

```bash
# Is the package installed?
opam list | grep coq-foo

# Add the library path explicitly to the file:
# Add-LoadPath "/path/to/lib" as Foo.
# Or, preferred: configure _CoqProject (see rocq-dune skill)
```

## Anti-Patterns

**MUST NOT** do any of the following:

- **Install Rocq into the default opam switch.** Version conflicts across
  projects become inevitable. Always use a project-specific or version-specific
  switch.

- **Manually copy `.vo` files between projects or switches.** `.vo` files encode
  the Rocq version that compiled them. Copying them causes `Inconsistent
  assumptions` errors.

- **Run VSCode without `eval $(opam env)` active in the launching terminal.**
  The LSP server will not be found, and the Goals panel will be silent.

- **Mix Rocq packages from different opam repositories without version pins.**
  `opam install coq coq-mathcomp-ssreflect` without explicit versions will
  install whatever is newest in the default repo, which may be incompatible.

- **Use `coq` and `rocq-prover` package names interchangeably in opam scripts.**
  `rocq-prover` is the new package name for Rocq 9.x; `coq` covers 8.x. They
  do not conflict but must not both be specified as dependencies in one opam file.

- **Use `From Coq Require Import` in new Rocq 9.x code.** This still works (with
  a deprecation warning) but `From Stdlib Require Import` is the correct form for
  9.x. Using the old form will break when the compat shim is removed in a future release.

- **Ignore opam conflict messages and use `--ignore-constraints`.** Forcing
  incompatible packages produces silent elaboration failures inside Rocq that
  are extremely difficult to debug.

## Verification Checklist

**MUST** confirm all of the following before beginning proof development:

- [ ] `rocq --version` (or `coqc --version`) prints the expected version
- [ ] `eval $(opam env)` is in the shell's startup file (`.bashrc` / `.zshrc`) or `.envrc`
- [ ] `rocq -e 'From Stdlib Require Import Arith. Check Nat.add_comm.'` exits with code 0
- [ ] Installed library loads cleanly: `rocq -e 'From mathcomp Require Import ssreflect.'`
- [ ] `rocq-lsp --version` prints the correct rocq-lsp version
- [ ] Editor (VSCode Goals panel or Proof General) displays goals for a trivial `.v` file
- [ ] Project `opam` file exists and `opam install . --deps-only` succeeds
- [ ] `.vscode/settings.json` (or `.dir-locals.el`) is committed to the repository
- [ ] For Rocq 9.x: project opam file depends on `rocq-prover` (not `coq`)
