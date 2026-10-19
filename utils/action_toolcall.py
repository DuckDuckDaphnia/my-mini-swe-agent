from utils.exceptions import FormatError
import json
from jinja2 import StrictUndefined, Template
#意识到了用jinja2是好的

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

def parse_actions(tool_calls:list,*,format_error_template:str,template_kwargs:dict|None = None):
    template_kwargs = template_kwargs or {}
    if not tool_calls:
        #处理空的tool_calls
        raise FormatError(
            {
                "role":"user",
                "content":Template(format_error_template,undefined=StrictUndefined).render(
                    error = "No tool calls found in the response. Every response MUST include at least one tool call.",
                    actions = [],
                    has_tool_calls = False,
                    **template_kwargs,
                ),
                "extra":{"interrupt_type": "FormatError"},
            }
        )
    #处理tool_call
    actions = []
    for tool_call in tool_calls:
        error_msg = ""
        args = {}
        try:
            args = json.loads(tool_call.function.arguments)
        except Exception as e:
            #json解析失败
            error_msg = f"Error parsing tool call arguments:{e}"
        if tool_call.function.name!="bash":
            #未知的命令
            error_msg += f"Unknown tool '{tool_call.function.name}'."
        if not isinstance(args, dict) or "command" not in args:
            #toolcall里没有command,或者args不是字典
            error_msg +="Missing 'command' argument in bash tool call."
        if error_msg:
            #如果出错rasie错误
            raise FormatError({
                "role":"user",
                "content":Template(format_error_template,undefined=StrictUndefined).render(
                    actions = [],
                    error = error_msg.strip(),
                    has_tool_calls=True,
                    **template_kwargs,
                ),
                "extra":{"interrupt_type":"FormatError"},
            })
        actions.append({"command":args["command"], "tool_call_id":tool_call.id})
    return actions