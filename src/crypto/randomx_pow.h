// Copyright (c) 2026 BITFUC developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef BITCOIN_CRYPTO_RANDOMX_POW_H
#define BITCOIN_CRYPTO_RANDOMX_POW_H

#include <cstddef>

/** Hash an 80-byte block header with RandomX (light mode, shared VM). Thread-safe. */
void RandomXPoW(const unsigned char* header, size_t header_len, unsigned char hash[32]);

#endif // BITCOIN_CRYPTO_RANDOMX_POW_H
