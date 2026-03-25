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

Use this skill to get a Rocq environment healthy before touching proof scripts
or Dune configuration. Keep `SKILL.md` for the default setup sequence; use the
full guide for version matrices, editor snippets, and troubleshooting detail.

## Instructions

- Decide first whether the job is a fresh install, a project-local switch, or
  a repair of an existing environment.
- Prefer Rocq Platform for a new general-purpose setup; choose manual opam
  installation only when you need tight version control.
- Always work in a dedicated opam switch for the project.
- Verify the toolchain before configuring editors or adding libraries.
- Add project-local persistence only after the switch and binaries are known to
  work.
- If the environment is broken, fix the active switch and load path before
  editing proof files.

## Workflow Checklist

1. Confirm whether the target is Rocq 9.x or an older 8.x-compatible stack.
2. Install or select an opam switch for that target version.
3. Install `rocq-prover` or the Rocq Platform bundle.
4. Verify `rocq`, `coqc`, and `rocq-lsp` in the active shell.
5. Add editor integration and project-local switch persistence only after basic
   commands succeed.
6. Install extra libraries and packages one layer at a time.

## Notes

- `rocq-dune` handles build-system setup after the environment is healthy.
- Import-prefix migration, editor configuration, and troubleshooting are kept in
  [references/guide.md](references/guide.md) so the entrypoint stays short.
- Do not mix global and project-specific switch logic in the same debugging pass.

## References

- [guide.md](references/guide.md)
