#!/usr/bin/env python3
import re

# Read the file
with open('src/test/Register.test.jsx', 'r') as f:
    content = f.read()

# Replace all render patterns - more comprehensive approach
# First pattern: the standard nested BrowserRouter
pattern1 = r'render\(\s*<BrowserRouter>\s*<Register />\s*</BrowserRouter>,\s*{ wrapper: \(props\) => renderWithProviders\(props\.children\) }\s*\)'
replacement1 = 'renderWithProviders(<Register />)'

# Second pattern: any remaining render with BrowserRouter
pattern2 = r'render\(\s*<BrowserRouter>\s*<Register />\s*</BrowserRouter>,?\s*(?:{ wrapper: [^}]+ })?\s*\)'
replacement2 = 'renderWithProviders(<Register />)'

# Apply the replacements
content = re.sub(pattern1, replacement1, content, flags=re.MULTILINE | re.DOTALL)
content = re.sub(pattern2, replacement2, content, flags=re.MULTILINE | re.DOTALL)

# Also handle any remaining standalone render(...<BrowserRouter>...
pattern3 = r'render\(\s*<BrowserRouter>\s*(.*?)\s*</BrowserRouter>\s*\)'
def replace_render(match):
    inner_content = match.group(1).strip()
    return f'renderWithProviders({inner_content})'

content = re.sub(pattern3, replace_render, content, flags=re.MULTILINE | re.DOTALL)

# Write the file back
with open('src/test/Register.test.jsx', 'w') as f:
    f.write(content)

print("Fixed all remaining BrowserRouter patterns in Register test file")
