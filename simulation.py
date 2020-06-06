from message import Message
from node import Node
from event import Event


class Simulation:

    def __init__(self, nP, nA, tmax):
        if nP + nA > 10:
            raise Exception("maximaal 10 nodes")
        if tmax > 999:
            raise Exception("maximum van tmax is 999")
        self.events = []
        self.network = []
        self.propose_id = 0
        self.proposals = [Node("P", i) for i in range(nP)]
        self.acceptors = [Node("A", i) for i in range(nP, nP+nA)]
        self.tmax = tmax

    def set_events(self):
        self.events.append(Event(0, [], [], "P0", 42))

    def run(self):
        for i in range(self.tmax):
            if len(self.events) == 0:
                return None

            if self.events[0].tick == i:
                event = self.events[0]
                del self.events[0]
                for node in event.F:
                    node.failed = True
                for node in event.R:
                    node.failed = False
                if (event.msg_P is not None) and (event.msg_V is not None):
                    message = Message(None, event.msg_P, "PREPARE", value=event.msg_V)
                    message.send(self.network)
            else:
                pass
                # proces mesages from network



a = Simulation(1, 3, 15)
a.set_events()
a.run()
print(a.network)


# for p in a.P:
#     print(p.node_id)
#
# for b in a.A:
#     print(b.node_id)
