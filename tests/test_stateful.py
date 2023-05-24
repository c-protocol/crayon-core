import pytest

import random
from brownie.test import strategy
from brownie import Desk, XCToken, Control, ERC20Token, Oracle, Borrower, Flashborrower
from utils import min_longable_amount

@pytest.fixture
def borrower_contract():
    yield Borrower

@pytest.fixture
def flashborrower_contract():
    yield Flashborrower

class StateMachine:

    st_uint = strategy("uint256", max_value=1e7)
    st_address = strategy("address")
    machine_precision = 10**-16
    one_100th_bps = 10**-6
    # # one_1000th_bps = 10**-7

    def __init__(cls, accounts, control, xctoken, base_token, horizons, fees, providers, provider_percentages, borrower_contract, flashborrower_contract):
        assert len(horizons) == len(fees)
        assert len(providers) == len(provider_percentages)

        cls.accounts = accounts
        cls.control = control
        cls.xctoken = xctoken
        cls.base_token = base_token
        cls.horizons = horizons
        cls.fees = fees
        cls.providers = providers
        cls.provider_percentages = provider_percentages
        cls.borrower_contract = borrower_contract
        cls.flashborrower_contract = flashborrower_contract
        cls.rules_called = set()

    def setup(self):
        # deploy contracts with some randomized parameters
        num_longables = random.choice(range(5)) + 1
        decimals = [18, 6, 12, 2]
        prices = range(20, 100)
        longables = []
        oracles = []
        longable_decimals = []
        longable_oracle = dict()
        for i in range(num_longables):
            d = random.choice(decimals)
            longable_decimals += [d]
            l = ERC20Token.deploy(d, {'from': self.accounts[0]})
            longables += [l]
            p = random.choice(prices) * 10**8
            o = Oracle.deploy(p, 8, {'from': self.accounts[0]})
            oracles += [o]
            longable_oracle[l] = o

        # note that we treat longables and oracles as paired throughout the tests
        self.longables = longables
        self.oracles = oracles
        self.longable_oracle = longable_oracle

        base_coin_decimals = self.base_token.decimals()
        self.desk = Desk.deploy(self.base_token, base_coin_decimals, longables, longable_decimals, oracles, self.control, 130, 9, 500, self.horizons, self.fees, {'from': self.accounts[0]})
        self.control.register_desk(self.desk, 5e26, 5e26, {'from': self.accounts[2]})
        for i in range(len(self.providers)):
            self.control.register_provider(self.provider_percentages[i], {'from': self.providers[i]})

        # reset tracking variables
        self.balances = dict()
        self.loans = dict()
        self.longable_users = dict()
        self.provider_users = dict()
        self.user_provider = dict()
        self.user_contract = dict()
        self.user_flash_contract = dict()

    def teardown_final(cls):
        print('rules called during test:')
        print(cls.rules_called)

    def rule_deposit(self, lender="st_address", amount="st_uint"):
        amount = amount * 10**self.base_token.decimals()
        p = self.get_provider(lender)

        self.seed_and_approve(lender, self.desk, self.base_token, amount)
        self.desk.deposit(amount, p, {'from': lender})
        if lender in self.balances.keys():
            self.balances[lender] += amount
        else:
            self.balances[lender] = amount
        if self.balances[lender] == 0:
            assert float(self.desk.balanceOf(lender)) <= 1
        elif abs(self.desk.balanceOf(lender) - self.balances[lender]) != 1:
            assert abs(self.desk.balanceOf(lender) - self.balances[lender]) / self.balances[lender] < self.machine_precision

        self.rules_called.add('rule_deposit')

    def rule_withdraw(self, amount="st_uint"):
        amount = amount * 10**self.base_token.decimals()
        if amount > self.desk.total_liquidity():
            amount = self.desk.total_liquidity()
        if amount == 0:
            return
            
        depositors = list(self.balances.keys())
        if len(depositors) == 0:
            return

        lender = random.choice(depositors)
        if self.balances[lender] == 0:
            return
        elif self.desk.user_reserved(lender) != 0:
            # if lender has funds on reserve then only that can be withdrawn
            amount = self.desk.user_reserved(lender)

        # if amount is greater than lender's balance then entire balance is withdrawn
        self.desk.withdraw(amount, self.user_provider[lender], {'from': lender})
        self.balances[lender] = self.balances[lender] - amount if amount <= self.balances[lender] else 0
            
        if self.balances[lender] == 0:
            assert float(self.desk.balanceOf(lender) - self.desk.user_reserved(lender)) <= 1
        elif abs(self.desk.balanceOf(lender) - self.desk.user_reserved(lender) - self.balances[lender]) != 1:
            assert abs(self.desk.balanceOf(lender) - self.desk.user_reserved(lender) - self.balances[lender]) / self.balances[lender] < self.machine_precision
        
        self.rules_called.add('rule_withdraw')

    def rule_borrow_then_post_longable(self, borrower="st_address", amount="st_uint"):
        amount = amount * 10**self.base_token.decimals()
        
        # desk info
        if amount != 0 and amount + self.desk.total_reserved() <= self.desk.total_liquidity():
            provider = self.get_provider(borrower)
            if borrower not in self.user_contract.keys():
                c = self.borrower_contract.deploy(self.desk, {'from': borrower})
                self.user_contract[borrower] = c
            c = self.user_contract[borrower]

            l, o = self.get_random_longable()
            horizon = random.choice(self.horizons)
            borrow_fee  = self.desk.borrow_fee(amount, l, horizon, {'from': borrower})
            longable_amount = min_longable_amount(amount, l.decimals(), o, self.desk.value_to_loan_ratio(), self.base_token.decimals(), borrow_fee)

            self.seed(c, l, longable_amount)

            bb = self.base_token.balanceOf(c)
            bl = l.balanceOf(c)
            a0, _, _ = self.desk.loanOf(c, l)
            c.borrow(amount, horizon, l, longable_amount, provider, {'from': borrower})
            assert bl - l.balanceOf(c) == longable_amount
            assert self.base_token.balanceOf(c) - bb == amount

            # calling this before or after c.borrow() is called
            borrow_fee = self.desk.borrow_fee(amount, l, horizon, {'from': c})
            self.update_deposits(borrow_fee)
            a1, _, _ = self.desk.loanOf(c, l)
            assert a1 == a0 + amount + borrow_fee
            self.update_user_loans(c, l, amount + borrow_fee, longable_amount)
            self.rules_called.add('rule_borrow_then_post_longable')

    def rule_post_longable_then_borrow(self, borrower="st_address", amount="st_uint"):
        amount = amount * 10**self.base_token.decimals()
        if amount != 0 and amount + self.desk.total_reserved() <= self.desk.total_liquidity():
            provider = self.get_provider(borrower)

            l, o = self.get_random_longable()
            horizon = random.choice(self.horizons)
            borrow_fee  = self.desk.borrow_fee(amount, l, horizon, {'from': borrower})
            longable_amount = min_longable_amount(amount, l.decimals(), o, self.desk.value_to_loan_ratio(), self.base_token.decimals(), borrow_fee)
            self.seed_and_approve(borrower, self.desk, l, longable_amount)

            bb = self.base_token.balanceOf(borrower)
            bl = l.balanceOf(borrower)
            self.desk.post_longable_then_borrow(amount, l, longable_amount, horizon, provider, {'from': borrower})
            assert bl - l.balanceOf(borrower) == longable_amount
            assert self.base_token.balanceOf(borrower) - bb == amount

            borrow_fee = self.desk.borrow_fee(amount, l, horizon, {'from': borrower})
            self.update_user_loans(borrower, l, amount + borrow_fee, longable_amount)
            self.update_deposits(borrow_fee)
            self.rules_called.add('rule_post_longable_then_borrow')

    def rule_post_longable(self, user="st_address", longable_amount="st_uint"):
        longable, _ = self.get_random_longable()
        longable_amount *= 10**longable.decimals()
        longable_owner = user
        self.seed_and_approve(longable_owner, self.desk, longable, longable_amount)
        bl = longable.balanceOf(longable_owner)
        a, l, e = self.desk.loanOf(longable_owner, longable)
        self.desk.post_longable(longable_amount, longable, {'from': longable_owner})
        assert bl - longable.balanceOf(longable_owner) == longable_amount
        a1, l1, e1 = self.desk.loanOf(longable_owner, longable)
        assert a == a1 and l+longable_amount==l1 and e==e1
        self.update_user_loans(longable_owner, longable, 0, longable_amount)

        self.rules_called.add('rule_post_longable')

    def rule_withdraw_longable_then_repay(self):
        contract_borrowers = list(self.user_contract.keys())
        if len(contract_borrowers) == 0:
            return

        borrower = random.choice(contract_borrowers)
        provider = self.get_provider(borrower)
        c = self.user_contract[borrower]
        longable = self.get_longable(c)
        if longable != "0x":
            a, l, _ = self.desk.loanOf(c, longable)

            assert a == self.desk.user_loans(c)

            bl = longable.balanceOf(c)
            self.seed(c, self.base_token, a)
            bb = self.base_token.balanceOf(c)
            # repay loan in full
            c.repay(longable, provider, {'from': borrower})
            
            assert bb - self.base_token.balanceOf(c) == a
            assert longable.balanceOf(c) - bl == l
            a1, l1, _ = self.desk.loanOf(c, longable)
            assert a1 == 0 and l1 == 0
            self.update_user_loans(c, longable, -a, -l)
            self.rules_called.add('rule_withdraw_longable_then_repay')

    def rule_withdraw_longable(self):
        borrower, longable, oracle = self.get_borrower_longable_oracle()
        if borrower == "0x":
            return
        a, l, _ = self.desk.loanOf(borrower, longable)
        if abs(l - self.longable_users[longable][borrower]) > 1:
            assert abs(l - self.longable_users[longable][borrower]) / self.longable_users[longable][borrower] < self.one_100th_bps
        
        # determine minimum collateral needed
        r = min_longable_amount(a, longable.decimals(), oracle, self.desk.value_to_loan_ratio(), self.base_token.decimals(), 0)
        if r < l:
            bl = longable.balanceOf(borrower)
            self.desk.withdraw_longable(l-r, longable, {'from': borrower})
            a1, l1, _ = self.desk.loanOf(borrower, longable)
            assert a == a1 and l1 == r
            assert longable.balanceOf(borrower) == bl + l - r
            self.update_user_loans(borrower, longable, 0, r-l)
            self.rules_called.add('rule_withdraw_longable')

    def rule_repay(self):
        borrower, longable, _ = self.get_borrower_longable_oracle()
        if borrower == "0x":
            return

        provider = self.get_provider(borrower)

        a, l, _ = self.desk.loanOf(borrower, longable)
        f = random.choice([1, 2, 3])
        p = a // f
        # if position is liquidatable, allow borrower to repay loan
        max_liq = self.desk.liquidatable(borrower, longable)
        if max_liq != 0:
            p = max_liq
        if self.base_token.balanceOf(borrower) < p:
            self.seed(borrower, self.base_token, p)
        assert self.base_token.balanceOf(borrower) >= p
        self.base_token.approve(self.desk, p, {'from': borrower})
        self.desk.repay(p, longable, provider, borrower, {'from': borrower})
        a1, l1, _ = self.desk.loanOf(borrower, longable)
        assert a1 == a - p and l1 == l
        self.update_user_loans(borrower, longable, -p, 0)

        self.rules_called.add('rule_repay')

    def rule_extend_loan(self):
        borrower, longable, oracle = self.get_borrower_longable_oracle()
        if borrower == "0x":
            return
        horizon = random.choice(self.horizons)
        a, l, e = self.desk.loanOf(borrower, longable)
        borrow_fee = self.desk.borrow_fee(a, longable, horizon, True, {'from': borrower})
        r = min_longable_amount(a, longable.decimals(), oracle, self.desk.value_to_loan_ratio(), self.base_token.decimals(), borrow_fee)
        if r > l:
            self.seed(borrower, longable, r - l + 10**longable.decimals())
            longable.approve(self.desk, r - l + 10**longable.decimals(), {'from': borrower})
            self.desk.post_longable(r - l + 10**longable.decimals(), longable, borrower, {'from': borrower})
            self.longable_users[longable][borrower] += r - l + 10**longable.decimals()
            
        self.desk.extend_loan(longable, horizon, {'from': borrower})
        a1, l1, e1 = self.desk.loanOf(borrower, longable)
        assert a1 == a + borrow_fee
        assert e1 == e + horizon
        assert l1 == l + r-l+10**longable.decimals() if r > l else l
        self.update_deposits(borrow_fee)
        self.update_user_loans(borrower, longable, borrow_fee, 0)

        self.rules_called.add('rule_extend_loan')

    def rule_flashloan(self, flashborrower="st_address"):
        a = 0
        l = "0x"
        for l in self.longables:
            a = self.desk.total_longable(l)
            if a != 0:
                break
        if a == 0:
            return
        
        if flashborrower not in self.user_flash_contract.keys():
            c = self.flashborrower_contract.deploy(self.desk, {'from': flashborrower})
            self.user_flash_contract[flashborrower] = c
        c = self.user_flash_contract[flashborrower]
        # does c own any l in the desk?
        _, l_amount, _ = self.desk.loanOf(c, l)
        flash_fee = 0
        # There's no fee for the flashloan if the amount is less than the collateral owned by the contract
        if a > l_amount:
            flash_fee = self.desk.flashloan_fee() * a // 10000
            if flash_fee == 0:
                return
        if flash_fee != 0:
            self.seed(c, l, flash_fee)
        c.flash_borrow(l, a, {'from': flashborrower})
        assert self.desk.total_longable(l) == a + flash_fee

        for u in self.longable_users[l].keys():
            self.longable_users[l][u] = self.longable_users[l][u] * (a + flash_fee) // a
            _, la, _ = self.desk.loanOf(u, l)
            if self.longable_users[l][u] == 0:
                assert float(la) <= 1
            elif abs(la - self.longable_users[l][u]) != 1:
                assert abs(la - self.longable_users[l][u]) / self.longable_users[l][u] < self.one_100th_bps

        self.rules_called.add('rule_flashloan')

    def rule_flashloan_base(self, flashborrower="st_address"):
        t_liq = int(self.desk.total_liquidity() / 10**self.desk.base_coin_decimals())
        if t_liq == 0:
            return
        a = random.choice(range(1, t_liq+1)) * 10**self.desk.base_coin_decimals()

        if flashborrower not in self.user_flash_contract.keys():
            c = self.flashborrower_contract.deploy(self.desk, {'from': flashborrower})
            self.user_flash_contract[flashborrower] = c
        c = self.user_flash_contract[flashborrower]
        flash_fee = 0
        # fee is 0 if the calling smart contract has a base_token balance of at least a
        if a > self.desk.balanceOf(c):
            flash_fee = self.desk.flashloan_fee() * a // 10000
            if flash_fee == 0:
                return
        if flash_fee != 0:
            self.seed(c, self.base_token, flash_fee)

        c.flash_borrow(self.base_token, a, {'from': flashborrower})
        if flash_fee != 0:
            self.update_deposits(flash_fee)

        self.rules_called.add('rule_flashloan_base')

    def rule_liquidate(self, liquidator="st_address"):
        a = 0
        for longable in self.longable_users.keys():
            for u in self.longable_users[longable].keys():
                a = self.desk.liquidatable(u, longable)
                if a != 0:
                    break
            if a != 0:
                break
        if a != 0:
            # pick random fraction of loan to pay
            f = random.choice([1, 2, 3]) # Note: in the last test we had f = 1
            amount = a // f
            self.seed_and_approve(liquidator, self.desk, self.base_token, amount)
            l0, c0, _ = self.desk.loanOf(u, longable)
            bl = longable.balanceOf(liquidator)
            self.desk.liquidate(u, longable, amount, {'from': liquidator})
            bl1 = longable.balanceOf(liquidator)
            l1, c1, _ = self.desk.loanOf(u, longable)
            assert c0 - c1 == bl1 - bl
            o = self.longable_oracle[longable]
            p = o.token_price()

            # check changes in collateral and loan outstanding are proportionately correct
            base_value = (l0-l1)/10**self.desk.base_coin_decimals() * ( 1+self.desk.liquidation_bonus()/10000)
            assert abs((bl1-bl)/10**longable.decimals() * p/10**o.decimals() - base_value) / base_value < self.one_100th_bps

            # note that longable_users tracks collateral held by borrowers so we don't care about the liquidator's holdings
            self.update_user_loans(u, longable, l1-l0, bl-bl1)
            self.rules_called.add('rule_liquidate')

    def rule_shock_oracle_price(self):
        longable = random.choice(self.longables)
        p = self.longable_oracle[longable].token_price()
        f = random.choice([2, 3, 4])
        self.longable_oracle[longable].set_token_price(p - p // f)

        self.rules_called.add('rule_shock_oracle_price')

    def invariant_deposits(self):
        # called after every rule
        total_deposits = 0
        for k in self.balances.keys():
            total_deposits += self.balances[k]
        # funds "reserved" for withdrawal appear as withdrawn in state machine. we correct here
        total_deposits += self.desk.total_reserved()
        if total_deposits == 0:
            assert abs(self.desk.total_liquidity() + self.desk.total_loans()) <= 1
        elif abs(total_deposits - (self.desk.total_liquidity() + self.desk.total_loans())) != 1:
            assert abs(total_deposits - (self.desk.total_liquidity() + self.desk.total_loans())) / total_deposits < self.one_100th_bps

    def invariant_loans(self):
        for u in self.loans.keys():
            if self.loans[u] == 0:
                assert self.desk.user_loans(u) <= 1
            elif abs(self.loans[u] - self.desk.user_loans(u)) != 1:
                assert abs(self.loans[u] - self.desk.user_loans(u)) / self.loans[u] < self.one_100th_bps

            sum = 0
            for longable in self.longables:
                l, _, _ = self.desk.loanOf(u, longable)
                sum += l
            assert sum == self.desk.user_loans(u)

    def get_provider(self, user):
        provider = random.choice(self.providers)
        # do not let users change providers in these tests to make it easier to track provider rewards
        if user not in self.user_provider.keys():
            self.user_provider[user] = provider
            if provider in self.provider_users.keys():
                self.provider_users[provider].add(user)
            else:
                self.provider_users[provider] = {user}
        else:
            provider = self.user_provider[user]
        
        return provider

    def get_random_longable(self):
            num_longables = len(self.longables)
            i = random.choice(range(num_longables))
            longable = self.longables[i]
            oracle = self.oracles[i]

            return longable, oracle

    def get_borrower_longable_oracle(self):
        borrowers = list(self.loans.keys())
        if len(borrowers) == 0:
            return "0x", "0x", "0x"

        borrower = random.choice(borrowers)
        for i in range(len(self.longables)):
            a, _, _ = self.desk.loanOf(borrower, self.longables[i])
            if a != 0:
                # just return the first one found
                return borrower, self.longables[i], self.oracles[i]
        return "0x", "0x", "0x"

    def get_longable(self, user):
        for longable in self.longables:
            a, _, _ = self.desk.loanOf(user, longable)
            if a != 0:
                # just return the first one found
                return longable
        return "0x"

    def seed_and_approve(self, sender, receiver, token, amount):
        b = token.balanceOf(sender)
        if b < amount:
            admin = token.admin()
            assert token.balanceOf(admin) >= amount-b
            token.transfer(sender, amount-b, {'from': admin})
        token.approve(receiver, amount, {'from': sender})

    def seed(self, receiver, token, amount):
        b = token.balanceOf(receiver)
        if b < amount:
            admin = token.admin()
            assert token.balanceOf(admin) >= amount-b
            token.transfer(receiver, amount-b, {'from': admin})

    def update_deposits(self, borrow_fee):
        total_deposits = 0
        for k in self.balances.keys():
            total_deposits += self.balances[k]

        for k in self.balances.keys():
            if self.balances[k] == 0:
                assert float(self.desk.balanceOf(k)-self.desk.user_reserved(k)) <= 1
            else:
                # this is OK. reserved funds are not compensated
                self.balances[k] = self.balances[k] * (total_deposits + borrow_fee) // total_deposits
                if abs(self.balances[k] - self.desk.balanceOf(k) + self.desk.user_reserved(k)) != 1:
                    assert abs(self.balances[k] - self.desk.balanceOf(k) + self.desk.user_reserved(k)) / self.balances[k] < self.machine_precision

    def update_user_loans(self, user, longable, amount, longable_amount):
        # compare against desk.user_loans
        if user in self.loans.keys():
            self.loans[user] += amount
        else:
            self.loans[user] = amount
        assert self.loans[user] >= 0

        if self.loans[user] == 0:
            assert float(self.desk.user_loans(user)) <= 1
        elif abs(self.desk.user_loans(user) - self.loans[user]) != 1:
            assert abs(self.desk.user_loans(user) - self.loans[user]) / self.loans[user] < self.machine_precision

        if longable not in self.longable_users.keys():
            self.longable_users[longable] = dict()
            self.longable_users[longable][user] = longable_amount
        else:
            if user not in self.longable_users[longable].keys():
                self.longable_users[longable][user] = longable_amount
            else:
                self.longable_users[longable][user] += longable_amount
        _, l, _ = self.desk.loanOf(user, longable)
        if self.longable_users[longable][user] == 0:
            assert float(l) <= 1
        elif abs(l - self.longable_users[longable][user]) != 1:
            assert abs(l - self.longable_users[longable][user]) / self.longable_users[longable][user] < self.one_100th_bps

def test_stateful(accounts, base_token, borrower_contract, flashborrower_contract, state_machine):   
    xctoken_contract = XCToken.deploy(accounts[1], {'from': accounts[0]})
    control_contract = Control.deploy(accounts[2], xctoken_contract, {'from': accounts[0]})
    xctoken_contract.add_minter(control_contract, {'from': accounts[0]})

    # approx. 1, 3, 7 days
    horizons = [5760, 5760 * 3, 5760 * 7]
    fees = [9, 18, 45]
    providers = [accounts.add(), accounts.add(), accounts.add(), accounts.add(), accounts.add()]
    provider_percentages = [2, 5, 10, 1, 0]

    state_machine(StateMachine, accounts, control_contract, xctoken_contract, base_token, horizons, fees, providers, provider_percentages, borrower_contract, flashborrower_contract)
