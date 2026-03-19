# OpenMath Skills Arena

AI agent skills for the [OpenMath](https://openmath-dev.shentu.org) formal verification platform. This repository provides a complete workflow for discovering open theorems, proving them locally in Lean or Rocq, and submitting verified proofs to earn rewards on the Shentu network.

## Skills

| Skill | Description |
|-------|-------------|
| **openmath-open-theorem** | Query and download open theorems from the OpenMath platform. Scaffold a local Lean/Rocq proof workspace. |
| **openmath-lean-theorem** | Configure Lean environment, install external proof skills, run preflight checks, and manage LEAN4 benchmarks. |
| **openmath-submit-theorem** | Hash your completed proof and submit it to the Shentu blockchain (commit-reveal scheme). |
| **openmath-claim-reward** | Query claimable rewards and generate the withdrawal command after proof verification. |

## Prerequisites

- An AI agent that supports skills ([Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview), [Cursor](https://www.cursor.com/), [Codex](https://openai.com/index/codex/), [Gemini CLI](https://github.com/google-gemini/gemini-cli), etc.)
- For Lean theorem proving: [Lean 4](https://lean-lang.org/) and [elan](https://github.com/leanprover/elan)

## Install

### Via npx (recommended)

```bash
cd your-project

# Install all OpenMath skills (default agent: claude)
npx openmath-skills install openmath-*

# For other agents
npx openmath-skills install openmath-* --agent cursor
npx openmath-skills install openmath-* --agent codex
```

### From source

```bash
git clone https://github.com/openmath/openmath-skills-arena.git
cd your-project

# Copy all OpenMath skills (default agent: claude)
mkdir -p .claude/skills
cp -r /path/to/openmath-skills-arena/skills/openmath-* .claude/skills/

# For Cursor
mkdir -p .cursor/skills
cp -r /path/to/openmath-skills-arena/skills/openmath-* .cursor/skills/
```

### Install Lean proving skills (optional)

Lean proving skills are maintained upstream and not bundled here. Install them separately when needed:

| Source | Skills | Install |
|--------|--------|---------|
| [leanprover/skills](https://github.com/leanprover/skills) | `lean-proof`, `lean-bisect`, `lean-mwe`, `lean-pr`, `lean-setup`, `mathlib-build`, `mathlib-pr`, `mathlib-review`, `nightly-testing` | `npx leanprover-skills install <name>` |

## Workflow

```
1. Discover    →  openmath-open-theorem   →  Browse open theorems, download one
2. Prove       →  openmath-lean-theorem   →  Set up Lean env, preflight, prove
3. Submit      →  openmath-submit-theorem →  Hash & reveal proof on-chain
4. Claim       →  openmath-claim-reward   →  Withdraw earned rewards
```

## Benchmarks

This repository includes a LEAN4 benchmark subsystem under `skills/openmath-lean-theorem/benchmarks/` for evaluating AI theorem proving capabilities. See `skills/openmath-lean-theorem/benchmarks/utils/README.md` for details.

```bash
# Setup
pip3 install -r skills/openmath-lean-theorem/benchmarks/utils/requirements.txt

# Generate proofs with an AI agent
python3 skills/openmath-lean-theorem/benchmarks/utils/solve.py --agent claude-code --benchmark-id easy_algebra_001

# Verify generated proofs
python3 skills/openmath-lean-theorem/benchmarks/utils/check.py
```

## Documentation

- **AGENTS.md** - Full guide for AI agents working with this repository
- **skills/openmath-lean-theorem/benchmarks/utils/README.md** - Benchmark scripts, solve/check workflow, and agent mode

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details.
