import time
from google.genai import Client
from google.genai import types

# Shared client instance to reuse connection pool
client = Client()

# Shared config to ensure identical model parameters
shared_config = types.GenerateContentConfig(
    system_instruction="You are a helpful assistant.",
    temperature=1.0
)

async def generate_native(prompt: str, model_name: str = "gemini-2.5-flash"):
    """Calls Gemini using the raw Google Gen AI SDK (Async)."""
    start_time = time.time()
    
    response = await client.aio.models.generate_content(
        model=model_name,
        contents=prompt,
        config=shared_config
    )
    
    latency_ms = int((time.time() - start_time) * 1000)
    
    return {
        "response": response.text,
        "latency_ms": latency_ms
    }

# In-memory store for native sessions
native_sessions = {}

async def chat_native(session_id: str, prompt: str, model_name: str = "gemini-2.5-flash"):
    """Calls Gemini using Native SDK and manually manages history (Async)."""
    from google.genai import types
    
    if session_id not in native_sessions:
        native_sessions[session_id] = []
        
    history = native_sessions[session_id]
    
    start_time = time.time()
    
    # Build contents list with history
    contents = []
    for i, text in enumerate(history):
        role = "user" if i % 2 == 0 else "model"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=text)]))
        
    # Add current prompt
    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=prompt)]))
    
    response = await client.aio.models.generate_content(
        model=model_name,
        contents=contents,
        config=shared_config
    )
    
    latency_ms = int((time.time() - start_time) * 1000)
    
    # Update history with current turn
    history.append(prompt)
    history.append(response.text)
    
    return {
        "response": response.text,
        "latency_ms": latency_ms
    }

async def tool_native(prompt: str, model_name: str = "gemini-2.5-flash"):
    """Calls Gemini using Native SDK and manually handles tool calls (Async)."""
    from google.genai import types
    
    def get_mock_weather(location: str):
        return f"The weather in {location} is sunny and 25°C."
        
    start_time = time.time()
    final_text = ""
    
    try:
        # Step 1: Call model with tool in config
        config = types.GenerateContentConfig(
            tools=[get_mock_weather],
            system_instruction="You are a helpful assistant.",
            temperature=1.0
        )
        response = await client.aio.models.generate_content(
            model=model_name,
            contents=prompt,
            config=config
        )
        
        final_text = response.text  # Default response if no tool call
        
        # Step 2: Check for tool call safely
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    fc = part.function_call
                    if fc.name == "get_mock_weather":
                        # Execute tool
                        args = fc.args
                        location = args.get("location", "unknown")
                        tool_result = get_mock_weather(location)
                        
                        # Step 3: Send result back to model
                        contents = [
                            types.Content(role="user", parts=[types.Part.from_text(text=prompt)]),
                            response.candidates[0].content,
                            types.Content(role="tool", parts=[
                                types.Part.from_function_response(
                                    name="get_mock_weather",
                                    response={"result": tool_result}
                                )
                            ])
                        ]
                        
                        response2 = await client.aio.models.generate_content(
                            model=model_name,
                            contents=contents,
                            config=shared_config
                        )
                        final_text = response2.text
                        break
                        
    except Exception as e:
        final_text = f"Error in Native SDK flow: {str(e)}"
        
    latency_ms = int((time.time() - start_time) * 1000)
    
    return {
        "response": final_text,
        "latency_ms": latency_ms
    }

async def agent_native(prompt: str, model_name: str = "gemini-2.5-flash"):
    """Simulates a multi-agent flow by chaining two model calls (Async)."""
    from google.genai import types
    
    start_time = time.time()
    
    # Step 1: "Research" phase
    research_prompt = f"You are a researcher. Provide 3 short key facts about: {prompt}"
    response1 = await client.aio.models.generate_content(
        model=model_name,
        contents=research_prompt,
        config=shared_config
    )
    research_result = response1.text
    
    # Step 2: "Writer" phase
    writer_prompt = f"You are a professional writer. Turn this research into a polite paragraph:\n{research_result}"
    response2 = await client.aio.models.generate_content(
        model=model_name,
        contents=writer_prompt,
        config=shared_config
    )
    final_text = response2.text
    
    latency_ms = int((time.time() - start_time) * 1000)
    
    return {
        "response": final_text,
        "latency_ms": latency_ms
    }

async def stream_native(prompt: str, model_name: str = "gemini-2.5-flash"):
    """Streams Gemini response using Native SDK."""
    import asyncio
    response = client.models.generate_content_stream(
        model=model_name,
        contents=prompt,
        config=shared_config
    )
    for chunk in response:
        if chunk.text:
            yield chunk.text
            await asyncio.sleep(0)  # Yield control to event loop

async def parallel_native(prompt: str, model_name: str = "gemini-2.5-flash"):
    """Calls Gemini 3 times in parallel using asyncio.gather in Native SDK."""
    start_time = time.time()
    final_text = ""
    
    try:
        prompts = [
            f"Provide a positive view on: {prompt}",
            f"Provide a negative view on: {prompt}",
            f"Provide a neutral view on: {prompt}"
        ]
        
        async def call_model(p):
            response = await client.aio.models.generate_content(
                model=model_name,
                contents=p,
                config=shared_config
            )
            return response.text
            
        # Run in parallel using asyncio.gather
        results = await asyncio.gather(*(call_model(p) for p in prompts))
            
        final_text = "\n\n".join([f"--- Response {i+1} ---\n{text}" for i, text in enumerate(results)])
        
    except Exception as e:
        final_text = f"Error in Native Parallel flow: {str(e)}"
        
    latency_ms = int((time.time() - start_time) * 1000)
    
    return {
        "response": final_text,
        "latency_ms": latency_ms
    }

async def loop_native(prompt: str, model_name: str = "gemini-2.5-flash"):
    """Simulates a loop workflow by calling Gemini 3 times in a loop (Async)."""
    
    start_time = time.time()
    current_prompt = prompt
    final_text = ""
    
    # Run the task 3 times in a loop
    for i in range(3):
        response = await client.aio.models.generate_content(
            model=model_name,
            contents=current_prompt,
            config=shared_config
        )
        final_text += f"--- Iteration {i+1} ---\n{response.text}\n\n"
        # Pass the response to the next iteration to simulate context passing
        current_prompt = f"Continue based on this previous response:\n{response.text}"
        
    latency_ms = int((time.time() - start_time) * 1000)
    
    return {
        "response": final_text,
        "latency_ms": latency_ms
    }

async def structured_native(prompt: str, model_name: str = "gemini-2.5-flash"):
    """Calls Gemini and asks for strictly formatted JSON output (Async)."""
    
    start_time = time.time()
    
    json_prompt = f"{prompt}. Respond ONLY with a valid JSON array of objects. Each object must have 'name', 'lifespan', and 'habitat' keys."
    
    response = await client.aio.models.generate_content(
        model=model_name,
        contents=json_prompt,
        config=shared_config
    )
    
    latency_ms = int((time.time() - start_time) * 1000)
    
    return {
        "response": response.text,
        "latency_ms": latency_ms
    }
