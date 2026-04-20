import time
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

# Define a simple agent for comparison
agent = Agent(
    name="comparison_agent",
    model="gemini-2.5-flash",
    instruction="You are a helpful assistant.",
    generate_content_config=types.GenerateContentConfig(temperature=1.0)
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

async def _ensure_session(session_service, app_name: str, session_id: str):
    session = await session_service.get_session(
        app_name=app_name,
        user_id="user_123",
        session_id=session_id
    )
    if not session:
        await session_service.create_session(
            app_name=app_name,
            user_id="user_123",
            session_id=session_id
        )

async def generate_adk(prompt: str, session_id: str = "session_123"):
    """Calls Gemini using the ADK Framework."""
    await _ensure_session(runner.session_service, "ComparisonApp", session_id)
    
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
    await _ensure_session(tool_runner.session_service, "ToolApp", "session_tool")
    
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

# --- Multi-Agent Scenario ---

researcher = Agent(
    name="researcher",
    model="gemini-2.5-flash",
    instruction="Provide 3 short key facts about the topic.",
)

writer = Agent(
    name="writer",
    model="gemini-2.5-flash",
    instruction="Turn the research results into a polite paragraph.",
)

coordinator = Agent(
    name="coordinator",
    model="gemini-2.5-flash",
    instruction="Delegate the research task to the researcher agent, and then delegate the results to the writer agent to produce the final response.",
    sub_agents=[researcher, writer],
)

agent_runner = InMemoryRunner(
    app_name="AgentApp",
    agent=coordinator,
)

async def agent_adk(prompt: str):
    """Calls Gemini using the ADK Framework for multi-agent coordination."""
    # Ensure session exists for agent test
    await _ensure_session(agent_runner.session_service, "AgentApp", "session_agent")
    
    start_time = time.time()
    response_text = ""
    
    for event in agent_runner.run(
        user_id="user_123",
        session_id="session_agent",
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

async def stream_adk(prompt: str):
    """Streams Gemini response using the ADK Framework."""
    await _ensure_session(runner.session_service, "ComparisonApp", "session_stream")
    
    # runner.run returns a sync generator.
    # We yield from it to make this an async generator.
    for event in runner.run(
        user_id="user_123",
        session_id="session_stream",
        new_message=types.Content(
            role="user", parts=[types.Part.from_text(text=prompt)]
        ),
    ):
        if event.content and event.content.parts:
            part = event.content.parts[0]
            if part.text:
                yield part.text
                await asyncio.sleep(0)

# --- Parallel Scenario ---

from google.adk.agents.parallel_agent import ParallelAgent

p_agent1 = Agent(
    name="positive",
    model="gemini-2.5-flash",
    instruction="Provide a positive view on the topic.",
)

p_agent2 = Agent(
    name="negative",
    model="gemini-2.5-flash",
    instruction="Provide a negative view on the topic.",
)

p_agent3 = Agent(
    name="neutral",
    model="gemini-2.5-flash",
    instruction="Provide a neutral view on the topic.",
)

parallel_agent = ParallelAgent(
    name="parallel_runner",
    sub_agents=[p_agent1, p_agent2, p_agent3]
)

parallel_runner = InMemoryRunner(
    app_name="ParallelApp",
    agent=parallel_agent,
)

async def parallel_adk(prompt: str):
    """Calls Gemini using the ADK Framework for parallel execution."""
    # Ensure session exists for parallel test
    await _ensure_session(parallel_runner.session_service, "ParallelApp", "session_parallel")
    
    start_time = time.time()
    response_text = ""
    
    for event in parallel_runner.run(
        user_id="user_123",
        session_id="session_parallel",
        new_message=types.Content(
            role="user", parts=[types.Part.from_text(text=prompt)]
        ),
    ):
        if event.content and event.content.parts:
            part = event.content.parts[0]
            if part.text:
                response_text += part.text + "\n"
                
    latency_ms = int((time.time() - start_time) * 1000)
    
    return {
        "response": response_text,
        "latency_ms": latency_ms
    }

# --- Loop Scenario ---

from google.adk.agents.loop_agent import LoopAgent

loop_sub_agent = Agent(
    name="worker",
    model="gemini-2.5-flash",
    instruction="Provide a short list of 3 animals.",
)

loop_agent = LoopAgent(
    name="loop_runner",
    sub_agents=[loop_sub_agent],
    max_iterations=3
)

loop_runner = InMemoryRunner(
    app_name="LoopApp",
    agent=loop_agent,
)

async def loop_adk(prompt: str):
    """Calls Gemini using the ADK Framework for loop execution."""
    # Ensure session exists for loop test
    await _ensure_session(loop_runner.session_service, "LoopApp", "session_loop")
    
    start_time = time.time()
    response_text = ""
    
    for event in loop_runner.run(
        user_id="user_123",
        session_id="session_loop",
        new_message=types.Content(
            role="user", parts=[types.Part.from_text(text=prompt)]
        ),
    ):
        if event.content and event.content.parts:
            part = event.content.parts[0]
            if part.text:
                response_text += part.text + "\n"
                
    latency_ms = int((time.time() - start_time) * 1000)
    
    return {
        "response": response_text,
        "latency_ms": latency_ms
    }

# --- Structured Output Scenario ---

structured_agent = Agent(
    name="structured_agent",
    model="gemini-2.5-flash",
    instruction="You are a data extractor. Respond ONLY with a valid JSON array of objects.",
)

structured_runner = InMemoryRunner(
    app_name="StructuredApp",
    agent=structured_agent,
)

async def structured_adk(prompt: str):
    """Calls Gemini using the ADK Framework and maintains session."""
    # Ensure session exists for structured test
    await _ensure_session(structured_runner.session_service, "StructuredApp", "session_structured")
    
    start_time = time.time()
    response_text = ""
    
    json_prompt = f"{prompt}. Each object must have 'name', 'lifespan', and 'habitat' fields."
    
    for event in structured_runner.run(
        user_id="user_123",
        session_id="session_structured",
        new_message=types.Content(
            role="user", parts=[types.Part.from_text(text=json_prompt)]
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
