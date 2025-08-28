#!/bin/bash

# Component Integration Script
# Copy missing components from localstorm reference repository

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Configuration
LOCALSTORM_REPO="https://github.com/robert1948/localstorm.git"
TEMP_DIR="/tmp/localstorm-sync"
BACKUP_DIR="./backups/$(date +%Y%m%d-%H%M%S)"

echo -e "${PURPLE}🔄 Component Integration from localstorm${NC}"
echo -e "${BLUE}==========================================${NC}"

# Function to show usage
show_usage() {
    echo -e "\n${BLUE}Usage:${NC}"
    echo -e "   $0 [component-type] [specific-component]"
    echo -e "\n${BLUE}Component Types:${NC}"
    echo -e "   frontend    - Copy frontend components"
    echo -e "   backend     - Copy backend modules"
    echo -e "   docs        - Copy documentation"
    echo -e "   all         - Copy all components (default)"
    echo -e "\n${BLUE}Examples:${NC}"
    echo -e "   $0 frontend"
    echo -e "   $0 backend api"
    echo -e "   $0 all"
    exit 1
}

# Function to backup existing files
backup_existing() {
    local source_path="$1"
    local backup_path="$2"
    
    if [ -e "$source_path" ]; then
        echo -e "${YELLOW}📦 Backing up existing: $source_path${NC}"
        mkdir -p "$(dirname "$backup_path")"
        cp -r "$source_path" "$backup_path"
    fi
}

# Function to copy components safely
safe_copy() {
    local source="$1"
    local destination="$2"
    local component_name="$3"
    
    if [ ! -e "$source" ]; then
        echo -e "${YELLOW}⚠️  Source not found: $source${NC}"
        return 1
    fi
    
    # Backup existing if it exists
    if [ -e "$destination" ]; then
        backup_existing "$destination" "$BACKUP_DIR/$(basename "$destination")"
    fi
    
    # Copy new component
    echo -e "${BLUE}📋 Copying $component_name...${NC}"
    mkdir -p "$(dirname "$destination")"
    cp -r "$source" "$destination"
    
    echo -e "${GREEN}✅ Copied: $component_name${NC}"
    return 0
}

# Function to update imports and dependencies
update_dependencies() {
    echo -e "\n${BLUE}📦 Updating dependencies...${NC}"
    
    # Update frontend dependencies
    if [ -f "client/package.json" ]; then
        echo -e "${YELLOW}🔄 Updating frontend dependencies...${NC}"
        cd client
        npm install
        cd ..
    fi
    
    # Update backend dependencies
    if [ -f "requirements.txt" ]; then
        echo -e "${YELLOW}🔄 Updating backend dependencies...${NC}"
        pip install -r requirements.txt
        pip install -r backend/requirements.txt
    fi
}

# Parse command line arguments
COMPONENT_TYPE="${1:-all}"
SPECIFIC_COMPONENT="$2"

if [ "$COMPONENT_TYPE" = "--help" ] || [ "$COMPONENT_TYPE" = "-h" ]; then
    show_usage
fi

echo -e "${BLUE}Component Type: ${YELLOW}$COMPONENT_TYPE${NC}"
if [ -n "$SPECIFIC_COMPONENT" ]; then
    echo -e "${BLUE}Specific Component: ${YELLOW}$SPECIFIC_COMPONENT${NC}"
fi

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Clone or update localstorm repository
echo -e "\n${BLUE}🔄 Preparing localstorm reference repository...${NC}"

if [ -d "$TEMP_DIR" ]; then
    echo -e "${YELLOW}🔄 Updating existing localstorm clone...${NC}"
    cd "$TEMP_DIR"
    git pull origin main
    cd - > /dev/null
else
    echo -e "${YELLOW}📥 Cloning localstorm repository...${NC}"
    git clone "$LOCALSTORM_REPO" "$TEMP_DIR"
fi

echo -e "${GREEN}✅ localstorm repository ready${NC}"

# Copy components based on type
case "$COMPONENT_TYPE" in
    "frontend")
        echo -e "\n${PURPLE}═══ FRONTEND COMPONENTS ═══${NC}"
        
        if [ -n "$SPECIFIC_COMPONENT" ]; then
            safe_copy "$TEMP_DIR/client/src/components/$SPECIFIC_COMPONENT" \
                     "client/src/components/$SPECIFIC_COMPONENT" \
                     "Frontend component: $SPECIFIC_COMPONENT"
        else
            # Copy all frontend components
            if [ -d "$TEMP_DIR/client/src/components" ]; then
                for component in "$TEMP_DIR/client/src/components"/*; do
                    if [ -d "$component" ] || [ -f "$component" ]; then
                        component_name=$(basename "$component")
                        safe_copy "$component" \
                                 "client/src/components/$component_name" \
                                 "Frontend component: $component_name"
                    fi
                done
            fi
            
            # Copy pages if they exist
            if [ -d "$TEMP_DIR/client/src/pages" ]; then
                for page in "$TEMP_DIR/client/src/pages"/*; do
                    if [ -f "$page" ]; then
                        page_name=$(basename "$page")
                        if [ ! -f "client/src/pages/$page_name" ]; then
                            safe_copy "$page" \
                                     "client/src/pages/$page_name" \
                                     "Frontend page: $page_name"
                        fi
                    fi
                done
            fi
        fi
        ;;
        
    "backend")
        echo -e "\n${PURPLE}═══ BACKEND COMPONENTS ═══${NC}"
        
        if [ -n "$SPECIFIC_COMPONENT" ]; then
            safe_copy "$TEMP_DIR/backend/app/$SPECIFIC_COMPONENT" \
                     "backend/app/$SPECIFIC_COMPONENT" \
                     "Backend module: $SPECIFIC_COMPONENT"
        else
            # Copy backend modules
            if [ -d "$TEMP_DIR/backend/app" ]; then
                for module in "$TEMP_DIR/backend/app"/*; do
                    if [ -d "$module" ] || [ -f "$module" ]; then
                        module_name=$(basename "$module")
                        if [ "$module_name" != "__pycache__" ] && [ ! -e "backend/app/$module_name" ]; then
                            safe_copy "$module" \
                                     "backend/app/$module_name" \
                                     "Backend module: $module_name"
                        fi
                    fi
                done
            fi
        fi
        ;;
        
    "docs")
        echo -e "\n${PURPLE}═══ DOCUMENTATION ═══${NC}"
        
        if [ -d "$TEMP_DIR/docs" ]; then
            for doc in "$TEMP_DIR/docs"/*; do
                if [ -f "$doc" ]; then
                    doc_name=$(basename "$doc")
                    if [ ! -f "docs/$doc_name" ]; then
                        safe_copy "$doc" \
                                 "docs/$doc_name" \
                                 "Documentation: $doc_name"
                    fi
                fi
            done
        fi
        ;;
        
    "all")
        echo -e "\n${PURPLE}═══ ALL COMPONENTS ═══${NC}"
        
        # Copy frontend components
        if [ -d "$TEMP_DIR/client/src/components" ]; then
            echo -e "\n${BLUE}Frontend Components:${NC}"
            for component in "$TEMP_DIR/client/src/components"/*; do
                if [ -d "$component" ] || [ -f "$component" ]; then
                    component_name=$(basename "$component")
                    if [ ! -e "client/src/components/$component_name" ]; then
                        safe_copy "$component" \
                                 "client/src/components/$component_name" \
                                 "Frontend: $component_name"
                    else
                        echo -e "${YELLOW}⏭️  Skipping existing: client/src/components/$component_name${NC}"
                    fi
                fi
            done
        fi
        
        # Copy backend modules
        if [ -d "$TEMP_DIR/backend/app" ]; then
            echo -e "\n${BLUE}Backend Modules:${NC}"
            for module in "$TEMP_DIR/backend/app"/*; do
                if [ -d "$module" ] || [ -f "$module" ]; then
                    module_name=$(basename "$module")
                    if [ "$module_name" != "__pycache__" ] && [ ! -e "backend/app/$module_name" ]; then
                        safe_copy "$module" \
                                 "backend/app/$module_name" \
                                 "Backend: $module_name"
                    else
                        echo -e "${YELLOW}⏭️  Skipping existing: backend/app/$module_name${NC}"
                    fi
                fi
            done
        fi
        
        # Copy documentation
        if [ -d "$TEMP_DIR/docs" ]; then
            echo -e "\n${BLUE}Documentation:${NC}"
            for doc in "$TEMP_DIR/docs"/*; do
                if [ -f "$doc" ]; then
                    doc_name=$(basename "$doc")
                    if [ ! -f "docs/$doc_name" ]; then
                        safe_copy "$doc" \
                                 "docs/$doc_name" \
                                 "Docs: $doc_name"
                    else
                        echo -e "${YELLOW}⏭️  Skipping existing: docs/$doc_name${NC}"
                    fi
                fi
            done
        fi
        ;;
        
    *)
        echo -e "${RED}❌ Unknown component type: $COMPONENT_TYPE${NC}"
        show_usage
        ;;
esac

# Update dependencies
update_dependencies

# Test integration
echo -e "\n${PURPLE}═══ INTEGRATION TESTING ═══${NC}"

echo -e "${BLUE}🧪 Testing frontend build...${NC}"
cd client
if npm run build > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend build successful${NC}"
else
    echo -e "${RED}❌ Frontend build failed${NC}"
fi
cd ..

echo -e "${BLUE}🧪 Testing backend imports...${NC}"
cd backend
if python -c "from app.main import app; print('✓ Backend imports successful')" 2>/dev/null; then
    echo -e "${GREEN}✅ Backend imports successful${NC}"
else
    echo -e "${RED}❌ Backend imports failed${NC}"
fi
cd ..

# Cleanup
echo -e "\n${BLUE}🧹 Cleaning up...${NC}"
rm -rf "$TEMP_DIR"

# Summary
echo -e "\n${PURPLE}═══ INTEGRATION SUMMARY ═══${NC}"
echo -e "${GREEN}✅ Component integration completed${NC}"
echo -e "${BLUE}📁 Backups saved to: ${YELLOW}$BACKUP_DIR${NC}"
echo -e "\n${BLUE}Next steps:${NC}"
echo -e "   1. Review integrated components"
echo -e "   2. Test application: ${YELLOW}./scripts/dev-test.sh${NC}"
echo -e "   3. Commit changes: ${YELLOW}git add . && git commit -m 'feat: integrate components from localstorm'${NC}"
echo -e "   4. Run full validation: ${YELLOW}./scripts/pre-production-check.sh${NC}"

echo -e "\n${GREEN}🎉 Component integration from localstorm completed!${NC}"
