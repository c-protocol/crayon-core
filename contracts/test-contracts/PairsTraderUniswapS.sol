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

interface IUniSwapRouter {
    struct ExactInputParams {
        bytes path;
        address recipient;
        uint256 deadline;
        uint256 amountIn;
        uint256 amountOutMinimum;
    }
    
    function exactInput(ExactInputParams calldata params) external payable returns (uint256 amountOut);
}

struct UniData {
    uint256 amount;
    address first;
    address middle;
    address last;
    uint256 expected;
}

contract PairsTraderUniswapS {

    address constant uniswapRouterV3 = 0xE592427A0AEce92De3Edee1F18E0157C05861564;

    // Note that uni_fee should probably be a parameter we pass to trade() and unwind() since it helps identify the uniswap pool. the change is straightforward
    uint24 constant uni_fee = 500;

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
         * @param data The encoded UniData object specifying the swap to be done on Uniswap v3
         */

        require(msg.sender == desk);
        require(_initiator == address(this));

        (UniData memory uniData) = abi.decode(data, (UniData));
        // use 1 or 2-hop swap
        bytes memory path = 
            uniData.middle != address(0)
                ? abi.encodePacked(uniData.first, uni_fee, uniData.middle, uni_fee, uniData.last)
                : abi.encodePacked(uniData.first, uni_fee, uniData.last);

        IUniSwapRouter.ExactInputParams memory params = IUniSwapRouter.ExactInputParams({
            path: path,
            recipient: address(this),
            deadline: block.timestamp,
            amountIn: uniData.amount,
            amountOutMinimum: uniData.expected
        });

        
        require(IErc20(_token).approve(uniswapRouterV3, uniData.amount));        
        IUniSwapRouter(uniswapRouterV3).exactInput(params);

        return keccak256("IBridgeBorrower.on_bridge_loan");
    }

    function trade(
        uint256 _loan_amount,
        uint256 _cap,
        uint256 _horizon,
        address _longable_token,
        uint256 _longable_amount,
        address _middle) external {
        /**
         * @dev Borrow base coin and post longable satisfying value_to_loan_ratio in one transaction
         * @param _loan_amount The number of base_coin tokens to be borrowed
         * @param _cap Initial capital in base_coin (the amount we want to leverage)
         * @param _horizon The horizon for this loan, i.e., the period for which the loan is desired. Must be one of the acceptable horizons
         * @param _longable_token The address of the ERC20 token that will be posted. Must be one of the acceptable longable tokens
         * @param _longable_amount The amount of _longable_token we will post as collateral
         * @param _middle The intermediate token in two-hop uniswap swap.  address(0) means use a one-hop swap
         */

        require(msg.sender == owner);
        
        uint256 allowance = IErc20(_longable_token).allowance(address(this), desk);
        require(IErc20(_longable_token).approve(desk, allowance + _longable_amount));

        // encode data needed for trade execution in callback
        bytes memory data = abi.encode(UniData({amount: _loan_amount + _cap, first: CrayonDesk(desk).base_coin(), middle: _middle, last: _longable_token, expected: _longable_amount}));

        // submit
        CrayonDesk(desk).borrow_then_post_longable(_loan_amount, _longable_token, _longable_amount, _horizon, address(this), data, address(0));
    }

    function unwind(
        address _longable_token,
        uint256 _longable_excess,
        address _middle) external {
        /**
         * @dev Withdraw token posted as collateral and repay the loan in one transaction
         * @param _longable_token The address of the ERC20 token that was posted
         * @param _longable_excess The amount of longable tokens that we received at trade inception in excess of what we had committed to deposit in Crayon Desk. When unwinding we want to liquidate that excess too
         * @param _middle The intermediate token in two-hop uniswap swap. address(0) means use a one-hop swap
         */

        require(msg.sender == owner);

        uint256 amount = 0;
        uint256 longable_amount = 0;
        uint256 expiration = type(uint256).max;
        // get loan position of this contract against _longable_token
        (amount, longable_amount, expiration) = CrayonDesk(desk).loanOf(address(this), _longable_token);

        address borrow_token = CrayonDesk(desk).base_coin();
        uint256 allowance = IErc20(borrow_token).allowance(address(this), desk);
        require(IErc20(borrow_token).approve(desk, allowance + amount));

        // encode data needed for trade execution in callback. Note that here we want out of the trade so expected is set to 0
        bytes memory data = abi.encode(UniData({amount: longable_amount + _longable_excess, first: _longable_token, middle: _middle, last: CrayonDesk(desk).base_coin(), expected: 0}));

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

