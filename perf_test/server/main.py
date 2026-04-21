from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import loadenv  # Loads environment variables on import
from native_impl import chat_native, generate_native, tool_native, agent_native, stream_native, parallel_native, loop_native, structured_native
from adk_impl import chat_adk, generate_adk, tool_adk, agent_adk, stream_adk, parallel_adk, loop_adk, structured_adk

app = FastAPI(
    title="ADK vs Native SDK Performance Comparison",
    description="API to compare performance between Google Gen AI Native SDK and ADK Framework.",
    version="1.0.0"
)



@app.get("/")
def read_root():
    return {
        "message": "Welcome to the ADK vs Native SDK Comparison API",
        "endpoints": {
            "/v1/native": "Test raw Native SDK performance",
            "/v1/adk": "Test ADK Framework performance"
        }
    }

@app.get("/v1/native/{scenario}")
async def run_native(scenario: str, prompt: str = "Hello", session_id: str = "session_123", model_name: str = "gemini-2.5-flash"):
    if scenario == "base":
        result = await generate_native(prompt, model_name)
    elif scenario == "chat":
        result = await chat_native(session_id, prompt, model_name)
    elif scenario == "tool":
        result = await tool_native(prompt, model_name)
    elif scenario == "agent":
        result = await agent_native(prompt, model_name)
    elif scenario == "parallel":
        result = await parallel_native(prompt, model_name)
    elif scenario == "loop":
        result = await loop_native(prompt, model_name)
    elif scenario == "structured":
        result = await structured_native(prompt, model_name)
    elif scenario == "stream":
        return StreamingResponse(stream_native(prompt, model_name), media_type="text/plain")
    else:
        return {"error": f"Scenario '{scenario}' not supported for Native SDK"}
        
    return {
        "mode": "native",
        "scenario": scenario,
        "prompt": prompt,
        "response": result["response"],
        "latency_ms": result["latency_ms"]
    }

@app.get("/v1/adk/{scenario}")
async def run_adk(scenario: str, prompt: str = "Hello", session_id: str = "session_123", model_name: str = "gemini-2.5-flash"):
    if scenario == "base":
        result = await generate_adk(prompt, session_id, model_name)
    elif scenario == "chat":
        result = await chat_adk(session_id, prompt, model_name)
    elif scenario == "tool":
        result = await tool_adk(prompt, model_name)
    elif scenario == "agent":
        result = await agent_adk(prompt, model_name)
    elif scenario == "parallel":
        result = await parallel_adk(prompt, model_name)
    elif scenario == "loop":
        result = await loop_adk(prompt, model_name)
    elif scenario == "structured":
        result = await structured_adk(prompt, model_name)
    elif scenario == "stream":
        return StreamingResponse(stream_adk(prompt, model_name), media_type="text/plain")
    else:
        return {"error": f"Scenario '{scenario}' not supported for ADK Framework"}
        
    return {
        "mode": "adk",
        "scenario": scenario,
        "prompt": prompt,
        "response": result["response"],
        "latency_ms": result["latency_ms"]
    }
