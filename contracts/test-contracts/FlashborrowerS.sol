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