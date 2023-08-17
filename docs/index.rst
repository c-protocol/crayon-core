Intoduction
###########

Crayon Protocol is a lending for financing and leveraging protocol for EVM-compatible blockchains.

Main advantages to lenders
==========================

Traditional DeFi lending protocols have tended to favor new participants in the lending pool at the expense of existing ones. When a new deposit is made, both the interest rate paid by the borrower and the share of the current participants in the pool decrease. With Crayon Protocol, borrowers pay a fee up-front that is fully credited to current participants. Future lenders will be paid from fees on loans taken after they made their deposit.

Crayon Protocol makes it possible for lenders to reserve funds for future withdrawal if current liquidity does not allow it.

Deposits are available for traditional flashloans. A flashloan requires the deployment of a smart contract. A smart contract can flashloan up to the full balance of its base token deposit for no fee.


Main advantages to trade leveraging
====================================

Traditional DeFi lending protocols expose borrowers to variable and unpredictable interest rates on their loans. PnL from certain leveraged trades can be highly dependent on the interest rate. In addition, some DeFi lending protocols require multiple transactions, sometimes across multiple platforms, for a leveraged position to be created. With Crayon Protocol, a leveraged trade can be created for a fixed fee in a single transaction that borrows funds, buys the desired (approved) tokens, and deposits them in the pool as collateral. It's similar to a traditional flashloan except that at the end of the transaction, instead of returning the borrowed funds, other tokens (from an approved list) can be deposited.

Tokens deposited by borrowers are available for traditional flashloans allowing borrowers to earn additional fees. Smart contracts can flashloan up to the full amount of their own collateral for no fee.

Main advantages to asset financing
==================================

Unlike trade leveraging, asset financing assumes the assets are already held by the borrower who wishes to obtain a loan. Crayon Protocol allows a more "repo-style" asset financing than traditional DeFi. Existing assets can be posted as collateral for a loan in some base token but, unlike traditional DeFi protocols, Crayon Protocol fixes the fee and the expiration date of the loan. This, again, allows for better cost predictions or PnL projections, depending on how the loan is used.

Interaction with the protocol
=============================

The Crayon Protocol team does not intend to build a front-end. Users can access the protocol through front-ends built by third-parties or through the more basic read/write contract features on etherscan.io (use links to contracts in the table below). 

Features
========

* **Term loans**: Loans from the protocol can be taken for a fixed number of terms, e.g., 1, 3 or 7 days.
* **Locked-in fees**: Borrowers pay the fee for the loan up-front, allowing existing lenders to lock the full gain from their participation.
* **Leveraging**: Traders can create leveraged positions in one transaction that borrows, buys approved tokens and deposits them in the protocol.
* **Predictable PnL for leveraged trades**: Traders can figure out exactly the cost of their leveraged trades.
* **Rewards**: ``XCRAY``, a limited supply token, is awarded to lenders and borrowers.
* **All fees go to users**: Lenders receive 100% of fees paid by borrowers and base token flashborrowers. Borrowers receive 100% of fees paid by flashborrowers of the token they used as collateral.

Contracts
=========

.. list-table:: **Arbitrum Contracts**
    :width: 75%
    :widths: 150 225
    :header-rows: 1

    *   -
        -
    *   - Contract
        - Address
    *   -
        -
    *   - WETH_Desk
        - `0x8351483e30928D1Fe1f80eD5062c6438faa85b88 <https://arbiscan.io/address/0x8351483e30928D1Fe1f80eD5062c6438faa85b88#writeContract>`_
    *   - WBTC_Desk
        - `0x3454923795c5EdD5b3967e3B63140c343e6BB3dF <https://arbiscan.io/address/0x3454923795c5EdD5b3967e3B63140c343e6BB3dF#writeContract>`_
    *   - USDC_Desk
        - `0x5dE27C6D5524EE07c0dB88CAB65022E3210a81c4 <https://arbiscan.io/address/0x5dE27C6D5524EE07c0dB88CAB65022E3210a81c4#writeContract>`_
    *   - ARB_Desk
        - `0x343d5F534C4C1fB83cdDf0875cC91591cCf69416 <https://arbiscan.io/address/0x343d5F534C4C1fB83cdDf0875cC91591cCf69416#writeContract>`_
    *   - GMX_Desk
        - `0x635b2fE7bF8d41B0477A492f953f57b40E385Cfb <https://arbiscan.io/address/0x635b2fE7bF8d41B0477A492f953f57b40E385Cfb#writeContract>`_
    *   - RDNT_Desk
        - `0xfE2A45BF13965393c863460F063bDD4a9874c415 <https://arbiscan.io/address/0xfE2A45BF13965393c863460F063bDD4a9874c415#writeContract>`_
    *   - Control
        - `0xe2c5fAC44aF73D44E047879C7A20383ecDC2EEfa <https://arbiscan.io/address/0xe2c5fAC44aF73D44E047879C7A20383ecDC2EEfa>`_ 
    *   - XCRAY
        - `0x2dEbe92EdBbA661362fC8BF062551E7c993ACb02 <https://arbiscan.io/address/0x2dEbe92EdBbA661362fC8BF062551E7c993ACb02>`_ 
