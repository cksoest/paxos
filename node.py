class Node:

    def __init__(self, node_id):
        self.promised = -1
        self.node_id = node_id
        self.failed = False
