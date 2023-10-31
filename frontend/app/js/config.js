
var network_provider_address;
var network_desk_collateral;
var network_desks;
var network_addresses;

export function updateGlobals() {

    var network = document.getElementById("network").value;

    if (network == "arbitrum") {
        /*
        * Frontend providers: set this to the address that you used to register with Crayon Control
        *
        * Other users (non-frontend-providers): set this to the null address, i.e.,
        * 0x0000000000000000000000000000000000000000
        */
        network_provider_address = "replace_me_with_valid_address_or_the_null_address";

        /*
        * Crayon Protocol deployment information below. Currently only deployed on Arbitrum
        */

        network_desk_collateral = new Map(
            [
                ["usdcDesk", ["weth", "wbtc", "arb", "gmx", "rdnt"]],
                ["wethDesk", ["wbtc", "wsteth"]],
                ["wbtcDesk", ["weth", "arb", "gmx", "usdc", "rdnt"]],
                ["arbDesk", ["weth", "wbtc", "gmx", "usdc", "rdnt"]],
                ["gmxDesk", ["weth", "wbtc", "arb", "usdc", "rdnt"]],
                ["rdntDesk", ["weth", "wbtc", "arb", "gmx", "usdc"]]
            ]
        );

        network_addresses = new Map(
            [
                ["usdcDesk", "0x5dE27C6D5524EE07c0dB88CAB65022E3210a81c4"],
                ["wethDesk", "0x8351483e30928D1Fe1f80eD5062c6438faa85b88"],
                ["wbtcDesk", "0x3454923795c5EdD5b3967e3B63140c343e6BB3dF"],
                ["arbDesk", "0x343d5F534C4C1fB83cdDf0875cC91591cCf69416"],
                ["gmxDesk", "0x635b2fE7bF8d41B0477A492f953f57b40E385Cfb"],
                ["rdntDesk", "0xfE2A45BF13965393c863460F063bDD4a9874c415"],
                ["weth", "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1"],
                ["wbtc", "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f"],
                ["arb", "0x912CE59144191C1204E64559FE8253a0e49E6548"],
                ["gmx", "0xfc5A1A6EB076a2C7aD06eD22C90d7E710E35ad0a"],
                ["rdnt", "0x3082CC23568eA640225c2467653dB90e9250AaA0"],
                ["usdc", "0xaf88d065e77c8cC2239327C5EDb3A432268e5831"],
                ["wsteth", "0x5979D7b546E38E414F7E9822514be443A4800529"],
                ["control", "0xe2c5fAC44aF73D44E047879C7A20383ecDC2EEfa"]
            ]
        );

    } else if (network == "sepolia") {

        /*
        * Frontend providers: set this to the address that you used to register with Crayon Control
        *
        * Other users (non-frontend-providers): set this to the null address, i.e.,
        * 0x0000000000000000000000000000000000000000
        */
        network_provider_address = "replace_me_with_valid_address_or_the_null_address";

        /*
        * Crayon Protocol deployment information below. Currently only deployed on Arbitrum
        */

        network_desk_collateral = new Map(
            [
                ["daiDesk", ["weth", "wbtc", "usdc"]],
                ["wethDesk", ["wbtc", "dai", "usdc"]],
                ["wbtcDesk", ["weth", "dai", "usdc"]]
            ]
        );
        
        network_addresses = new Map(
            [
                ["daiDesk", "0x9c27f6BC1fFb37ce0d9fBfc35DCC6b8aF1C08962"],
                ["wethDesk", "0x80d73254eF0a863E76eA0035613558f5e035b771"],
                ["wbtcDesk", "0x049041B5EFfe8b85d6476Ce696DF003ce4d54cD9"],
                ["control", "0x64292f63a4bFe61CC3C4C101b31494E5028B67b7"],
                ["xcray", "0x66e5392209eCb5Fab51C7B3DB53383E353a07995"],
                ["dai", "0x68194a729C2450ad26072b3D33ADaCbcef39D574"],
                ["weth", "0xD0dF82dE051244f04BfF3A8bB1f62E1cD39eED92"],
                ["wbtc", "0xf864F011C5A97fD8Da79baEd78ba77b47112935a"],
                ["usdc", "0xda9d4f9b69ac6C22e444eD9aF0CfC043b7a7f53f"]
            ]
        );

    } else {
        network_provider_address = "";
        network_desk_collateral = new Map();
        network_addresses = new Map();
    }

    network_desks = [...network_desk_collateral.keys()].map(d => network_addresses.get(d));

}

const networks = ["arbitrum", "sepolia"];

const erc20_abi = [
    "function approve(address, uint256) external returns (bool)",
    "function balanceOf(address) view returns (uint256)",
    "function transfer(address, uint256)"
];

// We currently assume desks will have the same interface across all networks

const desk_abi = [
    "function base_coin() external view returns (address)",
    "function total_liquidity() external view returns (uint256)",
    "function total_loans() external view returns (uint256)",
    "function total_reserved() external view returns (uint256)",
    "function deposit(uint256) external",
    "function withdraw(uint256, address) external",
    "function post_longable_then_borrow(uint256, address, uint256, uint256, address) external",
    "function withdraw_longable(uint256, address) external",
    "function repay(uint256, address, address, address) external",
    "function post_longable(uint256, address, address) external",
    "function extend_loan(address, uint256) external",
    "function balanceOf(address) external view returns (uint256)",
    "function loanOf(address, address) external view returns (uint256, uint256, uint256)",
    "function num_horizons() external view returns (int128)",
    "function get_horizon_and_fee(int128) external view returns (uint256, uint256)"
];

const control_abi = [
    "function reward_balanceOf(address, address[]) external view returns (uint256)",
    "function mint_all_reward_token(address) external"
];

const token_decimals = new Map(
    [
        ["usdc", 6],
        ["dai", 18],
        ["weth", 18],
        ["wbtc", 8],
        ["gmx", 18],
        ["arb", 18],
        ["rdnt", 18],
        ["wsteth", 18],
        ["xcray", 27]
    ]
);

export {network_provider_address, network_addresses, network_desks, network_desk_collateral, control_abi, desk_abi, erc20_abi, token_decimals, networks};
