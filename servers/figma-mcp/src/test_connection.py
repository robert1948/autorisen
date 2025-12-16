import os
import requests
from dotenv import load_dotenv

# Load environment variables from the parent directory's .env file
# We assume this script is run from servers/figma-mcp/ or src/
load_dotenv()

FIGMA_BASE_URL = "https://api.figma.com/v1"
API_KEY = os.getenv("FIGMA_API_KEY")

def test_connection():
    if not API_KEY:
        print("❌ Error: FIGMA_API_KEY not found in environment variables.")
        print("   Please ensure you have created the .env file in servers/figma-mcp/")
        return

    print(f"🔑 Found API Key: {API_KEY[:4]}...{API_KEY[-4:] if len(API_KEY) > 8 else ''}")
    
    headers = {"X-Figma-Token": API_KEY}
    print("📡 Testing connection to Figma API (GET /v1/me)...")
    
    try:
        response = requests.get(f"{FIGMA_BASE_URL}/me", headers=headers)
        
        if response.status_code == 200:
            user = response.json()
            print(f"✅ Success! Authenticated as: {user.get('handle')} ({user.get('email')})")
        else:
            print(f"❌ Connection failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error connecting to Figma: {str(e)}")

if __name__ == "__main__":
    test_connection()
