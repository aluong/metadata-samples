resource "azurerm_app_service_plan" "function" {
  name                = "${var.app_service_plan_name}-functions"
  resource_group_name = "${azurerm_resource_group.functionapp.name}"
  location            = "${var.app_service_plan_location}"

  kind     = "linux"
  reserved = true

  sku {
    tier = "${var.func_app_service_plan_tier}"
    size = "${var.func_app_service_plan_size}"
  }
}

data "azurerm_key_vault_secret" "SqlServer" {
  name = "SqlServer"
  key_vault_id = "${data.azurerm_key_vault.base.id}"
}

data "azurerm_key_vault_secret" "SqlDatabase" {
  name = "SqlDatabase"
  key_vault_id = "${data.azurerm_key_vault.base.id}"
}

data "azurerm_key_vault_secret" "SqlLogin" {
  name = "SqlLogin"
  key_vault_id = "${data.azurerm_key_vault.base.id}"
}

data "azurerm_key_vault_secret" "SqlPassword" {
  name = "SqlPassword"
  key_vault_id = "${data.azurerm_key_vault.base.id}"
}

module "qns" {
  source = "./python_function_app"

  name                      = "qns"
  resource_group_name       = "${azurerm_resource_group.functionapp.name}"
  location                  = "${azurerm_app_service_plan.function.location}"
  app_service_plan_id       = "${azurerm_app_service_plan.function.id}"
  storage_connection_string = "${data.azurerm_storage_account.base.primary_connection_string}"

  base_resource_group_name = "${var.base_resource_group_name}"
  base_acr_name = "${var.base_acr_name}"
  base_keyvault_name = "${var.base_keyvault_name}"

  url_secret_name = "QualifiedNameServiceUrl"

  docker_image = "metadata/qns"
  app_settings = {}
}

module "lineage_creator" {
  source = "./python_function_app"

  name                      = "lineagecreator"
  resource_group_name       = "${azurerm_resource_group.functionapp.name}"
  location                  = "${azurerm_app_service_plan.function.location}"
  app_service_plan_id       = "${azurerm_app_service_plan.function.id}"
  storage_connection_string = "${data.azurerm_storage_account.base.primary_connection_string}"

  base_resource_group_name = "${var.base_resource_group_name}"
  base_acr_name = "${var.base_acr_name}"
  base_keyvault_name = "${var.base_keyvault_name}"

  url_secret_name = "LineageCreatorServiceUrl"

  docker_image = "metadata/lineage_creator"
  app_settings = {
    qualifiedNameServiceUrl = "@Microsoft.KeyVault(SecretUri=${module.qns.url_secret_id})"
    qualifiedNameServiceKey = "placeholder"
    jsonGeneratorServiceUrl = "@Microsoft.KeyVault(SecretUri=${module.json_generator.url_secret_id})"
    metadataWrapperServiceUrl = "@Microsoft.KeyVault(SecretUri=${module.api_wrapper.url_secret_id})"

    sql_server = "@Microsoft.KeyVault(SecretUri=${data.azurerm_key_vault_secret.SqlServer.id})"
    sql_database = "@Microsoft.KeyVault(SecretUri=${data.azurerm_key_vault_secret.SqlDatabase.id})"
    sql_login = "@Microsoft.KeyVault(SecretUri=${data.azurerm_key_vault_secret.SqlLogin.id})"
    sql_password = "@Microsoft.KeyVault(SecretUri=${data.azurerm_key_vault_secret.SqlPassword.id})"
  }
}

module "json_generator" {
  source = "./python_function_app"

  name                      = "jsongenerator"
  resource_group_name       = "${azurerm_resource_group.functionapp.name}"
  location                  = "${azurerm_app_service_plan.function.location}"
  app_service_plan_id       = "${azurerm_app_service_plan.function.id}"
  storage_connection_string = "${data.azurerm_storage_account.base.primary_connection_string}"

  base_resource_group_name = "${var.base_resource_group_name}"
  base_acr_name = "${var.base_acr_name}"
  base_keyvault_name = "${var.base_keyvault_name}"

  url_secret_name = "JsonGeneratorServiceUrl"

  docker_image = "metadata/json_generator"

  app_settings = {}
}

