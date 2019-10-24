import logging

from .qualified_name_client.generated.swagger.models.azure_datalake_gen2_filesystem_py3 import AzureDatalakeGen2Filesystem
from .qualified_name_client.generated.swagger.models.azure_datalake_gen2_resource_set_py3 import AzureDatalakeGen2ResourceSet
from .qualified_name_client.generated.swagger.models.azure_cosmosdb_container_py3 import AzureCosmosdbContainer
from .qualified_name_client.generated.swagger.models.azure_sql_table_py3 import AzureSqlTable
from .qualified_name_client.generated.swagger.models.azure_storage_service_py3 import AzureStorageService
from .qualified_name_client.generated.swagger.models.tabular_schema_py3 import TabularSchema
from .qualified_name_client.generated.swagger.models.file_server_py3 import FileServer
from .qualified_name_client.generated.swagger.models.file_path_py3 import FilePath
from .qualified_name_client.generated.swagger.models.azure_cosmosdb_database_py3 import AzureCosmosdbDatabase

from urllib.parse import urlparse

def buildDatasetQNRequest(dataset):

    datasetType = dataset['type']

    if datasetType == 'azure_datalake_gen2_resource_set':
        azure_resource = dataset['azure_resource']
        url = urlparse(azure_resource)

        azure_storage_uri = '%s://%s' %(url.scheme, url.hostname)
        (_, filesystem_name, resource_set_path) = url.path.split('/', 2)

        resource_set_path = resource_set_path.strip("/")

        result = AzureDatalakeGen2ResourceSet(**{
                'azure_storage_uri' : azure_storage_uri,
                'filesystem_name' : filesystem_name,
                'resource_set_path' : resource_set_path
            })
    elif datasetType == 'tabular_schema':
        azure_resource = dataset['azure_resource']
        url = urlparse(azure_resource)

        azure_storage_uri = '%s://%s' %(url.scheme, url.hostname)
        (_, filesystem_name, resource_set_path) = url.path.split('/', 2)

        resource_set_path = resource_set_path.strip("/")

        result = TabularSchema(**{
                'azure_storage_uri' : azure_storage_uri,
                'filesystem_name' : filesystem_name,
                'resource_set_path' : resource_set_path
            })
    elif datasetType == 'azure_datalake_gen2_filesystem':
        azure_resource = dataset['azure_resource']
        url = urlparse(azure_resource)

        azure_storage_uri = '%s://%s' %(url.scheme, url.hostname)
        (_, filesystem_name) = url.path.split('/', 1)

        filesystem_name = filesystem_name.strip("/")

        result = AzureDatalakeGen2Filesystem(**{
                'azure_storage_uri' : azure_storage_uri,
                'filesystem_name' : filesystem_name
            })
    elif datasetType == 'file_path':
        azure_resource = dataset['azure_resource']
        url = urlparse(azure_resource)

        (_, file_path) = url.path.split('/', 1)

        file_path = file_path.strip("/")

        result = FilePath(**{
                'hostname' : url.hostname,
                'file_path' : file_path,
            })
    elif datasetType == 'azure_cosmosdb_container':

        azure_resource = dataset['azure_resource']
        url = urlparse(azure_resource)

        cosmosdb_uri = '%s://%s' %(url.scheme, url.hostname)
        (_, database, container) = url.path.split('/', 2)

        container = container.strip("/")

        result = AzureCosmosdbContainer(**{
                'cosmosdb_uri' : cosmosdb_uri,
                'cosmosdb_database' : database,
                'container_name' : container
            })
    elif datasetType == 'azure_cosmosdb_database':

        azure_resource = dataset['azure_resource']
        url = urlparse(azure_resource)

        cosmosdb_uri = '%s://%s' %(url.scheme, url.hostname)
        (_, database) = url.path.split('/', 1)

        database = database.strip("/")

        result = AzureCosmosdbDatabase(**{
                'cosmosdb_uri' : cosmosdb_uri,
                'cosmosdb_database' : database
            })
    elif datasetType == 'azure_storage_service':
        result = AzureStorageService(**{
                'uri' : dataset['azure_resource'].strip("/"),
            })
    elif datasetType == 'file_server':
        result = FileServer(**{
                'hostname' : dataset['azure_resource'].strip("/"),
            })
    elif datasetType == 'azure_sql_table':

        azure_resource = dataset['azure_resource']
        url = urlparse(azure_resource)

        azure_sql_server_uri = '%s://%s' %(url.scheme, url.hostname)
        (_, database_name, azure_sql_table_name) = url.path.split('/', 2)

        azure_sql_table_name = azure_sql_table_name.strip("/")

        result = AzureSqlTable(**{
                'azure_sql_server_uri' : azure_sql_server_uri,
                'database_name' : database_name,
                'azure_sql_table_name' : azure_sql_table_name
            })
    else:
        logging.error('Unsupported lineage dataset type "%s"' % datasetType)
        return None

    return result
