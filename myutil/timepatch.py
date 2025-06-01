from pathlib import Path

# Path to the models.py file
models_path = Path("/workspaces/autoagent/backend/src/models.py")

# Read the original content
original_code = models_path.read_text()

# Check if fields already exist
if "created_at" in original_code and "updated_at" in original_code:
    updated_code = original_code  # No changes needed
else:
    # Add imports and fields
    if "from sqlalchemy import" in original_code:
        updated_code = original_code.replace(
            "from sqlalchemy import",
            "from sqlalchemy import Column, Integer, String, Boolean, DateTime"
        )
    else:
        updated_code = "from sqlalchemy import Column, Integer, String, Boolean, DateTime\n" + original_code

    if "from datetime import datetime" not in updated_code:
        updated_code = "from datetime import datetime\n" + updated_code

    # Insert timestamps into both models
    def insert_timestamps(class_name, code):
        start = code.find(f"class {class_name}(")
        end = code.find("\n\n", start)
        insert_point = code.find(")", start, end) + 1
        field_code = "\n    created_at = Column(DateTime, default=datetime.utcnow)\n    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)"
        return code[:insert_point] + field_code + code[insert_point:]

    updated_code = insert_timestamps("User", updated_code)
    updated_code = insert_timestamps("Developer", updated_code)

# Write the updated code back to models.py
models_path.write_text(updated_code)
"models.py updated with timestamp fields."
