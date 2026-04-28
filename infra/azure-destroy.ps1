# Azure CLI Destroy Script for Open Data AI Analytics (PowerShell)
# Removes all resources created by azure-deploy.ps1
#
# Usage: .\azure-destroy.ps1 [-ResourceGroup "odaa-rg"]

param(
    [string]$ResourceGroup = "odaa-rg"
)

Write-Host "============================================" -ForegroundColor Red
Write-Host "  WARNING: Resource Deletion" -ForegroundColor Red
Write-Host "============================================" -ForegroundColor Red
Write-Host ""
Write-Host "This will delete the resource group: $ResourceGroup" -ForegroundColor Yellow
Write-Host "All resources inside will be permanently removed!" -ForegroundColor Yellow
Write-Host ""

$Confirm = Read-Host "Are you sure you want to continue? (yes/no)"

if ($Confirm -ne "yes") {
    Write-Host "Cancelled. No resources were deleted." -ForegroundColor Green
    exit 0
}

Write-Host ""
Write-Host "Deleting resource group: $ResourceGroup..." -ForegroundColor Yellow
Write-Host "This may take several minutes..." -ForegroundColor Yellow
Write-Host ""

az group delete `
    --name $ResourceGroup `
    --yes `
    --no-wait

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Resource group deletion initiated" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "The resource group $ResourceGroup is being deleted." -ForegroundColor Yellow
Write-Host "This process runs in the background and may take 5-10 minutes." -ForegroundColor Yellow
Write-Host ""
Write-Host "To check deletion status:" -ForegroundColor Green
Write-Host "  az group show --name $ResourceGroup" -ForegroundColor Yellow
Write-Host ""

# Remove deployment info file if exists
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$DeploymentInfoFile = Join-Path $ScriptDir ".deployment-info"
if (Test-Path $DeploymentInfoFile) {
    Remove-Item $DeploymentInfoFile
    Write-Host "Removed local deployment info file." -ForegroundColor Green
}
