# 3DSlicer AI Automation

## Overview

This project provides a command-line AI agent interface to control the 3D Slicer application using natural language commands. It leverages OpenAI's function-calling API to interpret user instructions and execute corresponding actions in 3D Slicer, such as changing views, scrolling slices, or running scripts. The agent communicates with a running instance of 3D Slicer via a file-based server mechanism.

## Features

- Natural language control of 3D Slicer via CLI
- Automated view switching (axial, coronal, sagittal, 4-up)
- Slice scrolling and other automation tools
- Extensible tool registry for new commands

## Requirements

- Python 3.8+
- 3D Slicer (installed locally)
- OpenAI API key

Python dependencies (see `requirements.txt`):
- openai
- python-dotenv
- requests

## Setup

1. **Clone the repository** and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   - Create a `.env` file in the project root with your OpenAI API key:
     ```
     OPENAI_API_KEY=your-key-here
     ```

3. **Configure 3D Slicer paths**:
   - Edit `tools/app_3dslicer_tools.py` and update `SLICER_EXE_PATH` and `SLICER_SERVER_SCRIPT` to match your system.

4. **(Optional) Start 3D Slicer server manually** if not using the agent to launch it.

## Usage

Run the main CLI agent:
```bash
python main.py
```

At the prompt, type natural language commands. Some examples:

- `Give me available actions`
- `Set view to axial`
- `Scroll slice up`
- `Open Slicer`
- `Close Slicer without saving`
- `Set view to coronal`
- `Set view to 4-up overview`

Type `exit` or `quit` to stop the agent.

The agent will respond with the result of your command or a list of available actions if you ask for them.

---

For more details or to extend the toolset, see the `tools/` directory and follow the existing patterns for registering new actions. 