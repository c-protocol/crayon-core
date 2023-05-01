.. index:: _flashloan

.. _flashloan:

Flash loans
###########

Base tokens or tokens deposited by borrowers as collateral are available for flash loans. Flash loans borrow and repay borrowed funds plus fees in the same transaction. To get a flash loan, users must deploy a smart contract that includes logic to use the borrowed loans (for example, a swap). It is the smart contract that receives the borrowed funds.

.. note::
    The flash loan is free if the amount of base tokens or longable tokens does not exceed the amount of those tokens deposited by the calling contract.

.. py:function:: flashloan(_amount: uint256, _token: address, _contract: address, data: Bytes[256])

    Borrow a token deposited as collateral and pay back the loan with fee in one transaction.

    * ``_amount``: Amount of token to be borrowed
    * ``_token``: The token of interest
    * ``_contract``: The smart contract to receive the loan. This is also the contract from which the call is expected to come.
    * ``data``: Calldata to pass to the loan receiver, i.e., _contract

.. note::

    This function will revert if ``_contract`` and ``msg.sender`` do not match.

.. py:function:: flashloan_fee() -> uint256

    Returns the fee required to take a flash loan. Returns value in bps. This is a ``view`` function.

.. py:function:: total_longable(_longable: address) -> uint256

    Returns the total of a longable token available for flash loans. Use ``total_liquidity()`` for the amount of available base tokens.

    * ``_longable``: The address of the ERC20 longable token the user wants to flashloan

.. note::

    The fee for a flash loan does not depend on the token being borrowed.


Sample Flash Loan Contract
==========================

.. code-block:: python

    # @version ^0.3.7

    from vyper.interfaces import ERC20

    256: constant(int128) = 256

    interface FlashLender:
        def flashloan_fee(
        ) -> uint256: view

        def flashloan(
            _amount: uint256,
            _token: address,
            _receiver: address,
            _data: Bytes[256]
        ): nonpayable

    enum Action:
        do_this
        do_that

    lender: address
    owner: address

    initial_balance: uint256

    @external
    def __init__(
        _lender: address
    ):
        self.lender = _lender
        self.owner = msg.sender

    @external
    def on_flash_loan(
        _initiator: address,
        _token: address,
        _amount: uint256,
        _fee: uint256,
        data: Bytes[256]
    ) -> bytes32:
        """
        @dev Callback function used by desk when contract calls flashloan()
        @param _initiator The contract initiating the call
        @param _token The token this contract is borrowing
        @param _amount The amount of _token the desk transferred to this contract
        @param _fee The fee for the flash loan. It's 0 if contract borrowed from its own deposit or its own collateral
        @param data Data that was initially built by this contract and that, for example, contains actions upon callback
        """

        assert msg.sender == self.lender
        assert _initiator == self

        assert ERC20(_token).balanceOf(self) == _amount + self.initial_balance

        action : Action = _abi_decode(data, Action)
        assert action == Action.do_this or action == Action.do_that
        if action == Action.do_this:
            # add logic for use of flash loan funds in do_this case
            pass
        else:
            # add logic for use of flash loan funds in do_that case
            pass

        return keccak256('IFlashBorrower.on_flash_loan')

    @external
    def flash_borrow(
        _token: address,
        _amount: uint256
    ):
        """
        @dev Borrow base token or longable token and pay it plus fees in one transaction. Note that the fee is 0 if borrowing from this contract's deposit or collateral posted by this contract
        @param _token The token to be borrowed
        @param _amount The amount of _token to borrow
        """

        assert msg.sender == self.owner

        # check how much lender was already approved for
        allowance : uint256 = ERC20(_token).allowance(self, self.lender)
        fee : uint256 = FlashLender(self.lender).flashloan_fee() * _amount / 10000
        repayment : uint256 = _amount + fee
    
        ERC20(_token).approve(self.lender, allowance + repayment)

        # action encoding bespoke logic
        data : Bytes[256] = _abi_encode(Action.do_this)

        self.initial_balance = ERC20(_token).balanceOf(self)

        FlashLender(self.lender).flashloan(_amount, _token, self, data)