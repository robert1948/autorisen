#!/bin/bash

# Quick Context Update - One-line version
# Usage: ./quick_update.sh

CONTEXT_FILE="DEVELOPMENT_CONTEXT.md"
HEROKU_APP="capecraft"
CURRENT_DATE=$(date '+%B %d, %Y')
HEROKU_VERSION=$(heroku releases -a $HEROKU_APP --json | jq -r '.[0].version' 2>/dev/null)

if [ -f "$CONTEXT_FILE" ] && [ ! -z "$HEROKU_VERSION" ] && [ "$HEROKU_VERSION" != "null" ]; then
    sed -i "s/\*\*Last Updated\*\*:.*/\*\*Last Updated\*\*: $CURRENT_DATE/" "$CONTEXT_FILE"
    sed -i "s/\*\*Current Version\*\*:.*/\*\*Current Version\*\*: $HEROKU_VERSION (Heroku)/" "$CONTEXT_FILE"
    # Update the Latest Deployment Log section
    sed -i "/## Latest Deployment Log/,/\*\*Updated By\*\*:.*/ {
        s/\*\*Date\*\*:.*/\*\*Date\*\*: $CURRENT_DATE/
        s/\*\*Version\*\*:.*/\*\*Version\*\*: $HEROKU_VERSION/
        s/\*\*Updated By\*\*:.*/\*\*Updated By\*\*: Quick Update Script/
    }" "$CONTEXT_FILE"
    echo "✅ Updated context: v$HEROKU_VERSION on $CURRENT_DATE"
else
    echo "❌ Error: Could not update context"
fi
