"""
brownie run deploy.py --network mainnet-fork
"""

import json
import os
import time

from brownie import XCToken, Control, Desk, OracleNormalizer, TestOracleSepolia
import brownie

def load_accounts():
    # admin_account owns the deployment of all our contracts. we can have different owners for different contracts if desired later
    admin_account = brownie.accounts.load('admin_account')
    # retrieve account. that's the address rewarded with the initial issue of XCRAY
    dev_account = brownie.accounts.load('dev_account')

    return admin_account, dev_account

def deploy_xctoken(admin_account, dev_account):
    return admin_account.deploy(XCToken, dev_account)

def deploy_c_control(admin_account, xctoken):
    return admin_account.deploy(Control, admin_account, xctoken)

def estimate_gas_c_control(admin_account, xctoken):
    data = Control.deploy.encode_input(admin_account, xctoken)
    return admin_account.estimate_gas(data=data)

def add_minter(admin_account, xctoken, c_control):
    xctoken.add_minter(c_control, {'from': admin_account})

def deploy_oracle(filename, admin_account, numeraire, token, decimals):
    with open(filename) as fp:
        oracle_data = json.load(fp)
    
    ret = admin_account.deploy(OracleNormalizer, oracle_data[numeraire], oracle_data[numeraire + '_oracle'], oracle_data[token], oracle_data[token + '_oracle'], decimals)
    print(token + '_oracle: ', ret)

    return ret

def deploy_test_oracle(filename, admin_account, numeraire, token, decimals):
    with open(filename) as fp:
        oracle_data = json.load(fp)

    ret = admin_account.deploy(TestOracleSepolia, oracle_data[numeraire], oracle_data[token], decimals)
    print(token + '_oracle: ', ret)

    return ret

def deploy_desk(path_to_data_file, admin_account, c_control):
    with open(path_to_data_file + '/desk_data.json') as fp:
        desk_data = json.load(fp)

    assert len(desk_data['oracles']) == len(desk_data['longables'])

    return admin_account.deploy(Desk, desk_data['base_coin'], desk_data['base_decimals'], desk_data['longables'], desk_data['longable_decimals'], desk_data['oracles'], c_control, desk_data['value_to_loan_ratio'], desk_data['flashloan_fee'], desk_data['liquidation_bonus'], desk_data['horizons'], desk_data['fees'])

def estimate_gas_desk(path_to_data_file, admin_account, c_control):
    with open(path_to_data_file + '/desk_data.json') as fp:
        desk_data = json.load(fp)

    assert len(desk_data['oracles']) == len(desk_data['longables'])
    data = Desk.deploy.encode_input(desk_data['base_coin'], desk_data['base_decimals'], desk_data['longables'], desk_data['longable_decimals'], desk_data['oracles'], c_control, desk_data['value_to_loan_ratio'], desk_data['flashloan_fee'], desk_data['liquidation_bonus'], desk_data['horizons'], desk_data['fees'])

    return admin_account.estimate_gas(data=data)

def register_desk(path_to_data_file, admin_account, c_control, desk):
    with open(path_to_data_file + '/control_data.json') as fp:
        control_data = json.load(fp)
    c_control.register_desk(desk, control_data['borrow_rate'], control_data['deposit_rate'], {'from': admin_account})
    
    assert c_control.get_reward_parameters(desk) == (control_data['borrow_rate'], control_data['deposit_rate'])

def main(path_to_data_folder):
    prod = os.getenv('CP_ENV')
    admin_account, dev_account = brownie.accounts[0], brownie.accounts[1] if prod != 'LIVE' else load_accounts()

    # deploy XCRAY contract
    xctoken = deploy_xctoken(admin_account, dev_account)
    
    # deploy Control contract and register as a minter for XCRAY
    c_control = deploy_c_control(admin_account, xctoken)
    add_minter(admin_account, xctoken, c_control)

    # deploy desks and register them with Control contract
    weth_desk = deploy_desk(path_to_data_folder + '/desk_weth', admin_account, c_control)
    print(weth_desk)
    register_desk(path_to_data_folder + '/desk_weth', admin_account, c_control, weth_desk)

    # # wbtc_desk = deploy_desk(path_to_data_folder + '/desk_wbtc', admin_account, c_control)
    # # print(wbtc_desk)
    # # register_desk(path_to_data_folder + '/desk_wbtc', admin_account, c_control, wbtc_desk)

    # # dai_desk = deploy_desk(path_to_data_folder + '/desk_dai', admin_account, c_control)
    # # print(dai_desk)
    # # register_desk(path_to_data_folder + '/desk_dai', admin_account, c_control, dai_desk)

    # # usdc_desk = deploy_desk(path_to_data_folder + '/desk_usdc', admin_account, c_control)
    # # print(usdc_desk)
    # # register_desk(path_to_data_folder + '/desk_usdc', admin_account, c_control, usdc_desk)
    
