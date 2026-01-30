variable "location" {
  default = "Central US"
}

variable "resource_group_name" {
  default = "zoomcamp-krish-rg"
}

variable "storage_account_name" {
  # Must be globally unique and lowercase (no spaces/special chars)
  default = "zoomcampkrishstorage" 
}

# Azure Auth Variables
variable "subscription_id" {}
variable "client_id" {}
variable "client_secret" {}
variable "tenant_id" {}