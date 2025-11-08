#!/bin/bash
# Figma Design Sync and Update Workflow
set -e

echo "🎨 CapeWire Design System - Figma Sync Workflow"
echo "==============================================="

# Configuration
FIGMA_API_TOKEN="${FIGMA_API_TOKEN:-figd_qJLC2dz3ozgb8JzNQcX8WlejCdSFHsrwJB4Az1w3}"
FIGMA_FILE_ID="${FIGMA_FILE_ID:-gRtWgiHmLTrIZGvkhF2aUC}"
ANALYSIS_DIR="./figma_analysis"
COMPONENTS_DIR="client/src/components/generated"

# Parse command line arguments
ACTION="${1:-watch}"
NODE_ID="${2:-}"
COMPONENT_NAME="${3:-}"

show_help() {
    echo "Usage: $0 [ACTION] [NODE_ID] [COMPONENT_NAME]"
    echo ""
    echo "Actions:"
    echo "  watch           - Monitor Figma file for changes"
    echo "  scan            - Scan entire page for new frames"
    echo "  generate        - Generate component from specific node"
    echo "  update          - Update existing component"
    echo "  list            - List all frames in the file"
    echo ""
    echo "Examples:"
    echo "  $0 scan                     # Scan page for all frames"
    echo "  $0 generate 2:9 Frame1      # Generate component from node 2:9"
    echo "  $0 list                     # Show all available frames"
    echo "  $0 watch                    # Monitor for changes"
}

check_env() {
    if [ -z "$FIGMA_API_TOKEN" ]; then
        echo "❌ FIGMA_API_TOKEN not set"
        exit 1
    fi
    
    if [ -z "$FIGMA_FILE_ID" ]; then
        echo "❌ FIGMA_FILE_ID not set"
        exit 1
    fi
    
    echo "✅ Environment ready"
    echo "   File ID: $FIGMA_FILE_ID"
    echo "   Token: ${FIGMA_API_TOKEN:0:10}..."
    echo ""
}

list_frames() {
    echo "📋 Scanning Figma file for frames..."
    python3 tools/figma_api_client.py \
        --token "$FIGMA_API_TOKEN" \
        --file-id "$FIGMA_FILE_ID" \
        --node-id "0:1" \
        --action metadata \
        --output-dir "$ANALYSIS_DIR"
    
    echo ""
    echo "📊 Available Frames:"
    python3 -c "
import json
import sys

try:
    with open('$ANALYSIS_DIR/file_metadata.json') as f:
        data = json.load(f)
    
    def find_frames(node, level=0):
        indent = '  ' * level
        if node.get('type') == 'FRAME':
            name = node.get('name', 'Unnamed')
            node_id = node.get('id', 'Unknown')
            print(f'{indent}🖼️  {name} (node: {node_id})')
        
        for child in node.get('children', []):
            find_frames(child, level + 1)
    
    find_frames(data['document'])
    
except Exception as e:
    print(f'Error reading frames: {e}')
"
}

scan_page() {
    echo "🔍 Scanning entire page for components..."
    list_frames
    
    echo ""
    echo "🤖 Auto-detecting new frames to generate..."
    
    # TODO: Compare with existing frames.csv and suggest new components
    echo "💡 To generate a component from a frame, run:"
    echo "   $0 generate NODE_ID COMPONENT_NAME"
}

generate_component() {
    if [ -z "$NODE_ID" ] || [ -z "$COMPONENT_NAME" ]; then
        echo "❌ Missing NODE_ID or COMPONENT_NAME"
        echo "Usage: $0 generate NODE_ID COMPONENT_NAME"
        echo "Example: $0 generate 2:9 MyFrame"
        exit 1
    fi
    
    echo "⚛️  Generating React component: $COMPONENT_NAME"
    echo "   From node: $NODE_ID"
    echo ""
    
    # Step 1: Analyze the node
    echo "🔍 Step 1: Analyzing node structure..."
    python3 tools/figma_api_client.py \
        --token "$FIGMA_API_TOKEN" \
        --file-id "$FIGMA_FILE_ID" \
        --node-id "$NODE_ID" \
        --action analyze \
        --output-dir "$ANALYSIS_DIR"
    
    # Step 2: Extract design tokens
    echo "🎨 Step 2: Extracting design tokens..."
    python3 tools/figma_api_client.py \
        --token "$FIGMA_API_TOKEN" \
        --file-id "$FIGMA_FILE_ID" \
        --node-id "$NODE_ID" \
        --action tokens \
        --output-dir "$ANALYSIS_DIR"
    
    # Step 3: Generate React component
    echo "⚛️  Step 3: Generating React component..."
    mkdir -p "$COMPONENTS_DIR"
    python3 tools/generate_react_component.py \
        --analysis-file "$ANALYSIS_DIR/component_analysis.json" \
        --tokens-file "$ANALYSIS_DIR/design_tokens.json" \
        --component-name "$COMPONENT_NAME" \
        --output-dir "$COMPONENTS_DIR"
    
    # Step 4: Update frames tracking
    echo "📝 Step 4: Updating component tracking..."
    update_frames_csv "$NODE_ID" "$COMPONENT_NAME"
    
    echo ""
    echo "✅ Component generated successfully!"
    echo "   📁 Component: $COMPONENTS_DIR/$COMPONENT_NAME.tsx"
    echo "   🎨 Styles: $COMPONENTS_DIR/$COMPONENT_NAME.css"
    echo ""
    echo "🚀 To use in your app:"
    echo "   import $COMPONENT_NAME from './components/generated/$COMPONENT_NAME';"
}

update_frames_csv() {
    local node_id="$1"
    local component_name="$2"
    local csv_file="docs/figma/frames.csv"
    
    # Convert node ID format (2:9 -> 2_9 for filename safety)
    local safe_name=$(echo "$component_name" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/_/g')
    
    # Check if node already exists in CSV
    if grep -q "$node_id" "$csv_file" 2>/dev/null; then
        echo "📝 Node $node_id already tracked in $csv_file"
    else
        echo "📝 Adding $node_id to $csv_file"
        echo "$safe_name,$node_id,png,2,ui/,ui/" >> "$csv_file"
    fi
}

watch_changes() {
    echo "👀 Watching for Figma file changes..."
    echo "   File: $FIGMA_FILE_ID"
    echo "   Press Ctrl+C to stop"
    echo ""
    
    local last_modified=""
    
    while true; do
        # Get current file modification time
        current_modified=$(python3 -c "
import json
import urllib.request

headers = {'X-Figma-Token': '$FIGMA_API_TOKEN'}
req = urllib.request.Request('https://api.figma.com/v1/files/$FIGMA_FILE_ID', headers=headers)

try:
    with urllib.request.urlopen(req) as response:
        data = json.load(response)
        print(data.get('lastModified', ''))
except Exception as e:
    print('ERROR')
" 2>/dev/null)
        
        if [ "$current_modified" != "ERROR" ] && [ -n "$current_modified" ]; then
            if [ -n "$last_modified" ] && [ "$current_modified" != "$last_modified" ]; then
                echo "🔔 Design file updated! ($current_modified)"
                echo "💡 Run '$0 scan' to check for new components"
                echo ""
            fi
            last_modified="$current_modified"
        fi
        
        sleep 10
    done
}

# Main execution
case "$ACTION" in
    "help"|"-h"|"--help")
        show_help
        ;;
    "list")
        check_env
        list_frames
        ;;
    "scan")
        check_env
        scan_page
        ;;
    "generate")
        check_env
        generate_component
        ;;
    "update")
        check_env
        if [ -z "$NODE_ID" ]; then
            echo "❌ NODE_ID required for update"
            exit 1
        fi
        # Use existing component name if not provided
        COMPONENT_NAME="${COMPONENT_NAME:-$(echo $NODE_ID | sed 's/:/_/g')}"
        generate_component
        ;;
    "watch")
        check_env
        watch_changes
        ;;
    *)
        echo "❌ Unknown action: $ACTION"
        show_help
        exit 1
        ;;
esac