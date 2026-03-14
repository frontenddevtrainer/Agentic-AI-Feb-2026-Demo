import asyncio
import io
import logging
import uuid
from typing import AsyncGenerator

from autogen_agentchat.messages import MultiModalMessage, TextMessage
from autogen_agentchat.base import TaskResult
from autogen_core import Image as AGImage
from PIL import Image as PILImage

from app.orchestration.team import build_team
from app.monitoring.tracing import get_langfuse

logger = logging.getLogger(__name__)


def _load_image(image_path: str) -> AGImage:
    """Convert a file path to an AutoGen Image object."""
    with open(image_path, "rb") as f:
        data = f.read()
    pil_img = PILImage.open(io.BytesIO(data)).convert("RGB")
    return AGImage(pil_img)


async def run_pipeline(
    image_path: str | None,
    user_prompt: str,
    session_id: str,
) -> AsyncGenerator[list[dict], None]:
    """
    Async generator that streams agent messages as Gradio chatbot history.
    Yields after each agent turn so the UI updates incrementally.
    """
    if not image_path:
        yield [{"role": "assistant", "content": "Please upload an image first."}]
        return

    langfuse = get_langfuse()
    trace = None
    if langfuse:
        trace = langfuse.start_trace(
            name="image-to-code",
            session_id=session_id,
            input={"user_prompt": user_prompt},
        )

    history: list[dict] = []

    try:
        ag_image = _load_image(image_path)
        task = MultiModalMessage(
            content=[
                ag_image,
                f"Analyze the uploaded image and generate complete, working code for it.\n"
                f"Additional instructions from the user: {user_prompt}" if user_prompt.strip()
                else "Analyze the uploaded image and generate complete, working code for it.",
            ],
            source="user",
        )

        team = build_team()
        agent_count = 0

        async for event in team.run_stream(task=task):
            if isinstance(event, TaskResult):
                break

            source = getattr(event, "source", None)
            content = getattr(event, "content", None)

            if source is None or content is None:
                continue

            # Skip user echo
            if source == "user":
                continue

            if isinstance(content, list):
                content = "\n".join(str(c) for c in content if not hasattr(c, "data"))

            content = str(content)
            agent_count += 1

            if langfuse and trace:
                span = trace.start_span(name=source, input={"turn": agent_count})
                span.end(output={"text": content[:2000]})

            history.append({
                "role": "assistant",
                "content": f"**{source}**\n\n{content}",
            })
            yield list(history)

    except Exception as exc:
        logger.exception("Pipeline error in session %s", session_id)
        history.append({"role": "assistant", "content": f"Pipeline error: {exc}"})
        yield list(history)

    finally:
        if langfuse and trace:
            trace.end(output={"agent_turns": agent_count if "agent_count" in dir() else 0})
        if langfuse:
            langfuse.flush()


def sync_run_pipeline(image_path: str | None, user_prompt: str):
    """Sync wrapper for Gradio's generator interface."""
    session_id = str(uuid.uuid4())
    history: list[dict] = []

    loop = asyncio.new_event_loop()
    try:
        gen = run_pipeline(image_path, user_prompt, session_id)
        while True:
            try:
                history = loop.run_until_complete(gen.__anext__())
                yield history
            except StopAsyncIteration:
                break
    finally:
        loop.close()
