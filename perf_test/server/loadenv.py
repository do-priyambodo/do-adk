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

# Set Vertex AI specific variables
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"

if "PROJECT_ID" in os.environ:
    os.environ["GOOGLE_CLOUD_PROJECT"] = os.environ["PROJECT_ID"]

if "GCP_REGION" in os.environ:
    os.environ["GOOGLE_CLOUD_LOCATION"] = os.environ["GCP_REGION"]

print("Environment variables loaded for Vertex AI")
