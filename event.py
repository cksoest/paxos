class Event:

    def __init__(self, tick, failed, recovered, proposal, value):
        self.tick = tick
        self.failed = failed
        self.recovered = recovered
        self.proposal = proposal
        self.value = value
