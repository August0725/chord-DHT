import time

import chord_pb2 as pb2
import chord_pb2_grpc as pb2_grpc
import util
import sys
import rpc_controller
import threading
import storage

class Node(pb2_grpc.ChordServicer):
    def __init__(self, addr, bootstrap):
        self.node = new_inner_node(addr)
        self.predecessor = None
        self.successor = None
        self.pointer_lock = threading.Lock()
        self.finger_table = self.create_finger_table()
        self.storage = storage.Storage()
        self.rpc_server = rpc_controller.RpcServer(addr)
        self.rpc_client = rpc_controller.RpcClient()
        self.stop_event = threading.Event()

        pb2_grpc.add_ChordServicer_to_server(self, self.rpc_server.server)
        self.rpc_server.start()
        self.join(bootstrap)

        if not self.join(new_inner_node(bootstrap)):
            self.rpc_server.stop()
            print(f"bootstrap is not accessible")
            return

        stabilization_thread = threading.Thread(target=self.stabilize)
        stabilization_thread.start()

        fix_thread = threading.Thread(target=self.fix_finger)
        fix_thread.start()

        # check_thread = threading.Thread(target=self.check_predecessor())
        # check_thread.start()

        stabilization_thread.join()
        fix_thread.join()
        time.sleep(2)
        # check_thread.join()

    def create_finger_table(self):
        finger_table = []
        m = util.m
        for i in range(util.m):
            index = (self.node.id + pow(2, i)) % pow(2, m)
            finger_table.append(([index, None]))
        return finger_table

    def print_finger_table(self):
        print("finger_table:")
        for index, entry in enumerate(self.finger_table):
            if entry[1] is None:
                print('Index: ', index, " Interval start: ", entry[0], " Successor: ", "None")
            else:
                print('Index: ', index, " Interval start: ", entry[0], " Successor: ", entry[1].id)

    def join(self, bootstrap):
        if bootstrap is None:
            self.successor = self.node
            self.finger_table[0][1] = self.node
            return True
        succ = self.find_successor_rpc(bootstrap, self.node.id)
        if succ is None or succ.id == -1:
            return False
        self.successor = succ
        self.finger_table[0][1] = succ
        return True

    def fix_finger(self):
        next_idx = 0
        while not self.stop_event.is_set():
            next_idx = self._fix_finger(next_idx)
            time.sleep(2)

    def _fix_finger(self, next_idx):
        hid = self.finger_table[next_idx][0]
        succ = self.find_successor(hid)
        if succ is None:
            time.sleep(1)
            return next_idx
        self.finger_table[next_idx][1] = succ
        return (next_idx + 1) % util.m

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
