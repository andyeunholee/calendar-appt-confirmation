import google.generativeai as genai
import os

api_key = "AIzaSyD7JWLRNm1CF1JfOQhWwORKiuiMaj-CGek"
genai.configure(api_key=api_key)

print("Listing available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Error: {e}")
