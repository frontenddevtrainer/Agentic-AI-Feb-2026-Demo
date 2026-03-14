import logging

logger = logging.getLogger(__name__)


def init_tracing():
    logger.info("Langfuse tracing disabled.")
    return None


def get_langfuse():
    return None
