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