# Crayon Protocol Examples

Power users can borrow from a Crayon Desk, add borrowed coins to their initial principal and swap them on a DEX for another coin that they post back as collateral on the Crayon desk. This creates a leveraged, (almost) dollar-matched pairs trade. Slippage on the DEX prevents this from being an exact dollar match.

This folder contains test code for integrations with various DEXes. Just as in the case of flashloans on other protocols, power users have to deploy a smart contract when executing the trade as described above. The actual smart contracts used by the integration tests here are in [`contracts/test-contracts`](../contracts/test-contracts/).

Crayon Protocol is currently only deployed on Arbitrum Main.

### Testing

The tests must be run against a fork of Arbitrum and require an Arbiscan API key (see [`Getting an API key`](https://docs.arbiscan.io/getting-started/viewing-api-usage-statistics)). From the root directory do:

```bash
brownie test examples --network arbitrum-fork
```
### Set-up

Your Brownie `network-config.yaml` file (typically found in `~/.brownie` on linux systems) must have an entry for an Arbitrum fork, for example:

```yaml
- name: Ganache-CLI (Arbitrum Fork)
    id: arbitrum-fork
    cmd: ganache-cli
    host: http://127.0.0.1
    timeout: 120 
    cmd_settings:
      port: 8545
      gas_limit: 12000000
      accounts: 10
      evm_version: istanbul
      mnemonic: brownie
      fork: arbitrum-main
```