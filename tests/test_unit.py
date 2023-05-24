import pytest

from brownie.network.state import Chain
from brownie import BorrowFlashDeposit
import brownie
from utils import min_longable_amount

# Number of blocks that the Control smart contract waits before implementing new fees, etc., on a desk. This number in production is the roughly number of blocks in a week. This number here is just for testing
MIN_WAITING_PERIOD= 10

def test_initial_state(long_desk):
    assert long_desk.total_liquidity() == 0
    assert long_desk.total_loans() == 0
    assert long_desk.total_reserved() == 0

def test_lending(long_desk, base_token, lender1, lender2, lender3, provider1, provider2):
    b1 = base_token.balanceOf(lender1)
    b2 = base_token.balanceOf(lender2)
    b3 = base_token.balanceOf(lender3)

    base_token.approve(long_desk, 5000e18, {'from': lender1})
    long_desk.deposit(5000e18, provider1, {'from': lender1})
    base_token.approve(long_desk, 123000e18, {'from': lender2})
    long_desk.deposit(123000e18, provider2, {'from': lender2})
    base_token.approve(long_desk, 23182e18, {'from': lender3})
    long_desk.deposit(23182e18, provider2, {'from': lender3})

    assert long_desk.total_liquidity() == 5000e18 + 123000e18 + 23182e18
    
    assert long_desk.balanceOf(lender1) == 5000e18
    assert long_desk.balanceOf(lender2) == 123000e18
    assert long_desk.balanceOf(lender3) == 23182e18
    assert base_token.balanceOf(lender1) == b1 - 5000e18
    assert base_token.balanceOf(lender2) == b2 - 123000e18
    assert base_token.balanceOf(lender3) == b3 - 23182e18

    long_desk.withdraw(1000e18, provider1, {'from': lender1})
    long_desk.withdraw(12000e18, provider2, {'from': lender3})

    assert long_desk.balanceOf(lender1) == 5000e18 - 1000e18
    assert long_desk.balanceOf(lender3) == 23182e18 - 12000e18    
    assert base_token.balanceOf(lender1) == b1 - 5000e18 + 1000e18
    assert base_token.balanceOf(lender3) == b3 - 23182e18 + 12000e18
    # avoid subtraction next to work around rounding error quirks
    assert long_desk.total_liquidity() + 1000e18 + 12000e18 == 5000e18 + 123000e18 + 23182e18 

@pytest.fixture
def funded_desk(long_desk, base_token, lender1, lender2, lender3, provider1, provider2):
    base_token.approve(long_desk, 5000e18, {'from': lender1})
    long_desk.deposit(5000e18, provider1, {'from': lender1})
    base_token.approve(long_desk, 123000e18, {'from': lender2})
    long_desk.deposit(123000e18, provider2, {'from': lender2})
    base_token.approve(long_desk, 23182e18, {'from': lender3})
    long_desk.deposit(23182e18, provider2, {'from': lender3})

    yield long_desk

def test_pre_borrowing(funded_desk, base_token, borrower1, contract_borrower1, longable1, oracle1, borrower2, contract_borrower2, longable2, oracle2, provider1, provider2, horizons, lender1):

    assert funded_desk.balanceOf(lender1) == 5000e18

    def borrow(loan, horizon, borrower, longable, contract_borrower, oracle, provider):
        fee = funded_desk.borrow_fee(loan, longable, horizon, {'from': contract_borrower})
        # posted longable will come from borrower contract. seed it
        longable.transfer(contract_borrower, longable.balanceOf(borrower), {'from': borrower})
        # borrower contract also has to pay fee for loan
        base_token.transfer(contract_borrower, fee, {'from': borrower})
        b = base_token.balanceOf(contract_borrower)
        longable_decimals = longable.decimals()
        borrow_fee = funded_desk.borrow_fee(loan, longable, horizon)
        longable_amount = min_longable_amount(loan, longable_decimals, oracle, funded_desk.value_to_loan_ratio(), base_token.decimals(), borrow_fee)
        contract_borrower.borrow(loan, horizon, longable, longable_amount, provider, {'from': borrower})
        # next assertion's success depends on actions in the borrowing contract
        assert base_token.balanceOf(contract_borrower) == b + loan
        return fee

    tot_liq = funded_desk.total_liquidity()
    # assume base coin is stable coin. loan1 is USD
    base_token_decimals = funded_desk.base_coin_decimals()

    loan1 = 45000 * 10**base_token_decimals
    fee1 = borrow(loan1, horizons[0], borrower1, longable1, contract_borrower1, oracle1, provider1)

    loan2 = 20100e18
    fee2 = borrow(loan2, horizons[1], borrower2, longable2, contract_borrower2, oracle2, provider2)

    assert funded_desk.total_loans() == loan1 + fee1 + loan2 + fee2
    assert funded_desk.total_liquidity() == tot_liq - loan1 - loan2 

    # now repay
    def repay(borrower, longable, contract_borrower, provider):
        pre_repay_base_bal = base_token.balanceOf(contract_borrower)
        pre_repay_longable_bal = longable.balanceOf(contract_borrower)
        loan_balance, longable_amount, _ = funded_desk.loanOf(contract_borrower, longable)
        contract_borrower.repay(longable, provider, {'from': borrower})
        assert base_token.balanceOf(contract_borrower) == pre_repay_base_bal - loan_balance
        assert longable.balanceOf(contract_borrower) == pre_repay_longable_bal + longable_amount

    repay(borrower2, longable2, contract_borrower2, provider2)
    repay(borrower1, longable1, contract_borrower1, provider1)

def test_deposit_borrow_and_flash(lender1, borrower1, provider1, long_desk, longable1, base_token, horizons, erc20token_admin):

    # test smart contracts that flashborrow below their deposit or collateral do not pay a fee

    lender_contract = lender1.deploy(BorrowFlashDeposit, long_desk)
    base_token.transfer(lender_contract, 1000000e18, {'from': erc20token_admin})
    lender_contract.deposit(300000e18, {'from': lender1})
    lender_contract.flash_borrow(base_token, 300000e18, {'from': lender1})

    # assert no fee was paid
    assert base_token.balanceOf(lender_contract) == 1000000e18 - 300000e18

    borrower_contract = borrower1.deploy(BorrowFlashDeposit, long_desk)
    longable1.transfer(borrower_contract, 1000000e18, {'from': erc20token_admin})
        
    borrower_contract.borrow(15000e18, horizons[0], longable1, 50000e18, provider1, {'from': borrower1})
    borrower_contract.flash_borrow(longable1, 45000e18, {'from': borrower1})

    # assert no fee was paid
    assert longable1.balanceOf(borrower_contract) == 1000000e18 - 50000e18

def test_post_borrowing(funded_desk, base_token, borrower1, longable1, oracle1, borrower2, longable2, oracle2, horizons, provider1, provider2):

    def post_longable_then_borrow(loan, borrower, longable, oracle, horizon, provider):
        fee = funded_desk.borrow_fee(loan, longable, horizon, {'from': borrower})
        # check how much desk was already approved for
        allowance = longable.allowance(borrower, funded_desk)
        ltv = funded_desk.value_to_loan_ratio() / 100
        (a, longable_price, b, c, d) = oracle.latestRoundData()
        oracle_decimals = oracle.decimals()
        longable_decimals = longable.decimals()
        longable_amount = (loan + fee) * ltv * 10 ** (oracle_decimals + longable_decimals) / (longable_price * 10**borrow_token_decimals) + 10 ** longable_decimals
        
        longable.approve(funded_desk, allowance + longable_amount, {'from': borrower})
        b = base_token.balanceOf(borrower)
        cb = longable.balanceOf(borrower)
        l, c, _ = funded_desk.loanOf(borrower, longable)
        funded_desk.post_longable_then_borrow(loan, longable, longable_amount, horizon, provider, {'from': borrower})
        assert base_token.balanceOf(borrower) == b + loan
        assert longable.balanceOf(borrower) == cb - longable_amount
        lp, cp, _ = funded_desk.loanOf(borrower, longable)
        assert lp == l + loan + fee
        assert cp == c + longable_amount

        return fee

    borrow_token_decimals = funded_desk.base_coin_decimals()
    tot_liq = funded_desk.total_liquidity()

    loan1 = 45000 * 10**borrow_token_decimals
    fee1 = post_longable_then_borrow(loan1, borrower1, longable1, oracle1, horizons[0], provider1)

    loan2 = 20100 * 10**borrow_token_decimals
    fee2 = post_longable_then_borrow(loan2, borrower2, longable2, oracle2, horizons[0], provider2)

    assert funded_desk.total_loans() == loan1 + fee1 + loan2 + fee2
    assert funded_desk.total_liquidity() == tot_liq - loan1 - loan2 

    bal = longable1.balanceOf(borrower1)
    lo, col, _ = funded_desk.loanOf(borrower1, longable1)
    add_longable = 1000 * 10**longable1.decimals()
    longable1.approve(funded_desk, add_longable, {'from': borrower1})
    funded_desk.post_longable(add_longable, longable1, {'from': borrower1})
    assert longable1.balanceOf(borrower1) == bal - add_longable
    lop, colp, _ = funded_desk.loanOf(borrower1, longable1)
    assert lop == lo
    assert colp == col + add_longable

    funded_desk.withdraw_longable(add_longable, longable1, {'from': borrower1})
    assert longable1.balanceOf(borrower1) == bal
    lop2, colp2 , _ = funded_desk.loanOf(borrower1, longable1)
    assert lop2 == lo
    assert colp2 == col

@pytest.fixture
def funded_posted_desk(funded_desk, borrower1, borrower2, longable1, longable2):
    longable1.approve(funded_desk, 100000 * 10**longable1.decimals(), {'from': borrower1})
    funded_desk.post_longable(10000 * 10**longable1.decimals(), longable1, {'from': borrower1})
    longable2.approve(funded_desk, 234567 * 10**longable2.decimals(), {'from': borrower2})
    funded_desk.post_longable(234567 * 10**longable2.decimals(), longable2, {'from': borrower2})

    yield funded_desk

def test_flashloan(flashborrower, longable2, funded_posted_desk, contract_flashborrower, erc20token_admin):
    col_decimals = longable2.decimals()
    # seed contract_flashborrower with some tokens to pay flash loan fee
    flashloan_amount = 100000*10**col_decimals
    longable2.transfer(contract_flashborrower, 1000 * 10**col_decimals, {'from': erc20token_admin})
    # get initial holdings
    flash_fee = funded_posted_desk.flashloan_fee() * flashloan_amount // 10000
    longable2_supply = funded_posted_desk.total_longable(longable2)

    contract_flashborrower.flash_borrow(longable2, flashloan_amount, {'from': flashborrower})

    assert funded_posted_desk.total_longable(longable2) == longable2_supply + flash_fee


def test_extend_loan(borrower1, longable1, funded_posted_desk, horizons, provider1):
    # borrower1 has already posted longable in funded_posted_desk
    loan = 10000 * 10**18
    fee = funded_posted_desk.borrow_fee(loan, longable1, horizons[0], {'from': borrower1})
    funded_posted_desk.post_longable_then_borrow(loan, longable1, 0, horizons[0], provider1, {'from': borrower1})
    l, c, e = funded_posted_desk.loanOf(borrower1, longable1)
    assert l == loan + fee
    assert funded_posted_desk.total_reserved() <= funded_posted_desk.total_liquidity()
    feefee = funded_posted_desk.borrow_fee(l, longable1, horizons[2], True, {'from': borrower1})
    funded_posted_desk.extend_loan(longable1, horizons[2], {'from': borrower1})
    l2, c2, e2 = funded_posted_desk.loanOf(borrower1, longable1)
    assert l2 == l + feefee
    assert c == c2
    assert e2 == e + horizons[2]
    

def test_liquidate(borrower1, longable1, oracle1, funded_posted_desk, erc20token_admin, base_token, liquidator, horizons, provider1):
    l, c, _ = funded_posted_desk.loanOf(borrower1, longable1)
    assert l == 0

    # borrower1 has already posted longable in funded_posted_desk
    (_, longable_price, _, _, _) = oracle1.latestRoundData()
    oracle_decimals = oracle1.decimals()
    # value_to_loan_ratio is stored as a percentage
    ltv = funded_posted_desk.value_to_loan_ratio() / 100
    base_token_decimals = funded_posted_desk.base_coin_decimals()
    longable_decimals = longable1.decimals()
    _, fee = funded_posted_desk.get_horizon_and_fee(0)

    max_loan = c * longable_price / ltv * 10**(base_token_decimals-oracle_decimals-longable_decimals) / (1+fee/10000)
    funded_posted_desk.post_longable_then_borrow(max_loan-10**base_token_decimals, longable1, 0, horizons[0], provider1, {'from': borrower1})

    assert funded_posted_desk.liquidatable(borrower1, longable1) == 0
    init_price = oracle1.token_price()
    crash_price = init_price // 2
    # set_token_price() takes the price excluding full decimals precision
    oracle1.set_token_price(crash_price, {'from': erc20token_admin})
    assert crash_price == oracle1.token_price()
    l, c, _ = funded_posted_desk.loanOf(borrower1, longable1)
    liquidatable_amount = funded_posted_desk.liquidatable(borrower1, longable1)
    assert liquidatable_amount == l
    
    # seed the liquidator with some base coin
    base_token.transfer(liquidator, liquidatable_amount, {'from': erc20token_admin})
    liquidation_bonus = funded_posted_desk.liquidation_bonus()
    bb = base_token.balanceOf(liquidator)
    cb = longable1.balanceOf(liquidator)
    base_token.approve(funded_posted_desk, liquidatable_amount, {'from': liquidator})
    funded_posted_desk.liquidate(borrower1, longable1, liquidatable_amount, {'from': liquidator})
    bbpost = base_token.balanceOf(liquidator)
    cbpost = longable1.balanceOf(liquidator)
    assert abs(((cbpost - cb) / 10**longable_decimals) * (crash_price / 10**oracle_decimals) - (bb-bbpost) * (1 + liquidation_bonus/10000) / 10**base_token_decimals) < 10**-oracle_decimals

def test_reserve(borrower1, longable1, oracle1, base_token, funded_desk, lender1, provider1, horizons):
    longable_price = oracle1.token_price()
    longable_decimals = longable1.decimals()
    oracle_decimals = oracle1.decimals()
    base_token_decimals = funded_desk.base_coin_decimals()
    ltv = funded_desk.value_to_loan_ratio() / 100
    total_liquidity = funded_desk.total_liquidity()
    borrow_fee = funded_desk.borrow_fee(total_liquidity, longable1, horizons[0], {'from': borrower1})
    required_longable = ltv * (total_liquidity + borrow_fee) * 10**oracle_decimals * 10**longable_decimals / (10**base_token_decimals * longable_price) + 10**longable_decimals
    bpre = base_token.balanceOf(borrower1)
    longable1.approve(funded_desk, required_longable, {'from': borrower1})
    funded_desk.post_longable_then_borrow(total_liquidity, longable1, required_longable, horizons[0], provider1, {'from': borrower1})
    assert base_token.balanceOf(borrower1) == bpre + total_liquidity
    assert funded_desk.total_liquidity() == 0 and funded_desk.total_reserved() == 0 and funded_desk.total_loans() == total_liquidity + borrow_fee

    balance_lender1 = funded_desk.balanceOf(lender1)
    lender1_withdrawal = balance_lender1//2
    funded_desk.withdraw(lender1_withdrawal, provider1, {'from': lender1})
    assert funded_desk.total_reserved() == lender1_withdrawal
    assert funded_desk.user_reserved(lender1) == lender1_withdrawal

    with brownie.reverts(''):
        funded_desk.extend_loan(longable1, horizons[2], {'from': borrower1})

    base_token.approve(funded_desk, lender1_withdrawal, {'from': borrower1})
    funded_desk.repay(lender1_withdrawal, longable1, provider1, borrower1, {'from': borrower1})
    assert funded_desk.total_liquidity() == lender1_withdrawal
    base_token_lender1 = base_token.balanceOf(lender1)
    funded_desk.withdraw(lender1_withdrawal, provider1, {'from': lender1})
    assert funded_desk.total_reserved() == 0
    assert base_token_lender1 + lender1_withdrawal == base_token.balanceOf(lender1)

# # def test_set_fee(long_desk, c_control, control_admin):
# #     h, f = long_desk.get_horizon_and_fee(1)
# #     assert f == 18
# #     assert long_desk.horizons(h) == f
# #     c_control.schedule_new_fee(h, 27, long_desk, {'from': control_admin})
# #     Chain().mine(MIN_WAITING_PERIOD)
# #     c_control.commit_new_fee(long_desk, h, {'from': control_admin})
# #     assert long_desk.horizons(h) == 27

# # def test_set_flashloan_fee(long_desk, c_control, control_admin):
# #     assert long_desk.flashloan_fee() == 9
# #     c_control.schedule_new_flashloan_fee(18, long_desk, {'from': control_admin})
# #     Chain().mine(MIN_WAITING_PERIOD)
# #     c_control.commit_new_flashloan_fee(long_desk, {'from': control_admin})
# #     assert long_desk.flashloan_fee() == 18

# # def test_set_liquidation_bonus(long_desk, c_control, control_admin):
# #     assert long_desk.liquidation_bonus() == 500
# #     c_control.schedule_new_liquidation_bonus(600, long_desk, {'from': control_admin})
# #     Chain().mine(MIN_WAITING_PERIOD)
# #     c_control.commit_new_liquidation_bonus(long_desk, {'from': control_admin})
# #     assert long_desk.liquidation_bonus() == 600

def test_set_admin(c_control, control_admin, accounts):
    assert c_control.admin() == control_admin
    mock_admin = accounts.add()
    c_control.set_admin(mock_admin, {'from': control_admin})
    assert c_control.admin() == mock_admin

def test_get_horizon_and_fee(long_desk, horizons, borrow_fees):
    for i in range(len(horizons)):
        h, f = long_desk.get_horizon_and_fee(i)
        assert h == horizons[i] and f == borrow_fees[i]

def test_get_longable(long_desk, longables):
    for i in range(len(longables)):
        l = long_desk.get_longable(i)
        assert l == longables[i]

def test_loanof_corner(long_desk, longables, accounts):
    user = accounts.add()
    l, c, _ = long_desk.loanOf(user, longables[0])
    assert l == 0 and c == 0

def test_rewards(xctoken, long_desk, c_control, base_token, lender1, lender2, borrower1, longable1, horizons, provider1, provider2):
    base_coin_decimals = long_desk.base_coin_decimals()

    borrow_reward_per_block, deposit_reward_per_block = c_control.get_reward_parameters(long_desk)
    prov_percent_1 = c_control.provider_percentage(provider1)
    prov_percent_2 = c_control.provider_percentage(provider2)
    
    chain = Chain()

    def dep_reward(lender, provider, prov_percent, dep, n_blocks):
        if dep != 0:
            base_token.approve(long_desk, dep, {'from': lender})
            long_desk.deposit(dep, provider, {'from': lender})
        c_control.mint_all_reward_token(lender)
        deposit_cumul = long_desk.deposit_cumul_reward()
        cbal = xctoken.balanceOf(lender)
        chain.mine(n_blocks)
        c_control.mint_all_reward_token(lender)
        assert long_desk.deposit_cumul_reward() - deposit_cumul == (n_blocks+1) * deposit_reward_per_block // (long_desk.total_liquidity() + long_desk.total_loans())
        reward = (long_desk.deposit_cumul_reward() - deposit_cumul) * long_desk.balanceOf(lender)
        assert xctoken.balanceOf(lender) - cbal == reward - reward * prov_percent // 100

    dep1 = 5000*10**base_coin_decimals
    n_blocks = 4
    dep_reward(lender1, provider1, prov_percent_1, dep1, n_blocks)

    dep2 = 123000*10**base_coin_decimals
    n_blocks = 5
    dep_reward(lender2, provider2, prov_percent_2, dep2, n_blocks)
    
    bor1 = 4500*10**base_coin_decimals
    bor1_fee = long_desk.borrow_fee(bor1, longable1, horizons[0], {'from': borrower1})
    longable1.approve(long_desk, longable1.balanceOf(borrower1), {'from': borrower1})
    long_desk.post_longable_then_borrow(bor1, longable1, longable1.balanceOf(borrower1), horizons[0], provider1, {'from': borrower1})
    borrower1_loan = long_desk.user_loans(borrower1)
    assert borrower1_loan == bor1 + bor1_fee
    c_control.mint_all_reward_token(borrower1)
    borrow_cumul = long_desk.borrow_cumul_reward()
    cbal = xctoken.balanceOf(borrower1)
    n_blocks = 3
    chain.mine(n_blocks)
    c_control.mint_all_reward_token(borrower1)
    assert long_desk.borrow_cumul_reward() - borrow_cumul == (n_blocks+1) * borrow_reward_per_block // long_desk.total_loans()
    reward = (bor1 + bor1_fee) * (long_desk.borrow_cumul_reward() - borrow_cumul)
    assert xctoken.balanceOf(borrower1) - cbal == reward - reward * prov_percent_1 // 100


    dep_reward(lender1, provider1, prov_percent_1, 0, 4)
    
def test_multiple_rewards(lender1, lender2, provider1, provider2, erc20token_admin, long_desk, second_desk, c_control, xctoken, base_token, base_token2):
    chain = Chain()
    _, deposit_reward_per_block = c_control.get_reward_parameters(long_desk)
    _, deposit_reward_per_block2 = c_control.get_reward_parameters(second_desk)
    prov_percent_1 = c_control.provider_percentage(provider1)

    base_token.approve(long_desk, 123000*10**long_desk.base_coin_decimals(), {'from': lender2})
    long_desk.deposit(123000*10**long_desk.base_coin_decimals(), provider2, {'from': lender2})

    base_token2.transfer(lender1, 1000000e8, {'from': erc20token_admin})

    dep1 = 5000*10**long_desk.base_coin_decimals()
    dep2 = 45000*10**second_desk.base_coin_decimals()

    base_token.approve(long_desk, dep1, {'from': lender1})
    base_token2.approve(second_desk, dep2, {'from': lender1})

    long_desk.deposit(dep1, provider1, {'from': lender1})
    second_desk.deposit(dep2, provider1, {'from': lender1})

    c_control.mint_all_reward_token(lender1)

    deposit_cumul = long_desk.deposit_cumul_reward()
    deposit_cumul2 = second_desk.deposit_cumul_reward()

    cbal = xctoken.balanceOf(lender1)
    n_blocks = 4
    chain.mine(n_blocks)
    c_control.mint_all_reward_token(lender1)
    assert long_desk.deposit_cumul_reward() - deposit_cumul == (n_blocks+1) * deposit_reward_per_block // (long_desk.total_liquidity() + long_desk.total_loans())
    assert second_desk.deposit_cumul_reward() - deposit_cumul2 == (n_blocks+1) * deposit_reward_per_block2 // (second_desk.total_liquidity() + second_desk.total_loans())
    
    reward = (long_desk.deposit_cumul_reward() - deposit_cumul) * long_desk.balanceOf(lender1)
    reward2 = (second_desk.deposit_cumul_reward() - deposit_cumul2) * second_desk.balanceOf(lender1)
    rwd = reward + reward2
    assert xctoken.balanceOf(lender1) - cbal == rwd - rwd * prov_percent_1 // 100
