#!/usr/bin/env python3

# This script is written in Python and not in bash
# for easier manipulation of the TOML file.

# Assumption: The binary has already been built.

import os
import subprocess
import toml

# localnet params
CHAINID="exocoretestnet_233-6"
KEYRING="test"
MONIKER="localnet"  # irrelevant
LOG_LEVEL="info"

# information
N = 4
KEYS = [
    "node{}".format( i ) for i in range( 1, 1 + N )
]
IPS = [
    "127.0.0.{}".format( i ) for i in range( 1, 1 + N )
]
MNEMONICS = [
    "owner elite knock paper bundle super nose year include scheme innocent already wife banner call festival work effort awkward know evoke radar uphold mom",
    "twist idea sword parent push solution pave slide early invest ask daring pole oblige dragon seed tongue depend style yard cage account asthma payment",
    "that roof sun soldier police useful village loan era merge tomato odor beach surge easy crush poem table seed charge unveil copy coyote knock",
    "mad shed endorse abandon borrow sign vibrant broom crew depart balance holiday truly pilot during coin manage exhibit pave tiger bomb tunnel robust shell",
]
RPC_PORTS = range( 20000, 20000 - N, -1 )
P2P_PORTS = range( 30000, 30000 - N, -1 )
PPROF_PORTS = range( 6060, 6060 + N )
GRPC_PORTS = range( 10000, 10000 + N )
GRPC_WEB_PORTS = range( 12000, 12000 + N )

def main():
    print( "Running `exocored init` to set up {}-node local net...".format( N ) )
    # initialize the nodes
    for i in range( 0, 0 + N ):
        subprocess.run(
            'echo "{}" | exocored init {} --chain-id {} --recover --home {}/.qatest/{}'.format(
                MNEMONICS[ i ], MONIKER, CHAINID, os.environ[ "HOME" ], KEYS[ i ],
            ),
            shell = True, text = True,
            capture_output = True,
            check = True,
        )
    # set up the config
    print( "Setting the persistent peers in `config.toml`..." )
    IDS = [
        subprocess.run(
            [
                "exocored",
                "tendermint",
                "show-node-id",
                "--home",
                "{}/.qatest/node{}".format(
                    os.environ[ "HOME" ], i,
                ),
            ],
            capture_output = True,
            check = True,
        ).stdout.decode().strip()
        for i in range( 1, 1 + N )
    ]
    PERSISTENT_PEERS = []
    for i in range( 0, 0 + N ):
        PERSISTENT_PEERS.append( [] )
        for j in range( 0, 0 + N ):
            if i == j:
                continue
            PERSISTENT_PEERS[ i ].append(
                "{}@{}:{}".format(
                    IDS[ j ],
                    IPS[ j ],
                    P2P_PORTS[ j ],
                )
            )
        PERSISTENT_PEERS[ i ] = ",".join( PERSISTENT_PEERS[ i ] )
    # now start work on the TOML files
    print( "Changing the IPs and ports to avoid conflicts..." )
    for i in range( 0, 0 + N ):
        # directory
        home_dir = "{}/.qatest/{}".format(
            os.environ[ "HOME" ], KEYS[ i ],
        )
        config_file_path = "{}/config/config.toml".format(
            home_dir,
        )
        with open( config_file_path, "r" ) as f:
            data = toml.load( f )
        data[ "log_level" ] = LOG_LEVEL
        data[ "rpc" ][ "laddr" ] = "tcp://{}:{}".format(
            IPS[ i ], RPC_PORTS[ i ],
        )
        data[ "rpc" ][ "pprof_laddr" ] = "{}:{}".format(
            IPS[ i ], PPROF_PORTS[ i ],
        )
        data[ "p2p" ][ "laddr" ] = "tcp://{}:{}".format(
            IPS[ i ], P2P_PORTS[ i ],
        )
        data[ "p2p" ][ "external_address" ] = "tcp://{}:{}".format(
            IPS[ i ], P2P_PORTS[ i ],
        )
        data[ "p2p" ][ "pex" ] = False
        data[ "p2p" ][ "persistent_peers" ] = PERSISTENT_PEERS[ i ]
        # the two flags below are not exposed via tendermint CLI
        # and are the reason why this script is written in Python.
        # allow_duplicate_ip is needed for localnet because of NAT traversal
        # which translates the loopback ip address to 127.0.0.1 instead.
        # all connections therefore (regardless of the source loopback address)
        # appear to arrive from 127.0.0.1, in other words.
        # note that this still does not allow one peer to open multiple connections
        # since filtering by peer id is still enforced.
        data[ "p2p" ][ "allow_duplicate_ip" ] = True
        # allow non-routable addresses (RFC1918 and friends) to be considered
        data[ "p2p" ][ "addr_book_strict" ] = False
        with open( config_file_path, "w" ) as file:
            toml.dump( data, file )
        # grpc and grpc-web bindings
        app_file_path = "{}/config/app.toml".format(
            home_dir,
        )
        with open(app_file_path, "r") as f:
            app_data = toml.load( f )
        app_data[ "grpc" ][ "address" ] = "{}:{}".format(
            IPS[ i ], GRPC_PORTS[ i ],
        )
        app_data[ "grpc-web" ][ "address" ] = "{}:{}".format(
            IPS[ i ], GRPC_WEB_PORTS[ i ],
        )
        with open( app_file_path, "w" ) as file:
            toml.dump( app_data, file )
    for i in range( 0, 0 + N ):
        # directory
        home_dir = "{}/.qatest/{}".format(
            os.environ[ "HOME" ], KEYS[ i ],
        )
        print( "done, run: `exocored start --home {}`".format( home_dir ) )

if __name__ == "__main__":
    main()
