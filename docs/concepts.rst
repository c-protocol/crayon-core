.. index:: _concepts

.. _concepts:

Concepts
########

We list here the concepts that underly the Crayon Protocol.

Desks
=====

At the center of the Crayon Protocol are the desks. A desk is specified by:

    * The base coin: This is the ERC20 token that lenders can deposit and traders/borrowers can borrow from the desk.
    * A number of approved ERC20 tokens that can be posted as collateral to secure loans or leveraged positions.
    * The control contract: This is the ``Control`` smart contract that manages awards of the reward token.
    * The ratio of values to loans: This is the minimum ratio of collateral to loan values, both expressed in a common numeraire, below which a loan is subject to liquidation.
    * The fee that is charged to flash loans of the base or collateral (longable) tokens. One fee rate is used for all flash loans.
    * The liquidation bonus: This is the additional value in collateral that liquidators obtain for paying a liquidatable part of a loan.
    * The horizons: Loans on the Crayon Protocol are not open-ended. Users choose one of these horizons when borrowing.
    * The borrowing fees that apply to each horizon.

Control
=======

It is planned for the ``Control`` smart contract to become the hub of governance exercise. Desks register with the ``Control`` smart contract through which some key desk settings (e.g., fees) can be set. Users invoke calls on the ``Control`` contract to mint their reward tokens.

XCRAY
=====

The Crayon Protocol token serves currently to incentivize usage of the platform. It is planned for ``XCRAY`` to become the governance token of the protocol, at which point, holders of ``XCRAY`` will vote to set the fees and ``XCRAY`` distribution rates on the different desks. See :ref:`Governance <governance>`.

Glossary
########

* **base token**: Also referred to as base coin of the Desk is the token that can be lent out by the desk and is the numeraire for all calculated values.
* **horizon**: The horizon of a loan is the number of blocks until the loan expires and must be repaid, extended or liquidated.
* **longable**: Tokens that are accepted in a Desk in exchange for loans are called longable tokens in reference to traders/borrowers being long those tokens and short the base token.
* **provider**: The Crayon Protocol team will not build a front end. Rather, third parties are incentivized to build interfaces by allowing them to keep a percentage of the reward tokens earned by their users. Some interactions with the Crayon Protocol, such as trade leveraging, require smart contract deployments. Providers are also incentivized to facilitate that. 

