# Crayon Protocol Dev Front-end

The Crayon Protocol team decided not to host a front-end. There are two main reasons for this decision:

  * Maintaining decentralization by not having a single entity depend on cloud service providers.
  * Impossibility to provide all Crayon Features through a GUI.

To elaborate on this last point, Crayon Protocol's powerful pairs trading support is only accessible through deployed smart contracts including through integrations by other protocols. 

A front-end does however make it possible to use the repo-style asset financing capabilities of the protocol and, for this reason, Crayon Protocol provides incentives to third-parties to provide a front-end. A third-party provider of a GUI, can register permissionlessly with the Crayon Protocol Control smart contract and keep a fraction of `XCRAY` token rewards earned by users of their GUI. The fraction of rewards is specified in the registration transaction. Further details about support for providers can be found in our docs.

This folder contains a basic web app that is integrated with the Crayon Protocol deployments on Arbitrum and Sepolia. This is beta software and for this reason access to Arbitrum One mainnet was disabled in the code. It can be used against a local fork of Arbitrum, however, in addition to Sepolia or a local fork of Sepolia.

### Testing

To serve the app in your browser, you must:

  * have the MetaMask browser extension installed
  * change `network_provider_address` in [`app/js/config.js`](./app/js/config.js) 

If your intention is to host the app and take advantage of the `XCRAY` rewards, then `network_provider_address` in the file must be set to the address to be credited with the fraction of rewards you keep. You must also register with the Control smart contract. 

If you're running the app for your own use, `network_provider_address` can be set to the `null` address specified in the file.

**Note**

You must access the app from a server in order for MetaMask to inject in the browser the RPC provider that the app depends on.

### Registering As Provider

The following code can be run in Node.js to register with the Crayon Control smart contract. Note that it requires installing `ethers` .

```javascript
  import { ethers } from 'ethers';
  
  // This is the address of the Crayon Protocol Control smart contract on Arbitrum
  const crayonControlAddress = '0xe2c5fAC44aF73D44E047879C7A20383ecDC2EEfa';

  // Assume local fork of Arbitrum running on localhost:8545
  const web3Provider = new ethers.JsonRpcProvider();

  // Retrieve accounts
  const accounts = await web3Provider.listAccounts();

  // use accounts[0] as your provider address for the purposes of this test
  const web3Signer = await web3Provider.getSigner(accounts[0].address);

  // You want to keep 1% of XCRAY rewards earned by users of your gui
  const my_fraction_of_reward = 1;

  // Crayon Control uses msg.sender as the address of the registering provider
  const crayonControlContract = new ethers.Contract(crayonControlAddress, ["function register_provider(uint256) external"], web3Signer);
  const tx = await crayonControlContract.register_provider(my_fraction_of_reward);
  await tx.wait();
```

**Note**

Third-party providers should remove the Crayon Protocol logo from the app they host.
