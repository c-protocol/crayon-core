# desk_weth

Data and oracles for the test deployment of the WETH Desk on Sepolia Testnet. We use test contracts deployed by our friends at Aave Protocol.

**Note:** Crayon Protocol desks require all prices to be expressed in units of the base token of the desk. The Aave test oracles we use for this deployment express prices in units of $0.00000001 (10**-8). We therefore deploy intermediate oracles that convert those prices to units of ETH 0.00000001.
