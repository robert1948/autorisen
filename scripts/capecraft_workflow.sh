#!/bin/bash

# CapeCraft Design Implementation Workflow
# Automated script to implement the MindMup design specification

set -euo pipefail

echo "🎨 CapeCraft Design Implementation Workflow"
echo "==========================================="

# Configuration
FIGMA_FILE_ID="gRtWgiHmLTrIZGvkhF2aUC"
SPEC_FILE="docs/figma/capecraft_design_spec.json"
COMPONENTS_DIR="client/src/components/generated"
PAGES_DIR="client/src/pages"

# Check if spec file exists
if [[ ! -f "$SPEC_FILE" ]]; then
    echo "❌ Design spec file not found: $SPEC_FILE"
    exit 1
fi

echo "✅ Design specification found: $SPEC_FILE"

# Parse the spec file to get component list
echo "📋 Parsing design specification..."

# Define components to create based on MindMup structure
declare -a COMPONENTS=(
    "HomePage"
    "SubscribePage" 
    "AboutPage"
    "RegisterPage"
    "LoginPage"
)

# Function to create a single component
create_component() {
    local component_name="$1"
    local node_id="$2"
    
    echo "⚛️  Creating component: $component_name"
    
    # Use our existing Figma sync workflow
    if ./scripts/figma_sync.sh generate "$node_id" "$component_name"; then
        echo "✅ Successfully created $component_name"
        return 0
    else
        echo "⚠️  Warning: Could not create $component_name (node: $node_id)"
        return 1
    fi
}

# Function to create page wrapper
create_page_wrapper() {
    local component_name="$1"
    local route_path="$2"
    
    local page_file="$PAGES_DIR/${component_name}Page.tsx"
    
    if [[ -f "$page_file" ]]; then
        echo "ℹ️  Page wrapper already exists: $page_file"
        return 0
    fi
    
    echo "📄 Creating page wrapper: $page_file"
    
    cat > "$page_file" << EOF
import React from 'react';
import ${component_name} from '../components/generated/${component_name}';

const ${component_name}Page: React.FC = () => {
  return (
    <div className="page-container">
      <${component_name} />
    </div>
  );
};

export default ${component_name}Page;
EOF

    echo "✅ Created page wrapper: $page_file"
}

# Function to update App.tsx with new routes
update_app_routes() {
    echo "🔄 Updating App.tsx with CapeCraft routes..."
    
    # Create a backup
    cp client/src/App.tsx client/src/App.tsx.backup
    
    # Check if CapeCraft routes already exist
    if grep -q "CapeCraft routes" client/src/App.tsx; then
        echo "ℹ️  CapeCraft routes already exist in App.tsx"
        return 0
    fi
    
    # Add the route imports (this would need manual review)
    echo "⚠️  Please manually add these routes to App.tsx:"
    echo ""
    echo "import HomePage from './pages/HomePagePage';"
    echo "import SubscribePage from './pages/SubscribePagePage';"
    echo "import AboutPage from './pages/AboutPagePage';"
    echo "import RegisterPage from './pages/RegisterPagePage';"
    echo "import LoginPage from './pages/LoginPagePage';"
    echo ""
    echo "// Add these routes to your Routes component:"
    echo "<Route path=\"/\" element={<HomePage />} />"
    echo "<Route path=\"/subscribe\" element={<SubscribePage />} />"
    echo "<Route path=\"/about\" element={<AboutPage />} />"
    echo "<Route path=\"/register\" element={<RegisterPage />} />"
    echo "<Route path=\"/login\" element={<LoginPage />} />"
}

# Main workflow
main() {
    echo ""
    echo "🚀 Starting CapeCraft implementation workflow..."
    echo ""
    
    # Step 1: Check Figma connection
    echo "📡 Checking Figma connection..."
    if ./scripts/figma_sync.sh list > /dev/null 2>&1; then
        echo "✅ Figma connection successful"
    else
        echo "❌ Figma connection failed. Please check your API token."
        exit 1
    fi
    
    # Step 2: Create components directory
    mkdir -p "$COMPONENTS_DIR"
    mkdir -p "$PAGES_DIR"
    
    # Step 3: List available frames
    echo ""
    echo "📋 Available Figma frames:"
    ./scripts/figma_sync.sh list
    echo ""
    
    # Step 4: Interactive component creation
    echo "🎨 Ready to create CapeCraft components!"
    echo ""
    echo "Based on your MindMup design, we need to create:"
    for component in "${COMPONENTS[@]}"; do
        echo "  • $component"
    done
    echo ""
    
    read -p "Would you like to proceed with interactive component creation? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "🔨 Starting interactive component creation..."
        echo "For each component, you'll need to provide the Figma node ID"
        echo ""
        
        for component in "${COMPONENTS[@]}"; do
            echo "Creating: $component"
            echo "1. Find the frame in Figma for $component"
            echo "2. Copy the node ID from the URL or frame properties"
            read -p "Enter node ID for $component (or 'skip' to skip): " node_id
            
            if [[ "$node_id" != "skip" && -n "$node_id" ]]; then
                if create_component "$component" "$node_id"; then
                    create_page_wrapper "$component" "/${component,,}"
                fi
            else
                echo "⏭️  Skipping $component"
            fi
            echo ""
        done
        
        # Step 5: Update routes
        update_app_routes
        
    else
        echo "⏭️  Component creation skipped"
        echo ""
        echo "To create components manually, use:"
        echo "  make design-helper"
        echo "  or"
        echo "  ./scripts/figma_sync.sh generate <node-id> <component-name>"
    fi
    
    # Step 6: Summary
    echo ""
    echo "📊 Implementation Summary:"
    echo "========================"
    echo "✅ Design specification created: $SPEC_FILE"
    echo "✅ Implementation guide created: docs/checklists/capecraft_implementation_guide.md"
    
    # Check what was actually created
    created_components=0
    for component in "${COMPONENTS[@]}"; do
        if [[ -f "$COMPONENTS_DIR/${component}.tsx" ]]; then
            echo "✅ Component created: ${component}"
            ((created_components++))
        else
            echo "⏸️  Component pending: ${component}"
        fi
    done
    
    echo ""
    echo "📈 Progress: $created_components/${#COMPONENTS[@]} components created"
    echo ""
    echo "🎯 Next Steps:"
    echo "1. Review generated components in $COMPONENTS_DIR"
    echo "2. Update App.tsx with new routes"
    echo "3. Test the user flows from your MindMup"
    echo "4. Iterate on designs in Figma and regenerate as needed"
    echo ""
    echo "🔧 Available commands:"
    echo "  make design-helper    # Interactive component generator"
    echo "  make design-status    # Check implementation status"
    echo "  make design-watch     # Monitor for Figma changes"
}

# Run the main workflow
main "$@"