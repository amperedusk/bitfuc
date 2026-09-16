// Copyright (c) The Bitcoin Core developers
// Copyright (c) 2026 BITFUC developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or https://opensource.org/license/mit.

#ifndef BITCOIN_CHAINPARAMSSEEDS_H
#define BITCOIN_CHAINPARAMSSEEDS_H
/**
 * Fixed seed nodes for bitfuc-main.
 * BIP155 serialized (networkID, addr, port). Port 17333.
 * Volunteer list: docs/mainnet-peers.md
 */
static const uint8_t chainparams_seed_main[] = {
    0x01,0x04,0x0d,0x8c,0x85,0x37,0x43,0xb5,
};
static const uint8_t chainparams_seed_test[] = {};
static const uint8_t chainparams_seed_testnet4[] = {};
static const uint8_t chainparams_seed_signet[] = {};
#endif // BITCOIN_CHAINPARAMSSEEDS_H
