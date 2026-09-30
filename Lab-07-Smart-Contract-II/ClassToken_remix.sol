// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

// ===========================================================================
// REMIX PATH — ClassToken (ERC-20, capped, permit)
// Open https://remix.trustkeys.com and paste this file, OR use the Hardhat
// project in lab/solutions/. Remix resolves the @openzeppelin imports below
// straight from npm — no manual flattening needed.
//
// COMPILER SETTINGS in Remix (Solidity Compiler tab):
//   - Compiler: 0.8.24
//   - EVM version: "paris"  (matches TrustKeys' Geth; avoids Cancun opcodes)
//   - Enable optimization: 200 runs
// The OZ version is PINNED in the import paths (@5.0.2) so a newer OZ that
// uses the Cancun `mcopy` opcode can't sneak in and break deployment.
//
// DEPLOY: "Deploy & Run" tab -> Environment = "Injected Provider - MetaMask"
//   (MetaMask on TrustKeys: RPC https://l1testnet.trustkeys.network, chainId 11968)
//   -> constructor arg initialHolder = your address -> Deploy.
// ===========================================================================

import {ERC20} from "@openzeppelin/contracts@5.0.2/token/ERC20/ERC20.sol";
import {ERC20Capped} from "@openzeppelin/contracts@5.0.2/token/ERC20/extensions/ERC20Capped.sol";
import {ERC20Permit} from "@openzeppelin/contracts@5.0.2/token/ERC20/extensions/ERC20Permit.sol";

/// @title ClassToken (CTK) — Session 7 lab, a fungible ERC-20
/// @notice Capped token; the whole supply (= cap) is minted to `initialHolder`.
contract ClassToken is ERC20, ERC20Capped, ERC20Permit {
    constructor(address initialHolder)
        ERC20("ClassToken", "CTK")
        ERC20Capped(1_000_000 * 10 ** 18)
        ERC20Permit("ClassToken")
    {
        _mint(initialHolder, 1_000_000 * 10 ** 18);
    }

    // ERC20 and ERC20Capped both define _update — disambiguate. super runs
    // Capped's cap check, then ERC20's balance bookkeeping.
    function _update(address from, address to, uint256 value)
        internal
        override(ERC20, ERC20Capped)
    {
        super._update(from, to, value);
    }
}
