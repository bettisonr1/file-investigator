"""
Datastore service - handles datastore creation and document import operations for Vertex AI Search datastores
"""
from google.cloud import discoveryengine_v1 as discoveryengine
import os

# Configuration from environment variables
PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT', 'infra-bedrock-415017')
LOCATION = os.getenv('DISCOVERY_ENGINE_LOCATION', 'global')
COLLECTION_ID = os.getenv('DISCOVERY_ENGINE_COLLECTION_ID', 'default_collection')
GCS_BUCKET_PATH = os.getenv('GCS_BUCKET_PATH', 'gs://query_bucket_for_manuals_rob/')
GCS_PROJECT = os.getenv('GCS_PROJECT', 'infra-bedrock-415017')
DATASTORE_PATH = f'projects/{GCS_PROJECT}/locations/global/collections/default_collection/dataStores/***datastore_name***/branches/default_branch'

# Configure API endpoint based on location
if LOCATION == 'global':
    API_ENDPOINT = 'discoveryengine.googleapis.com'
else:
    API_ENDPOINT = f'{LOCATION}-discoveryengine.googleapis.com'


def trigger_document_import_and_wait(file_name, datastore_name, reconciliation_mode='INCREMENTAL', timeout=600):
    """
    Triggers the import of a document and waits for it to complete.
    
    Args:
        gcs_path: The GCS URI of the document
        datastore_path: The full resource name of the datastore branch
        reconciliation_mode: 'INCREMENTAL' or 'FULL'
        timeout: Maximum seconds to wait for completion (default: 600 = 10 minutes)
    
    Returns:
        dict: Contains success status, operation details, and import results
    """
    try:
        client = discoveryengine.DocumentServiceClient(
            client_options={'api_endpoint': API_ENDPOINT}
        )

        gcs_path = GCS_BUCKET_PATH + file_name
        datastore_path = DATASTORE_PATH.replace('***datastore_name***', datastore_name)
        
        if not gcs_path.startswith('gs://'):
            raise ValueError(f'Invalid GCS path: {gcs_path}. Must start with gs://')
        
        mode_map = {
            'INCREMENTAL': discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
            'FULL': discoveryengine.ImportDocumentsRequest.ReconciliationMode.FULL
        }
        reconciliation_enum = mode_map.get(reconciliation_mode.upper(), 
                                           discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL)
        
        request = discoveryengine.ImportDocumentsRequest(
            parent=datastore_path,
            gcs_source=discoveryengine.GcsSource(
                input_uris=[gcs_path],
                data_schema='content'
            ),
            reconciliation_mode=reconciliation_enum
        )
        
        print(f'Importing documents from GCS: {gcs_path}')
        print(f'Into datastore: {datastore_path}')
        
        operation = client.import_documents(request=request)
        operation_name = operation.operation.name
        
        print(f'Import operation started: {operation_name}')
        print(f'Waiting for operation to complete (timeout: {timeout}s)...')
        
        # Wait for the operation to complete
        response = operation.result(timeout=timeout)
        
        print(f'Import completed successfully')
        
        return {
            'success': True,
            'operationName': operation_name,
            'gcsPath': gcs_path,
            'datastorePath': datastore_path,
            'response': str(response),
            'message': 'Import completed successfully'
        }
        
    except Exception as e:
        print(f'Error importing documents: {e}')
        return {
            'success': False,
            'error': str(e),
            'gcsPath': gcs_path,
            'datastorePath': datastore_path
        }

async def create_datastore(datastore_id, display_name=None):
    """
    Creates a Vertex AI Search datastore.
    
    Args:
        datastore_id: The ID for the datastore (must be unique)
        display_name: Optional display name for the datastore
        
    Returns:
        dict: Contains success status and datastore information
    """
    try:
        # Create the DataStore service client
        client = discoveryengine.DataStoreServiceClient(
            client_options={'api_endpoint': API_ENDPOINT}
        )
        
        # Construct the parent path
        parent = f'projects/{PROJECT_ID}/locations/{LOCATION}/collections/{COLLECTION_ID}'
        
        # Configure the datastore
        datastore = discoveryengine.DataStore(
            display_name=display_name or datastore_id,
            industry_vertical=discoveryengine.IndustryVertical.GENERIC,
            # Content config for unstructured data (PDFs, docs, etc.)
            content_config=discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED,
            # Solution types - use SOLUTION_TYPE_SEARCH for search functionality
            solution_types=[discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH]
        )
        
        # Create the request
        request = discoveryengine.CreateDataStoreRequest(
            parent=parent,
            data_store=datastore,
            data_store_id=datastore_id,
            # Create default schema
            create_advanced_site_search=False
        )
        
        print(f'Creating datastore at: {parent}')
        print(f'Datastore ID: {datastore_id}')
        
        # Execute the request (this is a long-running operation)
        operation_result = client.create_data_store(request=request)
        
        # Wait for the operation to complete
        print('Waiting for datastore creation to complete...')
        response = operation_result.result(timeout=300)  # 5 minute timeout
        
        datastore_name = response.name
        
        return {
            'success': True,
            'datastore_id': datastore_id,
            'datastore_name': datastore_name,
            'display_name': response.display_name,
            'content_config': str(response.content_config),
            'solution_types': [str(st) for st in response.solution_types]
        }
        
    except Exception as e:
        print(f'Error creating datastore: {e}')
        return {
            'success': False,
            'error': str(e)
        }
