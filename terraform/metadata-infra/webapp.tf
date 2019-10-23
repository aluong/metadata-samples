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

module "api_wrapper" {
  source = "./app_service_java"

  name                = "apiwrapper"
  resource_group_name = "${azurerm_resource_group.webapp.name}"
  location            = "${azurerm_app_service_plan.webapp.location}"
  app_service_plan_id = "${azurerm_app_service_plan.webapp.id}"

  base_resource_group_name = "${var.base_resource_group_name}"
  base_acr_name = "${var.base_acr_name}"
  base_keyvault_name = "${var.base_keyvault_name}"

  url_secret_name = "ApiWrapperUrl"

  docker_image = "wgbs/api-wrapper"

  app_settings = {
    AtlasPassword = "@Microsoft.KeyVault(SecretUri=${azurerm_key_vault_secret.atlas_password.id})"
    AtlasServerIP = "@Microsoft.KeyVault(SecretUri=${azurerm_key_vault_secret.atlas_server_ip.id})"
    AtlasServerPort = "@Microsoft.KeyVault(SecretUri=${azurerm_key_vault_secret.atlas_server_port.id})"
    AtlasUserName = "@Microsoft.KeyVault(SecretUri=${azurerm_key_vault_secret.atlas_username.id})"
  }
}
