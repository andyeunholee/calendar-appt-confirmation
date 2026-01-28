import google.generativeai as genai

# Test the new API key
api_key = "AIzaSyBO-MelbWaGKgPdoaxBEcLVOWHPRjkvXI8"


try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    response = model.generate_content("Say 'API key is working!' if you can read this.")
    print("✅ API Key Test PASSED!")
    print(f"Response: {response.text}")
    
except Exception as e:
    print("❌ API Key Test FAILED!")
    print(f"Error: {e}")
