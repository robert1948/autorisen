#!/bin/bash
# Complete Figma to React workflow
set -e

echo "🎨 AutoLocal Figma → React Component Generator"
echo "=============================================="

# Set defaults
NODE_ID="${1:-2:9}"
COMPONENT_NAME="${2:-TargetFrame}"
OUTPUT_DIR="./figma_analysis"

echo "📋 Configuration:"
echo "   Node ID: $NODE_ID"
echo "   Component Name: $COMPONENT_NAME"
echo "   Output Directory: $OUTPUT_DIR"

# Check environment
if [ -z "$FIGMA_API_TOKEN" ]; then
    echo "❌ FIGMA_API_TOKEN not set. Run setup first:"
    echo "   ./scripts/setup_figma_env.sh"
    echo "   source .env.local"
    exit 1
fi

if [ -z "$FIGMA_FILE_ID" ]; then
    export FIGMA_FILE_ID="gRtWgiHmLTrIZGvkhF2aUC"
fi

echo ""
echo "🔍 Step 1: Analyzing Figma node..."
mkdir -p "$OUTPUT_DIR"

python3 tools/figma_api_client.py \
    --token "$FIGMA_API_TOKEN" \
    --file-id "$FIGMA_FILE_ID" \
    --node-id "$NODE_ID" \
    --action all \
    --output-dir "$OUTPUT_DIR"

echo ""
echo "⚛️  Step 2: Generating React component..."
mkdir -p "client/src/components/generated"

python3 tools/generate_react_component.py \
    --analysis-file "$OUTPUT_DIR/component_analysis.json" \
    --tokens-file "$OUTPUT_DIR/design_tokens.json" \
    --component-name "$COMPONENT_NAME" \
    --output-dir "client/src/components/generated"

echo ""
echo "📊 Step 3: Results Summary"
echo "========================="

if [ -f "$OUTPUT_DIR/component_analysis.json" ]; then
    echo "📈 Component Analysis:"
    python3 -c "
import json
with open('$OUTPUT_DIR/component_analysis.json') as f:
    data = json.load(f)
print(f'  • Hierarchy levels: {len(data.get(\"hierarchy\", []))}')
print(f'  • Interactive elements: {len(data.get(\"interactive_elements\", []))}')
print(f'  • Text elements: {len(data.get(\"text_elements\", []))}')
print(f'  • Images: {len(data.get(\"images\", []))}')
print(f'  • Suggested props: {len(data.get(\"suggested_props\", []))}')
"
fi

echo ""
echo "📁 Generated Files:"
echo "  • Component: client/src/components/generated/$COMPONENT_NAME.tsx"
echo "  • Styles: client/src/components/generated/$COMPONENT_NAME.css"
echo "  • Analysis: $OUTPUT_DIR/"

echo ""
echo "🎯 Next Steps:"
echo "  1. Review the generated component"
echo "  2. Import it into your app:"
echo "     import $COMPONENT_NAME from './components/generated/$COMPONENT_NAME';"
echo "  3. Add it to your routing if it's a page component"

echo ""
echo "✅ Figma → React workflow complete!"