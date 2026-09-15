// Copyright (c) 2009-2010 Satoshi Nakamoto
// Copyright (c) 2009-present The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <pow.h>

#include <arith_uint256.h>
#include <chain.h>
#include <crypto/randomx_pow.h>
#include <primitives/block.h>
#include <span.h>
#include <streams.h>
#include <uint256.h>
#include <util/check.h>

#include <algorithm>
#include <cassert>
#include <cstdint>
#include <limits>

static arith_uint256 CalculateASERT(const arith_uint256& refTarget,
                                    const int64_t nPowTargetSpacing,
                                    const int64_t nTimeDiff,
                                    const int64_t nHeightDiff,
                                    const arith_uint256& powLimit,
                                    const int64_t nHalfLife)
{
    Assert(refTarget > 0);
    Assert(nHeightDiff >= 0);
    Assert(nHalfLife > 0);
    static_assert(int64_t(-1) >> 1 == int64_t(-1), "ASERT needs arithmetic right shift");

    // new_target ≈ refTarget * 2^((nTimeDiff - spacing*(heightDiff+1)) / halfLife)
    // 16.16 fixed-point exponent (aserti3-2d). Use 128-bit math so fuzz timestamps cannot overflow.
    const __int128 exponent_i = ((__int128)nTimeDiff - (__int128)nPowTargetSpacing * (nHeightDiff + 1)) * 65536 / nHalfLife;
    const int64_t exponent = exponent_i > std::numeric_limits<int64_t>::max() ? std::numeric_limits<int64_t>::max()
                          : exponent_i < std::numeric_limits<int64_t>::min() ? std::numeric_limits<int64_t>::min()
                          : static_cast<int64_t>(exponent_i);
    int64_t shifts = exponent >> 16;
    const uint16_t frac = static_cast<uint16_t>(exponent);

    const uint32_t factor = 65536 + ((
        + 195766423245049ull * frac
        + 971821376ull * frac * frac
        + 5127ull * frac * frac * frac
        + (1ull << 47)
        ) >> 48);

    arith_uint256 nextTarget = refTarget * factor;
    shifts -= 16;
    if (shifts > 256) {
        nextTarget = powLimit;
    } else if (shifts < -256) {
        nextTarget = arith_uint256(1);
    } else if (shifts <= 0) {
        nextTarget >>= -shifts;
    } else {
        const auto shifted = nextTarget << shifts;
        if ((shifted >> shifts) != nextTarget) {
            nextTarget = powLimit;
        } else {
            nextTarget = shifted;
        }
    }

    if (nextTarget == 0) {
        nextTarget = arith_uint256(1);
    } else if (nextTarget > powLimit) {
        nextTarget = powLimit;
    }
    return nextTarget;
}

static unsigned int GetNextASERTWorkRequired(const CBlockIndex* pindexLast, const CBlockHeader* pblock, const Consensus::Params& params)
{
    unsigned int nProofOfWorkLimit = UintToArith256(params.powLimit).GetCompact();
    if (params.fPowAllowMinDifficultyBlocks && pblock &&
        pblock->GetBlockTime() > pindexLast->GetBlockTime() + params.nPowTargetSpacing * 2) {
        return nProofOfWorkLimit;
    }

    // Genesis nBits/nTime are the ASERT anchor. Walk pprev so incomplete fuzz
    // indexes cannot trip GetAncestor's pprev assert.
    const CBlockIndex* pindexAnchor = pindexLast;
    while (pindexAnchor->pprev && pindexAnchor->nHeight > 0) {
        pindexAnchor = pindexAnchor->pprev;
    }

    arith_uint256 refTarget;
    refTarget.SetCompact(pindexAnchor->nBits);
    const arith_uint256 powLimit = UintToArith256(params.powLimit);
    if (refTarget == 0 || refTarget > powLimit) {
        refTarget = powLimit;
    }

    const int64_t nTimeDiff = pindexLast->GetBlockTime() - pindexAnchor->GetBlockTime();
    const int64_t nHeightDiff = static_cast<int64_t>(pindexLast->nHeight) - pindexAnchor->nHeight;
    return CalculateASERT(refTarget, params.nPowTargetSpacing, nTimeDiff, std::max<int64_t>(nHeightDiff, 0),
                          powLimit, params.nASERTHalfLife)
        .GetCompact();
}

unsigned int GetNextWorkRequired(const CBlockIndex* pindexLast, const CBlockHeader *pblock, const Consensus::Params& params)
{
    assert(pindexLast != nullptr);
    if (params.nASERTHalfLife > 0) {
        return GetNextASERTWorkRequired(pindexLast, pblock, params);
    }

    unsigned int nProofOfWorkLimit = UintToArith256(params.powLimit).GetCompact();

    // Only change once per difficulty adjustment interval
    if ((pindexLast->nHeight+1) % params.DifficultyAdjustmentInterval() != 0)
    {
        if (params.fPowAllowMinDifficultyBlocks)
        {
            // Special difficulty rule for testnet:
            // If the new block's timestamp is more than 2* 10 minutes
            // then it MUST be a min-difficulty block.
            if (pblock->GetBlockTime() > pindexLast->GetBlockTime() + params.nPowTargetSpacing*2)
                return nProofOfWorkLimit;
            else
            {
                // Return the last non-special-min-difficulty-rules-block
                const CBlockIndex* pindex = pindexLast;
                while (pindex->pprev && pindex->nHeight % params.DifficultyAdjustmentInterval() != 0 && pindex->nBits == nProofOfWorkLimit)
                    pindex = pindex->pprev;
                return pindex->nBits;
            }
        }
        return pindexLast->nBits;
    }

    // Go back by what we want to be 14 days worth of blocks
    int nHeightFirst = pindexLast->nHeight - (params.DifficultyAdjustmentInterval()-1);
    assert(nHeightFirst >= 0);
    const CBlockIndex* pindexFirst = pindexLast->GetAncestor(nHeightFirst);
    assert(pindexFirst);

    return CalculateNextWorkRequired(pindexLast, pindexFirst->GetBlockTime(), params);
}

unsigned int CalculateNextWorkRequired(const CBlockIndex* pindexLast, int64_t nFirstBlockTime, const Consensus::Params& params)
{
    if (params.fPowNoRetargeting)
        return pindexLast->nBits;

    // Limit adjustment step
    int64_t nActualTimespan = pindexLast->GetBlockTime() - nFirstBlockTime;
    if (nActualTimespan < params.nPowTargetTimespan/4)
        nActualTimespan = params.nPowTargetTimespan/4;
    if (nActualTimespan > params.nPowTargetTimespan*4)
        nActualTimespan = params.nPowTargetTimespan*4;

    // Retarget
    const arith_uint256 bnPowLimit = UintToArith256(params.powLimit);
    arith_uint256 bnNew;

    // Special difficulty rule for Testnet4
    if (params.enforce_BIP94) {
        // Here we use the first block of the difficulty period. This way
        // the real difficulty is always preserved in the first block as
        // it is not allowed to use the min-difficulty exception.
        int nHeightFirst = pindexLast->nHeight - (params.DifficultyAdjustmentInterval()-1);
        const CBlockIndex* pindexFirst = pindexLast->GetAncestor(nHeightFirst);
        bnNew.SetCompact(pindexFirst->nBits);
    } else {
        bnNew.SetCompact(pindexLast->nBits);
    }

    bnNew *= nActualTimespan;
    bnNew /= params.nPowTargetTimespan;

    if (bnNew > bnPowLimit)
        bnNew = bnPowLimit;

    return bnNew.GetCompact();
}

// Check that on difficulty adjustments, the new difficulty does not increase
// or decrease beyond the permitted limits.
bool PermittedDifficultyTransition(const Consensus::Params& params, int64_t height, uint32_t old_nbits, uint32_t new_nbits)
{
    if (params.fPowAllowMinDifficultyBlocks) return true;
    if (params.nASERTHalfLife > 0) {
        return DeriveTarget(new_nbits, params.powLimit).has_value();
    }

    if (height % params.DifficultyAdjustmentInterval() == 0) {
        int64_t smallest_timespan = params.nPowTargetTimespan/4;
        int64_t largest_timespan = params.nPowTargetTimespan*4;

        const arith_uint256 pow_limit = UintToArith256(params.powLimit);
        arith_uint256 observed_new_target;
        observed_new_target.SetCompact(new_nbits);

        // Calculate the largest difficulty value possible:
        arith_uint256 largest_difficulty_target;
        largest_difficulty_target.SetCompact(old_nbits);
        largest_difficulty_target *= largest_timespan;
        largest_difficulty_target /= params.nPowTargetTimespan;

        if (largest_difficulty_target > pow_limit) {
            largest_difficulty_target = pow_limit;
        }

        // Round and then compare this new calculated value to what is
        // observed.
        arith_uint256 maximum_new_target;
        maximum_new_target.SetCompact(largest_difficulty_target.GetCompact());
        if (maximum_new_target < observed_new_target) return false;

        // Calculate the smallest difficulty value possible:
        arith_uint256 smallest_difficulty_target;
        smallest_difficulty_target.SetCompact(old_nbits);
        smallest_difficulty_target *= smallest_timespan;
        smallest_difficulty_target /= params.nPowTargetTimespan;

        if (smallest_difficulty_target > pow_limit) {
            smallest_difficulty_target = pow_limit;
        }

        // Round and then compare this new calculated value to what is
        // observed.
        arith_uint256 minimum_new_target;
        minimum_new_target.SetCompact(smallest_difficulty_target.GetCompact());
        if (minimum_new_target > observed_new_target) return false;
    } else if (old_nbits != new_nbits) {
        return false;
    }
    return true;
}

// Bypasses the actual proof of work check during fuzz testing with a simplified validation checking whether
// the most significant bit of the last byte of the hash is set.
uint256 GetPoWHash(const CBlockHeader& header, const Consensus::Params& params)
{
    if (!params.fPowUseRandomX) {
        return header.GetHash();
    }
    DataStream ss{};
    ss << header;
    uint256 hash;
    RandomXPoW(UCharCast(ss.data()), ss.size(), hash.data());
    return hash;
}

bool CheckProofOfWork(const CBlockHeader& header, const Consensus::Params& params)
{
    return CheckProofOfWork(GetPoWHash(header, params), header.nBits, params);
}

bool CheckProofOfWork(uint256 hash, unsigned int nBits, const Consensus::Params& params)
{
    if (EnableFuzzDeterminism()) return (hash.data()[31] & 0x80) == 0;
    return CheckProofOfWorkImpl(hash, nBits, params);
}

std::optional<arith_uint256> DeriveTarget(unsigned int nBits, const uint256 pow_limit)
{
    bool fNegative;
    bool fOverflow;
    arith_uint256 bnTarget;

    bnTarget.SetCompact(nBits, &fNegative, &fOverflow);

    // Check range
    if (fNegative || bnTarget == 0 || fOverflow || bnTarget > UintToArith256(pow_limit))
        return {};

    return bnTarget;
}

bool CheckProofOfWorkImpl(uint256 hash, unsigned int nBits, const Consensus::Params& params)
{
    auto bnTarget{DeriveTarget(nBits, params.powLimit)};
    if (!bnTarget) return false;

    if (UintToArith256(hash) > bnTarget)
        return false;

    return true;
}
