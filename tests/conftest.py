import pytest

from brownie import Desk, XCToken, Control, ERC20Token, Oracle, Borrower, Flashborrower

@pytest.fixture
def erc20token_admin(accounts):
    yield accounts[6]

@pytest.fixture
def liquidator(accounts):
    yield accounts[7]

@pytest.fixture
def dev_account(accounts):
    yield accounts[8]

@pytest.fixture
def create_token(erc20token_admin):
    def create_token(decimals=18):
        return erc20token_admin.deploy(ERC20Token, decimals)

    yield create_token

@pytest.fixture
def create_oracle(erc20token_admin):
    def create_oracle(price=100e8, decimals=8):
        return erc20token_admin.deploy(Oracle, price, decimals)

    yield create_oracle

@pytest.fixture
def base_token(create_token):
    yield create_token(decimals=18)

@pytest.fixture
def longable1(create_token):
    yield create_token(decimals=18)

@pytest.fixture
def oracle1(create_oracle):
    yield create_oracle(price=3e8)

@pytest.fixture
def longable2(create_token):
    yield create_token(decimals=12)
    
@pytest.fixture
def oracle2(create_oracle):
    yield create_oracle(price=90e8)

@pytest.fixture
def longable3(create_token):
    yield create_token(decimals=6)
    
@pytest.fixture
def oracle3(create_oracle):
    yield create_oracle(price=103e8)

@pytest.fixture
def longable4(create_token):
    yield create_token(decimals=2)
    
@pytest.fixture
def oracle4(create_oracle):
    yield create_oracle(price=2e8)

@pytest.fixture
def longables(longable1, longable2, longable3, longable4):
    yield [longable1, longable2, longable3, longable4]

@pytest.fixture
def oracles(oracle1, oracle2, oracle3, oracle4):
    yield [oracle1, oracle2, oracle3, oracle4]

@pytest.fixture
def xctoken_admin(accounts):
    yield accounts.add()

@pytest.fixture
def xctoken_contract(xctoken_admin, dev_account):
    c = xctoken_admin.deploy(XCToken, dev_account)
    yield c

@pytest.fixture
def control_admin(accounts):
    yield accounts.add()

@pytest.fixture
def control_contract(control_admin, xctoken_contract):
    yield control_admin.deploy(Control, control_admin, xctoken_contract)

@pytest.fixture
def horizons():
    yield [5760, 5760 * 3, 5760 * 7]

@pytest.fixture
def borrow_fees():
    yield [9, 18, 45]

@pytest.fixture
def long_desk(base_token, control_contract, longables, oracles, horizons, borrow_fees, accounts):
    longable_decimals = [18, 12, 6, 2]
    yield accounts.add().deploy(
        Desk,
        base_token,
        18,
        longables,
        longable_decimals,
        oracles,
        control_contract,
        130,
        9,
        500,
        horizons,
        borrow_fees
    )

@pytest.fixture
def provider1(accounts):
    yield accounts.add()

@pytest.fixture
def provider2(accounts):
    yield accounts.add()

@pytest.fixture
def lender1(base_token, erc20token_admin, accounts):
    base_token.transfer(accounts[1], 1000000e18, {'from': erc20token_admin})
    yield accounts[1]

@pytest.fixture
def lender2(base_token, erc20token_admin, accounts):
    base_token.transfer(accounts[2], 1000000e18, {'from': erc20token_admin})
    yield accounts[2]

@pytest.fixture
def lender3(base_token, erc20token_admin, accounts):
    base_token.transfer(accounts[3], 1000000e18, {'from': erc20token_admin})
    yield accounts[3]

@pytest.fixture
def borrower1(base_token, longable1, erc20token_admin, accounts):
    # needs to have some base coin to pay the fee for loan
    base_token.transfer(accounts[4], 1000e18, {'from': erc20token_admin})
    longable1.transfer(accounts[4], 1000000e18, {'from': erc20token_admin})
    yield accounts[4]

@pytest.fixture
def borrower2(base_token, longable2, erc20token_admin, accounts):
    base_token.transfer(accounts[5], 1000e18, {'from': erc20token_admin})
    longable2.transfer(accounts[5], 1000000e12, {'from': erc20token_admin})
    yield accounts[5]

@pytest.fixture
def flashborrower(accounts):
    yield accounts[9]

@pytest.fixture
def contract_borrower1(borrower1, long_desk):
    yield borrower1.deploy(Borrower, long_desk)

@pytest.fixture
def contract_borrower2(borrower2, long_desk):
    yield borrower2.deploy(Borrower, long_desk)

@pytest.fixture
def contract_flashborrower(flashborrower, long_desk):
    yield flashborrower.deploy(Flashborrower, long_desk)

@pytest.fixture(autouse=True)
def c_control(control_contract, long_desk, control_admin, provider1, provider2):
    control_contract.register_desk(long_desk, 5e26, 5e26, {'from': control_admin})
    control_contract.register_provider(2, {'from': provider1})
    control_contract.register_provider(5, {'from': provider2})
    yield control_contract

@pytest.fixture(autouse=True)
def xctoken(xctoken_contract, c_control, xctoken_admin):
    xctoken_contract.add_minter(c_control, {'from': xctoken_admin})
    yield xctoken_contract
