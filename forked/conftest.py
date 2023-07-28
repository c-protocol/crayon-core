import pytest
import json

from brownie import Contract, Desk, OracleNormalizer
from brownie._config import CONFIG

@pytest.fixture(scope='module')
def deployment_data():
    assert 'fork' in CONFIG.active_network['id']

    with open('./forked/deployment_data.json') as fp:
        test_dict = json.load(fp)

    return test_dict

@pytest.fixture(scope='module')
def admin(accounts):
    yield accounts[0]

@pytest.fixture(scope='module')
def depositor(accounts):
    yield accounts[1]

@pytest.fixture(scope='module')
def borrower(accounts):
    yield accounts[2]

@pytest.fixture(scope='module')
def c_control(deployment_data):
    # we assume that Control has been deployed already. we're just testing the new desk in this module
    yield Contract.from_explorer(deployment_data['control'])

def token_contract(recv, token, accounts):
    contract = Contract.from_explorer(token['address'])

    holder = accounts.at(token['holder'], force=True)
    contract.transfer(recv, contract.balanceOf(holder), {'from': holder})

    return contract 

@pytest.fixture(scope='module')
def base_token(depositor, deployment_data, accounts):
    yield token_contract(depositor, deployment_data['base_token'], accounts)

@pytest.fixture(scope='module')
def base_token_oracle(deployment_data):
    oracle_address = deployment_data['base_token_oracle']
    # if all longable oracles already use base_token as numeraire then oracle_address is ''
    if oracle_address != '':
        yield Contract.from_explorer(oracle_address)

@pytest.fixture(scope='module')
def longables(borrower, deployment_data, accounts):
    longs = deployment_data['longables']
    ret = []
    for long in longs:
        ret.append(token_contract(borrower, long, accounts))

    yield ret

@pytest.fixture(scope='module')
def oracles(deployment_data, accounts):
    orcs = deployment_data['oracles']
    longs = deployment_data['longables']
    ret = []
    for i in range(len(orcs)):
        is_normalized = orcs[i]['is_normalized']
        if is_normalized:
            c = accounts[0].deploy(OracleNormalizer, deployment_data['base_token']['address'], deployment_data['base_token_oracle'], longs[i]['address'], orcs[i]['address'], orcs[i]['normalized_decimals'])
        else:
            c = Contract.from_explorer(orcs[i]['address'])

        ret.append(c)
    
    yield ret

@pytest.fixture(scope='module')
def desk(c_control, base_token, longables, oracles, deployment_data, accounts):
    longable_decimals = []
    for longable in longables:
        longable_decimals.append(longable.decimals())

    desk = accounts[0].deploy(
        Desk,
        base_token,
        base_token.decimals(),
        longables,
        longable_decimals,
        oracles,
        c_control,
        deployment_data['value_to_loan_ratio'],
        deployment_data['flashloan_fee'],
        deployment_data['liquidation_bonus'],
        deployment_data['horizons'],
        deployment_data['fees'])
    
    admin = accounts.at(c_control.admin(), force=True)
    c_control.register_desk(desk, deployment_data['dep_reward'], deployment_data['bor_reward'], {'from': admin})

    yield desk
