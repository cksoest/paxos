class Node:

    def __init__(self, node_type, node_id):
        self.promised = -1
        self.node_id = node_type + str(node_id)
        self.failed = False
        self.records = []
