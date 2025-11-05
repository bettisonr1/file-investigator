"""
Vertex Search Agent - Creates an ADK LlmAgent with Vertex AI Search capabilities
"""
from google.adk.agents import LlmAgent
from google.adk.tools import VertexAiSearchTool
import os

AGENT_NAME_VSEARCH = "vertex_search_agent"
GEMINI_2_FLASH = "gemini-2.5-flash"


def create_vertex_search_agent(datastore_location):
    return LlmAgent(
    name=f"{AGENT_NAME_VSEARCH}",
    model=GEMINI_2_FLASH,
    tools=[VertexAiSearchTool(data_store_id=datastore_location)],
    instruction="""
    You are a helpful assistant that can search the Vertex AI Search datastore and draft an answer with citations.
    You will be given a query and you will need to search the datastore and draft an answer with citations.
    You will need to use the Vertex AI Search datastore to search for the answer.
    You will need to use the Vertex AI Search datastore to draft an answer with citations.
    You will need to use the Vertex AI Search datastore to search for the answer.
    """,
    description="Searches the Vertex AI Search datastore and drafts an answer with citations.",
)

