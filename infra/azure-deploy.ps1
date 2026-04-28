# Azure CLI Deployment Script for Open Data AI Analytics (PowerShell)
# Lab 4: Infrastructure as Code using Azure CLI
#
# Usage: .\azure-deploy.ps1 [-ResourceGroup "odaa-rg"] [-Location "eastus"]

param(
    [string]$ResourceGroup = "odaa-rg",
    [string]$Location = "eastus"
)

# Configuration
$VmName = "odaa-vm"
$VnetName = "odaa-vnet"
$SubnetName = "odaa-subnet"
$NsgName = "odaa-nsg"
$PublicIpName = "odaa-public-ip"
$NicName = "odaa-nic"
$VmSize = "Standard_D2s_v3"
$VmImage = "Ubuntu2204"
$AdminUsername = "azureuser"

Write-Host "============================================" -ForegroundColor Green
Write-Host "  Open Data AI Analytics - Azure Deployment " -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Resource Group: $ResourceGroup" -ForegroundColor Yellow
Write-Host "Location:       $Location" -ForegroundColor Yellow
Write-Host "VM Name:        $VmName" -ForegroundColor Yellow
Write-Host ""

# Step 1: Create Resource Group
Write-Host "[1/7] Creating Resource Group..." -ForegroundColor Green
az group create `
    --name $ResourceGroup `
    --location $Location `
    --output table

# Step 2: Create Virtual Network and Subnet
Write-Host "[2/7] Creating Virtual Network and Subnet..." -ForegroundColor Green
az network vnet create `
    --resource-group $ResourceGroup `
    --name $VnetName `
    --address-prefix "10.0.0.0/16" `
    --subnet-name $SubnetName `
    --subnet-prefix "10.0.1.0/24" `
    --output table

# Step 3: Create Network Security Group with Rules
Write-Host "[3/7] Creating Network Security Group..." -ForegroundColor Green
az network nsg create `
    --resource-group $ResourceGroup `
    --name $NsgName `
    --output table

# Allow SSH (port 22)
Write-Host "  Adding SSH rule (port 22)..." -ForegroundColor Yellow
az network nsg rule create `
    --resource-group $ResourceGroup `
    --nsg-name $NsgName `
    --name "AllowSSH" `
    --priority 1000 `
    --access Allow `
    --direction Inbound `
    --protocol Tcp `
    --destination-port-ranges 22 `
    --output table

# Allow Web (port 8080)
Write-Host "  Adding Web rule (port 8080)..." -ForegroundColor Yellow
az network nsg rule create `
    --resource-group $ResourceGroup `
    --nsg-name $NsgName `
    --name "AllowWeb" `
    --priority 1001 `
    --access Allow `
    --direction Inbound `
    --protocol Tcp `
    --destination-port-ranges 8080 `
    --output table

# Allow Grafana (port 3000)
Write-Host "  Adding Grafana rule (port 3000)..." -ForegroundColor Yellow
az network nsg rule create `
    --resource-group $ResourceGroup `
    --nsg-name $NsgName `
    --name "AllowGrafana" `
    --priority 1002 `
    --access Allow `
    --direction Inbound `
    --protocol Tcp `
    --destination-port-ranges 3000 `
    --output table

# Allow Prometheus (port 9090)
Write-Host "  Adding Prometheus rule (port 9090)..." -ForegroundColor Yellow
az network nsg rule create `
    --resource-group $ResourceGroup `
    --nsg-name $NsgName `
    --name "AllowPrometheus" `
    --priority 1003 `
    --access Allow `
    --direction Inbound `
    --protocol Tcp `
    --destination-port-ranges 9090 `
    --output table

# Step 4: Create Public IP Address
Write-Host "[4/7] Creating Public IP Address..." -ForegroundColor Green
az network public-ip create `
    --resource-group $ResourceGroup `
    --name $PublicIpName `
    --sku Standard `
    --allocation-method Static `
    --output table

# Step 5: Create Network Interface
Write-Host "[5/7] Creating Network Interface..." -ForegroundColor Green
az network nic create `
    --resource-group $ResourceGroup `
    --name $NicName `
    --vnet-name $VnetName `
    --subnet $SubnetName `
    --network-security-group $NsgName `
    --public-ip-address $PublicIpName `
    --output table

# Step 6: Create Linux Virtual Machine with cloud-init
Write-Host "[6/7] Creating Linux Virtual Machine..." -ForegroundColor Green
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$CloudInitFile = Join-Path $ScriptDir "cloud-init.yaml"

if (-not (Test-Path $CloudInitFile)) {
    Write-Host "Error: cloud-init.yaml not found at $CloudInitFile" -ForegroundColor Red
    exit 1
}

az vm create `
    --resource-group $ResourceGroup `
    --name $VmName `
    --nics $NicName `
    --image $VmImage `
    --size $VmSize `
    --admin-username $AdminUsername `
    --generate-ssh-keys `
    --custom-data $CloudInitFile `
    --output table

# Step 7: Get Public IP and Display Results
Write-Host "[7/7] Deployment Complete!" -ForegroundColor Green
$PublicIp = az network public-ip show `
    --resource-group $ResourceGroup `
    --name $PublicIpName `
    --query "ipAddress" `
    --output tsv

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Deployment Summary" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Public IP:       $PublicIp" -ForegroundColor Yellow
Write-Host ""
Write-Host "Access URLs (wait 5-10 minutes for cloud-init):" -ForegroundColor Green
Write-Host "  Web Interface: http://${PublicIp}:8080" -ForegroundColor Yellow
Write-Host "  Grafana:       http://${PublicIp}:3000  (admin/admin)" -ForegroundColor Yellow
Write-Host "  Prometheus:    http://${PublicIp}:9090" -ForegroundColor Yellow
Write-Host ""
Write-Host "SSH Access:" -ForegroundColor Green
Write-Host "  ssh ${AdminUsername}@${PublicIp}" -ForegroundColor Yellow
Write-Host ""
Write-Host "Check cloud-init status:" -ForegroundColor Green
Write-Host "  ssh ${AdminUsername}@${PublicIp} 'cloud-init status'" -ForegroundColor Yellow
Write-Host "  ssh ${AdminUsername}@${PublicIp} 'cat /var/log/cloud-init-output.log'" -ForegroundColor Yellow
Write-Host ""
Write-Host "============================================" -ForegroundColor Green

# Save deployment info to file
$DeploymentInfo = @"
RESOURCE_GROUP=$ResourceGroup
PUBLIC_IP=$PublicIp
VM_NAME=$VmName
Deployment completed at: $(Get-Date)
"@
$DeploymentInfo | Out-File -FilePath (Join-Path $ScriptDir ".deployment-info") -Encoding UTF8

Write-Host "Deployment info saved to: $(Join-Path $ScriptDir '.deployment-info')" -ForegroundColor Green
