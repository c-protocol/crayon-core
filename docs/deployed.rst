Deployed Desks
##############

Contracts deployed to Arbitrum One.

``WETH`` desk
=============

    * desk address: `0x8351483e30928D1Fe1f80eD5062c6438faa85b88 <https://arbiscan.io/address/0x8351483e30928D1Fe1f80eD5062c6438faa85b88#writeContract>`_
    * base coin (to deposit/borrow): ``WETH`` (`0x82aF49447D8a07e3bd95BD0d56f35241523fBab1 <https://arbiscan.io/address/0x82aF49447D8a07e3bd95BD0d56f35241523fBab1>`_)
    * longables (to buy with leverage/post as collateral): 
        * ``WBTC``:   `0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f <https://arbiscan.io/address/0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f>`_
        * ``wstETH``: `0x5979D7b546E38E414F7E9822514be443A4800529 <https://arbiscan.io/address/0x5979D7b546E38E414F7E9822514be443A4800529>`_
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

``WBTC`` desk
=============

    * desk address: `0x3454923795c5EdD5b3967e3B63140c343e6BB3dF <https://arbiscan.io/address/0x3454923795c5EdD5b3967e3B63140c343e6BB3dF#writeContract>`_
    * base coin: ``WBTC`` (`0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f <https://arbiscan.io/address/0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f>`_)
    * longables:
        * ``WETH``: `0x82aF49447D8a07e3bd95BD0d56f35241523fBab1 <https://arbiscan.io/address/0x82aF49447D8a07e3bd95BD0d56f35241523fBab1>`_
        * ``ARB``:  `0x912CE59144191C1204E64559FE8253a0e49E6548 <https://arbiscan.io/address/0x912CE59144191C1204E64559FE8253a0e49E6548>`_
        * ``GMX``:  `0xfc5A1A6EB076a2C7aD06eD22C90d7E710E35ad0a <https://arbiscan.io/address/0xfc5A1A6EB076a2C7aD06eD22C90d7E710E35ad0a>`_
        * ``USDC``: `0xaf88d065e77c8cC2239327C5EDb3A432268e5831 <https://arbiscan.io/address/0xaf88d065e77c8cC2239327C5EDb3A432268e5831>`_
        * ``RDNT``: `0x3082CC23568eA640225c2467653dB90e9250AaA0 <https://arbiscan.io/address/0x3082CC23568eA640225c2467653dB90e9250AaA0>`_
    * oracles (price ratios to ``WBTC`` from Chainlink prices):
        * ``WETH``: `0x7A8d454d553Fa464FE9FA63180555e8582565e1c <https://arbiscan.io/address/0x7A8d454d553Fa464FE9FA63180555e8582565e1c>`_
        * ``ARB``:  `0xCf5C0726D2F88092F1dB477c9b8D70c674c94C0A <https://arbiscan.io/address/0xCf5C0726D2F88092F1dB477c9b8D70c674c94C0A>`_
        * ``GMX``:  `0xd3b9bB3d94653815512C4F322c3AAdD741734Ef9 <https://arbiscan.io/address/0xd3b9bB3d94653815512C4F322c3AAdD741734Ef9>`_
        * ``USDC``: `0x1f26523116b78C96c74F61417d79B77219eEF81b <https://arbiscan.io/address/0x1f26523116b78C96c74F61417d79B77219eEF81b>`_
        * ``RDNT``: `0xf309849D200cf4C6E79e605A15CCdE9cF6b726A9 <https://arbiscan.io/address/0xf309849D200cf4C6E79e605A15CCdE9cF6b726A9>`_    
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

``USDC`` desk
=============

    * desk address: `0x5dE27C6D5524EE07c0dB88CAB65022E3210a81c4 <https://arbiscan.io/address/0x5dE27C6D5524EE07c0dB88CAB65022E3210a81c4#writeContract>`_
    * base coin: ``USDC`` (`0xaf88d065e77c8cC2239327C5EDb3A432268e5831 <https://arbiscan.io/address/0xaf88d065e77c8cC2239327C5EDb3A432268e5831>`_)
    * longables:
        * ``WBTC``: `0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f <https://arbiscan.io/address/0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f>`_
        * ``GMX``:  `0xfc5A1A6EB076a2C7aD06eD22C90d7E710E35ad0a <https://arbiscan.io/address/0xfc5A1A6EB076a2C7aD06eD22C90d7E710E35ad0a>`_
        * ``ARB``:  `0x912CE59144191C1204E64559FE8253a0e49E6548 <https://arbiscan.io/address/0x912CE59144191C1204E64559FE8253a0e49E6548>`_
        * ``WETH``: `0x82aF49447D8a07e3bd95BD0d56f35241523fBab1 <https://arbiscan.io/address/0x82aF49447D8a07e3bd95BD0d56f35241523fBab1>`_
        * ``RDNT``: `0x3082CC23568eA640225c2467653dB90e9250AaA0 <https://arbiscan.io/address/0x3082CC23568eA640225c2467653dB90e9250AaA0>`_
    * oracles (price ratios to ``USDC`` from Chainlink prices):
        * ``WBTC``: `0xB2c742c8b96C50E6dAF57A21c29f096737172acB <https://arbiscan.io/address/0xB2c742c8b96C50E6dAF57A21c29f096737172acB>`_
        * ``GMX``:  `0xDA584431C700852d5bD9066F803bB07a31d37b0E <https://arbiscan.io/address/0xDA584431C700852d5bD9066F803bB07a31d37b0E>`_
        * ``ARB``:  `0x224F0e7EAe498Aa2a60A73A4e6Ac73Ef82E934Aa <https://arbiscan.io/address/0x224F0e7EAe498Aa2a60A73A4e6Ac73Ef82E934Aa>`_
        * ``WETH``: `0x95cD44358D301B2A48fF85f5a4F02547c03c8285 <https://arbiscan.io/address/0x95cD44358D301B2A48fF85f5a4F02547c03c8285>`_
        * ``RDNT``: `0xbD2A74a9797FC0B1E8136D24cD3B43637744ad09 <https://arbiscan.io/address/0xbD2A74a9797FC0B1E8136D24cD3B43637744ad09>`_
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

``ARB`` desk
============

    * desk address: `0x343d5F534C4C1fB83cdDf0875cC91591cCf69416 <https://arbiscan.io/address/0x343d5F534C4C1fB83cdDf0875cC91591cCf69416#writeContract>`_
    * base coin: ``ARB`` (`0x912CE59144191C1204E64559FE8253a0e49E6548 <https://arbiscan.io/address/0x912CE59144191C1204E64559FE8253a0e49E6548>`_)
    * longables:
        * ``WETH``: `0x82aF49447D8a07e3bd95BD0d56f35241523fBab1 <https://arbiscan.io/address/0x82aF49447D8a07e3bd95BD0d56f35241523fBab1>`_
        * ``WBTC``: `0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f <https://arbiscan.io/address/0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f>`_
        * ``GMX`` : `0xfc5A1A6EB076a2C7aD06eD22C90d7E710E35ad0a <https://arbiscan.io/address/0xfc5A1A6EB076a2C7aD06eD22C90d7E710E35ad0a>`_
        * ``USDC``: `0xaf88d065e77c8cC2239327C5EDb3A432268e5831 <https://arbiscan.io/address/0xaf88d065e77c8cC2239327C5EDb3A432268e5831>`_
        * ``RDNT``: `0x3082CC23568eA640225c2467653dB90e9250AaA0 <https://arbiscan.io/address/0x3082CC23568eA640225c2467653dB90e9250AaA0>`_
    * oracles (price ratios to ``ARB`` from Chainlink prices):
        * ``WETH``: `0x1Ff947C7F44A1001aC7821b9aD4e3c2A0c840B70 <https://arbiscan.io/address/0x1Ff947C7F44A1001aC7821b9aD4e3c2A0c840B70>`_
        * ``WBTC``: `0xE3Ff67F96bfE959b1779c1A22A8De65E1E13D38B <https://arbiscan.io/address/0xE3Ff67F96bfE959b1779c1A22A8De65E1E13D38B>`_
        * ``GMX`` : `0x98bda488D7771eDc6498A411210aA8e533ca4fb1 <https://arbiscan.io/address/0x98bda488D7771eDc6498A411210aA8e533ca4fb1>`_
        * ``USDC``: `0xBFB072221C1b297db87a479656C0ad7A5d95B0af <https://arbiscan.io/address/0xBFB072221C1b297db87a479656C0ad7A5d95B0af>`_
        * ``RDNT``: `0xF49C148B82D7F20ED107ebA0F3C6de89AD78f2d5 <https://arbiscan.io/address/0xF49C148B82D7F20ED107ebA0F3C6de89AD78f2d5>`_
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

``GMX`` desk
============

    * desk address: `0x635b2fE7bF8d41B0477A492f953f57b40E385Cfb <https://arbiscan.io/address/0x635b2fE7bF8d41B0477A492f953f57b40E385Cfb#writeContract>`_
    * base coin: ``GMX`` (`0xfc5A1A6EB076a2C7aD06eD22C90d7E710E35ad0a <https://arbiscan.io/address/0xfc5A1A6EB076a2C7aD06eD22C90d7E710E35ad0a>`_)
    * longables:
        * ``WETH``: `0x82aF49447D8a07e3bd95BD0d56f35241523fBab1 <https://arbiscan.io/address/0x82aF49447D8a07e3bd95BD0d56f35241523fBab1>`_
        * ``WBTC``: `0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f <https://arbiscan.io/address/0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f>`_
        * ``ARB`` : `0x912CE59144191C1204E64559FE8253a0e49E6548 <https://arbiscan.io/address/0x912CE59144191C1204E64559FE8253a0e49E6548>`_
        * ``USDC``: `0xaf88d065e77c8cC2239327C5EDb3A432268e5831 <https://arbiscan.io/address/0xaf88d065e77c8cC2239327C5EDb3A432268e5831>`_
        * ``RDNT``: `0x3082CC23568eA640225c2467653dB90e9250AaA0 <https://arbiscan.io/address/0x3082CC23568eA640225c2467653dB90e9250AaA0>`_
    * oracles (price ratios to ``GMX`` from Chainlink prices):
        * ``WETH``: `0x5FFA5275A36292a1FF31F7D23491334250209143 <https://arbiscan.io/address/0x5FFA5275A36292a1FF31F7D23491334250209143>`_
        * ``WBTC``: `0xd5B236C34F4767dc323922FFE8FC0636257aDc15 <https://arbiscan.io/address/0xd5B236C34F4767dc323922FFE8FC0636257aDc15>`_
        * ``ARB`` : `0xd931d55F3C2CBa797015f9C71eE01986B433Bc61 <https://arbiscan.io/address/0xd931d55F3C2CBa797015f9C71eE01986B433Bc61>`_
        * ``USDC``: `0x78489dDF2fD9ef4c4E809598A6271991347E82Fc <https://arbiscan.io/address/0x78489dDF2fD9ef4c4E809598A6271991347E82Fc>`_
        * ``RDNT``: `0x4f594d0f096E8ac666806Cff1503A067cA01864A <https://arbiscan.io/address/0x4f594d0f096E8ac666806Cff1503A067cA01864A>`_
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


``RDNT`` desk
=============

    * desk address: `0xfE2A45BF13965393c863460F063bDD4a9874c415 <https://arbiscan.io/address/0xfE2A45BF13965393c863460F063bDD4a9874c415#writeContract>`_
    * base coin: ``RDNT`` (`0x3082CC23568eA640225c2467653dB90e9250AaA0 <https://arbiscan.io/address/0x3082CC23568eA640225c2467653dB90e9250AaA0>`_)
    * longables:
        * ``WETH``: `0x82aF49447D8a07e3bd95BD0d56f35241523fBab1 <https://arbiscan.io/address/0x82aF49447D8a07e3bd95BD0d56f35241523fBab1>`_
        * ``WBTC``: `0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f <https://arbiscan.io/address/0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f>`_
        * ``ARB`` : `0x912CE59144191C1204E64559FE8253a0e49E6548 <https://arbiscan.io/address/0x912CE59144191C1204E64559FE8253a0e49E6548>`_
        * ``USDC``: `0xaf88d065e77c8cC2239327C5EDb3A432268e5831 <https://arbiscan.io/address/0xaf88d065e77c8cC2239327C5EDb3A432268e5831>`_
        * ``GMX``: `0xfc5A1A6EB076a2C7aD06eD22C90d7E710E35ad0a <https://arbiscan.io/address/0xfc5A1A6EB076a2C7aD06eD22C90d7E710E35ad0a>`_
    * oracles (price ratios to ``RDNT`` from Chainlink prices):
        * ``WETH``: `0x0955c1FD089dea1929C2bD7176e08eE29fD92b4D <https://arbiscan.io/address/0x0955c1FD089dea1929C2bD7176e08eE29fD92b4D>`_
        * ``WBTC``: `0x7C3155653E0075F7dB75D9CAeA4B3D6bD39DdaE6 <https://arbiscan.io/address/0x7C3155653E0075F7dB75D9CAeA4B3D6bD39DdaE6>`_
        * ``ARB`` : `0xE31ea2670050F0F30Ca9c4217672675F2876F385 <https://arbiscan.io/address/0xE31ea2670050F0F30Ca9c4217672675F2876F385>`_
        * ``USDC``: `0x3F0681C63ce9d7f1A3474c9a1dA6875AE4D223D3 <https://arbiscan.io/address/0x3F0681C63ce9d7f1A3474c9a1dA6875AE4D223D3>`_
        * ``GMX``:  `0xD5933D569c064E4D291991260cA24d4917db69F3 <https://arbiscan.io/address/0xD5933D569c064E4D291991260cA24d4917db69F3>`_
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

