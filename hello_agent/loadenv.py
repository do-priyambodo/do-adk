import os
import sys

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

# Map GEMINI_API_KEY to GOOGLE_API_KEY for the SDK
if "GEMINI_API_KEY" in os.environ:
    os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]

print("Environment variables loaded from env.local")
