#!/bin/bash

# please note this script will automatically update the genesis_time in the genesis file
GENESIS=genesis_v7_enableoracle.json
TMP_GENESIS=genesis_v7_enableoracle_tmp.json

# Get the current UTC time
current_utc_time=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Print the current UTC time
echo "Current UTC time: $current_utc_time"

# Update the genesis_time in the JSON file
jq --arg time "$current_utc_time" '.genesis_time=$time' "$GENESIS" >"$TMP_GENESIS" && mv "$TMP_GENESIS" "$GENESIS"

for i in {1..4}; do
  cp genesis_v7_enableoracle.json node$i/config/genesis.json
done
