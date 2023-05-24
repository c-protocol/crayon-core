.. index:: _queries

.. _queries:

Desk Queries
############

A number of functions can be called to retrieve information about a desk's attributes and state. All these are ``view`` functions.

.. py:function:: base_coin() -> address

    Returns the address of the smart contract of the base token for this desk.

.. py:function:: base_coin_decimals() -> uint8

    Returns the number of decimal digits for the base coin.

.. py:function:: flashloan_fee() -> uint256

    Returns the fee in bps that all flash loans will be charged.

.. py:function:: liquidation_bonus() -> uint256

    Returns the gain in bps that a liquidator gets from paying a liquidatable part of a loan.

.. py:function:: control_contract() -> address

    Returns the address of the ``Control`` smart contract that controls some of the settings in this desk.

.. py:function:: horizons(_horizon : uint256) -> uint256

    Returns the fee in bps that applies to loans for horizon _horizon. Note this returns 0 if ``_horizon`` is not one of the horizons accepted by this desk.

    * ``_horizon``: The horizon desired expressed in number of blocks

.. py:function:: total_liquidity() -> uint256

    Returns the number of base tokens in the desk, i.e., deposited but not lent.

.. py:function:: total_loans() -> uint256

    Returns the aggregate number of base tokens in all loans.

.. py:function:: total_reserved() -> uint256

    Returns the total number of base tokens reserved for withdrawal by all users.

.. note::

    When depositors submit a withdrawal request when not enough liquidity is available in the desk, the amount requested becomes a target level to be reserved until withdrawals are met. When loans are repaid, the additional liquidity is not available for re-lending until all the reserved target is matched. Reserved funds do not earn reward tokens.

.. py:function:: user_reserved(_user : address) -> uint256

    Returns the amount of base tokens the user wants to withdraw. Repaid base tokens from loans will not be lent again until that amount is met.

    * ``_user``: The address of the user whose reserved funds are sought

.. py:function:: user_loans(_user : address) -> uint256

    Returns the total of all loans taken by _user.

    * ``_user``: The address of the user whose loans amount is desired

.. py:function:: num_horizons() -> int128

    Returns the number of horizons accepted by this desk.

.. py:function:: get_horizon_and_fee(_i : int128) -> (uint256, uint256)
    
    Returns the i-th accepted horizon by this desk and the corresponding fee.

    * ``_i``: The index of the horizon. Use num_horizons() to get the full range

.. py:function:: num_longables() -> int128

    Returns the number of longable tokens accepted by this desk.

.. py:function:: get_longable(_i : int128) -> address

    Returns the i-th accepted longable token.

    * ``_i``: The index of the desired longable. Use ``num_longables`` to get the range