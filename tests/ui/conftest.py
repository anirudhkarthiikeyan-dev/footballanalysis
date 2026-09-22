"""Fixtures for the Playwright browser test suite. Kept separate from
tests/ (the fast pytest unit suite) because these tests launch a real
Streamlit server and a real browser - they're slower and need Playwright's
browser binaries installed (`python -m playwright install chromium`).

Run with: python -m pytest tests/ui/ -v
"""
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]


def _find_free_port() -> int:
    # Binding to port 0 asks the OS for any free ephemeral port - avoids
    # collisions with a leftover process from a previous test run still
    # holding a hardcoded port (which previously caused this whole suite
    # to silently skip instead of testing anything).
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("localhost", 0))
        return s.getsockname()[1]


def _wait_for_server(url: str, timeout: float = 45.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(url, timeout=2)
            return True
        except Exception:
            time.sleep(0.5)
    return False


@pytest.fixture(scope="session")
def streamlit_server():
    test_port = _find_free_port()
    base_url = f"http://localhost:{test_port}"

    log_path = ROOT / "tests" / "ui" / "_server.log"
    log_file = open(log_path, "w", encoding="utf-8")
    proc = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run", "app/Home.py",
            "--server.headless", "true", "--server.port", str(test_port),
            "--browser.gatherUsageStats", "false",
            "--server.runOnSave", "false",
        ],
        cwd=str(ROOT),
        stdout=log_file,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        if not _wait_for_server(base_url):
            proc.terminate()
            log_file.close()
            pytest.fail(f"Streamlit test server did not start within timeout. See {log_path}")
        yield base_url
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        log_file.close()


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


@pytest.fixture
def page(browser):
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    pg = context.new_page()
    pg.set_default_navigation_timeout(60000)
    pg.set_default_timeout(60000)
    yield pg
    context.close()
