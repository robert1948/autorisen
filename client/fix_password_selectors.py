#!/usr/bin/env python3

import re

def fix_password_selectors():
    file_path = "/home/robert/Documents/localstorm250722/client/src/test/Login.test.jsx"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace getByLabelText(/password/i) with document.getElementById('password')
    content = re.sub(
        r'screen\.getByLabelText\(/password/i\)',
        "document.getElementById('password')",
        content
    )
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("Fixed password selectors in Login.test.jsx")

if __name__ == "__main__":
    fix_password_selectors()
