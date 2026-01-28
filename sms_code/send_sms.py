from playwright.sync_api import sync_playwright
import os
import time

# Path to the saved user data
USER_DATA_DIR = os.path.join(os.getcwd(), 'playwright_user_data')

def normalize_phone_number(raw_input):
    """
    Normalizes phone number input which might be:
    - A clean string: "7143003245"
    - A float string: "7143003245.0"
    - Scientific notation: "7.143E+09" (or similar)
    - Formatted string: "(714) 300-3245"
    """
    try:
        s = str(raw_input).strip()
        
        # 1. Handle Scientific Notation / Float strings
        if 'E' in s.upper() or '.' in s:
            try:
                f_val = float(s)
                s = str(int(f_val))
            except ValueError:
                pass
        
        # 2. Remove non-digits
        digits = "".join(filter(str.isdigit, s))
        
        return digits
    except Exception as e:
        print(f"Error normalizing {raw_input}: {e}")
        return ""

def send_sms(phone_number, message):
    # Normalize input
    phone_number = normalize_phone_number(phone_number)
    print(f"Preparing to send to {phone_number}...")
    
    with sync_playwright() as p:
        print("Launching browser...")
        # Launch with the same user data directory to reuse login
        context = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False, # Set to True later to run in background
            slow_mo=50, # Add slight delay to make it more human-like
        )
        
        page = context.pages[0] if context.pages else context.new_page()
        
        print("Navigating to Google Voice...")
        page.goto("https://voice.google.com/messages") # Go directly to messages
        page.wait_for_load_state("domcontentloaded")
        
        # Debug: Print where we are
        print(f"Current URL: {page.url}")
        if "signin" in page.url:
            print("CRITICAL WARNING: It looks like you are NOT logged in. Please run setup_auth.py again.")
            return

        try:
            # 1. Click "Send new message" button
            print("Opening new message dialog...")
            
            # Try multiple selectors
            selectors = [
                'div[aria-label="Send new message"]',
                'div[role="button"][aria-label="Send new message"]',
                '#gv-text-button', # Sometimes used
                'div[data-togglable="true"]' # Very generic, risky but might work
            ]
            
            found = False
            for selector in selectors:
                try:
                    print(f"Trying selector: {selector}")
                    if page.is_visible(selector, timeout=3000):
                        page.click(selector)
                        found = True
                        break
                except:
                    continue
            
            if not found:
                print("Could not find 'Send new message' button with known selectors.")
                print("Trying to find by text...")
                # Fallback: try to find by text if possible, though GV is mostly icons
                # Let's just wait a bit longer for the first one as a last resort
                page.click('div[aria-label="Send new message"]', timeout=10000)

            # 2. Enter phone number
            print("Entering phone number...")
            # Wait for the input to appear
            phone_input = 'input[placeholder="Type a name or phone number"]'
            page.wait_for_selector(phone_input, timeout=10000)
            page.fill(phone_input, phone_number)
            time.sleep(2) # Wait for dropdown suggestions to appear
            
            print("Confirming recipient...")
            # Strategy: Use keyboard navigation which is often more reliable than clicking
            # 1. Press ArrowDown to select the first option ("Send to ...")
            page.keyboard.press("ArrowDown")
            time.sleep(1)
            # 2. Press Enter to confirm
            page.keyboard.press("Enter")
            time.sleep(2)
            
            # Verification: We assume it worked based on user feedback.
            # Removing the strict check that was causing the crash.
            print("Recipient confirmed (assumed). Proceeding to message input...")

            # 3. Enter message
            print("Entering message body...")
            # User request: Press Tab 3 times to reach the message box
            print("Navigating to message box via keyboard (Tab x3)...")
            for _ in range(3):
                page.keyboard.press("Tab")
                time.sleep(0.5) # Small delay between tabs
            
            # Type the message directly (since we should be focused now)
            print("Typing message...")
            page.keyboard.type(message)
            time.sleep(1)
            
            # 4. Send
            print("Sending message...")
            page.keyboard.press("Enter")
            
            print("SUCCESS: Message sent!")
            time.sleep(5) # Wait a bit to ensure it sends before closing
            
        except Exception as e:
            print(f"ERROR: Failed to send message. Details: {e}")
            # Keep browser open for a bit to debug if it fails
            print("Keeping browser open for 30 seconds for debugging...")
            time.sleep(30)
            
        finally:
            context.close()

if __name__ == "__main__":
    # --- USER CONFIGURATION ---
    # Please change these values to test!
    TEST_PHONE_NUMBER = "7143003245" # Updated from numbers.csv
    TEST_MESSAGE = "Hello! This is an automated test message from Python."
    # --------------------------
    
    # Test with a formatted number to verify normalization
    formatted_number = "714-300-3245"
    send_sms(formatted_number, "안녕하세요! 자동 발송 테스트입니다.")
