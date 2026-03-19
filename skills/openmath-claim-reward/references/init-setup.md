# Init Setup

## Overview

Triggered when:

1. The user wants to query rewards but did not provide an address
2. `openmath-env.json` is missing from `./.openmath-skills/` and `~/.openmath-skills/`, or it exists but is missing `prover_address`
3. The user wants to withdraw rewards but no local `os` keyring key is known for `prover_address`

For read-only reward queries, an explicit address is enough. A config file is only needed when the address is omitted and the skill must auto-discover `prover_address`.

For withdrawals, the local signing key must control the same address as `prover_address`. Do not create a new random key for withdrawal unless it is the same wallet that owns the rewards.

## Setup Flow

```text
Address provided explicitly         No address provided
           |                               |
           v                               v
 +----------------------+       +----------------------+
 | Query rewards        |       | Check openmath-env   |
 +----------------------+       +----------------------+
                                         |
                                         v
                             +--------------------------+
                             | Missing prover_address   |
                             | Ask user for Profile addr|
                             +--------------------------+
                                         |
                                         v
                             +--------------------------+
                             | Save/update config       |
                             +--------------------------+
                                         |
                                         v
                                  Continue query
```

## Flow 1: Query Rewards

If the user already provided an address, use it directly.

If no address was provided, try auto-discovery from:

- `./.openmath-skills/openmath-env.json`
- `~/.openmath-skills/openmath-env.json`

Read `prover_address` from the first existing config.

## Missing `prover_address`

Ask for the user's OpenMath Wallet Address.

How to find it:

1. Open [https://openmath-canary.shentu.org](https://openmath-canary.shentu.org)
2. Connect the wallet and enter `Profile`
3. Find `Wallet Address`
4. Copy it

Recommended save locations:

| Choice | Path | Scope |
|--------|------|-------|
| Project | `./.openmath-skills/openmath-env.json` | Current repository / workspace only |
| User | `~/.openmath-skills/openmath-env.json` | Reused across repositories |

If `openmath-env.json` already exists, update it in place and add:

```json
{
  "prover_address": "shentu1..."
}
```

If the file does not exist yet, create it and save at least `prover_address`. Other OpenMath skills may later extend the same file with `preferred_language`, `agent_key_name`, and `agent_address`.

## Flow 2: Withdraw Rewards

Withdrawal requires a local `os` keyring key that controls `prover_address`.

First inspect the local keyring:

```bash
shentud keys list --keyring-backend os
```

If the user already knows the matching key name, confirm it resolves to `prover_address`:

```bash
shentud keys show <key-name> -a --keyring-backend os
```

If no existing local key matches `prover_address`, stop and ask the user to recover or import the wallet key for that address:

```bash
shentud keys add <key-name> --recover --keyring-backend os
```

Do not generate a new random key for withdrawal unless the user explicitly intends to use a different wallet address.

## After Setup

Expected behavior after setup:

1. A reward address is known, either from the command line or from `prover_address`
2. If withdrawal is requested, a local `os` keyring key matches that address
3. `query_reward_status.py rewards` can run without extra address input when config is present
