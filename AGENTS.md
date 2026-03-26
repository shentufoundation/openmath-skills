# AGENTS.md - OpenMath Skills Arena

> AI agent guide for the OpenMath Skills Arena project.

## What This Project Does

Provides AI agent skills for the [OpenMath](https://openmath-dev.shentu.org) formal verification platform — discover open theorems, prove them in Lean or Rocq, submit proofs on-chain, and claim rewards.

## Skills

| Skill | Trigger |
|-------|---------|
| `openmath-open-theorem` | User asks for open theorems, wants to download a theorem, or scaffold a proof workspace |
| `openmath-lean-theorem` | User wants to configure Lean environment, install proof skills, run preflight, or prove a theorem |
| `openmath-lean-benchmark` | User wants to run Lean benchmarks, compare proving agents/models, validate benchmark sets, or analyze benchmark results |
| `openmath-rocq-theorem` | User wants to configure Rocq environment, run preflight, or prove a Rocq/Coq theorem |
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
               →  openmath-rocq-theorem   →  Set up Rocq env, preflight, prove
3. Benchmark   →  openmath-lean-benchmark →  Optional: evaluate Lean proof agents on bundled benchmarks
4. Submit      →  openmath-submit-theorem →  Hash & reveal proof on-chain
5. Claim       →  openmath-claim-reward   →  Withdraw earned rewards
```

## External Dependencies

Lean proving skills are not bundled. Install from [leanprover/skills](https://github.com/leanprover/skills):

```bash
npx leanprover-skills install lean-proof
npx leanprover-skills install mathlib-build
```

## Benchmarks

The `skills/openmath-lean-benchmark/` directory contains a standalone LEAN4 benchmark skill for evaluating AI theorem proving. See [skills/openmath-lean-benchmark/AGENTS.md](skills/openmath-lean-benchmark/AGENTS.md) for the full agent guide, or [skills/openmath-lean-benchmark/utils/README.md](skills/openmath-lean-benchmark/utils/README.md) for script usage.

Benchmark runtime notes:

- Direct API mode (`solve.py --prompt ...`) requires `ANTHROPIC_API_KEY`.
- Agent mode (`solve.py --agent ...`) requires the selected CLI to be installed and already authenticated/configured locally.
- Generated artifacts under `skills/openmath-lean-benchmark/answers/` and `skills/openmath-lean-benchmark/results/*.json` are local-only and gitignored by default.
- Raw provider/agent diagnostic output is only written when explicitly requested with `--save-diagnostics` and `--include-diagnostics`.

```bash
pip3 install -r skills/openmath-lean-benchmark/utils/requirements.txt
python3 skills/openmath-lean-benchmark/utils/solve.py --agent claude-code --benchmark-id easy_algebra_001
python3 skills/openmath-lean-benchmark/utils/check.py
```

## Project Structure

```
openmath-skills-arena/
├── skills/                          # OpenMath workflow skills
│   ├── openmath-open-theorem/       # Query and download theorems
│   ├── openmath-lean-theorem/       # Lean env and proving workflow
│   ├── openmath-lean-benchmark/     # Lean benchmark evaluation workflow
│   ├── openmath-rocq-theorem/       # Rocq env and proving workflow
│   ├── openmath-submit-theorem/     # Submit proofs on-chain
│   └── openmath-claim-reward/       # Claim rewards
├── bin/                             # CLI for skill installation
├── package.json                     # npm package for npx support
├── AGENTS.md                        # This file
├── CLAUDE.md                        # Claude Code guidance
└── README.md                        # Project readme
```
