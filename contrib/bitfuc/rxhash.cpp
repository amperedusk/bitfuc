// Copyright (c) 2026 BITFUC developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.
//
// Hash or mine an 80-byte header with RandomX. Used to freeze genesis.

#include <crypto/randomx_pow.h>

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

static std::vector<unsigned char> ParseHex(const char* hex)
{
    std::string s(hex);
    if (s.size() % 2) {
        std::fprintf(stderr, "odd hex length\n");
        std::exit(1);
    }
    std::vector<unsigned char> out(s.size() / 2);
    for (size_t i = 0; i < out.size(); ++i) {
        unsigned int v = 0;
        if (std::sscanf(s.c_str() + 2 * i, "%2x", &v) != 1) {
            std::fprintf(stderr, "bad hex\n");
            std::exit(1);
        }
        out[i] = static_cast<unsigned char>(v);
    }
    return out;
}

static void PrintHex(const unsigned char* p, size_t n)
{
    for (size_t i = 0; i < n; ++i) std::printf("%02x", p[i]);
    std::printf("\n");
}

static uint32_t ReadLE32(const unsigned char* p)
{
    return uint32_t(p[0]) | (uint32_t(p[1]) << 8) | (uint32_t(p[2]) << 16) | (uint32_t(p[3]) << 24);
}

static void WriteLE32(unsigned char* p, uint32_t v)
{
    p[0] = v & 0xff;
    p[1] = (v >> 8) & 0xff;
    p[2] = (v >> 16) & 0xff;
    p[3] = (v >> 24) & 0xff;
}

/** Compact nBits -> whether hash (32 LE bytes as Bitcoin uint256) meets target. */
static bool Meets(const unsigned char hash[32], uint32_t nbits)
{
    int n_size = nbits >> 24;
    uint32_t n_word = nbits & 0x007fffff;
    if (n_word == 0 || (nbits & 0x00800000) || n_size > 34) return false;
    unsigned char target[32]{};
    if (n_size <= 3) {
        n_word >>= 8 * (3 - n_size);
        WriteLE32(target, n_word);
    } else {
        const int start = n_size - 3;
        if (start >= 32) return false;
        target[start] = n_word & 0xff;
        if (start + 1 < 32) target[start + 1] = (n_word >> 8) & 0xff;
        if (start + 2 < 32) target[start + 2] = (n_word >> 16) & 0xff;
    }
    for (int i = 31; i >= 0; --i) {
        if (hash[i] < target[i]) return true;
        if (hash[i] > target[i]) return false;
    }
    return true;
}

int main(int argc, char** argv)
{
    if (argc == 3 && std::strcmp(argv[1], "hash") == 0) {
        auto hdr = ParseHex(argv[2]);
        if (hdr.size() != 80) {
            std::fprintf(stderr, "header must be 80 bytes\n");
            return 1;
        }
        unsigned char out[32];
        RandomXPoW(hdr.data(), hdr.size(), out);
        PrintHex(out, 32);
        return 0;
    }
    if (argc == 3 && std::strcmp(argv[1], "mine") == 0) {
        auto hdr = ParseHex(argv[2]);
        if (hdr.size() != 80) {
            std::fprintf(stderr, "header must be 80 bytes\n");
            return 1;
        }
        const uint32_t nbits = ReadLE32(hdr.data() + 72);
        unsigned char out[32];
        for (;;) {
            RandomXPoW(hdr.data(), hdr.size(), out);
            if (Meets(out, nbits)) {
                const uint32_t nonce = ReadLE32(hdr.data() + 76);
                std::printf("nonce %u\n", nonce);
                std::printf("pow ");
                PrintHex(out, 32);
                return 0;
            }
            uint32_t nonce = ReadLE32(hdr.data() + 76) + 1;
            WriteLE32(hdr.data() + 76, nonce);
            if (nonce == 0) {
                std::fprintf(stderr, "nonce wrapped\n");
                return 1;
            }
        }
    }
    std::fprintf(stderr, "usage: bitfuc-rxhash hash <80-byte-hex>\n       bitfuc-rxhash mine <80-byte-hex>\n");
    return 1;
}
