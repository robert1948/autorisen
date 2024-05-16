import os
import sys

# Print Python version and executable
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

# Verify installation path
decouple_path = os.path.join(sys.prefix, 'Lib', 'site-packages', 'decouple')
print(f"decouple path: {decouple_path}")
print(f"Contents of decouple directory: {os.listdir(decouple_path)}")

try:
    from decouple import config
    print("decouple import successful")
except ImportError as e:
    print(f"ImportError: {e}")
