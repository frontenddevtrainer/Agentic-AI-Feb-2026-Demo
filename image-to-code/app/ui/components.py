import gradio as gr
from app.ui.chat_interface import sync_run_pipeline

PIPELINE_STAGES = """
### Pipeline Stages
1. **AnalyzerAgent** — reads the image with GPT-4o Vision
2. **PlannerAgent** — designs the implementation plan
3. **CoderAgent** — writes all source files
4. **ReviewerAgent** — fixes bugs & gaps
5. **PublisherAgent** — packages final JSON deliverable
"""

HOW_IT_WORKS = """
### How to use
1. Upload a **UI mockup**, **wireframe**, **flowchart**, **ER diagram**, or any technical image.
2. Optionally add extra instructions (language preference, framework, etc.).
3. Click **Generate Code** and watch the pipeline run step by step.
4. Copy the final code from the **PublisherAgent** JSON output.
"""

EXAMPLES = [
    ["Generate a React component that matches this mockup exactly."],
    ["Use Tailwind CSS for styling and TypeScript for the component."],
    ["Implement this as a Python FastAPI backend with Pydantic models."],
    ["Generate a Vue 3 Composition API component with SCSS."],
    ["Build this as a vanilla HTML/CSS/JS page — no frameworks."],
]

CUSTOM_CSS = """
footer { display: none !important; }
.pipeline-output .message { font-family: monospace; font-size: 0.85rem; }
"""


def create_ui() -> gr.Blocks:
    with gr.Blocks(title="Image → Code") as demo:
        gr.Markdown("# Image → Code Generator\nUpload any technical image and get working code.")

        with gr.Row():
            # Left column — inputs
            with gr.Column(scale=1):
                image_input = gr.Image(
                    label="Upload Image",
                    type="filepath",
                    height=300,
                )
                prompt_input = gr.Textbox(
                    label="Extra Instructions (optional)",
                    placeholder="e.g. Use React + TypeScript + Tailwind CSS",
                    lines=3,
                )
                submit_btn = gr.Button("Generate Code", variant="primary", size="lg")

                gr.Markdown(PIPELINE_STAGES)
                gr.Markdown(HOW_IT_WORKS)

            # Right column — streaming output
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(
                    label="Pipeline Output",
                    height=680,
                    render_markdown=True,
                    elem_classes=["pipeline-output"],
                )

        gr.Examples(
            examples=EXAMPLES,
            inputs=[prompt_input],
            label="Example Instructions",
        )

        submit_btn.click(
            fn=sync_run_pipeline,
            inputs=[image_input, prompt_input],
            outputs=[chatbot],
        )

    return demo
