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

interface Oracle {
    function latestRoundData() external view returns(uint80, int256, uint256, uint256, uint80);
}

interface ICurvePool {
    function exchange(uint256 from, uint256 to, uint256 _from_amount, uint256 _min_to_amount) external;
    function get_dy(uint256 from, uint256 to, uint256 _from_amount) external view returns (uint256);
}

struct CrvData {
    address pool;
    uint256 amount;
    uint256 ind0;
    uint256 ind1;
    uint256 expected;
}

contract PairsTraderCurveS {

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
         * @param _token The desk's base coin at trade inception or a longable (when unwinding the trade with unwind())
         * @param _amount The amount of tokens the desk transferred to this contract
         * @param data The encoded CrvData object specifying the swap to be done on Curve
         */

        require(msg.sender == desk);
        require(_initiator == address(this));

        (CrvData memory crvData) = abi.decode(data, (CrvData));

        ICurvePool curvePool = ICurvePool(crvData.pool);
        // e is what the Curve pool predicts we will receive in the swap
        uint256 e = curvePool.get_dy(crvData.ind0, crvData.ind1, crvData.amount);
        // we committed to deposit crvData.expected coins to the Crayon desk. Make sure we are going to get them
        require (e >= crvData.expected);

        // swap
        IErc20(_token).approve(crvData.pool, crvData.amount);
        curvePool.exchange(crvData.ind0, crvData.ind1, crvData.amount, crvData.expected);
        
        return keccak256("IBridgeBorrower.on_bridge_loan");
    }

    function trade(
        address _crv_pool,
        uint256 _loan_amount,
        uint256 _cap,
        uint256 _horizon,
        uint256 _ind0,
        uint256 _ind1,
        address _longable_token,
        uint256 _longable_amount) external {
        /**
         * @dev Borrow base coin and post longable satisfying value_to_loan_ratio in one transaction
         * @param _crv_pool The Curve pool address where we're executing the swap
         * @param _loan_amount The number of base_coin tokens to be borrowed
         * @param _cap Initial capital in base_coin (the amount we want to leverage)
         * @param _horizon The horizon for this loan, i.e., the period for which the loan is desired. Must be one of the acceptable horizons
         * @param _ind0 The index of the coin we're swapping out of (selling) as specified in the Curve pool
         * @param _ind1 The index of the coin we're receiving
         * @param _longable_token The address of the ERC20 token that will be posted. Must be one of the acceptable longable tokens
         * @param _longable_amount The amount of _longable_token we will post as collateral
         */

        require(msg.sender == owner);

        uint256 allowance = IErc20(_longable_token).allowance(address(this), desk);
        require(IErc20(_longable_token).approve(desk, allowance + _longable_amount));

        // encode data needed for trade execution in callback
        bytes memory data = abi.encode(CrvData({pool: _crv_pool, amount: _loan_amount + _cap, ind0: _ind0, ind1: _ind1, expected: _longable_amount}));

        // submit
        CrayonDesk(desk).borrow_then_post_longable(_loan_amount, _longable_token, _longable_amount, _horizon, address(this), data, address(0));
    }

    function unwind(
        address _crv_pool,
        address _longable_token,
        uint256 _longable_excess,
        uint256 ind0,
        uint256 ind1) external {
        /**
         * @dev Withdraw token posted as collateral and repay part/all of the loan in one transaction
         * @param _longable_token The address of the ERC20 token that was posted
         * @param _longable_excess The amount of excess longable tokens (i.e., beyond what we had committed to deposit in Crayon Desk) that we received at trade inception
         * @param ind0 The index of the coin we're swapping out of (selling)
         * @param ind1 The index of the coin we're receiving
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

        // encode data needed for trade execution in callback. Note that here we just want out of the trade so we just set expected to 0
        bytes memory data = abi.encode(CrvData({pool: _crv_pool, amount: longable_amount + _longable_excess, ind0: ind0, ind1: ind1, expected: 0}));

        // pay back the full loan
        CrayonDesk(desk).withdraw_longable_then_repay(amount, _longable_token, longable_amount, address(this), data, address(0));
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

