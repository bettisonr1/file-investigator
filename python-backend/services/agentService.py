"""
Agent Service - Manages agent sessions and query routing
"""
from agents.vertex_search_agent import create_vertex_search_agent
from google.adk.sessions import DatabaseSessionService
from google.adk.runners import Runner
from google.genai import types
import os
from threading import Lock
from dotenv import load_dotenv

load_dotenv()

# Dictionary to store session_id -> agent mappings
agent_sessions = {}

# Lock for thread-safe access to the sessions dictionary
sessions_lock = Lock()

# Default datastore location from environment
DEFAULT_DATASTORE_LOCATION = None
DEFAULT_APP_NAME = "Query Agent"
DEFAULT_USER_ID = "user-123"
GCS_DATASTORE_PATH = os.getenv('GCS_DATASTORE_PATH')

session_service = DatabaseSessionService(db_url="sqlite:///./my_agent_data.db")
print(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))

async def get_session_event_history(session_id):
    session = session_service.get_session(app_name=DEFAULT_APP_NAME, user_id=DEFAULT_USER_ID, session_id=session_id)
    session_events = session.events;

    events_json = [];

    for event in session_events:
        events_json.append({
            "text": event.content.parts[0].text,
            "sender": event.content.role
        })
    
    print(f'Session events: {session_events}')
    return {
        'success': True,
        'session_id': session_id,
        'events': events_json
    }


async def query_agent_by_session(session_id, query, datastore_location):
    """
    Queries an agent for a given session ID.
    
    This method manages agent sessions by:
    1. Checking if an agent exists for the session_id
    2. Creating a new agent if it doesn't exist
    3. Storing the agent in the sessions dictionary
    4. Querying the agent and returning the response
    
    Args:
        session_id: Unique identifier for the session (e.g., user ID, conversation ID)
        query: The query string to send to the agent
        datastore_location: Optional datastore location. If not provided, uses environment variables.
                          Format: 'projects/{project}/locations/{location}/collections/{collection}/dataStores/{datastore}'
    
    Returns:
        dict: Contains the query response and session information
        {
            'success': bool,
            'session_id': str,
            'query': str,
            'response': str,
            'agent_created': bool,  # True if agent was created this call
            'error': str (if failed)
        }
        
    Example:
        result = query_agent_by_session('user-123', 'What is the installation process?')
        print(result['response'])
    """
    try:

        datastore_path = GCS_DATASTORE_PATH + "/" + datastore_location
        agent = None
        session = await session_service.get_session(app_name=DEFAULT_APP_NAME, user_id=DEFAULT_USER_ID, session_id=session_id)
        if session is None:
            session = await session_service.create_session(app_name=DEFAULT_APP_NAME, user_id=DEFAULT_USER_ID, session_id=session_id)
            agent = create_vertex_search_agent(datastore_path)
            agent_sessions[session.id] = agent
        else:
            agent = agent_sessions[session_id]
        
        # Query the agent
        runner = Runner(agent = agent, app_name = DEFAULT_APP_NAME, session_service = session_service)        
            
        content = types.Content(role="user", parts=[types.Part(text=query)])

        print(f'Runner passing query to agent: {query}')

        async for event in runner.run_async(
            user_id=DEFAULT_USER_ID,
            session_id=session.id,
            new_message=content,
        ):
            if event.is_final_response():
                print(f'Final response: {event.content.parts[0]}')
                final_response = event.content.parts[0].text

        print(f'Final response: {final_response}')
        
        return {
            'success': True,
            'session_id': session_id,
            'query': query,
            'response': str(final_response),

        }
        
    except Exception as e:
        print(f'Error querying agent for session {session_id}: {e}')
        return {
            'success': False,
            'session_id': session_id,
            'query': query,
            'error': str(e)
        }


def clear_session(session_id):
    """
    Clears an agent session from the dictionary.
    
    Args:
        session_id: The session ID to clear
    
    Returns:
        dict: Result of the operation
    """
    with sessions_lock:
        if session_id in agent_sessions:
            del agent_sessions[session_id]
            print(f'Session cleared: {session_id}')
            return {
                'success': True,
                'message': f'Session {session_id} cleared successfully'
            }
        else:
            return {
                'success': False,
                'error': 'Session not found'
            }


def clear_all_sessions():
    """
    Clears all agent sessions.
    
    Returns:
        dict: Result of the operation
    """
    with sessions_lock:
        count = len(agent_sessions)
        agent_sessions.clear()
        print(f'All sessions cleared ({count} sessions)')
        return {
            'success': True,
            'message': f'Cleared {count} sessions',
            'count': count
        }


def list_active_sessions():
    """
    Lists all active session IDs.
    
    Returns:
        dict: List of active sessions with their info
    """
    with sessions_lock:
        sessions = []
        for session_id, session_data in agent_sessions.items():
            sessions.append({
                'session_id': session_id,
                'query_count': session_data['query_count'],
                'datastore_location': session_data['datastore_location']
            })
        
        return {
            'success': True,
            'sessions': sessions,
            'count': len(sessions)
        }

