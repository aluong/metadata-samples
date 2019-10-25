# metadata_infra

## Deploying resources via Terraform

We use Terraform to deploy Azure resources

The terraform folder is separated into two modules:

1. `base-infra` - for starting with no deployed resources
2. `metadata-infra` - if base-infra resources are already deployed

### Base Infrastructure

Navigate to the base infrastructure folder and create a file named `terraform.tfvars`, and fill it using the content from `terraform.tfvars.template` and the values for your own environment. Here's an example of what a concrete config might look like for the `base-infra` module:

```ini
resource_group_name = "base-infra-name"
location = "East US2"
sql_username = "testusername"
sql_password = "testPassw0rd"
adls_name = "baseadls"
acr_name = "baseacr"
keyvault_name = "basekv"
```

After filling in values for your own environment, run:

```
terraform init
terraform apply
```
When prompted type `yes` to create the following resources:

1. Resource Group
2. Virtual Network
3. Subnet
4. Application Insights
5. User Assigned Identity
6. ACR
7. Storage Account
8. ADLS
9. SQL Server
10. SQL DB
11. SQL DW
12. SQL VNet Rule
13. Key Vault
14. Azure Container Registry

If successful, you should see:

```
Apply complete! Resources: 14 added, 0 changed, 0 destroyed. 

Outputs:

base_keyvault_name=""
base_user_assigned_identity_name=""
base_storage_account_name=""
base_resource_group_name=""
base_vnet_name=""
base_acr_name=""
```

These output values will be used in the `terraform.tfvars` file in the metadata folder. You can copy paste them to the file.


### Metadata Infrastructure

Navigate to the metadata infrastructure folder and create a file named `terraform.tfvars`, and fill it using the content from `terraform.tfvars.template` and the values for your own environment. Here's an example of what a concrete config might look like for the `metadata-infra` module:

```ini
base_storage_account_name = "storage00000000"
base_resource_group_name = "base-infra-name"
base_vnet_name = "base-infra-name-basevnet"
base_user_assigned_identity_name = "base-infra-name-webapp"
base_acr_name="base-infra-acr"
base_keyvault_name="base-infra-keyvault"

resource_group_name = "metadata-test" 
location="eastus2"
databricks_name = "metadatabricks"
atlas_dns_name = "metadatadns"
data_factory_name = "metadatafactory"

app_service_plan_name = "metadata-service-plan"
```

You can easily access the `base_` information by running `terraform output` in the `base-infra` folder.
 After filling in values for your own environment, run:

```
terraform init
terraform apply
```
When prompted type `yes` to create the following resources:

1. Resource Group
2. Resource Group for Function ASP
3. Resource Group for WebApp ASP
4. ADF
5. ADF Pipeline
6. Container Group (Kafka, Atlas images)
7. Databricks workspace
8. VNet peering for databricks
9. ASP for Azure Functions
10. Function app (lineage creator)
11. ASP for WebApps
12. Webapp (metadata wrapper)


WebApp is wired up to run Dockerized Java application pushed to the ACR. It takes less than 10 minutes after image is pushed until webapp is up and running.
