#!/usr/bin/env python3
"""
Figma Design System Helper - Interactive design workflow manager
"""
import json
import subprocess
import sys
import os
from pathlib import Path


class FigmaDesignHelper:
    def __init__(self):
        self.root_dir = Path(__file__).resolve().parent.parent
        self.figma_token = os.getenv(
            "FIGMA_API_TOKEN", "figd_qJLC2dz3ozgb8JzNQcX8WlejCdSFHsrwJB4Az1w3"
        )
        self.figma_file = os.getenv("FIGMA_FILE_ID", "gRtWgiHmLTrIZGvkhF2aUC")

    def show_menu(self):
        print("\n🎨 CapeWire Design System Helper")
        print("================================")
        print("1. 📋 List all frames")
        print("2. ⚛️  Generate component from frame")
        print("3. 🔄 Update existing component")
        print("4. 👀 Watch for design changes")
        print("5. 📊 Show design system status")
        print("6. 🚀 Quick demo page generator")
        print("0. 🚪 Exit")
        print()

    def list_frames(self):
        """List all available frames in the Figma file."""
        print("📋 Scanning Figma file for frames...")
        result = subprocess.run(
            ["./scripts/figma_sync.sh", "list"],
            capture_output=True,
            text=True,
            cwd=self.root_dir,
        )

        print(result.stdout)

    def generate_component(self):
        """Interactive component generation."""
        print("\n⚛️  Generate React Component")
        print("============================")

        # First, show available frames
        self.list_frames()

        print("\n💡 Enter the details for your new component:")
        node_id = input("🎯 Node ID (e.g., 2:9): ").strip()
        component_name = input("📝 Component Name (e.g., HeaderFrame): ").strip()

        if not node_id or not component_name:
            print("❌ Both Node ID and Component Name are required!")
            return

        print(f"\n🚀 Generating component '{component_name}' from node '{node_id}'...")

        result = subprocess.run(
            ["./scripts/figma_sync.sh", "generate", node_id, component_name],
            cwd=self.root_dir,
        )

        if result.returncode == 0:
            print(f"\n✅ Component '{component_name}' generated successfully!")
            self.offer_demo_page(component_name)
        else:
            print("\n❌ Component generation failed!")

    def offer_demo_page(self, component_name):
        """Offer to create a demo page for the new component."""
        create_demo = (
            input(f"\n🎨 Create demo page for {component_name}? (y/N): ")
            .strip()
            .lower()
        )

        if create_demo in ["y", "yes"]:
            self.create_demo_page(component_name)

    def create_demo_page(self, component_name):
        """Create a demo page for the component."""
        demo_content = f"""import React from 'react';
import {component_name} from '../components/generated/{component_name}';

const {component_name}Demo = () => {{
  return (
    <div style={{{{ padding: '20px', backgroundColor: '#f5f5f5', minHeight: '100vh' }}}}>
      <h1>🎨 {component_name} - Generated from Figma</h1>
      
      <div style={{{{ marginBottom: '20px' }}}}>
        <h2>Default Component</h2>
        <{component_name} />
      </div>

      <div style={{{{ marginBottom: '20px' }}}}>
        <h2>With Custom Props</h2>
        <{component_name} 
          className="custom-styling"
          // Add your custom props here
        />
      </div>

      <div style={{{{ marginTop: '40px', padding: '20px', backgroundColor: 'white', borderRadius: '8px' }}}}>
        <h3>📋 Component Details</h3>
        <ul>
          <li><strong>Component:</strong> {component_name}</li>
          <li><strong>Generated:</strong> {{{{ new Date().toLocaleString() }}}}</li>
          <li><strong>Source:</strong> CapeWire Design System (Figma)</li>
          <li><strong>Framework:</strong> React + TypeScript</li>
        </ul>
      </div>
    </div>
  );
}};

export default {component_name}Demo;
"""

        demo_path = self.root_dir / "client/src/pages" / f"{component_name}Demo.tsx"

        try:
            demo_path.write_text(demo_content)
            print(f"✅ Demo page created: {demo_path}")
            print(f"🌐 Access at: http://localhost:3000/{component_name.lower()}-demo")

            # Update App.tsx to include the new route
            self.add_route_to_app(component_name)

        except Exception as e:
            print(f"❌ Failed to create demo page: {e}")

    def add_route_to_app(self, component_name):
        """Add route to App.tsx for the demo page."""
        app_path = self.root_dir / "client/src/App.tsx"

        try:
            app_content = app_path.read_text()

            # Add import
            import_line = (
                f'import {component_name}Demo from "./pages/{component_name}Demo";'
            )
            if import_line not in app_content:
                # Find the last import and add after it
                lines = app_content.split("\n")
                import_index = -1
                for i, line in enumerate(lines):
                    if line.strip().startswith("import ") and line.strip().endswith(
                        ";"
                    ):
                        import_index = i

                if import_index >= 0:
                    lines.insert(import_index + 1, import_line)

            # Add route
            route_line = f'      <Route path="/{component_name.lower()}-demo" element={{<{component_name}Demo />}} />'
            if route_line not in app_content:
                # Find the last route and add before the closing </Routes>
                route_index = -1
                for i, line in enumerate(lines):
                    if "<Route path=" in line:
                        route_index = i

                if route_index >= 0:
                    lines.insert(route_index + 1, route_line)

            app_path.write_text("\n".join(lines))
            print(f"✅ Route added to App.tsx")

        except Exception as e:
            print(f"⚠️  Could not auto-add route: {e}")
            print(f"💡 Manually add this route to App.tsx:")
            print(
                f'   <Route path="/{component_name.lower()}-demo" element={{<{component_name}Demo />}} />'
            )

    def show_status(self):
        """Show current design system status."""
        print("\n📊 Design System Status")
        print("=======================")

        # Check generated components
        components_dir = self.root_dir / "client/src/components/generated"
        if components_dir.exists():
            components = list(components_dir.glob("*.tsx"))
            print(f"⚛️  Generated Components: {len(components)}")
            for comp in components:
                print(f"   • {comp.stem}")
        else:
            print("⚛️  Generated Components: 0")

        # Check frames tracking
        frames_csv = self.root_dir / "docs/figma/frames.csv"
        if frames_csv.exists():
            with open(frames_csv) as f:
                lines = f.readlines()
            print(f"📋 Tracked Frames: {len(lines) - 1}")  # -1 for header
        else:
            print("📋 Tracked Frames: 0")

        # Check analysis data
        analysis_dir = self.root_dir / "figma_analysis"
        if analysis_dir.exists():
            files = list(analysis_dir.glob("*.json"))
            print(f"📊 Analysis Files: {len(files)}")
        else:
            print("📊 Analysis Files: 0")

    def watch_changes(self):
        """Start watching for Figma changes."""
        print("\n👀 Starting Figma change watcher...")
        print("Press Ctrl+C to stop")

        subprocess.run(["./scripts/figma_sync.sh", "watch"], cwd=self.root_dir)

    def run(self):
        """Main interactive loop."""
        while True:
            self.show_menu()

            try:
                choice = input("Choose an option (0-6): ").strip()

                if choice == "0":
                    print("👋 Goodbye!")
                    break
                elif choice == "1":
                    self.list_frames()
                elif choice == "2":
                    self.generate_component()
                elif choice == "3":
                    print("🔄 Update feature coming soon!")
                elif choice == "4":
                    self.watch_changes()
                elif choice == "5":
                    self.show_status()
                elif choice == "6":
                    component_name = input("Component name for demo: ").strip()
                    if component_name:
                        self.create_demo_page(component_name)
                else:
                    print("❌ Invalid choice. Please try again.")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    helper = FigmaDesignHelper()
    helper.run()
