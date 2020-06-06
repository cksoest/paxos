class Message:

    def __init__(self, src, dst, message_type, promise_id=None, value=None):
        self.src = src
        self.dst = dst
        self.message_type = message_type
        self.promise_id = promise_id
        self.value = value

    def send(self, network):
        network.append(self)
