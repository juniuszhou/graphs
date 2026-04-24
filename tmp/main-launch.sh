#!/usr/bin/env bash
target/release/node-subtensor --base-path target/clone --chain target/mainnet-clone-chainspec.json --database paritydb --force-authoring --alice --validator --unsafe-force-node-key-generation --rpc-cors=all --allow-private-ipv4 --unsafe-rpc-external

