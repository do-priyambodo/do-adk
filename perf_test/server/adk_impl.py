import time
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

# Define a simple agent for comparison
agent = Agent(
    name="comparison_agent",
    model="gemini-2.5-flash",
    instruction="You are a helpful assistant. Answer the user's questions concisely.",
)

import asyncio

# Create a Runner
runner = InMemoryRunner(
    app_name="ComparisonApp",
    agent=agent,
)

async def setup_session():
    # Explicitly create session for version 1.31.0 since auto_create_session failed
    await runner.session_service.create_session(
        app_name="ComparisonApp",
        user_id="user_123",
        session_id="session_123"
    )

# Session setup will be called by FastAPI startup event

async def _ensure_session(session_id: str):
    session = await runner.session_service.get_session(
        app_name="ComparisonApp",
        user_id="user_123",
        session_id=session_id
    )
    if not session:
        await runner.session_service.create_session(
            app_name="ComparisonApp",
            user_id="user_123",
            session_id=session_id
        )

async def generate_adk(prompt: str, session_id: str = "session_123"):
    """Calls Gemini using the ADK Framework."""
    await _ensure_session(session_id)
    
    start_time = time.time()
    response_text = ""
    
    # Using the synchronous run interface for testing
    for event in runner.run(
        user_id="user_123",
        session_id=session_id,
        new_message=types.Content(
            role="user", parts=[types.Part.from_text(text=prompt)]
        ),
    ):
        if event.content and event.content.parts:
            part = event.content.parts[0]
            if part.text:
                response_text += part.text
                
    latency_ms = int((time.time() - start_time) * 1000)
    
    return {
        "response": response_text,
        "latency_ms": latency_ms
    }

async def chat_adk(session_id: str, prompt: str):
    """Calls Gemini using the ADK Framework and maintains session."""
    return await generate_adk(prompt, session_id=session_id)

# --- Tool Use Scenario ---

def get_mock_weather(location: str):
    """Mock tool for weather."""
    return f"The weather in {location} is sunny and 25°C."

tool_agent = Agent(
    name="tool_agent",
    model="gemini-2.5-flash",
    instruction="You are a helpful assistant. Use the get_mock_weather tool to find weather.",
    tools=[get_mock_weather],
)

tool_runner = InMemoryRunner(
    app_name="ToolApp",
    agent=tool_agent,
)

async def tool_adk(prompt: str):
    """Calls Gemini using the ADK Framework and handles tool calls."""
    # Ensure session exists for tool test
    await tool_runner.session_service.create_session(
        app_name="ToolApp",
        user_id="user_123",
        session_id="session_tool"
    )
    
    start_time = time.time()
    response_text = ""
    
    for event in tool_runner.run(
        user_id="user_123",
        session_id="session_tool",
        new_message=types.Content(
            role="user", parts=[types.Part.from_text(text=prompt)]
        ),
    ):
        if event.content and event.content.parts:
            part = event.content.parts[0]
            if part.text:
                response_text += part.text
                
    latency_ms = int((time.time() - start_time) * 1000)
    
    return {
        "response": response_text,
        "latency_ms": latency_ms
    }
