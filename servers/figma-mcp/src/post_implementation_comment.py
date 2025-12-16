import os
import sys
from dotenv import load_dotenv

# Add current directory to path so we can import sibling
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from figma_tools import post_comment

# Load .env from parent directory
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path)

FILE_KEY = "JKgEoJAzb5J74OaNAhTsql"
MESSAGE = """🚀 Implementation Update:
The Home page has been implemented in React matching the design.
Location: `src/pages/Home.tsx`
Status: Running on localhost:5173"""

print(f"Posting comment to Figma file: {FILE_KEY}...")

result = post_comment(FILE_KEY, MESSAGE)
print(result)
