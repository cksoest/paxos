class Message:

    def __init__(self, tick, src, dst, message_type, propose_id=None, value=None):
        self.tick = tick
        self.src = src
        self.dst = dst
        self.message_type = message_type
        self.propose_id = propose_id
        self.value = value

    def send(self, network):
        network.append(self)
        print(self)

    def __str__(self):
        return str(self.tick) + " " + str(self.src) + " " + "->" + " " + str(self.dst) + " " + self.message_type + " propose_id=" + str(self.propose_id) + " value=" + str(self.value)
