
resource "azurerm_sql_server" "base" {
  name                         = "${azurerm_resource_group.this.name}-base"
  resource_group_name          = "${azurerm_resource_group.this.name}"
  location                     = "${var.location}"
  version                      = "12.0"
  administrator_login          = "${var.sql_username}"
  administrator_login_password = "${var.sql_password}"
}

resource "azurerm_sql_database" "base_db" {
  name                = "${azurerm_resource_group.this.name}-base-db"
  resource_group_name = "${azurerm_resource_group.this.name}"
  location            = "${var.location}"
  server_name         = "${azurerm_sql_server.base.name}"
}

resource "azurerm_sql_database" "base_dw" {
  name                             = "${azurerm_resource_group.this.name}-base-dw"
  resource_group_name              = "${azurerm_resource_group.this.name}"
  location                         = "${var.location}"
  server_name                      = "${azurerm_sql_server.base.name}"
  edition                          = "DataWarehouse"
  requested_service_objective_name = "DW100c"
}

resource "azurerm_sql_firewall_rule" "azure_services" {
  name                = "AzureServicesAccess"
  resource_group_name = "${azurerm_resource_group.this.name}"
  server_name         = "${azurerm_sql_server.base.name}"
  start_ip_address    = "0.0.0.0"
  end_ip_address      = "0.0.0.0"
}

# Allow public IPs
resource "azurerm_sql_firewall_rule" "public" {
  name                = "ClientIPAddress"
  resource_group_name = "${azurerm_resource_group.this.name}"
  server_name         = "${azurerm_sql_server.base.name}"
  start_ip_address    = "0.0.0.0"
  end_ip_address      = "255.255.255.255"
}
# resource "azurerm_sql_virtual_network_rule" "vnet_sql_association" {
#   name                = "${azurerm_sql_server.base.name}-vnet-rule"
#   resource_group_name = "${azurerm_resource_group.this.name}"
#   server_name         = "${azurerm_sql_server.base.name}"
#   subnet_id           = "${azurerm_subnet.this.id}"
# }

resource "azurerm_key_vault_secret" "sql_server" {
  name         = "SqlServer"
  value        = "${azurerm_sql_server.base.fully_qualified_domain_name}"
  key_vault_id = "${azurerm_key_vault.this.id}"
}

resource "azurerm_key_vault_secret" "sql_database" {
  name         = "SqlDatabase"
  value        = "${azurerm_sql_database.base_db.name}"
  key_vault_id = "${azurerm_key_vault.this.id}"
}

resource "azurerm_key_vault_secret" "sql_login" {
  name         = "SqlLogin"
  value        = "${var.sql_username}"
  key_vault_id = "${azurerm_key_vault.this.id}"
}

resource "azurerm_key_vault_secret" "sql_password" {
  name         = "SqlPassword"
  value        = "${var.sql_password}"
  key_vault_id = "${azurerm_key_vault.this.id}"
}