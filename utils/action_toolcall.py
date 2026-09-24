BASH_TOOL = {
    "type": "function",
    "function": {
        "name": "bash",
        "description": "Execute a bash command",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The bash command to execute",
                }
            },
            "required": ["command"],
        },
    },
}

def format_toolcall_observation_message(
        actions:list[dict],
        outputs:list[dict]
)->list[dict]:
    not_executed = {"outputs":"","returncode":-1,"exception_info":"action was not executed"}
    padded_outputs = outputs + [not_executed]*(len(actions)-len(outputs))

    result = []
    for action, output in zip(actions, padded_outputs):
        content = f"Command output:\n{output.get('output', '')}\nExit code: {output.get('returncode', 0)}"
        msg = {
            "content":content,
            "extra":{
                "output":output.get("output",""),
                "returncode":output.get("returncode"),
                "exception_info":output.get("exception_info"),
                **output.get("extra",{})
            }
        }
        if "tool_call_id" in action:
            msg["tool_call_id"] = action["tool_call_id"]
            msg["role"] = "tool"
        else:
            msg["role"] = "user"
        result.append(msg)
    return result