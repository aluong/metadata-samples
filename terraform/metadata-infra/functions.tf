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


module "qns" {
  source = "./python_function_app"

  name                      = "qns"
  resource_group_name       = "${azurerm_resource_group.functionapp.name}"
  location                  = "${azurerm_app_service_plan.function.location}"
  app_service_plan_id       = "${azurerm_app_service_plan.function.id}"
  storage_connection_string = "${data.azurerm_storage_account.base.primary_connection_string}"

  docker_image = "wgbs/qns:latest"
  app_settings = {}
  base_resource_group_name = "${var.base_resource_group_name}"
  base_acr_name = "${var.base_acr_name}"
  base_keyvault_name = "${var.base_keyvault_name}"
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

  docker_image = "wgbs/lineage_creator:latest"
  app_settings = {
    qualifiedNameServiceUrl = "test"
#    qualifiedNameServiceKey = "${azurerm_function_app.qns.default_hostname}"
#    jsonGeneratorServiceUrl = "https://${azurerm_function_app.json_generator.default_hostname}"
#    metadataWrapperServiceUrl = "https://${azurerm_app_service.metadata_wrapper.default_site_hostname}"

    # sql_server = "<sqlservername>.database.windows.net"
    # sql_database = "<database with lineage requests>"
    # sql_login = "<login>"
    # sql_password = "<password>"
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

  docker_image = "wgbs/json_generator:latest"

  app_settings = {}
}

