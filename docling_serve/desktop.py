"""Desktop wrapper for Docling Serve using pywebview."""

import logging
import multiprocessing
import time
from pathlib import Path

import httpx

from docling_serve.settings import docling_serve_settings, uvicorn_settings

logger = logging.getLogger(__name__)


def start_server(
    host: str,
    port: int,
    artifacts_path: Path | None,
    enable_ui: bool,
) -> None:
    """Start the FastAPI server in a separate process."""
    import uvicorn

    # Propagate the settings
    uvicorn_settings.host = host
    uvicorn_settings.port = port
    docling_serve_settings.artifacts_path = artifacts_path
    docling_serve_settings.enable_ui = enable_ui

    # Start the server
    uvicorn.run(
        app="docling_serve.app:create_app",
        factory=True,
        host=host,
        port=port,
        log_level="info",
    )


def run_desktop(
    host: str = "127.0.0.1",
    port: int = 5001,
    artifacts_path: Path | None = None,
    window_title: str = "Docling Serve",
    width: int = 1200,
    height: int = 800,
) -> None:
    """
    Run Docling Serve as a desktop application.

    Args:
        host: Host to bind the server to
        port: Port to bind the server to
        artifacts_path: Path to model artifacts
        window_title: Title of the desktop window
        width: Window width
        height: Window height
    """
    try:
        import webview
    except ImportError:
        logger.error(
            "pywebview is not installed. "
            "Install it with `pip install docling-serve[desktop]` "
            "or `pip install pywebview`"
        )
        raise

    # Start the server in a separate process
    server_process = multiprocessing.Process(
        target=start_server,
        args=(host, port, artifacts_path, True),
        daemon=True,
    )
    server_process.start()

    # Wait for the server to start with health check polling
    logger.info("Starting Docling Serve server...")
    url = f"http://{host}:{port}/health"
    max_retries = 30  # 30 seconds timeout
    retry_interval = 1  # 1 second between retries

    for attempt in range(max_retries):
        try:
            response = httpx.get(url, timeout=1.0)
            if response.status_code == 200:
                logger.info("Server is ready!")
                break
        except (httpx.ConnectError, httpx.RequestError):
            pass

        if attempt < max_retries - 1:
            time.sleep(retry_interval)
        else:
            logger.error("Server failed to start within the timeout period.")
            server_process.terminate()
            raise RuntimeError(
                "Server did not start within 30 seconds. "
                "Check if the port is already in use or if there are other errors."
            )

    # Build the UI URL
    url = f"http://{host}:{port}/ui"

    logger.info(f"Opening desktop window at {url}")

    # Create and start the webview window
    try:
        webview.create_window(
            title=window_title,
            url=url,
            width=width,
            height=height,
            resizable=True,
            fullscreen=False,
        )
        webview.start()
    finally:
        # Clean up the server process
        if server_process.is_alive():
            logger.info("Shutting down server...")
            server_process.terminate()
            server_process.join(timeout=5)
            if server_process.is_alive():
                server_process.kill()
