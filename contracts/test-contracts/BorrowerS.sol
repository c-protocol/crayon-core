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
         * @param _token The desk's base coin
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

