import time
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

# Cache for runners to avoid recreation overhead
runners_cache = {}

def get_runner(model_name: str):
    app_name = f"App_{model_name.replace('-', '_')}"
    if model_name not in runners_cache:
        local_agent = Agent(
            name="comparison_agent",
            model=model_name,
            instruction="You are a helpful assistant.",
            generate_content_config=types.GenerateContentConfig(temperature=1.0)
        )
        runners_cache[model_name] = InMemoryRunner(
            app_name=app_name,
            agent=local_agent,
        )
    return runners_cache[model_name]

import asyncio



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

async def generate_adk(prompt: str, session_id: str = "session_123", model_name: str = "gemini-2.5-flash"):
    """Calls Gemini using the ADK Framework."""
    local_runner = get_runner(model_name)
    app_name = f"App_{model_name.replace('-', '_')}"
    await _ensure_session(local_runner.session_service, app_name, session_id)
    
    start_time = time.time()
    response_text = ""
    
    # Using the synchronous run interface for testing
    for event in local_runner.run(
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

async def chat_adk(session_id: str, prompt: str, model_name: str = "gemini-2.5-flash"):
    """Calls Gemini using the ADK Framework and maintains session."""
    return await generate_adk(prompt, session_id=session_id, model_name=model_name)

# --- Tool Use Scenario ---

def get_mock_weather(location: str):
    """Mock tool for weather."""
    return f"The weather in {location} is sunny and 25°C."

tool_runners_cache = {}

def get_tool_runner(model_name: str):
    app_name = f"ToolApp_{model_name.replace('-', '_')}"
    if model_name not in tool_runners_cache:
        local_tool_agent = Agent(
            name="tool_agent",
            model=model_name,
            instruction="You are a helpful assistant. Use the get_mock_weather tool to find weather.",
            tools=[get_mock_weather],
        )
        tool_runners_cache[model_name] = InMemoryRunner(
            app_name=app_name,
            agent=local_tool_agent,
        )
    return tool_runners_cache[model_name]

async def tool_adk(prompt: str, model_name: str = "gemini-2.5-flash"):
    """Calls Gemini using the ADK Framework and handles tool calls."""
    local_runner = get_tool_runner(model_name)
    app_name = f"ToolApp_{model_name.replace('-', '_')}"
    # Ensure session exists for tool test
    await _ensure_session(local_runner.session_service, app_name, "session_tool")
    
    start_time = time.time()
    response_text = ""
    
    for event in local_runner.run(
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

agent_runners_cache = {}

def get_agent_runner(model_name: str):
    app_name = f"AgentApp_{model_name.replace('-', '_')}"
    if model_name not in agent_runners_cache:
        local_researcher = Agent(
            name="researcher",
            model=model_name,
            instruction="Provide 3 short key facts about the topic.",
        )
        local_writer = Agent(
            name="writer",
            model=model_name,
            instruction="Turn the research results into a polite paragraph.",
        )
        local_coordinator = Agent(
            name="coordinator",
            model=model_name,
            instruction="Delegate the research task to the researcher agent, and then delegate the results to the writer agent to produce the final response.",
            sub_agents=[local_researcher, local_writer],
        )
        agent_runners_cache[model_name] = InMemoryRunner(
            app_name=app_name,
            agent=local_coordinator,
        )
    return agent_runners_cache[model_name]

async def agent_adk(prompt: str, model_name: str = "gemini-2.5-flash"):
    """Calls Gemini using the ADK Framework for multi-agent coordination."""
    local_runner = get_agent_runner(model_name)
    app_name = f"AgentApp_{model_name.replace('-', '_')}"
    # Ensure session exists for agent test
    await _ensure_session(local_runner.session_service, app_name, "session_agent")
    
    start_time = time.time()
    response_text = ""
    
    for event in local_runner.run(
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

async def stream_adk(prompt: str, model_name: str = "gemini-2.5-flash"):
    """Streams Gemini response using the ADK Framework."""
    local_runner = get_runner(model_name)
    app_name = f"App_{model_name.replace('-', '_')}"
    await _ensure_session(local_runner.session_service, app_name, "session_stream")
    
    # runner.run returns a sync generator.
    # We yield from it to make this an async generator.
    for event in local_runner.run(
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

parallel_runners_cache = {}

def get_parallel_runner(model_name: str):
    app_name = f"ParallelApp_{model_name.replace('-', '_')}"
    if model_name not in parallel_runners_cache:
        local_p1 = Agent(
            name="positive",
            model=model_name,
            instruction="Provide a positive view on the topic.",
        )
        local_p2 = Agent(
            name="negative",
            model=model_name,
            instruction="Provide a negative view on the topic.",
        )
        local_p3 = Agent(
            name="neutral",
            model=model_name,
            instruction="Provide a neutral view on the topic.",
        )
        local_parallel = ParallelAgent(
            name="parallel_runner",
            sub_agents=[local_p1, local_p2, local_p3]
        )
        parallel_runners_cache[model_name] = InMemoryRunner(
            app_name=app_name,
            agent=local_parallel,
        )
    return parallel_runners_cache[model_name]

async def parallel_adk(prompt: str, model_name: str = "gemini-2.5-flash"):
    """Calls Gemini using the ADK Framework for parallel execution."""
    local_runner = get_parallel_runner(model_name)
    app_name = f"ParallelApp_{model_name.replace('-', '_')}"
    # Ensure session exists for parallel test
    await _ensure_session(local_runner.session_service, app_name, "session_parallel")
    
    start_time = time.time()
    response_text = ""
    
    for event in local_runner.run(
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

loop_runners_cache = {}

def get_loop_runner(model_name: str):
    app_name = f"LoopApp_{model_name.replace('-', '_')}"
    if model_name not in loop_runners_cache:
        local_sub_agent = Agent(
            name="worker",
            model=model_name,
            instruction="Provide a short list of 3 animals.",
        )
        local_loop_agent = LoopAgent(
            name="loop_runner",
            sub_agents=[local_sub_agent],
            max_iterations=3
        )
        loop_runners_cache[model_name] = InMemoryRunner(
            app_name=app_name,
            agent=local_loop_agent,
        )
    return loop_runners_cache[model_name]

async def loop_adk(prompt: str, model_name: str = "gemini-2.5-flash"):
    """Calls Gemini using the ADK Framework for loop execution."""
    local_runner = get_loop_runner(model_name)
    app_name = f"LoopApp_{model_name.replace('-', '_')}"
    # Ensure session exists for loop test
    await _ensure_session(local_runner.session_service, app_name, "session_loop")
    
    start_time = time.time()
    response_text = ""
    
    for event in local_runner.run(
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

structured_runners_cache = {}

def get_structured_runner(model_name: str):
    app_name = f"StructuredApp_{model_name.replace('-', '_')}"
    if model_name not in structured_runners_cache:
        local_structured_agent = Agent(
            name="structured_agent",
            model=model_name,
            instruction="You are a data extractor. Respond ONLY with a valid JSON array of objects.",
        )
        structured_runners_cache[model_name] = InMemoryRunner(
            app_name=app_name,
            agent=local_structured_agent,
        )
    return structured_runners_cache[model_name]

async def structured_adk(prompt: str, model_name: str = "gemini-2.5-flash"):
    """Calls Gemini using the ADK Framework and maintains session."""
    local_runner = get_structured_runner(model_name)
    app_name = f"StructuredApp_{model_name.replace('-', '_')}"
    # Ensure session exists for structured test
    await _ensure_session(local_runner.session_service, app_name, "session_structured")
    
    start_time = time.time()
    response_text = ""
    
    json_prompt = f"{prompt}. Each object must have 'name', 'lifespan', and 'habitat' fields."
    
    for event in local_runner.run(
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
