.. index:: _flashloan

.. _flashloan:

Flash loans
###########

Base tokens or tokens deposited by borrowers as collateral are available for flash loans. Flash loans borrow and repay borrowed funds plus fees in the same transaction. To get a flash loan, users must deploy a smart contract that includes logic to use the borrowed loans (for example, a swap). It is the smart contract that receives the borrowed funds.

.. note::
    
    The flash loan is not charged any fee if the amount of base tokens or longable tokens does not exceed the amount of those tokens deposited by the calling smart contract. This incentives Crayon lenders and borrowers to help with :ref:`liquidation <liquidation>` of bad loans by increasing the profitability of the resulting arbitrage trades.

.. py:function:: flashloan(_amount: uint256, _token: address, _contract: address, data: Bytes[256])

    Borrow a token deposited as collateral and pay back the loan with fee in one transaction.

    * ``_amount``: Amount of token to be borrowed
    * ``_token``: The token of interest
    * ``_contract``: The smart contract to receive the loan. This is also the contract from which the call is expected to come.
    * ``data``: Calldata to pass to the loan receiver, i.e., _contract

.. note::

    This function will revert if ``_contract`` and ``msg.sender`` do not match. It will also revert if the flashloan amount is so small the fee is 0.

.. py:function:: flashloan_fee() -> uint256

    Returns the fee required to take a flash loan. Returns value in bps. This is a ``view`` function.

.. py:function:: total_longable(_longable: address) -> uint256

    Returns the total of a longable token available for flash loans. Use ``total_liquidity()`` for the amount of available base tokens.

    * ``_longable``: The address of the ERC20 longable token the user wants to flashloan

.. note::

    The fee for a flash loan does not depend on the token being borrowed.


Template Flash Loan Contracts
=============================

Flashloan loan borrowers can follow one of these templates for the smart contracts they deploy. The first is written in Vyper and the second in Solidity.

.. code-block:: python

    # @version ^0.3.7

    from vyper.interfaces import ERC20

    MAX_DATA_LENGTH: constant(int128) = 256

    interface CrayonDesk:
        def flashloan_fee(
        ) -> uint256: view

        def flashloan(
            _amount: uint256,
            _token: address,
            _receiver: address,
            _data: Bytes[MAX_DATA_LENGTH]
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
        data: Bytes[MAX_DATA_LENGTH]
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
        fee : uint256 = CrayonDesk(self.lender).flashloan_fee() * _amount / 10000
        repayment : uint256 = _amount + fee
    
        ERC20(_token).approve(self.lender, allowance + repayment)

        # action encoding bespoke logic
        data : Bytes[MAX_DATA_LENGTH] = _abi_encode(Action.do_this)

        self.initial_balance = ERC20(_token).balanceOf(self)

        CrayonDesk(self.lender).flashloan(_amount, _token, self, data)
        
And a template for Solidity borrowers:

.. code-block:: javascript

    // SPDX-License-Identifier: MIT

    pragma solidity=0.8.19;

    interface IErc20 {
        function allowance(address _from, address _to) external view returns(uint256);
        function transfer(address _to, uint _amount) external returns(bool success);
        function approve(address _to, uint _amount) external returns(bool success);
        function balanceOf(address _from) external view returns(uint256);
    }

    interface CrayonDesk {
        function flashloan_fee() external view returns(uint256);

        function flashloan(
            uint256 _amount,
            address _token,
            address _receiver,
            bytes calldata _data
        ) external;
    }

    contract FlashborrowerS {
        enum Action{DO_THIS, DO_THAT}

        address lender;
        address owner;

        uint256 initial_balance;

        constructor(address _lender) {
            /*
             * _lender is the desk from which we want to borrow
             */

            lender = _lender;
            owner = msg.sender;
        }

        function on_flash_loan(
            address _initiator,
            address _token,
            uint256 _amount,
            uint256 _fee,
            bytes calldata data
        ) external returns(bytes32) {
            /**
             * @dev Callback function used by desk when contract calls flashloan()
             * @param _initiator The contract initiating the call
             * @param _token The token this contract is borrowing
             * @param _amount The amount of _token the desk transferred to this contract
             * @param _fee The fee for the flash loan. It's 0 if contract borrowed from its own deposit or its own collateral
             * @param data Data that was initially built by this contract and that, for example, contains actions upon callback
             */

            require(msg.sender == lender);
            require(_initiator == address(this));

            require(IErc20(_token).balanceOf(address(this)) == _amount + initial_balance);

            (Action action) = abi.decode(data, (Action));
            require(action == Action.DO_THIS || action == Action.DO_THIS);
            if (action == Action.DO_THIS) {
                // add logic for use of flash loan funds in DO_THIS case
            } else {
                // add logic for use of flash loan funds in DO_THIS case
            }

            return keccak256("IFlashBorrower.on_flash_loan");
        }

        function flash_borrow(
            address _token,
            uint256 _amount
        ) external {
            /**
             * @dev Borrow base token or longable token and pay it plus fees in one transaction. Note that the fee is 0 if borrowing from this contract's deposit or collateral posted by this contract
             * @param _token The token to be borrowed
             * @param _amount The amount of _token to borrow
             */

            require(msg.sender == owner);

            // check how much lender was already approved for
            uint256 allowance = IErc20(_token).allowance(address(this), lender);
            uint256 fee = CrayonDesk(lender).flashloan_fee() * _amount / 10000;
            uint256 repayment = _amount + fee;
        
            IErc20(_token).approve(lender, allowance + repayment);

            // action encoding bespoke logic
            bytes memory data = abi.encode(Action.DO_THIS);

            initial_balance = IErc20(_token).balanceOf(address(this));

            CrayonDesk(lender).flashloan(_amount, _token, address(this), data);
        }
    }
