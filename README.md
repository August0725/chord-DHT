# Distributed Hash Table (DHT) Project using Chord Algorithm

## Overview

This project is an implementation of a Distributed Hash Table (DHT) using the Chord algorithm. It efficiently distributes and manages data across a network of nodes, ensuring availability and fault tolerance in a decentralized way. The system handles dynamic network changes, allowing nodes to join and leave without disruption.

## Getting Started

### Setting Up the Environment

Before launching nodes and the client, activate the virtual environment:

`source env/bin/activate`

### Launching a Node

To launch the initial node in the network:
`python node.py 127.0.0.1:9092`

This starts a node at IP address 127.0.0.1 and port 9092.

### Joining a New Node

To add a new node to the DHT network:
`python node.py 127.0.0.1:9094 127.0.0.1:9092`

This initiates a new node on IP address 127.0.0.1 and port 9999, connecting to the node on port 9092.

### Leaving the Network

To exit a node from the network, type `stop` in the node's command line.

### Launching the Client

To interact with the DHT network:

`python client.py bootstrap_server 127.0.0.1:9094`

Replace `9094` with the appropriate port number of the bootstrap server node.

### Client Commands

- Add Key-Value Pair: set `<key>` `<value>`
- Delete Key-Value Pair: del `<key>` `<value>`
- Retrieve Value by Key: get `<key>`

Replace `<key>` and `<value>` with the desired key and value for your operations.


