import grpc
import chord_pb2 as pb2
import chord_pb2_grpc as pb2_grpc
import util


class CmdClient:

    def __init__(self, addr):
        self.addr = 'addr'
        self.channel = grpc.insecure_channel(addr)
        self.stub = pb2_grpc.ChordStub(self.channel)

    def set(self, k, v):
        self.stub.SetKV(pb2.SetRequest(key=k, value=v))

    def get(self, k):
        return self.stub.GetKV(pb2.GetRequest(key=k))

    def delete(self, k):
        return self.stub.DeleteKV(pb2.DelRequest(key=k))

    def stop(self):
        self.stub.Stop(pb2.ER())


if __name__ == '__main__':
    client = None
    while True:
        cmd_line = input('chordClient$ ')
        args = cmd_line.split()
        if not args:
            continue

        cmd = args[0]
        if cmd == "bootstrap_server":
            if len(args) != 2:
                print("Parameter error!")
                continue
            addr = args[1]
            client = CmdClient(addr)
            print(f"Set bootstrap to {addr}")
            continue
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
        if cmd == "stop":
            if len(args) != 1:
                print("Parameter error!")
                continue
            if client is None:
                print("Bootstrap server haven't been setup")
                continue
            client.stop()
            break
        if cmd == "quit":
            break