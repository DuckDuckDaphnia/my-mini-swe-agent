from pydantic import BaseModel
from model.litellm_base_model import LitellmModel,LitellmModelConfig
from environment.docker import DockerEnv
from utils.exceptions import InterruptAgentFlow

class AgentConfig(BaseModel):
    #填入config
    step_limit: int = 0


class DefaultAgent:
    def __init__(self, model:LitellmModel,env:DockerEnv,config_class: type = AgentConfig):
        self.config = config_class
        self.model = model
        self.env = env
        self.messages:list[dict] = []
        #未实现的功能

        #没有做add message

    def run(self, task:str=""):
        "run"
        #等待完善.format_message和add_message
        self.messages = [
            {
                "role":"system",
                "content":"You are a helpful assistant.Output one bash command"
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
            # break
        return self.messages[-1].get("extra",{})

    def step(self):
        return self.execute_action(self.query())

    def query(self):
        #待完善花费退出和时间超时
        message = self.model.query(self.messages)
        self.messages.append(message)
        return message

    def execute_action(self,message:dict):
        outputs = [self.env.execute(action) for action in message.get("extra",{}).get("actions",[])]
        self.messages.extend(self.model.format_observation_messages(message=message,outputs=outputs))
        return outputs