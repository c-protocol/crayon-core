import random
from brownie import Contract

zero_address = '0x'+'0' * 40

# scale the price the way it will be internally in the desk
def scale_price(p, base_decimals, oracle_decimals):
    if base_decimals >= oracle_decimals:
        return p * 10 ** (base_decimals - oracle_decimals)
    else:
        return p * 10 ** base_decimals // 10 ** oracle_decimals

def test_deposit(base_token, desk, depositor):
    # deposit
    base_decimals = base_token.decimals()
    bal0 = base_token.balanceOf(depositor)
    bal = bal0 // 10 ** base_decimals
    sum = 0
    for i in range(50):
        if bal - sum <= 1:
            break
        dep = random.choice(range(1, bal - sum))
        sum += dep
        base_token.approve(desk, dep * 10 ** base_decimals, {'from': depositor})
        desk.deposit(dep * 10 ** base_decimals, zero_address, {'from': depositor})

    bal = bal * 10 ** base_decimals
    sum = sum * 10 ** base_decimals
    assert sum == desk.balanceOf(depositor)
    assert base_token.balanceOf(depositor) == bal0 - sum

    # withdraw
    desk.withdraw(sum, zero_address, {'from': depositor})
    assert 0 == desk.balanceOf(depositor)
    assert bal0 == base_token.balanceOf(depositor)

def test_borrow(base_token, longables, oracles, desk, borrower, depositor, deployment_data):
    # fund the desk
    bal = base_token.balanceOf(depositor) // 2
    base_token.approve(desk, bal, {'from': depositor})
    desk.deposit(bal, zero_address, {'from': depositor})

    # borrow
    num_longs = len(longables)
    loan0 = desk.total_liquidity() // num_longs
    v2l = deployment_data['value_to_loan_ratio']
    horizon = deployment_data['horizons'][0]
    cumul_loan = 0
    for i in range(num_longs):
        loan = loan0
        longable = longables[i]
        oracle = oracles[i]
        # calculate collateral for loan
        bal = longable.balanceOf(borrower)
        (_, p, _, _, _) = oracles[i].latestRoundData()
        p_scaled = scale_price(p, base_token.decimals(), oracle.decimals())

        # adjust the loan to make sure we have enough collateral for it
        while True:
            fee = desk.borrow_fee(loan, longable, horizon, {'from': borrower})
            # v2l has to be divided by 100 hence the enigmatic -2
            collateral = v2l * (loan + fee) * 10**(longable.decimals() - 2) // p_scaled + 10 ** longable.decimals()
            if collateral <= bal:
                break
            loan = loan // 2

        # make sure there's enough collateral for the loan
        assert collateral <= bal

        # borrow
        longable.approve(desk, collateral, {'from': borrower})
        desk.post_longable_then_borrow(loan, longable, collateral, horizon, zero_address, {'from': borrower})
        cumul_loan += loan

        assert base_token.balanceOf(borrower) == cumul_loan
        assert longable.balanceOf(borrower) == bal - collateral
        l, c, _ = desk.loanOf(borrower, longable)
        assert l == loan + fee
        assert c == collateral

    # now repay. borrower only owns what was borrowed. transfer so borrower can pay accumulated fees
    base_token.transfer(borrower, base_token.balanceOf(depositor), {'from': depositor})
    base_token.approve(desk, base_token.balanceOf(borrower), {'from': borrower})
    for longable in longables:
        l, c, _ = desk.loanOf(borrower, longable)
        base_bal = base_token.balanceOf(borrower)
        long_bal = longable.balanceOf(borrower)
        # approve desk and repay loan
        longable.approve(desk, l, {'from': borrower})
        desk.repay(l, longable, zero_address, borrower, {'from': borrower})
        # withdraw collateral
        desk.withdraw_longable(c, longable, {'from': borrower})
        # check numbers
        assert base_token.balanceOf(borrower) == base_bal - l
        assert longable.balanceOf(borrower) == long_bal + c


def test_oracles(oracles, deployment_data):
    if deployment_data['base_token_oracle'] == '':
        print('skipping test_oracles because no oracles are normalized')
        return

    oracles_data = deployment_data['oracles']
    base_token_oracle = Contract.from_explorer(deployment_data['base_token_oracle'])
    (_, pb, _, _, _) = base_token_oracle.latestRoundData() 
    for i in range(len(oracles)):
        odata = oracles_data[i]
        if not odata['is_normalized']:
            continue
        normed_oracle = oracles[i]
        oracle = Contract.from_explorer(odata['address'])
        (_, pl, _, _, _) = oracle.latestRoundData()
        (_, pn, _, _, _) = normed_oracle.latestRoundData()

        assert pn == pl * 10**(normed_oracle.decimals()+base_token_oracle.decimals()-oracle.decimals()) // pb
