# Reproducible builds

Anyone can compile `bitfucd` from https://github.com/amperedusk/bitfuc and
compare hashes. This is not Guix (Bitcoin Core’s `contrib/guix` still exists
upstream if you want that path). It is the flags this project actually uses.

```bash
git clone https://github.com/amperedusk/bitfuc.git
cd bitfuc
git checkout <commit>
cmake -B build -DENABLE_IPC=OFF -DBUILD_GUI=OFF -DINSTALL_MAN=OFF
cmake --build build --target bitfuc
shasum -a 256 build/bin/bitfucd build/bin/bitfuc-cli   # macOS
# sha256sum build/bin/bitfucd build/bin/bitfuc-cli    # Linux
```

`cmake --build build --target bitfuc` writes `bitfucd` and `bitfuc-cli`.

Linux CI on `main` runs the same cmake line and prints SHA-256 (workflow
`bitfuc-build`). Compare the log to your tree.

## Why the build still says bitcoin

This is a Bitcoin Core derivative, so the inherited build graph keeps upstream
names. Reading `BUILD_DAEMON`, `BUILD_CLI`, `BUILD_BITCOIN_BIN`, or a
`bitcoind` CMake target is expected and is not a sign that you built Bitcoin.
Those are internal option and target names; the programs written to
`build/bin/` are renamed via `OUTPUT_NAME` in `src/CMakeLists.txt`:

| CMake target | Program you run |
| --- | --- |
| `bitcoind` | `bitfucd` |
| `bitcoin-cli` | `bitfuc-cli` |
| `bitcoin` | `bitfuc` |
| `bitcoin-tx` / `bitcoin-util` | `bitfuc-tx` / `bitfuc-util` |

Renaming the upstream targets themselves would churn consensus-adjacent build
files for cosmetics, which is the opposite of the policy in
`docs/architecture.md`.

RandomX is compiled and linked, not aspirational. `src/crypto/CMakeLists.txt`
adds `randomx_pow.cpp` to `bitcoin_crypto`, pulls in
`src/crypto/randomx` as a subdirectory, and links the `randomx` library;
`src/kernel`, `src/test`, and the node link it in turn. Check a finished build
instead of trusting this file:

```bash
nm build/bin/bitfucd | grep -i randomx | head        # symbols present
./build/bin/bitfuc-rxhash --help                     # RandomX helper built
```

`bitfuc-rxhash` exists only because RandomX is linked; if the library were
missing, the build would fail rather than fall back to SHA-256d for public-net
proof of work (`docs/pow.md`).

## Record: darwin-x86_64

C++ at `e8577a841ed7024772866f3d5e1908e31eb7f0ff` (later docs/scripts commits do not change these hashes).

| Field | Value |
| --- | --- |
| OS | macOS 15.2 (24C101), Darwin 24.2.0 x86_64 |
| CMake | 4.4.2 |
| Compiler | Apple clang 17.0.0 (clang-1700.0.13.3) |
| Flags | `-DENABLE_IPC=OFF -DBUILD_GUI=OFF -DINSTALL_MAN=OFF` |
| `bitfucd` SHA-256 | `1b2d8451f8fbd28614dd63a01748044775b82ecd4c8ad8c70024cab09b6d49a7` |
| `bitfuc-cli` SHA-256 | `87a2128ef0ed7d393d2dc1c4c0aa0d1244c1e9d1c39f2b3e4e20d8277cc79351` |

Same commit, different compiler or OS → different hashes. That is expected.
Match OS + compiler before treating a mismatch as a different program.
