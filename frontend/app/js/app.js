import { network_addresses, desk_abi, control_abi, erc20_abi, token_decimals,  networks, updateGlobals, network_desk_collateral} from "./config.js";
import * as protocol from "./protocol.js";

// fill the network menu
(function() {
    let menu = '<option value="blank"></option>';
    for (let n of networks) {
        menu += `<option value=${n}>${n}</option>`;
    }

    document.getElementById("network").innerHTML = menu;
})();

export function fill_desk_menu() {
    updateGlobals();

    let menu = '<option value="blank"></option>';
    for (let d of network_desk_collateral.keys()) {
        let c = d.replace('Desk', '');
        menu += `<option value=${d}>${c}</option>`;
    }

    document.getElementById("desk").innerHTML = menu;
};

export async function update_parameters() {
    let desk_name = document.getElementById("desk").value;
    let deskAction = document.getElementById("deskAction").value;

    if (desk_name == "blank" || deskAction == "blank") {
        reset_parameters();
        return;
    }

    let base_coin = get_selected('desk');

    switch (deskAction) {
        case "deposit":
            document.getElementById("callingSequence").innerHTML = deposit_parameters(base_coin);
            break;
        case "withdraw":
            document.getElementById("callingSequence").innerHTML = withdraw_parameters(base_coin);
            break;
        case "borrow":
            document.getElementById("callingSequence").innerHTML = await borrow_parameters(desk_name, base_coin);
            break;
        case "repay":
            document.getElementById("callingSequence").innerHTML = await repay_parameters(desk_name, base_coin);
            break;
        case "extend":
            document.getElementById("callingSequence").innerHTML = await extend_parameters(desk_name);
            break;
        case "addCollateral":
            document.getElementById("callingSequence").innerHTML = await addCollateral_parameters(desk_name);
            break;
        case "withdrawCollateral":
            document.getElementById("callingSequence").innerHTML = await withdrawCollateral_parameters(desk_name);
            break;
        default:
            console.error("unkown method");
    }
}

export function reset_parameters() {
    document.getElementById("callingSequence").innerHTML = '';
}

export async function fill_view() {
    let desk_name = document.getElementById("desk").value;

    if (desk_name == "blank") {
        reset_view();
        return;
    }

    let base_name = desk_name.replace('Desk', '');

    let contract_address = network_addresses.get(desk_name);
    let crayonDesk = newContractV(contract_address, desk_abi);
    let crayonControl = newContractV(network_addresses.get("control"), control_abi);

    let total_liq = await protocol.desk_liquidity(crayonDesk);
    let total_loans = await protocol.desk_loans(crayonDesk);
    let total_reserved = await protocol.desk_reserved(crayonDesk);

    let user = web3.account;
    let bal = await protocol.user_balance(crayonDesk, user);
    let earned = await protocol.earned_balance(crayonControl, user);

    document.getElementById("base").innerHTML = get_selected('desk');
    document.getElementById("totalLiq").innerHTML = int_to_dec(total_liq, base_name);
    document.getElementById("totalLoans").innerHTML = int_to_dec(total_loans, base_name);
    document.getElementById("totalRes").innerHTML = int_to_dec(total_reserved, base_name);

    document.getElementById("userDeposit").innerHTML = int_to_dec(bal, base_name);
    document.getElementById("earnedXcray").innerHTML = int_to_dec(earned, 'xcray');

    // fill user loans table
    let ulTBody = document.getElementById("loansBody");
    ulTBody.innerHTML = '';
    let user_loans = await protocol.user_loans(desk_name, crayonDesk, user);
    for (let c of user_loans.keys()) {
        let m = user_loans.get(c);
        let newRow = ulTBody.insertRow(-1);
        let lCell = newRow.insertCell(-1);
        lCell.innerHTML = int_to_dec(m.get("loan_amount"), base_name);
        let cCell = newRow.insertCell(-1);
        cCell.innerHTML = c;
        let aCell = newRow.insertCell(-1);
        aCell.innerHTML = int_to_dec(m.get("collateral_amount"), c);
        let eCell = newRow.insertCell(-1);
        eCell.innerHTML = BigInt(m.get("expiration").toString());
    }

    // fill horizon/fee table
    let hfTbody = document.getElementById("horizonsBody");
    hfTbody.innerHTML = '';
    let [horizons, fees] = await protocol.horizon_and_fee(crayonDesk);
    for (let i = 0; i < horizons.length; i++) {
        let newRow = hfTbody.insertRow(-1);
        let hCell = newRow.insertCell(-1);
        hCell.innerHTML = BigInt(horizons[i].toString()) / BigInt(5760);
        let fCell = newRow.insertCell(-1);
        fCell.innerHTML = fees[i];
    }

}

function reset_view() {

    document.getElementById("totalLiq").innerHTML = '';
    document.getElementById("totalLoans").innerHTML = '';
    document.getElementById("totalRes").innerHTML = '';

    document.getElementById("userDeposit").innerHTML = '';
    document.getElementById("earnedXcray").innerHTML = '';

    document.getElementById("loansBody").innerHTML = '';
    document.getElementById("horizonsBody").innerHTML = '';
}

export async function mint_action() {
    let crayonControl = newContractS(network_addresses.get("control"), control_abi);
    await protocol.earned_mint(crayonControl, web3.account);
}

export async function form_action() {
    let desk_name = document.getElementById("desk").value;
    let deskAction = document.getElementById("deskAction").value;

    if (desk_name == "blank" || deskAction == "blank") {
        return;
    }

    let contract_address = network_addresses.get(desk_name);
    let crayonDesk = newContractS(contract_address, desk_abi);
    switch (deskAction) {
        case "deposit":
            await deposit_action(crayonDesk);
            break;
        case "withdraw":
            await withdraw_action(crayonDesk);
            break;
        case "borrow":
            await borrow_action(crayonDesk);
            break;
        case "repay":
            await repay_action(crayonDesk);
            break;
        case "extend":
            await extend_action(crayonDesk);
            break;
        case "addCollateral":
            await addCollateral_action(crayonDesk);
            break;
        case "withdrawCollateral":
            await withdrawCollateral_action(crayonDesk);
            break;
        default:
            console.error("unkown method");
    }
}

function deposit_parameters(base_coin) {
    return input_amount('amount', base_coin + ' Amount');
}

async function deposit_action(desk) {
    let base_coin_adrs = await protocol.desk_base(desk);
    let base_contract = newContractS(base_coin_adrs, erc20_abi);

    let amount = dec_to_int(document.getElementById('amount').value, get_selected('desk'));
    await protocol.base_deposit(desk, base_contract, amount);
}

function withdraw_parameters(base_coin) {
    return input_amount('amount', base_coin + ' Amount');
}

async function withdraw_action(desk) {
    let amount = dec_to_int(document.getElementById('amount').value, get_selected('desk'));
    await protocol.base_withdraw(desk, amount);
}

async function borrow_parameters(desk_name, base_coin) {
    return input_amount('amount', base_coin + ' Amount') + await input_horizon_choice(desk_name) + await input_collateral_choice(desk_name) +  input_amount('cAmount', 'Collateral Amount');
}

async function borrow_action(desk) {
    let collateral = document.getElementById('collateral').value;
    let horizon =  document.getElementById('horizon').value;
    if (collateral == 'blank' || horizon == 'horizon') {
        return;
    }

    let collateral_contract = newContractS(collateral, erc20_abi);
    let amount = dec_to_int(document.getElementById('amount').value, get_selected('desk'));
    let cAmount = dec_to_int(document.getElementById('cAmount').value, get_selected('collateral'));
    await protocol.loan_get(desk, amount, collateral_contract, collateral, cAmount, horizon)
}

async function repay_parameters(desk_name, base_coin) {
    return input_amount('amount', base_coin + ' Amount') + await input_collateral_choice(desk_name) + input_default_owner();
}

async function repay_action(desk) {
    let collateral = document.getElementById('collateral').value;
    if (collateral == 'blank') {
        return;
    }
    let base_coin = await protocol.desk_base(desk);
    let base_contract = newContractS(base_coin, erc20_abi);
    let amount = dec_to_int(document.getElementById('amount').value, get_selected('desk'));
    await protocol.loan_repay(desk, base_contract, amount, collateral, document.getElementById('owner').value)
}

async function extend_parameters(desk_name) {
    return await input_horizon_choice(desk_name) + await input_collateral_choice(desk_name);
}

async function extend_action(desk) {
    let collateral = document.getElementById('collateral').value;
    let horizon =  document.getElementById('horizon').value;
    if (collateral == 'blank' || horizon == 'horizon') {
        return;
    }
    await protocol.loan_extend(desk, collateral, horizon)
}

async function addCollateral_parameters(desk_name) {
    return await input_collateral_choice(desk_name) + input_amount('cAmount', 'Collateral Amount') + input_default_owner();
}

async function addCollateral_action(desk) {
    let collateral = document.getElementById('collateral').value;
    if (collateral == 'blank') {
        return;
    }
    
    let collateral_contract = newContractS(collateral, erc20_abi);
    let cAmount = dec_to_int(document.getElementById('cAmount').value, get_selected('collateral'));
    await protocol.collateral_add(desk, collateral_contract, collateral, cAmount, document.getElementById('owner').value);
}

async function withdrawCollateral_parameters(desk_name) {
    return await input_collateral_choice(desk_name) + input_amount('cAmount', 'Collateral Amount'); 
}

async function withdrawCollateral_action(desk) {
    let collateral = document.getElementById('collateral').value;
    if (collateral == 'blank') {
        return;
    }
    let cAmount = dec_to_int(document.getElementById('cAmount').value, get_selected('collateral'));
    await protocol.collateral_rm(desk, cAmount, collateral);
}

function input_amount(amnt, label) {    
    return `<div class="form-floating mb-2"><input class="form-control" type="text" id=${amnt}><label for=${amnt}>${label}</label></div>`;
}

async function input_collateral_choice(desk_name) {
    let ret = '<div class="form-floating mb-2"><select class="form-select form-select-sm" id="collateral">';
    let [collateral_addresses, collateral_names] = await protocol.collateral_accepted(desk_name);
    ret += '<option value="blank"></option>';
    for (let i = 0; i < collateral_addresses.length; i++) {
        ret += '<option value=' + collateral_addresses[i] + '>' + collateral_names[i] + '</option>'
    }
    ret += '</select><label for="collateral">Collateral</label></div>';
    return ret;
}

async function input_horizon_choice(desk_name) {
    let contract_address = network_addresses.get(desk_name);
    let desk = newContractV(contract_address, desk_abi);

    let ret = '<div class="form-floating mb-2"><select class="form-select form-select-sm" id="horizon">';
    let [horizons, fees] = await protocol.horizon_and_fee(desk);
    ret += '<option value="blank"></option>';
    for (let i = 0; i < horizons.length; i++) {
        let numDays = BigInt(horizons[i]) / BigInt(5760);
        let days = numDays == 1 ? "day" : "days";
        ret += '<option value=' + horizons[i] + '>' +  numDays + ' ' + days + '</option>'; 
    }
    ret += '</select><label for="horizon">Horizon</label></div>';
    return ret;
}

function input_default_owner() {
    return `<div class="form-floating mb-2"><input class="form-control" type="text" id="owner" value=${web3.account.address}><label for="owner">Owner Address</label></div>`;
}

function newContractS(adrs, abi) {
    return new web3.ethers.Contract(adrs, abi, web3.browserSigner);
}

function newContractV(adrs, abi) {
    return new web3.ethers.Contract(adrs, abi, web3.browserViewer);
}

function get_selected(element_id) {
    let option_selected = document.getElementById(element_id);
    return option_selected.options[option_selected.selectedIndex].text;
}

function dec_to_int(amount, coin_name) {
    let decimals = token_decimals.get(coin_name.toLowerCase());

    let parts = amount.split('.');
    if (parts.length == 2) {
        let d = parts[1].length;
        if (d > decimals) {
            console.error(coin_name + ' has precision of only ' + decimals + ' digits.');
        }
        amount = parts[0] + parts[1];
        decimals -= d;
    }

    return BigInt(amount) * BigInt(10**decimals);
}

function int_to_dec(amount, coin_name) {
    let decimals = token_decimals.get(coin_name.toLowerCase());

    let am_str = (amount).toString();
    let l = am_str.length;
    if (l < decimals + 1) {
        let zero = '0';
        am_str = zero.repeat(decimals + 1 - l) + am_str;
        l = decimals + 1;
    }

    return am_str.slice(0, l-decimals) + '.' + am_str.slice(l-decimals, l);
}