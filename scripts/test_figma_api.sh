#!/bin/bash
# Quick test script for Figma API connection
set -e

echo "🔍 Testing Figma API connection..."

# Check if token is set
if [ -z "$FIGMA_API_TOKEN" ]; then
    echo "❌ FIGMA_API_TOKEN not set. Please set it first:"
    echo "   export FIGMA_API_TOKEN='your_token_here'"
    exit 1
fi

# Check if file ID is set
if [ -z "$FIGMA_FILE_ID" ]; then
    echo "❌ FIGMA_FILE_ID not set. Setting from .env.figma..."
    export FIGMA_FILE_ID="gRtWgiHmLTrIZGvkhF2aUC"
fi

echo "📡 Testing API access to file: $FIGMA_FILE_ID"

# Test basic file access
curl -s -H "X-Figma-Token: $FIGMA_API_TOKEN" \
    "https://api.figma.com/v1/files/$FIGMA_FILE_ID" \
    | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if 'name' in data:
        print(f'✅ API connection successful!')
        print(f'   File name: {data[\"name\"]}')
        print(f'   Last modified: {data.get(\"lastModified\", \"unknown\")}')
        
        # Check if node 2:9 exists
        def find_node(node, target_id):
            if node.get('id') == target_id:
                return node
            for child in node.get('children', []):
                result = find_node(child, target_id)
                if result:
                    return result
            return None
        
        document = data.get('document', {})
        target_node = find_node(document, '2:9')
        
        if target_node:
            print(f'✅ Target node 2:9 found: \"{target_node.get(\"name\", \"Unnamed\")}\"')
        else:
            print('⚠️  Node 2:9 not found - you may need to check the node ID')
            
    elif 'err' in data:
        print(f'❌ API Error: {data[\"err\"]}')
        sys.exit(1)
    else:
        print('❌ Unexpected response format')
        sys.exit(1)
except json.JSONDecodeError:
    print('❌ Failed to parse API response')
    sys.exit(1)
"

echo "🎉 Ready to proceed with Figma integration!"