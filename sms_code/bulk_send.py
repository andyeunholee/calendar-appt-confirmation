from playwright.sync_api import sync_playwright
import os
import time
import random

# Path to the saved user data
# Ensure we map to the correct location relative to this file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
USER_DATA_DIR = os.path.join(CURRENT_DIR, 'playwright_user_data')

def normalize_phone_number(raw_input):
    """
    Normalizes phone number string to digits only.
    """
    try:
        s = str(raw_input).strip()
        if 'E' in s.upper() or '.' in s:
            try:
                f_val = float(s)
                s = str(int(f_val))
            except ValueError:
                pass
        digits = "".join(filter(str.isdigit, s))
        return digits
    except:
        return ""

def bulk_send(phone_numbers, message_text, progress_callback=None, group_mode=False):
    """
    Sends SMS to a list of phone numbers using Google Voice via Playwright.
    If group_mode is True, sends ONE message to ALL numbers (Group Chat).
    If group_mode is False, sends individual messages to each number (Bulk Send).
    """
    if not phone_numbers:
        return

    def log(msg):
        if progress_callback:
            progress_callback(msg)
        else:
            print(msg)

    mode_str = "GROUP" if group_mode else "INDIVIDUAL"
    log(f"Initiating {mode_str} send for {len(phone_numbers)} recipients")

    with sync_playwright() as p:
        log("Launching browser...")
        try:
            # Use persistent context to keep login state
            context = p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                headless=False,
                slow_mo=50,
            )
            
            page = context.pages[0] if context.pages else context.new_page()
            
            log("Navigating to Google Voice...")
            page.goto("https://voice.google.com/messages")
            try:
                page.wait_for_load_state("domcontentloaded", timeout=15000)
            except:
                pass
            
            # Check login
            if "signin" in page.url or "AccountChooser" in page.url:
                log("CRITICAL: Not logged in. Please run setup_auth.py manually.")
                time.sleep(3)
                context.close()
                return

            if group_mode:
                # --- GROUP SEND MODE ---
                # 1. Click New Message ONCE
                try:
                    log("Starting Group Message...")
                    # Force reload to be safe
                    page.goto("https://voice.google.com/messages")
                    time.sleep(2)
                    
                    selectors = ['div[aria-label="Send new message"]', 'div[role="button"][aria-label="Send new message"]']
                    found_btn = False
                    for sel in selectors:
                        if page.is_visible(sel):
                            page.click(sel)
                            found_btn = True
                            break
                    
                    if not found_btn:
                        log("Error: Could not find 'Send new message' button.")
                        return

                    # 2. Add ALL recipients
                    # NOTE: placeholder might change/disappear after adding first person, so use aria-label
                    phone_input_sel = 'input[aria-label="Type a name or phone number"]'
                    try:
                        page.wait_for_selector(phone_input_sel, state="visible", timeout=8000)
                    except:
                        # Fallback generic input if specific label not found
                        phone_input_sel = 'input[aria-autocomplete="list"]'
                        page.wait_for_selector(phone_input_sel, state="visible", timeout=5000)
                    
                    for raw_num in phone_numbers:
                        target = normalize_phone_number(raw_num)
                        if not target: continue
                        
                        log(f"Adding recipient: {target}")
                        
                        # 1. Find the safe input selector
                        # We re-evaluate this every time because the DOM might change after adding a recipient
                        # (e.g., placeholder changes from "Type a name..." to "Add recipients")
                        recipient_selectors = [
                            'input[placeholder="Type a name or phone number"]',
                            'input[aria-label="Type a name or phone number"]',
                            'input[placeholder="Add recipients"]',
                            'input[aria-label="Add recipients"]',
                            'div[role="combobox"] input', # Generic combobox input often used for chips
                        ]
                        
                        active_selector = None
                        
                        # Try to find a visible, valid input
                        for sel in recipient_selectors:
                            try:
                                # Get all matching elements
                                elements = page.query_selector_all(sel)
                                for el in elements:
                                    if not el.is_visible(): continue
                                    
                                    # EXCLUDE Search bar logic
                                    aria_label = el.get_attribute("aria-label") or ""
                                    placeholder = el.get_attribute("placeholder") or ""
                                    
                                    if "Search" in aria_label or "Search" in placeholder:
                                        continue
                                        
                                    # Found a good candidate
                                    active_selector = sel # We use the selector string for page.click, or we can use the element handle
                                    # Let's use the element handle to click directly to be safe? 
                                    # Actually, mixing handles and selectors can be tricky with timeouts.
                                    # Let's sticking to the first valid specific selector found.
                                    break
                            except:
                                pass
                            if active_selector: break
                        
                        if not active_selector:
                            # Fallback: Just try to click focused element or last known good?
                            # Let's default to the standard one if nothing better found, hoping it works
                            active_selector = 'input[placeholder="Type a name or phone number"]'

                        # 2. Click to Focus
                        try:
                            page.click(active_selector)
                        except:
                            # Sometimes direct click implies strict visibility. 
                            pass

                        # 3. Type Number
                        page.keyboard.type(target, delay=50) 
                        time.sleep(0.5)
                        
                        # 4. Type Comma (User indicated strategy)
                        # Comma usually triggers the chip creation in mailing/SMS apps
                        page.keyboard.type(",")
                        
                        # 5. Wait for chip processing
                        time.sleep(1.0) 
                        
                        # Double check: sometimes comma leaves the input empty and ready for next.
                        # We loop back to Click->Type for the next number.
                        
                        # Verify? It's hard to verify without reading DOM, but the delays should help.
                    
                    # 3. Enter Message (Using "Smart Focus Hunter")
                    log("Hunting for message box...")
                    found_textarea = False
                    for i in range(8):
                        is_textarea = page.evaluate("document.activeElement.tagName === 'TEXTAREA'")
                        if is_textarea:
                            found_textarea = True
                            break
                        
                        aria_label = page.evaluate("document.activeElement.getAttribute('aria-label')")
                        if aria_label == "Type a message":
                            found_textarea = True
                            break

                        page.keyboard.press("Tab")
                        time.sleep(0.5)
                    
                    if not found_textarea:
                        log("Warning: Could not confirm focus on textarea. Clicking...")
                        try:
                            page.click('textarea[aria-label="Type a message"]', timeout=2000)
                        except:
                            pass

                    log("Typing group message...")
                    page.keyboard.type(message_text)
                    time.sleep(1)
                    
                    log("Sending...")
                    page.keyboard.press("Enter")
                    time.sleep(3)
                    log("Group Message Sent!")

                except Exception as e:
                    log(f"Group Send Error: {e}")

            else:
                # --- INDIVIDUAL SEND MODE (Loop) ---
                for idx, raw_num in enumerate(phone_numbers):
                    target_number = normalize_phone_number(raw_num)
                    if not target_number:
                        log(f"Skipping invalid number: {raw_num}")
                        continue

                    log(f"Preparing to send to {target_number} ({idx+1}/{len(phone_numbers)})...")
                    
                    # FORCE RELOAD/NAVIGATE
                    try:
                        log("Refreshing page...")
                        page.goto("https://voice.google.com/messages")
                        page.wait_for_load_state("domcontentloaded", timeout=10000)
                        time.sleep(2)
                    except:
                        pass

                    try:
                        # 1. Click 'Send new message'
                        selectors = ['div[aria-label="Send new message"]', 'div[role="button"][aria-label="Send new message"]']
                        found_btn = False
                        for i in range(3):
                            for sel in selectors:
                                if page.is_visible(sel):
                                    try:
                                        page.click(sel, timeout=2000)
                                        found_btn = True
                                        break
                                    except: pass
                            if found_btn: break
                            time.sleep(1)
                        
                        if not found_btn:
                            log(f"Failed to find 'Send' button for {target_number}")
                            continue

                        # 2. Enter Number
                        phone_input = 'input[placeholder="Type a name or phone number"]'
                        try:
                            page.wait_for_selector(phone_input, state="visible", timeout=8000)
                        except:
                            log("Phone input not found, skipping...")
                            continue

                        page.fill(phone_input, target_number)
                        time.sleep(1.5)
                        
                        page.keyboard.press("ArrowDown")
                        time.sleep(0.5)
                        page.keyboard.press("Enter")
                        time.sleep(1.0)

                        # 3. Enter Message (Smart Hunter)
                        log("Hunting for message box...")
                        found_textarea = False
                        for i in range(8):
                            is_textarea = page.evaluate("document.activeElement.tagName === 'TEXTAREA'")
                            if is_textarea:
                                found_textarea = True
                                break
                            aria_label = page.evaluate("document.activeElement.getAttribute('aria-label')")
                            if aria_label == "Type a message":
                                found_textarea = True
                                break
                            page.keyboard.press("Tab")
                            time.sleep(0.5)
                        
                        if not found_textarea:
                             try:
                                page.click('textarea[aria-label="Type a message"]', timeout=2000)
                             except: pass

                        log(f"Typing message to {target_number}...")
                        page.keyboard.type(message_text)
                        time.sleep(1)
                        
                        # 4. Send
                        page.keyboard.press("Enter")
                        log(f"Message sent to {target_number}")
                        time.sleep(3)
                        
                    except Exception as e:
                        log(f"Error sending to {target_number}: {e}")

        except Exception as e:
            log(f"Browser Init Error: {e}")
            import traceback
            log(traceback.format_exc())
            
        finally:
            log("Closing browser session.")


