locals {
  unique_id = "${substr(md5(var.resource_group_name), 0, 8)}"
}

resource "azurerm_storage_account" "this" {
  name                     = "${join("", ["storage", local.unique_id])}"
  resource_group_name      = "${azurerm_resource_group.this.name}"
  location                 = "${var.location}"
  account_kind             = "StorageV2"
  account_tier             = "Standard"
  account_replication_type = "LRS"
  is_hns_enabled           = "true"

  # Associates SA under VNet
  network_rules {
    # Allow for now as trying to add ADLS Gen2 after network rule is in place denies request from outside IP
    default_action             = "Allow"
    bypass                     = ["AzureServices"]
    virtual_network_subnet_ids = ["${azurerm_subnet.this.id}"]
  }
}

resource "azurerm_storage_data_lake_gen2_filesystem" "this" {
  name               = "${azurerm_resource_group.this.name}"
  storage_account_id = azurerm_storage_account.this.id
}
