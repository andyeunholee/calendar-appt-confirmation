
import sys
import os

# Add parent dir to sys.path to allow imports if needed, though we are running from root
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

import bulk_send

print("--- Starting Debug Test ---")
try:
    # Use a dummy number for testing (won't actually send if we stop it or if logic fails before)
    # But wait, bulk_send actually tries to send.
    # Let's just try to launch the browser to see if it works.
    print(f"USER_DATA_DIR is: {bulk_send.USER_DATA_DIR}")
    print(f"Exists? {os.path.exists(bulk_send.USER_DATA_DIR)}")
    
    # Try a simple navigation
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        print("Playwright started.")
        print("Launching browser context...")
        context = p.chromium.launch_persistent_context(
            user_data_dir=bulk_send.USER_DATA_DIR,
            headless=True, # Start headless for debug to avoid popup, or False if we want to mimic user
        )
        print("Browser launched successfully.")
        page = context.new_page()
        page.goto("https://google.com")
        print("Navigated to Google.")
        context.close()
        print("Context closed.")

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()

print("--- End Debug Test ---")
