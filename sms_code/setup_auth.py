from playwright.sync_api import sync_playwright
import os

# Define a persistent user data directory in the current folder
USER_DATA_DIR = os.path.join(os.getcwd(), 'playwright_user_data')

def run():
    print(f"User Data Directory: {USER_DATA_DIR}")
    print("Launching browser...")
    
    with sync_playwright() as p:
        # Launch browser with persistent context
        context = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False, # Headless=False so user can see and interact
        )
        
        # Get the first page or create one
        page = context.pages[0] if context.pages else context.new_page()
        
        print("Navigating to Google Voice...")
        page.goto("https://voice.google.com")
        
        print("\n" + "="*50)
        print("ACTION REQUIRED: Log in to Google Voice in the opened browser.")
        print("Make sure you can see your messages.")
        print("When finished, press ENTER in this terminal to save and exit.")
        print("="*50 + "\n")
        
        input("Press Enter to finish setup...")
        
        context.close()
        print("Session saved successfully.")

if __name__ == "__main__":
    run()
