.. index:: _repay

.. _repay:

Repay a loan
############

Two functions are provided to pay back loans. ``withdraw_longable_then_repay`` was designed for the leveraged trade use case where the user swapped the borrowed base token for a longable token and then needs to swap back before the loan can be paid. 

``repay`` can be used to repay a loan taken by the user or a smart contract the user deployed but does not recover any of the longable token backing the loan.

.. py:function:: withdraw_longable_then_repay(_amount: uint256, _longable: address, _longable_amount: uint256, _contract: address, data: Bytes[256], _provider: address = empty(address))

    Retrieve posted longable and repay part or all of the loan in one transaction.

    * ``_amount``: Amount of the desk's base coin to be repaid
    * ``_longable``: The longable token used for the loan being repaid
    * ``_longable_amount``: The amount of longable tokens to withdraw
    * ``_contract``: The address of the contract that receives longable
    * ``data``: Calldata to longable receiver, i.e., ``_contract``
    * ``_provider``: Third-party provider if applicable

.. note::
    
    See :ref:`borrower sample <borrower_sample>` for an example usage.

This function can be called to increase the value-to-loan ratio (and decrease risk of liquidation).

.. py:function:: repay(_amount: uint256, _longable: address, _provider: address, _loan_owner: address = msg.sender)

    Repay part/full loan.

    * ``_amount``: Amount of base coin being repaid
    * ``_longable``: The longable token backing the loan being repaid
    * ``_provider``: Front end provider
    * ``_loan_owner``: Optional. Address that owns the loan. Default is ``msg.sender``
