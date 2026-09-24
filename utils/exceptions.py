class InterruptAgentFlow(Exception):
    def __init__(self, messages:dict):
        self.messages = messages
        super().__init__()

class Submitted(InterruptAgentFlow):
    "raise when the agent has finished work"