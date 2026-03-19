# OpenMath Workspace Preflight

Run this immediately after `download_theorem.py` and before writing any proof.

## Command

```bash
python3 scripts/check_theorem_env.py <workspace>
```

Optional:

```bash
python3 scripts/check_theorem_env.py <workspace> --auto-install-skills
python3 scripts/check_theorem_env.py <workspace> --skip-build
```

## Lean Flow

The Lean preflight does all of the following:

1. Detects the workspace from `lean-toolchain` / `lakefile.lean`
2. Checks `lean`, `lake`, and `elan`
3. Reads the expected Lean version from `lean-toolchain`
4. Checks that required proof skills are installed:
   - `lean-proof`
   - `mathlib-build`
5. Reports optional debugging/review skills if missing:
   - `lean-mwe`
   - `lean-bisect`
   - `nightly-testing`
   - `mathlib-review`
   - `mathlib-pr`
   - `lean-pr`
   - `lean-setup`
6. If mathlib is required, runs:
   ```bash
   lake exe cache get
   ```
7. Runs:
   ```bash
   lake build -q --log-level=info
   ```

If required Lean skills are missing, the checker prints the standard install steps:

```bash
git clone --depth 1 https://github.com/leanprover/skills.git /tmp/leanprover-skills
cp -R /tmp/leanprover-skills/skills/<missing-skill> ~/.agents/skills/
```

If you pass `--auto-install-skills`, it will try to run the clone-and-copy flow automatically.

## Rocq Flow

The Rocq preflight does all of the following:

1. Detects the workspace from `_CoqProject` or root `.v` files
2. Checks `coqc`
3. Checks `rocq` if available, but treats it as optional compatibility information
4. Reads `_CoqProject` flags
5. Compiles the generated `.v` file(s) with `coqc`

Current limitation:

- This repository does not define a pinned Rocq-specific skill bundle
- The preflight therefore treats compiler/toolchain validation as mandatory
- Rocq skill installation is optional and only happens if you configure:
  - `OPENMATH_ROCQ_REQUIRED_SKILLS`
  - `OPENMATH_ROCQ_SKILL_INSTALL_CMD`

That gives Rocq a defined preflight path even when no dedicated Rocq skill stack exists yet.

## Skill Search Paths

By default, the checker searches common skill directories such as:

- `~/.agent/skills`
- `~/.agents/skills`
- `~/.codex/skills`
- `~/.claude/skills`
- project-local `.{agent}/skills`

Override this with:

```bash
OPENMATH_SKILL_DIRS=/path/one:/path/two python3 scripts/check_theorem_env.py <workspace>
```

Or add directories explicitly:

```bash
python3 scripts/check_theorem_env.py <workspace> --skills-dir /path/to/skills
```
