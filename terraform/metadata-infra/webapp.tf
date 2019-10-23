locals {
  webapp_name = "${join("", ["web", substr(md5(azurerm_resource_group.webapp.name), 0, 8)])}"
}

resource "azurerm_app_service_plan" "webapp" {
  name                = "${var.app_service_plan_name}-webapp"
  resource_group_name = "${azurerm_resource_group.webapp.name}"
  location            = "${var.app_service_plan_location}"

  kind = "Linux"
  reserved = true

  sku {
    tier = "${var.web_app_service_plan_tier}"
    size = "${var.web_app_service_plan_size}"
  }
}

resource "azurerm_app_service" "metadata_wrapper" {
  name                = "${local.webapp_name}"
  resource_group_name = "${azurerm_resource_group.webapp.name}"
  location            = "${azurerm_app_service_plan.webapp.location}"
  app_service_plan_id = "${azurerm_app_service_plan.webapp.id}"

  app_settings = {
    WEBSITES_ENABLE_APP_SERVICE_STORAGE = false

    AtlasPassword = "@Microsoft.KeyVault(SecretUri=${azurerm_key_vault_secret.atlas_password.id})"
    AtlasServerIP = "@Microsoft.KeyVault(SecretUri=${azurerm_key_vault_secret.atlas_server_ip.id})"
    AtlasServerPort = "@Microsoft.KeyVault(SecretUri=${azurerm_key_vault_secret.atlas_server_port.id})"
    AtlasUserName = "@Microsoft.KeyVault(SecretUri=${azurerm_key_vault_secret.atlas_username.id})"

    DOCKER_ENABLE_CI = true
    DOCKER_REGISTRY_URL = "${data.azurerm_container_registry.base.login_server}"
    DOCKER_REGISTRY_SERVER_USERNAME = "${data.azurerm_container_registry.base.admin_username}"
    DOCKER_REGISTRY_SERVER_PASSWORD = "${data.azurerm_container_registry.base.admin_password}"
  }

  site_config {
    linux_fx_version = "DOCKER|${data.azurerm_container_registry.base.login_server}/wgbs/api-wrapper:latest"
    always_on        = "true"

  # Ignoring putting web app in VNet because specified region is unclear
  # site_config {
    # virtual_network_name = "${var.base_vnet_name}"
  # }
  }

  identity {
    type = "SystemAssigned, UserAssigned"
    identity_ids = ["${data.azurerm_user_assigned_identity.base.id}"]
  } 
}

resource "azurerm_container_registry_webhook" "metadata_wrapper" {
  name                = "metadatawrapperwebhook"
  resource_group_name = "${data.azurerm_container_registry.base.resource_group_name}"
  registry_name       = "${data.azurerm_container_registry.base.name}"
  location            = "${data.azurerm_container_registry.base.location}"

  service_uri    = "https://${azurerm_app_service.metadata_wrapper.site_credential[0].username}:${azurerm_app_service.metadata_wrapper.site_credential[0].password}@${azurerm_app_service.metadata_wrapper.name}.scm.azurewebsites.net/docker/hook"
  status         = "enabled"
  scope          = "wgbs/api-wrapper:*"
  actions        = ["push"]
  custom_headers = { "Content-Type" = "application/json" }
}

resource "azurerm_key_vault_access_policy" "metadata_wrapper" {
  key_vault_id = "${data.azurerm_key_vault.base.id}"

  tenant_id = "${azurerm_app_service.metadata_wrapper.identity[0].tenant_id}"
  object_id = "${azurerm_app_service.metadata_wrapper.identity[0].principal_id}"

  secret_permissions = [
    "get",
  ]
}