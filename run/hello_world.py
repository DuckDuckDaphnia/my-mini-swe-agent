from model.litellm_base_model import LitellmModel
from environment.docker import DockerEnv
from agents.default import DefaultAgent
import typer
import logging
import os

app = typer.Typer()

@app.command()
def main(
    task: str = typer.Option(..., "-t", "--task",help="Task statement",prompt=True),
    model_name: str = typer.Option(
        os.getenv("MODEL_NAME"),
        #还没有做指定模型
        help="Model name"
    ),
) -> DefaultAgent:
    logging.basicConfig(level=logging.DEBUG)
    agent = DefaultAgent(
        LitellmModel(model_name = model_name),
        DockerEnv(image="ubuntu",
            cwd="/home/dev/my-swe-agent/environment/envTs")
    )
    agent.run(task)
    return agent

if __name__ == "__main__":
    app()
#完善default Agent.