import json
import os
import shutil
import subprocess
import toml
import yaml

def write_service_file(service_path, sourceFolder):
    # Write systemd service file
    if not service_path:
        print("Error: 'service' path is not defined in config.json!")
        return

    try:
        with open(service_path, "w") as f:
            if "@" in service_path:
                service_content = f"""
[Unit]
Description=Cosmovisor for imuad node %I
After=network.target

[Service]
User=root
Group=root
EnvironmentFile=-{sourceFolder}/%I/start.env
ExecStart=/bin/bash -c "/usr/bin/cosmovisor --cosmovisor-config {sourceFolder}/%I/cosmovisor/config.toml run start --home {sourceFolder}/%I ${{ADDITIONAL_OPTS}}"
Restart=on-failure
LogRateLimitIntervalSec=0
LogRateLimitBurst=0

[Install]
WantedBy=default.target
"""
            else:
                service_content = f"""
[Unit]
Description=Cosmovisor for imuad node
After=network.target

[Service]
User=root
Group=root
EnvironmentFile=-{sourceFolder}/start.env
ExecStart=/bin/bash -c "/usr/bin/cosmovisor --cosmovisor-config {sourceFolder}/cosmovisor/config.toml run start --home {sourceFolder} ${{ADDITIONAL_OPTS}}"
Restart=on-failure
LogRateLimitIntervalSec=0
LogRateLimitBurst=0

[Install]
WantedBy=default.target
"""

            f.write(service_content.strip() + "\n")
            print(f"Systemd service file written to {service_path}")

    except Exception as e:
        print(f"Error writing service file: {e}")

# 自定义表示器以保留 !!str 标记
# def str_representer(dumper, data):
#     return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='')

# yaml.add_representer(str, str_representer)

# Read the YAML file
def read_yaml(file_path):
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)
    return data

def str_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='')

# Write the YAML file
def write_yaml(file_path, data):
    yaml.add_representer(str, str_representer)
    with open(file_path, "w") as file:
        yaml.dump(data, file, sort_keys=False, default_flow_style=False)

def main():
    config_path = "config.json"
    N = 4
    # Check if config.json exists
    if not os.path.exists(config_path):
        print("Error: config.json not found!")
        return

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in config.json!")
        return

    sourceFolder = config.get("sourceFolder", "")
    if not sourceFolder:
        print("Error: 'sourceFolder' is not defined in config.json!")
        return

    currentDirectory = os.getcwd()
    nodeFolders = ["node1", "node2", "node3", "node4", "Operator1"]
    validators = ["node1", "node2", "node3", "node4"]

    # Copy all node folders to the sourceFolder
    for node in nodeFolders:
        src = os.path.join(currentDirectory, node)
        dst = os.path.join(sourceFolder, node)

        if os.path.exists(src):
            try:
                shutil.copytree(src, dst, dirs_exist_ok=True)  # Avoid errors if folders exist
                print(f"Copied {src} to {dst}")
            except Exception as e:
                print(f"Error copying {src} to {dst}: {e}")
        else:
            print(f"Warning: {src} does not exist, skipping...")
    # show node id for all nodes
    IDS = [
        subprocess.run(
            [
                "imuad",
                "tendermint",
                "show-node-id",
                "--home",
                "{}/{}".format(
                    sourceFolder, node,
                ),
            ],
            capture_output = True,
            check = True,
        ).stdout.decode().strip()
        for node in validators
    ]
    print(IDS)
    IPS = config.get("ips", [])
    P2P_PORTS = config.get("p2pPorts", [])
    RPC_PORTS = config.get("rpcPorts", [])
    GRPC_PORTS = config.get("grpcPorts", [])
    DEBUGGER_PORTS = config.get("debuggerPorts", [])
    JSONPRC_PORTS = config.get("jsonrpcPorts", [])
    ENV_OPTS = config.get("envOpts", "")
    # modify p2p ports in validators config.toml
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
    print(PERSISTENT_PEERS)
    operator_persistent_peers = []
    for i in range(0, 0 + N):
        operator_persistent_peers.append("{}@{}:{}".format(
            IDS[i], IPS[i], P2P_PORTS[i]
        ))
    operator_persistent_peers = ",".join(operator_persistent_peers)
    print(operator_persistent_peers)
    PERSISTENT_PEERS.append(operator_persistent_peers)
    print(PERSISTENT_PEERS)
    
    for i in range(0, N + 1): 
        config_file_path = "{}/config/config.toml".format(sourceFolder + "/" + nodeFolders[i])
        print(f"Changing the IPs and ports to avoid conflicts in {config_file_path}...")
        with open( config_file_path, "r" ) as f:
            data = toml.load( f )
        data[ "rpc" ][ "laddr" ] = "tcp://{}:{}".format(
            IPS[ i ], RPC_PORTS[ i ],
        )
        # data[ "rpc" ][ "pprof_laddr" ] = "{}:{}".format(
        #     IPS[ i ], PPROF_PORTS[ i ],
        # )
        data[ "p2p" ][ "laddr" ] = "tcp://{}:{}".format(
            IPS[ i ], P2P_PORTS[ i ],
        )
        data[ "p2p" ][ "external_address" ] = "tcp://{}:{}".format(
            IPS[ i ], P2P_PORTS[ i ],
        )
        data[ "p2p" ][ "persistent_peers" ] = PERSISTENT_PEERS[ i ]
        with open( config_file_path, "w" ) as file:
            toml.dump( data, file )
    
    for i in range(0, N + 1):
        app_file_path = "{}/config/app.toml".format(sourceFolder + "/" + nodeFolders[i])
        with open( app_file_path, "r" ) as f:
            data = toml.load( f )
        data[ "grpc" ][ "address" ] = "{}:{}".format(
            IPS[ i ], GRPC_PORTS[ i ],
        )
        data['json-rpc' ][ "address" ] = "0.0.0.0:{}".format( JSONPRC_PORTS [ i ] )
        with open( app_file_path, "w" ) as file:
            toml.dump( data, file ) 
    #=================================================================================================
    # set oracle feeder yaml file
    # read oracle feeder yaml file
    for i in range(0, N + 1):
        oracle_feeder_file_path = "{}/config/oracle_feeder.yaml".format(sourceFolder + "/" + nodeFolders[i])
        oracle_feeder_data = read_yaml(oracle_feeder_file_path)
        oracle_feeder_data["sender"]["path"] = "{}/{}/config".format(sourceFolder, nodeFolders[i])
        oracle_feeder_data["imua"]["grpc"] = "{}:{}".format(IPS[i], GRPC_PORTS[i])
        oracle_feeder_data["imua"]["rpc"] = "http://{}:{}".format(IPS[i], RPC_PORTS[i])
        oracle_feeder_data["imua"]["ws"] = "ws://{}:{}/websocket".format(IPS[i], RPC_PORTS[i])
        oracle_feeder_data["debugger"]["grpc"] = ":{}".format(DEBUGGER_PORTS[i])
        print(oracle_feeder_data)
        write_yaml(oracle_feeder_file_path, oracle_feeder_data)
    #=================================================================================================
    # write start.env file
    for i in range(0, N + 1):
        start_env_file_path = "{}/start.env".format(sourceFolder + "/" + nodeFolders[i])
        start_env_enableoracle_file_path = "{}/start_enable_oracle.env".format(sourceFolder + "/" + nodeFolders[i])
        start_env_nooralce_file_path = "{}/start_no_oracle.env".format(sourceFolder + "/" + nodeFolders[i])

        with open(start_env_file_path, "w") as f:
            new_opts = ENV_OPTS [ i ]
            start_env_data = f'ADDITIONAL_OPTS="{new_opts}"'
            f.write(start_env_data)
        with open(start_env_enableoracle_file_path, "w") as f:
            new_opts = ENV_OPTS [ i ]
            start_env_enableoracle_data = f'ADDITIONAL_OPTS="{new_opts}"'
            f.write(start_env_enableoracle_data)  
        with open(start_env_nooralce_file_path, "w") as f:
            new_opts = ENV_OPTS [ i ].replace("--oracle", "")
            start_env_nooracle_data = f'ADDITIONAL_OPTS="{new_opts}"'
            f.write(start_env_nooracle_data)               
    #=================================================================================================
    # set start.env file
    # =================================================================================================
    # service_path = config.get("service", "")
    # write_service_file(service_path, sourceFolder)


if __name__ == "__main__":
    main()