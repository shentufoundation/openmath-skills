# OpenMath Authz Setup

Use this when `openmath-submit-theorem` is configured for the default authz-based flow.

Before writing `openmath-env.json`, creating or recovering a local key, or installing `shentud`, get explicit user approval.

## Required Local Config

Create a local config file from the example. See `references/init-setup.md` for the full flow. Auto-discovery only checks `./.openmath-skills/openmath-env.json` and `~/.openmath-skills/openmath-env.json`.

```bash
mkdir -p .openmath-skills
cp references/openmath-env.example.json .openmath-skills/openmath-env.json
```

Or for a reusable shared config:

```bash
mkdir -p ~/.openmath-skills
cp references/openmath-env.example.json ~/.openmath-skills/openmath-env.json
```

Fill in:

- `preferred_language` (optional shared preference used by `openmath-open-theorem`)
- `prover_address`: the user's OpenMath Wallet Address copied from OpenMath Profile
- `agent_key_name`: the local key name that will sign `shentud tx authz exec` (default: `agent-prover`)
- `agent_address`: the bech32 address for that agent key

The fee granter defaults to `prover_address`; do not add a separate config field for it.

Recommended local key flow:

```bash
shentud keys show agent-prover -a --keyring-backend os
```

If the key does not exist, stop and ask the user whether to create a new local key or recover an existing one. Do not run `shentud keys add` without explicit approval.

Create a new key only if the user approves:

```bash
shentud keys add agent-prover --keyring-backend os
```

Recover an existing key only if the user approves:

```bash
shentud keys add agent-prover --recover --keyring-backend os
```

Then save:

- `agent_key_name`: `agent-prover`
- `agent_address`: the detected or resulting bech32 address

Runtime chain settings are not stored in `openmath-env.json`:

- `SHENTU_CHAIN_ID` or default `shentu-2.2`
- `SHENTU_NODE_URL` or default `https://rpc.shentu.org:443`

## Website Flow

If the user has not configured authz yet, use this sequence:

1. Make sure `prover_address` and `agent_address` are already known and saved in `openmath-env.json`.
2. Open [https://openmath.shentu.org/OpenMath/Profile](https://openmath.shentu.org/OpenMath/Profile).
3. Scroll to the bottom of the page and find `AI Agent Authorization`.
4. Enter `agent_address`.
5. Click `Authorize`.
6. Confirm the wallet transaction(s).
7. Re-run `python3 scripts/check_authz_setup.py --config .openmath-skills/openmath-env.json` to confirm chain state.
8. Do not run `generate_submission.py` in authz mode until the checker returns `Status: ready`.

## Manual CLI Fallback

If the website flow is unavailable, the OpenMath wallet owner can authorize the agent manually. Use `SHENTU_CHAIN_ID` and `SHENTU_NODE_URL`, or fall back to the built-in defaults `shentu-2.2` and `https://rpc.shentu.org:443`.

### Authz Grants

```bash
shentud tx authz grant <agent-address> generic \
  --msg-type=/shentu.bounty.v1.MsgSubmitProofHash \
  --expiration 2026-03-18T00:00:00Z \
  --from <prover-key> \
  --chain-id <shentu_chain_id> \
  --node <shentu_node_url>

shentud tx authz grant <agent-address> generic \
  --msg-type=/shentu.bounty.v1.MsgSubmitProofDetail \
  --expiration 2026-03-18T00:00:00Z \
  --from <prover-key> \
  --chain-id <shentu_chain_id> \
  --node <shentu_node_url>
```

### Feegrant

The feegrant must allow the outer authz wrapper:

```bash
shentud tx feegrant grant <prover-address> <agent-address> \
  --allowed-messages "/cosmos.authz.v1beta1.MsgExec" \
  --spend-limit 1000000uctk \
  --expiration 2026-03-18T00:00:00Z \
  --gas-prices 0.025uctk \
  --gas-adjustment 2.0 \
  --gas auto \
  --chain-id <shentu_chain_id> \
  --node <shentu_node_url> \
  --keyring-backend os
```

Add more message types only if the agent also needs direct access outside `authz exec`.

## Validation

Run the bundled checker before generating submission commands:

```bash
python3 scripts/check_authz_setup.py --config .openmath-skills/openmath-env.json
```

The checker verifies:

- `shentud` is available
- the local agent key exists and matches the configured address
- authz grants exist for the required OpenMath message types
- a feegrant exists and allows `/cosmos.authz.v1beta1.MsgExec`

Warnings about missing `spend_limit` or `expiration` do not block submission, but they indicate a broad feegrant.

`generate_submission.py` in authz mode should be treated as blocked until this checker reports `Status: ready`.
