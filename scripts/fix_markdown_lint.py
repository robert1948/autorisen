#!/usr/bin/env python3
"""
Script to fix remaining markdown linting issues that markdownlint --fix can't handle automatically.
"""

import re
import sys
from pathlib import Path


def fix_ordered_list_prefixes(content):
    """Fix ordered list prefixes to use 1/1/1 style instead of 1/2/3."""
    lines = content.split("\n")
    fixed_lines = []

    for line in lines:
        # Fix ordered list prefixes: change any numbered list to 1.
        if re.match(r"^\s*[0-9]+\.\s", line):
            # Extract the indentation and replace the number with 1
            match = re.match(r"^(\s*)([0-9]+)(\.\s.*)", line)
            if match:
                indentation, number, rest = match.groups()
                if number != "1":  # Only fix if it's not already 1
                    line = indentation + "1" + rest
        fixed_lines.append(line)

    return "\n".join(fixed_lines)


def fix_fenced_code_language(content):
    """Add language specification to fenced code blocks."""
    # Replace ``` with ```text when no language is specified
    content = re.sub(r"^```\s*$", "```text", content, flags=re.MULTILINE)
    return content


def fix_multiple_h1_headers(content):
    """Convert multiple H1 headers to H2 after the first one."""
    lines = content.split("\n")
    fixed_lines = []
    h1_count = 0

    for line in lines:
        if line.startswith("# "):
            h1_count += 1
            if h1_count > 1:
                line = "##" + line[1:]  # Convert H1 to H2
        fixed_lines.append(line)

    return "\n".join(fixed_lines)


def process_file(file_path):
    """Process a single markdown file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Apply fixes
        content = fix_ordered_list_prefixes(content)
        content = fix_fenced_code_language(content)
        content = fix_multiple_h1_headers(content)

        # Write back if changed
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ Fixed: {file_path}")
            return True
        else:
            return False

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False


def main():
    """Main function to process all markdown files."""
    project_root = Path(__file__).parent.parent

    # Find all markdown files
    md_files = []
    for pattern in ["**/*.md"]:
        md_files.extend(project_root.glob(pattern))

    # Filter out excluded directories
    excluded_dirs = {"node_modules", ".git", "client/dist"}
    md_files = [f for f in md_files if not any(exc in str(f) for exc in excluded_dirs)]

    print(f"🔍 Found {len(md_files)} markdown files to check")

    fixed_count = 0
    for file_path in sorted(md_files):
        if process_file(file_path):
            fixed_count += 1

    print(f"✅ Fixed {fixed_count} files")

    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        # Run markdownlint to verify fixes
        import subprocess

        result = subprocess.run(
            [
                "markdownlint",
                "**/*.md",
                "--ignore",
                "node_modules",
                "--ignore",
                "client/dist",
                "--ignore",
                ".git",
            ],
            cwd=project_root,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("🎉 All markdown files now pass linting!")
        else:
            print("⚠️  Some issues remain:")
            print(result.stdout)


if __name__ == "__main__":
    main()
