# @version ^0.3.7

#
# Smart contract that can be used for borrowing (for leveraged trading) and flashloans and deposits.
#

from vyper.interfaces import ERC20

MAX_DATA_LENGTH: constant(int128) = 256

interface CrayonDesk:
    def deposit(
        _amount: uint256,
        _provider: address = empty(address)
    ): nonpayable

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

    def flashloan_fee(
    ) -> uint256: view

    def flashloan(
        _amount: uint256,
        _token: address,
        _receiver: address,
        _data: Bytes[MAX_DATA_LENGTH]
    ): nonpayable


interface C_Control:
    def mint_all_reward_token(
        _user: address
    ): nonpayable

    def token_contract() -> address: view

enum BorrowAction:
    buy
    sell

enum FlashAction:
    do_this
    do_that

desk: address
owner: address

initial_balance: uint256

@external
def __init__(
    _desk: address
):
    self.desk = _desk
    self.owner = msg.sender

@external
def deposit(
    _amount: uint256
):
    assert msg.sender == self.owner

    base_coin : address = CrayonDesk(self.desk).base_coin()
    allowance : uint256 = ERC20(base_coin).allowance(self, self.desk)
    assert ERC20(base_coin).approve(self.desk, allowance + _amount)

    CrayonDesk(self.desk).deposit(_amount)

@external
def on_bridge_loan(
    _initiator: address,
    _token: address,
    _amount: uint256,
    data: Bytes[MAX_DATA_LENGTH]
) -> bytes32:
    """
    @dev Callback function used by desk when contract calls borrow_then_post_longable() or withdraw_longable_then_repay()
    @param _initiator The contract initiating the call
    @param _token The desk's base coin
    @param _amount The amount of tokens the desk transferred to this contract
    @param data Data that was initially built by this contract and that, for example, contains actions upon callback
    """

    # Only accept calls initiated from registered desk
    assert msg.sender == self.desk
    assert _initiator == self

    action : BorrowAction = _abi_decode(data, BorrowAction)
    # assert data was uncorrupted after passing through Pool
    if action == BorrowAction.buy:
        # enter position: for example, write the code to acquire the longable tokens
        pass
    elif action == BorrowAction.sell:
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
    data : Bytes[MAX_DATA_LENGTH] = _abi_encode(BorrowAction.buy)

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
    data : Bytes[MAX_DATA_LENGTH] = _abi_encode(BorrowAction.sell)

    # pay back the full loan
    CrayonDesk(self.desk).withdraw_longable_then_repay(amount, _longable_token, longable_amount, self, data, _provider)

@external
def mint(
    _is_transferring : bool = False
):
    """
    @dev Mint the XCRAY reward tokens that have accumulated to this contract
    @param _is_transferring Optional parameter. True means transfer minted tokens to owner. Default is False
    """

    # One way to do it...
    control_contract : address = CrayonDesk(self.desk).control_contract()
    c_control : C_Control = C_Control(control_contract)
    c_control.mint_all_reward_token(self)
    if _is_transferring:
        xcToken : ERC20 = ERC20(c_control.token_contract())
        xcToken.transfer(self.owner, xcToken.balanceOf(self))

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

    assert msg.sender == self.desk
    assert _initiator == self

    assert ERC20(_token).balanceOf(self) == _amount + self.initial_balance

    action : FlashAction = _abi_decode(data, FlashAction)
    assert action == FlashAction.do_this or action == FlashAction.do_that
    if action == FlashAction.do_this:
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

    # check how much desk was already approved for
    allowance : uint256 = ERC20(_token).allowance(self, self.desk)
    fee : uint256 = CrayonDesk(self.desk).flashloan_fee() * _amount / 10000
    repayment : uint256 = _amount + fee
   
    ERC20(_token).approve(self.desk, allowance + repayment)

    # action encoding bespoke logic
    data : Bytes[MAX_DATA_LENGTH] = _abi_encode(FlashAction.do_this)

    self.initial_balance = ERC20(_token).balanceOf(self)

    CrayonDesk(self.desk).flashloan(_amount, _token, self, data)