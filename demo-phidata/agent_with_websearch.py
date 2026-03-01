from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.duckduckgo import DuckDuckGo

from dotenv import load_dotenv

load_dotenv()

def create_websearch_agent():
    """Creates a single conversational agent."""
    agent = Agent(
        name="Jarvis",
        model=OpenAIChat(id="gpt-4o"),
        description="You are a research assistant that searches the web for information",
        instructions=[
            "Always search for the most recent information.",
            "Include sources in your responses.",
            "Summarize findings clearly.",
        ],
        show_tool_calls=True,
        markdown=True,
        debug_mode=False, 
        tools=[DuckDuckGo()] 
    )
    return agent

if __name__ == "__main__":
    agent = create_websearch_agent()
    agent.print_response("what are the new movies release in hollywood", stream=True)