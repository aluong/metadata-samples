import logging
import pyodbc
import os

class SqlWrapper:
    def __init__(self, config):
        self.config = config
        self._connection = None
        
    def getModifiedDatasets(self):

        selectStatement = """
            SELECT 
                r.clm_int_id as request_id,
				clm_varchar_datafactory_name as datafactory_name,
				clm_varchar_pipeline_name as pipeline_name,
				clm_varchar_activity_name as activity_name,
                clm_varchar_execution_start_time as execution_start_time,
                clm_varchar_execution_end_time as execution_end_time,
                d.clm_int_id as dataset_id,
                d.clm_varchar_dataset as dataset,
                d.clm_varchar_direction as direction,
                d.clm_varchar_type as type,
                d.clm_varchar_azure_resource as azure_resource
            FROM [dbo].[tbl_lineage_request] as r
            JOIN [dbo].[tbl_datasets] d on d.clm_int_lineage_request_id = r.clm_int_id
            """

        cursor = self._getConnection().cursor()

        cursor.execute(selectStatement)

        results = [dict(zip([column[0] for column in cursor.description], row))
                for row in cursor.fetchall()]

        logging.info('%d dataset records loaded from the SQL DB', len(results))

        return results
        
    def deleteRequests(self, requestIds):

        parameters = ', '.join('?' * len(requestIds))

        deleteStatement = """
            DELETE FROM [dbo].[tbl_lineage_request]
            WHERE clm_int_id in (%s)
            """ % parameters

        cursor = self._getConnection().cursor()
        cursor.execute(deleteStatement, requestIds)

        self._getConnection().commit()

        logging.info('%d lineage requests deleted from the SQL DB', len(requestIds))

    def _getConnection(self):
        if self._connection is None:
            logging.info('Connecting to SQL db %s at %s as %s' % 
                (self.config['sql_database'], self.config['sql_server'], self.config['sql_login']))

            self._connection = pyodbc.connect("Driver={ODBC Driver 17 for SQL Server};"
                                "Server=%s;Database=%s;uid=%s;pwd=%s;" % 
                                (
                                    self.config['sql_server'],
                                    self.config['sql_database'],
                                    self.config['sql_login'], 
                                    self.config['sql_password']
                                ))
        return self._connection
