# AGENTS.md - OpenMath Skills Arena

> AI agent guide for the OpenMath Skills Arena project.

## What This Project Does

Provides AI agent skills for the [OpenMath](https://openmath-dev.shentu.org) formal verification platform — discover open theorems, prove them in Lean or Rocq, submit proofs on-chain, and claim rewards.

## Skills

| Skill | Trigger |
|-------|---------|
| `openmath-open-theorem` | User asks for open theorems, wants to download a theorem, or scaffold a proof workspace |
| `openmath-lean-theorem` | User wants to configure Lean environment, install proof skills, run preflight, prove a theorem, or run benchmarks |
| `openmath-submit-theorem` | User wants to submit/hash a proof for an OpenMath theorem ID |
| `openmath-claim-reward` | User wants to check or withdraw earned rewards |

Skills live in `skills/<name>/SKILL.md`. Install with:

```bash
npx openmath-skills install openmath-*                # default agent: claude
npx openmath-skills install openmath-* --agent cursor # for other agents

# Or from source
mkdir -p .claude/skills && cp -r skills/openmath-* .claude/skills/
```

## Workflow

```
1. Discover    →  openmath-open-theorem   →  Browse open theorems, download one
2. Prove       →  openmath-lean-theorem   →  Set up Lean env, preflight, prove
3. Submit      →  openmath-submit-theorem →  Hash & reveal proof on-chain
4. Claim       →  openmath-claim-reward   →  Withdraw earned rewards
```

## External Dependencies

Lean proving skills are not bundled. Install from [leanprover/skills](https://github.com/leanprover/skills):

```bash
npx leanprover-skills install lean-proof
npx leanprover-skills install mathlib-build
```

## Benchmarks

The `skills/openmath-lean-theorem/benchmarks/` directory contains a LEAN4 benchmark subsystem for evaluating AI theorem proving. See [skills/openmath-lean-theorem/benchmarks/AGENTS.md](skills/openmath-lean-theorem/benchmarks/AGENTS.md) for the full agent guide, or [skills/openmath-lean-theorem/benchmarks/utils/README.md](skills/openmath-lean-theorem/benchmarks/utils/README.md) for script usage.

```bash
pip3 install -r skills/openmath-lean-theorem/benchmarks/utils/requirements.txt
python3 skills/openmath-lean-theorem/benchmarks/utils/solve.py --agent claude-code --benchmark-id easy_algebra_001
python3 skills/openmath-lean-theorem/benchmarks/utils/check.py
```

## Project Structure

```
openmath-skills-arena/
├── skills/                          # OpenMath workflow skills
│   ├── openmath-open-theorem/       # Query and download theorems
│   ├── openmath-lean-theorem/       # Lean env, proving, benchmarks
│   ├── openmath-submit-theorem/     # Submit proofs on-chain
│   └── openmath-claim-reward/       # Claim rewards
├── bin/                             # CLI for skill installation
├── tools/                           # Non-skill tools
├── package.json                     # npm package for npx support
├── AGENTS.md                        # This file
├── CLAUDE.md                        # Claude Code guidance
└── README.md                        # Project readme
```
