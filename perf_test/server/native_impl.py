import time
from google.genai import Client

def generate_native(prompt: str):
    """Calls Gemini using the raw Google Gen AI SDK."""
    client = Client()  # Automatically picks up GOOGLE_API_KEY from environment
    
    start_time = time.time()
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    
    latency_ms = int((time.time() - start_time) * 1000)
    
    return {
        "response": response.text,
        "latency_ms": latency_ms
    }

# In-memory store for native sessions
native_sessions = {}

def chat_native(session_id: str, prompt: str):
    """Calls Gemini using Native SDK and manually manages history."""
    from google.genai import Client
    from google.genai import types
    
    client = Client()
    
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
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
    )
    
    latency_ms = int((time.time() - start_time) * 1000)
    
    # Update history with current turn
    history.append(prompt)
    history.append(response.text)
    
    return {
        "response": response.text,
        "latency_ms": latency_ms
    }

def tool_native(prompt: str):
    """Calls Gemini using Native SDK and manually handles tool calls."""
    from google.genai import Client
    from google.genai import types
    
    client = Client()
    
    def get_mock_weather(location: str):
        return f"The weather in {location} is sunny and 25°C."
        
    start_time = time.time()
    final_text = ""
    
    try:
        # Step 1: Call model with tool in config
        config = types.GenerateContentConfig(tools=[get_mock_weather])
        response = client.models.generate_content(
            model="gemini-2.5-flash",
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
                        
                        response2 = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=contents
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
