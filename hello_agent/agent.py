from . import loadenv
from google.adk.agents import Agent

# Define the agent that the CLI will look for
root_agent = Agent(
    name="greeter_agent",
    model="gemini-2.5-flash",
    instruction="You are a helpful assistant. Answer the user's questions.",
)
