from flask import Flask, request, jsonify
import uvicorn
from flask_cors import CORS
from dotenv import load_dotenv
from services.user_service import get_user, create_user, update_user
from services.item_service import get_all_items, create_item
from services.datastore_service import trigger_document_import_and_wait, create_datastore
from services.cloudstorage_service import generate_v4_upload_signed_url
from services.agentService import query_agent_by_session, clear_session, clear_all_sessions, list_active_sessions
from data.mongoClient import create_file_agent, get_all_file_agents, get_all_files, get_file_agent, update_file, update_single_file_agent
from fastapi import APIRouter, Body, FastAPI, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

from models.file_agent import FileAgent, FileAgentUpdate

app = FastAPI()
router = APIRouter()

load_dotenv()

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



# if __name__ == "__main__":
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)