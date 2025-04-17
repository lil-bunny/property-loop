# Real Estate Property Chatbot

A FastAPI-based chatbot API for real estate property analysis, using Google's Gemini AI.

## Features

- Text-based chat for real estate questions
- Image upload and analysis of property images 
- Multiple API endpoints for different use cases
- Session-based conversation history

## Core Components

### API Server (`api_server.py`)

The main FastAPI server with the following endpoints:

- `/chat` - JSON-based chat with optional base64-encoded image
- `/chat/form` - Form-based chat with file upload support
- `/chat/with-file` - Dedicated endpoint for file uploads using FormData

### Chatbot Implementation

- `chatbot/real_estate_chatbot.py` - Core chatbot logic using Gemini API
- `config/chatbot_config.py` - Configuration options
- `tools/property_tools.py` - Helper tools for property analysis

### Utility Scripts

- `image_analysis.py` - Standalone script for image analysis using Gemini API
- `test_chat_with_image.py` - Test client for the JSON chat endpoint with base64 image
- `test_formdata_upload.py` - Test client for the FormData upload endpoint

## Getting Started

### Prerequisites

```
pip install -r requirements.txt
```

Required Python packages:
- fastapi
- uvicorn
- python-multipart
- google-generativeai
- requests
- python-magic

### Running the API Server

```
python api_server.py
```

The server will start on port 8002 (http://localhost:8002).

## API Usage Examples

### JSON Endpoint with Base64 Image

```bash
curl -X POST "http://localhost:8002/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "What can you tell me about this property?",
    "image_base64": "BASE64_ENCODED_IMAGE",
    "session_id": "optional-session-id"
  }'
```

### FormData Endpoint with File Upload

```bash
curl -X POST "http://localhost:8002/chat/with-file" \
  -F "text=What can you tell me about this property?" \
  -F "image=@path/to/property.jpg" \
  -F "session_id=optional-session-id"
```

### Python Client Example

```python
import requests

# FormData upload
files = {'image': open('property.jpg', 'rb')}
data = {'text': 'Analyze this property', 'session_id': 'my-session'}
response = requests.post('http://localhost:8002/chat/with-file', files=files, data=data)
print(response.json())
```

## Testing

Use the provided test scripts:

```
python test_formdata_upload.py --image property.jpg --text "What issues do you see?" --api-url http://localhost:8002
```

```
python test_chat_with_image.py --image property.jpg --text "Analyze this property" --api-url http://localhost:8002
```

```
python image_analysis.py property.jpg "What issues do you see with this property?"
```

## License

MIT 