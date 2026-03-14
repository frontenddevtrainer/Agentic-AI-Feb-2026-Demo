from typing import Sequence

from autogen_agentchat.agents import BaseChatAgent

SELECTOR_PROMPT = """You are routing messages between specialized agents in an image-to-code pipeline.

Pipeline order:
1. AnalyzerAgent  — analyzes the uploaded image
2. PlannerAgent   — creates the implementation plan
3. CoderAgent     — writes all the code
4. ReviewerAgent  — reviews and corrects the code
5. PublisherAgent — packages the final deliverable

Select the NEXT agent based on the most recent message:
- If the last message contains ANALYSIS_COMPLETE  → select PlannerAgent
- If the last message contains PLAN_COMPLETE      → select CoderAgent
- If the last message contains CODE_COMPLETE      → select ReviewerAgent
- If the last message contains REVIEW_COMPLETE    → select PublisherAgent
- If the last message contains PUBLISH_READY      → pipeline is done (return PublisherAgent)
- Otherwise select the agent that logically comes next given the conversation.

Return ONLY the agent name, nothing else.
"""

ROUTING_MAP = {
    "ANALYSIS_COMPLETE": "PlannerAgent",
    "PLAN_COMPLETE": "CoderAgent",
    "CODE_COMPLETE": "ReviewerAgent",
    "REVIEW_COMPLETE": "PublisherAgent",
    "PUBLISH_READY": "PublisherAgent",
}


def selector_func(messages: Sequence) -> str | None:
    """Fast-path keyword routing; falls back to LLM selector on None."""
    if not messages:
        return "AnalyzerAgent"

    last = messages[-1]
    content = getattr(last, "content", "") or ""
    if isinstance(content, list):
        content = " ".join(str(c) for c in content)

    for keyword, agent_name in ROUTING_MAP.items():
        if keyword in content:
            return agent_name

    return None
