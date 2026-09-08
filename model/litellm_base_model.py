import litellm
from pydantic import BaseModel
from collections.abc import Callable
import os
from dotenv import load_dotenv
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
            messages=messages
        )


messages=[{"role": "user", "content": "Tell me a joke."}]
llmModel = LitellmModel(LitellmModelConfig)
print(llmModel._query(messages))
