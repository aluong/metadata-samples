import unittest 
import os

#from ..src.azfunctions.lineageCreator import qnRequestBuilder
# temporal workaround for importing modules from the parent directory
import sys
sys.path.insert(0,'..') 
from src.azfunctions.lineageCreator.qnRequestBuilder import buildDatasetQNRequest
  
class QnRequestBuilderTest(unittest.TestCase): 
  
    def testAdlsResourceSet(self):
        azure_storage_uri = 'http://storageaccounrt.azure.whatever'
        filesystem_name = 'thefs'
        resource_set_path = 'the/rest/of/the/path'
        azure_resource = '%s/%s/%s' % (azure_storage_uri, filesystem_name, resource_set_path)

        dataset = {'azure_resource' : azure_resource, 'type' : 'azure_datalake_gen2_resource_set'}

        result = buildDatasetQNRequest(dataset)

        self.assertEqual(azure_storage_uri, result.azure_storage_uri) 
        self.assertEqual(filesystem_name, result.filesystem_name) 
        self.assertEqual(resource_set_path, result.resource_set_path) 
  
    def testAdlsResourceSetSlash(self):
        azure_storage_uri = 'http://storageaccounrt.azure.whatever'
        filesystem_name = 'thefs'
        resource_set_path = 'the/rest/of/the/path'
        azure_resource = '%s/%s/%s/' % (azure_storage_uri, filesystem_name, resource_set_path)

        dataset = {'azure_resource' : azure_resource, 'type' : 'azure_datalake_gen2_resource_set'}

        result = buildDatasetQNRequest(dataset)

        self.assertEqual(azure_storage_uri, result.azure_storage_uri) 
        self.assertEqual(filesystem_name, result.filesystem_name) 
        self.assertEqual(resource_set_path, result.resource_set_path) 
  
    def testTabularSchema(self):
        azure_storage_uri = 'http://storageaccounrt.azure.whatever'
        filesystem_name = 'thefs'
        resource_set_path = 'the/rest/of/the/path'
        azure_resource = '%s/%s/%s/' % (azure_storage_uri, filesystem_name, resource_set_path)

        dataset = {'azure_resource' : azure_resource, 'type' : 'tabular_schema'}

        result = buildDatasetQNRequest(dataset)

        self.assertEqual(azure_storage_uri, result.azure_storage_uri) 
        self.assertEqual(filesystem_name, result.filesystem_name) 
        self.assertEqual(resource_set_path, result.resource_set_path) 
  
    def testDatalakeRoot(self):
        azure_storage_uri = 'http://storageaccounrt.azure.whatever'
        filesystem_name = 'thefs'
        azure_resource = '%s/%s/' % (azure_storage_uri, filesystem_name)

        dataset = {'azure_resource' : azure_resource, 'type' : 'azure_datalake_gen2_filesystem'}

        result = buildDatasetQNRequest(dataset)

        self.assertEqual(azure_storage_uri, result.azure_storage_uri) 
        self.assertEqual(filesystem_name, result.filesystem_name) 
  
    def testFilePath(self):
        host = 'somehost.azure.whatever'
        file_path = 'some/path/1'
        azure_resource = 'http://%s/%s' % (host, file_path)

        dataset = {'azure_resource' : azure_resource, 'type' : 'file_path'}

        result = buildDatasetQNRequest(dataset)

        self.assertEqual(host, result.hostname) 
        self.assertEqual(file_path, result.file_path) 
  
    def testFilePathSlash(self):
        host = 'somehost.azure.whatever'
        file_path = 'some/path/1'
        azure_resource = 'http://%s/%s/' % (host, file_path)

        dataset = {'azure_resource' : azure_resource, 'type' : 'file_path'}

        result = buildDatasetQNRequest(dataset)

        self.assertEqual(host, result.hostname) 
        self.assertEqual(file_path, result.file_path) 
  
    def testCosmosContainer(self):
        cosmosdb_uri = 'http://storageaccounrt.azure.whatever'
        cosmosdb_database = 'database'
        container_name = 'containername'
        azure_resource = '%s/%s/%s/' % (cosmosdb_uri, cosmosdb_database, container_name)

        dataset = {'azure_resource' : azure_resource, 'type' : 'azure_cosmosdb_container'}

        result = buildDatasetQNRequest(dataset)

        self.assertEqual(cosmosdb_uri, result.cosmosdb_uri) 
        self.assertEqual(cosmosdb_database, result.cosmosdb_database) 
        self.assertEqual(container_name, result.container_name) 
  
    def testCosmosDatabase(self):
        cosmosdb_uri = 'http://storageaccounrt.azure.whatever'
        cosmosdb_database = 'database'
        azure_resource = '%s/%s/' % (cosmosdb_uri, cosmosdb_database)

        dataset = {'azure_resource' : azure_resource, 'type' : 'azure_cosmosdb_database'}

        result = buildDatasetQNRequest(dataset)

        self.assertEqual(cosmosdb_uri, result.cosmosdb_uri) 
        self.assertEqual(cosmosdb_database, result.cosmosdb_database) 
  
    def testSqlTable(self):
        azure_sql_server_uri = 'http://sql-server.azure.whatever'
        database_name = 'database'
        azure_sql_table_name = 'tablename'

        azure_resource = '%s/%s/%s/' % (azure_sql_server_uri, database_name, azure_sql_table_name)

        dataset = {'azure_resource' : azure_resource, 'type' : 'azure_sql_table'}

        result = buildDatasetQNRequest(dataset)

        self.assertEqual(azure_sql_server_uri, result.azure_sql_server_uri) 
        self.assertEqual(database_name, result.database_name) 
        self.assertEqual(azure_sql_table_name, result.azure_sql_table_name) 
  
    def testAzureStorageService(self):
        uri = 'http://some.azure.whatever'

        dataset = {'azure_resource' : uri + '/', 'type' : 'azure_storage_service'}

        result = buildDatasetQNRequest(dataset)

        self.assertEqual(uri, result.uri) 
  
    def testAzureStorageServiceSlash(self):
        uri = 'http://some.azure.whatever'

        dataset = {'azure_resource' : uri + '/', 'type' : 'azure_storage_service'}

        result = buildDatasetQNRequest(dataset)

        self.assertEqual(uri, result.uri) 
  
    def testFileServer(self):
        hostname = 'hostname'

        dataset = {'azure_resource' : hostname + '/', 'type' : 'file_server'}

        result = buildDatasetQNRequest(dataset)

        self.assertEqual(hostname, result.hostname) 
  
if __name__ == '__main__': 
    unittest.main() 