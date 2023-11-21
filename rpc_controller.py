import grpc
from concurrent import futures
import threading
import chord_pb2 as pb2
import chord_pb2_grpc as pb2_grpc

class RpcServer:
    def __init__(self, addr):
        self.addr = addr
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    def start(self):
        thread1 = threading.Thread(target=self._start)
        thread1.start()

    def _start(self):
        self.server.add_insecure_port(self.addr)
        self.server.start()

class RpcClient:
    def __init__(self):
        self.channel = None

    def get_connect(self, addr):
        self.channel = grpc.insecure_channel(addr)
        stub = pb2_grpc.ChordStub(self.channel)
        return stub

    def get_successor(self, node):
        client = self.get_connect(node.addr)
        return client.GetSuccessor(pb2.ER())

    def get_predecessor(self, node):
        client = self.get_connect(node.addr)
        return client.GetPredecessor(pb2.ER())

    def find_successor(self, node, hid):
        client = self.get_connect(node.addr)
        return client.FindSuccessor(pb2.ID(id=hid))

    def closest_preceding_finger(self, node, hid):
        client = self.get_connect(node.addr)
        return client.ClosestPrecedingFinger(pb2.ID(id=hid))