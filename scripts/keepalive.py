import os
import sys
from playwright.sync_api import sync_playwright

URLS = [
    os.environ.get("STREAMLIT_APP_URL", "https://https://us-macro-dashboard.streamlit.app/"),
]

WAKE_BUTTONS = [
    "Yes, get this app back up!",
    "Yes, get this app back up",
]

def visit(page, url: str) -> str:
    page.goto(url, wait_until="domcontentloaded", timeout=120_000)
    page.wait_for_timeout(5_000)

    for name in WAKE_BUTTONS:
        btn = page.get_by_role("button", name=name)
        if btn.count() > 0:
            print(f"WAKE  {url}")
            btn.first.click()
            page.wait_for_timeout(45_000)
            return "woke"

    if page.locator("[data-testid='stAppViewContainer']").count() > 0:
        print(f"OK    {url}")
        return "ok"

    print(f"UNKNOWN  {url}  title={page.title()!r}")
    return "unknown"

def main() -> int:
    failed = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for url in URLS:
            url = url.strip()
            if not url:
                continue
            try:
                visit(page, url)
            except Exception as e:
                print(f"ERROR {url}: {e}")
                failed += 1
        browser.close()
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())
