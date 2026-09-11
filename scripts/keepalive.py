import os
import sys
from playwright.sync_api import sync_playwright

URLS = [
    os.environ.get("STREAMLIT_APP_URL", "https://us-macro-dashboard.streamlit.app/"),
]

WAKE_NAMES = [
    "Yes, get this app back up!",
    "Yes, get this app back up",
]

SLEEP_HINTS = [
    "zzzz",
    "gone to sleep",
    "wake it back up",
    "would you like to wake",
]


def text_of(page) -> str:
    parts = [page.title() or "", page.content() or ""]
    for frame in page.frames:
        try:
            parts.append(frame.title() or "")
            parts.append(frame.locator("body").inner_text(timeout=2_000)[:2_000])
        except Exception:
            pass
    return "\n".join(parts).lower()


def click_wake(page) -> bool:
    # Outer page + iframes
    locators = [page.get_by_role("button", name=name) for name in WAKE_NAMES]
    for frame in page.frames:
        for name in WAKE_NAMES:
            locators.append(frame.get_by_role("button", name=name))

    for loc in locators:
        try:
            if loc.count() > 0:
                loc.first.click(timeout=5_000)
                return True
        except Exception:
            continue
    return False


def app_is_up(page) -> bool:
    selectors = "[data-testid='stAppViewContainer'], [data-testid='stApp']"
    if page.locator(selectors).count() > 0:
        return True
    for frame in page.frames:
        try:
            if frame.locator(selectors).count() > 0:
                return True
        except Exception:
            continue
    return False


def visit(page, url: str) -> str:
    page.goto(url, wait_until="domcontentloaded", timeout=120_000)
    page.wait_for_timeout(8_000)

    if click_wake(page):
        print(f"WAKE  {url}")
        page.wait_for_timeout(45_000)
        return "woke"

    if app_is_up(page):
        print(f"OK    {url}")
        return "ok"

    blob = text_of(page)
    if any(h in blob for h in SLEEP_HINTS):
        print(f"SLEEP-NO-BUTTON  {url}")
        return "sleep"

    # Live Streamlit shell with a real app title
    title = page.title() or ""
    if "· Streamlit" in title and "sleep" not in title.lower():
        print(f"OK    {url}  (title={title!r})")
        return "ok"

    print(f"UNKNOWN  {url}  title={title!r}")
    return "unknown"


def main() -> int:
    failed = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for url in URLS:
            url = (url or "").strip()
            if not url:
                continue
            try:
                status = visit(page, url)
                if status in {"unknown", "sleep"}:
                    failed += 1
            except Exception as e:
                print(f"ERROR {url}: {e}")
                failed += 1
        browser.close()
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
