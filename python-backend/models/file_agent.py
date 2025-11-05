import uuid
import datetime
from typing import Optional
from pydantic import BaseModel, Field

class FileAgent(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    fileName: str = Field(alias="file_name")
    createdAt: str = Field(alias="created_at")
    updatedAt: str = Field(alias="updated_at")
    sessionId: str = Field(alias="session_id")
    datastoreId: str = Field(alias="datastore_id")
    indexed: bool = Field(...)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "fileName": "examplefile.pdf",
                "createdAt": "10-10-2025",
                "sessionId": "066de609-b04a-4b30-b46c-32537c7f1f6t",
                "datastoreId": "066de609-b04a-4b30-b46c-32537c7f1f6c"
            }
        }

class FileAgentUpdate(BaseModel):
    sessionId: Optional[str] = Field(alias="session_id")
    datastoreId: Optional[str] = Field(alias="datastore_id")
    indexed: Optional[bool] = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "sessionId": "066de609-b04a-4b30-b46c-32537c7f1f6t",
                "datastoreId": "066de609-b04a-4b30-b46c-32537c7f1f6c"
            }
        }