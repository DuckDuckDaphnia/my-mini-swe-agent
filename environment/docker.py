import subprocess, uuid

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
        return {"output":r.stdout, "returncode":r.returncode}

    def cleanup(self):
        subprocess.run(["docker","rm","-f",self.container_id],
                        capture_output=True)