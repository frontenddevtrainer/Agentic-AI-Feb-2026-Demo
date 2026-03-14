from autogen_agentchat.agents import AssistantAgent
from app.agents.base import get_model_client

SYSTEM_PROMPT = """You are a delivery engineer. You receive reviewed, finalized code and package
it into a clean, developer-ready output.

Your output must be a single JSON object with this exact schema:

{
  "image_type": "<what kind of image was analyzed>",
  "tech_stack": ["<language>", "<framework>", ...],
  "files": [
    {
      "path": "<relative/file/path>",
      "language": "<language identifier>",
      "content": "<complete file contents as a string>"
    }
  ],
  "setup_instructions": [
    "<step 1>",
    "<step 2>",
    ...
  ],
  "run_command": "<command to start/run the project>",
  "notes": "<any important caveats or follow-up actions>"
}

Rules:
- Extract EVERY file from the ### FILE: blocks in the reviewed code.
- Preserve exact file contents — do not truncate or summarize.
- setup_instructions must be actionable shell commands or numbered steps.
- Output ONLY the raw JSON — no markdown fences, no prose before or after.

End your response with: PUBLISH_READY
"""


def create_publisher_agent() -> AssistantAgent:
    return AssistantAgent(
        name="PublisherAgent",
        model_client=get_model_client(),
        system_message=SYSTEM_PROMPT,
    )
