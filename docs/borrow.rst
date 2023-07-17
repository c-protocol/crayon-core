.. index:: _borrowing

.. _borrowing:

Borrowing
#########

Traders can borrow the desk's base coin and post a longable token as collateral using one of two functions depending on which of the following use cases applies:

    * **Leveraging**: The trader holds a favorable view about a longable token and wants to multiply potential profits through leverage (note that leverage also multiplies potential losses).
    * **Financing**: The trader owns a longable token and needs funds but does not wish to sell that token.

The two functions available for borrowing are:

.. py:function:: borrow_then_post_longable(_amount: uint256, _longable: address, _longable_amount: uint256, _horizon: uint256, _contract: address, data: Bytes[256], _provider: address = empty(address)

    Borrow base coin and post longable satisfying value-to-loan ratio in one transaction using a smart contract deployed by the borrower

    * ``_amount``: The number of base_coin tokens to be borrowed
    * ``_longable`` The address of the ERC20 token that will be posted as collateral. Must be one of the approved longable tokens for this desk
    * ``_longable_amount``: The amount of longable to be posted against the loan at the end of the transaction
    * ``_horizon``: If a new loan, the loan expires at the block height _horizon blocks hence
    * ``_contract``: The address of the smart contract receiving the loan and that will also provide the required _longable_amount of the longable token
    * ``data``: Opaque calldata to be passed to the smart contract receiving the loan
    * ``_provider``: For use by third-party, front-end provider if applicable. Use default otherwise

.. note::

    The provider in this case could be a third party that provided the smart contract to its users.

.. py:function:: post_longable_then_borrow(_amount: uint256, _longable: address, _longable_amount: uint256, _horizon: uint256, _provider: address = empty(address)
    
    Post longable as collateral and borrow against it in one transaction. Can be used to borrow against excess collateral.

    * ``_amount``: The amount of base_coin to borrow
    * ``_longable``: The address of the ERC20 token used as longable
    * ``_longable_amount``: Amount of longable being posted against the loan. Can be 0 if borrowing against longable already posted
    * ``_horizon``: If a new loan, the loan expires at the block height _horizon blocks hence
    * ``_provider``: For use by third-party, front-end provider if applicable. Use default otherwise

.. note::

    The two borrowing functions will revert if the loan amount is so small the internally calculated borrowing fee is 0.

Users can call this function to determine the cost of borrowing:

.. py:function:: borrow_fee(_amount: uint256, _longable: address, _horizon: uint256, _is_extend : bool = False) -> uint256

    Return the fee that will be charged for the loan. This is a ``view`` function.

    * ``_amount``: The (new) amount to be borrowed. This is ignored if ``_is_extend = True``
    * ``_longable``: The token that will be deposited against the loan
    * ``_horizon``: The desired horizon. If a loan for ``msg.sender`` against ``_longable`` already exists, then ``_horizon`` is ignored and the expiration of the loan is unchanged
    * ``_is_extend``: Optional. ``True`` means an existing loan is being extended. Default is ``False``.


.. note::
    
    The fee will depend on the horizon unless a loan against the same longable token is active in which case the fee is based on the rate used at the inception of the loan.

Notes on borrowing
==================

* A user can only have one active loan against a specific longable token. This means that all borrowed funds secured by that longable token expire at the same time.
* A user can have multiple loans each secured by a different longable token and having different expiration dates.
* When a user with an active loan against a specific longable token borrows additional amounts of base token against that same longable token, _horizon is ignored and the original expiration date of the loan remains unchanged.
* Borrowing fees are added to the amount borrowed and are due, with the rest of the borrowed funds, at loan expiration.

Extending loan
==============

A loan expires at the block height determined by the chosen horizon at the time the loan is taken. This function allows extending the loan:

.. py:function:: extend_loan(_longable: address, _horizon: uint256)
    
    Extend the life of the loan taken by msg.sender against _longable longable
    
    * ``_longable``: Address of longable used as collateral for this loan
    * ``_horizon``: The horizon. The extended loan expires ``_horizon`` blocks after the original expiration block

.. note::

    The fee for extending the loan is the same fee that applies for a new loan for the amount and horizon of the loan being extended.

Managing Loans
==============

Two functions can be used to manage an existing loan in order to maintain the minimal value-to-loan ratio required by the desk.

.. py:function:: post_longable(_longable_amount: uint256, _longable: address, longable_owner: address = msg.sender)
    
    Add to the longable token backing an existing loan against that longable token in order to increase the value-to-loan ratio or park the longable tokens with a view of collecting fees from flashloans against that token.

    * ``_longable_amount``: Amount of longable being deposited
    * ``_longable``: ERC20 token address to use as longable
    * ``longable_owner``: Optional. Address to be credited for longable. This can be a borrowing smart contract. 

.. note::

    The last argument allows a user to deposit the longable token on behalf of another address. A use case for this is the user adding collateral to a loan taken by a smart contract the user deployed.

.. py:function:: withdraw_longable(_longable_amount: uint256, _longable: address)

    Withdraw some/all of existing longable posted for an existing or a previous (repaid) loan.

    * ``_longable_amount``: Amount of the longable token to withdraw
    * ``_longable``: Longable token to withdraw
    
.. note::

    For an existing loan, this function will revert if the amount of longable token remaining after the withdrawal will violate the required minimum value-to-loan ratio.

.. py:function:: loanOf(_user : address, _longable : address) -> (uint256, uint256, uint256)

    Returns information about the loan the user has taken against the specified longable: (``loan_amount``, ``collateral_amount``, ``loan_expiration``). This is a ``view`` function.

    * ``_user``: The address of the user
    * ``_longable``: The ERC20 token posted against the loan

.. note::

    Note that a user can have only one loan against a given longable token. The ``loan_expiration`` value is the block number at which the loan is due to expire.

.. _borrower_sample:

Template Borrow Contracts
=========================

Smart contracts deployed by leveraged traders can follow these two templates. The first is written in Vyper and the second in Solidity.


.. code-block:: python

    # @version ^0.3.7

    from vyper.interfaces import ERC20

    MAX_DATA_LENGTH: constant(int128) = 256

    interface CrayonDesk:
        def borrow_then_post_longable(
            _amount: uint256,
            _longable: address,
            _longable_amount: uint256,
            _horizon: uint256,
            _contract: address,
            data: Bytes[MAX_DATA_LENGTH],
            _provider: address = empty(address)
        ): nonpayable

        def withdraw_longable_then_repay(
            _amount: uint256,
            _longable: address,
            _longable_amount: uint256,
            _contract: address,
            data: Bytes[MAX_DATA_LENGTH],
            _provider: address = empty(address)
        ): nonpayable

        def base_coin() -> address: view
        
        def loanOf(
            _user: address,
            _longable: address
        ) -> (uint256, uint256, uint256): view

        def control_contract() -> address: view

    interface C_Control:
        def mint_all_reward_token(
            _user: address
        ): nonpayable

        def token_contract() -> address: view

    enum Action:
        buy
        sell

    desk: address
    owner: address

    @external
    def __init__(
        _desk: address
    ):
        self.desk = _desk
        self.owner = msg.sender

    @external
    def on_bridge_loan(
        _initiator: address,
        _token: address,
        _amount: uint256,
        data: Bytes[MAX_DATA_LENGTH]
    ) -> bytes32:
        """
        @dev Callback function used by desk when smart contract calls borrow_then_post_longable() or withdraw_longable_then_repay()
        @param _initiator The contract initiating the call
        @param _token The desk's base coin (when borrowing) or a longable (when unwinding the trade with repay())
        @param _amount The amount of tokens the desk transferred to this contract
        @param data Data that was initially built by this contract and that, for example, contains actions upon callback
        """

        # Only accept calls initiated from registered desk
        assert msg.sender == self.desk
        assert _initiator == self

        action : Action = _abi_decode(data, Action)
        # assert data was uncorrupted after passing through Pool
        if action == Action.buy:
            # enter position: for example, write the code to acquire the longable tokens
            pass
        elif action == Action.sell:
            # exit position: for example, write the code to swap the longable tokens for base tokens
            pass
        else:
            raise "on_bridge_loan(): unknown action"

        return keccak256('IBridgeBorrower.on_bridge_loan')

    @external
    def borrow(
        _amount: uint256,
        _horizon: uint256,
        _longable_token: address,
        _longable_amount: uint256,
        _provider: address
    ):
        """
        @dev Borrow base coin and post longable satisfying value_to_loan_ratio in one transaction
        @param _amount The number of base_coin tokens to be borrowed
        @param _horizon The horizon for this loan, i.e., the period for which the loan is desired. Must be one of the acceptable horizons
        @param _longable_token The address of the ERC20 token that will be posted. Must be one of the acceptable longable tokens
        @param _longable_amount The amount of longable to be posted against the loan at the end of the transaction
        @param _provider Set to empty(address) if writing your own contract. For use by front-end and/or third-party providers
        """

        assert msg.sender == self.owner

        # bespoke logic. we want to use the borrowed base coin to buy the longable token that we then post as collateral
        data : Bytes[MAX_DATA_LENGTH] = _abi_encode(Action.buy)

        # check how much borrower was already approved for
        allowance : uint256 = ERC20(_longable_token).allowance(self, self.desk)
        assert ERC20(_longable_token).approve(self.desk, allowance + _longable_amount)
        CrayonDesk(self.desk).borrow_then_post_longable(_amount, _longable_token, _longable_amount, _horizon, self, data, _provider)

    @external
    def repay(
        _longable_token: address,
        _provider: address
    ):
        """
        @dev Withdraw token posted as collateral and repay part/all of the loan in one transaction
        @param _longable_token The address of the ERC20 token that was posted
        @param _provider Set to empty(address) if writing your own contract. For use by front-end and/or third-party providers
        """

        assert msg.sender == self.owner

        amount : uint256 = 0
        longable_amount : uint256 = 0
        expiration : uint256 = max_value(uint256)
        # get loan position of this contract
        amount, longable_amount, expiration = CrayonDesk(self.desk).loanOf(self, _longable_token)

        borrow_token : address = CrayonDesk(self.desk).base_coin()
        allowance : uint256 = ERC20(borrow_token).allowance(self, self.desk)
        assert ERC20(borrow_token).approve(self.desk, allowance + amount)

        # bespoke logic. we want to sell the withdrawn collateral to generate the funds to pay back the loan
        data : Bytes[MAX_DATA_LENGTH] = _abi_encode(Action.sell)

        # pay back the full loan
        CrayonDesk(self.desk).withdraw_longable_then_repay(amount, _longable_token, longable_amount, self, data, _provider)

    @external
    def mint(
        _is_transferring : bool = False
    ):
        """
        @dev Mint the XCRAY reward tokens that have accumulated to this smart contract
        @param _is_transferring Optional parameter. True means transfer minted tokens to owner. Default is False
        """

        # One way to do it...
        control_contract : address = CrayonDesk(self.desk).control_contract()
        c_control : C_Control = C_Control(control_contract)
        c_control.mint_all_reward_token(self)
        if _is_transferring:
            xcToken : ERC20 = ERC20(c_control.token_contract())
            xcToken.transfer(self.owner, xcToken.balanceOf(self))


And a template for Solidity traders:

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
        function borrow_then_post_longable(
            uint256 _amount,
            address _longable,
            uint256 _longable_amount,
            uint256 _horizon,
            address _contract,
            bytes calldata data,
            address _provider) external;

        function withdraw_longable_then_repay(
            uint256 _amount,
            address _longable,
            uint256 _longable_amount,
            address _contract,
            bytes calldata data,
            address _provider) external;

        function base_coin() external view returns(address);
        
        function loanOf(
            address _user,
            address _longable) external view returns(uint256, uint256, uint256);

        function control_contract() external view returns(address);
    }


    interface C_Control {
        function mint_all_reward_token(
            address _user
        ) external;

        function token_contract() external view returns(address);
    }


    contract BorrowerS {
        enum Action{ BUY, SELL }

        address desk;
        address owner;

        constructor(address _desk) {

            /*
            * _desk is the desk from which we want to borrow
            */
            
            desk = _desk;
            owner = msg.sender;
        }

        function on_bridge_loan(
            address _initiator,
            address _token,
            uint256 _amount,
            bytes calldata data
        ) external returns(bytes32) {
            /**
            * @dev Callback function used by desk when contract calls borrow_then_post_longable() or withdraw_longable_then_repay()
            * @param _initiator The contract initiating the call
            * @param _token The desk's base coin (when borrowing) or a longable (when unwinding the trade with repay())
            * @param _amount The amount of tokens the desk transferred to this contract
            * @param data Data that was initially built by this contract and that, for example, contains actions upon callback
            */

            require(msg.sender == desk);
            require(_initiator == address(this));

            (Action action) = abi.decode(data, (Action));

            if (action == Action.BUY) {
                // enter position: for example, write the code to acquire the longable tokens
            } else if (action == Action.SELL) {
                // exit position: for example, write the code to swap the longable tokens for base tokens
            } else {
                revert("on_bridge_loan(): unknown action");
            }


            return keccak256("IBridgeBorrower.on_bridge_loan");
        }

        function borrow(
            uint256 _amount,
            uint256 _horizon,
            address _longable_token,
            uint256 _longable_amount,
            address _provider) external {
            /**
            * @dev Borrow base coin and post longable satisfying value_to_loan_ratio in one transaction
            * @param _amount The number of base_coin tokens to be borrowed
            * @param _horizon The horizon for this loan, i.e., the period for which the loan is desired. Must be one of the acceptable horizons
            * @param _longable_token The address of the ERC20 token that will be posted. Must be one of the acceptable longable tokens
            * @param _longable_amount The amount of longable to be posted against the loan at the end of the transaction
            * @param _provider Set to empty(address) if writing your own contract. For use by front-end and/or third-party providers
            */

            require(msg.sender == owner);

            bytes memory data = abi.encode((Action.BUY));

            uint256 allowance = IErc20(_longable_token).allowance(address(this), desk);
            require(IErc20(_longable_token).approve(desk, allowance + _longable_amount));
            CrayonDesk(desk).borrow_then_post_longable(_amount, _longable_token, _longable_amount, _horizon, address(this), data, _provider);
        }

        function repay(
            address _longable_token,
            address _provider) external {
            /**
            * @dev Withdraw token posted as collateral and repay part/all of the loan in one transaction
            * @param _longable_token The address of the ERC20 token that was posted
            * @param _provider Set to empty(address) if writing your own contract. For use by front-end and/or third-party providers
            */

            require(msg.sender == owner);

            uint256 amount = 0;
            uint256 longable_amount = 0;
            uint256 expiration = type(uint256).max;
            // get loan position of this contract
            (amount, longable_amount, expiration) = CrayonDesk(desk).loanOf(address(this), _longable_token);

            address borrow_token = CrayonDesk(desk).base_coin();
            uint256 allowance = IErc20(borrow_token).allowance(address(this), desk);
            require(IErc20(borrow_token).approve(desk, allowance + amount));

            // bespoke logic. we want to sell the withdrawn collateral to generate the funds to pay back the loan
            bytes memory data = abi.encode(Action.SELL);

            // pay back the full loan
            CrayonDesk(desk).withdraw_longable_then_repay(amount, _longable_token, longable_amount, address(this), data, _provider);
        }

        function mint(
            bool _is_transferring
        ) external {
            /**
            * @dev Mint the XCRAY reward tokens that have accumulated to this contract
            * @param _is_transferring Optional parameter. True means transfer minted tokens to owner
            */

            // One way to do it...
            address control_contract = CrayonDesk(desk).control_contract();
            C_Control c_control = C_Control(control_contract);
            c_control.mint_all_reward_token(address(this));
            if (_is_transferring) {
                IErc20 xcToken = IErc20(c_control.token_contract());
                xcToken.transfer(owner, xcToken.balanceOf(address(this)));
            }
        }
    }

