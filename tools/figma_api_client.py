#!/usr/bin/env python3
"""
Enhanced Figma REST API client for Zeonita (paid) plan.

Features:
- File inspection and metadata extraction
- Component analysis and design tokens
- Enhanced export with multiple formats
- Design system synchronization
- Node hierarchy traversal
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

API_BASE = "https://api.figma.com/v1"


@dataclass
class FigmaNode:
    """Represents a Figma node with metadata."""

    id: str
    name: str
    type: str
    children: List["FigmaNode"]
    styles: Dict[str, Any]
    properties: Dict[str, Any]


class FigmaApiClient:
    """Enhanced Figma API client with Zeonita features."""

    def __init__(self, token: str, file_id: str):
        self.token = token
        self.file_id = file_id
        self.headers = {"X-Figma-Token": token}

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make authenticated request to Figma API."""
        url = f"{API_BASE}/{endpoint}"
        if params:
            url += "?" + urllib.parse.urlencode(params)

        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read())
                if "err" in data:
                    raise Exception(f"Figma API error: {data['err']}")
                return data
        except Exception as e:
            raise Exception(f"Failed to fetch {url}: {e}")

    def get_file_metadata(self) -> Dict:
        """Get comprehensive file metadata."""
        return self._make_request(f"files/{self.file_id}")

    def get_file_nodes(
        self, node_ids: List[str], depth: int = 1, geometry: str = "paths"
    ) -> Dict:
        """Get detailed node information with enhanced metadata."""
        params = {
            "ids": ",".join(node_ids),
            "depth": depth,
            "geometry": geometry,
            "plugin_data": "shared",  # Zeonita feature
        }
        return self._make_request(f"files/{self.file_id}/nodes", params)

    def get_component_sets(self) -> Dict:
        """Get component sets from the file (Zeonita feature)."""
        return self._make_request(f"files/{self.file_id}/component_sets")

    def get_styles(self) -> Dict:
        """Get all styles (colors, text, effects) from the file."""
        return self._make_request(f"files/{self.file_id}/styles")

    def export_images(
        self,
        node_ids: List[str],
        format: str = "png",
        scale: str = "1",
        use_absolute_bounds: bool = False,
    ) -> Dict:
        """Enhanced image export with Zeonita capabilities."""
        params = {
            "ids": ",".join(node_ids),
            "format": format,
            "use_absolute_bounds": str(use_absolute_bounds).lower(),
        }

        if format == "png":
            params["scale"] = scale
        elif format == "svg":
            # Zeonita feature: Include node IDs in SVG export
            params["svg_include_id"] = "true"
            params["svg_simplify_stroke"] = "true"
        elif format == "pdf":
            # Zeonita feature: PDF with layers
            params["pdf_include_id"] = "true"

        return self._make_request(f"images/{self.file_id}", params)

    def extract_design_tokens(self, node_id: str) -> Dict:
        """Extract design tokens from a specific node (Zeonita enhancement)."""
        node_data = self.get_file_nodes([node_id], depth=3)

        tokens = {"colors": {}, "typography": {}, "spacing": {}, "effects": {}}

        def extract_from_node(node: Dict, path: str = ""):
            """Recursively extract tokens from node tree."""
            current_path = (
                f"{path}/{node.get('name', 'unnamed')}"
                if path
                else node.get("name", "root")
            )

            # Extract colors
            if "fills" in node:
                for fill in node["fills"]:
                    if fill.get("type") == "SOLID":
                        color = fill.get("color", {})
                        if color:
                            tokens["colors"][current_path] = {
                                "r": color.get("r", 0),
                                "g": color.get("g", 0),
                                "b": color.get("b", 0),
                                "a": color.get("a", 1),
                            }

            # Extract typography
            if "style" in node:
                style = node["style"]
                if "fontFamily" in style:
                    tokens["typography"][current_path] = {
                        "fontFamily": style.get("fontFamily"),
                        "fontSize": style.get("fontSize"),
                        "fontWeight": style.get("fontWeight"),
                        "lineHeight": style.get("lineHeightPx"),
                    }

            # Extract spacing (from constraints and layout)
            if "constraints" in node:
                constraints = node["constraints"]
                tokens["spacing"][current_path] = {
                    "horizontal": constraints.get("horizontal"),
                    "vertical": constraints.get("vertical"),
                }

            # Recursively process children
            for child in node.get("children", []):
                extract_from_node(child, current_path)

        nodes = node_data.get("nodes", {})
        if node_id in nodes:
            extract_from_node(nodes[node_id]["document"])

        return tokens

    def analyze_component_structure(self, node_id: str) -> Dict:
        """Analyze component structure for React mapping."""
        node_data = self.get_file_nodes([node_id], depth=5)

        analysis = {
            "hierarchy": [],
            "interactive_elements": [],
            "text_elements": [],
            "images": [],
            "suggested_props": [],
        }

        def analyze_node(node: Dict, level: int = 0):
            node_type = node.get("type", "")
            node_name = node.get("name", "Unnamed")

            analysis["hierarchy"].append(
                {
                    "level": level,
                    "name": node_name,
                    "type": node_type,
                    "id": node.get("id"),
                }
            )

            # Identify interactive elements
            if node_type in ["INSTANCE", "COMPONENT"] and "button" in node_name.lower():
                analysis["interactive_elements"].append(
                    {
                        "name": node_name,
                        "type": "button",
                        "suggested_prop": f"{node_name.lower().replace(' ', '_')}_handler",
                    }
                )

            # Identify text elements
            if node_type == "TEXT":
                text_content = node.get("characters", "")
                analysis["text_elements"].append(
                    {
                        "name": node_name,
                        "content": text_content,
                        "suggested_prop": f"{node_name.lower().replace(' ', '_')}_text",
                    }
                )

            # Identify images
            if node_type == "RECTANGLE" and node.get("fills"):
                for fill in node["fills"]:
                    if fill.get("type") == "IMAGE":
                        analysis["images"].append(
                            {
                                "name": node_name,
                                "suggested_prop": f"{node_name.lower().replace(' ', '_')}_src",
                            }
                        )

            # Recursively analyze children
            for child in node.get("children", []):
                analyze_node(child, level + 1)

        nodes = node_data.get("nodes", {})
        if node_id in nodes:
            analyze_node(nodes[node_id]["document"])

        # Generate suggested React props
        analysis["suggested_props"] = []
        for elem in analysis["interactive_elements"]:
            analysis["suggested_props"].append(elem["suggested_prop"])
        for elem in analysis["text_elements"]:
            analysis["suggested_props"].append(elem["suggested_prop"])
        for elem in analysis["images"]:
            analysis["suggested_props"].append(elem["suggested_prop"])

        return analysis


def main():
    parser = argparse.ArgumentParser(
        description="Enhanced Figma API client for Zeonita"
    )
    parser.add_argument("--token", required=True, help="Figma API token")
    parser.add_argument("--file-id", required=True, help="Figma file ID")
    parser.add_argument("--node-id", required=True, help="Target node ID")
    parser.add_argument(
        "--action",
        choices=["metadata", "export", "tokens", "analyze", "all"],
        default="all",
        help="Action to perform",
    )
    parser.add_argument(
        "--output-dir", default="./figma_output", help="Output directory"
    )
    parser.add_argument(
        "--format", default="png", choices=["png", "svg", "pdf"], help="Export format"
    )
    parser.add_argument("--scale", default="2", help="Export scale (for PNG)")

    args = parser.parse_args()

    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)

    client = FigmaApiClient(args.token, args.file_id)

    try:
        if args.action in ["metadata", "all"]:
            print("📊 Fetching file metadata...")
            metadata = client.get_file_metadata()
            with open(f"{args.output_dir}/file_metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)
            print(f"✓ Saved metadata to {args.output_dir}/file_metadata.json")

        if args.action in ["export", "all"]:
            print(f"🖼️  Exporting node {args.node_id} as {args.format}...")
            export_data = client.export_images([args.node_id], args.format, args.scale)

            if args.node_id in export_data.get("images", {}):
                image_url = export_data["images"][args.node_id]
                # Download the image
                req = urllib.request.Request(image_url)
                with urllib.request.urlopen(req) as response:
                    content = response.read()

                filename = f"node_{args.node_id.replace(':', '_')}.{args.format}"
                filepath = f"{args.output_dir}/{filename}"
                with open(filepath, "wb") as f:
                    f.write(content)
                print(f"✓ Exported image to {filepath}")
            else:
                print("❌ Failed to export image")

        if args.action in ["tokens", "all"]:
            print(f"🎨 Extracting design tokens from node {args.node_id}...")
            tokens = client.extract_design_tokens(args.node_id)
            with open(f"{args.output_dir}/design_tokens.json", "w") as f:
                json.dump(tokens, f, indent=2)
            print(f"✓ Saved design tokens to {args.output_dir}/design_tokens.json")

        if args.action in ["analyze", "all"]:
            print(f"🔍 Analyzing component structure for node {args.node_id}...")
            analysis = client.analyze_component_structure(args.node_id)
            with open(f"{args.output_dir}/component_analysis.json", "w") as f:
                json.dump(analysis, f, indent=2)
            print(
                f"✓ Saved component analysis to {args.output_dir}/component_analysis.json"
            )

            # Print summary
            print("\n📋 Component Analysis Summary:")
            print(
                f"  • Hierarchy levels: {len(set(h['level'] for h in analysis['hierarchy']))}"
            )
            print(f"  • Interactive elements: {len(analysis['interactive_elements'])}")
            print(f"  • Text elements: {len(analysis['text_elements'])}")
            print(f"  • Images: {len(analysis['images'])}")
            print(f"  • Suggested props: {len(analysis['suggested_props'])}")

        print(f"\n✅ Complete! Results saved to {args.output_dir}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
