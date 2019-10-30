# Deploys metadata layer infra after the base infrastructure is in place

provider "azurerm" {
  version = "=1.35.0"
}

terraform {
    backend "azurerm" {
        container_name = "terraform"
    }
}

resource "azurerm_resource_group" "this" {
  name     = "${var.resource_group_name}"
  location = "${var.location}"
}

resource "azurerm_resource_group" "functionapp" {
  name     = "${var.resource_group_name}-functionapp"
  location = "${var.app_service_plan_location}"
}

resource "azurerm_resource_group" "webapp" {
  name     = "${var.resource_group_name}-webapp"
  location = "${var.app_service_plan_location}"
}

data "azurerm_virtual_network" "base" {
  name                = "${var.base_vnet_name}"
  resource_group_name = "${var.base_resource_group_name}"
}

data "azurerm_storage_account" "base" {
  name                = "${var.base_storage_account_name}"
  resource_group_name = "${var.base_resource_group_name}"
}

data "azurerm_user_assigned_identity" "base" {
  name                = "${var.base_user_assigned_identity_name}"
  resource_group_name = "${var.base_resource_group_name}"
}

data "azurerm_key_vault" "base" {
  name = "${var.base_keyvault_name}"
  resource_group_name = "${var.base_resource_group_name}"
}

data "azurerm_container_registry" "base" {
  name = "${var.base_acr_name}"
  resource_group_name = "${var.base_resource_group_name}"
}

data "azurerm_sql_server" "base" {
  name                = "${var.base_sql_server_name}"
  resource_group_name = "${var.base_resource_group_name}"
}