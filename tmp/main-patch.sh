#!/usr/bin/env bash
target/release/node-subtensor build-patched-spec --alice --base-path target/mainnet-clone --chain chainspecs/raw_spec_finney.json --bootnodes /dns/bootnode.finney.chain.opentensor.ai/tcp/30333/ws/p2p/12D3KooWRwbMb85RWnT8DSXSYMWQtuDwh4LJzndoRrTDotTR5gDC --output target/mainnet-clone-chainspec.json



