import pymongo
from bson import json_util, ObjectId
import json

async def get_all_files():
    uri = 'mongodb+srv://admin:admin@cluster0.ifmh4lk.mongodb.net/?appName=Cluster0'
    client = pymongo.MongoClient(uri)
    try:
        result = client["vertex_document_search_db"]["files"].find()
        return {
            "success": True,
            "data": json.dumps(list(result), default=json_util.default)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

async def create_file(file_name, datastore_id = None):
    uri = 'mongodb+srv://admin:admin@cluster0.ifmh4lk.mongodb.net/?appName=Cluster0'
    client = pymongo.MongoClient(uri)
    
    try:
        client["vertex_document_search_db"]["files"].insert_one({
            "file_name": file_name,
            "datastore_id": datastore_id,
            "indexed": False
        })
        return {
            "success": True,
            "data": {
                "file_name": file_name,
                "datastore_id": datastore_id
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

async def update_file(file_id, indexed = True):
    uri = 'mongodb+srv://admin:admin@cluster0.ifmh4lk.mongodb.net/?appName=Cluster0'
    client = pymongo.MongoClient(uri)
    try:
        # Convert string file_id to ObjectId
        object_id = ObjectId(file_id)
        
        result = client["vertex_document_search_db"]["files"].update_one({
            "_id": object_id
        }, {
            "$set": {
                "indexed": indexed
            }
        })
        
        if result.matched_count == 0:
            return {
                "success": False,
                "error": "File not found"
            }
        
        return {
            "success": True,
            "data": {
                "file_id": file_id,
                "indexed": indexed
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

