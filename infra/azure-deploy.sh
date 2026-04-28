#!/bin/bash
# Azure CLI Deployment Script for Open Data AI Analytics
# Lab 4: Infrastructure as Code using Azure CLI
#
# Usage: ./azure-deploy.sh [RESOURCE_GROUP] [LOCATION]
# Example: ./azure-deploy.sh odaa-rg eastus

set -e

# =============================================================================
# Configuration
# =============================================================================
RESOURCE_GROUP="${1:-odaa-rg}"
LOCATION="${2:-eastus}"
VM_NAME="odaa-vm"
VNET_NAME="odaa-vnet"
SUBNET_NAME="odaa-subnet"
NSG_NAME="odaa-nsg"
PUBLIC_IP_NAME="odaa-public-ip"
NIC_NAME="odaa-nic"
VM_SIZE="Standard_D2s_v3"
VM_IMAGE="Ubuntu2204"
ADMIN_USERNAME="azureuser"

# =============================================================================
# Colors for output
# =============================================================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Open Data AI Analytics - Azure Deployment ${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "Resource Group: ${YELLOW}${RESOURCE_GROUP}${NC}"
echo -e "Location:       ${YELLOW}${LOCATION}${NC}"
echo -e "VM Name:        ${YELLOW}${VM_NAME}${NC}"
echo ""

# =============================================================================
# Step 1: Create Resource Group
# =============================================================================
echo -e "${GREEN}[1/7] Creating Resource Group...${NC}"
az group create \
    --name "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --output table

# =============================================================================
# Step 2: Create Virtual Network and Subnet
# =============================================================================
echo -e "${GREEN}[2/7] Creating Virtual Network and Subnet...${NC}"
az network vnet create \
    --resource-group "$RESOURCE_GROUP" \
    --name "$VNET_NAME" \
    --address-prefix 10.0.0.0/16 \
    --subnet-name "$SUBNET_NAME" \
    --subnet-prefix 10.0.1.0/24 \
    --output table

# =============================================================================
# Step 3: Create Network Security Group with Rules
# =============================================================================
echo -e "${GREEN}[3/7] Creating Network Security Group...${NC}"
az network nsg create \
    --resource-group "$RESOURCE_GROUP" \
    --name "$NSG_NAME" \
    --output table

# Allow SSH (port 22)
echo -e "${YELLOW}  Adding SSH rule (port 22)...${NC}"
az network nsg rule create \
    --resource-group "$RESOURCE_GROUP" \
    --nsg-name "$NSG_NAME" \
    --name "AllowSSH" \
    --priority 1000 \
    --access Allow \
    --direction Inbound \
    --protocol Tcp \
    --destination-port-ranges 22 \
    --output table

# Allow Web (port 8080)
echo -e "${YELLOW}  Adding Web rule (port 8080)...${NC}"
az network nsg rule create \
    --resource-group "$RESOURCE_GROUP" \
    --nsg-name "$NSG_NAME" \
    --name "AllowWeb" \
    --priority 1001 \
    --access Allow \
    --direction Inbound \
    --protocol Tcp \
    --destination-port-ranges 8080 \
    --output table

# Allow Grafana (port 3000)
echo -e "${YELLOW}  Adding Grafana rule (port 3000)...${NC}"
az network nsg rule create \
    --resource-group "$RESOURCE_GROUP" \
    --nsg-name "$NSG_NAME" \
    --name "AllowGrafana" \
    --priority 1002 \
    --access Allow \
    --direction Inbound \
    --protocol Tcp \
    --destination-port-ranges 3000 \
    --output table

# Allow Prometheus (port 9090)
echo -e "${YELLOW}  Adding Prometheus rule (port 9090)...${NC}"
az network nsg rule create \
    --resource-group "$RESOURCE_GROUP" \
    --nsg-name "$NSG_NAME" \
    --name "AllowPrometheus" \
    --priority 1003 \
    --access Allow \
    --direction Inbound \
    --protocol Tcp \
    --destination-port-ranges 9090 \
    --output table

# =============================================================================
# Step 4: Create Public IP Address
# =============================================================================
echo -e "${GREEN}[4/7] Creating Public IP Address...${NC}"
az network public-ip create \
    --resource-group "$RESOURCE_GROUP" \
    --name "$PUBLIC_IP_NAME" \
    --sku Standard \
    --allocation-method Static \
    --output table

# =============================================================================
# Step 5: Create Network Interface
# =============================================================================
echo -e "${GREEN}[5/7] Creating Network Interface...${NC}"
az network nic create \
    --resource-group "$RESOURCE_GROUP" \
    --name "$NIC_NAME" \
    --vnet-name "$VNET_NAME" \
    --subnet "$SUBNET_NAME" \
    --network-security-group "$NSG_NAME" \
    --public-ip-address "$PUBLIC_IP_NAME" \
    --output table

# =============================================================================
# Step 6: Create Linux Virtual Machine with cloud-init
# =============================================================================
echo -e "${GREEN}[6/7] Creating Linux Virtual Machine...${NC}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLOUD_INIT_FILE="$SCRIPT_DIR/cloud-init.yaml"

if [ ! -f "$CLOUD_INIT_FILE" ]; then
    echo -e "${RED}Error: cloud-init.yaml not found at $CLOUD_INIT_FILE${NC}"
    exit 1
fi

az vm create \
    --resource-group "$RESOURCE_GROUP" \
    --name "$VM_NAME" \
    --nics "$NIC_NAME" \
    --image "$VM_IMAGE" \
    --size "$VM_SIZE" \
    --admin-username "$ADMIN_USERNAME" \
    --generate-ssh-keys \
    --custom-data "$CLOUD_INIT_FILE" \
    --output table

# =============================================================================
# Step 7: Get Public IP and Display Results
# =============================================================================
echo -e "${GREEN}[7/7] Deployment Complete!${NC}"
PUBLIC_IP=$(az network public-ip show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$PUBLIC_IP_NAME" \
    --query "ipAddress" \
    --output tsv)

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Deployment Summary${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "Public IP:       ${YELLOW}${PUBLIC_IP}${NC}"
echo ""
echo -e "${GREEN}Access URLs (wait 5-10 minutes for cloud-init):${NC}"
echo -e "  Web Interface: ${YELLOW}http://${PUBLIC_IP}:8080${NC}"
echo -e "  Grafana:       ${YELLOW}http://${PUBLIC_IP}:3000${NC}  (admin/admin)"
echo -e "  Prometheus:    ${YELLOW}http://${PUBLIC_IP}:9090${NC}"
echo ""
echo -e "${GREEN}SSH Access:${NC}"
echo -e "  ssh ${ADMIN_USERNAME}@${PUBLIC_IP}"
echo ""
echo -e "${GREEN}Check cloud-init status:${NC}"
echo -e "  ssh ${ADMIN_USERNAME}@${PUBLIC_IP} 'cloud-init status'"
echo -e "  ssh ${ADMIN_USERNAME}@${PUBLIC_IP} 'cat /var/log/cloud-init-output.log'"
echo ""
echo -e "${GREEN}============================================${NC}"

# Save deployment info to file
echo "RESOURCE_GROUP=$RESOURCE_GROUP" > "$SCRIPT_DIR/.deployment-info"
echo "PUBLIC_IP=$PUBLIC_IP" >> "$SCRIPT_DIR/.deployment-info"
echo "VM_NAME=$VM_NAME" >> "$SCRIPT_DIR/.deployment-info"
echo "Deployment completed at: $(date)" >> "$SCRIPT_DIR/.deployment-info"

echo -e "${GREEN}Deployment info saved to: $SCRIPT_DIR/.deployment-info${NC}"
