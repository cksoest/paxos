from message import Message
from node import Node
from event import Event


class Simulation:

    def __init__(self, nP, nA, nL, tmax):
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
        self.learners = [Node("L", i) for i in range(nP+nA, nP+nA+nL)]
        self.tmax = tmax

    def set_events(self):
        self.events.append(Event(0, [], [], self.proposals[0], 43))
        # self.events.append(Event(1, [], [], self.proposals[0], 44))
        self.events.append(Event(1, [], [], self.proposals[1], 45))
        # self.events.append(Event(7, self.acceptors[:2], [], None, None))
        # self.events.append(Event(15, [], self.acceptors[:2], self.proposals[0], None))

    def run(self):
        for i in range(self.tmax):
            for event in self.events:
                if event.tick == i:
                    for node in event.failed:
                        node.to_fail(i)
                    for node in event.recovered:
                        node.to_recover(i)
                    if (event.proposal is not None) and (event.value is not None):
                        propose_message = Message(i, None, event.proposal, "PROPOSE", value=event.value)
                        propose_message.send(self.queue)
                    self.events.remove(event)

            for proposal in self.proposals:
                if not proposal.failed:
                    for message in self.network:
                        if message.dst == proposal:

                            if message.message_type == "PROPOSE":
                                for acceptor in self.acceptors:
                                    prepare_message = Message(i, proposal, acceptor, "PREPARE", propose_id=self.propose_id)
                                    prepare_message.send(self.queue)
                                proposal.propose_value = message.value = message.value
                                proposal.propose_id = self.propose_id
                                self.propose_id += 1

                            if message.message_type == "PROMISE" and message.propose_id not in proposal.reject_promise:
                                if message.propose_id == proposal.propose_id:
                                    proposal.promise_received += 1
                                    if proposal.promise_received > len(self.acceptors)/2:
                                        for acceptor in self.acceptors:
                                            accept_message = Message(i, proposal, acceptor, "ACCEPT", propose_id=message.propose_id, value=proposal.propose_value)
                                            accept_message.send(self.queue)
                                        proposal.promise_received = 0
                                        proposal.reject_promise.append(message.propose_id)

                            if message.message_type == "ACCEPTED" and message.propose_id not in proposal.reject_accepted:
                                if message.propose_id == proposal.propose_id and message.value == proposal.propose_value:
                                    proposal.accepted_received += 1
                                    if proposal.accepted_received > len(self.acceptors)/2:
                                        for learner in self.learners:
                                            success_message = Message(i, proposal, learner, "SUCCESS", value=message.value)
                                            success_message.send(self.queue)
                                        proposal.accepted_received = 0
                                        proposal.propose_value = None
                                        proposal.propose_id = 0
                                        proposal.reject_accepted.append(message.propose_id)

                            if message.message_type == "REJECTED" and message.propose_id not in proposal.reject_rejected:
                                if message.propose_id == proposal.propose_id:
                                    proposal.rejected_received += 1
                                    if proposal.rejected_received > len(self.acceptors)/2:
                                        for acceptor in self.acceptors:
                                            prepare_message = Message(i, proposal, acceptor, "PREPARE", propose_id=self.propose_id)
                                            prepare_message.send(self.queue)
                                        proposal.propose_id = self.propose_id
                                        self.propose_id += 1
                                        proposal.rejected_received = 0
                                        proposal.reject_rejected.append(message.propose_id)

                            self.network.remove(message)

            for acceptor in self.acceptors:
                if not acceptor.failed:
                    for message in self.network:
                        if message.dst == acceptor:

                            if message.message_type == "PREPARE":
                                if message.propose_id > acceptor.promised:
                                    acceptor.promised = message.propose_id
                                    promise_message = Message(i, acceptor, message.src, "PROMISE", propose_id=message.propose_id)
                                    promise_message.send(self.queue)

                            if message.message_type == "ACCEPT":
                                if message.propose_id == acceptor.promised:
                                    acceptor.records.append({"propose_id": message.propose_id, "value": message.value})
                                    accepted_message = Message(i, acceptor, message.src, "ACCEPTED", propose_id=message.propose_id, value=message.value)
                                    accepted_message.send(self.queue)
                                else:
                                    rejected_message = Message(i, acceptor, message.src, "REJECTED", propose_id=message.propose_id)
                                    rejected_message.send(self.queue)

                            self.network.remove(message)

            for learner in self.learners:
                if not learner.failed:
                    for message in self.network:
                        if message.dst == learner:

                            if message.message_type == "SUCCESS":
                                print(str(i) + " " + str(learner) + " PREDICTED " + str(message.value*1.11))

                            self.network.remove(message)

            self.network += self.queue
            self.queue = []


a = Simulation(2, 3, 1, 150)
a.set_events()
a.run()
print(a.network)
print(a.events)
print(a.queue)

for ui in a.acceptors:
    print(ui.records)
