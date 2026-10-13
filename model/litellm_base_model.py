import litellm
from pydantic import BaseModel
from collections.abc import Callable
import os
from dotenv import load_dotenv
from utils.action_toolcall import (BASH_TOOL,
                                   format_toolcall_observation_message)
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
        cost_output = self._calculate_cost(response)
        actions = self._parse_actions(response=response)

        message = response.choices[0].message.model_dump()
        message["extra"] = {
            "actions": actions,
            "response":response.model_dump(),
            **cost_output
        }
        return message

    def _parse_actions(self, response):
        tool_calls =response.choices[0].message.tool_calls
        actions=[]
        for tool_call in tool_calls:
            args = json.loads(tool_call.function.arguments)
            actions.append({"command":args["command"],"tool_call_id":tool_call.id})
        return actions

    def _calculate_cost(self, response) -> dict[str, float]:
        cost = litellm.cost_calculator.completion_cost(response,model = self.config.model_name)
        return {"cost":cost}

    def format_observation_messages(self, message:dict,outputs:list[dict])->list[dict]:
        actions = message.get("extra", {}).get("actions",[])
        return format_toolcall_observation_message(actions = actions, outputs = outputs)