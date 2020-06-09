class Node:

    def __init__(self, node_type, node_id):
        self.promised = 0
        self.node_id = node_type + str(node_id)
        self.failed = False
        self.records = []
        self.state = "SLEEP"
        self.promise_request = 0
        self.promise_received = 0
        self.propose_value = None

        self.accepted_received = 0

    def __str__(self):
        return self.node_id
