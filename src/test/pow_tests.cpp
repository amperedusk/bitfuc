// Copyright (c) 2015-present The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <arith_uint256.h>
#include <chain.h>
#include <chainparams.h>
#include <pow.h>
#include <test/util/random.h>
#include <test/util/common.h>
#include <test/util/setup_common.h>
#include <util/chaintype.h>

#include <boost/test/unit_test.hpp>

BOOST_FIXTURE_TEST_SUITE(pow_tests, BasicTestingSetup)

/** Bitcoin-style DAA, independent of BITFUC public-net ASERT / 2-minute params. */
static Consensus::Params ClassicBitcoinDAA()
{
    Consensus::Params p;
    p.nPowTargetSpacing = 10 * 60;
    p.nPowTargetTimespan = 14 * 24 * 60 * 60;
    p.fPowAllowMinDifficultyBlocks = false;
    p.fPowNoRetargeting = false;
    p.nASERTHalfLife = 0;
    p.powLimit = uint256{"00000000ffffffffffffffffffffffffffffffffffffffffffffffffffffffff"};
    return p;
}

/* Test calculation of next difficulty target with no constraints applying */
BOOST_AUTO_TEST_CASE(get_next_work)
{
    const auto consensus = ClassicBitcoinDAA();
    int64_t nLastRetargetTime = 1261130161; // Block #30240
    CBlockIndex pindexLast;
    pindexLast.nHeight = 32255;
    pindexLast.nTime = 1262152739;  // Block #32255
    pindexLast.nBits = 0x1d00ffff;

    // Here (and below): expected_nbits is calculated in
    // CalculateNextWorkRequired(); redoing the calculation here would be just
    // reimplementing the same code that is written in pow.cpp. Rather than
    // copy that code, we just hardcode the expected result.
    unsigned int expected_nbits = 0x1d00d86aU;
    BOOST_CHECK_EQUAL(CalculateNextWorkRequired(&pindexLast, nLastRetargetTime, consensus), expected_nbits);
    BOOST_CHECK(PermittedDifficultyTransition(consensus, pindexLast.nHeight+1, pindexLast.nBits, expected_nbits));
}

/* Test the constraint on the upper bound for next work */
BOOST_AUTO_TEST_CASE(get_next_work_pow_limit)
{
    const auto consensus = ClassicBitcoinDAA();
    int64_t nLastRetargetTime = 1231006505; // Block #0
    CBlockIndex pindexLast;
    pindexLast.nHeight = 2015;
    pindexLast.nTime = 1233061996;  // Block #2015
    pindexLast.nBits = 0x1d00ffff;
    unsigned int expected_nbits = 0x1d00ffffU;
    BOOST_CHECK_EQUAL(CalculateNextWorkRequired(&pindexLast, nLastRetargetTime, consensus), expected_nbits);
    BOOST_CHECK(PermittedDifficultyTransition(consensus, pindexLast.nHeight+1, pindexLast.nBits, expected_nbits));
}

/* Test the constraint on the lower bound for actual time taken */
BOOST_AUTO_TEST_CASE(get_next_work_lower_limit_actual)
{
    const auto consensus = ClassicBitcoinDAA();
    int64_t nLastRetargetTime = 1279008237; // Block #66528
    CBlockIndex pindexLast;
    pindexLast.nHeight = 68543;
    pindexLast.nTime = 1279297671;  // Block #68543
    pindexLast.nBits = 0x1c05a3f4;
    unsigned int expected_nbits = 0x1c0168fdU;
    BOOST_CHECK_EQUAL(CalculateNextWorkRequired(&pindexLast, nLastRetargetTime, consensus), expected_nbits);
    BOOST_CHECK(PermittedDifficultyTransition(consensus, pindexLast.nHeight+1, pindexLast.nBits, expected_nbits));
    // Test that reducing nbits further would not be a PermittedDifficultyTransition.
    unsigned int invalid_nbits = expected_nbits-1;
    BOOST_CHECK(!PermittedDifficultyTransition(consensus, pindexLast.nHeight+1, pindexLast.nBits, invalid_nbits));
}

/* Test the constraint on the upper bound for actual time taken */
BOOST_AUTO_TEST_CASE(get_next_work_upper_limit_actual)
{
    const auto consensus = ClassicBitcoinDAA();
    int64_t nLastRetargetTime = 1263163443; // NOTE: Not an actual block time
    CBlockIndex pindexLast;
    pindexLast.nHeight = 46367;
    pindexLast.nTime = 1269211443;  // Block #46367
    pindexLast.nBits = 0x1c387f6f;
    unsigned int expected_nbits = 0x1d00e1fdU;
    BOOST_CHECK_EQUAL(CalculateNextWorkRequired(&pindexLast, nLastRetargetTime, consensus), expected_nbits);
    BOOST_CHECK(PermittedDifficultyTransition(consensus, pindexLast.nHeight+1, pindexLast.nBits, expected_nbits));
    // Test that increasing nbits further would not be a PermittedDifficultyTransition.
    unsigned int invalid_nbits = expected_nbits+1;
    BOOST_CHECK(!PermittedDifficultyTransition(consensus, pindexLast.nHeight+1, pindexLast.nBits, invalid_nbits));
}

BOOST_AUTO_TEST_CASE(CheckProofOfWork_test_negative_target)
{
    const auto consensus = CreateChainParams(*m_node.args, ChainType::MAIN)->GetConsensus();
    uint256 hash;
    unsigned int nBits;
    nBits = UintToArith256(consensus.powLimit).GetCompact(true);
    hash = uint256{1};
    BOOST_CHECK(!CheckProofOfWork(hash, nBits, consensus));
}

BOOST_AUTO_TEST_CASE(CheckProofOfWork_test_overflow_target)
{
    const auto consensus = CreateChainParams(*m_node.args, ChainType::MAIN)->GetConsensus();
    uint256 hash;
    unsigned int nBits{~0x00800000U};
    hash = uint256{1};
    BOOST_CHECK(!CheckProofOfWork(hash, nBits, consensus));
}

BOOST_AUTO_TEST_CASE(CheckProofOfWork_test_too_easy_target)
{
    const auto consensus = CreateChainParams(*m_node.args, ChainType::MAIN)->GetConsensus();
    uint256 hash;
    unsigned int nBits;
    arith_uint256 nBits_arith = UintToArith256(consensus.powLimit);
    nBits_arith *= 2;
    nBits = nBits_arith.GetCompact();
    hash = uint256{1};
    BOOST_CHECK(!CheckProofOfWork(hash, nBits, consensus));
}

BOOST_AUTO_TEST_CASE(CheckProofOfWork_test_biger_hash_than_target)
{
    const auto consensus = CreateChainParams(*m_node.args, ChainType::MAIN)->GetConsensus();
    uint256 hash;
    unsigned int nBits;
    arith_uint256 hash_arith = UintToArith256(consensus.powLimit);
    nBits = hash_arith.GetCompact();
    hash_arith *= 2; // hash > nBits
    hash = ArithToUint256(hash_arith);
    BOOST_CHECK(!CheckProofOfWork(hash, nBits, consensus));
}

BOOST_AUTO_TEST_CASE(CheckProofOfWork_test_zero_target)
{
    const auto consensus = CreateChainParams(*m_node.args, ChainType::MAIN)->GetConsensus();
    uint256 hash;
    unsigned int nBits;
    arith_uint256 hash_arith{0};
    nBits = hash_arith.GetCompact();
    hash = ArithToUint256(hash_arith);
    BOOST_CHECK(!CheckProofOfWork(hash, nBits, consensus));
}

BOOST_AUTO_TEST_CASE(GetBlockProofEquivalentTime_test)
{
    const auto consensus = ClassicBitcoinDAA();
    std::vector<CBlockIndex> blocks(10000);
    for (int i = 0; i < 10000; i++) {
        blocks[i].pprev = i ? &blocks[i - 1] : nullptr;
        blocks[i].nHeight = i;
        blocks[i].nTime = 1269211443 + i * consensus.nPowTargetSpacing;
        blocks[i].nBits = 0x207fffff; /* target 0x7fffff000... */
        blocks[i].nChainWork = i ? blocks[i - 1].nChainWork + GetBlockProof(blocks[i - 1]) : arith_uint256(0);
    }

    for (int j = 0; j < 1000; j++) {
        CBlockIndex *p1 = &blocks[m_rng.randrange(10000)];
        CBlockIndex *p2 = &blocks[m_rng.randrange(10000)];
        CBlockIndex *p3 = &blocks[m_rng.randrange(10000)];

        int64_t tdiff = GetBlockProofEquivalentTime(*p1, *p2, *p3, consensus);
        BOOST_CHECK_EQUAL(tdiff, p1->GetBlockTime() - p2->GetBlockTime());
    }
}

BOOST_AUTO_TEST_CASE(bitfuc_asert_retargets)
{
    const auto consensus = CreateChainParams(*m_node.args, ChainType::MAIN)->GetConsensus();
    BOOST_CHECK_GT(consensus.nASERTHalfLife, 0);
    BOOST_CHECK_EQUAL(CreateChainParams(*m_node.args, ChainType::REGTEST)->GetConsensus().nASERTHalfLife, 0);

    CBlockIndex genesis;
    genesis.nHeight = 0;
    genesis.nTime = 1'700'000'000;
    genesis.nBits = UintToArith256(consensus.powLimit).GetCompact();
    genesis.pprev = nullptr;

    CBlockIndex on_time;
    on_time.nHeight = 1;
    on_time.nTime = genesis.nTime + consensus.nPowTargetSpacing;
    on_time.nBits = genesis.nBits;
    on_time.pprev = &genesis;

    CBlockIndex too_fast;
    too_fast.nHeight = 1;
    too_fast.nTime = genesis.nTime + 1;
    too_fast.nBits = genesis.nBits;
    too_fast.pprev = &genesis;

    CBlockIndex too_slow;
    too_slow.nHeight = 1;
    too_slow.nTime = genesis.nTime + consensus.nPowTargetSpacing * 100;
    too_slow.nBits = genesis.nBits;
    too_slow.pprev = &genesis;

    CBlockHeader next;
    next.nTime = genesis.nTime + consensus.nPowTargetSpacing * 2;

    arith_uint256 t_on, t_fast, t_slow;
    t_on.SetCompact(GetNextWorkRequired(&on_time, &next, consensus));
    t_fast.SetCompact(GetNextWorkRequired(&too_fast, &next, consensus));
    t_slow.SetCompact(GetNextWorkRequired(&too_slow, &next, consensus));
    BOOST_CHECK(t_on > 0);
    BOOST_CHECK(t_fast <= t_on);
    BOOST_CHECK(t_slow >= t_on);
    BOOST_CHECK(DeriveTarget(t_on.GetCompact(), consensus.powLimit).has_value());
    const auto pow_bits = UintToArith256(consensus.powLimit).bits();
    arith_uint256 t_from_genesis;
    t_from_genesis.SetCompact(GetNextWorkRequired(&genesis, &next, consensus));
    BOOST_CHECK_GE(t_from_genesis.bits(), pow_bits - 1);
    BOOST_CHECK_GE(t_on.bits(), pow_bits - 1);
}

/**
 * Genesis-anchored ASERT could not raise difficulty on bitfuc-main, because
 * genesis nTime predates the first mined block by a year and the resulting
 * block deficit pinned the target to powLimit. Past nASERTForkHeight the
 * anchor moves to the last pre-fork block and the floor tightens.
 */
BOOST_AUTO_TEST_CASE(bitfuc_asert_refork_tightens_target)
{
    const auto consensus = CreateChainParams(*m_node.args, ChainType::MAIN)->GetConsensus();
    BOOST_CHECK_GT(consensus.nASERTForkHeight, 0);
    BOOST_CHECK(!consensus.powLimitPostFork.IsNull());

    const arith_uint256 old_limit = UintToArith256(consensus.powLimit);
    const arith_uint256 new_limit = UintToArith256(consensus.powLimitPostFork);
    // The fork is only meaningful if the new floor actually costs more work.
    BOOST_CHECK(new_limit < old_limit);
    BOOST_CHECK_EQUAL(consensus.PowLimitAtHeight(consensus.nASERTForkHeight - 1), consensus.powLimit);
    BOOST_CHECK_EQUAL(consensus.PowLimitAtHeight(consensus.nASERTForkHeight), consensus.powLimitPostFork);

    // Reproduce the bug's shape: genesis a year before the chain moved, then
    // blocks arriving far faster than the two-minute target.
    const int64_t genesis_time = 1'757'948'400;
    const int64_t launch_time = genesis_time + 365 * 24 * 60 * 60;

    std::vector<std::unique_ptr<CBlockIndex>> chain;
    CBlockIndex* prev = nullptr;
    const int last_height = consensus.nASERTForkHeight + 400;
    for (int height = 0; height <= last_height; ++height) {
        auto& index = *chain.emplace_back(std::make_unique<CBlockIndex>());
        index.nHeight = height;
        index.pprev = prev;
        // One second per block: hopelessly ahead of a 120-second target.
        index.nTime = height == 0 ? genesis_time : launch_time + height;
        index.nBits = prev ? GetNextWorkRequired(prev, nullptr, consensus)
                           : old_limit.GetCompact();
        index.BuildSkip();
        prev = &index;
    }

    // Compact encoding truncates the mantissa, so compare against what a
    // floor actually round-trips to rather than the raw uint256.
    arith_uint256 old_floor, new_floor;
    old_floor.SetCompact(old_limit.GetCompact());
    new_floor.SetCompact(new_limit.GetCompact());

    // Below the fork the old rule still applies, so difficulty never left the
    // genesis floor. This is the behaviour the existing chain was built under.
    arith_uint256 pre_fork;
    pre_fork.SetCompact(chain.at(consensus.nASERTForkHeight - 1)->nBits);
    BOOST_CHECK_EQUAL(pre_fork, old_floor);

    // At the fork the target drops to the new floor (a hair under it, since
    // ASERT already sees the first block as early), and keeps falling while
    // blocks stay fast.
    arith_uint256 at_fork, after_fork;
    at_fork.SetCompact(chain.at(consensus.nASERTForkHeight)->nBits);
    after_fork.SetCompact(chain.at(last_height)->nBits);
    BOOST_CHECK(at_fork <= new_floor);
    BOOST_CHECK(at_fork > new_floor / 2);
    BOOST_CHECK(after_fork < at_fork);
    // The whole point: the fork must be a real difficulty increase.
    BOOST_CHECK(at_fork < old_floor);

    // The floor is a ceiling on the target: fast blocks may go below it, but
    // nothing pushes back above it once the fork is active.
    for (int height = consensus.nASERTForkHeight; height <= last_height; ++height) {
        arith_uint256 target;
        target.SetCompact(chain.at(height)->nBits);
        BOOST_CHECK(target <= new_floor);
    }
}

void sanity_check_chainparams(const ArgsManager& args, ChainType chain_type)
{
    const auto chainParams = CreateChainParams(args, chain_type);
    const auto consensus = chainParams->GetConsensus();

    // hash genesis is correct
    BOOST_CHECK_EQUAL(consensus.hashGenesisBlock, chainParams->GenesisBlock().GetHash());

    // target timespan is an even multiple of spacing
    BOOST_CHECK_EQUAL(consensus.nPowTargetTimespan % consensus.nPowTargetSpacing, 0);

    // genesis nBits is positive, doesn't overflow and is lower than powLimit
    arith_uint256 pow_compact;
    bool neg, over;
    pow_compact.SetCompact(chainParams->GenesisBlock().nBits, &neg, &over);
    BOOST_CHECK(!neg && pow_compact != 0);
    BOOST_CHECK(!over);
    BOOST_CHECK(UintToArith256(consensus.powLimit) >= pow_compact);

    // check max target * 4*nPowTargetTimespan doesn't overflow -- see pow.cpp:CalculateNextWorkRequired()
    if (!consensus.fPowNoRetargeting && consensus.nASERTHalfLife == 0) {
        arith_uint256 targ_max{UintToArith256(uint256{"ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"})};
        targ_max /= consensus.nPowTargetTimespan*4;
        BOOST_CHECK(UintToArith256(consensus.powLimit) < targ_max);
    }
}

BOOST_AUTO_TEST_CASE(ChainParams_MAIN_sanity)
{
    sanity_check_chainparams(*m_node.args, ChainType::MAIN);
}

BOOST_AUTO_TEST_CASE(ChainParams_REGTEST_sanity)
{
    sanity_check_chainparams(*m_node.args, ChainType::REGTEST);
}

BOOST_AUTO_TEST_CASE(ChainParams_TESTNET_sanity)
{
    sanity_check_chainparams(*m_node.args, ChainType::TESTNET);
}

BOOST_AUTO_TEST_CASE(ChainParams_TESTNET4_sanity)
{
    sanity_check_chainparams(*m_node.args, ChainType::TESTNET4);
}

BOOST_AUTO_TEST_CASE(ChainParams_SIGNET_sanity)
{
    sanity_check_chainparams(*m_node.args, ChainType::SIGNET);
}

BOOST_AUTO_TEST_SUITE_END()
