from pydantic import BaseModel
from model.litellm_base_model import LitellmModel,LitellmModelConfig
from environment.docker import DockerEnv
from utils.exceptions import InterruptAgentFlow, LimitsExceeded

class AgentConfig(BaseModel):
    #填入config
    step_limit: int = 0
    cost_limit: float = 3.0


class DefaultAgent:
    def __init__(self, model:LitellmModel,env:DockerEnv,config_class: type = AgentConfig, **kwargs):
        self.config = config_class(**kwargs)
        self.model = model
        self.env = env
        self.messages:list[dict] = []
        self.cost = 0.0
        #未实现的功能


        #没有做add message

    def run(self, task:str=""):
        "run"
        #等待完善.format_message和add_message
        self.messages = [
            {
                "role":"system",
                "content":"You are a helpful assistant. "
                "Output one bash command. "
                "when finished, make the FIRST line of your command's output be COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT, followed by the answer "
            },
            {
                "role":"user",
                "content":f"Please solve this issue:{task}"
            }
        ]
        #等待完善退出任务和step
        while True:
            try:
                self.step()
            except InterruptAgentFlow as e:
                self.messages.append(e.messages)
            if self.messages[-1].get("role") == "exit":
                break
        return self.messages[-1].get("extra",{})

    def step(self):
        return self.execute_action(self.query())

    def query(self):
        #待完善花费退出和时间超时
        if 0<self.config.cost_limit <= self.cost:
            raise LimitsExceeded(
                {
                    "role":"exit",
                    "content":"LimitsExceeded",
                    "extra":{"exit_status":"LimitsExceeded","submission":""},
                }
            )
        message = self.model.query(self.messages)
        self.cost += message.get("extra", {}).get("cost", 0.0)
        self.messages.append(message)
        return message

    def execute_action(self,message:dict):
        outputs = [self.env.execute(action) for action in message.get("extra",{}).get("actions",[])]
        self.messages.extend(self.model.format_observation_messages(message=message,outputs=outputs))
        return outputs