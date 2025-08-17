#!/bin/bash

# CapeControl Development Context Updater
# Automatically updates DEVELOPMENT_CONTEXT.md after each deployment
# Usage: ./update_context.sh

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CONTEXT_FILE="DEVELOPMENT_CONTEXT.md"
HEROKU_APP="capecraft"

echo -e "${BLUE}🚀 CapeControl Context Updater${NC}"
echo "================================================"

# Check if context file exists
if [ ! -f "$CONTEXT_FILE" ]; then
    echo -e "${RED}❌ Error: $CONTEXT_FILE not found${NC}"
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Not in a git repository${NC}"
    exit 1
fi

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo -e "${RED}❌ Error: Heroku CLI not installed${NC}"
    echo "Install from: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

echo -e "${YELLOW}📋 Gathering deployment information...${NC}"

# Get current date
CURRENT_DATE=$(date '+%B %d, %Y')
echo "📅 Current Date: $CURRENT_DATE"

# Get current Heroku version
echo "🔍 Fetching Heroku version..."
HEROKU_VERSION=$(heroku releases -a $HEROKU_APP --json | jq -r '.[0].version' 2>/dev/null)

if [ "$HEROKU_VERSION" = "null" ] || [ -z "$HEROKU_VERSION" ]; then
    echo -e "${RED}❌ Error: Could not fetch Heroku version${NC}"
    echo "Make sure you're logged into Heroku and have access to app: $HEROKU_APP"
    exit 1
fi

echo "🏷️  Current Heroku Version: $HEROKU_VERSION"

# Get git commit hash for reference
GIT_COMMIT=$(git rev-parse --short HEAD)
echo "📝 Git Commit: $GIT_COMMIT"

# Get git branch
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "🌿 Git Branch: $GIT_BRANCH"

echo -e "${YELLOW}✏️  Updating DEVELOPMENT_CONTEXT.md...${NC}"

# Backup the original file
cp "$CONTEXT_FILE" "${CONTEXT_FILE}.backup"
echo "💾 Created backup: ${CONTEXT_FILE}.backup"

# Update Last Updated field
sed -i "s/\*\*Last Updated\*\*:.*/\*\*Last Updated\*\*: $CURRENT_DATE/" "$CONTEXT_FILE"

# Update Current Version field  
sed -i "s/\*\*Current Version\*\*:.*/\*\*Current Version\*\*: $HEROKU_VERSION (Heroku)/" "$CONTEXT_FILE"

# Update the Latest Deployment Log section with current info
sed -i "/## Latest Deployment Log/,/\*\*Updated By\*\*:.*/ {
    s/\*\*Date\*\*:.*/\*\*Date\*\*: $CURRENT_DATE/
    s/\*\*Version\*\*:.*/\*\*Version\*\*: $HEROKU_VERSION/
    s/\*\*Git Commit\*\*:.*/\*\*Git Commit\*\*: $GIT_COMMIT/
    s/\*\*Git Branch\*\*:.*/\*\*Git Branch\*\*: $GIT_BRANCH/
    s/\*\*Updated By\*\*:.*/\*\*Updated By\*\*: Automated Context Updater/
}" "$CONTEXT_FILE"

echo -e "${GREEN}✅ Successfully updated $CONTEXT_FILE${NC}"

# Show what was changed
echo -e "${BLUE}📊 Changes made:${NC}"
echo "  • Last Updated: $CURRENT_DATE"
echo "  • Current Version: $HEROKU_VERSION (Heroku)"
echo "  • Added deployment log entry"

# Ask if user wants to commit the changes
echo ""
read -p "🤔 Do you want to commit these changes to git? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}📝 Committing changes...${NC}"
    git add "$CONTEXT_FILE"
    git commit -m "📄 Auto-update context: v$HEROKU_VERSION deployed on $CURRENT_DATE"
    echo -e "${GREEN}✅ Changes committed to git${NC}"
    
    # Ask if user wants to push
    read -p "🚀 Do you want to push to remote repository? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push origin $GIT_BRANCH
        echo -e "${GREEN}✅ Changes pushed to remote repository${NC}"
    fi
else
    echo -e "${YELLOW}⏭️  Skipping git commit${NC}"
fi

# Verify the application is running
echo -e "${YELLOW}🔍 Verifying application status...${NC}"
APP_STATUS=$(heroku ps -a $HEROKU_APP --json | jq -r '.[0].state' 2>/dev/null)

if [ "$APP_STATUS" = "up" ]; then
    echo -e "${GREEN}✅ Application is running successfully${NC}"
else
    echo -e "${YELLOW}⚠️  Application status: $APP_STATUS${NC}"
fi

# Quick health check
echo -e "${YELLOW}🏥 Running quick health check...${NC}"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://capecraft-65eeb6ddf78b.herokuapp.com/api/auth/health" || echo "000")

if [ "$HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ API health check passed${NC}"
else
    echo -e "${YELLOW}⚠️  API health check returned: $HTTP_STATUS${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Context update completed!${NC}"
echo "================================================"
echo -e "${BLUE}📋 Summary:${NC}"
echo "  • Context file updated with latest deployment info"
echo "  • Version: $HEROKU_VERSION"
echo "  • Date: $CURRENT_DATE"
echo "  • Application status verified"
echo ""
echo -e "${YELLOW}💡 Next steps:${NC}"
echo "  • Review the updated DEVELOPMENT_CONTEXT.md"
echo "  • Share the updated context with your team"
echo "  • Continue with your development workflow"
