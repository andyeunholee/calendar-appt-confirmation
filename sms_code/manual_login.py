
import sys
import os
import time
from playwright.sync_api import sync_playwright

# Ensure we can find the sms_code module components if needed, 
# but here we just need the path logic.
current_dir = os.path.dirname(os.path.abspath(__file__))
msg_user_data_dir = os.path.join(current_dir, 'playwright_user_data')

def login():
    print("----------------------------------------------------------------")
    print("OPENING BROWSER FOR MANUAL LOGIN...")
    print(f"User Data Directory: {msg_user_data_dir}")
    print("----------------------------------------------------------------")
    print("1. A browser window will open shortly.")
    print("2. Please SIGN IN to your Google Account.")
    print("3. Ensure you can see your Google Voice messages.")
    print("4. Once you are successfully logged in, close the browser window.")
    print("----------------------------------------------------------------")

    with sync_playwright() as p:
        # Launch persistent context
        # We use the exact same directory as bulk_send.py
        context = p.chromium.launch_persistent_context(
            user_data_dir=msg_user_data_dir,
            headless=False, # Must be visible
            slow_mo=50,
            # Arguments to avoid "browser not secure" error
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-infobars',
            ],
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = context.pages[0] if context.pages else context.new_page()
        
        # Go to Google Voice
        page.goto("https://voice.google.com/messages")
        
        print("Browser launched. Waiting for you to close the browser window...")
        
        # Keep the script running until the browser context is closed by the user
        try:
            # We'll just wait indefinitely until the user closes the window
            # checking periodically
            while context.pages:
                time.sleep(1)
        except Exception as e:
            print("Browser closed or disconnected.")
            
        print("----------------------------------------------------------------")
        print("LOGIN SESSION SAVED.")
        print("You can now return to the App and try sending SMS again.")
        print("----------------------------------------------------------------")

if __name__ == "__main__":
    login()
