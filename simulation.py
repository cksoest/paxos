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
        self.queue = []
        self.propose_id = 1
        self.proposals = [Node("P", i) for i in range(nP)]
        self.acceptors = [Node("A", i) for i in range(nP, nP+nA)]
        self.tmax = tmax

    def set_events(self):
        self.events.append(Event(0, [], [], self.proposals[0], 42))

    def run(self):
        for i in range(self.tmax):
            event = False
            if len(self.events) > 0:
                if self.events[0].tick == i:
                    event = self.events[0]
                    del self.events[0]
                    for node in event.F:
                        node.failed = True
                    for node in event.R:
                        node.failed = False
                    if (event.msg_P is not None) and (event.msg_V is not None):
                        propose_message = Message(i, None, event.msg_P, "PROPOSE", value=event.msg_V)
                        propose_message.send(self.network)
                    event = True

            elif not event:
                for proposal in self.proposals:
                    for message in self.network:
                        if message.dst == proposal:
                            if message.message_type == "PROPOSE":
                                for acceptor in self.acceptors:
                                    prepare_message = Message(i, proposal, acceptor, "PREPARE", propose_id=self.propose_id)
                                    prepare_message.send(self.queue)
                                proposal.propose_value = message.value = message.value
                                proposal.promise_request = self.propose_id
                                self.propose_id += 1

                            if message.message_type == "PROMISE":
                                if message.propose_id == proposal.promise_request:
                                    proposal.promise_received += 1
                                    if proposal.promise_received > len(self.acceptors)/2:
                                        for acceptor in self.acceptors:
                                            accept_message = Message(i, proposal, acceptor, "ACCEPT", propose_id=message.propose_id, value=proposal.propose_value)
                                            accept_message.send(self.queue)
                                        proposal.promise_received = 0

                            if message.message_type == "ACCEPTED":
                                if message.propose_id == proposal.promise_request and message.value == proposal.propose_value:
                                    proposal.accepted_received += 1
                                    if proposal.accepted_received > len(self.acceptors)/2:
                                        proposal.accepted_received = 0
                                        proposal.propose_value = None
                                        # TODO state to sleep

                            self.network.remove(message)

                for acceptor in self.acceptors:
                    for message in self.network:
                        if message.dst == acceptor:
                            if message.message_type == "PREPARE":
                                if message.propose_id > acceptor.promised:
                                    acceptor.promised = message.propose_id
                                    promise_message = Message(i, acceptor, message.src, "PROMISE", propose_id=message.propose_id)
                                    promise_message.send(self.queue)

                            if message.message_type == "ACCEPT":
                                if message.propose_id == acceptor.promised:
                                    acceptor.records.append(message.value)
                                    accepted_message = Message(i, acceptor, message.src, "ACCEPTED", propose_id=message.propose_id, value=message.value)
                                    accepted_message.send(self.queue)

                            self.network.remove(message)

                self.network += self.queue
                self.queue = []

a = Simulation(1, 3, 15)
a.set_events()
a.run()
print(a.network)
print(a.events)
print(a.queue)

for ui in a.acceptors:
    print(ui.records)
