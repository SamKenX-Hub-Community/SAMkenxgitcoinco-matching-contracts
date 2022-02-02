// We require the Hardhat Runtime Environment explicitly here. This is optional
// but useful for running the script in a standalone fashion through `node <script>`.
// When running the script with `hardhat run <script>` you'll find the Hardhat
// Runtime Environment's members available in the global scope.
import hre from 'hardhat';
import { Contract, ContractFactory } from 'ethers';
import { ConstructorArgs } from '../types';
import { Signer } from '@ethersproject/abstract-signer';

const { ethers } = hre;
const padding = 25; // spacing for console.log outputs

// Define constructor arguments by network
const constructorArgs: Record<string, ConstructorArgs> = {
  localhost: {
    // localhost values populated at runtime
    owner: '',
    funder: '',
    dai: '',
  },
  mainnet: {
    owner: '0x5cdb35fADB8262A3f88863254c870c2e6A848CcA', // TODO: UDPATE
    funder: '0xde21F729137C5Af1b01d73aF1dC21eFfa2B8a0d6', // Gitcoin Grants multisig
    dai: '0x6B175474E89094C44Da98b954EedeAC495271d0F',
  },
  rinkeby: {
    owner: '0x5cdb35fADB8262A3f88863254c870c2e6A848CcA', // TODO: UDPATE
    funder: '0x5cdb35fADB8262A3f88863254c870c2e6A848CcA', // TODO: UDPATE
    dai: '0x2e055eEe18284513B993dB7568A592679aB13188',
  },
  polygon: {
    owner: '0x5cdb35fADB8262A3f88863254c870c2e6A848CcA',
    funder: '0x5cdb35fADB8262A3f88863254c870c2e6A848CcA',
    dai: '0x8f3cf7ad23cd3cadbd9735aff958023239c6a063', // https://polygonscan.com/token/0x8f3cf7ad23cd3cadbd9735aff958023239c6a063
  },
  polygonMumbai: {
    owner: '0x5cdb35fADB8262A3f88863254c870c2e6A848CcA',
    funder: '0x5cdb35fADB8262A3f88863254c870c2e6A848CcA',
    dai: '0x75DB33382DF5FbbA9d4344bFD04b3D8c8f3a0eB9', // This is a random dummy DAI contract https://mumbai.polygonscan.com/address/0x75DB33382DF5FbbA9d4344bFD04b3D8c8f3a0eB9#readContract
  },
};

async function main(): Promise<void> {
  const network = hre.network.name;

  // Hardhat always runs the compile task when running scripts through it.
  // If this runs in a standalone fashion you may want to call compile manually
  // to make sure everything is compiled
  await hre.run('compile');

  let deployer: Signer;
  if (network === 'localhost') {
    // If localhost, deploy mock DAI and configure constructor arguments
    // Deploy Mock DAI
    console.log('Deploying mock DAI on localhost...');
    const Dai: ContractFactory = await ethers.getContractFactory('MockERC20');
    const dai: Contract = await Dai.deploy('Dai', 'DAI');
    await dai.deployed();
    console.log('Mock DAI deployed to'.padEnd(padding), dai.address);

    // Set constructor arguments
    const signers: Signer[] = await ethers.getSigners();
    constructorArgs[network].owner = await signers[1].getAddress();
    constructorArgs[network].funder = await signers[2].getAddress();
    constructorArgs[network].dai = dai.address;

    // Set deployer
    deployer = signers[0];
  } else {
    // We want to deploy with the third account derived from the mnemonic, and we hardcode that
    // address here to enforce that
    const signers: Signer[] = await ethers.getSigners();

    // NOTE: UPDATE THIS WITH YOUR ADDRESS POSITION IN signers
    deployer = signers[0];

    const deployerAddress = await deployer.getAddress();
    if (deployerAddress !== process.env.DEPLOYER_ADDRESS) {
      throw new Error('Wrong deployer address!');
    }
  }

  // Deploy MatchPayouts contract
  const { owner, funder, dai } = constructorArgs[network];
  const MatchPayouts: ContractFactory = await ethers.getContractFactory('MatchPayouts');
  const matchPayouts: Contract = await MatchPayouts.connect(deployer).deploy(owner, funder, dai);
  await matchPayouts.deployed();
  console.log('MatchPayouts deployed to'.padEnd(padding), matchPayouts.address);
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main()
  .then(() => process.exit(0))
  .catch((error: Error) => {
    console.error(error);
    process.exit(1);
  });
