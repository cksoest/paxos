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
        self.events.append(Event(3, [], [], self.proposals[1], 400))
        self.events.append(Event(17, [], [], self.proposals[0], 1000))

    def run(self):
        for i in range(self.tmax):
            ran_event = False
            for event in self.events:
                if event.tick == i:
                    for node in event.failed:
                        node.failed = True
                    for node in event.recovered:
                        node.failed = False
                    if (event.proposal is not None) and (event.value is not None):
                        propose_message = Message(i, None, event.proposal, "PROPOSE", value=event.value)
                        propose_message.send(self.queue)
                    self.events.remove(event)
                    ran_event = True

            if not ran_event:
                for proposal in self.proposals:
                    for message in self.network:
                        if message.dst == proposal:

                            if message.message_type == "PROPOSE" and proposal.state == "SLEEP":
                                for acceptor in self.acceptors:
                                    prepare_message = Message(i, proposal, acceptor, "PREPARE", propose_id=self.propose_id)
                                    prepare_message.send(self.queue)
                                proposal.propose_value = message.value = message.value
                                proposal.propose_id = self.propose_id
                                self.propose_id += 1
                                proposal.state = "ACTIVE"

                            if message.message_type == "PROMISE":
                                if message.propose_id == proposal.propose_id:
                                    proposal.promise_received += 1
                                    if proposal.promise_received > len(self.acceptors)/2:
                                        for acceptor in self.acceptors:
                                            accept_message = Message(i, proposal, acceptor, "ACCEPT", propose_id=message.propose_id, value=proposal.propose_value)
                                            accept_message.send(self.queue)
                                        proposal.promise_received = 0
                                        for m in self.network:
                                            if m.message_type == "PROMISE" and m.dst == proposal and m.propose_id == proposal.propose_id:
                                                if m != message:
                                                    self.network.remove(m)

                            if message.message_type == "ACCEPTED":
                                if message.propose_id == proposal.propose_id and message.value == proposal.propose_value:
                                    proposal.accepted_received += 1
                                    if proposal.accepted_received > len(self.acceptors)/2:
                                        proposal.accepted_received = 0
                                        proposal.propose_value = None
                                        proposal.propose_id = None
                                        proposal.state = "SLEEP"
                                        for m in self.network:
                                            if m.message_type == "ACCEPTED" and m.dst == proposal and m.propose_id == proposal.propose_id:
                                                if m != message:
                                                    self.network.remove(m)

                            self.network.remove(message)

                for acceptor in self.acceptors:
                    for message in self.network:
                        if message.dst == acceptor:

                            if message.message_type == "PREPARE" and acceptor.state == "SLEEP":
                                if message.propose_id > acceptor.promised:
                                    acceptor.promised = message.propose_id
                                    promise_message = Message(i, acceptor, message.src, "PROMISE", propose_id=message.propose_id)
                                    promise_message.send(self.queue)
                                    acceptor.state = "ACTIVE"

                            if message.message_type == "ACCEPT":
                                if message.propose_id == acceptor.promised:
                                    acceptor.records.append({"propose_id": message.propose_id, "value": message.value})
                                    accepted_message = Message(i, acceptor, message.src, "ACCEPTED", propose_id=message.propose_id, value=message.value)
                                    accepted_message.send(self.queue)
                                    acceptor.state = "SLEEP"

                            self.network.remove(message)

            self.network += self.queue
            self.queue = []


a = Simulation(2, 5, 150)
a.set_events()
a.run()
print(a.network)
print(a.events)
print(a.queue)

for ui in a.acceptors:
    print(ui.records)
