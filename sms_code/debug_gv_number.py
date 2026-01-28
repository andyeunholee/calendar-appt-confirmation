import time
import os
from playwright.sync_api import sync_playwright

# --- CONFIGURATION ---
TARGET_NUMBER = "4702531004"
MESSAGE_TEXT = "Debug test message for GV number"
USER_DATA_DIR = os.path.join(os.getcwd(), 'playwright_user_data')
# ---------------------

def debug_send():
    with sync_playwright() as p:
        print("Launching browser...")
        context = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            slow_mo=100 # Slower to see what happens
        )
        page = context.pages[0] if context.pages else context.new_page()
        
        print(f"Processing: {TARGET_NUMBER}")
        
        try:
            page.goto("https://voice.google.com/messages")
            page.wait_for_load_state("domcontentloaded")
            
            # 1. Click "Send new message"
            print("Opening new message dialog...")
            new_msg_btn = 'div[aria-label="Send new message"]'
            try:
                page.wait_for_selector(new_msg_btn, state="visible", timeout=5000)
                page.click(new_msg_btn)
            except:
                print("Standard button not found, trying generic selector...")
                page.click('div[role="button"][aria-label="Send new message"]')

            # 2. Enter phone number
            print("Entering phone number...")
            phone_input = 'input[placeholder="Type a name or phone number"]'
            page.wait_for_selector(phone_input, state="visible", timeout=10000)
            page.fill(phone_input, TARGET_NUMBER)
            time.sleep(3)
            
            # 3. Confirm recipient
            print("Confirming recipient...")
            page.keyboard.press("ArrowDown")
            time.sleep(1)
            page.keyboard.press("Enter")
            time.sleep(3) # Wait longer for conversation to load
            
            # 4. Focus Message Box
            print("Focusing message box...")
            message_box_selector = 'textarea[placeholder="Type a message"]'
            try:
                page.wait_for_selector(message_box_selector, state="visible", timeout=5000)
                page.click(message_box_selector)
            except:
                print("Message box not found with placeholder, dumping textareas...")
                textareas = page.query_selector_all("textarea")
                for i, ta in enumerate(textareas):
                    print(f"TA {i}: visible={ta.is_visible()}, placeholder={ta.get_attribute('placeholder')}")
                
                print("Trying Tab fallback...")
                page.keyboard.press("Tab")
                page.keyboard.press("Tab")
                page.keyboard.press("Tab")

            # 5. Type message
            print(f"Typing message... {MESSAGE_TEXT}")
            page.keyboard.type(MESSAGE_TEXT)
            time.sleep(2)
            
            # 6. Send - TRYING BUTTON CLICK FIRST
            print("Attempting to send via button click...")
            send_button_selector = 'div[aria-label="Send message"][role="button"]'
            # Sometimes the button is disabled until text is typed.
            
            try:
                btn = page.wait_for_selector(send_button_selector, state="visible", timeout=3000)
                # Check if disabled
                if btn.get_attribute("aria-disabled") == "true":
                    print("Send button is disabled!")
                else:
                    print("Clicking send button...")
                    btn.click()
            except Exception as e:
                print(f"Send button click failed ({e}), falling back to Enter key...")
                page.keyboard.press("Enter")

            time.sleep(5)
            
            # 7. Verification
            print("Verifying sent message...")
            # Look for the message text in the chat history
            # Message bubbles usually have the text.
            content = page.content()
            if MESSAGE_TEXT in content:
                print("VERIFICATION SUCCESS: Message text found in page content.")
            else:
                print("VERIFICATION FAILED: Message text NOT found in page content.")
                page.screenshot(path="debug_fail.png")
                print("Saved screenshot to debug_fail.png")

        except Exception as e:
            print(f"ERROR: {e}")
            page.screenshot(path="debug_error.png")
        
        print("\nFinished.")
        # Keep open briefly
        time.sleep(5)
        context.close()

if __name__ == "__main__":
    debug_send()
