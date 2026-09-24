import subprocess, uuid
from utils.exceptions import Submitted

class DockerEnv:
    def __init__(self,image,cwd="/",timeout=30):
        self.image, self.cwd, self.timeout = image, cwd, timeout
        "获得id"
        self.container_id = self._start_container()

    def _start_container(self):
        name = f"swedev-{uuid.uuid4().hex[:8]}"
        r = subprocess.run(
            ["docker", "run", "-d", "--name", name, "-w",self.cwd,
                self.image,"sleep","2h"],
                capture_output=True,
                text=True,
                check=True,
        )
        return r.stdout.strip()

    def execute(self, action:dict):
        command = action.get("command","")
        r = subprocess.run(
            ["docker", "exec", "-w", self.cwd,self.container_id,
                "bash","-lc",command],
                capture_output=True, text=True,timeout=self.timeout,
        )
        output = {"output":r.stdout, "returncode":r.returncode}
        self._check_finished(output=output)
        return output

    def _check_finished(self, output:dict):
        lines = output.get("output","").lstrip().splitlines(keepends=True)
        #这里没有完成line第一行出任务完成
        if lines and output["returncode"]==0:
            submission = "".join(lines[1:])
            raise Submitted(
                #把信息传过去
                {
                    "role":"exit",
                    "content":submission,
                    "extra":{"exit_status":"Submitted","submission":submission}
                }
            )

    def cleanup(self):
        subprocess.run(["docker","rm","-f",self.container_id],
                        capture_output=True)