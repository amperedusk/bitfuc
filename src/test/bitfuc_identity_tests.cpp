// Copyright (c) 2026 BITFUC developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <chainparams.h>
#include <chainparamsbase.h>
#include <consensus/amount.h>
#include <kernel/chainparams.h>
#include <key_io.h>
#include <pow.h>
#include <test/util/setup_common.h>
#include <uint256.h>
#include <util/chaintype.h>

#include <boost/test/unit_test.hpp>

#include <array>
#include <string>
#include <string_view>

BOOST_FIXTURE_TEST_SUITE(bitfuc_identity_tests, BasicTestingSetup)

static constexpr std::array<unsigned char, 4> BTC_MAIN_MAGIC{0xf9, 0xbe, 0xb4, 0xd9};
static constexpr std::array<unsigned char, 4> BTC_TEST_MAGIC{0x0b, 0x11, 0x09, 0x07};
static constexpr std::array<unsigned char, 4> BTC_TEST4_MAGIC{0x1c, 0x16, 0x3f, 0x28};
static constexpr std::array<unsigned char, 4> BTC_REGTEST_MAGIC{0xfa, 0xbf, 0xb5, 0xda};

static bool SameMagic(const CChainParams& params, const std::array<unsigned char, 4>& magic)
{
    const auto& start = params.MessageStart();
    return start[0] == magic[0] && start[1] == magic[1] && start[2] == magic[2] && start[3] == magic[3];
}

BOOST_AUTO_TEST_CASE(not_bitcoin_magic_or_ports)
{
    const auto main = CChainParams::Main();
    const auto test = CChainParams::TestNet();
    const auto reg = CChainParams::RegTest({});

    BOOST_CHECK(!SameMagic(*main, BTC_MAIN_MAGIC));
    BOOST_CHECK(!SameMagic(*test, BTC_TEST_MAGIC));
    BOOST_CHECK(!SameMagic(*reg, BTC_REGTEST_MAGIC));
    BOOST_CHECK(!SameMagic(*CChainParams::TestNet4(), BTC_TEST4_MAGIC));

    BOOST_CHECK_NE(main->GetDefaultPort(), 8333);
    BOOST_CHECK_NE(test->GetDefaultPort(), 18333);
    BOOST_CHECK_NE(reg->GetDefaultPort(), 18444);
    BOOST_CHECK_NE(CreateBaseChainParams(ChainType::MAIN)->RPCPort(), 8332);
    BOOST_CHECK_NE(CreateBaseChainParams(ChainType::TESTNET)->RPCPort(), 18332);
    BOOST_CHECK_NE(CreateBaseChainParams(ChainType::REGTEST)->RPCPort(), 18443);
}

BOOST_AUTO_TEST_CASE(not_bitcoin_genesis)
{
    const auto main = CChainParams::Main();
    const auto reg = CChainParams::RegTest({});
    BOOST_CHECK(main->GetConsensus().hashGenesisBlock != uint256{"000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f"});
    BOOST_CHECK(reg->GenesisBlock().hashMerkleRoot != uint256{"4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b"});
    BOOST_CHECK(main->DNSSeeds().empty());
    BOOST_CHECK_EQUAL(main->FixedSeeds().size(), 8); // one BIP155 IPv4 seed (network+len+4+port)
}

BOOST_AUTO_TEST_CASE(not_bitcoin_address_hrp)
{
    BOOST_CHECK_EQUAL(CChainParams::Main()->Bech32HRP(), "fuc");
    BOOST_CHECK_EQUAL(CChainParams::TestNet()->Bech32HRP(), "tfuc");
    BOOST_CHECK_EQUAL(CChainParams::RegTest({})->Bech32HRP(), "fucrt");
    BOOST_CHECK_NE(CChainParams::Main()->Bech32HRP(), "bc");
    BOOST_CHECK_NE(CChainParams::TestNet()->Bech32HRP(), "tb");
    BOOST_CHECK_NE(CChainParams::RegTest({})->Bech32HRP(), "bcrt");
}

BOOST_AUTO_TEST_CASE(chain_name_aliases)
{
    BOOST_CHECK(ChainTypeFromString("bitfuc-regtest") == ChainType::REGTEST);
    BOOST_CHECK(ChainTypeFromString("bitfuc-test") == ChainType::TESTNET);
    BOOST_CHECK(ChainTypeFromString("bitfuc-main") == ChainType::MAIN);
    BOOST_CHECK(ChainTypeFromString("regtest") == ChainType::REGTEST);
}

BOOST_AUTO_TEST_CASE(regtest_address_roundtrip_not_bitcoin)
{
    SelectParams(ChainType::REGTEST);
    const CTxDestination dest{WitnessV0KeyHash{uint160{}}};
    const std::string addr{EncodeDestination(dest)};
    BOOST_CHECK(addr.starts_with("fucrt1"));
    BOOST_CHECK(!addr.starts_with("bcrt1"));
    BOOST_CHECK(!addr.starts_with("bc1"));
    BOOST_CHECK(!addr.starts_with("tb1"));
    const auto decoded{DecodeDestination(addr)};
    BOOST_CHECK(decoded == dest);
}

BOOST_AUTO_TEST_CASE(public_money_policy)
{
    const auto main = CChainParams::Main();
    const auto test = CChainParams::TestNet();
    const auto reg = CChainParams::RegTest({});
    BOOST_CHECK_EQUAL(main->GetConsensus().nMoneyCap, 1'000'000'000 * COIN);
    BOOST_CHECK_EQUAL(main->GetConsensus().nIssuingBlocks, 13'140'000);
    BOOST_CHECK_EQUAL(main->GetConsensus().nPowTargetSpacing, 2 * 60);
    BOOST_CHECK_EQUAL(main->GetConsensus().nFeeBurnPerMille, 20);
    BOOST_CHECK_EQUAL(main->GetConsensus().nASERTHalfLife, 2 * 24 * 60 * 60);
    BOOST_CHECK_EQUAL(test->GetConsensus().nMoneyCap, main->GetConsensus().nMoneyCap);
    BOOST_CHECK_EQUAL(test->GetConsensus().nASERTHalfLife, main->GetConsensus().nASERTHalfLife);
    BOOST_CHECK_EQUAL(reg->GetConsensus().nIssuingBlocks, 0);
    BOOST_CHECK_EQUAL(reg->GetConsensus().nFeeBurnPerMille, 0);
    BOOST_CHECK_EQUAL(reg->GetConsensus().nASERTHalfLife, 0);
    BOOST_CHECK(main->GetConsensus().fPowUseRandomX);
    BOOST_CHECK(test->GetConsensus().fPowUseRandomX);
    BOOST_CHECK(!reg->GetConsensus().fPowUseRandomX);
    BOOST_CHECK(main->GetConsensus().hashGenesisBlock == uint256{"a1d32d9f62f1d1d2f9115a2a36bb35bf15a44b2e603003ca394c159b6758533a"});
    BOOST_CHECK(GetPoWHash(main->GenesisBlock(), main->GetConsensus()) != main->GenesisBlock().GetHash());
    BOOST_CHECK(CheckProofOfWork(main->GenesisBlock(), main->GetConsensus()));
    BOOST_CHECK(CheckProofOfWork(test->GenesisBlock(), test->GetConsensus()));
}

BOOST_AUTO_TEST_SUITE_END()
