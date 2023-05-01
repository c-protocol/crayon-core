.. index:: _withdrawing

.. _withdrawing:

Withdrawing
###########

To withdraw base token deposited in the desk use ``withdraw``.


.. py:function:: withdraw(_amount: uint256, _provider: address = empty(address))

    Withdraw part/all of deposit

    * ``_amount``: The amount of base coin to be withdrawn
    * ``_provider``: For use by front-end providers, if applicable

.. note::

    If the amount submitted by the user exceeds the user's balance, then the entire balance is transferred to the user.

.. note::

    The user can call ``withdraw`` even if current total liquidity is less than the amount to be withdrawn. In this case, funds are **reserved** for the user. This means that funds from repaid loans will not be lent out again until withdrawal requests are met.
