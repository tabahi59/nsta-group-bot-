# instagram_group_autobot_ready.py
# ⚠️ Test on secondary account first! Using automation may risk your Instagram account.

import asyncio
import re
import os
from playwright.async_api import async_playwright

# --- CONFIGURATION FROM ENVIRONMENT VARIABLES ---
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
GROUP_NAME = os.getenv("GROUP_NAME", "Your Group Name")
WELCOME_TEXT = os.getenv("WELCOME_TEXT", "🎉 Welcome to the group! Please follow the rules.")
BANNED_WORDS = [r"\b(noob)\b", r"\b(badword)\b"]  # customize banned words here

# --- SELECTORS (adjust if UI changes) ---
SELECTORS = {
    "group_thread": f'//span[text()="{GROUP_NAME}"]',
    "message_items": 'div[role="listitem"]',
    "message_text": 'div[role="listitem"] div > span',
    "username": 'div[role="listitem"] a',
    "input_box": 'textarea',
    "remove_menu": '//button[contains(text(),"Remove from group")]',
    "remove_confirm": '//button[contains(text(),"Remove")]'
}

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # cloud me headless = True
        context = await browser.new_context()
        page = await context.new_page()

        # Login
        await page.goto("https://www.instagram.com/accounts/login/")
        await page.wait_for_selector('input[name="username"]', timeout=20000)
        await page.fill('input[name="username"]', USERNAME)
        await page.fill('input[name="password"]', PASSWORD)
        await page.click('button[type="submit"]')
        await page.wait_for_timeout(8000)

        # Open inbox
        await page.goto("https://www.instagram.com/direct/inbox/")
        await page.wait_for_timeout(5000)

        # Open group chat
        await page.click(SELECTORS["group_thread"])
        await page.wait_for_timeout(5000)

        print(f"🚀 Monitoring group: {GROUP_NAME}")

        while True:
            await page.wait_for_timeout(3000)
            messages = await page.query_selector_all(SELECTORS["message_items"])
            if not messages:
                continue

            for m in messages[-5:]:
                text = (await m.inner_text()).strip().lower()

                # Welcome new members
                if "added" in text or "joined the group" in text:
                    try:
                        input_sel = SELECTORS["input_box"]
                        await page.fill(input_sel, WELCOME_TEXT)
                        await page.press(input_sel, "Enter")
                        print("✅ Sent welcome message.")
                    except Exception as e:
                        print("⚠️ Welcome failed:", e)

                # Check banned words
                for pattern in BANNED_WORDS:
                    if re.search(pattern, text):
                        try:
                            username_elem = await m.query_selector(SELECTORS["username"])
                            username = await username_elem.inner_text() if username_elem else "unknown"
                        except:
                            username = "unknown"

                        print(f"🚨 Banned word detected from {username}: {text}")

                        # ⚠️ Remove flow may need selector update
                        try:
                            await m.click(button="right")
                            await page.click(SELECTORS["remove_menu"])
                            await page.click(SELECTORS["remove_confirm"])
                            print(f"🛑 Removed {username} from group")
                        except Exception as e:
                            print("⚠️ Remove failed:", e)

            await page.wait_for_timeout(4000)

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("🛑 Bot stopped.")
