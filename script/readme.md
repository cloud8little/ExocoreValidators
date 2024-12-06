# Exocore Validators

## Overview

The Exocore Validators repository provides a setup for four default validators, configured with default deposit and delegation settings.

## Quick Start

### Steps

#### Four Validators on the Same VM

1. Clone the repository:
    ```sh
    git clone https://github.com/cloud8little/ExocoreValidators.git
    ```

2. Ensure the folder path `/root/testnetV6` exists:
    ```sh
    cd testnetV6
    cp -r <DIR>/ExocoreValidators/node* ./
    ```

3. Create a system service at `/etc/systemd/system/testnet@.service`:
    ```ini
    [Unit]
    Description=Exocored node %I
    After=network.target

    [Service]
    Type=simple
    Environment=HOME=/root
    WorkingDirectory=/root/testnetV6
    EnvironmentFile=-/root/testnetV6/node%I/start.env
    ExecStart=/usr/bin/exocored start --home ./node%I --minimum-gas-prices 0.0001hua $ADDITIONAL_OPTS
    Restart=on-failure

    [Install]
    WantedBy=multi-user.target
    ```

4. Start the four services:
    ```sh
    systemctl start testnet@1.service
    systemctl start testnet@2.service
    systemctl start testnet@3.service
    systemctl start testnet@4.service
    ```

#### Four Validators on Different VMs

1. For VM1 to VM4, copy `node1` to `node4` to different VMs under `/root/testnetV6`.

2. Update `node1~4/config/config.toml`:
    ```toml
    persistent_peers = "0de015146582aa1a300366c8c6491323a631a17a@<IP_VM2>:29999,1c5133f1be821199d23b6106b9d9b58b8407c96d@<IP_VM3>:29998,60c5ad014f750f243afdf28a4b2412b48457bcab@<IP_VM4>:29997"
    ```

3. Replace `<IP_VM1>` with the IP address of VM1.
4. Replace `<IP_VM2>` with the IP address of VM2.
5. Replace `<IP_VM3>` with the IP address of VM3.
6. Replace `<IP_VM4>` with the IP address of VM4.
7. Start the four services on each VM:
    ```sh
    systemctl start testnet@1.service
    systemctl start testnet@2.service
    systemctl start testnet@3.service
    systemctl start testnet@4.service
    ```


## License

This project is licensed under the MIT License.