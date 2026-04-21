import asyncio
import time
import httpx
from google.genai import Client
import os

# Load environment variables from env.local
env_path = "/usr/local/google/home/priyambodo/Coding/DO-PRIYAMBODO/do-adk/env.local"
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                try:
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value.strip("\"'")
                except ValueError:
                    pass

# Set Vertex AI specific variables
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"
if "PROJECT_ID" in os.environ:
    os.environ["GOOGLE_CLOUD_PROJECT"] = os.environ["PROJECT_ID"]
if "GCP_REGION" in os.environ:
    os.environ["GOOGLE_CLOUD_LOCATION"] = os.environ["GCP_REGION"]

print("Environment variables loaded for Vertex AI")

BASE_URL = "http://127.0.0.1:8001"
SCENARIOS = ["base", "structured", "chat", "tool", "agent", "parallel", "loop"]

MODEL_NAME = "gemini-2.5-flash-lite"

async def test_scenario(client: httpx.AsyncClient, mode: str, scenario: str):
    url = f"{BASE_URL}/v1/{mode}/{scenario}"
    params = {"prompt": "Tell me a short story", "model_name": MODEL_NAME}
    
    print(f"Testing {mode.upper()} - {scenario}... ", end="", flush=True)
    start_time = time.time()
    
    try:
        response = await client.get(url, params=params, timeout=60.0)
        
        if response.status_code == 200:
            latency_ms = int((time.time() - start_time) * 1000)
            data = response.json()
            print(f"[OK] ({latency_ms}ms)")
            return latency_ms
        else:
            print(f"  [Error] Status: {response.status_code} | {response.text}")
            return None
    except Exception as e:
        print(f"  [Exception] {e}")
        return None

async def test_stream(client: httpx.AsyncClient, mode: str):
    url = f"{BASE_URL}/v1/{mode}/stream"
    params = {"prompt": "Tell me a short story", "model_name": MODEL_NAME}
    
    print(f"Testing {mode.upper()} - stream...")
    start_time = time.time()
    ttft_ms = None
    total_time_ms = None
    
    try:
        async with client.stream("GET", url, params=params, timeout=60.0) as r:
            if r.status_code == 200:
                async for chunk in r.aiter_text():
                    if ttft_ms is None:
                        ttft_ms = int((time.time() - start_time) * 1000)
                        print(f"  [First Token] TTFT: {ttft_ms}ms")
                total_time_ms = int((time.time() - start_time) * 1000)
                print(f"  [Stream Done] Total Time: {total_time_ms}ms")
                return {"ttft": ttft_ms, "total": total_time_ms}
            else:
                print(f"  [Error] Status: {r.status_code}")
                return None
    except Exception as e:
        print(f"  [Exception] {e}")
        return None

async def run_all_tests(client: httpx.AsyncClient):
    """Runs all test scenarios and returns the raw results."""
    results = {}
    
    for scenario in SCENARIOS:
        results[scenario] = {
            "native": await test_scenario(client, "native", scenario),
            "adk": await test_scenario(client, "adk", scenario)
        }
        
    # Test streaming
    results["stream"] = {
        "native": await test_stream(client, "native"),
        "adk": await test_stream(client, "adk")
    }
    return results

def print_summary(results):
    """Prints the summary table based on results."""
    print("\n=== BENCHMARK SUMMARY ===")
    print(f"{'Scenario':<15} | {'Native (ms)':<12} | {'ADK (ms)':<12} | {'Diff (ms)':<10} | {'Diff (%)':<10} | {'Winner':<10}")
    print("-" * 85)
    for scenario, data in results.items():
        n = data["native"]
        a = data["adk"]
        
        if scenario == "stream":
            n_val = n["total"] if n else "N/A"
            a_val = a["total"] if a else "N/A"
            diff = abs(n["total"] - a["total"]) if n and a else "N/A"
            
            if n and a and n["total"] > 0:
                p_diff = int(((n["total"] - a["total"]) / n["total"]) * 100)
                p_diff_str = f"{p_diff:+}%"
            else:
                p_diff_str = "N/A"
                
            winner = "ADK" if n and a and a["total"] < n["total"] else "Native"
            print(f"{scenario:<15} | {n_val:<12} | {a_val:<12} | {diff:<10} | {p_diff_str:<10} | {winner:<10}")
            
            # Also print TTFT
            n_ttft = n["ttft"] if n else "N/A"
            a_ttft = a["ttft"] if a else "N/A"
            diff_ttft = abs(n["ttft"] - a["ttft"]) if n and a else "N/A"
            
            if n and a and n["ttft"] > 0:
                p_diff_ttft = int(((n["ttft"] - a["ttft"]) / n["ttft"]) * 100)
                p_diff_ttft_str = f"{p_diff_ttft:+}%"
            else:
                p_diff_ttft_str = "N/A"
                
            winner_ttft = "ADK" if n and a and a["ttft"] < n["ttft"] else "Native"
            print(f"{'  (TTFT)':<15} | {n_ttft:<12} | {a_ttft:<12} | {diff_ttft:<10} | {p_diff_ttft_str:<10} | {winner_ttft:<10}")
        else:
            n_val = n if n is not None else "N/A"
            a_val = a if a is not None else "N/A"
            diff = abs(n - a) if n is not None and a is not None else "N/A"
            
            if n and a and n > 0:
                p_diff = int(((n - a) / n) * 100)
                p_diff_str = f"{p_diff:+}%"
            else:
                p_diff_str = "N/A"
                
            winner = "ADK" if n is not None and a is not None and a < n else "Native"
            print(f"{scenario:<15} | {n_val:<12} | {a_val:<12} | {diff:<10} | {p_diff_str:<10} | {winner:<10}")

async def warm_up(client: httpx.AsyncClient):
    print("Warming up connections... ", end="", flush=True)
    try:
        await client.get(f"{BASE_URL}/v1/native/base", params={"prompt": "Hi"}, timeout=60.0)
        await client.get(f"{BASE_URL}/v1/adk/base", params={"prompt": "Hi"}, timeout=60.0)
        print("[OK]")
    except Exception as e:
        print(f"[Failed] {e}")

async def main():
    async with httpx.AsyncClient() as client:
        await warm_up(client)
        results = await run_all_tests(client)
        print_summary(results)
        
        # Real-time Analysis using Gemini
        print("\n=== COMPREHENSIVE ANALYSIS (Generated by Gemini) ===")
        
        try:
            client_ai = Client() # Will pick up GOOGLE_API_KEY from environment
            
            # Convert results to string for prompt
            results_str = ""
            for scenario, data in results.items():
                results_str += f"- {scenario}: Native={data['native']}, ADK={data['adk']}\n"
                
            prompt = f"""
            You are a performance analyst expert. Here are the results of a benchmark comparing Google Gen AI Native SDK vs ADK Framework for various scenarios:
            
            {results_str}
            
            Analyze these results. Explain why ADK might be winning or losing in specific scenarios based on the numbers (smaller is better). 
            Common factors include connection reuse, prompt length, and orchestration overhead.
            Keep the analysis concise, technical, and actionable. Be direct.
            """
            
            response = client_ai.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            print(response.text)
            
        except Exception as e:
            print(f"Failed to generate real-time analysis: {e}")

if __name__ == "__main__":
    asyncio.run(main())
