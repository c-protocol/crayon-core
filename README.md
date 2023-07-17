# crayon-protocol

Vyper contracts implementing the Crayon Protocol.

## Overview

Crayon is a lending, trade leveraging and financing protocol on Ethereum and EVM-compatible blockchains.

Users interact mainly with Crayon Desks. A Crayon Desk specifies a base token that lenders deposit and tokens that are accepted as collateral for loans that we refer to as longables. The base token must also be the numeraire. Therefore oracles used by the desk must express prices in units of base token.

Traders looking to finance an accepted longable, deposit the longable in exchange for the base token and pay a fee, in a single transaction.

Power traders can borrow the base token to create a leveraged position in a longable. This requires deploying a smart contract and is similar to a flash loan except that at the end of the transaction, a longable is deposited instead of returning the borrowed funds.

Users are rewarded with the protocol token, XCRAY. It is intended for XCRAY to morph into a governance token in future.

## Development and Testing

### Dependencies

* python3 from version 3.10.6
* brownie version 1.19.3
* ganache-cli version 6.12.2

### Testing

Install dependencies and clone repository. Then, the root directory do:

```bash
brownie test
```

This will run all tests, unit and stateful. Stateful testing is very important for Crayon Protocol and is close to a simulation of actual production use. To only do stateful testing:

```bash
brownie test --stateful true
```

### Organization

The Vyper language does not allow contract inheritance (a good thing!). Deployed desks are built from a Desk template [`contracts/desk-templates`](contracts/desk-templates/) together with data specific to each desk. The data is a json file in a folder with a name beginning with `desk_` in [`deployments/`](deployments/).

[`contracts/Control.vy`](contracts/Control.vy/) is the governance contract for Crayon Protocol. It currently has sole privileges to set key variables on the different desks and minting reward tokens for users. It will eventually be controlled by the Crayon Protocol DAO.