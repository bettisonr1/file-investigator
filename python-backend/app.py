from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from services.user_service import get_user, create_user, update_user
from services.item_service import get_all_items, create_item
from services.datastore_service import trigger_document_import_and_wait, create_datastore
from services.cloudstorage_service import generate_v4_upload_signed_url
from services.agentService import query_agent_by_session, get_session_info, clear_session, clear_all_sessions, list_active_sessions
from data.mongoClient import get_all_files, create_file, update_file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Health check endpoint
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Flask API Server',
        'status': 'running',
        'version': '1.0.0'
    }), 200

# GET endpoint - retrieve a user
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user_endpoint(user_id):
    try:
        user = get_user(user_id)
        if user:
            return jsonify({
                'success': True,
                'data': user
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# POST endpoint - create a new user
@app.route('/api/users', methods=['POST'])
def create_user_endpoint():
    try:
        data = request.get_json()
        
        if not data or 'name' not in data or 'email' not in data:
            return jsonify({
                'success': False,
                'error': 'Name and email are required'
            }), 400
        
        user = create_user(data['name'], data['email'])
        return jsonify({
            'success': True,
            'data': user,
            'message': 'User created successfully'
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# PUT endpoint - update a user
@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user_endpoint(user_id):
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        user = update_user(user_id, data)
        if user:
            return jsonify({
                'success': True,
                'data': user,
                'message': 'User updated successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Additional GET endpoint - list all items
@app.route('/api/items', methods=['GET'])
def get_items_endpoint():
    try:
        # Get optional query parameters
        limit = request.args.get('limit', default=10, type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        items = get_all_items(limit, offset)
        return jsonify({
            'success': True,
            'data': items,
            'count': len(items)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Additional POST endpoint - create an item
@app.route('/api/items', methods=['POST'])
def create_item_endpoint():
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({
                'success': False,
                'error': 'Item name is required'
            }), 400
        
        item = create_item(data['name'], data.get('description', ''))
        return jsonify({
            'success': True,
            'data': item,
            'message': 'Item created successfully'
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/files', methods=['GET'])
async def get_files_endpoint():
    try:
        files = await get_all_files()
        print(files)
        return jsonify({
            'success': True,
            'data': files['data']
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/files', methods=['POST'])
async def create_file_endpoint():
    try:
        data = request.get_json()
        
        if not data or 'file_name' not in data:
            return jsonify({
                'success': False,
                'error': 'file_name is required'
            }), 400
        
        file_name = data['file_name']
        datastore_id = data.get('datastore_id', None)
        
        result = await create_file(file_name, datastore_id)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/files/<file_id>', methods=['PUT'])
async def update_file_endpoint(file_id):
    try:
        data = request.get_json()
        
        indexed = data.get('indexed', True)
        
        result = await update_file(file_id, indexed)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Vertex AI Search endpoints

# POST endpoint - create datastore and search app
@app.route('/api/vertex/create-datastore', methods=['POST'])
async def create_datastore_endpoint():
    try:
        data = request.get_json()
        
        if not data or 'datastore_name' not in data:
            return jsonify({
                'success': False,
                'error': 'datastore_name is required'
            }), 400
        
        datastore_name = data['datastore_name']
        display_name = data.get('display_name', datastore_name)
        
        result = await create_datastore(datastore_name, display_name)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# POST endpoint - trigger document import
@app.route('/api/vertex/import-document', methods=['POST'])
def import_document_endpoint():
    try:
        data = request.get_json()
        
        if not data or 'file_name' not in data or 'datastore_name' not in data:
            return jsonify({
                'success': False,
                'error': 'file_name and datastore_name are required'
            }), 400
        
        file_name = data['file_name']
        datastore_name = data['datastore_name']
        reconciliation_mode = data.get('reconciliation_mode', 'INCREMENTAL')
        wait_for_completion = data.get('wait', True)
        
        if wait_for_completion:
            timeout = data.get('timeout', 600)
            result = trigger_document_import_and_wait(file_name, datastore_name, reconciliation_mode, timeout)

        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# GET endpoint - check import operation status
# TODO: Implement get_import_operation_status function in datastore_service
# @app.route('/api/vertex/import-status/<path:operation_name>', methods=['GET'])
# def get_import_status_endpoint(operation_name):
#     try:
#         result = get_import_operation_status(operation_name)
#         return jsonify(result), 200
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500

# GET endpoint - generate signed upload URL
@app.route('/api/storage/signed-url', methods=['GET'])
def get_upload_signed_url_endpoint():
    try:
        file_name = request.args.get('fileName') or None
        content_type = request.args.get('contentType') or 'application/octet-stream'
        
        result = generate_v4_upload_signed_url(file_name, content_type)
        return jsonify({
            'success': True,
            'signedUrl': result['url'],
            'fileName': result['fileName']
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Agent endpoints

# POST endpoint - query the search agent with session management
@app.route('/api/agent/query', methods=['POST'])
async def query_agent_endpoint():
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'query is required'
            }), 400
        
        query = data['query']
        session_id = data.get('session_id', 'default')  # Default session if not provided
        datastore_location = data.get('datastore_location')  # Optional
        
        # Query the agent using session management
        result = await query_agent_by_session(session_id, query, datastore_location)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# GET endpoint - get session info
@app.route('/api/agent/sessions/<session_id>', methods=['GET'])
def get_session_info_endpoint(session_id):
    try:
        result = get_session_info(session_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# GET endpoint - list all active sessions
@app.route('/api/agent/sessions', methods=['GET'])
def list_sessions_endpoint():
    try:
        result = list_active_sessions()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# DELETE endpoint - clear a session
@app.route('/api/agent/sessions/<session_id>', methods=['DELETE'])
def clear_session_endpoint(session_id):
    try:
        result = clear_session(session_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# DELETE endpoint - clear all sessions
@app.route('/api/agent/sessions', methods=['DELETE'])
def clear_all_sessions_endpoint():
    try:
        result = clear_all_sessions()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 5001
    print(f'Flask server starting at http://{host}:{port}/')
    print(f'Available endpoints:')
    print(f'  GET    http://{host}:{port}/api/users/<id>')
    print(f'  POST   http://{host}:{port}/api/users')
    print(f'  PUT    http://{host}:{port}/api/users/<id>')
    print(f'  GET    http://{host}:{port}/api/items')
    print(f'  POST   http://{host}:{port}/api/items')
    print(f'  GET    http://{host}:{port}/api/files')
    print(f'  POST   http://{host}:{port}/api/files')
    print(f'  PUT    http://{host}:{port}/api/files/<id>')
    print(f'  POST   http://{host}:{port}/api/vertex/create-datastore')
    print(f'  POST   http://{host}:{port}/api/vertex/import-document')
    print(f'  GET    http://{host}:{port}/api/storage/signed-url')
    print(f'  POST   http://{host}:{port}/api/agent/query')
    print(f'  GET    http://{host}:{port}/api/agent/sessions')
    print(f'  GET    http://{host}:{port}/api/agent/sessions/<id>')
    print(f'  DELETE http://{host}:{port}/api/agent/sessions/<id>')
    app.run(host=host, port=port, debug=True)

