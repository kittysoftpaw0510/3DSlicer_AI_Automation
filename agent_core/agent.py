import os
from dotenv import load_dotenv
from tools.tools import get_registered_tools
import openai
import json

load_dotenv()

# Helper functions for OpenAI agent

def get_openai_function_schemas():
    """
    Returns a list of OpenAI function schemas for all registered tools.
    """
    return [
        {
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["parameters"]
        }
        for tool in get_registered_tools()
    ]

def get_tool_lookup():
    """
    Returns a dict mapping tool names to their function implementations.
    """
    return {tool["name"]: tool["function"] for tool in get_registered_tools()}

def run_openai_agent(messages, functions):
    """
    Calls the OpenAI ChatCompletion API with function calling support (openai>=1.0.0 syntax).
    """
    print("[Agent] Thinking...")
    return openai.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        messages=messages,
        functions=functions,
        function_call="auto"
    )

class AI_Agent:
    def __init__(self):
        self.functions = get_openai_function_schemas()
        self.tool_lookup = get_tool_lookup()
        self.max_history = 10  # Limit to last 10 messages (excluding system)
        self.messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert assistant for 3D Slicer and related automation tasks. "
                    "You remember the user's previous questions and your own answers within the current session. "
                    "You can use available tools to perform actions in 3D Slicer, such as changing views, scrolling slices, or running scripts. "
                    "Always explain your reasoning and results clearly. "
                    "If you use a tool, summarize the outcome for the user. "
                    "If you need more information, ask clarifying questions. "
                    "Be concise, helpful, and context-aware. But clear and short."
                )
            }
        ]

    def handle_command(self, command: str) -> str:
        if not command:
            return "Please enter a command."
        self.messages.append({"role": "user", "content": command})
        if len(self.messages) > self.max_history + 1:
            self.messages = [self.messages[0]] + self.messages[-self.max_history:]
        response = run_openai_agent(self.messages, self.functions)
        message = response.choices[0].message
        if hasattr(message, "function_call") and message.function_call:
            func_name = message.function_call.name
            func_args = json.loads(message.function_call.arguments)
            print(f"[Agent] Calling tool: {func_name} with args: {func_args}")
            if func_name in self.tool_lookup:
                tool_result = self.tool_lookup[func_name](**func_args)
                print(f"[Agent] Tool result: {tool_result}")
                tool_result_str = str(tool_result) if tool_result else "[No result returned]"
                self.messages.append({
                    "role": "function",
                    "name": func_name,
                    "content": tool_result_str
                })
                if len(self.messages) > self.max_history + 1:
                    self.messages = [self.messages[0]] + self.messages[-self.max_history:]
                print("[Agent] Thinking...")
                response = run_openai_agent(self.messages, self.functions)
                final_message = response.choices[0].message.content
                print("[Agent] Final answer generated.")
                if not final_message:
                    final_message = "[No answer generated]"
                self.messages.append({"role": "assistant", "content": final_message})
                if len(self.messages) > self.max_history + 1:
                    self.messages = [self.messages[0]] + self.messages[-self.max_history:]
                return final_message
            else:
                return f"Tool '{func_name}' not found."
        else:
            print("Final answer generated.")
            final_message = message.content
            if not final_message:
                final_message = "[No answer generated]"
            self.messages.append({"role": "assistant", "content": final_message})
            if len(self.messages) > self.max_history + 1:
                self.messages = [self.messages[0]] + self.messages[-self.max_history:]
            return final_message 