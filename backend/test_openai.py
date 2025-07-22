#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("Testing OpenAI API connection...")
print(f"API Key loaded: {os.getenv('OPENAI_API_KEY')[:10]}..." if os.getenv('OPENAI_API_KEY') else "No API key found")

try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Say hello!"}
        ],
        max_tokens=10
    )
    print("✅ API connection successful!")
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ API connection failed: {e}")
    print("This could be due to:")
    print("1. Invalid API key")
    print("2. No billing set up on OpenAI account")
    print("3. Network connectivity issues")
    print("4. API rate limits or quota exceeded")
