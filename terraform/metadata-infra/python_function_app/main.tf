variable "resource_group_name" {}
variable "location" {}
variable "app_service_plan_id" {}
variable "storage_connection_string"{}
variable "app_settings" {}
variable "name" {}
variable "docker_image" {}

variable "base_resource_group_name" {}
variable "base_acr_name" {}
variable "base_keyvault_name" {}

locals {
  app_settings_internal = {
    WEBSITES_ENABLE_APP_SERVICE_STORAGE = false

    "FUNCTIONS_WORKER_RUNTIME"     = "python"
    "WEBSITE_NODE_DEFAULT_VERSION" = "10.14.1"

    DOCKER_ENABLE_CI = true
    DOCKER_REGISTRY_URL = "${data.azurerm_container_registry.base.login_server}"
    DOCKER_REGISTRY_SERVER_USERNAME = "${data.azurerm_container_registry.base.admin_username}"
    DOCKER_REGISTRY_SERVER_PASSWORD = "${data.azurerm_container_registry.base.admin_password}"
  }
  func_name = "${join("", [var.name, substr(md5(var.app_service_plan_id), 0, 8)])}"
}

data "azurerm_key_vault" "base" {
  name = "${var.base_keyvault_name}"
  resource_group_name = "${var.base_resource_group_name}"
}

data "azurerm_container_registry" "base" {
  name = "${var.base_acr_name}"
  resource_group_name = "${var.base_resource_group_name}"
}

resource "azurerm_function_app" "this" {
  name                      = "${local.func_name}"
  resource_group_name       = "${var.resource_group_name}"
  location                  = "${var.location}"
  app_service_plan_id       = "${var.app_service_plan_id}"
  storage_connection_string = "${var.storage_connection_string}"
  
  site_config {
    linux_fx_version = "DOCKER|${data.azurerm_container_registry.base.login_server}/${var.docker_image}"
  }

  version = "~2"

  app_settings = "${merge(local.app_settings_internal, var.app_settings)}"

  # Ignoring putting function app in VNet because specified region is unclear
  # site_config {
    # virtual_network_name = "${var.base_vnet_name}"
  # }
  identity {
    type = "SystemAssigned"
  } 
}

resource "azurerm_key_vault_access_policy" "this" {
  key_vault_id = "${data.azurerm_key_vault.base.id}"

  tenant_id = "${azurerm_function_app.this.identity[0].tenant_id}"
  object_id = "${azurerm_function_app.this.identity[0].principal_id}"

  secret_permissions = [
    "get",
  ]
}
