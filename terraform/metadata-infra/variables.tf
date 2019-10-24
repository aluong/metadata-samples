variable "resource_group_name" {
  description = "Name of resource group"
  type        = "string"
}

variable "location" {
  description = "Location of resource group"
  type        = "string"
  default     = "East US2"
}

variable "base_storage_account_name" {
  description = "Name of the base storage account "
  type        = "string"
}

variable "databricks_name" {
  description = "Name of databricks cluster"
  type        = "string"
}

variable "base_resource_group_name" {
  description = "Name of base resource group"
  type        = "string"
}

variable "base_vnet_name" {
  description = "Name of base vnet resource"
  type        = "string"
}

variable "app_service_plan_name" {
  description = "Name of the app service plan"
  type        = "string"
  default     = "azure-functions-service-plan"
}

# Premium app service plan cannot be deployed in East US2
variable "app_service_plan_location" {
  description = "Location of app service plan"
  type        = "string"
  default     = "East US"
}

variable "func_app_service_plan_tier" {
  description = "Tier of the App Service Plan"
  type        = "string"
  default     = "PremiumV2"
}

variable "func_app_service_plan_size" {
  description = "Size of the App Service Plan"
  type        = "string"
  default     = "P1v2"
}

variable "web_app_service_plan_tier" {
  description = "Tier of the App Service Plan"
  type        = "string"
  default     = "PremiumV2"
}

variable "web_app_service_plan_size" {
  description = "Size of the App Service Plan"
  type        = "string"
  default     = "P1v2"
}

variable "base_user_assigned_identity_name" {
  description = "Name of the base user assigned identity"
  type        = "string"
}

variable "atlas_dns_name" {
  description = "Hostname for Atlas, and used to derive container name"
  type        = "string"
}

variable "data_factory_name" {
  description = "Name of Azure Data Factory"
  type    = "string"
}

variable "base_keyvault_name" {
  type = "string"
}

variable "base_acr_name" {
  type = "string"
}

variable "sql_db_connection_string" {
 type = "string" 
}
