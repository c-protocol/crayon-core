import * as config from "./config.js";

export async function desk_base(desk) {
    let base_token = await desk.base_coin();
    return base_token;
}

export async function desk_liquidity(desk) {
    let tot_liq = await desk.total_liquidity();
    return tot_liq;
}

export async function desk_loans(desk) {
    let tot_loans = await desk.total_loans();
    return tot_loans;
}

export async function desk_reserved(desk) {
    let tot_res = await desk.total_reserved();
    return tot_res;
}

export async function base_deposit(desk, base_contract, amount) {
    await (await base_contract.approve(desk, amount)).wait();
    let tx = await desk.deposit(amount);
    await tx.wait();
}

export async function base_withdraw(desk, amount) {
    let tx = await desk.withdraw(amount, config.network_provider_address);
    await tx.wait();
}

export async function loan_get(desk, amount, collateral_contract, collateral, collateral_amount, horizon) {
    await (await collateral_contract.approve(desk, collateral_amount)).wait();
    let tx = await desk.post_longable_then_borrow(amount, collateral, collateral_amount, horizon, config.network_provider_address);
    await tx.wait();
}

export async function loan_repay(desk, base_contract, amount, collateral, loan_owner) {
    await (await base_contract.approve(desk, amount)).wait();
    let tx = await desk.repay(amount, collateral, config.network_provider_address, loan_owner);
    await tx.wait();
}

export async function loan_extend(desk, collateral, horizon) {
    let tx = await desk.extend_loan(collateral, horizon);
    await tx.wait();
}

// which collateral does this desk accept?
export async function collateral_accepted(desk_name) {
    // return 2-element array: collateral_addresses, collateral_names
    let collateral_names = config.network_desk_collateral.get(desk_name);
    let collateral_addresses = [];
    for (let i = 0; i < collateral_names.length; i++) {
        collateral_addresses.push(config.network_addresses.get(collateral_names[i]));
    }

    return [collateral_addresses, collateral_names];
}

export async function collateral_add(desk, collateral_contract, collateral, collateral_amount, owner) {
    await (await collateral_contract.approve(desk, collateral_amount)).wait();
    let tx = await desk.post_longable(collateral_amount, collateral, owner);
    await tx.wait();
}

export async function collateral_rm(desk, amount, collateral) {
    let tx = await desk.withdraw_longable(amount, collateral);
    await tx.wait();
}

export async function user_balance(desk, user) {
    let bal = await desk.balanceOf(user);
    return bal;
}

export async function user_loans(desk_name, desk, user) {
    let collateral_names = config.network_desk_collateral.get(desk_name);
    let ret = [];
    for (let i = 0; i < collateral_names.length; i++) {
        let collateral_address = config.network_addresses.get(collateral_names[i]);
        // loanOf() returns (loan_amount, collateral_amount, expiration)
        let a = await desk.loanOf(user, collateral_address);
        let expiration = a[2];

        // expiration of non-existing loans will be max uint256 so we change it here
        if (BigInt(expiration.toString() > BigInt('10000000000000000000000000000000000000000000000'))) {
            expiration = 0;
        }

        ret.push([collateral_names[i], new Map([["loan_amount", a[0]], ["collateral_amount", a[1]], ["expiration", expiration]])])
    }

    return new Map(ret);
}

export async function horizon_and_fee(desk) {
    let num_horizons = await desk.num_horizons();
    let horizons = [];
    let fees = [];
    for (let i = 0; i< num_horizons; i++) {
        let a = await desk.get_horizon_and_fee(i);
        horizons.push(a[0]);
        fees.push(a[1]);
    }

    return [horizons, fees];
}

export async function earned_balance(control, user) {
    let earned_tokens = await control.reward_balanceOf(user, config.network_desks);

    return earned_tokens;
}

export async function earned_mint(control, user) {
    let tx = await control.mint_all_reward_token(user);
    await tx.wait();
}
