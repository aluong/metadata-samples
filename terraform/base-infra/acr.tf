resource "azurerm_container_registry" "this" {
  name                     = "${var.acr_name}"
  resource_group_name      = "${azurerm_resource_group.this.name}"
  location                 = "${azurerm_resource_group.this.location}"
  sku                      = "Standard"
  admin_enabled            = true
}

resource "azurerm_role_assignment" "acr-contributor" {
  scope                            = "${azurerm_container_registry.this.id}"
  role_definition_name             = "Contributor"
  principal_id                     = "${azurerm_user_assigned_identity.this.principal_id}"
  skip_service_principal_aad_check = true
}
