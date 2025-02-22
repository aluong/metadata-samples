resource "azurerm_data_factory" "lineage" {
  name                = "${var.data_factory_name}"
  location            = "${azurerm_resource_group.this.location}"
  resource_group_name = "${azurerm_resource_group.this.name}"
}

resource "azurerm_data_factory_pipeline" "lineage_copy" {
  name                = "${azurerm_data_factory.lineage.name}-message-post"
  resource_group_name = "${azurerm_resource_group.this.name}"
  data_factory_name   = "${azurerm_data_factory.lineage.name}"
}

resource "azurerm_template_deployment" "test" {
  name                = "acctesttemplate-01"
  resource_group_name = "${azurerm_resource_group.this.name}"
  template_body = <<DEPLOY
 {
    "$schema": "http://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "factoryName": {
            "type": "string",
            "metadata": "Data Factory name"
        },
        "sqldatabase_connectionString": {
            "type": "secureString",
            "metadata": "Secure string for 'connectionString' of 'sqldatabase'"
        }
    },
    "variables": {
        "factoryId": "[concat('Microsoft.DataFactory/factories/', parameters('factoryName'))]"
    },
    "resources":[
        {
        "name": "[concat(parameters('factoryName'), '/CreateLineageSp')]",
        "type": "Microsoft.DataFactory/factories/pipelines",
        "apiVersion": "2018-06-01",
        "properties": {
            "activities": [
                {
                    "name": "Execute sp",
                    "type": "SqlServerStoredProcedure",
                    "dependsOn": [],
                    "policy": {
                        "timeout": "7.00:00:00",
                        "retry": 0,
                        "retryIntervalInSeconds": 30,
                        "secureOutput": false,
                        "secureInput": false
                    },
                    "userProperties": [],
                    "typeProperties": {
                        "storedProcedureName": "[[dbo].[sp_create_lineage]",
                        "storedProcedureParameters": {
                            "activity_name": {
                                "value": {
                                    "value": "@pipeline().parameters.ActivityName",
                                    "type": "Expression"
                                },
                                "type": "String"
                            },
                            "datafactory_name": {
                                "value": {
                                    "value": "@pipeline().DataFactory",
                                    "type": "Expression"
                                },
                                "type": "String"
                            },
                            "pipeline_name": {
                                "value": {
                                    "value": "@pipeline().parameters.PipelineName",
                                    "type": "Expression"
                                },
                                "type": "String"
                            },
                            "destination_azure_resource": {
                                "value": {
                                    "value": "@pipeline().parameters.DestinationAzureResource",
                                    "type": "Expression"
                                },
                                "type": "String"
                            },
                            "destination_dataset": {
                                "value": {
                                    "value": "@pipeline().parameters.DestinationDataset",
                                    "type": "Expression"
                                },
                                "type": "String"
                            },
                            "destination_type": {
                                "value": {
                                    "value": "@pipeline().parameters.DestinationType",
                                    "type": "Expression"
                                },
                                "type": "String"
                            },
                            "execution_end_time": {
                                "value": {
                                    "value": "@pipeline().parameters.ExecutionEndTime",
                                    "type": "Expression"
                                },
                                "type": "String"
                            },
                            "execution_start_time": {
                                "value": {
                                    "value": "@pipeline().parameters.ExecutionStartTime",
                                    "type": "Expression"
                                },
                                "type": "String"
                            },
                            "source_azure_resource": {
                                "value": {
                                    "value": "@pipeline().parameters.SourceAzureResource",
                                    "type": "Expression"
                                },
                                "type": "String"
                            },
                            "source_dataset": {
                                "value": {
                                    "value": "@pipeline().parameters.SourceDataset",
                                    "type": "Expression"
                                },
                                "type": "String"
                            },
                            "source_type": {
                                "value": {
                                    "value": "@pipeline().parameters.SourceType",
                                    "type": "Expression"
                                },
                                "type": "String"
                            }
                        }
                    },
                    "linkedServiceName": {
                        "referenceName": "sqldatabase",
                        "type": "LinkedServiceReference"
                    }
                }
            ],
            "parameters": {
                "ExecutionStartTime": {
                    "type": "string",
                },
                "ExecutionEndTime": {
                    "type": "string",
                },
                "SourceDataset": {
                    "type": "string",
                    "defaultValue": "OneFile"
                },
                "SourceType": {
                    "type": "string",
                },
                "SourceAzureResource": {
                    "type": "string",
                },
                "DestinationDataset": {
                    "type": "string",
                },
                "DestinationType": {
                    "type": "string",
                    "defaultValue": "azure_datalake_gen2_resource_set"
                },
                "DestinationAzureResource": {
                    "type": "string",
                },
                "PipelineName": {
                    "type": "string",
                    "defaultValue": "pipelineName"
                },
                "ActivityName": {
                    "type": "string",
                    "defaultValue": "ActivityName"
                }
            },
            "variables": {
                "MessageText": {
                    "type": "String"
                }
            },
            "annotations": []
        },
        "dependsOn": [
            "[concat(variables('factoryId'), '/linkedServices/sqldatabase')]"
        ]
    },
    {
        "name": "[concat(parameters('factoryName'), '/sqldatabase')]",
        "type": "Microsoft.DataFactory/factories/linkedServices",
        "apiVersion": "2018-06-01",
        "properties": {
            "annotations": [],
            "type": "AzureSqlDatabase",
            "typeProperties": {
                "connectionString": "[parameters('sqldatabase_connectionString')]"
            }
        },
        "dependsOn": []
    }]
} 
DEPLOY
  parameters = {
    "factoryName" = "${azurerm_data_factory.lineage.name}",
    "sqldatabase_connectionString" = "${var.sql_db_connection_string}"
  }
  deployment_mode = "Incremental"
}