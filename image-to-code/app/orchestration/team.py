from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination

from app.agents.analyzer import create_analyzer_agent
from app.agents.planner import create_planner_agent
from app.agents.coder import create_coder_agent
from app.agents.reviewer import create_reviewer_agent
from app.agents.publisher import create_publisher_agent
from app.agents.base import get_model_client
from app.orchestration.selector import SELECTOR_PROMPT, selector_func


def build_team() -> SelectorGroupChat:
    agents = [
        create_analyzer_agent(),
        create_planner_agent(),
        create_coder_agent(),
        create_reviewer_agent(),
        create_publisher_agent(),
    ]

    termination = (
        TextMentionTermination("PUBLISH_READY")
        | TextMentionTermination("TERMINATE")
        | MaxMessageTermination(max_messages=30)
    )

    return SelectorGroupChat(
        participants=agents,
        model_client=get_model_client(),
        termination_condition=termination,
        selector_prompt=SELECTOR_PROMPT,
        selector_func=selector_func,
        allow_repeated_speaker=False,
    )
