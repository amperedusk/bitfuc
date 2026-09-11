#!/usr/bin/env python3
# Copyright (c) 2026 BITFUC developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Phase 2 acceptance: 3-node BITFUC regtest mesh.

Mine, send a real transaction, restart, wipe one node's chain, and resync to
the same tip. Addresses must be BITFUC (`fucrt1`), not Bitcoin `bcrt1`.
"""

import shutil

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal

REGTEST_GENESIS = "36dd99e42f28638b0c4c26c43c4c57ec9edba5fb713011b0795df00d067329d5"


class BitfucMeshTest(BitcoinTestFramework):
    def set_test_params(self):
        self.num_nodes = 3
        self.setup_clean_chain = True
        self.extra_args = [["-whitelist=noban,in,out@127.0.0.1"]] * 3

    def skip_test_if_missing_module(self):
        self.skip_if_no_wallet()

    def setup_nodes(self):
        # Do not import Bitcoin-testnet WIF fixtures; prefixes are BITFUC-only.
        self.add_nodes(self.num_nodes, self.extra_args)
        self.start_nodes()
        for n in self.nodes:
            n.createwallet(wallet_name=self.default_wallet_name, load_on_startup=True)

    def run_test(self):
        a, b, c = self.nodes

        self.log.info("BITFUC identity: genesis, user-agent, address HRP")
        info = a.getblockchaininfo()
        assert_equal(info["chain"], "regtest")
        assert_equal(info["blocks"], 0)
        assert_equal(info["bestblockhash"], REGTEST_GENESIS)
        net = a.getnetworkinfo()
        assert net["subversion"].startswith("/Bitfuc:")
        mining_addr = a.getnewaddress()
        assert mining_addr.startswith("fucrt1"), mining_addr

        self.log.info("Mine 101 blocks on A so one coinbase is mature")
        self.generatetoaddress(a, 101, mining_addr)
        assert_equal(a.getblockcount(), 101)
        assert_equal(b.getblockcount(), 101)
        assert_equal(c.getblockcount(), 101)
        tmpl = a.getblocktemplate({"rules": ["segwit"]})
        assert_equal(tmpl["previousblockhash"], a.getbestblockhash())
        assert "bits" in tmpl

        self.log.info("Send a real transaction A -> B and mine it")
        dest = b.getnewaddress()
        assert dest.startswith("fucrt1"), dest
        txid = a.sendtoaddress(dest, 10)
        self.sync_mempools()
        assert txid in b.getrawmempool()
        self.generatetoaddress(a, 1, mining_addr)
        assert_equal(b.getreceivedbyaddress(dest), 10)
        assert_equal(c.getblockcount(), 102)
        tip = a.getbestblockhash()
        assert_equal(b.getbestblockhash(), tip)
        assert_equal(c.getbestblockhash(), tip)

        self.log.info("Restart all three nodes; recover the same tip")
        for i in range(3):
            self.restart_node(i)
        self.connect_nodes(0, 1)
        self.connect_nodes(0, 2)
        self.connect_nodes(1, 2)
        self.sync_all()
        for n in self.nodes:
            assert_equal(n.getbestblockhash(), tip)
            assert_equal(n.getblockcount(), 102)

        self.log.info("Wipe C's blocks/chainstate and resync from A")
        self.stop_node(2)
        shutil.rmtree(c.blocks_path)
        shutil.rmtree(c.chain_path / "chainstate")
        self.start_node(2)
        self.connect_nodes(0, 2)
        self.sync_blocks()
        assert_equal(c.getbestblockhash(), tip)
        assert_equal(c.getblockcount(), 102)
        assert_equal(c.getblockhash(0), REGTEST_GENESIS)


if __name__ == "__main__":
    BitfucMeshTest(__file__).main()
