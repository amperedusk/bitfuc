// Copyright (c) 2026 BITFUC developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <crypto/randomx_pow.h>

#include <randomx.h>

#include <mutex>
#include <stdexcept>

namespace {

// SHA256("BITFUC RandomX key v1")
constexpr unsigned char KEY[32] = {
    0x6f, 0xbd, 0x63, 0xb9, 0xec, 0x83, 0x1b, 0x11, 0x39, 0xa2, 0x35, 0x9e, 0x83, 0x39, 0x10, 0x01,
    0x27, 0x13, 0xd0, 0x06, 0x83, 0x09, 0x86, 0xf8, 0xab, 0xdd, 0x0d, 0xfc, 0xd1, 0x04, 0xb2, 0x91};

std::mutex g_mutex;
randomx_cache* g_cache = nullptr;
randomx_vm* g_vm = nullptr;

void EnsureVM()
{
    if (g_vm) return;

    randomx_flags flags = randomx_get_flags();
    g_cache = randomx_alloc_cache(flags);
    if (!g_cache) {
        flags = RANDOMX_FLAG_DEFAULT;
        g_cache = randomx_alloc_cache(flags);
    }
    if (!g_cache) {
        throw std::runtime_error("RandomX: alloc_cache failed");
    }
    randomx_init_cache(g_cache, KEY, sizeof(KEY));
    g_vm = randomx_create_vm(flags, g_cache, nullptr);
    if (!g_vm) {
        randomx_release_cache(g_cache);
        g_cache = nullptr;
        throw std::runtime_error("RandomX: create_vm failed");
    }
}

} // namespace

void RandomXPoW(const unsigned char* header, size_t header_len, unsigned char hash[32])
{
    std::lock_guard<std::mutex> lock(g_mutex);
    EnsureVM();
    randomx_calculate_hash(g_vm, header, header_len, hash);
}
