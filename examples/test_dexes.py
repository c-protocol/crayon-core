import json
import os

from brownie import PairsTraderCurveS, PairsTraderUniswapS, Contract, Desk, Control, XCToken
from brownie._config import CONFIG

"""
    pairs_trader wants to execute 2 trades one on Uniswap and one on Curve. pairs_trader decides to deploy 2 separate smart contracts (makes what follows easier to read).

    pairs_trader's smart contract owns p WBTC. Some of that has to be reserved to pay the fee for the loan and the rest will be swapped alongside the loan for the coin that pairs_trader thinks will outperform WBTC. The amount to repay has to include the fee. The constraint  (inequality) to solve then is (x is the loan amount):
    
    (p - fee * x + x) / (x + fee * x) >= v2l / 100

    Almost there. The swap will cause some slippage. The dollar value of the coin we swap WBTC for, therefore, is going to be less than the dollar value of WBTC we put in. Let s be the slippage in bps, then the final constraint on x is:

    (1 - s / 10000) * (p - fee * x + x) / (x + fee * x) >= v2l / 100
    
    Note f is in bps so fee = f / 10000. Also, we add a little safety buffer to remain above the liquidation threshold so we use (v2l+1). For v2l=130, this gives a leveraged position of more than 4x
"""

zero_address = '0x'+'0' * 40

def pairs_curve( _cap, _crv_trader,_pairs_trader, _v2l, _horizon, _fee):
    # The pair we'll trade on Curve is WBTC <-> WETH. we hold the view that over _horizon blocks WETH will outperform WBTC
    tricrypto_pool = '0x960ea3e3C7FB317332d990873d354E18d7645590'
    wbtc_ind = 1
    weth_ind = 2
    weth = '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1'
    weth_contract = Contract.from_explorer(weth)
    weth_oracle = Contract.from_explorer('0x7A8d454d553Fa464FE9FA63180555e8582565e1c') # this oracle gives the price ratio of WETH to WBTC. So the price of WETH in WBTC units

    # allow 50 bps slippage on Curve
    crv_slippage = 60
    # v2l+1 instead of v2l as a little buffer above the liquidation threshold
    loan_amount = _cap // ((_v2l+1) / 100 * (1 + _fee / 10000) / (1 - crv_slippage / 10000) - (1 - _fee / 10000))
    cap_eff = _cap - loan_amount * _fee // 10000

    # decimals for the different contracts including the oracle
    wbtc_dec = 8
    weth_dec = 18
    orc_dec = 8
    (_, longable_price, _, _, _) = weth_oracle.latestRoundData()
    longable_amount = (1 - crv_slippage / 10000) * (cap_eff + loan_amount) * 10**(orc_dec + weth_dec - wbtc_dec) // longable_price

    weth_bal0 = weth_contract.balanceOf(_crv_trader)
    # create leveraged (almost) dollar-matched pairs position
    _crv_trader.trade(tricrypto_pool, loan_amount, cap_eff, _horizon, wbtc_ind, weth_ind, weth, longable_amount, {'from': _pairs_trader})
    # in the previous call, we committed to deposit longable_amount of WETH in the Crayon Desk. However the swap on Curve could have given us more than longable_amount
    weth_excess = weth_contract.balanceOf(_crv_trader) - weth_bal0
    
    # finally unwind position. note that we want to swap back all WETH we received at trade inception -- not just the WETH we posted as collateral in Crayon Desk
    _crv_trader.unwind(tricrypto_pool, weth, weth_excess, weth_ind, wbtc_ind, {'from': _pairs_trader})
    

def pairs_uniswap(_cap, _uni_trader, _pairs_trader, _v2l, _horizon, _fee):
    # The pair we'll trade on Uniswap is WBTC <-> ARB. we hold the view that over _horizon blocks, ARB will outperform WBTC
    arb = '0x912CE59144191C1204E64559FE8253a0e49E6548'
    arb_contract = Contract.from_explorer(arb)
    arb_oracle = Contract.from_explorer('0xCf5C0726D2F88092F1dB477c9b8D70c674c94C0A') # price ratio to WBTC
    # weth is used as intermediate token in a two-hop swap wbtc <-> weth <-> arb
    weth = '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1'

    # allow 30 bps of slippage on uniswap
    uni_slippage = 30
    # v2l+1 instead of v2l as a little buffer above the liquidation threshold
    loan_amount = _cap // ((_v2l+1) / 100 * (1 + _fee / 10000) / (1 - uni_slippage / 10000) - (1 - _fee / 10000))
    cap_eff = _cap - loan_amount * _fee / 10000

    # decimals for the different contracts including the oracle
    wbtc_dec = 8
    arb_dec = 18
    orc_dec = 8
    (_, longable_price, _, _, _) = arb_oracle.latestRoundData()    
    longable_amount = (1 - uni_slippage / 10000) * (cap_eff + loan_amount) * 10**(orc_dec + arb_dec - wbtc_dec) // longable_price
    
    arb_bal0 = arb_contract.balanceOf(_uni_trader)
    # create position
    _uni_trader.trade(loan_amount, cap_eff, _horizon, arb, longable_amount, weth, {'from': _pairs_trader})
    # also test this
    # # _uni_trader.unwind(arb, arb_received, zero_address)
    # we deposited longable_amount of arb in the desk. however, in the swap that was executed in the _uni_trader smart contract we could have received more arb. this is how much
    arb_excess = arb_contract.balanceOf(_uni_trader) - arb_bal0
    
    # unwind position. note that when swapping back to wbtc we want to swap all the arb we received earlier, not just what we ended up depositing as collateral
    _uni_trader.unwind(arb, arb_excess, weth, {'from': _pairs_trader})
    
# this is useful and only needed when debugging
def deploy_desk(accounts):
    # random account
    admin = accounts.add()

    # deploy XCRAY token contract
    xctoken = admin.deploy(XCToken, accounts.add())

    # deploy Control and add it as minter to XCRAY token
    c_control = admin.deploy(Control, admin, xctoken)
    xctoken.add_minter(c_control, {'from': admin})
    
    # get data for WBTC desk, deploy and register it with c_control
    with open('deployments/arbitrum/desk_wbtc/desk_data.json') as fp:
        desk_data = json.load(fp)

    assert len(desk_data['oracles']) == len(desk_data['longables'])

    wbtc_desk = admin.deploy(Desk, desk_data['base_coin'], desk_data['base_decimals'], desk_data['longables'], desk_data['longable_decimals'], desk_data['oracles'], c_control, desk_data['value_to_loan_ratio'], desk_data['flashloan_fee'], desk_data['liquidation_bonus'], desk_data['horizons'], desk_data['fees'])

    c_control.register_desk(wbtc_desk, 5e26, 5e26, {'from': admin})

    return wbtc_desk


def test_pairs_arbitrum(accounts):
    # run this test only if we're on arbitrum-fork and we have the wbtc desk deployed
    if CONFIG.active_network['id'] != 'arbitrum-fork':
        print('skipping test_pairs_arbitrum() because we are not on arbitrum-fork...')

        # and just leave
        return
    
    # base_token is WBTC for this test
    base_token = Contract.from_explorer('0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f')
    # here's a WBTC holder
    depositor = accounts.at('0x489ee077994b6658eafa855c308275ead8097c4a', force=True)

    # use deployed desk or deploy fresh version?
    if os.getenv('DEP_WBTC') == 'true':
        print('environment variable DEP_WBTC set to true. deploying test copy of WBTC desk')
        desk = deploy_desk(accounts)
    else:
        # use arbitrum-main WBTC desk
        desk = Contract.from_explorer('0x3454923795c5EdD5b3967e3B63140c343e6BB3dF')

    # deposit in the desk
    dep = 100 * 10 ** base_token.decimals()
    base_token.approve(desk, dep, {'from': depositor} )
    desk.deposit(dep, {'from': depositor})

    # create a random address for the trader in the test
    pairs_trader = accounts.add()

    # pairs_trader deploys two smart contracts for trading on each of Uniswap and Curve. Note that these can be combined in one. we're just trying to keep things clearer here
    uni_trader = pairs_trader.deploy(PairsTraderUniswapS, desk)
    crv_trader = pairs_trader.deploy(PairsTraderCurveS, desk)

    # the leveraged, dollar-matched pairs trades have to be done through the just deployed smart contracts. So let's transfer some WBTC directly to the those contracts. depositor owns all the WBTC in our test. Note that the initial amount we're transferring + the borrowed amount will be swapped for a coin to set up the dollar-matched pairs trade position
    p = 1 * 10**base_token.decimals()
    base_token.transfer(uni_trader, p, {'from': depositor})
    base_token.transfer(crv_trader, p, {'from': depositor})

    # pairs_trader wants to hold the position over 3 days which corresponds to its view of the market move. pairs_trader knows that 3 days is the second horizon (so, index = 1) on the WBTC desk
    index_of_desired_horizon = 1
    h, f = desk.get_horizon_and_fee(index_of_desired_horizon)
    # sanity check: assert this is the right horizon (expressed in blocks)
    assert h == 17280

    # Note v2l is a percentage. 
    v2l = desk.value_to_loan_ratio()

    # execute on uniswap
    pairs_uniswap(p, uni_trader, pairs_trader, v2l, h, f)

    # execute on curve
    pairs_curve(p, crv_trader, pairs_trader, v2l, h, f)
    
