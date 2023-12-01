# Distributed Hash Table (DHT) Project using Chord Algorithm

## Overview

This project is an implementation of a Distributed Hash Table (DHT) using the Chord algorithm. It efficiently distributes and manages data across a network of nodes, ensuring availability and fault tolerance in a decentralized way. The system handles dynamic network changes, allowing nodes to join and leave without disruption.

## Getting Started

### Setting Up the Environment

Before launching nodes and the client, create and activate the virtual environment (install necessary packages):

```
virtualenv -p python3.8 env
python -m pip install grpcio
python -m, pip install grpcio-tools
source env/bin/activate
```

### Launching a Node

To launch the initial node in the network:
`python node.py 127.0.0.1:9092`

This starts a node at IP address 127.0.0.1 and port 9092.

### Joining a New Node

To add a new node to the DHT network:
`python node.py 127.0.0.1:9094 127.0.0.1:9092`

This initiates a new node on IP address 127.0.0.1 and port 9094, connecting to the node on port 9092.

### Launching the Client

To interact with the DHT network:

`python client.py`


### Client Commands

- Connect the client to a bootstrap node：`bootstrap_server <ip:port>`
- Add Key-Value Pair: `set <key> <value>`
- Delete Key-Value Pair: `del <key> <value>`
- Retrieve Value by Key: `get <key>`
- Exit a node from the system: `stop`

Replace `<key>` and `<value>` with the desired key and value for your operations.


