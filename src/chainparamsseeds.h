// Copyright (c) The Bitcoin Core developers
// Copyright (c) 2026 BITFUC developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or https://opensource.org/license/mit.

#ifndef BITCOIN_CHAINPARAMSSEEDS_H
#define BITCOIN_CHAINPARAMSSEEDS_H
/**
 * BITFUC ships with no hardcoded seed nodes. Anyone can operate a seed.
 * Bitcoin Core's seed lists must not be included: those IPs are Bitcoin peers.
 */
static const uint8_t chainparams_seed_main[] = {};
static const uint8_t chainparams_seed_test[] = {};
static const uint8_t chainparams_seed_testnet4[] = {};
static const uint8_t chainparams_seed_signet[] = {};
#endif // BITCOIN_CHAINPARAMSSEEDS_H
