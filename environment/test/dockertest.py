from environment.docker import DockerEnv

dEnv = DockerEnv(
    image="ubuntu",
    cwd="/home/dev/my-swe-agent/environment/envTs"
)

result = dEnv.execute("echo Hello")

print(result)

dEnv.cleanup()