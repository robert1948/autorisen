import json
import os
import sys
from dotenv import load_dotenv

# Add current directory to path so we can import sibling
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from figma_tools import get_file_structure

# Load .env from parent directory
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path)

FILE_KEY = "2xhcVwTZWQlk3PzRRGX8DR"

print(f"Inspecting Figma file: {FILE_KEY}...")

response = get_file_structure(FILE_KEY)

try:
    data = json.loads(response)
    if 'status' in data and data['status'] != 200 and 'err' in data:
         print(f"Error from Figma: {data['err']}")
    else:
        print(f"Project Name: {data.get('name', 'Unknown')}")
        print("\n--- Pages & Frames ---")
        document = data.get('document', {})
        children = document.get('children', [])
        
        for canvas in children:
            print(f"\nPage: {canvas.get('name')} (ID: {canvas.get('id')})")
            # Print ALL children types to debug
            for child in canvas.get('children', []):
                print(f"  - [{child.get('type')}] {child.get('name')} (ID: {child.get('id')})")
                
except json.JSONDecodeError:
    print("Failed to decode JSON response.")
    print(response)
except Exception as e:
    print(f"An error occurred: {e}")
