import litellm
from pydantic import BaseModel
from collections.abc import Callable
import os
from dotenv import load_dotenv
from utils.action_toolcall import BASH_TOOL
import json

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

class LitellmModelConfig(BaseModel):
    "the name of model"
    model_name: str = "deepseek/deepseek-chat"

class LitellmModel:
    def __init__(self, config_class: Callable = LitellmModelConfig,**kwargs):
        self.config = config_class(**kwargs)

    def _query(self, messages:list[dict[str,str]], **kwargs):
        return litellm.completion(
            model = self.config.model_name,
            messages=messages,
            tools=[BASH_TOOL]
        )
    def query(self, messages:list[dict[str,str]]):
        response = self._query(messages)
        actions = self._parse_actions(response=response)

        messages = response.choices[0].message.model_dump()
        messages["extra"] = {
            "actions": actions
        }
        return messages

    def _parse_actions(self, response):
        tool_calls =response.choices[0].message.tool_calls
        actions=[]
        for tool_call in tool_calls:
            args = json.loads(tool_call.function.arguments)
            actions.append({"command":args["command"],"tool_call_id":tool_call.id})
        return actions

testmodel = LitellmModel(LitellmModelConfig)
message = testmodel.query([{
    "role":"user",
    "content":"你可以试着echo hello吗"
}])
print(message)