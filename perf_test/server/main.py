from fastapi import FastAPI
import loadenv  # Loads environment variables on import
from native_impl import chat_native, generate_native, tool_native
from adk_impl import chat_adk, generate_adk, tool_adk

app = FastAPI(
    title="ADK vs Native SDK Performance Comparison",
    description="API to compare performance between Google Gen AI Native SDK and ADK Framework.",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    from adk_impl import setup_session
    await setup_session()

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
async def run_native(scenario: str, prompt: str = "Hello", session_id: str = "session_123"):
    if scenario == "base":
        result = generate_native(prompt)
    elif scenario == "chat":
        result = chat_native(session_id, prompt)
    elif scenario == "tool":
        result = tool_native(prompt)
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
async def run_adk(scenario: str, prompt: str = "Hello", session_id: str = "session_123"):
    if scenario == "base":
        result = await generate_adk(prompt, session_id=session_id)
    elif scenario == "chat":
        result = await chat_adk(session_id, prompt)
    elif scenario == "tool":
        result = await tool_adk(prompt)
    else:
        return {"error": f"Scenario '{scenario}' not supported for ADK Framework"}
        
    return {
        "mode": "adk",
        "scenario": scenario,
        "prompt": prompt,
        "response": result["response"],
        "latency_ms": result["latency_ms"]
    }
