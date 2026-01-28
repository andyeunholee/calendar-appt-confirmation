
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
        # If it looks like a float or scientific notation, convert to float first
        if 'E' in s.upper() or '.' in s:
            try:
                f_val = float(s)
                s = str(int(f_val)) # Convert to int to remove decimal, then back to string
            except ValueError:
                pass # Not a valid float, treat as regular string
        
        # 2. Remove non-digits
        digits = "".join(filter(str.isdigit, s))
        
        return digits
    except Exception as e:
        print(f"Error normalizing {raw_input}: {e}")
        return ""

# Test Cases
test_cases = [
    ("7143003245", "7143003245"),
    ("7143003245.0", "7143003245"),
    ("7.143003245E+09", "7143003245"),
    ("7.14E+09", "7140000000"), # Data loss expected, but should be digits
    ("(714) 300-3245", "7143003245"),
    ("714-300-3245", "7143003245"),
    ("  714 300 3245  ", "7143003245"),
    ("invalid", ""),
]

print("Running tests...")
all_passed = True
for input_val, expected in test_cases:
    result = normalize_phone_number(input_val)
    if result == expected:
        print(f"[PASS] '{input_val}' -> '{result}'")
    else:
        print(f"[FAIL] '{input_val}' -> '{result}' (Expected: '{expected}')")
        all_passed = False

if all_passed:
    print("\nAll tests passed!")
else:
    print("\nSome tests failed.")
