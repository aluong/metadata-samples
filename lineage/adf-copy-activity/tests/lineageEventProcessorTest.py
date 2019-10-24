import uuid
import unittest 
import os
from unittest.mock import MagicMock, call
import datetime
import json


#from ..src.azfunctions.lineageCreator import qnRequestBuilder
# temporal workaround for importing modules from the parent directory
import sys
sys.path.insert(0,'..') 
from src.azfunctions.lineageCreator import LineageEventProcessor
from src.azfunctions.lineageCreator.qualified_name_client.generated.swagger.models.qualified_name_py3 import QualifiedName
from src.azfunctions.lineageCreator.qualified_name_client.generated.swagger.models.azure_sql_table_py3 import AzureSqlTable
from src.azfunctions.lineageCreator.qualified_name_client.generated.swagger.models.azure_datalake_gen2_filesystem_py3 import AzureDatalakeGen2Filesystem
from src.azfunctions.lineageCreator.qualified_name_client.generated.swagger.models.azure_datalake_gen2_resource_set_py3 import AzureDatalakeGen2ResourceSet
from src.azfunctions.lineageCreator.qualified_name_client.generated.swagger.models.adf_copy_activity_py3 import AdfCopyActivity

from src.azfunctions.lineageCreator.json_generator_client.generated.swagger.models.response_py3 import Response
from src.azfunctions.lineageCreator.json_generator_client.generated.swagger.models.entities_py3 import Entities
from src.azfunctions.lineageCreator.json_generator_client.generated.swagger.models.attributes_py3 import Attributes
from src.azfunctions.lineageCreator.json_generator_client.generated.swagger.models import Request, Response, Inputs, Outputs, ProcessAttributes

class MockQualifiedNameClient:  
    def get_qualified_name(self): return None

class MockJsonGeneratorClient:  
    def get_qualified_name(self): return None

class MockMetadataClient:  
    def entity_post_using_post(self): return None

config = {'qualifiedNameServiceKey' : 'qualifiedNameServiceKey', 'jsonGeneratorServiceKey' : 'jsonGeneratorServiceKey'}

class LineageEventProcessorTest(unittest.TestCase): 
  
    def testscanEventSimple(self):

        processor = LineageEventProcessor(config)

        start_time1 = datetime.datetime(2019, 1, 1, 1, 1, 1)
        end_time1 =datetime.datetime(2019, 1, 1, 1, 1, 10)

        start_time2 = datetime.datetime(2019, 1, 1, 1, 2, 1)
        end_time2 =datetime.datetime(2019, 1, 1, 1, 2, 10)

        datasets = [{
                'activity_name': 'Copy SQL to ADLS',
                'azure_resource': 'https://gbssqlserver.database.windows.net/gbssqldw/salesv2',
                'datafactory_name': 'walmart-gbs-adf',
                'dataset': 'AzureSqlDWTable1',
                'dataset_id': 42,
                'direction': 'source',
                'execution_end_time': end_time1,
                'execution_start_time': start_time1,
                'pipeline_name': 'DataCopyWithLineage',
                'request_id': 9,
                'type': 'azure_sql_table'
            }, {
                'activity_name': 'Copy SQL to ADLS',
                'azure_resource': 'https://beamdatav2.dfs.core.windows.net/salesv2',
                'datafactory_name': 'walmart-gbs-adf',
                'dataset': 'salesadlsv2',
                'dataset_id': 43,
                'direction': 'destination',
                'execution_end_time': end_time1,
                'execution_start_time': start_time1,
                'pipeline_name': 'DataCopyWithLineage',
                'request_id': 9,
                'type': 'azure_datalake_gen2_filesystem'
            }, {
                'activity_name': 'Copy Data1',
                'azure_resource': 'https://beamdatav2.dfs.core.windows.net/sales/2019/8/20/0/0/sales-201982000.csv',
                'datafactory_name': 'walmart-gbs-adf',
                'dataset': 'SampleAdlsSource',
                'dataset_id': 44,
                'direction': 'source',
                'execution_end_time': end_time2,
                'execution_start_time': start_time2,
                'pipeline_name': 'DataCopyWithLineage',
                'request_id': 10,
                'type': 'azure_datalake_gen2_resource_set'
            }, {
                'activity_name': 'Copy Data1',
                'azure_resource': 'https://beamdatav2.dfs.core.windows.net/salesv2',
                'datafactory_name': 'walmart-gbs-adf',
                'dataset': 'salesadlsv2',
                'dataset_id': 45,
                'direction': 'destination',
                'execution_end_time': end_time2,
                'execution_start_time': start_time2,
                'pipeline_name': 'DataCopyWithLineage',
                'request_id': 10,
                'type': 'azure_datalake_gen2_filesystem'
            }
        ]

        processor.sql.getModifiedDatasets = MagicMock(return_value=datasets)

        processor.sql.deleteRequests = MagicMock()

        #region Qualified Name client mock setup
        qnClientMock = MockQualifiedNameClient()

        processor.restFactory.getQnClient = MagicMock(return_value=qnClientMock)

        qnClientMock.get_qualified_name = MagicMock()

        qnNames = [ 
                'https://gbssqlserver.database.windows.net/gbssqldw/salesv2',
                'https://beamdatav2.dfs.core.windows.net/salesv2',
                'https://beamdatav2.dfs.core.windows.net/sales/2019/8/20/0/0/sales-201982000.csv',
                'https://beamdatav2.dfs.core.windows.net/salesv2',
                'walmart-gbs-adf/DataCopyWithLineage/Copy SQL to ADLS',
                'walmart-gbs-adf/DataCopyWithLineage/Copy Data1'
            ]

        qnResponses = [QualifiedName(**{'guid': uuid.uuid4(), 'is_exists': True, 'qualified_name': n}) for n in qnNames]

        qnClientMock.get_qualified_name.side_effect = qnResponses

        #endregion Qualified Name client mock setup

        #region Json Generator mock setup
        jsonGeneratorClientMock = MockJsonGeneratorClient()

        processor.restFactory.getJsonGeneratorClient = MagicMock(return_value=jsonGeneratorClientMock)

        jsonGeneratorClientMock.create_lineage_data = MagicMock()

        json1 = Response(entities=[Entities(
            guid=qnResponses[4].guid,
            type_name='adf_copy_activity', 
            created_by='ADF', 
            attributes=Attributes(
                inputs=[Inputs(guid=qnResponses[0].guid, type_name='azure_sql_table')],
                outputs=[Outputs(guid=qnResponses[1].guid, type_name='azure_datalake_gen2_filesystem')],
                qualified_name='walmart-gbs-adf/DataCopyWithLineage/Copy SQL to ADLS', 
                name='Copy SQL to ADLS', 
                start_time=int(start_time1.timestamp()),
                end_time=int(end_time1.timestamp())
            )
            )])

        json2 = Response(entities=[Entities(
            guid=qnResponses[5].guid,
            type_name='adf_copy_activity', 
            created_by='ADF', 
            attributes=Attributes(
                inputs=[Inputs(guid=qnResponses[2].guid, type_name='azure_datalake_gen2_resource_set')],
                outputs=[Outputs(guid=qnResponses[3].guid, type_name='azure_datalake_gen2_filesystem')],
                qualified_name='walmart-gbs-adf/DataCopyWithLineage/Copy Data1', 
                name='Copy Data1', 
                start_time=int(start_time2.timestamp()),
                end_time=int(end_time2.timestamp())
            )
            )])

        jsonGeneratorClientMock.create_lineage_data.side_effect = [json1, json2]

        #endregion Json Generator mock setup

        #region Metadata Client mock setup
        metadataClientMock = MockMetadataClient()

        processor.restFactory.getMetadataClient = MagicMock(return_value=metadataClientMock)

        metadataClientMock.entity_bulk_post_using_post = MagicMock()

        metadataClientMock.entity_bulk_post_using_post.side_effect = ['mockedresponse1', 'mockedresponse2']
        #endregion Metadata Client mock setup

        # invoke the processor

        processor.scanEvents()

        #region verify qualified name client calls

        expectedQnCall1 = call(
            body=AzureSqlTable(**{
                'azure_sql_server_uri' : 'https://gbssqlserver.database.windows.net',
                'database_name' : 'gbssqldw',
                'azure_sql_table_name' : 'salesv2'}), 
            code='qualifiedNameServiceKey', 
            type_name='azure_sql_table')

        expectedQnCall2 = call(
            body=AzureDatalakeGen2Filesystem(**{
                'azure_storage_uri' : 'https://beamdatav2.dfs.core.windows.net',
                'filesystem_name' : 'salesv2'}), 
            code='qualifiedNameServiceKey', 
            type_name='azure_datalake_gen2_filesystem')

        expectedQnCall3 = call(
            body=AzureDatalakeGen2ResourceSet(**{
                'azure_storage_uri' : 'https://beamdatav2.dfs.core.windows.net',
                'filesystem_name' : 'sales',
                'resource_set_path' : '2019/8/20/0/0/sales-201982000.csv'}), 
            code='qualifiedNameServiceKey', 
            type_name='azure_datalake_gen2_resource_set')

        expectedQnCall4 = call(
            body=AzureDatalakeGen2Filesystem(**{
                'azure_storage_uri' : 'https://beamdatav2.dfs.core.windows.net',
                'filesystem_name' : 'salesv2'}),
            code='qualifiedNameServiceKey', 
            type_name='azure_datalake_gen2_filesystem')

        expectedQnCall5 = call(
            body=AdfCopyActivity(**{
                'datafactory_name' : 'walmart-gbs-adf',
                'pipeline_name' : 'DataCopyWithLineage',
                'activity_name' : 'Copy SQL to ADLS'}), 
            code='qualifiedNameServiceKey', 
            type_name='adf_copy_activity')

        expectedQnCall6 = call(
            body=AdfCopyActivity(**{
                'datafactory_name' : 'walmart-gbs-adf',
                'pipeline_name' : 'DataCopyWithLineage',
                'activity_name' : 'Copy Data1'}), 
            code='qualifiedNameServiceKey', 
            type_name='adf_copy_activity')

        qnClientMock.get_qualified_name.assert_has_calls([
            expectedQnCall1, 
            expectedQnCall2, 
            expectedQnCall3, 
            expectedQnCall4, 
            expectedQnCall5, 
            expectedQnCall6])
        #endregion verify qualified name client calls

        #region verify json generator client calls

        inputs = [Inputs(guid=qnResponses[0].guid, type_name='azure_sql_table')]
        outputs = [Outputs(guid=qnResponses[1].guid, type_name='azure_datalake_gen2_filesystem')]

        process_attributes = [
            ProcessAttributes(**{
                'attr_name': 'StartTime',
                'attr_value': int(start_time1.timestamp()),
                'is_entityref': False
            }),
            ProcessAttributes(**{
                'attr_name': 'EndTime',
                'attr_value': int(end_time1.timestamp()),
                'is_entityref': False
            })
        ]

        expectedJG1 = call(
            body=Request(
                guid=qnResponses[4].guid,
                name='Copy SQL to ADLS', 
                type_name='adf_copy_activity', 
                qualified_name='walmart-gbs-adf/DataCopyWithLineage/Copy SQL to ADLS', 
                created_by='ADF', 
                process_attributes=process_attributes,
                inputs=inputs, 
                outputs=outputs),
            code='jsonGeneratorServiceKey')

        inputs = [Inputs(guid=qnResponses[2].guid, type_name='azure_datalake_gen2_resource_set')]
        outputs = [Outputs(guid=qnResponses[3].guid, type_name='azure_datalake_gen2_filesystem')]

        process_attributes = [
            ProcessAttributes(**{
                'attr_name': 'StartTime',
                'attr_value': int(start_time2.timestamp()),
                'is_entityref': False
            }),
            ProcessAttributes(**{
                'attr_name': 'EndTime',
                'attr_value': int(end_time2.timestamp()),
                'is_entityref': False
            })
        ]

        expectedJG2 = call(
            body=Request(
                guid=qnResponses[5].guid,
                name='Copy Data1', 
                type_name='adf_copy_activity', 
                qualified_name='walmart-gbs-adf/DataCopyWithLineage/Copy Data1', 
                created_by='ADF', 
                process_attributes=process_attributes,
                inputs=inputs, 
                outputs=outputs),
            code='jsonGeneratorServiceKey')

        jsonGeneratorClientMock.create_lineage_data.assert_has_calls([expectedJG1, expectedJG2])

        #endregion verify json generator client calls

        #region verify metadata client calls

        expectedRequest = {
            "entities": [{
                    "typeName": "adf_copy_activity",
                    "guid": str(qnResponses[4].guid),
                    "createdBy": "ADF",
                    "attributes": {
                        "inputs": [{
                                "guid": str(qnResponses[0].guid),
                                "typeName": "azure_sql_table"
                            }
                        ],
                        "outputs": [{
                                "guid": str(qnResponses[1].guid),
                                "typeName": "azure_datalake_gen2_filesystem"
                            }
                        ],
                        "qualifiedName": "walmart-gbs-adf/DataCopyWithLineage/Copy SQL to ADLS",
                        "name": "Copy SQL to ADLS",
                        "StartTime": int(start_time1.timestamp()),
                        "EndTime": int(end_time1.timestamp())
                    }
                }
            ]
        }

        expectedMD1 = call(expectedRequest)

        expectedRequest = {
            "entities": [{
                    "typeName": "adf_copy_activity",
                    "guid": str(qnResponses[5].guid),
                    "createdBy": "ADF",
                    "attributes": {
                        "inputs": [{
                                "guid": str(qnResponses[2].guid),
                                "typeName": "azure_datalake_gen2_resource_set"
                            }
                        ],
                        "outputs": [{
                                "guid": str(qnResponses[3].guid),
                                "typeName": "azure_datalake_gen2_filesystem"
                            }
                        ],
                        "qualifiedName": "walmart-gbs-adf/DataCopyWithLineage/Copy Data1",
                        "name": "Copy Data1",
                        "StartTime": int(start_time2.timestamp()),
                        "EndTime": int(end_time2.timestamp())
                    }
                }
            ]
        }

        expectedMD2 = call(expectedRequest)

        metadataClientMock.entity_bulk_post_using_post.assert_has_calls([expectedMD1, expectedMD2])

        #endregion verify metadata client calls
  
        processor.sql.deleteRequests.assert_called_with([9, 10])

    def testscanEventMissingEntity(self):

        processor = LineageEventProcessor(config)

        start_time1 = datetime.datetime(2019, 1, 1, 1, 1, 1)
        end_time1 =datetime.datetime(2019, 1, 1, 1, 1, 10)

        start_time2 = datetime.datetime(2019, 1, 1, 1, 2, 1)
        end_time2 =datetime.datetime(2019, 1, 1, 1, 2, 10)

        datasets = [{
                'activity_name': 'Copy SQL to ADLS',
                'azure_resource': 'https://gbssqlserver.database.windows.net/gbssqldw/salesv2',
                'datafactory_name': 'walmart-gbs-adf',
                'dataset': 'AzureSqlDWTable1',
                'dataset_id': 42,
                'direction': 'source',
                'execution_end_time': end_time1,
                'execution_start_time': start_time1,
                'pipeline_name': 'DataCopyWithLineage',
                'request_id': 9,
                'type': 'azure_sql_table'
            }, {
                'activity_name': 'Copy SQL to ADLS',
                'azure_resource': 'https://beamdatav2.dfs.core.windows.net/salesv2',
                'datafactory_name': 'walmart-gbs-adf',
                'dataset': 'salesadlsv2',
                'dataset_id': 43,
                'direction': 'destination',
                'execution_end_time': end_time1,
                'execution_start_time': start_time1,
                'pipeline_name': 'DataCopyWithLineage',
                'request_id': 9,
                'type': 'azure_datalake_gen2_filesystem'
            }, {
                'activity_name': 'Copy Data1',
                'azure_resource': 'https://beamdatav2.dfs.core.windows.net/sales/2019/8/20/0/0/sales-201982000.csv',
                'datafactory_name': 'walmart-gbs-adf',
                'dataset': 'SampleAdlsSource',
                'dataset_id': 44,
                'direction': 'source',
                'execution_end_time': end_time2,
                'execution_start_time': start_time2,
                'pipeline_name': 'DataCopyWithLineage',
                'request_id': 10,
                'type': 'azure_datalake_gen2_resource_set'
            }, {
                'activity_name': 'Copy Data1',
                'azure_resource': 'https://beamdatav2.dfs.core.windows.net/salesv2',
                'datafactory_name': 'walmart-gbs-adf',
                'dataset': 'salesadlsv2',
                'dataset_id': 45,
                'direction': 'destination',
                'execution_end_time': end_time2,
                'execution_start_time': start_time2,
                'pipeline_name': 'DataCopyWithLineage',
                'request_id': 10,
                'type': 'azure_datalake_gen2_filesystem'
            }
        ]

        processor.sql.getModifiedDatasets = MagicMock(return_value=datasets)

        processor.sql.deleteRequests = MagicMock()

        #region Qualified Name client mock setup
        qnClientMock = MockQualifiedNameClient()

        processor.restFactory.getQnClient = MagicMock(return_value=qnClientMock)

        qnClientMock.get_qualified_name = MagicMock()

        qnNames = [ 
                'https://gbssqlserver.database.windows.net/gbssqldw/salesv2',
                'https://beamdatav2.dfs.core.windows.net/salesv2',
                'https://beamdatav2.dfs.core.windows.net/sales/2019/8/20/0/0/sales-201982000.csv',
                'https://beamdatav2.dfs.core.windows.net/salesv2',
                'walmart-gbs-adf/DataCopyWithLineage/Copy SQL to ADLS',
                'walmart-gbs-adf/DataCopyWithLineage/Copy Data1'
            ]

        qnResponses = [
            QualifiedName(**{'guid': None, 'is_exists': False, 'qualified_name': qnNames[0]}),
            QualifiedName(**{'guid': uuid.uuid4(), 'is_exists': True, 'qualified_name': qnNames[2]}),
            QualifiedName(**{'guid': uuid.uuid4(), 'is_exists': True, 'qualified_name': qnNames[3]}),
            QualifiedName(**{'guid': uuid.uuid4(), 'is_exists': True, 'qualified_name': qnNames[5]}),
        ]

        qnClientMock.get_qualified_name.side_effect = qnResponses

        #endregion Qualified Name client mock setup

        #region Json Generator mock setup
        jsonGeneratorClientMock = MockJsonGeneratorClient()

        processor.restFactory.getJsonGeneratorClient = MagicMock(return_value=jsonGeneratorClientMock)

        jsonGeneratorClientMock.create_lineage_data = MagicMock()

        json2 = Response(entities=[Entities(
            guid=qnResponses[3].guid,
            type_name='adf_copy_activity', 
            created_by='ADF', 
            attributes=Attributes(
                inputs=[Inputs(guid=qnResponses[1].guid, type_name='azure_datalake_gen2_resource_set')],
                outputs=[Outputs(guid=qnResponses[2].guid, type_name='azure_datalake_gen2_filesystem')],
                qualified_name='walmart-gbs-adf/DataCopyWithLineage/Copy Data1', 
                name='Copy Data1', 
                start_time=int(start_time2.timestamp()),
                end_time=int(end_time2.timestamp())
            )
            )])

        jsonGeneratorClientMock.create_lineage_data.side_effect = [json2]

        #endregion Json Generator mock setup

        #region Metadata Client mock setup
        metadataClientMock = MockMetadataClient()

        processor.restFactory.getMetadataClient = MagicMock(return_value=metadataClientMock)

        metadataClientMock.entity_bulk_post_using_post = MagicMock()

        metadataClientMock.entity_bulk_post_using_post.side_effect = ['mockedresponse2']

        #endregion Metadata Client mock setup

        # invoke the processor

        processor.scanEvents()

        #region verify qualified name client calls

        expectedQnCall1 = call(
            body=AzureSqlTable(**{
                'azure_sql_server_uri' : 'https://gbssqlserver.database.windows.net',
                'database_name' : 'gbssqldw',
                'azure_sql_table_name' : 'salesv2'}), 
            code='qualifiedNameServiceKey', 
            type_name='azure_sql_table')

        expectedQnCall3 = call(
            body=AzureDatalakeGen2ResourceSet(**{
                'azure_storage_uri' : 'https://beamdatav2.dfs.core.windows.net',
                'filesystem_name' : 'sales',
                'resource_set_path' : '2019/8/20/0/0/sales-201982000.csv'}), 
            code='qualifiedNameServiceKey', 
            type_name='azure_datalake_gen2_resource_set')

        expectedQnCall4 = call(
            body=AzureDatalakeGen2Filesystem(**{
                'azure_storage_uri' : 'https://beamdatav2.dfs.core.windows.net',
                'filesystem_name' : 'salesv2'}),
            code='qualifiedNameServiceKey', 
            type_name='azure_datalake_gen2_filesystem')

        expectedQnCall6 = call(
            body=AdfCopyActivity(**{
                'datafactory_name' : 'walmart-gbs-adf',
                'pipeline_name' : 'DataCopyWithLineage',
                'activity_name' : 'Copy Data1'}), 
            code='qualifiedNameServiceKey', 
            type_name='adf_copy_activity')

        qnClientMock.get_qualified_name.assert_has_calls([
            expectedQnCall1, 
            expectedQnCall3, 
            expectedQnCall4, 
            expectedQnCall6])
  
        #endregion verify qualified name client calls

        #region verify json generator client calls

        inputs = [Inputs(guid=qnResponses[1].guid, type_name='azure_datalake_gen2_resource_set')]
        outputs = [Outputs(guid=qnResponses[2].guid, type_name='azure_datalake_gen2_filesystem')]

        process_attributes = [
            ProcessAttributes(**{
                'attr_name': 'StartTime',
                'attr_value': int(start_time2.timestamp()),
                'is_entityref': False
            }),
            ProcessAttributes(**{
                'attr_name': 'EndTime',
                'attr_value': int(end_time2.timestamp()),
                'is_entityref': False
            })
        ]

        expectedJG2 = Request(
                guid=qnResponses[3].guid,
                name='Copy Data1', 
                type_name='adf_copy_activity', 
                qualified_name='walmart-gbs-adf/DataCopyWithLineage/Copy Data1', 
                created_by='ADF', 
                process_attributes=process_attributes,
                inputs=inputs, 
                outputs=outputs)

        jsonGeneratorClientMock.create_lineage_data.assert_called_with(body=expectedJG2, code='jsonGeneratorServiceKey')

        #endregion verify json generator client calls

        #region verify metadata client calls

        expectedMD2 = {
            "entities": [{
                    "typeName": "adf_copy_activity",
                    "guid": str(qnResponses[3].guid),
                    "createdBy": "ADF",
                    "attributes": {
                        "inputs": [{
                                "guid": str(qnResponses[1].guid),
                                "typeName": "azure_datalake_gen2_resource_set"
                            }
                        ],
                        "outputs": [{
                                "guid": str(qnResponses[2].guid),
                                "typeName": "azure_datalake_gen2_filesystem"
                            }
                        ],
                        "qualifiedName": "walmart-gbs-adf/DataCopyWithLineage/Copy Data1",
                        "name": "Copy Data1",
                        "StartTime": int(start_time2.timestamp()),
                        "EndTime": int(end_time2.timestamp())
                    }
                }
            ]
        }

        metadataClientMock.entity_bulk_post_using_post.assert_called_with(expectedMD2)

        #endregion verify metadata client calls

        processor.sql.deleteRequests.assert_called_with([9, 10])

if __name__ == '__main__': 
    unittest.main() 