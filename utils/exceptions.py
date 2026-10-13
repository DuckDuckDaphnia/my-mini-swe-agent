class InterruptAgentFlow(Exception):
    def __init__(self, messages:dict):
        self.messages = messages
        super().__init__()

class Submitted(InterruptAgentFlow):
    "raise when the agent has finished work"

class LimitsExceeded(InterruptAgentFlow):
    """Raised when the agent has exceeded its cost or step limit."""

class FormatError(InterruptAgentFlow):
    """Raised when the LM's output is not in the expected format."""