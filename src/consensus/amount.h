// Copyright (c) 2009-2010 Satoshi Nakamoto
// Copyright (c) 2009-present The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef BITCOIN_CONSENSUS_AMOUNT_H
#define BITCOIN_CONSENSUS_AMOUNT_H

#include <cstdint>

/** Amount in bits (can be negative). 1 FUC = 100,000,000 bits. */
typedef int64_t CAmount;

/** The number of bits in one FUC. */
static constexpr CAmount COIN = 100000000;

/** No amount larger than this (in bits) is valid.
 *
 * This is a sanity check used by consensus-critical validation, not the
 * circulating supply. BITFUC's public-net cap is 1,000,000,000 FUC
 * (`docs/monetary-policy.md`). Changing MAX_MONEY after a public launch
 * is a fork.
 * */
static constexpr CAmount MAX_MONEY = 1000000000 * COIN;
inline bool MoneyRange(const CAmount& nValue) { return (nValue >= 0 && nValue <= MAX_MONEY); }

#endif // BITCOIN_CONSENSUS_AMOUNT_H
