# OpenMath Skills Arena

AI agent skills for the [OpenMath](https://openmath.shentu.org) formal verification platform. This repository provides a complete workflow for discovering open theorems, proving them locally in Lean or Rocq, and submitting verified proofs to earn rewards on the Shentu network.

## Skills

| Skill | Description |
|-------|-------------|
| **openmath-open-theorem** | Query and download open theorems from the OpenMath platform. Scaffold a local Lean/Rocq proof workspace. |
| **openmath-lean-theorem** | Configure Lean environment, install external proof skills, run preflight checks, and prove downloaded OpenMath Lean theorems. |
| **openmath-lean-benchmark** | Run and evaluate the bundled Lean benchmark suite for AI theorem proving. Compare agents, prompts, and benchmark results. |
| **openmath-rocq-theorem** | Configure Rocq environment, install Rocq proof skills, run preflight checks, and prove OpenMath Rocq theorems. |
| **openmath-submit-theorem** | Hash your completed proof and submit it to the Shentu blockchain (commit-reveal scheme). |
| **openmath-claim-reward** | Query claimable rewards and generate the withdrawal command after proof verification. |

## Prerequisites

- An AI agent that supports skills ([Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview), [Cursor](https://www.cursor.com/), [Codex](https://openai.com/index/codex/), [Gemini CLI](https://github.com/google-gemini/gemini-cli), etc.)
- For Lean theorem proving: [Lean 4](https://lean-lang.org/) and [elan](https://github.com/leanprover/elan)
- For Rocq theorem proving: [Rocq](https://rocq.pro/) 9.x (via [opam](https://opam.ocaml.org/)), dune

## Install

### Using AI Skills CLI (recommended)

You can add these skills to your local agent environment with a single command:

```bash
# Add all skills from this repository
npx skills add shentufoundation/openmath-skills
```

### From source

```bash
git clone https://github.com/shentufoundation/openmath-skills.git
cd openmath-skills

# Copy skills manually (e.g., for Claude)
mkdir -p .claude/skills
cp -r skills/openmath-* .claude/skills/
```

### Install Lean proving skills (optional)

Lean proving skills are maintained upstream and not bundled here. Install them separately when needed:

| Source | Skills | Install |
|--------|--------|---------|
| [leanprover/skills](https://github.com/leanprover/skills) | `lean-proof`, `lean-bisect`, `lean-mwe`, `lean-pr`, `lean-setup`, `mathlib-build`, `mathlib-pr`, `mathlib-review`, `nightly-testing` | `npx leanprover-skills install <name>` |

### Install Rocq proving skills (optional)

Rocq proof skills are bundled in this repository. Using `npx skills add shentufoundation/openmath-skills` installs them automatically. When installing from source with `cp -r skills/openmath-* .claude/skills/`, also copy the Rocq skills:

```bash
for d in skills/rocq-*; do cp -R "$d" .claude/skills/; done
```

## Setup Flow

```text
  +------------------------+
  | openmath-open-theorem   |
  | Discover & download     |
  | open theorems           |
  +------------------------+
            |
            v
  +------------------------+
  | Language selection      |
  | (from downloaded        |
  |  theorem workspace)     |
  +------------------------+
            |
     +------+------+
     |             |
     v             v
  +--------+   +--------+
  | Lean   |   | Rocq   |
  +--------+   +--------+
     |             |
     v             v
  +------------------+  +------------------+
  | openmath-lean-   |  | openmath-rocq-   |
  | theorem          |  | theorem          |
  | Set up env,      |  | Set up env,      |
  | preflight, prove |  | preflight, prove |
  +------------------+  +------------------+
     |                       |
     +-----------+-----------+
                 |
                 v
  +------------------------+
  | openmath-submit-theorem |
  | Hash & reveal proof     |
  | on-chain                |
  +------------------------+
            |
            v
  +------------------------+
  | openmath-claim-reward   |
  | Withdraw verified       |
  | rewards                 |
  +------------------------+
```

## Workflow

```
1. Discover    →  openmath-open-theorem   →  Browse open theorems, download one
2. Prove       →  openmath-lean-theorem   →  Lean: set up env, preflight, prove
               →  openmath-rocq-theorem   →  Rocq: set up env, preflight, prove
3. Benchmark   →  openmath-lean-benchmark →  Optional: evaluate Lean proof agents on bundled benchmarks
4. Submit      →  openmath-submit-theorem →  Hash & reveal proof on-chain
5. Claim       →  openmath-claim-reward   →  Withdraw earned rewards
```

## Benchmarks

This repository includes a standalone LEAN4 benchmark skill under `skills/openmath-lean-benchmark/` for evaluating AI theorem proving capabilities. See `skills/openmath-lean-benchmark/utils/README.md` for details.

Benchmark runtime notes:

- `python3 .../solve.py --prompt ...` uses the Anthropic API and requires `ANTHROPIC_API_KEY`.
- `python3 .../solve.py --agent <name>` requires the selected CLI (`claude`, `gemini`, `aider`, `opencode`, or `codex`) to be installed and already authenticated/configured locally.
- Benchmark runs write local artifacts under `skills/openmath-lean-benchmark/answers/` and `skills/openmath-lean-benchmark/results/*.json`; those generated files are gitignored by default.
- Raw provider/agent diagnostic output is not persisted unless you explicitly opt in with `--save-diagnostics` on `solve.py` and `--include-diagnostics` on `check.py`.

```bash
# Setup
pip3 install -r skills/openmath-lean-benchmark/utils/requirements.txt

# Generate proofs with an AI agent
python3 skills/openmath-lean-benchmark/utils/solve.py --agent claude-code --benchmark-id easy_algebra_001

# Verify generated proofs
python3 skills/openmath-lean-benchmark/utils/check.py
```

## Documentation

- **AGENTS.md** - Full guide for AI agents working with this repository
- **skills/openmath-lean-benchmark/utils/README.md** - Benchmark scripts, solve/check workflow, and agent mode

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details.
