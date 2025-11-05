from fastapi import HTTPException, status
import pymongo

uri = 'mongodb+srv://admin:admin@cluster0.ifmh4lk.mongodb.net/?appName=Cluster0'
client = pymongo.MongoClient(uri)

async def create_file_agent(file_agent):
    try:
        created_file_agent = client["vertex_document_search_db"]["file_agent"].insert_one(file_agent)
        return created_file_agent
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
    
async def get_file_agent(id):
    return client["vertex_document_search_db"]["file_agent"].find_one(
        {"_id": id}
    )

async def get_all_file_agents():
    return client["vertex_document_search_db"]["file_agent"].find(limit=100)

async def update_single_file_agent(id, file_agent):
    file_agent = {k: v for k, v in file_agent.dict().items() if v is not None}
    update_result = client["vertex_document_search_db"]["file_agent"].update_one(
        {"_id": id}, {"$set": file_agent}
    )
    if update_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {id} not found")

    if (
        existing_book := await get_file_agent(id)
    ) is not None:
        return existing_book

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {id} not found")
