from tools.tools import get_registered_tools

print("Registered tools at startup:", [tool["name"] for tool in get_registered_tools()])

from agent_core.agent import AI_Agent

def main():
    agent = AI_Agent()
    print("AI Agent CLI for 3DSlicer GUI Control. Type 'exit' or 'quit' to stop.")
    while True:
        command = input('> ').strip()
        if command.lower() in {'exit', 'quit'}:
            print("Goodbye!")
            break
        response = agent.handle_command(command)
        print(response)

if __name__ == '__main__':
    main() 