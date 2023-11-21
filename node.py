import time

import chord_pb2 as pb2
import chord_pb2_grpc as pb2_grpc
import util
import sys
import rpc_controller

class Node(pb2_grpc.ChordServicer):
    def __init__(self, addr, bootstrap):
        hid = util.get_hash(addr)
        self.node = pb2.Node(id=hid, addr=addr)
        self.predecessor = None
        self.successor = None
        self.finger_table = self.create_finger_table()
        self.storage = {}
        self.rpcServer = rpc_controller.RpcServer(addr)
        self.rpcClient = rpc_controller.RpcClient()

        pb2_grpc.add_ChordServicer_to_server(self, self.rpcServer.server)
        self.rpcServer.start()
        self.join(bootstrap)

    def create_finger_table(self):
        finger_table = []
        m = util.m
        for i in range(util.m):
            index = (self.node.id + pow(2, i)) % pow(2, m)
            finger_table.append(([index, self.node]))
        return finger_table

    def join(self, bootstrap):
        if bootstrap is None:
            self.successor = self.node
            return
        succ = self.find_successor_rpc(bootstrap, self.node.id)
        self.successor = succ

    def find_successor(self, hid):
        pred = self.find_predecessor(hid)
        succ = self.get_successor_rpc(pred)
        return succ

    def find_predecessor(self, hid):
        curr = self.node
        while not util.between_include_right(hid, curr.id, curr.successor.id):
            curr = self.closest_preceding_finger_rpc(curr, hid)
        return curr

    def closest_preceding_finger_rpc(self, node, hid):
        return self.rpcClient.closest_preceding_finger(node, hid)

    def get_successor_rpc(self, node):
        return self.rpcClient.get_successor(node)

    def find_successor_rpc(self, node, hid):
        return self.rpcClient.find_successor(node, hid)

    def GetPredecessor(self, request, context):
        return self.predecessor

    def GetSuccessor(self, request, context):
        return self.successor

    def FindSuccessor(self, request, context):
        hid = request.ID
        return self.find_successor(hid)

    def ClosestPrecedingFinger(self, request, context):
        hid = request.ID
        for i in range(len(self.finger_table) - 1, -1, -1):
            if util.between(self.finger_table[i][1].id, self.node.id, hid):
                return self.finger_table[i][1]
        return self.node

if __name__ == '__main__':
    node2 = Node(sys.argv[1], None)
    try:
        while True:
            pass  # or any other blocking operation
    except KeyboardInterrupt:
        print("Program terminated by user (Ctrl+C)")
