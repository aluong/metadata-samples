resource "azurerm_key_vault" "this" {
  name                        = "${var.keyvault_name}"
  location                    = "${azurerm_resource_group.this.location}"
  resource_group_name         = "${azurerm_resource_group.this.name}"
  enabled_for_disk_encryption = true
  tenant_id                   = "${data.azurerm_client_config.current.tenant_id}"
  sku_name = "standard"

  access_policy {
      tenant_id = "${data.azurerm_client_config.current.tenant_id}"
      object_id = "${data.azurerm_client_config.current.object_id}"

      secret_permissions = [
        "get",
        "list",
        "set",
        "delete",
        "backup",
        "purge",
        "recover",
        "restore"
      ]
  }

  access_policy  {
      tenant_id = "${data.azurerm_client_config.current.tenant_id}"
      object_id = "${azurerm_user_assigned_identity.this.principal_id}"

      secret_permissions = [
        "get",
        "list",
        "set",
        "delete",
        "backup",
        "purge",
        "recover",
        "restore"
      ]
    }

  lifecycle {
    ignore_changes = [access_policy]
  }
}
