import uvicorn
from dotenv import load_dotenv
from services.datastore_service import trigger_document_import_and_wait, create_datastore
from services.cloudstorage_service import generate_v4_upload_signed_url
from services.agentService import query_agent_by_session
from data.mongoClient import create_file_agent, get_all_file_agents, get_file_agent, update_single_file_agent
from fastapi import Body, FastAPI, Request, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
from typing import Optional

from models.file_agent import FileAgent, FileAgentUpdate

load_dotenv()

app = FastAPI(
    title="File Investigator API",
    description="API for managing files and querying documents with Vertex AI",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Pydantic Models
# ============================================================================

class HealthResponse(BaseModel):
    message: str
    status: str
    version: str

class ErrorResponse(BaseModel):
    success: bool = False
    error: str

class SuccessResponse(BaseModel):
    success: bool = True
    data: Optional[dict] = None
    message: Optional[str] = None

class CreateDatastoreRequest(BaseModel):
    datastore_name: str
    display_name: Optional[str] = None

class ImportDocumentRequest(BaseModel):
    file_name: str
    datastore_name: str
    reconciliation_mode: str = "INCREMENTAL"
    wait: bool = True
    timeout: int = 600

class CreateFileRequest(BaseModel):
    file_name: str
    datastore_id: Optional[str] = None

class UpdateFileRequest(BaseModel):
    indexed: bool = True

class AgentQueryRequest(BaseModel):
    query: str
    session_id: str = "default"
    datastore_location: Optional[str] = None

class UserCreateRequest(BaseModel):
    name: str
    email: str

class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

class ItemCreateRequest(BaseModel):
    name: str
    description: str = ""

# ============================================================================
# File Agent endpoints
# ============================================================================

@app.post("/api/file-agent", response_description="Create a new FileAgent", 
            status_code=status.HTTP_201_CREATED, response_model=FileAgent)
async def create_file_agent(request: Request, file_agent: FileAgent = Body(...)):
    try:
        file_agent = jsonable_encoder(file_agent)
        new_file_agent = await create_file_agent(file_agent)
        created_file_agent = await get_file_agent(new_file_agent.inserted_id)
        return created_file_agent
    except Exception as e:
        return {
            "success": False
        }

@app.get("/api/file-agent", response_description="List all FileAgents", response_model=List[FileAgent])
async def list_file_agents():
    file_agent_list = list(await get_all_file_agents())
    return file_agent_list

@app.put("/api/file-agent/{fileAgentId}", status_code=status.HTTP_200_OK)
async def update_file_agent(fileAgentId: str, file_agent: FileAgentUpdate = Body(...)):
    return await update_single_file_agent(fileAgentId, file_agent)

# ============================================================================
# Health Check Endpoint
# ============================================================================

@app.get("/", response_model=HealthResponse)
async def home():
    """Health check endpoint"""
    return {
        "message": "FastAPI Server",
        "status": "running",
        "version": "1.0.0"
    }

# ============================================================================
# Vertex AI Search Endpoints
# ============================================================================

@app.post("/api/vertex/create-datastore", status_code=201)
async def create_datastore_endpoint(datastore: CreateDatastoreRequest):
    """Create a Vertex AI datastore and search app"""
    try:
        display_name = datastore.display_name or datastore.datastore_name
        result = await create_datastore(datastore.datastore_name, display_name)
        
        if result['success']:
            return result
        raise HTTPException(status_code=500, detail=result.get('error', 'Failed to create datastore'))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/vertex/import-document")
async def import_document_endpoint(import_data: ImportDocumentRequest):
    """Trigger document import to Vertex AI datastore"""
    try:
        result = trigger_document_import_and_wait(
            import_data.file_name,
            import_data.datastore_name,
            import_data.reconciliation_mode,
            import_data.timeout
        )
        
        if result['success']:
            return result
        raise HTTPException(status_code=500, detail=result.get('error', 'Failed to import document'))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Storage Endpoints
# ============================================================================

@app.get("/api/storage/signed-url")
async def get_upload_signed_url_endpoint(
    fileName: Optional[str] = Query(None),
    contentType: str = Query("application/octet-stream")
):
    """Generate a signed upload URL for Google Cloud Storage"""
    try:
        result = generate_v4_upload_signed_url(fileName, contentType)
        return {
            "success": True,
            "signedUrl": result['url'],
            "fileName": result['fileName']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Agent Endpoints
# ============================================================================

@app.post("/api/agent/query")
async def query_agent_endpoint(query_data: AgentQueryRequest):
    """Query the search agent with session management"""
    try:
        result = await query_agent_by_session(
            query_data.session_id,
            query_data.query,
            query_data.datastore_location
        )
        
        if result['success']:
            return result
        raise HTTPException(status_code=500, detail=result.get('error', 'Query failed'))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Server Startup
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    host = "127.0.0.1"
    port = 5001
    
    print(f'FastAPI server starting at http://{host}:{port}/')
    print(f'📚 API Documentation: http://{host}:{port}/docs')
    print(f'📘 Alternative docs: http://{host}:{port}/redoc')
    print(f'\nAvailable endpoints:')
    print(f'  GET    http://{host}:{port}/')
    print(f'  POST   http://{host}:{port}/api/vertex/create-datastore')
    print(f'  POST   http://{host}:{port}/api/vertex/import-document')
    print(f'  GET    http://{host}:{port}/api/storage/signed-url')
    print(f'  POST   http://{host}:{port}/api/agent/query')
    
    uvicorn.run(app, host=host, port=port, reload=True)
