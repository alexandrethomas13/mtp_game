import time
from playwright.sync_api import sync_playwright


def go_youtube():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        page = browser.new_page()

        page.goto("https://www.youtube.com")

        page.wait_for_selector("yt-core-attributed-string")

        sign_in = page.locator("yt-core-attributed-string")

        sign_in.click()

        time.sleep(10000)

        page.wait_for_selector("input[name='search_query']")
        page.fill("input[name='search_query']", "Trump")

        page.keyboard.press("Enter")

        page.wait_for_selector(
            "ytd-video-renderer ytd-thumbnail", timeout=100000)

        first_vid = page.locator("ytd-thumbnail").nth(0)
        first_vid.click()

        comments = page.locator('selector_of_element')

        comments.scroll_into_view_if_needed()

        print("Done1")

        page.wait_for_selector(
            "ytd-comment-simplebox-renderer", timeout=100000)

        page.evaluate('window.scrollBy(0, 500)')

        time.sleep(2)

        yt_comments = page.locator("ytd-comment-simplebox-renderer")
        yt_comments.click()

        print("Done2")

        page.evaluate('window.scrollBy(0, 500)')

        page.pause()


go_youtube()
