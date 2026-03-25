---
name: openmath-claim-reward
description: Claims earned rewards from the OpenMath platform. Use when the user wants to query claimable imported/proof rewards or withdraw verified Shentu rewards after a proof has passed verification.
version: v1.0.3
---

# OpenMath Claim Reward

## Instructions

Query and withdraw rewards for verified OpenMath activity on Shentu. Flow: query `bounty rewards` → withdraw via `bounty withdraw-rewards` → wait 5–10 s → re-query. Uses `SHENTU_CHAIN_ID` and `SHENTU_NODE_URL` for runtime chain/RPC settings, with built-in mainnet defaults if unset. Shared config resolution order: `--config <path>` → `OPENMATH_ENV_CONFIG` → `./.openmath-skills/openmath-env.json` → `~/.openmath-skills/openmath-env.json`. If `OPENMATH_ENV_CONFIG` is set, treat it as the selected config path. If that file is missing or invalid, stop and fix it instead of silently falling back.

### First-run gate

If the user already provided an address explicitly, reward query can run immediately.

If no address was provided, auto-discover `prover_address` from `OPENMATH_ENV_CONFIG` when it is set; otherwise check only `./.openmath-skills/openmath-env.json` or `~/.openmath-skills/openmath-env.json`. If no usable config exists, or if the config exists but `prover_address` is missing, **do not guess the address**. Follow [references/init-setup.md](references/init-setup.md).

For withdrawals, do not proceed until a local `os` keyring key is known for the same address.

### Workflow checklist

- [ ] **Env**: If needed, export `SHENTU_CHAIN_ID` / `SHENTU_NODE_URL`, or set `OPENMATH_ENV_CONFIG` to a specific `openmath-env.json`; otherwise use the built-in mainnet defaults and standard config auto-discovery.
- [ ] **Address**: Use an explicit address, or let `query_reward_status.py rewards` auto-discover `prover_address` from `OPENMATH_ENV_CONFIG` or the standard `openmath-env.json` locations.
- [ ] **Query**: Run `query_reward_status.py rewards [address]` (or `shentud q bounty rewards <address> --node <shentu_node_url>`) to see `imported_rewards` and/or `proof_rewards`.
- [ ] **Withdraw**: If any bucket is non-empty, first make sure a local `os` keyring key controls the same address, confirm `shentud keys show <your-key> -a --keyring-backend os` matches the reward address, then run `shentud tx bounty withdraw-rewards --from <your-key> --keyring-backend os --chain-id <shentu_chain_id> --node <shentu_node_url> --gas-prices 0.025uctk --gas-adjustment 2.0 --gas auto` (use `SHENTU_CHAIN_ID` / `SHENTU_NODE_URL` or the built-in defaults).
- [ ] **Wait**: 5–10 s for block inclusion.
- [ ] **Re-query**: Run `query_reward_status.py tx <txhash> --wait-seconds 6`, then `query_reward_status.py rewards <address> --wait-seconds 6` to confirm withdrawal; empty buckets are reported as zero, not error.

### Scripts

| Script | Command | Use when |
|--------|---------|----------|
| Query rewards | `python3 scripts/query_reward_status.py rewards [address] [--config <path>] [--wait-seconds 0]` | Checking claimable imported_rewards and proof_rewards for an address, or auto-discovering `prover_address` from `--config`, `OPENMATH_ENV_CONFIG`, or the default config locations when omitted. |
| Query tx | `python3 scripts/query_reward_status.py tx <txhash> [--wait-seconds 6]` | After withdraw broadcast to confirm inclusion. |

Withdraw is done with raw `shentud tx bounty withdraw-rewards --keyring-backend os` (see workflow above).

### Notes

- **Buckets**: `imported_rewards` (theorem imported/referenced), `proof_rewards` (proofs verified). One withdraw pulls both if present.
- **Mainnet**: Default `--chain-id shentu-2.2 --node https://rpc.shentu.org:443`.
- **Config override**: Set `OPENMATH_ENV_CONFIG=/path/to/openmath-env.json` or use `--config` if you want a non-default config path.
- **Keyring**: Always use `--keyring-backend os` for reward withdrawal commands generated from this skill.
- **Trust boundary**: Reward queries shell out to local `shentud`; withdrawals also sign through the local OS keyring. Verify the key name, resolved address, and RPC/node URL before broadcasting.

## References

Load when needed (one level from this file):

- **[references/init-setup.md](references/init-setup.md)** — Reward address discovery and withdraw-key setup.
- **[references/reward_claim_flow.md](references/reward_claim_flow.md)** — Address-based buckets, withdraw behavior, and on-chain claim flow.

Identity setup for theorem submission still lives in **openmath-submit-theorem**, but reward querying itself does not require `openmath-env.json`.
