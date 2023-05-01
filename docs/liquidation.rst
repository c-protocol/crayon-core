.. index:: _liquidation

.. _liquidation:

Liquidation 
###########

Tokens posted as collateral for loans whose value-to-loan ratio has dropped below the desk's minimum can be acquired at a liquidation bonus by liquidators who repay part of the loan. 

.. note::

    Values are calculated in terms of the desk's base coin which is also the desk's numeraire. For instance, if the base coin is ETH then all token prices are expressed in ETH for the purpose of calculating the value-to-loan ratio.

.. py:function:: liquidate(_user: address, _longable: address, _amount: uint256)
    
    Pay all/part of the liquidatable portion of a user's loan in exchange for discounted tokens.
    
    * ``_user``: The address whose loan can be liquidated
    * ``_longable``: The longable token backing the liquidatable loan
    * ``_amount``: The amount of loan the liquidator wants to Pay

The functions below can be used to get information on liquidation and liquidatable loans.

.. py:function:: liquidatable(_user: address, _longable: address) -> uint256
    
    Return the amount of the loan that ``_user`` has taken against ``_longable`` that is subject to liquidation. Returns 0 if the loan is not in violation of the desk's value-to-loan ratio. This is a ``view`` function.

    * ``_user``: The address whose loan is targeted
    * ``_longable``: The ERC20 token (longable) backing the targeted loan


.. py:function:: liquidation_bonus() -> uint256

    Return the desk's liquidation bonus in basis points (``1bps = 0.01%``). The liquidator receives ``x * ( 1 + liquidation_bonus / 10000)`` worth of tokens for an amount ``x`` paid for liquidating a loan. This is a ``view`` function.