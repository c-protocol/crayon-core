# arbitrum deployment

Contracts deployed to Arbitrum One.

### Desks

* WETH desk:

    * base coin (to deposit/borrow): WETH (0x82aF49447D8a07e3bd95BD0d56f35241523fBab1)
    * longables (to buy with leverage/post as collateral): 

        * WBTC: 0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f
        * wstETH: 0x5979D7b546E38E414F7E9822514be443A4800529

    * horizons (periods for loans) and current fees:

        * 5760 blocks (~ 1 day) for 9 bps
        * 17280 blocks (~ 3 days) for 18 bps
        * 40320 blocks (~ 7 days) for 45 bps

    * current rates of XCRAY rewards per block:

        * borrowers: 0.5 XCRAY
        * lenders: 0.5 XCRAY

    * threshold to liquidation (collateral value / loan value): 130%
    * liquidation bonus: 500 bps (5%)
    * fee for flash loans (base coin or longables): 9 bps

* WBTC desk:

    * base coin: WBTC (0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f)
    * longables:

        * WETH: 0x82aF49447D8a07e3bd95BD0d56f35241523fBab1
        * ARB:  0x912CE59144191C1204E64559FE8253a0e49E6548
        * GMX:  0xfc5A1A6EB076a2C7aD06eD22C90d7E710E35ad0a
        * USDC: 0xaf88d065e77c8cC2239327C5EDb3A432268e5831
        * RDNT: 0x3082CC23568eA640225c2467653dB90e9250AaA0

    * oracles (normalized from Chainlink prices):

        * WETH: 0x7A8d454d553Fa464FE9FA63180555e8582565e1c
        * ARB:  0xCf5C0726D2F88092F1dB477c9b8D70c674c94C0A
        * GMX:  0xd3b9bB3d94653815512C4F322c3AAdD741734Ef9
        * USDC: 0x1f26523116b78C96c74F61417d79B77219eEF81b
        * RDNT: 0xf309849D200cf4C6E79e605A15CCdE9cF6b726A9
    
    * horizons (periods for loans) and current fees:

        * 5760 blocks (~ 1 day) for 9 bps
        * 17280 blocks (~ 3 days) for 18 bps
        * 40320 blocks (~ 7 days) for 45 bps

    * current rates of XCRAY rewards per block:

        * borrowers: 0.5 XCRAY
        * lenders: 0.5 XCRAY

    * threshold to liquidation (collateral value / loan value): 130%
    * liquidation bonus: 500 bps (5%)
    * fee for flash loans (base coin or longables): 9 bps

* USDC desk:

    * base coin: USDC (0xaf88d065e77c8cC2239327C5EDb3A432268e5831)
    * longables:

        * WBTC: 0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f
        * GMX:  0xfc5A1A6EB076a2C7aD06eD22C90d7E710E35ad0a
        * ARB:  0x912CE59144191C1204E64559FE8253a0e49E6548
        * WETH: 0x82aF49447D8a07e3bd95BD0d56f35241523fBab1
        * RDNT: 0x3082CC23568eA640225c2467653dB90e9250AaA0

    * oracles (normalized from Chainlink prices):

        * WBTC: 0xB2c742c8b96C50E6dAF57A21c29f096737172acB
        * GMX:  0xDA584431C700852d5bD9066F803bB07a31d37b0E
        * ARB:  0x224F0e7EAe498Aa2a60A73A4e6Ac73Ef82E934Aa
        * WETH: 0x95cD44358D301B2A48fF85f5a4F02547c03c8285
        * RDNT: 0xbD2A74a9797FC0B1E8136D24cD3B43637744ad09

    * horizons (periods for loans) and current fees:

        * 5760 blocks (~ 1 day) for 9 bps
        * 17280 blocks (~ 3 days) for 18 bps
        * 40320 blocks (~ 7 days) for 45 bps

    * current rates of XCRAY rewards per block:

        * borrowers: 0.5 XCRAY
        * lenders: 0.5 XCRAY

    * threshold to liquidation (collateral value / loan value): 130%
    * liquidation bonus: 500 bps (5%)
    * fee for flash loans (base coin or longables): 9 bps

### Oracles

All oracles in [`oracles_data.json`](oracles_data.json) are Chainlink oracles and have USD as numeraire. We combine two oracles to change the numeraire for use in one of our desks. A change of numeraire amounts to calculating a price ratio.