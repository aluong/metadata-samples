locals {
  func_name = "${join("", ["func", substr(md5(azurerm_resource_group.functionapp.name), 0, 8)])}"
}

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

resource "azurerm_function_app" "qns" {
  name                      = "${local.func_name}"
  resource_group_name       = "${azurerm_resource_group.functionapp.name}"
  location                  = "${azurerm_app_service_plan.function.location}"
  app_service_plan_id       = "${azurerm_app_service_plan.function.id}"
  storage_connection_string = "${data.azurerm_storage_account.base.primary_connection_string}"
  
  site_config {
    linux_fx_version = "DOCKER|${data.azurerm_container_registry.base.login_server}/wgbs/qns:latest"

  }

  version = "~2"

  app_settings = {
    WEBSITES_ENABLE_APP_SERVICE_STORAGE = false

    "FUNCTIONS_WORKER_RUNTIME"     = "python"
    "WEBSITE_NODE_DEFAULT_VERSION" = "10.14.1"

    DOCKER_ENABLE_CI = true
    DOCKER_REGISTRY_URL = "${data.azurerm_container_registry.base.login_server}"
    DOCKER_REGISTRY_SERVER_USERNAME = "${data.azurerm_container_registry.base.admin_username}"
    DOCKER_REGISTRY_SERVER_PASSWORD = "${data.azurerm_container_registry.base.admin_password}"
  }

  # Ignoring putting function app in VNet because specified region is unclear
  # site_config {
    # virtual_network_name = "${var.base_vnet_name}"
  # }
}
