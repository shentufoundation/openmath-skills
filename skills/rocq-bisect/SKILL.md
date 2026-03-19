---
name: rocq-bisect
description: >
  Use when identifying which Rocq version or commit introduced a regression
  or behaviour change. Covers release-level bisection with opam switches,
  commit-level bisection with git bisect on the Rocq source, Docker-based
  bisection with coqorg/coq images, writing self-contained test files,
  and interpreting bisection results. Use rocq-mwe to minimise the test
  file first.
tags: [rocq, coq, bisect, regression, opam, git-bisect, docker, debugging, toolchain]
---

# Bisecting Rocq Regressions

Rocq bisection locates the **exact version or commit** that changed a
behaviour — either introducing a bug or fixing one. There are three tiers,
each with increasing resolution and cost:

| Tier | Resolution | Cost | Use when |
|---|---|---|---|
| Release bisection | Between released versions (8.x.y) | Low — opam switches | Unknown which minor release broke it |
| Docker bisection | Between released versions (fast) | Very low — no opam setup | CI / no local opam available |
| Commit bisection | Between individual commits | High — build from source | Release identified; need exact commit |

**MUST** have a self-contained test file before bisecting. See `rocq-mwe`
for minimisation. Test files that depend on MathComp or other libraries
require extra steps (see Library Dependencies section).

## Test File Requirements

A bisection test file MUST be:

1. **Self-contained** — no `From MyProject Require Import`. All definitions
   are inlined or replaced with `Axiom` stubs.
2. **Deterministic** — same input always produces the same pass/fail result.
3. **Fast** — each bisection step runs the full file. Keep it under 5 seconds
   per `coqc` invocation.
4. **Unambiguous** — it either succeeds (exit code 0) or fails with the
   specific error. Do not rely on warning text that may change between versions.

### Test File Patterns

#### Pattern 1: Exit Code Only (simplest)

```coq
(* test.v — fails with the bug, passes without it *)
Lemma regression_example (n : nat) : n + 0 = n.
Proof.
  the_tactic_that_regressed.
Qed.
```

`coqc test.v` exits 0 on versions where the proof works, non-zero where it
fails. Bisect on exit code.

#### Pattern 2: Expect a Specific Error

Use `Set Warnings` + a deliberate failure to detect a specific message:

```coq
(* test.v — passes (exit 0) when the bug IS present,
            fails (exit non-0) when the bug is ABSENT *)
Set Warnings "+my-warning-flag".
(* ... code that triggers the warning *)
```

Or more reliably, wrap in a script that greps for the error string:

```bash
#!/usr/bin/env bash
# test.sh
output=$(coqc -q test.v 2>&1)
echo "$output" | grep -q "the exact error substring"
# exit 0 if string found (bug present), exit 1 if not
```

#### Pattern 3: Expect Compilation Success

```coq
(* test.v — should always compile cleanly on good versions *)
Require Import Coq.Arith.Arith.
Lemma test : forall n : nat, n = n. Proof. reflexivity. Qed.
```

`coqc test.v` exit 0 = "good", non-zero = regression.

**MUST** verify BOTH endpoints before starting bisection:

```bash
# On the known-good version:
GOOD_VER=8.19.2   coqc test.v   # MUST succeed (exit 0)
# On the known-bad version:
BAD_VER=8.20.0    coqc test.v   # MUST fail (exit non-0)
```

Bisecting without confirming endpoints wastes all steps and produces
a misleading result.

## Tier 1: Release Bisection with opam Switches

Create one opam switch per candidate Rocq version and test the file in each.

### Step 1: List Available Rocq Releases

```bash
opam show coq | grep "^all-versions:"
# or more readably:
opam info coq --field=all-versions | tr ' ' '\n' | sort -V
```

Published releases as of March 2026:

```
8.7.0  8.7.1  8.7.2
8.8.0  8.8.1  8.8.2
8.9.0  8.9.1
8.10.0 8.10.1 8.10.2
8.11.0 8.11.1 8.11.2
8.12.0 8.12.1
8.13.0 8.13.1 8.13.2
8.14.0 8.14.1
8.15.0 8.15.1 8.15.2
8.16.0 8.16.1
8.17.0 8.17.1
8.18.0
8.19.0 8.19.1 8.19.2
8.20.0 8.20.1
9.0.0  9.0.1          ← first Rocq-branded release (Mar 2025); opam package: rocq-prover
9.1.0                 ← current stable (Sep 2025); opam package: rocq-prover
```

**Note on Rocq 9.x opam package names**: For version switches involving Rocq 9.x,
use `rocq-prover` (not `coq`) as the package name:

```bash
opam install rocq-prover.9.1.0 --switch=rocq-9.1
# coqc still available as a compatibility shim (same binary)
```

### Step 2: Create Switches for the Candidate Range

```bash
# Example: narrowing between 8.20 and 9.1 (spanning the 8.x/9.x boundary)
for VER in 8.20.0 8.20.1 9.0.0 9.0.1 9.1.0; do
  opam switch create rocq-$VER ocaml-base-compiler.4.14.2 -y --no-switch
  # Use 'coq' package name for 8.x, 'rocq-prover' for 9.x
  case $VER in
    8.*) opam install coq.$VER --switch=rocq-$VER -y ;;
    9.*) opam install rocq-prover.$VER --switch=rocq-$VER -y ;;
  esac
done
```

**SHOULD** create all candidate switches before testing — switches can be
created in parallel or in background while you work.

### Step 3: Test Each Version

```bash
for VER in 8.20.0 8.20.1 9.0.0 9.0.1 9.1.0; do
  # coqc is a compatibility shim in 9.x; works for both 8.x and 9.x
  result=$(opam exec --switch=rocq-$VER -- coqc -q test.v 2>&1)
  if [ $? -eq 0 ]; then
    echo "PASS  $VER"
  else
    echo "FAIL  $VER"
    echo "  $result" | head -3
  fi
done
```

The first `FAIL` in the sequence (when scanning good→bad) marks the
regressing version. Narrow to the minor release, then use commit bisection
for the exact patch.

### Step 4: Clean Up Switches

```bash
# Remove switches when done (they are large — ~2 GB each)
for VER in 8.20.0 8.20.1 9.0.0 9.0.1 9.1.0; do
  opam switch remove rocq-$VER -y
done
```

**MUST** remove temporary bisection switches after use. Stale switches
accumulate disk space rapidly.

## Tier 2: Docker Bisection (No opam Setup)

Use `coqorg/coq` Docker images when you cannot or do not want to create
opam switches locally. Available tags match released Rocq versions.

```bash
# Available tags: 8.7, 8.8, 8.9, ... 8.20, 9.0, 9.1, dev
# Full list: https://hub.docker.com/r/coqorg/coq/tags

# Test a single version
docker run --rm -v $(pwd):/work -w /work coqorg/coq:8.19 \
  coqc -q test.v && echo "PASS 8.19" || echo "FAIL 8.19"

# Sweep a range spanning 8.x and 9.x
for VER in 8.18 8.19 8.20 9.0 9.1; do
  result=$(docker run --rm -v $(pwd):/work -w /work coqorg/coq:$VER \
    coqc -q test.v 2>&1)
  [ $? -eq 0 ] && echo "PASS $VER" || echo "FAIL $VER: $(echo $result | head -c 120)"
done
```

**MUST** mount the directory containing your test file with `-v $(pwd):/work`.
Docker images do not have access to the host filesystem otherwise.

**Note**: In Rocq 9.x images, `coqc` is still available as a compatibility shim
that delegates to `rocq compile`. Test files using `coqc` work unchanged.

### MathComp + Docker

For test files that require MathComp, use `mathcomp/mathcomp` images which
bundle Rocq + MathComp together:

```bash
# Tags follow the pattern: <mathcomp-version>-coq-<rocq/coq-version>
# Rocq 8.x:  2.2.0-coq-8.20,  2.3.0-coq-8.20
# Rocq 9.x:  2.3.0-coq-9.0,   2.3.0-coq-9.1
docker run --rm -v $(pwd):/work -w /work \
  mathcomp/mathcomp:2.3.0-coq-9.1 \
  coqc -q test_with_mathcomp.v && echo "PASS" || echo "FAIL"
```

Available MathComp image tags: `https://hub.docker.com/r/mathcomp/mathcomp/tags`

## Tier 3: Commit Bisection with `git bisect`

Use when Tier 1/2 has identified the regressing minor release (e.g., between
8.19.2 and 8.20.0) and you need the exact commit.

### Step 1: Clone the Rocq Source

```bash
git clone https://github.com/rocq-prover/rocq.git
cd rocq
```

### Step 2: Identify the Commit Range

```bash
# Find the tags for your two bounding versions
git tag | grep -E "V8\.(19|20)"
# e.g.: V8.19.2  V8.20.0

# Verify the range makes sense
git log --oneline V8.19.2..V8.20.0 | wc -l   # number of commits to bisect
```

For a 1000-commit range, `git bisect` requires ~10 build steps (log₂(1000) ≈ 10).
Each step requires building Rocq from source (~10–30 min per step). Plan accordingly.

### Step 3: Build Helper Script

Create a script that builds Rocq at the current commit and tests it:

```bash
# bisect-test.sh
#!/usr/bin/env bash
set -e

# Build Rocq at the currently checked-out commit
./configure -prefix /tmp/rocq-bisect -native-compiler no 2>/dev/null
make -j$(nproc) -s 2>/dev/null
make install -s 2>/dev/null

# Test with the freshly built coqc
/tmp/rocq-bisect/bin/coqc -q /path/to/test.v
# exit 0 = good, non-0 = bad
```

```bash
chmod +x bisect-test.sh
```

### Step 4: Run `git bisect`

```bash
# Start bisection
git bisect start

# Mark the known-bad version (regression is present)
git bisect bad V8.20.0

# Mark the known-good version (regression is absent)
git bisect good V8.19.2

# Automate: run bisect-test.sh at each candidate commit
git bisect run ./bisect-test.sh
```

`git bisect` will:

1. Check out the commit at the midpoint of the range
2. Run `bisect-test.sh`
3. Record good/bad from the exit code
4. Repeat until the first bad commit is isolated

### Step 5: Interpret the Result

```bash
# When bisection completes, git prints:
# "<commit-hash> is the first bad commit"
# commit <hash>
# Author: ...
# Date:   ...
#     <commit message>

# Confirm the identified commit
git show <commit-hash>

# Clean up bisect state
git bisect reset
```

**MUST** run `git bisect reset` after bisection — without it, git leaves
the repository in a detached HEAD state.

### Skipping Unbuildable Commits

Some commits between two releases may not compile (broken intermediate states):

```bash
# Skip a single commit that does not build
git bisect skip

# Skip a range of known-broken commits
git bisect skip V8.19.2..V8.19.2-broken-range
```

Modify `bisect-test.sh` to distinguish build failures from test failures:

```bash
#!/usr/bin/env bash
# Build
if ! make -j$(nproc) -s 2>/dev/null; then
  exit 125   # exit code 125 = "skip this commit" in git bisect
fi
# Test
/tmp/rocq-bisect/bin/coqc -q /path/to/test.v
```

`exit 125` tells `git bisect run` to skip the current commit rather than
mark it good or bad.

## Library Dependencies in Test Files

Test files that require MathComp or other libraries cannot be used directly
with a plain `coqc test.v` call during bisection — library `.vo` files are
compiled against a specific Rocq version and will cause `Inconsistent
assumptions` on other versions.

### Option A: Minimise Away the Dependency (Best)

Use `rocq-mwe` to inline all MathComp definitions needed for the regression
into the test file itself. This is the most reliable approach and produces
a cleaner bug report.

### Option B: Docker Images with Pre-Built Libraries

Use `mathcomp/mathcomp` images (Tier 2) which bundle a compatible MathComp:

```bash
for TAG in 2.1.0-coq-8.19 2.2.0-coq-8.20; do
  docker run --rm -v $(pwd):/work -w /work \
    mathcomp/mathcomp:$TAG coqc -q test_mathcomp.v \
    && echo "PASS $TAG" || echo "FAIL $TAG"
done
```

### Option C: Per-Version Library Reinstall

For release bisection with opam switches, reinstall MathComp in each switch:

```bash
for VER in 8.20.0 8.20.1 9.0.0 9.1.0; do
  case $VER in
    8.*) opam install coq.$VER coq-mathcomp-ssreflect --switch=rocq-$VER -y ;;
    9.*) opam install rocq-prover.$VER coq-mathcomp-ssreflect --switch=rocq-$VER -y ;;
  esac
  opam exec --switch=rocq-$VER -- coqc -q test_mathcomp.v \
    && echo "PASS $VER" || echo "FAIL $VER"
done
```

**MUST NOT** use the same compiled MathComp `.vo` files across different
Rocq version switches. Each switch needs its own `coq-mathcomp-*` install.

## Bisecting a Fix (Good→Bad Direction)

Sometimes you need to find when a bug was *fixed* (to backport the fix or
understand the change). Git bisect handles this with swapped semantics:

```bash
git bisect start --term-old broken --term-new fixed
git bisect broken V8.19.2    # the bug IS present here
git bisect fixed  V8.20.0    # the bug is ABSENT here
git bisect run ./bisect-test.sh
# Now exit 0 = "bug still present (old)" and non-0 = "bug fixed (new)"
```

Or equivalently, invert the test file's exit code in `bisect-test.sh`:

```bash
# Invert: pass when the bug IS present, fail when it is fixed
/tmp/rocq-bisect/bin/coqc -q /path/to/test.v && exit 1 || exit 0
```

## Reporting the Result

Once the regressing commit or version is identified, include in the bug report:

```
- Last known good: Rocq 8.19.2 (or commit <sha>)
- First known bad: Rocq 8.20.0 (or commit <sha>)
- Bisect result: commit <sha> "<commit message>"
- Test file: <attached mwe.v>
- Reproduction: coqc -q mwe.v  # fails on bad, succeeds on good
```

File the issue at:

- Rocq core regressions: `https://github.com/rocq-prover/rocq/issues`
- MathComp regressions: `https://github.com/math-comp/math-comp/issues`

## Anti-Patterns

**MUST NOT** do any of the following:

- **Start bisection without verifying both endpoints.** If the "good" version
  also fails or the "bad" version also passes, the bisection result will be
  meaningless. Always run the test on both bounds before `git bisect start`.

- **Use a test file that imports project libraries directly.** Every bisection
  step would require rebuilding the library against that Rocq version — use
  `rocq-mwe` to inline dependencies first.

- **Forget `git bisect reset`.** Leaving the repository in bisect mode
  (detached HEAD) corrupts subsequent git operations and wastes build time.

- **Skip commits indiscriminately.** Skipping too many commits produces an
  interval rather than an exact commit as the result. Only skip commits that
  genuinely fail to build (`exit 125`).

- **Leave temporary opam switches after bisection.** Each switch is ~1-2 GB.
  Remove them with `opam switch remove rocq-$VER -y`.

- **Use `opam upgrade` during bisection.** Running upgrades in a bisection
  switch can change the Rocq version mid-session, invalidating all accumulated
  results.

- **Use wall-clock timing as a regression signal.** Performance regressions
  require statistical testing (multiple runs, controlled environment) — they
  cannot be reliably bisected with a single `coqc` invocation per commit.

- **Report a bisection result without attaching the test file.** The commit
  hash alone is not actionable — the exact reproduction case is essential for
  developers to understand the regression scope.

## Verification Checklist

**MUST** confirm all of the following before reporting a bisect result:

- [ ] Test file is self-contained — `coqc -q test.v` works with no project files present
- [ ] Confirmed PASS on the last-known-good version
- [ ] Confirmed FAIL on the first-known-bad version
- [ ] Bisect result commit confirmed: `coqc -q test.v` passes on `commit~1` and fails on `commit`
- [ ] `git bisect reset` has been run (no detached HEAD)
- [ ] All temporary opam switches removed
- [ ] Bug report includes: good version, bad version, bisect commit, and attached test file
- [ ] For MathComp regressions: MathComp version and Rocq version both recorded
