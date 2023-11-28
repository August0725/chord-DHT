import grpc
import chord_pb2 as pb2
import chord_pb2_grpc as pb2_grpc
import util


class CmdClient:
    # Initialize the client with the server's address.
    def __init__(self, addr):
        self.addr = 'addr'
        self.channel = grpc.insecure_channel(addr)          # Set up a gRPC channel for connecting to the server.
        self.stub = pb2_grpc.ChordStub(self.channel)        # Create a stub to communicate with the Chord gRPC service.

    # Send a set request to the server to store a key-value pair.
    def set(self, k, v):
        self.stub.SetKV(pb2.SetRequest(key=k, value=v))

    # Send a get request to the server to retrieve the value associated with a key.
    def get(self, k):
        return self.stub.GetKV(pb2.GetRequest(key=k))

    # Send a delete request to the server to remove a key-value pair.
    def delete(self, k):
        return self.stub.DeleteKV(pb2.DelRequest(key=k))

    # Send a stop request to the server to terminate its operations.
    def stop(self):
        self.stub.Stop(pb2.ER())


if __name__ == '__main__':
    client = None
    while True:
        # Accept input from the user.
        cmd_line = input('chordClient$ ')
        args = cmd_line.split()
        # Skip empty input.
        if not args:
            continue

        # The first argument is the command.
        cmd = args[0]
        # Process the 'bootstrap_server' command to connect to a server.
        if cmd == "bootstrap_server":
            if len(args) != 2:                   # Validate the parameter count.
                print("Parameter error!")
                continue
            # Initialize the client with the provided server address.
            addr = args[1]
            client = CmdClient(addr)
            print(f"Set bootstrap to {addr}")
            continue
        # Process the 'set' command to store a key-value pair.
        if cmd == "set":
            if len(args) != 3:
                print("Parameter error!")
                continue
            if client is None:
                print("Bootstrap server haven't been setup")
                continue
            client.set(args[1], args[2])
            print(f"Set kv: key={args[1]}(hash={util.get_hash(args[1])}), value={args[2]}")
            continue
        # Process the 'get' command to retrieve a value for a key.
        if cmd == "get":
            if len(args) != 2:
                print("Parameter error!")
                continue
            if client is None:
                print("Bootstrap server haven't been setup")
                continue
            res = client.get(args[1])
            if res.ok:
                print(f"Get kv: key={args[1]}(hash={util.get_hash(args[1])}), value={res.value}")
            else:
                print("Key doesn't exist")
                continue
        # Process the 'del' command to delete a key-value pair.
        if cmd == "del":
            if len(args) != 2:
                print("Parameter error!")
                continue
            if client is None:
                print("Bootstrap server haven't been setup")
                continue
            res = client.delete(args[1])
            if res.ok:
                print(f"Delete kv: key={args[1]}(hash={util.get_hash(args[1])}), value={res.value}")
            else:
                print("Key doesn't exist")
                continue
        # Process the 'stop' command to terminate the server operations.
        if cmd == "stop":
            if len(args) != 1:
                print("Parameter error!")
                continue
            if client is None:
                print("Bootstrap server haven't been setup")
                continue
            client.stop()
            break
        # Process the 'quit' command to exit the CLI.
        if cmd == "quit":
            break