#!/bin/bash

exocored start --home ./node1 --minimum-gas-prices 0.0001hua --log_format json --json-rpc.api eth,txpool,personal,net,debug,web3 --api.enable --grpc.enable true --json-rpc.enable true --json-rpc.address 0.0.0.0:9545 --oracle > "out1.log"  2>&1 &
pid1 = $!

for i in {2..4}; do
    echo "Starting node$i..."
    # Start the second process
    exocored start --home ./node$i --minimum-gas-prices 0.0001hua --grpc.enable true --oracle &
    pid$i=$!
done

for i in {1..4}; do
    wait $pid$i
done

echo "All processes have completed."
