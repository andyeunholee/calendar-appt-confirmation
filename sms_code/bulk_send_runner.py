import csv
import os
import sys
from bulk_send import bulk_send

def run():
    # 1. Read Phone Numbers
    phone_numbers = []
    if os.path.exists("temp_numbers.csv"):
        with open("temp_numbers.csv", 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    phone_numbers.append(row[0])
    
    # 2. Read Message
    message_text = ""
    if os.path.exists("temp_message.txt"):
        with open("temp_message.txt", 'r', encoding='utf-8') as f:
            message_text = f.read()
            
    if not phone_numbers:
        print("Error: No phone numbers found in temp_numbers.csv")
        return

    if not message_text:
        print("Error: No message found in temp_message.txt")
        return

    # 3. Run Bulk Send
    # We define a simple callback that prints to stdout
    # The Streamlit app will capture this stdout
    def print_progress(msg):
        print(msg)
        sys.stdout.flush()

    print(f"Starting bulk send to {len(phone_numbers)} numbers...")
    sys.stdout.flush()
    
    try:
        bulk_send(phone_numbers=phone_numbers, message_text=message_text, progress_callback=print_progress)
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run()
