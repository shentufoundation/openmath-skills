
# Building and Installing Mathematical Components

Mathematical Components (MathComp) is the largest structured Rocq library in
active use. It is distributed as a set of separate opam packages under the
`coq-mathcomp-*` prefix. This skill covers installing and building MathComp and
its ecosystem; for proof methodology see `rocq-ssreflect`.

## Package Architecture

MathComp is split into fine-grained packages. Install only what you need —
the full dependency chain is large.

```
coq-mathcomp-ssreflect          ← base: ssreflect, seq, fintype, bigop, ...
  └─ coq-mathcomp-fingroup       ← group theory: groups, morphisms, quotients
       └─ coq-mathcomp-algebra   ← rings, fields, linear algebra, polynomials
            └─ coq-mathcomp-solvable  ← solvable groups
                 └─ coq-mathcomp-field     ← field extensions, Galois theory
                      └─ coq-mathcomp-character  ← character theory
```

Extensions (depend on the base stack above):

| opam package | Content |
|---|---|
| `coq-mathcomp-finmap` | Finite sets, finite maps, multisets |
| `coq-mathcomp-multinomials` | Multivariate polynomials |
| `coq-mathcomp-real-closed` | Real closed fields |
| `coq-mathcomp-classical` | Classical reasoning layer (needed for Analysis) |
| `coq-mathcomp-analysis` | Real analysis, topology, measure theory |
| `coq-mathcomp-algebra-tactics` | `ring` and `linarith` for MathComp types |
| `coq-hierarchy-builder` | HB: algebraic hierarchy DSL |
| `coq-mathcomp-odd-order` | Feit-Thompson (Odd Order) theorem |
| `coq-fourcolor` | Four Colour theorem |

## Method 1: Install via opam (Standard)

### Ensure the Rocq opam repository is added

```bash
# Add the released package repository (required if not using Rocq Platform)
opam repo add coq-released https://coq.inria.fr/opam/released --all-switches

# Verify it is listed
opam repo list
```

**MUST** have `coq-released` in the active switch's repository list. Without
it, `coq-mathcomp-*` packages are not found.

### Install the base library

```bash
# Activate the correct switch first
eval $(opam env --switch=rocq-9.1)

# Pin Rocq version before installing MathComp (strongly recommended)
# For Rocq 9.x:
opam pin add -n rocq-prover -k version 9.1.0
# For Rocq 8.x:
opam pin add -n coq -k version 8.20.0

# Install MathComp 2.3.x (works with Rocq 9.x and 8.20)
opam install coq-mathcomp-ssreflect -j$(nproc)

# Install the full base stack (algebra included)
opam install coq-mathcomp-algebra -j$(nproc)
# opam resolves the entire dependency chain automatically

# Install common extensions
opam install \
  coq-mathcomp-finmap \
  coq-mathcomp-algebra-tactics \
  coq-hierarchy-builder \
  -j$(nproc)

# Install the analysis stack (large — allocate 20+ min)
opam install coq-mathcomp-analysis -j$(nproc)
```

**MUST** pin Rocq to a specific version before installing MathComp. Without
pinning, opam may downgrade or upgrade Rocq to satisfy MathComp's constraints,
silently invalidating other installed packages.

**SHOULD** use `-j$(nproc)` (Linux) or `-j$(sysctl -n hw.ncpu)` (macOS) to
parallelise the build across all available cores.

### Check what is installed

```bash
opam list | grep coq-mathcomp
# or for a single package:
opam info coq-mathcomp-ssreflect
```

### Version Compatibility Matrix

| MathComp | Rocq / Coq | OCaml | HB | Notes |
|---|---|---|---|---|
| 2.3.x | 9.1 / 9.0 / 8.20 | 5.2 / 4.14 | ≥ 1.8.0 | Current (Nov 2024); recommended for Rocq 9.x |
| 2.2.x | 8.19 / 8.20 | 4.14 | ≥ 1.6.0 | Stable; widely used with 8.x |
| 2.1.x | 8.18 / 8.19 | 4.14 | ≥ 1.5.0 | Legacy |
| 1.19.x | 8.17 / 8.18 | 4.14 | ≥ 1.4.0 | Older; avoid for new projects |

**MUST** check `opam info coq-mathcomp-ssreflect` for the exact version
constraints before fixing your Rocq pin — the table above is indicative and
versions change with new releases.

## Method 2: Install Dev Version

```bash
# Add the extra-dev repository
opam repo add coq-extra-dev https://coq.inria.fr/opam/extra-dev --all-switches

# Install the development (HEAD) version
opam install coq-mathcomp-ssreflect.dev -j$(nproc)
```

**MUST NOT** use `.dev` in a production or reproducibility-sensitive environment.
Dev builds track `master` and may break without notice.

## Method 3: Build from Source with opam pin

Use this when you need a specific commit or a local patch:

```bash
# Clone the source
git clone https://github.com/math-comp/math-comp.git
cd math-comp

# Pin all packages in the repo to the local checkout
for P in *.opam; do
  opam pin add -n -k path "${P%.opam}" . --yes
done

# Install the target package (pulls in all dependencies)
opam install coq-mathcomp-algebra -j$(nproc)
```

To unpin after development:

```bash
for P in *.opam; do
  opam unpin "${P%.opam}"
done
```

## Method 4: Build from Source with make

Use when opam is unavailable (CI containers, nix environments) or you need
to inspect compiled output directly.

```bash
# Prerequisites: coqc must be in PATH
coqc --version   # confirm Rocq is available

# Clone and build
git clone https://github.com/math-comp/math-comp.git
cd math-comp/mathcomp

# Build all packages
make -j$(nproc)

# Build a specific package only
make -j$(nproc) ssreflect
make -j$(nproc) algebra

# Install into the Rocq load path
make install
```

Available make targets (correspond to subdirectories):

| Target | Content |
|---|---|
| `ssreflect` | Base: seq, fintype, bigop, div, prime |
| `fingroup` | Groups, cosets, morphisms |
| `algebra` | Rings, modules, polynomials, matrices |
| `solvable` | Sylow, Burnside, solvable groups |
| `field` | Field extensions, Galois |
| `character` | Characters, representations |

**SHOULD** prefer the opam method unless you have a concrete reason to use
`make` — opam handles `.vo` installation into the correct load path
automatically; `make install` requires `COQLIBINSTALL` to be set correctly
on non-standard Rocq installations.

## Hierarchy Builder (HB)

HB is the meta-language for defining MathComp-style algebraic hierarchies.
All MathComp ≥ 1.14 and MathComp Analysis use HB. Any project extending or
building on the MathComp hierarchy MUST install HB.

```bash
opam install coq-hierarchy-builder
```

### HB Import

```coq
From HB Require Import structures.
```

### Core HB Vernaculars (build-time awareness)

HB vernaculars are processed at `Require` time and produce canonical instances.
Build failures in HB-using files typically manifest as:

- `No instance found for ...` — an HB structure is not exported/installed
- `Illegal application` at instance synthesis — HB version mismatch
- `Unknown notation` — `From HB Require Import structures` is missing

```bash
# Check HB version in the active switch
opam info coq-hierarchy-builder | grep version
```

**MUST** ensure `coq-hierarchy-builder` version is compatible with the
MathComp version installed. Mismatches cause synthesis failures that look
like Rocq type errors, not build system errors.

| MathComp | HB version required | Rocq compatibility |
|---|---|---|
| 2.3.x | ≥ 1.8.0 | Rocq 9.1 / 9.0 / Coq 8.20 |
| 2.2.x | ≥ 1.6.0 | Coq 8.19 / 8.20 |
| 2.1.x | ≥ 1.5.0 | Coq 8.18 / 8.19 |

## Reducing Build Verbosity

MathComp builds produce large volumes of output by default. Suppress when
building in CI or checking specific files:

```bash
# opam build: suppress coqc output
opam install coq-mathcomp-algebra -j$(nproc) 2>&1 | grep -E '(ERROR|error|warning)'

# make build: suppress per-file progress
make -j$(nproc) COQFLAGS="-q" ssreflect

# dune build (for projects using MathComp as a dependency): reduce verbosity
dune build -j$(nproc) --display short 2>&1 | grep -v "^\s*rocq"
```

For CI pipelines, redirect full output to a log file and surface only errors:

```bash
dune build 2>&1 | tee build.log | grep -E '(Error:|error:|File.*line)' || true
```

## Building Only Affected Files (Incremental)

When working on a project that depends on MathComp, build only the changed
Rocq files rather than the full library:

```bash
# dune: build a specific theory file
dune build theories/MyProof.vo

# dune: build only one subdirectory
dune build theories/Algebra/

# make (in math-comp source): force rebuild of one file
touch ssreflect/ssreflect.v
make ssreflect/ssreflect.vo
```

For small fixes in a large project it is often fine to leave a full
recompilation to CI. Only rebuild locally if you need to iterate quickly on
a specific lemma.

## Verifying the Installation

After installing, confirm MathComp is accessible from Rocq:

```bash
# Quick smoke test: load ssreflect
rocq -e 'From mathcomp Require Import ssreflect. Check leq_add.'

# Load the algebra stack
rocq -e 'From mathcomp Require Import all_algebra. Check GRing.addr0.'

# Check the installed .vo path
coqc -config | grep COQPATH
ls $(coqc -config | grep 'COQPATH' | cut -d= -f2 | tr ':' '\n' | head -1)/mathcomp/
```

All three commands MUST succeed before using MathComp in a proof file.

## Updating MathComp

```bash
# Update the opam package index
opam update

# Upgrade MathComp packages (respects pinned Rocq version)
opam upgrade coq-mathcomp-ssreflect coq-mathcomp-algebra

# Upgrade the entire switch (careful — may update Rocq itself)
opam upgrade
```

**MUST NOT** run `opam upgrade` without reviewing the proposed changes first:

```bash
# Dry run: show what would change, do not apply
opam upgrade --dry-run
```

If Rocq itself is in the upgrade set and you do not intend to change its
version, cancel and pin it explicitly:

```bash
opam pin add coq $(opam info coq --field=installed-version | tr -d ' ')
```

## Troubleshooting

### `coq-mathcomp-ssreflect` not found by opam

```bash
# The coq-released repository is missing
opam repo list   # check output for 'coq-released'
opam repo add coq-released https://coq.inria.fr/opam/released
opam update
opam install coq-mathcomp-ssreflect
```

### `Inconsistent assumptions over ...` when loading MathComp

The `.vo` files were compiled with a different Rocq version than the current
one. Reinstall MathComp to recompile against the active Rocq:

```bash
opam reinstall coq-mathcomp-ssreflect coq-mathcomp-algebra
```

If the error persists after reinstall, the active switch may have an
inconsistency between the `coq` binary and the `coq-mathcomp-*` packages:

```bash
opam list coq coq-mathcomp-ssreflect   # compare version constraints
opam install coq-mathcomp-ssreflect --dry-run  # check proposed changes
```

### `Cannot find library mathcomp.ssreflect` in Rocq

The library is installed but not in the current load path. Confirm:

```bash
coqc -config | grep COQPATH
# If empty or not pointing to the opam prefix:
eval $(opam env)    # re-source opam environment
which coqc          # must be inside the opam switch prefix
```

If using Dune, ensure `(theories mathcomp.ssreflect)` is in the `coq.theory`
stanza (see `rocq-dune` skill).

### `No instance found for GRing.Ring ...` (HB synthesis failure)

```bash
# Check HB version compatibility
opam info coq-hierarchy-builder | grep installed
opam info coq-mathcomp-algebra  | grep depends
# If HB version is below the required minimum:
opam upgrade coq-hierarchy-builder
```

Also confirm the file imports HB before MathComp algebra modules:

```coq
From HB Require Import structures.   (* MUST come before algebra imports *)
From mathcomp Require Import all_algebra.
```

### Build takes too long / runs out of memory

```bash
# Reduce parallelism (each coqc process uses ~1-2 GB RAM)
opam install coq-mathcomp-algebra -j2   # instead of -j$(nproc)

# For make builds:
make -j2 algebra
```

## Anti-Patterns

**MUST NOT** do any of the following:

- **Run `opam upgrade` without `--dry-run` first.** MathComp upgrades can pull
  in a new Rocq minor version and invalidate all other `.vo` caches in the switch.

- **Mix MathComp versions in one switch.** E.g., `coq-mathcomp-ssreflect 2.2`
  with `coq-mathcomp-algebra 2.3` is not supported and produces `Inconsistent
  assumptions` errors at `Require` time.

- **Import MathComp modules without `Set Implicit Arguments.`** See
  `rocq-ssreflect` skill. Build succeeds but proofs fail with confusing
  unification errors.

- **Use `Require Import mathcomp.ssreflect.ssreflect` (old path syntax).**
  Use `From mathcomp Require Import ssreflect` — the qualified `From` syntax
  is the supported form and is immune to COQPATH ordering.

- **Install `coq-mathcomp-*` packages without pinning the Rocq version first.**
  opam may silently downgrade Rocq to satisfy MathComp's constraints,
  breaking other packages in the switch.

- **Copy `.vo` files from a different switch or machine.** `.vo` files encode
  the exact Rocq binary that compiled them. Cross-switch copying always causes
  `Inconsistent assumptions`.

- **Use `make install` without setting `COQLIBINSTALL`.** On a non-standard
  Rocq install, `make install` drops `.vo` files in the wrong location and
  they are not found by `coqc`. Use opam instead, or set:

  ```bash
  make install COQLIBINSTALL=$(coqc -config | grep COQLIB | cut -d= -f2)/user-contrib
  ```

## Verification Checklist

**MUST** confirm all of the following before using MathComp in a project:

- [ ] `opam list | grep coq-mathcomp` shows all required packages at compatible versions
- [ ] `rocq -e 'From mathcomp Require Import ssreflect. Check leq_add.'` exits with code 0
- [ ] HB is installed and at a compatible version: `opam info coq-hierarchy-builder`
- [ ] `coq-hierarchy-builder` version satisfies the MathComp version's dependency bound (2.3.x → HB ≥ 1.8.0)
- [ ] No `Inconsistent assumptions` on `Require` (confirms `.vo` / Rocq version match)
- [ ] `eval $(opam env)` is active in the shell used to invoke `rocq` / `dune` / editors
- [ ] Project `opam` file declares `coq-mathcomp-*` dependencies with explicit version bounds
- [ ] For Rocq 9.x: project depends on `rocq-prover` (not `coq`) with appropriate version bounds
