# Agent Development Kit (ADK) - Beginner's Guide

Welcome to the Agent Development Kit (ADK)! This guide will help you understand how to build, test, and deploy AI agents using the Python ecosystem.

## What is ADK?
ADK is a flexible and modular framework for developing and deploying AI agents. It makes agent development feel more like standard software development, providing flexibility and control over agent behaviors.

## Prerequisites
- **Python 3.10 or higher**
- **`uv`**: A fast Python package manager (highly recommended in restricted environments where `pip` is not available).

---

## 1. How to Build (Create an Agent)

Building an agent in ADK involves defining the agent in a Python file and placing it in a specific folder structure so that the ADK CLI tools can find it.

### Folder Structure
The ADK expects a folder where each subdirectory represents an agent. Each agent folder must contain:
- `__init__.py`: To make it a Python package.
- `agent.py`: Where the agent is defined.

Example:
```
hello_agent/
├── __init__.py
└── agent.py
```

### Define the Agent
In `hello_agent/agent.py`, you create an `Agent` object and name it `root_agent` (the default name the CLI looks for).

```python
from google.adk.agents import Agent

root_agent = Agent(
    name="greeter_agent",
    model="gemini-2.5-flash",
    instruction="You are a helpful assistant. Answer the user's questions.",
)
```

---

## 2. How to Test (Using Web UI)

Testing your agent with the built-in Development UI is the best way to iterate.

### Running the Web UI
1.  **Navigate to the parent folder** that contains your agent folder (e.g., `do-adk`).
2.  **Ensure your virtual environment is active**:
    ```bash
    source .venv/bin/activate
    ```
3.  **Start the server**:
    ```bash
    adk web
    ```
    *Note: If you specify a folder like `adk web hello_agent/`, it will fail because it looks for agents inside that folder.*

4.  **Open your browser** and go to `http://127.0.0.1:8000` to interact with your agent!

---

## 3. Troubleshooting & Tips

### Missing `google.genai` Module
In restricted environments, use **`uv`** to install it:
```bash
uv pip install google-adk
```

### API Key Issues
If you get an error about missing API key, ensure you set or map your key to **`GOOGLE_API_KEY`** in the environment or in a helper file:
```python
import os

os.environ["GOOGLE_API_KEY"] = os.environ.get("GEMINI_API_KEY")
```

### Suppressing Warnings
If you find deprecation or experimental feature warnings annoying, you can suppress them at the top of your script or by running the command with an environment variable:
```bash
PYTHONWARNINGS="ignore" adk web
```
Or in code:
```python
import warnings

warnings.filterwarnings("ignore")
```

---

## 4. How to Deploy

Once your agent is working locally, you can deploy it to the cloud.

### Option A: Google Cloud Run
You can containerize your application and deploy it to Cloud Run.
*   Use `gcloud builds submit` to build a Docker image.
*   Use `gcloud run deploy` to deploy it.
*   *Reference*: See the script `01.setup-first.sh` in this project folder for the exact commands.

### Option B: Vertex AI Agent Engine
ADK is built for seamless integration with Vertex AI. You can deploy your agents directly to the Vertex AI Agent Engine for scaling and management.

---

## Important References
- **Python API Reference**: https://adk.dev/api-reference/python/
- **REST API Reference**: https://adk.dev/api-reference/rest/#/
- **ADK Python Repository**: https://github.com/google/adk-python
- **A2A Sample Code**: https://github.com/a2aproject/a2a-samples/tree/main/samples/python/agents
