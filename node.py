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

    def migrate_data(self):
        res = self.find_kvs_rpc()
        if res is None:
            return
        self.storage.lock.acquire()
        for kv in res.values:
            self.storage.data[kv.key] = kv.value
        self.storage.lock.release()

    def _stabilize(self):
        self.pointer_lock.acquire()
        succ = self.successor
        x = self.get_predecessor_rpc(succ)
        if x is None:
            return
        if x.id != -1 and util.between(x.id, self.node.id, succ.id):
            self.successor = x
            self.finger_table[0][1] = x
        self.pointer_lock.release()
        self.migrate_data()
        self.notify_rpc(self.successor, self.node)

    def stabilize(self):
        while not self.stop_event.is_set():
            # time.sleep(3)
            self._stabilize()
            print(f"self: {self.node.id}, {self.node.addr}")
            print(
                f"successor: {self.successor.id if self.successor else None}, {self.successor.addr if self.successor else None}")
            print(
                f"predecessor: {self.predecessor.id if self.predecessor else None}, {self.predecessor.addr if self.predecessor else None}")
            print(f"storage: {self.storage.data}")
            self.print_finger_table()
            print("-------------------------------------")
            time.sleep(3)

    def fix_finger(self):
        next_idx = 0
        while not self.stop_event.is_set():
            # time.sleep(2)
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

    def check_predecessor(self):
        while not self.stop_event.is_set():
            time.sleep(1)
            self._check_predecessor()

    def _check_predecessor(self):
        if self.predecessor is None:
            return
        if not self.rpc_client.check_predecessor(self.predecessor):
            self.predecessor = None

    def find_successor(self, hid):
        pred = self.find_predecessor(hid)
        if pred is None:
            return None
        succ = self.get_successor_rpc(pred)
        if succ is None:
            return None
        return succ

    def find_predecessor(self, hid):
        curr = self.node
        succ = self.get_successor_rpc(curr)
        if succ is None:
            return None
        while not util.between_include_right(hid, curr.id, succ.id):
            curr = self.closest_preceding_finger_rpc(curr, hid)
            if curr is None:
                return None
            succ = self.get_successor_rpc(curr)
            if succ is None:
                return None
        return curr

    def closest_preceding_finger_rpc(self, node, hid):
        return self.rpc_client.closest_preceding_finger(node, hid)

    def get_successor_rpc(self, node):
        return self.rpc_client.get_successor(node)

    def get_predecessor_rpc(self, node):
        return self.rpc_client.get_predecessor(node)

    def find_successor_rpc(self, node, hid):
        return self.rpc_client.find_successor(node, hid)

    def notify_rpc(self, node, pred):
        return self.rpc_client.notify(node, pred)

    def get_kv_rpc(self, node, key):
        return self.rpc_client.get_kv(node, key)

    def set_kv_rpc(self, node, kv):
        return self.rpc_client.set_kv(node, kv)

    def delete_kv_rpc(self, node, key):
        return self.rpc_client.delete_kv(node, key)

    def find_kvs_rpc(self):
        return self.rpc_client.find_kvs(self.node, self.successor)

    def set_successor_rpc(self, node, succ):
        return self.rpc_client.set_successor(node, succ)

    def set_predecessor_rpc(self, node, pred):
        return self.rpc_client.set_predecessor(node, pred)

    def move_data_rpc(self, kvs):
        return self.rpc_client.move_data(self.successor, kvs)

    def GetPredecessor(self, request, context):
        if self.predecessor is None:
            return pb2.Node(id=-1, addr="")
        return self.predecessor

    def GetSuccessor(self, request, context):
        return self.successor

    def FindSuccessor(self, request, context):
        hid = request.id
        res = self.find_successor(hid)
        if res is None:
            return pb2.Node(id=-1, addr="")
        return res

    def ClosestPrecedingFinger(self, request, context):
        hid = request.id
        for i in range(len(self.finger_table) - 1, -1, -1):
            if self.finger_table[i][1] is not None and util.between(self.finger_table[i][1].id, self.node.id, hid):
                return self.finger_table[i][1]
        return self.node

    def Notify(self, request, context):
        self.pointer_lock.acquire()
        x = request
        pred = self.predecessor
        if pred is None or util.between(x.id, pred.id, self.node.id):
            self.predecessor = x
        self.pointer_lock.release()
        return pb2.ER()

    def SetKV(self, request, context):
        key = request.key
        hid = util.get_hash(key)
        x = self.find_successor(hid)
        self.set_kv_rpc(x, request)
        return pb2.SetResponse()

    def Set(self, request, context):
        self.storage.lock.acquire()
        self.storage.data[request.key] = request.value
        self.storage.lock.release()
        return pb2.SetResponse()

    def GetKV(self, request, context):
        key = request.key
        hid = util.get_hash(key)
        x = self.find_successor(hid)
        return self.get_kv_rpc(x, request)

    def Get(self, request, context):
        key = request.key
        self.storage.lock.acquire()
        if key not in self.storage.data:
            res = pb2.GetResponse(value="", ok=False)
        else:
            res = pb2.GetResponse(value=self.storage.data[key], ok=True)
        self.storage.lock.release()
        return res

    def DeleteKV(self, request, context):
        key = request.key
        hid = util.get_hash(key)
        x = self.find_successor(hid)
        return self.delete_kv_rpc(x, request)

    def Delete(self, request, context):
        key = request.key
        self.storage.lock.acquire()
        if key not in self.storage.data:
            res = pb2.DelResponse(value="", ok=False)
        else:
            res = pb2.DelResponse(value=self.storage.data.pop(key), ok=True)
        self.storage.lock.release()
        return res

    def FindKVs(self, request, context):
        low = request.id
        high = self.node.id
        del_dict = pb2.KVs()

        self.storage.lock.acquire()
        for k in list(self.storage.data):
            hid = util.get_hash(k)
            if util.between_include_right(hid, high, low):
                v = self.storage.data.pop(k)
                del_dict.values.append(pb2.KV(key=k, value=v))
        self.storage.lock.release()
        return del_dict

    def Stop(self, request, context):
        del_dict = pb2.KVs()
        self.storage.lock.acquire()
        for k in list(self.storage.data):
            v = self.storage.data.pop(k)
            del_dict.values.append(pb2.KV(key=k, value=v))
        self.move_data_rpc(del_dict)
        self.storage.lock.release()
        self.stop_event.set()
        time.sleep(3)
        self.set_successor_rpc(self.predecessor, self.successor)
        self.set_predecessor_rpc(self.successor, self.predecessor)
        self.rpc_server.stop()
        return pb2.ER()

    def SetSuccessor(self, request, context):
        self.pointer_lock.acquire()
        succ = request
        self.successor = succ
        self.finger_table[0][1] = succ
        self.pointer_lock.release()
        return pb2.ER()

    def SetPredecessor(self, request, context):
        self.pointer_lock.acquire()
        pred = request
        self.predecessor = pred
        self.pointer_lock.release()
        return pb2.ER()

    def MoveData(self, request, context):
        self.storage.lock.acquire()
        for kv in request.values:
            self.storage.data[kv.key] = kv.value
        self.storage.lock.release()
        return pb2.ER()

    def CheckPredecessor(self, request, context):
        return pb2.ER()


def new_inner_node(addr):
    if addr is None:
        return None
    hid = util.get_hash(addr)
    return pb2.Node(id=hid, addr=addr)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        node2 = Node(sys.argv[1], None)
    elif len(sys.argv) == 3:
        node2 = Node(sys.argv[1], sys.argv[2])