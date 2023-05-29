# arbitrum deployment

Contracts deployed to Arbitrum One.

### Desks

* ETH desk:

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
