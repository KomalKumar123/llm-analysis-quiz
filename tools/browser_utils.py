from typing import Dict
import requests


def load_quiz_page(url: str) -> Dict[str, str]:
    """
    Try to load a JS-rendered page with Playwright.
    If Playwright is not available or crashes (e.g., on some hosts),
    fall back to a simple requests.get.

    Returns: {"html": ..., "text": ...}
    """
    # First try Playwright
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            context = browser.new_context()
            page = context.new_page()
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(500)  # allow JS to run

            html = page.content()
            text = page.inner_text("body")

            browser.close()

        return {"html": html, "text": text}
    except Exception:
        # Fallback: plain HTTP GET without JS.
        # This will still work for many quiz pages, including ones that just embed a link or JSON.
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        html = resp.text
        # Simple fallback: use HTML as text as well; our regexes mostly work on text/html both.
        return {"html": html, "text": html}
