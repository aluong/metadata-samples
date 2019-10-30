# Deploys base infrastructure
data "azurerm_client_config" "current" {}

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

resource "azurerm_application_insights" "this" {
  name                = "${var.resource_group_name}-insights"
  location            = "${azurerm_resource_group.this.location}"
  resource_group_name = "${azurerm_resource_group.this.name}"
  application_type    = "other"
}

resource "azurerm_user_assigned_identity" "this" {
  resource_group_name = "${azurerm_resource_group.this.name}"
  location            = "${azurerm_resource_group.this.location}"

  name = "${azurerm_resource_group.this.name}-webapp"
}
