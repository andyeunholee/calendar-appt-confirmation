import sys
import json
import os
import traceback

# Add current dir to sys.path to ensure we can import bulk_send
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

import bulk_send
import io

# Force UTF-8 encoding for stdout/stderr to handle emojis on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def run():
    try:
        # Read config file path from arguments
        if len(sys.argv) < 2:
            print("PROGRESS:Error: Internal Config Missing")
            return

        config_path = sys.argv[1]
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        phone_numbers = config.get('phone_numbers', [])
        message_text = config.get('message_text', '')

        # Define a callback to flush stdout so the parent process (Streamlit) sees update immediately
        def progress_callback(msg):
            # We use a special prefix to parse this in the main app
            print(f"PROGRESS:{msg}")
            sys.stdout.flush()

        group_mode = config.get('group_mode', False)

        bulk_send.bulk_send(
            phone_numbers=phone_numbers, 
            message_text=message_text,
            progress_callback=progress_callback,
            group_mode=group_mode
        )
        
    except Exception as e:
        print(f"PROGRESS:Critical Error detected in sub-process")
        print(f"ERROR_TRACE:{traceback.format_exc()}")
        sys.stdout.flush()

if __name__ == "__main__":
    run()
