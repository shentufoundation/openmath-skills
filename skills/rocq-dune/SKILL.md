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

Dune is the standard build system for Rocq projects. It replaces the legacy
`coq_makefile` approach with composable, incremental, dependency-aware builds.
This skill covers all Rocq-specific Dune stanzas and common project layouts.

## Minimum Required Files

Every Dune-based Rocq project needs exactly two files at the root:

```
my-project/
├── dune-project       ← declares Dune and Rocq language versions
└── theories/
    ├── dune           ← declares the coq.theory stanza
    └── MyFile.v
```

### `dune-project`

```scheme
(lang dune 3.20)
(using coq 0.8)   ; enables coq.theory and all coq.* stanzas
```

**MUST** specify `(using coq 0.8)` (or higher) to unlock `coq.theory`,
`coq.extraction`, and `coq.pp` stanzas. Without it, Dune silently ignores
all Rocq-specific stanzas and produces no `.vo` files.

**MUST NOT** use `(using coq 0.1)` through `(using coq 0.7)` for new projects —
these are deprecated experimental versions. Use `0.8` as the stable baseline.

### Coq Language Version Reference

| Version | Feature unlocked |
|---|---|
| `0.8` | Stable baseline: `coq.theory`, `coq.extraction`, installed theory composition, `vos` builds |
| `0.9` | Per-module flags: `(modules_flags ...)` |
| `0.10` | Custom `coqdep` flags: `(coqdep_flags ...)` |

Use the lowest version that provides the features you need — this maximises
compatibility with older Dune versions.

## `coq.theory` Stanza

The `coq.theory` stanza builds all `.v` files in a directory (and optionally
its subdirectories) into a named Rocq theory.

### Full Field Reference

```scheme
(coq.theory
 (name <module_prefix>)           ; REQUIRED: dot-separated, e.g. MyProject.Core
 (package <opam_package_name>)    ; makes theory public and generates install rules
 (synopsis "Short description")   ; human-readable label
 (modules <module_list>)          ; default :standard (all .v files)
 (theories <dep_theories>)        ; other coq.theory names this depends on
 (plugins <ocaml_plugins>)        ; OCaml plugins this theory loads
 (flags <coq_flags>)              ; extra flags passed to coqc
 (modules_flags <flags_map>)      ; per-module flag overrides (requires coq 0.9)
 (coqdep_flags <coqdep_flags>)    ; extra coqdep flags (requires coq 0.10)
 (coqdoc_flags <coqdoc_flags>)    ; extra coqdoc flags
 (stdlib <yes|no>)                ; default yes; set no to exclude Coq stdlib
 (mode <vo|vos>))                 ; default: auto-detected from Rocq config
```

### Minimal Private Theory (no installation)

```scheme
; theories/dune
(coq.theory
 (name MyProject))
```

All `.v` files in `theories/` are compiled as `MyProject.FileName`.

### Public Theory (installs via opam)

```scheme
; dune-project
(lang dune 3.20)
(using coq 0.8)
(package
 (name coq-my-project)
 (synopsis "My Rocq project")
 ; For Rocq 8.x:
 ; (depends coq (>= "8.20"))
 ; For Rocq 9.x (use rocq-prover, not coq):
 (depends rocq-prover (>= "9.0")))

; theories/dune
(coq.theory
 (name MyProject)
 (package coq-my-project)
 (synopsis "MyProject theories"))
```

**MUST** use `rocq-prover` (not `coq`) as the opam dependency name for Rocq 9.x
projects. The `coq` opam package only covers 8.x releases. For projects that need
to support both 8.x and 9.x, use a disjunction in the `depends` field — see the
`rocq-setup` skill for the opam file pattern.

**MUST** add `(package ...)` to `coq.theory` for any theory that will be
installed or depended upon by other packages. A theory without `(package ...)`
is private — it cannot be referenced from outside its `dune-project` scope.

## Subdirectory Module Qualification

By default, Dune only includes `.v` files in the same directory as the `dune`
file. To include subdirectories with qualified module names:

```scheme
; theories/dune
(include_subdirs qualified)
(coq.theory
 (name MyProject))
```

With `(include_subdirs qualified)`:

- `theories/Core.v` → module `MyProject.Core`
- `theories/Data/List.v` → module `MyProject.Data.List`
- `theories/Data/Tree.v` → module `MyProject.Data.Tree`

**MUST** add `(include_subdirs qualified)` before `(coq.theory ...)` in the
same `dune` file — it applies to the entire directory, not per-stanza.

**MUST NOT** add `(include_subdirs qualified)` to intermediate subdirectory
`dune` files — it belongs only in the top-level `dune` file of the theory root.

## Inter-Theory Dependencies

### Dependencies in the Same Workspace

```scheme
; lib/dune
(coq.theory
 (name MyLib))

; theories/dune
(coq.theory
 (name MyProject)
 (theories MyLib))    ; depend on MyLib defined above
```

In `.v` files:

```coq
From MyLib Require Import SomeModule.
```

Dune resolves inter-theory dependencies with fine granularity: only the files
actually needed are compiled, not the whole depended theory.

### Dependencies on Installed Theories (MathComp, Equations, etc.)

```scheme
(coq.theory
 (name MyProject)
 (theories
  mathcomp.ssreflect      ; From mathcomp Require Import ssreflect.
  mathcomp.algebra        ; From mathcomp Require Import all_algebra.
  Equations.Prop          ; From Equations Require Import Equations.
  ))
```

**MUST** use the exact theory name as installed, not the opam package name.
The theory name is the directory path under `user-contrib/` in the Rocq
installation. Verify with:

```bash
ls $(coqc -config | grep COQPATH | cut -d= -f2)/
ls $(coqc -config | grep COQLIB | cut -d= -f2)/user-contrib/
```

Common installed theory names:

| opam package | Theory name in `(theories ...)` |
|---|---|
| `coq-mathcomp-ssreflect` | `mathcomp.ssreflect` |
| `coq-mathcomp-algebra` | `mathcomp.algebra` |
| `coq-equations` | `Equations.Prop` |
| `coq-stdpp` | `stdpp` |
| `coq-flocq` | `Flocq` |
| `coq-vst` | `VST` |

### Multi-Scope Composition

To compose two independent Dune projects (e.g., a library sub-project
and a main project in the same repo), nest them under a shared `dune-project`:

```
workspace/
├── dune-project         ← top-level scope
├── mylib/
│   ├── dune-project     ← sub-scope (makes mylib public to workspace)
│   ├── mylib.opam
│   └── theories/dune
└── main/
    └── theories/dune    ← can depend on mylib's public theories
```

The `main/theories/dune` depends on `mylib` theory by name:

```scheme
(coq.theory
 (name Main)
 (theories MyLib))
```

## Selective Module Inclusion

Exclude specific files from a theory:

```scheme
(coq.theory
 (name MyProject)
 (modules :standard \ Scratch Experiments))  ; exclude Scratch.v and Experiments.v
```

Include only specific files:

```scheme
(coq.theory
 (name MyProject)
 (modules Core Data.List Data.Tree))   ; only these three modules
```

## Per-Module Flags (requires `coq 0.9`)

Override compiler flags for specific files:

```scheme
(coq.theory
 (name MyProject)
 (modules_flags
  (SlowProof (:standard -async-proofs-j 1))   ; disable parallel checking
  (NativeFile (:standard -native-compiler yes))))
```

`:standard` expands to the theory's default `(flags ...)` value, so
`(:standard <extra>)` adds to the defaults rather than replacing them.

## Compiler Flags

Global flags for all `.v` files in a theory:

```scheme
(coq.theory
 (name MyProject)
 (flags :standard -w -notation-incompatible-format))

; or silence all warnings:
(coq.theory
 (name MyProject)
 (flags :standard -w all))
```

Set workspace-wide defaults in `dune-project` (applies to all theories):

```scheme
(env
 (dev (coq (flags :standard -w +all))))
```

## `coq.extraction` Stanza

The `coq.extraction` stanza drives OCaml extraction as part of the Dune build.
See `rocq-extraction` skill for the Rocq-side `Extraction` commands.

```scheme
; Place in the same dune file as the theory that contains the extraction commands

(coq.extraction
 (prelude Extraction)           ; the .v file containing Extraction commands
                                ; (without .v extension, relative module name)
 (extracted_modules             ; EXHAUSTIVE list of all .ml files produced
  MyAlgo
  MyAlgoAux
  MyDataType)
 (theories MyProject)           ; theories the prelude file depends on
 (flags :standard))

; The extracted .ml files can now be used in OCaml stanzas:
(library
 (name my_certified_lib)
 (modules MyAlgo MyAlgoAux MyDataType))

(executable
 (name runner)
 (libraries my_certified_lib))
```

**MUST** list every `.ml` file that the extraction produces in
`(extracted_modules ...)`. Dune cannot discover these automatically — an
incomplete list causes missing module errors at the OCaml compilation step.

**MUST NOT** use Rocq's `Cd` command in the prelude file. It is deprecated
since Rocq 8.12 and incompatible with Dune's extraction. Dune controls the
output directory.

**MUST NOT** mix `Extraction Library` (which extracts whole modules) with the
`coq.extraction` stanza in a way that produces files outside the prelude's
directory. All extracted files are written to the directory containing the
prelude `.v` file.

## `coq.pp` Stanza (Plugin Grammar Preprocessing)

For Rocq plugins that extend the grammar via `.mlg` files:

```scheme
; src/dune
(library
 (name my_plugin)
 (public_name my-coq-plugin.plugin)
 (libraries coq-core.vernac))

(coq.pp
 (modules syntax))   ; preprocesses src/syntax.mlg → src/syntax.ml
```

**MUST** create an empty `my_plugin.mlpack` file in the same directory as the
library — `coqdep` uses it to detect plugin presence and will silently
fail to build the plugin without it.

## Building a Rocq Plugin (Full Layout)

```
my-coq-plugin/
├── dune-project
├── my-coq-plugin.opam
├── src/
│   ├── dune
│   ├── my_plugin.ml
│   ├── my_plugin.mlpack     ← empty file, required by coqdep
│   └── syntax.mlg
└── theories/
    ├── dune
    └── UsingPlugin.v
```

```scheme
; dune-project
(lang dune 3.20)
(using coq 0.8)
(package
 (name my-coq-plugin)
 (depends coq-core))

; src/dune
(library
 (name my_plugin)
 (public_name my-coq-plugin.plugin)
 (flags :standard -rectypes -w -27)
 (libraries coq-core.vernac))
(coq.pp (modules syntax))

; theories/dune
(coq.theory
 (name MyPlugin)
 (package my-coq-plugin)
 (plugins my-coq-plugin.plugin))
```

In `UsingPlugin.v` (Rocq 8.17+):

```coq
Declare ML Module "my-coq-plugin.plugin".
```

## Build Commands

```bash
# Build everything
dune build

# Build a specific theory (by directory target)
dune build theories/

# Build a specific file
dune build theories/MyProject/Core.vo

# Build only compiled interfaces (fast: skips proof checking)
# Requires (mode vos) in coq.theory or dune coq top
dune build @vos

# Build HTML documentation for theory MyProject
dune build theories/MyProject.html/

# Build LaTeX documentation
dune build theories/MyProject.tex/

# Build all HTML documentation targets in workspace
dune build @doc

# Clean build artifacts
dune clean
```

## Fast Proof Checking with `vos` Mode

`.vos` files are compiled interface files — they are built without checking
proofs, making dependency compilation much faster during development.

```scheme
(coq.theory
 (name MyProject)
 (mode vos))    ; produce .vos instead of .vo
```

**MUST NOT** ship a library with `(mode vos)` — `.vos` files do not contain
verified proofs. Use `vos` only in development/editor-integration scenarios,
then remove or guard with an env condition before release:

```scheme
(env
 (dev  (coq (flags :standard)))          ; vo mode for dev
 (release (coq (flags :standard -vos)))) ; never — keep release as vo
```

## `dune coq top` for Editor Integration

`dune coq top` starts `coqtop` (or another toplevel) with the correct flags
for a specific file, rebuilding dependencies as needed:

```bash
# Start coqtop for theories/MyProject/Core.v
dune coq top theories/MyProject/Core.v

# Pass -emacs flag (required by Proof General)
dune coq top theories/MyProject/Core.v -- -emacs

# Skip rebuilding dependencies (fast restart)
dune coq top --no-build theories/MyProject/Core.v

# Inspect flags that would be passed (debugging)
dune coq top --toplevel echo theories/MyProject/Core.v
```

**MUST** configure editors to invoke `dune coq top` rather than bare `coqtop`
— otherwise Rocq cannot find the project's theories and gives `Cannot find
library` errors.

For `rocq-lsp` (VSCode) — recommended configuration for Dune projects:

```json
{
  "coq-lsp.server_command": "dune exec -- rocq-lsp"
}
```

This ensures rocq-lsp is launched through Dune and can find the project's
theories without needing a separate `_CoqProject` file.

For Proof General (Emacs):

```elisp
(setq coq-prog-name
      (concat "dune coq top "
              (buffer-file-name)
              " -- "))
```

## `_CoqProject` Compatibility File

Some tools (CoqIDE, older Proof General, `coqdoc` standalone) require a
`_CoqProject` file. Dune does not generate this automatically. Add it manually
to the project root:

```
# _CoqProject
-R theories MyProject
-Q lib MyLib
```

**MUST NOT** put `_CoqProject` under version control if it would diverge from
the Dune build — it is a compatibility shim, not the source of truth.
Alternatively, generate it as a Dune rule:

```scheme
; dune (at project root)
(rule
 (targets _CoqProject)
 (action (write-file _CoqProject "-R theories MyProject\n")))
```

## Project Skeletons

### Minimal Single-Theory Project

```
my-project/
├── dune-project
└── theories/
    ├── dune
    └── Main.v
```

```scheme
; dune-project
(lang dune 3.20)
(using coq 0.8)

; theories/dune
(coq.theory
 (name MyProject))
```

### Library + Extraction + Compiled OCaml

```
my-project/
├── dune-project
├── my-project.opam
├── theories/
│   ├── dune
│   ├── Core.v
│   └── Extract.v          ← contains Extraction commands
└── extracted/
    └── dune               ← coq.extraction + library stanzas
```

```scheme
; theories/dune
(include_subdirs qualified)
(coq.theory
 (name MyProject)
 (package my-project))

; extracted/dune
(coq.extraction
 (prelude ../theories/Extract)
 (extracted_modules MyAlgo)
 (theories MyProject))

(library
 (name my_algo_lib)
 (modules MyAlgo))
```

### MathComp-Based Project

```scheme
; dune-project
(lang dune 3.20)
(using coq 0.8)

; theories/dune
(include_subdirs qualified)
(coq.theory
 (name MyMCProject)
 (theories
  mathcomp.ssreflect
  mathcomp.algebra))
```

## Anti-Patterns

**MUST NOT** do any of the following:

- **Omit `(using coq 0.8)` from `dune-project`.** Dune silently skips all
  `coq.*` stanzas and produces no `.vo` files with no error.

- **Use `coq_makefile` and Dune in the same project simultaneously.** They
  write `.vo` files to different locations and will corrupt each other's caches.

- **Reference a private theory from outside its `dune-project` scope.** Add
  `(package ...)` to make it public first, or the dependent build will fail
  with a theory-not-found error.

- **Omit `my_plugin.mlpack` when building a plugin.** `coqdep` looks for this
  file to detect plugin presence — without it, `coqdep` silently skips the
  dependency and the plugin is not loaded at runtime.

- **Use `Declare ML Module "my_plugin"` (old name syntax) on Rocq 8.17+.**
  Use the findlib public name syntax: `Declare ML Module "my-coq-plugin.plugin"`.

- **Use `(mode vos)` in a released library.** `.vos` files do not contain
  verified proofs. A downstream user who `opam install`s a `vos`-mode library
  gets unverified objects silently.

- **Forget `(extracted_modules ...)` or list fewer files than extraction
  produces.** The OCaml compilation step will report missing modules with no
  indication that extraction is the cause.

- **Use `Cd "path"` in an extraction prelude file.** This command is deprecated
  since Rocq 8.12 and incompatible with Dune. Dune controls all output paths.

- **Manually invoke `coqc` on files that Dune manages.** Dune's dependency
  tracking will not see the manually produced `.vo` files and may overwrite or
  ignore them in subsequent builds.

## Verification Checklist

**MUST** confirm all of the following before considering the build setup complete:

- [ ] `dune build` exits with code 0 and produces `.vo` files in `_build/default/`
- [ ] `dune clean && dune build` succeeds (no stale `.vo` dependency issues)
- [ ] All `From <Theory> Require Import` in `.v` files resolve to a `(theories ...)` entry or installed theory
- [ ] `(package ...)` is set on every `coq.theory` that other packages will depend on
- [ ] `(include_subdirs qualified)` is present for multi-directory theories
- [ ] `my_plugin.mlpack` exists for every Rocq plugin library
- [ ] `dune coq top theories/SomeFile.v` launches `coqtop` without "Cannot find library" errors
- [ ] `(mode vos)` is absent from all release-targeted `coq.theory` stanzas
- [ ] `extracted_modules` lists all `.ml` files produced by extraction (verified by `dune build` with no missing module errors)
