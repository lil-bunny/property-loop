# API Usage Examples - Curl Commands

## JSON-based API with Base64 Image 

### Basic Chat (No Image)
```bash
curl -X POST "http://localhost:8002/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Tell me about common issues in older properties",
    "session_id": "test-session-123"
  }'
```

### Chat with Base64 Image
```bash
curl -X POST "http://localhost:8002/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "What can you tell me about this property?",
    "image_base64": "BASE64_ENCODED_IMAGE_HERE",
    "session_id": "test-session-123"
  }'
```

### Generate Base64 Image String
For Windows PowerShell:
```powershell
$imageBytes = [System.IO.File]::ReadAllBytes("C:\path\to\your\image.jpg")
$base64String = [System.Convert]::ToBase64String($imageBytes)
```

For Linux/Mac:
```bash
base64 -i /path/to/your/image.jpg | tr -d '\n'
```

## Form-based API with File Upload

### Chat with Form Data (No Image)
```bash
curl -X POST "http://localhost:8002/chat/form" \
  -F "text=What can you tell me about common issues in older properties?" \
  -F "session_id=test-session-123"
```

### Chat with Image Upload
```bash
curl -X POST "http://localhost:8002/chat/form" \
  -F "text=What can you tell me about this property?" \
  -F "image=@/path/to/your/image.jpg" \
  -F "session_id=test-session-123"
```

## Dedicated File Upload Endpoint

### Chat with File Upload
```bash
curl -X POST "http://localhost:8002/chat/with-file" \
  -F "text=What can you tell me about this property?" \
  -F "image=@/path/to/your/image.jpg" \
  -F "session_id=test-session-123"
```

## Session Management

### Clear Chat History
```bash
curl -X DELETE "http://localhost:8002/chat/test-session-123"
```

### Get Helper Information
```bash
curl "http://localhost:8002/image-upload-info"
```

## Windows PowerShell Examples

### Basic Chat
```powershell
Invoke-RestMethod -Uri "http://localhost:8002/chat" -Method Post -ContentType "application/json" -Body '{"text":"Tell me about common issues in older properties","session_id":"test-session-123"}'
```

### File Upload
```powershell
$filePath = "C:\path\to\your\image.jpg"
$form = @{
    text = "What can you tell me about this property?"
    session_id = "test-session-123"
    image = Get-Item -Path $filePath
}
Invoke-RestMethod -Uri "http://localhost:8002/chat/with-file" -Method Post -Form $form
```

# Testing Image API with cURL

Use these curl commands to test the simplified image analysis API running on port 8001.

## 1. Check if the API is running

```bash
curl http://localhost:8001/
```

Expected response:
```json
{"message":"Simple Image Analysis API is running"}
```

## 2. Test the basic file upload functionality

```bash
curl -X POST http://localhost:8001/test-upload \
  -F "image=@/path/to/your/image.jpg"
```

Replace `/path/to/your/image.jpg` with the actual path to an image file on your system.

Expected response:
```json
{
  "filename": "image.jpg",
  "content_type": "image/jpeg",
  "size": 123456
}
```

## 3. Analyze an image with a question

```bash
curl -X POST http://localhost:8001/analyze \
  -F "text=I have this crack in my wall, what should I do?" \
  -F "image=@/path/to/your/image.jpg"
```

Replace `/path/to/your/image.jpg` with the actual path to an image file on your system.

Expected response:
```json
{
  "analysis": "Detailed analysis of the property issue..."
}
```

## Troubleshooting

If you encounter issues:

1. Make sure the server is running:
   ```bash
   python simple_api.py
   ```
   
2. Check that the port 8001 is not in use by another application

3. Make sure your image file path is correct and accessible 