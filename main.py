from tools.tools import get_registered_tools
from voiceio.voice_input import listen_for_command
from voiceio.voice_output import speak

print("Registered tools at startup:", [tool["name"] for tool in get_registered_tools()])

from agent_core.agent import AI_Agent

def cli_mode():
    agent = AI_Agent()
    print("AI Agent CLI for 3DSlicer GUI Control. Type 'exit' or 'quit' to stop.")
    while True:
        command = input('> ').strip()
        if command.lower() in {'exit', 'quit', 'bye'}:
            print("Goodbye!")
            break
        response = agent.handle_command(command)
        print(response)

def voice_mode():
    def handle_transcribe(transcribe):
        response = agent.handle_command(transcribe)
        speak(response)
    
    agent = AI_Agent()
    print("Voice AI Agent for 3DSlicer GUI Control. Ask anything you want for control 3DSlicer.")
    listen_for_command(handle_transcribe)

def main(mode="cli"):
    if mode == "cli":
        cli_mode()
    elif mode == "voice":
        voice_mode()
    else:
        print("[Main] Invaild Mode")

if __name__ == '__main__':
    # main("voice")
    main()