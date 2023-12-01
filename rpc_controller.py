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
        self.server.add_insecure_port(self.addr)
        self.server.start()

    def stop(self):
        self.server.stop(5)


class RpcClient:
    def __init__(self):
        self.channel = None

    def get_connect(self, addr):
        self.channel = grpc.insecure_channel(addr)
        stub = pb2_grpc.ChordStub(self.channel)
        return stub

    def get_successor(self, node):
        try:
            conn = self.get_connect(node.addr)
            res = conn.GetSuccessor(pb2.ER())
        except grpc.RpcError as rpc_error:
            print(f"error while getting successor")
            res = None
        return res

    def get_predecessor(self, node):
        try:
            conn = self.get_connect(node.addr)
            res = conn.GetPredecessor(pb2.ER())
        except grpc.RpcError as rpc_error:
            print(f"error while getting predecessor")
            res = None
        return res

    def find_successor(self, node, hid):
        try:
            conn = self.get_connect(node.addr)
            res = conn.FindSuccessor(pb2.ID(id=hid))
        except grpc.RpcError as rpc_error:
            print(f"error while finding successor")
            res = None
        return res

    def closest_preceding_finger(self, node, hid):
        try:
            conn = self.get_connect(node.addr)
            res = conn.ClosestPrecedingFinger(pb2.ID(id=hid))
        except grpc.RpcError as rpc_error:
            print(f"error while getting closest finger")
            res = None
        return res

    def notify(self, node, pred):
        try:
            conn = self.get_connect(node.addr)
            res = conn.Notify(pred)
        except grpc.RpcError as rpc_error:
            print(f"error while notifying successor")
            res = None
        return res

    def get_kv(self, node, key):
        conn = self.get_connect(node.addr)
        return conn.Get(key)

    def set_kv(self, node, kv):
        conn = self.get_connect(node.addr)
        return conn.Set(kv)

    def delete_kv(self, node, key):
        conn = self.get_connect(node.addr)
        return conn.Delete(key)

    def find_kvs(self, node, succ):
        try:
            conn = self.get_connect(succ.addr)
            res = conn.FindKVs(pb2.ID(id=node.id))
        except grpc.RpcError as rpc_error:
            print(f"error while finding kvs")
            res = None
        return res

    def set_successor(self, node, succ):
        conn = self.get_connect(node.addr)
        return conn.SetSuccessor(succ)

    def set_predecessor(self, node, pred):
        conn = self.get_connect(node.addr)
        return conn.SetPredecessor(pred)

    def move_data(self, succ, kvs):
        conn = self.get_connect(succ.addr)
        return conn.MoveData(kvs)

    def check_predecessor(self, node):
        res = True
        try:
            conn = self.get_connect(node.addr)
            conn.CheckPredecessor(pb2.ER())
        except grpc.RpcError as rpc_error:
            print(f"error while checking predecessor")
            res = False
        return res