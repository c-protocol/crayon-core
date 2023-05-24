.. index:: _depositing

.. _depositing:

Lending
#######

Users deposit the desk's base token using the ``deposit`` function.

.. py:function:: deposit(_amount: uint256, _provider: address = empty(address))

    Deposit base coin into the desk for lending.

    * ``_amount``: Amount of base coin being deposited
    * ``_provider``: For use by front-end providers, if applicable

.. note::

    Users who use a smart contract to make their deposit, can then flashloan up to their full deposit with no fee if the same smart contract is used for the flashloan. See :ref:`Flashloan <flashloan>`.

.. py:function:: balanceOf(_user : address) -> uint256

    Returns the base token balance of a user. This is a ``view`` function.

    * ``_user``: The address of the user
