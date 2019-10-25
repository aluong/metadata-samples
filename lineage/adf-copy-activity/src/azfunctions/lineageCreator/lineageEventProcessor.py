import uuid
import logging
import json

from .qualified_name_client.generated.swagger.qualified_name_client import QualifiedNameClient
from .json_generator_client.generated.swagger.json_generator_client import JsonGeneratorClient

from .restFactory import RestFactory
from .sqlWrapper import SqlWrapper
from .qnRequestBuilder import buildDatasetQNRequest

from .qualified_name_client.generated.swagger.models.adf_copy_activity_py3 import AdfCopyActivity
from .json_generator_client.generated.swagger.models import Request, Response, Inputs, Outputs, ProcessAttributes

class LineageEventProcessor:
    def __init__(self, config):
        self.config = config
        self.restFactory = RestFactory(self.config)
        self.sql = SqlWrapper(config)

    def scanEvents(self):
        datasets = self.sql.getModifiedDatasets()

        lineageRequests = self._buildLineageRequests(datasets)

        self._reportActivities(lineageRequests)

        self._deleteRequests(lineageRequests)

    def _buildLineageRequests(self, datasets):
        lineageRequests = {}

        qnClient = self.restFactory.getQnClient()

        for dataset in datasets:
            requestId = dataset["request_id"]

            if requestId not in lineageRequests:
                lineageRequests[requestId] = { 
                    'datafactory_name' : dataset['datafactory_name'],
                    'pipeline_name' : dataset['pipeline_name'],
                    'activity_name' : dataset['activity_name'],
                    'execution_start_time' :dataset['execution_start_time'],
                    'execution_end_time' :dataset['execution_end_time'],
                    'sources' : [], 
                    'destinations' : [], 
                    'valid': False 
                }
            elif not lineageRequests[requestId]['valid']:
                continue

            if dataset['direction'].lower() == "source":
                lineageRequests[requestId]['sources'] += [dataset]
            else:
                lineageRequests[requestId]['destinations'] += [dataset]
            
            dsInfo = buildDatasetQNRequest(dataset)

            if dsInfo is not None:
                try:
                    qn = qnClient.get_qualified_name(
                        type_name=dataset['type'], 
                        body=dsInfo, 
                        code=self.config['qualifiedNameServiceKey'])
                except Exception as e:
                    logging.error('Error querying qualified name for request %s: %s' % (requestId, e))
                    continue
                
                dataset["qualified_name"] = qn.qualified_name

                if qn.is_exists:
                    dataset["guid"] = qn.guid
                    lineageRequests[requestId]['valid'] = True
                else:
                    logging.error('Type "%s" does not exist in the Qualified Service' % dataset['type'])

        for lineageRequest in lineageRequests.values():
            if not lineageRequest['valid']: 
                continue

            activityInfo = AdfCopyActivity(**{
                'datafactory_name' : lineageRequest['datafactory_name'],
                'pipeline_name' : lineageRequest['pipeline_name'],
                'activity_name' : lineageRequest['activity_name']
            })

            qn = qnClient.get_qualified_name(
                type_name='adf_copy_activity', 
                body=activityInfo, 
                code=self.config['qualifiedNameServiceKey'])

            if qn.is_exists:
                lineageRequest['guid'] = qn.guid
            else:
                logging.info('adf_copy_activity does not exist in the Qualified Service')
                lineageRequest['guid'] = -100

            lineageRequest['qualified_name'] = qn.qualified_name

        return lineageRequests

    def _reportActivities(self, lineageRequests):
        for lineageRequest in lineageRequests.values():
            if not lineageRequest['valid']: 
                continue 

            try:
                self._reportActivity(lineageRequest)
            except Exception as e:
                logging.error('Error posting lineage "%s": %s' % (lineageRequest['qualified_name'], e))

        logging.info('%d lineage requests processed', len(lineageRequests))

    def _reportActivity(self, lineageRequest):
        jsonClient = self.restFactory.getJsonGeneratorClient()
        process_attributes = [
            ProcessAttributes(**{
                'attr_name': 'StartTime',
                'attr_value': int(lineageRequest['execution_start_time'].timestamp()),
                'is_entityref': False
            }),
            ProcessAttributes(**{
                'attr_name': 'EndTime',
                'attr_value': int(lineageRequest['execution_end_time'].timestamp()),
                'is_entityref': False
            })
        ]

        inputs = [Inputs(guid=s['guid'], type_name=s['type']) for s in lineageRequest['sources']]
        outputs = [Outputs(guid=s['guid'], type_name=s['type']) for s in lineageRequest['destinations']]

        request = Request(
            guid=lineageRequest['guid'],
            name=lineageRequest['activity_name'], 
            type_name='adf_copy_activity', 
            qualified_name=lineageRequest['qualified_name'], 
            created_by='ADF', 
            process_attributes=process_attributes,
            inputs=inputs, 
            outputs=outputs)

        response = jsonClient.create_lineage_data(body=request, code=self.config['jsonGeneratorServiceKey'])

        metadataRequest = response.serialize()
        metadataRequest['entities'][0]['attributes']['StartTime'] = int(metadataRequest['entities'][0]['attributes']['StartTime'])
        metadataRequest['entities'][0]['attributes']['EndTime'] = int(metadataRequest['entities'][0]['attributes']['EndTime'])

        metadataRequestLog = json.dumps(metadataRequest)
        logging.info('Sending "%s" request to metadata wrapper' % metadataRequestLog)

        metadataClient = self.restFactory.getMetadataClient()

        response = metadataClient.entity_bulk_post_using_post(metadataRequest)

    def _deleteRequests(self, lineageRequests):
        ids = [id for id in lineageRequests.keys()]
        self.sql.deleteRequests(ids)
