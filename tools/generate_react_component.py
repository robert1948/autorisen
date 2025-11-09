#!/usr/bin/env python3
"""
React component generator from Figma analysis.

Takes the output from figma_api_client.py and generates React/TypeScript components
with proper props, styling, and structure based on Figma node hierarchy.
"""
import argparse
import json
import os
import re
from typing import Dict

COMPONENT_TEMPLATE = """import React from 'react';

{imports}

{interfaces}

{main_component}

export default {component_name};
"""

INTERFACE_TEMPLATE = """export interface {interface_name}Props {{
{props}
}}"""

COMPONENT_BODY_TEMPLATE = """export const {component_name}: React.FC<{interface_name}Props> = ({{
{destructured_props}
}}) => {{
  return (
{jsx_content}
  );
}};"""


def pascal_case(text: str) -> str:
    """Convert text to PascalCase."""
    words = re.sub(r"[^a-zA-Z0-9]", " ", text).split()
    return "".join(word.capitalize() for word in words if word)


def camel_case(text: str) -> str:
    """Convert text to camelCase."""
    pascal = pascal_case(text)
    return pascal[0].lower() + pascal[1:] if pascal else ""


def kebab_case(text: str) -> str:
    """Convert text to kebab-case."""
    return re.sub(r"[^a-zA-Z0-9]", "-", text).lower().strip("-")


class ReactComponentGenerator:
    """Generates React components from Figma analysis."""

    def __init__(self, analysis_data: Dict, tokens_data: Dict):
        self.analysis = analysis_data
        self.tokens = tokens_data
        self.component_name = "FigmaComponent"
        self.imports = set()

    def set_component_name(self, name: str):
        """Set the component name."""
        self.component_name = pascal_case(name)

    def _generate_props_interface(self) -> str:
        """Generate TypeScript interface for component props."""
        props = []

        # Add props for interactive elements
        for elem in self.analysis.get("interactive_elements", []):
            prop_name = camel_case(elem["suggested_prop"])
            props.append(f"  {prop_name}?: () => void;")

        # Add props for text elements
        for elem in self.analysis.get("text_elements", []):
            prop_name = camel_case(elem["suggested_prop"])
            props.append(f"  {prop_name}?: string;")

        # Add props for images
        for elem in self.analysis.get("images", []):
            prop_name = camel_case(elem["suggested_prop"])
            props.append(f"  {prop_name}?: string;")

        # Add common props
        props.extend(["  className?: string;", "  children?: React.ReactNode;"])

        interface_name = f"{self.component_name}"
        return INTERFACE_TEMPLATE.format(
            interface_name=interface_name, props="\n".join(props)
        )

    def _generate_css_classes(self) -> Dict[str, str]:
        """Generate CSS classes from design tokens."""
        classes = {}

        # Generate color classes
        for token_path, color in self.tokens.get("colors", {}).items():
            class_name = kebab_case(token_path.split("/")[-1])
            r = int(color.get("r", 0) * 255)
            g = int(color.get("g", 0) * 255)
            b = int(color.get("b", 0) * 255)
            a = color.get("a", 1)

            if a < 1:
                classes[f"bg-{class_name}"] = f"rgba({r}, {g}, {b}, {a})"
            else:
                classes[f"bg-{class_name}"] = f"rgb({r}, {g}, {b})"

        return classes

    def _generate_jsx_element(self, node: Dict, level: int = 0) -> str:
        """Generate JSX for a single node."""
        indent = "    " * (level + 2)
        node_type = node.get("type", "div")
        node_name = node.get("name", "Element")

        # Determine HTML element type
        html_element = "div"
        if "button" in node_name.lower():
            html_element = "button"
            self.imports.add("// Button functionality")
        elif node_type == "TEXT":
            html_element = "span"
        elif "image" in node_name.lower() or "img" in node_name.lower():
            html_element = "img"

        # Generate props
        props = []
        class_names = [f"figma-{kebab_case(node_name)}"]

        # Add event handlers for interactive elements
        if html_element == "button":
            prop_name = camel_case(f"{node_name}_handler")
            props.append(f"onClick={{{prop_name}}}")

        # Add src for images
        if html_element == "img":
            prop_name = camel_case(f"{node_name}_src")
            props.append(f'src={{{prop_name} || "/placeholder.png"}}')
            props.append(f'alt="{node_name}"')

        # Add className
        class_names_str = " ".join(class_names)
        props.append(f'className="{class_names_str}"')

        # Generate content
        if node_type == "TEXT":
            text_prop = camel_case(f"{node_name}_text")
            content = f"{{{text_prop} || '{node_name}'}}"
        elif html_element == "img":
            content = ""
        else:
            content = f"{{/* {node_name} content */}}"

        props_str = " ".join(props)

        if html_element == "img" or not content:
            return f"{indent}<{html_element} {props_str} />"
        else:
            return f"{indent}<{html_element} {props_str}>\n{indent}  {content}\n{indent}</{html_element}>"

    def _generate_jsx_content(self) -> str:
        """Generate the main JSX content."""
        jsx_lines = []

        # Generate elements based on hierarchy
        for node in self.analysis.get("hierarchy", []):
            if node.get("level", 0) <= 2:  # Limit depth for readability
                jsx_lines.append(self._generate_jsx_element(node, node.get("level", 0)))

        if not jsx_lines:
            jsx_lines = [
                '      <div className="figma-component">',
                "        <h2>Generated from Figma</h2>",
                "        <p>Component structure will be generated based on Figma analysis.</p>",
                "      </div>",
            ]

        return "\n".join(jsx_lines)

    def _generate_destructured_props(self) -> str:
        """Generate destructured props for component signature."""
        props = []

        # Add props for interactive elements
        for elem in self.analysis.get("interactive_elements", []):
            prop_name = camel_case(elem["suggested_prop"])
            props.append(prop_name)

        # Add props for text elements
        for elem in self.analysis.get("text_elements", []):
            prop_name = camel_case(elem["suggested_prop"])
            props.append(prop_name)

        # Add props for images
        for elem in self.analysis.get("images", []):
            prop_name = camel_case(elem["suggested_prop"])
            props.append(prop_name)

        # Add common props
        props.extend(["className", "children"])

        # Group into lines for readability
        if len(props) <= 3:
            return "  " + ", ".join(props)
        else:
            lines = []
            for i in range(0, len(props), 3):
                line_props = props[i : i + 3]
                lines.append(
                    "  " + ", ".join(line_props) + ("," if i + 3 < len(props) else "")
                )
            return "\n".join(lines)

    def generate_component(self) -> str:
        """Generate the complete React component."""
        interface_name = self.component_name

        # Generate imports
        imports_str = "\n".join(sorted(self.imports)) if self.imports else ""

        # Generate interface
        interface_str = self._generate_props_interface()

        # Generate component body
        component_body = COMPONENT_BODY_TEMPLATE.format(
            component_name=self.component_name,
            interface_name=interface_name,
            destructured_props=self._generate_destructured_props(),
            jsx_content=self._generate_jsx_content(),
        )

        return COMPONENT_TEMPLATE.format(
            imports=imports_str,
            interfaces=interface_str,
            main_component=component_body,
            component_name=self.component_name,
        )

    def generate_styles_css(self) -> str:
        """Generate CSS styles from design tokens."""
        css_rules = []
        css_rules.append("/* Generated from Figma design tokens */")

        # Generate color styles
        css_classes = self._generate_css_classes()
        for class_name, color_value in css_classes.items():
            css_rules.append(f".{class_name} {{ background-color: {color_value}; }}")

        # Generate typography styles
        for token_path, typography in self.tokens.get("typography", {}).items():
            class_name = kebab_case(token_path.split("/")[-1])
            css_rules.append(f".text-{class_name} {{")

            if typography.get("fontFamily"):
                css_rules.append(f"  font-family: {typography['fontFamily']};")
            if typography.get("fontSize"):
                css_rules.append(f"  font-size: {typography['fontSize']}px;")
            if typography.get("fontWeight"):
                css_rules.append(f"  font-weight: {typography['fontWeight']};")
            if typography.get("lineHeight"):
                css_rules.append(f"  line-height: {typography['lineHeight']}px;")

            css_rules.append("}")

        # Add base component styles
        css_rules.extend(
            [
                "",
                ".figma-component {",
                "  /* Base component styles */",
                "  display: flex;",
                "  flex-direction: column;",
                "}",
                "",
                ".figma-component * {",
                "  box-sizing: border-box;",
                "}",
            ]
        )

        return "\n".join(css_rules)


def main():
    parser = argparse.ArgumentParser(
        description="Generate React component from Figma analysis"
    )
    parser.add_argument(
        "--analysis-file", required=True, help="Path to component_analysis.json"
    )
    parser.add_argument(
        "--tokens-file", required=True, help="Path to design_tokens.json"
    )
    parser.add_argument(
        "--component-name", required=True, help="Name for the React component"
    )
    parser.add_argument(
        "--output-dir", required=True, help="Output directory for generated files"
    )

    args = parser.parse_args()

    # Load analysis data
    try:
        with open(args.analysis_file) as f:
            analysis_data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load analysis file: {e}")
        return 1

    # Load tokens data
    try:
        with open(args.tokens_file) as f:
            tokens_data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load tokens file: {e}")
        return 1

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Generate component
    generator = ReactComponentGenerator(analysis_data, tokens_data)
    generator.set_component_name(args.component_name)

    # Generate TypeScript component
    component_code = generator.generate_component()
    component_file = f"{args.output_dir}/{generator.component_name}.tsx"
    with open(component_file, "w") as f:
        f.write(component_code)

    # Generate CSS styles
    css_code = generator.generate_styles_css()
    css_file = f"{args.output_dir}/{generator.component_name}.css"
    with open(css_file, "w") as f:
        f.write(css_code)

    print("✅ Generated React component:")
    print(f"  • Component: {component_file}")
    print(f"  • Styles: {css_file}")
    print("\n📋 Component Analysis Summary:")
    print(
        f"  • Interactive elements: {len(analysis_data.get('interactive_elements', []))}"
    )
    print(f"  • Text elements: {len(analysis_data.get('text_elements', []))}")
    print(f"  • Images: {len(analysis_data.get('images', []))}")

    return 0


if __name__ == "__main__":
    exit(main())
