# Flask API Server - Skeleton

A simple Flask REST API skeleton with example endpoints demonstrating GET, POST, and PUT operations.

## Structure

```
python-backend/
├── app.py                    # Main Flask application
├── services/                 # Service layer for business logic
│   ├── __init__.py
│   ├── user_service.py       # User operations
│   └── item_service.py       # Item operations
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

```bash
python app.py
```

The server will start at `http://127.0.0.1:5000/`

## API Endpoints

### Users

- **GET** `/api/users/<id>` - Get a specific user
  ```bash
  curl http://127.0.0.1:5000/api/users/1
  ```

- **POST** `/api/users` - Create a new user
  ```bash
  curl -X POST http://127.0.0.1:5000/api/users \
    -H "Content-Type: application/json" \
    -d '{"name": "John Doe", "email": "john@example.com"}'
  ```

- **PUT** `/api/users/<id>` - Update a user
  ```bash
  curl -X PUT http://127.0.0.1:5000/api/users/1 \
    -H "Content-Type: application/json" \
    -d '{"name": "Alice Updated", "email": "alice.new@example.com"}'
  ```

### Items

- **GET** `/api/items` - Get all items (with optional pagination)
  ```bash
  curl http://127.0.0.1:5000/api/items?limit=5&offset=0
  ```

- **POST** `/api/items` - Create a new item
  ```bash
  curl -X POST http://127.0.0.1:5000/api/items \
    -H "Content-Type: application/json" \
    -d '{"name": "Webcam", "description": "HD webcam"}'
  ```

### Vertex AI Search

- **POST** `/api/vertex/create-datastore-app` - Create a datastore and search app
  ```bash
  curl -X POST http://127.0.0.1:5000/api/vertex/create-datastore-app \
    -H "Content-Type: application/json" \
    -d '{"datastore_name": "my-datastore", "display_name": "My Search Datastore"}'
  ```

- **GET** `/api/vertex/datastores` - List all datastores
  ```bash
  curl http://127.0.0.1:5000/api/vertex/datastores
  ```

- **GET** `/api/vertex/datastores/<id>` - Get specific datastore info
  ```bash
  curl http://127.0.0.1:5000/api/vertex/datastores/my-datastore
  ```

- **POST** `/api/vertex/import-document` - Import a document from GCS to datastore
  ```bash
  curl -X POST http://127.0.0.1:5000/api/vertex/import-document \
    -H "Content-Type: application/json" \
    -d '{
      "gcs_path": "gs://my-bucket/document.pdf",
      "datastore_path": "projects/my-project/locations/global/collections/default_collection/dataStores/my-datastore/branches/default_branch",
      "reconciliation_mode": "INCREMENTAL",
      "wait": false
    }'
  ```

- **GET** `/api/vertex/import-status/<operation>` - Check import operation status
  ```bash
  curl http://127.0.0.1:5000/api/vertex/import-status/projects/.../operations/...
  ```

### Cloud Storage

- **GET** `/api/storage/signed-url` - Generate signed upload URL
  ```bash
  curl "http://127.0.0.1:5000/api/storage/signed-url?fileName=document.pdf&contentType=application/pdf"
  ```

### Agent

- **POST** `/api/agent/query` - Query the Vertex AI Search agent with session management
  ```bash
  curl -X POST http://127.0.0.1:5000/api/agent/query \
    -H "Content-Type: application/json" \
    -d '{
      "session_id": "user-123",
      "query": "What are the installation instructions?",
      "datastore_location": "projects/my-project/locations/global/collections/default_collection/dataStores/my-datastore"
    }'
  ```
  
  Notes:
  - `session_id` is optional. Defaults to 'default' if not provided.
  - `datastore_location` is optional. Uses environment variables if not provided.
  - Agents are cached per session for efficiency.

- **GET** `/api/agent/sessions` - List all active agent sessions
  ```bash
  curl http://127.0.0.1:5000/api/agent/sessions
  ```

- **GET** `/api/agent/sessions/<id>` - Get info about a specific session
  ```bash
  curl http://127.0.0.1:5000/api/agent/sessions/user-123
  ```

- **DELETE** `/api/agent/sessions/<id>` - Clear a specific session
  ```bash
  curl -X DELETE http://127.0.0.1:5000/api/agent/sessions/user-123
  ```

## Response Format

All endpoints return JSON responses with the following structure:

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional message"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message"
}
```

## Features

- ✅ RESTful API structure
- ✅ CORS enabled
- ✅ Service layer pattern
- ✅ Error handling
- ✅ Mock data for testing
- ✅ Query parameters support
- ✅ JSON request/response
- ✅ Proper HTTP status codes

## Next Steps

To extend this skeleton:

1. **Add Database**: Replace mock data with SQLAlchemy or another ORM
2. **Add Authentication**: Implement JWT or session-based auth
3. **Add Validation**: Use marshmallow or pydantic for request validation
4. **Add Testing**: Add pytest tests for endpoints and services
5. **Add Logging**: Implement proper logging
6. **Add Environment Variables**: Use python-dotenv for configuration
7. **Add More Endpoints**: Implement DELETE, PATCH, etc.

