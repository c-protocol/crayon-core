# @version ^0.3.7

from vyper.interfaces import ERC20

MAX_DATA_LENGTH: constant(int128) = 256

interface LongDesk:
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

interface Oracle:
    def latestRoundData() -> (uint80, int256, uint256, uint256, uint80): view
    def decimals() -> uint8: view

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
    @dev Callback function used by desk when contract calls borrow_then_post_longable() or withdraw_longable_then_repay()
    @param _initiator The contract initiating the call
    @param _token The desk's base coin
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
    _longable_oracle: address,
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
    ERC20(_longable_token).approve(self.desk, allowance + _longable_amount)
    LongDesk(self.desk).borrow_then_post_longable(_amount, _longable_token, _longable_amount, _horizon, self, data, _provider)

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
    amount, longable_amount, expiration = LongDesk(self.desk).loanOf(self, _longable_token)

    borrow_token : address = LongDesk(self.desk).base_coin()
    allowance : uint256 = ERC20(borrow_token).allowance(self, self.desk)
    assert ERC20(borrow_token).approve(self.desk, allowance + amount)

    # bespoke logic. we want to sell the withdrawn collateral to generate the funds to pay back the loan
    data : Bytes[MAX_DATA_LENGTH] = _abi_encode(Action.sell)

    # pay back the full loan
    LongDesk(self.desk).withdraw_longable_then_repay(amount, _longable_token, longable_amount, self, data, _provider)

@external
def mint(
    _is_transferring : bool = False
):
    """
    @dev Mint the XCRAY reward tokens that have accumulated to this contract
    @param _is_transferring Optional parameter. True means transfer minted tokens to owner. Default is False
    """

    # One way to do it...
    control_contract : address = LongDesk(self.desk).control_contract()
    c_control : C_Control = C_Control(control_contract)
    c_control.mint_all_reward_token(self)
    if _is_transferring:
        xcToken : ERC20 = ERC20(c_control.token_contract())
        xcToken.transfer(self.owner, xcToken.balanceOf(self))