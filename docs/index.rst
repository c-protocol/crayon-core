Intoduction
###########

Crayon Protocol is a lending for financing and leveraging protocol for EVM-compatible blockchains.

Main advantages to lenders
==========================

Traditional DeFi lending protocols have tended to favor new participants in the lending pool at the expense of existing ones. When a new deposit is made, both the interest rate paid by the borrower and the share of the current participants in the pool decrease. With Crayon Protocol, borrowers pay a fee up-front that is fully credited to current participants. Future lenders will be paid from fees on loans taken after they made their deposit.

Crayon Protocol makes it possible for lenders to reserve funds for future withdrawal if current liquidity does not allow it.


Main advantages to leveraged trading
====================================

Traditional DeFi lending protocols expose borrowers to variable and unpredictable interest rates on their loans. PnL from certain leveraged trades can be highly dependent on the interest rate. In addition, the main DeFi lending protocols require multiple transactions, sometimes across multiple platforms, for a leveraged position to be created. With Crayon Protocol, a leveraged trade can be created for a fixed fee in a single transaction that borrows funds, buys the desired (approved) tokens, and deposits them in the pool as collateral. It's similar to a flashloan except that at the end of the transaction, instead of returning the borrowed funds, other tokens (from an approved list) can be deposited.

Tokens deposited by borrowers are available for traditional flashloans allowing borrowers to earn additional fees.

Main advantages to asset financing
==================================

Unlike leveraged trading, asset financing assumes the assets are already held by the borrower who wishes to obtain a loan. Crayon Protocol allows a more "repo-style" asset financing than traditional DeFi. Existing assets can be posted as collateral for a loan in some base token but, unlike traditional DeFi protocols, Crayon Protocol fixes the fee and the expiration date of the loan. This, again, allows for better cost predictions or PnL projections, depending on how the loan is used.

Interaction with the protocol
=============================

The Crayon Protocol team does not intend to build a front-end. Users can access the protocol through front-ends built by third-parties or through the more basic read/write contract features on etherscan.io (use links to contracts in the table below). 

Features
========

* **Term loans**: Loans from the protocol can be taken for a fixed number of terms, e.g., 1, 3 or 7 days.
* **Locked-in fees**: Borrowers pay the fee for the loan up-front, allowing existing lenders to lock the full gain from their participation.
* **Leveraging**: Traders can create leveraged positions in one transaction that borrows, buys approved tokens and deposits them in the protocol.
* **Predictable PnL for leveraged trades**: Traders can figure out exactly the cost of their leveraged trades.
* **Rewards**: XCRAY, a limited supply token, is awarded to lenders and borrowers.

Contracts
=========

.. list-table:: **Sepolia Contracts**
    :width: 75%
    :widths: 150 225
    :header-rows: 1

    *   -
        -
    *   - Contract
        - Address
    *   -
        -
    *   - ETH_Desk
        - `0x80d73254eF0a863E76eA0035613558f5e035b771 <https://sepolia.etherscan.io/address/0x80d73254eF0a863E76eA0035613558f5e035b771#writeContract>`_
    *   - BTC_Desk
        - `0x049041B5EFfe8b85d6476Ce696DF003ce4d54cD9 <https://sepolia.etherscan.io/address/0x049041B5EFfe8b85d6476Ce696DF003ce4d54cD9#writeContract>`_
    *   - DAI_Desk
        - `0x9c27f6BC1fFb37ce0d9fBfc35DCC6b8aF1C08962 <https://sepolia.etherscan.io/address/0x9c27f6BC1fFb37ce0d9fBfc35DCC6b8aF1C08962#writeContract>`_ 
    *   - Control
        - `0x64292f63a4bFe61CC3C4C101b31494E5028B67b7 <https://sepolia.etherscan.io/address/0x64292f63a4bFe61CC3C4C101b31494E5028B67b7>`_ 
    *   - XCRAY
        - `0x66e5392209eCb5Fab51C7B3DB53383E353a07995 <https://sepolia.etherscan.io/address/0x66e5392209eCb5Fab51C7B3DB53383E353a07995>`_ 
    *   - BTC_ETH
        - `0xB1Dc9B6e55e1B4486a786770848f22A4d83F0A70 <https://sepolia.etherscan.io/address/0xB1Dc9B6e55e1B4486a786770848f22A4d83F0A70>`_
    *   - DAI_ETH
        - `0x96b54779b913f1DEf5c24adCB97D1B074f288A8e <https://sepolia.etherscan.io/address/0x96b54779b913f1DEf5c24adCB97D1B074f288A8e>`_
    *   - USDC_ETH
        - `0xb57fEb2a72cEA4E5E8ba902C2674F195B2ec812C <https://sepolia.etherscan.io/address/0xb57fEb2a72cEA4E5E8ba902C2674F195B2ec812C>`_ 
    *   - ETH_BTC
        - `0xf0acE87bd164F659AD32CFDfAC368260bdDf37db <https://sepolia.etherscan.io/address/0xf0acE87bd164F659AD32CFDfAC368260bdDf37db>`_ 
    *   - DAI_BTC
        - `0x636D6cf0204b4BaA0f5f6fb98423F3494c68921D <https://sepolia.etherscan.io/address/0x636D6cf0204b4BaA0f5f6fb98423F3494c68921D>`_ 
    *   - USDC_BTC
        - `0x2d83190Df8d68e53E7D4A6fCcEa0267779Dae337 <https://sepolia.etherscan.io/address/0x2d83190Df8d68e53E7D4A6fCcEa0267779Dae337>`_ 
    *   - ETH_DAI
        - `0x6ba7A78De4aa049557e7be4340834685D836592a <https://sepolia.etherscan.io/address/0x6ba7A78De4aa049557e7be4340834685D836592a>`_ 
    *   - BTC_DAI
        - `0x6FD5d5B8F5eD6280A3E4878EE2Fc4896207043A4 <https://sepolia.etherscan.io/address/0x6FD5d5B8F5eD6280A3E4878EE2Fc4896207043A4>`_ 
    *   - USDC_DAI
        - `0x6C7653C3E066E482Fef42671710De3baE2f09f49 <https://sepolia.etherscan.io/address/0x6C7653C3E066E482Fef42671710De3baE2f09f49>`_ 
    


