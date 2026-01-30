terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}

  # These values will come from your Service Principal (appId, password, etc.)
  subscription_id = var.subscription_id
  client_id       = var.client_id
  client_secret   = var.client_secret
  tenant_id       = var.tenant_id
}

resource "azurerm_resource_group" "zoomcamp_rg" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_storage_account" "taxi_storage" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.zoomcamp_rg.name
  location                 = azurerm_resource_group.zoomcamp_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS" # Local Redundancy (cheapest)
  
  # Enabling Hierarchical Namespace makes it behave like a real file system (Data Lake Gen2)
  is_hns_enabled           = true 
}

resource "azurerm_storage_container" "data_lake" {
  name                  = "nytaxi-data"
  storage_account_id    = azurerm_storage_account.taxi_storage.id
  container_access_type = "private"
}