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

std::once_flag g_cache_once;
randomx_cache* g_cache = nullptr;
randomx_flags g_flags = RANDOMX_FLAG_DEFAULT;

void InitCache()
{
    g_flags = randomx_get_flags();
    g_cache = randomx_alloc_cache(g_flags);
    if (!g_cache) {
        g_flags = RANDOMX_FLAG_DEFAULT;
        g_cache = randomx_alloc_cache(g_flags);
    }
    if (!g_cache) {
        throw std::runtime_error("RandomX: alloc_cache failed");
    }
    randomx_init_cache(g_cache, KEY, sizeof(KEY));
}

struct ThreadVM {
    randomx_vm* vm{nullptr};
    ThreadVM()
    {
        std::call_once(g_cache_once, InitCache);
        vm = randomx_create_vm(g_flags, g_cache, nullptr);
        if (!vm) {
            throw std::runtime_error("RandomX: create_vm failed");
        }
    }
    ~ThreadVM()
    {
        if (vm) randomx_destroy_vm(vm);
    }
    ThreadVM(const ThreadVM&) = delete;
    ThreadVM& operator=(const ThreadVM&) = delete;
};

} // namespace

void RandomXPoW(const unsigned char* header, size_t header_len, unsigned char hash[32])
{
    thread_local ThreadVM tls;
    randomx_calculate_hash(tls.vm, header, header_len, hash);
}
