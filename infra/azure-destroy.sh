#!/bin/bash
# Azure CLI Destroy Script for Open Data AI Analytics
# Removes all resources created by azure-deploy.sh
#
# Usage: ./azure-destroy.sh [RESOURCE_GROUP]
# Example: ./azure-destroy.sh odaa-rg

set -e

# =============================================================================
# Configuration
# =============================================================================
RESOURCE_GROUP="${1:-odaa-rg}"

# =============================================================================
# Colors for output
# =============================================================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${RED}============================================${NC}"
echo -e "${RED}  WARNING: Resource Deletion${NC}"
echo -e "${RED}============================================${NC}"
echo ""
echo -e "This will delete the resource group: ${YELLOW}${RESOURCE_GROUP}${NC}"
echo -e "All resources inside will be permanently removed!"
echo ""
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo -e "${GREEN}Cancelled. No resources were deleted.${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}Deleting resource group: ${RESOURCE_GROUP}...${NC}"
echo -e "${YELLOW}This may take several minutes...${NC}"
echo ""

az group delete \
    --name "$RESOURCE_GROUP" \
    --yes \
    --no-wait

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Resource group deletion initiated${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "The resource group ${YELLOW}${RESOURCE_GROUP}${NC} is being deleted."
echo -e "This process runs in the background and may take 5-10 minutes."
echo ""
echo -e "${GREEN}To check deletion status:${NC}"
echo -e "  az group show --name $RESOURCE_GROUP"
echo ""

# Remove deployment info file if exists
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/.deployment-info" ]; then
    rm "$SCRIPT_DIR/.deployment-info"
    echo -e "${GREEN}Removed local deployment info file.${NC}"
fi
