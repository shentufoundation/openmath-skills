---
name: rocq-dune
version: 0.1.0
description: >
  Use when setting up or maintaining a Rocq project build system with Dune:
  creating dune-project and dune files, configuring coq.theory stanzas,
  managing inter-theory dependencies, composing with installed libraries
  (MathComp, Equations, etc.), building plugins, setting up coq.extraction
  stanzas, generating coqdoc documentation, and running dune coq top for
  editor integration. Assumes the environment is already configured (see
  rocq-setup). Complements rocq-extraction for the extraction workflow.
tags: [rocq, coq, dune, build-system, coq-theory, plugin, extraction, toolchain]
agent-support: [claude-code, cursor, gemini-cli, codex, cline]
---

# Rocq Build System with Dune

Use this skill when you need to create or repair a Dune-based Rocq project.
Keep `SKILL.md` for the build-system execution loop, then open the full guide
for stanza field matrices, skeletons, and advanced flags.

## Instructions

- Start from the smallest possible Dune layout: one `dune-project`, one theory
  root, and one `coq.theory` stanza.
- Confirm the Rocq environment is already healthy before debugging Dune.
- Add package metadata, subdirectories, or advanced flags only after the basic
  theory builds.
- Treat opam package names and installed theory names as different identifiers.
- Rebuild the smallest target affected by each change before adding more.
- Use `_CoqProject` compatibility only when you truly need legacy tooling.

## Workflow Checklist

1. Verify the active Rocq switch with `rocq-setup` first.
2. Create or inspect `dune-project` and ensure `(using coq 0.8)` or later.
3. Define a minimal `coq.theory` stanza and make it build.
4. Add same-workspace or installed theory dependencies one layer at a time.
5. Only after a clean build, add extraction, plugin, documentation, or `vos`
   optimizations.
6. Use the verification checklist in [references/guide.md](references/guide.md)
   before declaring the build fixed.

## Notes

- Most Dune failures come from theory naming, load-path assumptions, or adding
  too many features before the minimal build works.
- The full stanza reference, project skeletons, anti-patterns, and command list
  live in [references/guide.md](references/guide.md).
- Keep build-system debugging separate from proof debugging whenever possible.

## References

- [guide.md](references/guide.md)
