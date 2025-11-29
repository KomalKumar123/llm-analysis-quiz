from playwright.sync_api import sync_playwright

def load_quiz_page(url: str) -> dict:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context()
        page = context.new_page()
        page.goto(url, wait_until="networkidle")
        # Let JS execute
        page.wait_for_timeout(500)
        html = page.content()
        text = page.inner_text("body")
        browser.close()
    return {"html": html, "text": text}
