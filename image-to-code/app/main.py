import logging

from app.config import settings
from app.monitoring.tracing import init_tracing
from app.ui.components import create_ui

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting Image → Code generator (env=%s)", settings.environment)
    init_tracing()

    ui = create_ui()
    import gradio as gr
    ui.launch(
        server_name=settings.gradio_server_name,
        server_port=settings.gradio_server_port,
        show_error=True,
        theme=gr.themes.Soft(),
    )


if __name__ == "__main__":
    main()
