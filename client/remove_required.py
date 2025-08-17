#!/usr/bin/env python3

import re

def remove_required_attributes():
    file_path = "/home/robert/Documents/localstorm250722/client/src/pages/Register.jsx"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Remove required attributes from input elements
    content = re.sub(r'\s*required\s*', '', content)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("Removed all required attributes from Register.jsx")

if __name__ == "__main__":
    remove_required_attributes()
