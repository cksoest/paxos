class Node:

    def __init__(self, node_type, node_id):
        self.promised = 0
        self.node_id = node_type + str(node_id)
        self.failed = False
        self.records = []
        self.state = "SLEEP"
        self.propose_id = 0
        self.propose_value = None
        self.promise_received = 0
        self.accepted_received = 0
        self.rejected_received = 0
        self.reject_promise = []
        self.reject_accepted = []
        self.reject_rejected = []

    def to_fail(self, tick):
        self.failed = True
        print(str(tick) + " " + str(self) + " failed")

    def to_recover(self, tick):
        self.failed = False
        print(str(tick) + " " + str(self) + " recovered")

    def __str__(self):
        return self.node_id
