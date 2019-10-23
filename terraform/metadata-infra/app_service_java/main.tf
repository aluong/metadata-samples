variable "resource_group_name" {}
variable "location" {}
variable "app_service_plan_id" {}
variable "app_settings" {}
variable "name" {}
variable "docker_image" {}

variable "url_secret_name"{}

variable "base_resource_group_name" {}
variable "base_acr_name" {}
variable "base_keyvault_name" {}

locals {
  app_settings_internal = {
    WEBSITES_ENABLE_APP_SERVICE_STORAGE = false

    DOCKER_ENABLE_CI = true
    DOCKER_REGISTRY_URL = "${data.azurerm_container_registry.base.login_server}"
    DOCKER_REGISTRY_SERVER_USERNAME = "${data.azurerm_container_registry.base.admin_username}"
    DOCKER_REGISTRY_SERVER_PASSWORD = "${data.azurerm_container_registry.base.admin_password}"
  }
  app_name = "${join("", [var.name, substr(md5(var.app_service_plan_id), 0, 8)])}"
}

data "azurerm_key_vault" "base" {
  name = "${var.base_keyvault_name}"
  resource_group_name = "${var.base_resource_group_name}"
}

data "azurerm_container_registry" "base" {
  name = "${var.base_acr_name}"
  resource_group_name = "${var.base_resource_group_name}"
}

resource "azurerm_app_service" "this" {
  name                      = "${local.app_name}"
  resource_group_name       = "${var.resource_group_name}"
  location                  = "${var.location}"
  app_service_plan_id       = "${var.app_service_plan_id}"

  app_settings = "${merge(local.app_settings_internal, var.app_settings)}"

  site_config {
    linux_fx_version = "DOCKER|${data.azurerm_container_registry.base.login_server}/${var.docker_image}:latest"
    always_on        = "true"

  # Ignoring putting web app in VNet because specified region is unclear
  # site_config {
    # virtual_network_name = "${var.base_vnet_name}"
  # }
  }

  identity {
    type = "SystemAssigned"
  } 
}

resource "azurerm_container_registry_webhook" "this" {
  name                = "${local.app_name}webhook"
  resource_group_name = "${data.azurerm_container_registry.base.resource_group_name}"
  registry_name       = "${data.azurerm_container_registry.base.name}"
  location            = "${data.azurerm_container_registry.base.location}"

  service_uri    = "https://${azurerm_app_service.this.site_credential[0].username}:${azurerm_app_service.this.site_credential[0].password}@${azurerm_app_service.this.name}.scm.azurewebsites.net/docker/hook"
  status         = "enabled"
  scope          = "${var.docker_image}:*"
  actions        = ["push"]
  custom_headers = { "Content-Type" = "application/json" }
}

resource "azurerm_key_vault_access_policy" "this" {
  key_vault_id = "${data.azurerm_key_vault.base.id}"

  tenant_id = "${azurerm_app_service.this.identity[0].tenant_id}"
  object_id = "${azurerm_app_service.this.identity[0].principal_id}"

  secret_permissions = [
    "get",
  ]
}

resource "azurerm_key_vault_secret" "this" {
  name         = "${var.url_secret_name}"
  value        = "https://${azurerm_app_service.this.default_site_hostname}"
  key_vault_id = "${data.azurerm_key_vault.base.id}"
}

output "url_secret_id" {
  value = "${azurerm_key_vault_secret.this.id}"
}