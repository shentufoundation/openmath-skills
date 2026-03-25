# Shentu Proof Submission Guidelines

## 0. Config
Before any proof submission, confirm the local Shentu CLI environment is ready.

Required components:
*   `shentud` is installed and available in `PATH`
*   The target key already exists in the local keyring
*   The RPC endpoint is reachable from the current machine

Recommended checks:

```bash
command -v shentud
shentud version
shentud keys list --keyring-backend os
```

If `shentud` is missing or the keyring is not configured, stop here and install/configure the Shentu environment first. Do not start Stage 1 until these checks pass.
If `command -v shentud` fails, the default path is broken, or `shentud version` cannot run, use the bundled installer:

```bash
python3 scripts/ensure_shentud.py --check-only
```

Only after explicit user approval should you run:

```bash
python3 scripts/ensure_shentud.py --install [--persist-path]
```

### Install `shentud` if Missing
1. Download the latest release from:
   `https://github.com/shentufoundation/shentu/releases`
2. Releases usually include separate binaries for Linux and Apple Silicon macOS. For example, in release `v2.17.0`:
   *   `shentud_2.17.0_arm64_macos`
   *   `shentud_2.17.0_linux_amd64`
3. Choose the binary that matches the current machine architecture and operating system.
4. After downloading, place the binary somewhere in your `PATH` and make sure the executable name is `shentud`, so it can be called directly from any shell.
5. Verify the installation with:

```bash
shentud version
```

The command should print the installed version and confirm that `shentud` is available globally.

### Example Setup
After downloading a release binary, make it executable and rename it to `shentud`:

```bash
chmod +x shentud_2.17.0_arm64_macos
mv shentud_2.17.0_arm64_macos shentud
```

Common ways to place it in `PATH`:

macOS (`zsh`):

```bash
mkdir -p "$HOME/bin"
mv shentud "$HOME/bin/shentud"
echo 'export PATH="$HOME/bin:$PATH"' >> "$HOME/.zshrc"
source "$HOME/.zshrc"
```

Linux (`bash`):

```bash
mkdir -p "$HOME/bin"
mv shentud "$HOME/bin/shentud"
echo 'export PATH="$HOME/bin:$PATH"' >> "$HOME/.bashrc"
source "$HOME/.bashrc"
```

If you prefer a system-wide location, you can also place the binary in a directory that is already in `PATH`, such as `/usr/local/bin`, and keep the executable name as `shentud`.

### Automatic Install Helper
The bundled helper below can handle the common case where `shentud` is missing or the default PATH points to a broken binary:

```bash
python3 scripts/ensure_shentud.py --check-only
```

What it does:
1. Checks whether an existing `shentud` binary already works.
2. If you later rerun it with `--install`, it downloads the latest release from GitHub.
3. Selects the correct binary for the current OS and CPU architecture.
4. Installs it as `~/bin/shentud`.
5. Appends the install directory to the active shell rc file only if `--persist-path` is used.

Useful options:

```bash
python3 scripts/ensure_shentud.py --check-only
python3 scripts/ensure_shentud.py --install
python3 scripts/ensure_shentud.py --install --persist-path
python3 scripts/ensure_shentud.py --force-download
```

### Configure Keys if `shentud keys list` Is Empty
If the local `os` keyring does not contain the key you want to use for submission, stop and ask the user to create or recover it before continuing. Do not switch to other keyring backends.

Create a new local key:

```bash
shentud keys add <key-name> --keyring-backend os
```

Recover an existing key from its mnemonic:

```bash
shentud keys add <key-name> --recover --keyring-backend os
```

Recover from a mnemonic file:

```bash
shentud keys add <key-name> --recover --source ./mnemonic.txt --keyring-backend os
```

Show the submission address for a configured key:

```bash
shentud keys show <key-name> -a --keyring-backend os
```

After creating or recovering a key, make sure the address has enough `uctk` for the proof deposit and gas fees before starting Stage 1.

### Authz Submission Config

The default OpenMath submission flow now uses:

1. an inner raw OpenMath message JSON (`proofhash.json` / `proofdetail.json`)
2. an outer `shentud tx authz exec`
3. a feegrant from the OpenMath Wallet Address owner (`prover_address`)

Create a local config file first. Auto-discovery only checks `./.openmath-skills/openmath-env.json` and `~/.openmath-skills/openmath-env.json`. See `references/init-setup.md` for the full setup flow.

```bash
mkdir -p .openmath-skills
cp references/openmath-env.example.json .openmath-skills/openmath-env.json
```

Or:

```bash
mkdir -p ~/.openmath-skills
cp references/openmath-env.example.json ~/.openmath-skills/openmath-env.json
```

Fill in:

- `preferred_language` (optional shared preference used by `openmath-open-theorem`: `lean` or `rocq`)
- `prover_address` (`OpenMath Wallet Address`)
- `agent_key_name` (default: `agent-prover`)
- `agent_address`
- fee granter is derived automatically from `prover_address`

Runtime chain settings are not stored in `openmath-env.json`:

- `SHENTU_CHAIN_ID` (default: `shentu-2.2`)
- `SHENTU_NODE_URL` (default: `https://rpc.shentu.org:443`)

If the config is missing from both locations, or if it exists but is missing `prover_address`, `agent_address`, or `agent_key_name`, stop and run `references/init-setup.md`, then validate:

```bash
python3 scripts/check_authz_setup.py --config .openmath-skills/openmath-env.json
```

Do not run `generate_submission.py` in authz mode until that command returns `Status: ready`.

## 1. Network Defaults
Chain settings are read from `SHENTU_CHAIN_ID` and `SHENTU_NODE_URL` (default: `shentu-2.2`, `https://rpc.shentu.org:443`).

## 2. Prerequisites
Before submitting, ensure:
*   **Proof Integrity**: Your Lean/Rocq proof is complete and locally verified.
*   **Environment**: The `Config` checks above already pass.

### Pre-Submission Checklist
Before generating or broadcasting any submission command, confirm all 6 items below:

1. **`shentud` is available**
   ```bash
   command -v shentud
   shentud version
   ```
2. **The local agent execution key exists**
   ```bash
   shentud keys show agent-prover -a --keyring-backend os
   ```
   If the key is missing, stop and ask the user whether to create a new key or recover an existing one. Do not run `shentud keys add` without explicit approval.
   Create a new key only if the user approves:
   ```bash
   shentud keys add agent-prover --keyring-backend os
   ```
   Recover an existing key only if the user approves:
   ```bash
   shentud keys add agent-prover --recover --keyring-backend os
   ```
   Then save the resulting address as `agent_address` and tell the user to securely store the mnemonic or recovery material.
3. **The OpenMath Wallet Address owner (`prover_address`) has enough `uctk`**
   ```bash
   shentud q bank balance --denom uctk --address <FEE_GRANTER_ADDRESS> --node <shentu_node_url>
   ```
   Use `SHENTU_NODE_URL` or the built-in default `https://rpc.shentu.org:443`. Make sure the balance covers the proof deposit and gas fees.
4. **The authz + feegrant setup is ready**
   ```bash
   python3 scripts/check_authz_setup.py --config .openmath-skills/openmath-env.json
   ```
   Confirm that the required authz grants exist and the feegrant allows `/cosmos.authz.v1beta1.MsgExec`. `generate_submission.py` in authz mode should be treated as blocked until this returns `Status: ready`.
5. **The proof file is the right local file**
   ```bash
   test -f <proof-path>
   ```
   The file should match the target theorem, use the correct language, and be locally checked before submission.
6. **The theorem ID is correct**
   ```bash
   shentud q bounty theorem <theorem-id> --node <shentu_node_url>
   ```
   Confirm that the theorem exists and that you are submitting against the intended theorem ID.

### Shortest Submission Flow
If the environment, authz config, balance, proof file, and theorem ID are already confirmed, the shortest end-to-end flow is:

1. Verify authz readiness:
   ```bash
   python3 scripts/check_authz_setup.py --config .openmath-skills/openmath-env.json
   ```
2. Generate the Stage 1 commands:
   ```bash
   python3 scripts/generate_submission.py hash <theoremId> <proofPath> <proverKeyOrAddress> <proverAddr>
   ```
3. Run the emitted `proofhash.json` generation command.
4. Broadcast Stage 1 with the emitted `shentud tx authz exec proofhash.json ... --fee-granter <prover-address>` command and record the returned `txhash`.
5. Wait `5-10` seconds, then query the tx:
   ```bash
   python3 scripts/query_submission_status.py tx <txhash> --wait-seconds 6
   ```
6. Confirm the proof exists on-chain and is in `PROOF_STATUS_HASH_LOCK_PERIOD`, then record the returned `proof_id`.
7. Generate the Stage 2 commands:
   ```bash
   python3 scripts/generate_submission.py detail <proofId> <proofPath> <proverKeyOrAddress>
   ```
8. Run the emitted `proofdetail.json` generation command.
9. Broadcast Stage 2 during the hash-lock window with the emitted `shentud tx authz exec proofdetail.json ... --fee-granter <prover-address>` command and record the returned `txhash`.
10. Wait `5-10` seconds, then query the Stage 2 tx:
   ```bash
   python3 scripts/query_submission_status.py tx <txhash> --wait-seconds 6
   ```
11. Wait another `5-10` seconds, then query the theorem status:
   ```bash
   python3 scripts/query_submission_status.py theorem <theoremId> --wait-seconds 6
   ```
12. Treat `THEOREM_STATUS_PASSED` as the successful final state.

## 3. Wallet & Balance Check
### Check Keys
Verify the local agent execution key exists and get its address:
```bash
shentud keys show <agent-key-name> -a --keyring-backend os
```

This address should match `agent_address` in `openmath-env.json`.
If the key is missing, go back to the `Config` section and create or recover it first in the `os` keyring.

### Check Balance
Proof submission requires:

- the OpenMath Wallet Address owner (`prover_address`) to cover the proof deposit
- the feegranter allowance to cover outer `authz exec` gas

Verify the `prover_address` `uctk` balance:
```bash
shentud q bank balance --denom uctk --address <PROVER_ADDRESS> --node <shentu_node_url>
```
*   **Precision**: 1 CTK = 1,000,000 uctk (6 decimal places).
*   Ensure you have enough `uctk` for both the deposit and gas fees.

## 4. Two-Stage Submission Process

### Stage 1: Submit Proof Hash (Commitment)
Prevents front-running and proof leakage while securing your spot.
*   **Message**: `MsgSubmitProofHash`
*   **Parameters**: `theorem_id`, `prover` (address), `proof_hash`, `deposit`.

#### Proof Hash Calculation (Go Logic)
The `proof_hash` is a hex-encoded SHA256 hash of the marshaled `ProofHash` struct:
```go
func (k Keeper) GetProofHash(theoremID uint64, prover, detail string) string {
    proofHash := &types.ProofHash{
        TheoremId: theoremID,
        Prover:    prover,
        Detail:    detail,
    }
    bz := k.cdc.MustMarshal(proofHash)
    hash := sha256.Sum256(bz)
    return hex.EncodeToString(hash[:])
}
```
*   `theoremID`: The ID of the theorem.
*   `prover`: Your OpenMath Wallet Address on Shentu.
*   `detail`: The actual proof content string.

**Default Authz Flow** (same shape emitted by the bundled script):
```bash
shentud tx bounty proof-hash \
  --theorem-id <theorem-id> \
  --hash <proof-hash> \
  --deposit 1000000uctk \
  --from <prover-address> \
  --fees 5000uctk \
  --gas 200000 \
  --chain-id shentu-2.2 \
  --keyring-backend os \
  --generate-only -o json > proofhash.json

shentud tx authz exec proofhash.json \
  --from <agent-key-name> \
  --fee-granter <prover-address> \
  --gas auto \
  --gas-adjustment 2.0 \
  --gas-prices 0.025uctk \
  --keyring-backend os \
  --chain-id shentu-2.2 \
  --node https://rpc.shentu.org:443 \
  -y
```

The inner `proofhash.json` should be the raw `MsgSubmitProofHash` transaction generated with `--generate-only`.
The outer `authz exec` is the real broadcast transaction, so the feegrant must allow `/cosmos.authz.v1beta1.MsgExec`.
Any fee, gas, signer info, or signatures inside `proofhash.json` are not what the chain uses for the outer broadcast.

**After Broadcast**:
1. Wait about **5-10 seconds** for the next block.
2. Query the tx receipt:
   ```bash
   python3 scripts/query_submission_status.py tx <txhash> --wait-seconds 6
   ```
3. Query the proof and confirm it is in `PROOF_STATUS_HASH_LOCK_PERIOD`. Submit Stage 2 during this hash-lock window; do not wait for the proof `end_time` to pass before revealing.

#### Stage 1 Broadcast Checklist
After broadcasting `proof-hash`, confirm all 5 items below:

1. Record the returned `txhash`.
2. Wait about `5-10` seconds for block inclusion.
3. Confirm the tx query returns `code: 0`.
4. Confirm the outer tx action is `/cosmos.authz.v1beta1.MsgExec`.
5. Query the proof, confirm it is in `PROOF_STATUS_HASH_LOCK_PERIOD`, and record the returned `proof_id` for Stage 2. On the current flow, this matches the submitted proof hash hex string.

### Stage 2: Submit Proof Detail (Reveal)
Submit the actual proof content to claim the bounty after the hash is successfully recorded. Reveal during the `PROOF_STATUS_HASH_LOCK_PERIOD`; do not wait for the hash-lock window to end.
*   **Message**: `MsgSubmitProofDetail`
*   **Parameters**: `proof_id` (received after stage 1; this matches the proof hash hex string), `prover`, `detail` (the actual proof text).
*   **Default Authz Flow** (the bundled script shell-quotes the proof body for you):
    ```bash
    shentud tx bounty proof-detail \
      --proof-id <proof-id> \
      --detail '<proof-content-string>' \
      --from <prover-address> \
      --fees 5000uctk \
      --gas 200000 \
      --chain-id shentu-2.2 \
      --keyring-backend os \
      --generate-only -o json > proofdetail.json

    shentud tx authz exec proofdetail.json \
      --from <agent-key-name> \
      --fee-granter <prover-address> \
      --gas auto \
      --gas-adjustment 2.0 \
      --gas-prices 0.025uctk \
      --keyring-backend os \
      --chain-id shentu-2.2 \
      --node https://rpc.shentu.org:443 \
      -y
    ```

The inner `proofdetail.json` should be the raw `MsgSubmitProofDetail` transaction generated with `--generate-only`.
Only the inner `body.messages` content matters to `authz exec`; the outer tx determines the real signer, gas, and feegrant usage.

**After Broadcast**:
1. Wait about **5-10 seconds** for the next block.
2. Query the tx receipt:
   ```bash
   python3 scripts/query_submission_status.py tx <txhash> --wait-seconds 6
   ```
3. Wait another **5-10 seconds** and query the theorem status:
   ```bash
   python3 scripts/query_submission_status.py theorem <theorem-id> --wait-seconds 6
   ```

#### Stage 2 Broadcast Checklist
After broadcasting `proof-detail`, confirm all 6 items below:

1. Record the returned `txhash`.
2. Wait about `5-10` seconds for block inclusion.
3. Confirm the tx query returns `code: 0`.
4. Confirm the outer tx action is `/cosmos.authz.v1beta1.MsgExec`.
5. Wait another `5-10` seconds and query the theorem status.
6. Confirm the theorem status reaches the expected final state, typically `THEOREM_STATUS_PASSED`.

## 5. Theorem Status Meanings

Use the chain query below to check the canonical theorem status:

```bash
shentud q bounty theorem <theorem-id> --node <shentu_node_url>
```

Important statuses:

*   `THEOREM_STATUS_PASSED`: The theorem proof has passed verification.
*   `THEOREM_STATUS_PROOF_PERIOD`: The theorem is still within the active proof period and is being proven.
*   `THEOREM_STATUS_CLOSED`: The theorem is no longer active and has been closed.
