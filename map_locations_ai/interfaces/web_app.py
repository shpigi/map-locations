"""
Web interface for the location AI agent using Gradio.
"""

import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import gradio as gr
import yaml
from map_locations.common import LocationList, save_locations_to_yaml

from ..agent.pipeline import LocationPipeline


class WebInterface:
    """Web interface for the location AI agent."""

    def __init__(self):
        """Initialize the web interface."""
        self.pipeline = LocationPipeline()

    def process_text_input(self, text: str, region: str = "") -> Tuple[str, Optional[str]]:
        """
        Process text input and return results.

        Args:
            text: Input text containing location mentions
            region: Optional region hint

        Returns:
            Tuple of (status_message, download_file_path)
        """
        if not text.strip():
            return "Please enter some text to process.", None

        try:
            # Process text
            locations = self.pipeline.process_text(text, region=region if region else None)

            if not locations:
                return "No locations found in the provided text.", None

            # Create temporary file for download
            temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
            save_locations_to_yaml(locations, temp_file.name)

            return (
                f"✅ Found {len(locations)} locations! Click below to download.",
                temp_file.name,
            )

        except Exception as e:
            return f"❌ Error processing text: {str(e)}", None

    def process_url_input(self, urls_text: str, region: str = "") -> Tuple[str, Optional[str]]:
        """
        Process URL input and return results.

        Args:
            urls_text: Newline-separated URLs
            region: Optional region hint

        Returns:
            Tuple of (status_message, download_file_path)
        """
        if not urls_text.strip():
            return "Please enter URLs to process.", None

        # Parse URLs
        urls = [url.strip() for url in urls_text.split("\n") if url.strip()]

        if not urls:
            return "No valid URLs found.", None

        try:
            # Process URLs
            locations = self.pipeline.process_urls(urls, region=region if region else None)

            if not locations:
                return "No locations found from the provided URLs.", None

            # Create temporary file for download
            temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
            save_locations_to_yaml(locations, temp_file.name)

            return (
                f"✅ Found {len(locations)} locations! Click below to download.",
                temp_file.name,
            )

        except Exception as e:
            return f"❌ Error processing URLs: {str(e)}", None

    def enrich_locations_file(self, file_path: str) -> Tuple[str, Optional[str]]:
        """
        Enrich locations from uploaded file.

        Args:
            file_path: Path to uploaded YAML file

        Returns:
            Tuple of (status_message, download_file_path)
        """
        if not file_path:
            return "Please upload a YAML file with locations.", None

        try:
            # Load locations from uploaded file
            with open(file_path, "r") as f:
                data = yaml.safe_load(f)
            locations = data.get("locations", [])

            if not locations:
                return "No locations found in the uploaded file.", None

            # Enrich locations
            enriched_locations = self.pipeline.enrich_existing_locations(locations)

            # Create temporary file for download
            temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
            save_locations_to_yaml(enriched_locations, temp_file.name)

            return (
                f"✅ Enriched {len(enriched_locations)} locations! " "Click below to download.",
                temp_file.name,
            )

        except Exception as e:
            return f"❌ Error enriching locations: {str(e)}", None

    def create_interface(self) -> Any:  # type: ignore[no-any-return]
        """Create the Gradio interface."""
        with gr.Blocks(
            title="Map Locations AI Agent",
            theme=gr.themes.Soft(),
            css="""
            .main-header {
                text-align: center;
                margin-bottom: 2rem;
            }
            .tab-content {
                padding: 1rem;
            }
            """,
        ) as interface:
            # Header
            gr.HTML(
                """
                <div class="main-header">
                    <h1>🗺️ Map Locations AI Agent</h1>
                    <p>Automatically extract, enrich, and validate location data</p>
                </div>
                """
            )

            with gr.Tabs():
                # Text Processing Tab
                with gr.Tab("📝 Extract from Text"):
                    with gr.Column(elem_classes=["tab-content"]):
                        gr.Markdown(
                            """
                            Enter text containing location mentions (e.g., travel blog,
                            itinerary, or any text with place names).
                            """
                        )

                        text_input = gr.Textbox(
                            label="Text Input",
                            placeholder="Enter text mentioning locations...",
                            lines=5,
                        )
                        text_region = gr.Textbox(
                            label="Region Hint (Optional)",
                            placeholder="e.g., Paris, London, New York",
                        )

                        text_submit = gr.Button("🔍 Extract Locations", variant="primary")
                        text_status = gr.Textbox(label="Status", interactive=False)
                        text_download = gr.File(label="Download Results")

                        text_submit.click(
                            fn=self.process_text_input,
                            inputs=[text_input, text_region],
                            outputs=[text_status, text_download],
                        )

                # URL Processing Tab
                with gr.Tab("🔗 Extract from URLs"):
                    with gr.Column(elem_classes=["tab-content"]):
                        gr.Markdown(
                            """
                            Enter URLs to travel websites, blogs, or any pages
                            containing location information.
                            """
                        )

                        urls_input = gr.Textbox(
                            label="URLs (one per line)",
                            placeholder=(
                                "https://example.com/paris-guide\n" "https://travel-blog.com/london"
                            ),
                            lines=5,
                        )
                        urls_region = gr.Textbox(
                            label="Region Hint (Optional)",
                            placeholder="e.g., Europe, Asia, North America",
                        )

                        urls_submit = gr.Button("🔍 Extract Locations", variant="primary")
                        urls_status = gr.Textbox(label="Status", interactive=False)
                        urls_download = gr.File(label="Download Results")

                        urls_submit.click(
                            fn=self.process_url_input,
                            inputs=[urls_input, urls_region],
                            outputs=[urls_status, urls_download],
                        )

                # Enrichment Tab
                with gr.Tab("✨ Enrich Locations"):
                    with gr.Column(elem_classes=["tab-content"]):
                        gr.Markdown(
                            """
                            Upload a YAML file with existing location data to enrich
                            it with additional information like descriptions,
                            websites, and opening hours.
                            """
                        )

                        enrich_file = gr.File(
                            label="Upload YAML File",
                            file_types=[".yaml", ".yml"],
                        )

                        enrich_submit = gr.Button("✨ Enrich Locations", variant="primary")
                        enrich_status = gr.Textbox(label="Status", interactive=False)
                        enrich_download = gr.File(label="Download Results")

                        enrich_submit.click(
                            fn=self.enrich_locations_file,
                            inputs=[enrich_file],
                            outputs=[enrich_status, enrich_download],
                        )

            # Footer
            gr.HTML(
                """
                <div style="text-align: center; margin-top: 2rem; color: #666;">
                    <p>
                        🔧 Powered by AI •
                        📊 Data from Wikipedia, OpenStreetMap, and other sources •
                        🗺️ Compatible with map-locations visualization tools
                    </p>
                </div>
                """
            )

        return interface


def launch_web_interface(share: bool = False, port: int = 7860, host: str = "127.0.0.1") -> None:
    """
    Launch the web interface.

    Args:
        share: Whether to create a public shareable link
        port: Port number for the server
        host: Host address for the server
    """
    web_interface = WebInterface()
    interface = web_interface.create_interface()

    print("🚀 Launching Map Locations AI Agent web interface...")
    print(f"   URL: http://{host}:{port}")

    if share:
        print("   Share: Creating public link...")

    interface.launch(
        share=share,
        server_port=port,
        server_name=host,
        show_error=True,
    )


if __name__ == "__main__":
    launch_web_interface()
