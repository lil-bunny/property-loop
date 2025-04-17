from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Union
import uuid
import os
import tempfile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import base64

from chatbot.real_estate_chatbot import RealEstateChatbot
from google.genai import types
from google import genai

# Create the FastAPI app
app = FastAPI(title="Real Estate Chatbot API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# API key for Gemini
API_KEY = "AIzaSyB5TK4d119fIweLsOjaoVChBV0cEEnVPSg"

# Initialize Google Generative AI client
genai_client = genai.Client(api_key=API_KEY)

# Initialize the chatbot
chatbot = RealEstateChatbot(API_KEY)

# Store for conversation histories (in-memory for MVP)
# Format: {session_id: conversation_history}
conversation_histories = {}

class Message(BaseModel):
    text: str
    session_id: Optional[str] = None
    conversation_history: Optional[List[Dict]] = None
    image_base64: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    session_id: str
    conversation_history: List[Dict]

@app.get("/")
async def root():
    return {"message": "Real Estate Chatbot API is running"}

# JSON-based chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat_json(message: Message):
    # Get or create session ID
    session_id = message.session_id or str(uuid.uuid4())
    
    # Initialize conversation history from the request or from stored history
    if message.conversation_history:
        # Convert the provided history to the format expected by the chatbot
        conversation_history = []
        for msg in message.conversation_history:
            role = msg.get("role")
            text = msg.get("text")
            if role and text:
                conversation_history.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=text)]
                    )
                )
    elif session_id in conversation_histories:
        # Retrieve existing history
        conversation_history = conversation_histories[session_id]
    else:
        # Start a new conversation
        conversation_history = []
    
    # Use the chatbot instance with the conversation history
    chatbot.conversation_history = conversation_history
    
    reply = ""
    
    # Process the image if provided
    if message.image_base64:
        temp_file = None
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp:
                temp_file = temp.name
                # Decode base64 image and write to file
                image_data = base64.b64decode(message.image_base64)
                temp.write(image_data)
            
            # Upload the image to Google Generative AI
            uploaded_file = genai_client.files.upload(file=temp_file)
            
            # Generate content using the uploaded file and text
            result = genai_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    uploaded_file,
                    "\n\n",
                    f"This is a property issue. {message.text} Analyze the image and tell me: What are the visible property issues? How severe are they? What actions should I take? Keep your response concise and actionable.",
                ],
            )
            
            reply = result.text
            
            # Update conversation history
            chatbot.conversation_history.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=f"{message.text} [Image attached]")]
                )
            )
            
            # Add model response to conversation history
            chatbot.conversation_history.append(
                types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=reply)]
                )
            )
            
        finally:
            # Clean up the temporary file
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)
    else:
        # Regular text processing
        reply = chatbot.get_response(message.text)
    
    # Update the stored conversation history
    conversation_histories[session_id] = chatbot.conversation_history
    
    # Convert the entire conversation history to a simple format for the response
    history_for_response = []
    for content in chatbot.conversation_history:
        if content.parts and hasattr(content.parts[0], 'text'):
            history_for_response.append({
                "role": content.role,
                "text": content.parts[0].text
            })
    
    return ChatResponse(
        reply=reply,
        session_id=session_id,
        conversation_history=history_for_response
    )

# Form-based chat endpoint with image upload support
@app.post("/chat/form", response_model=ChatResponse)
async def chat_form(
    text: str = Form(...),
    image: Optional[UploadFile] = File(None),
    session_id: Optional[str] = Form(None)
):
    # Get or create session ID
    session_id = session_id or str(uuid.uuid4())
    
    # Get conversation history
    if session_id in conversation_histories:
        conversation_history = conversation_histories[session_id]
    else:
        conversation_history = []
    
    # Set the conversation history
    chatbot.conversation_history = conversation_history
    
    reply = ""
    
    # Process the uploaded image if present
    if image:
        temp_file = None
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp:
                temp_file = temp.name
                # Read and write the contents of the uploaded file
                contents = await image.read()
                temp.write(contents)
            
            # Upload the image to Google Generative AI
            uploaded_file = genai_client.files.upload(file=temp_file)
            
            # Generate content using the uploaded file and text
            result = genai_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    uploaded_file,
                    "\n\n",
                    f"This is a property issue. {text} Analyze the image and tell me: What are the visible property issues? How severe are they? What actions should I take? Keep your response concise and actionable.",
                ],
            )
            
            reply = result.text
            
            # Update conversation history
            chatbot.conversation_history.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=f"{text} [Image attached]")]
                )
            )
            
            # Update conversation history with the model's response
            chatbot.conversation_history.append(
                types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=reply)]
                )
            )
            
        finally:
            # Clean up the temporary file
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)
    else:
        # Regular text processing
        reply = chatbot.get_response(text)
    
    # Update the stored conversation history
    conversation_histories[session_id] = chatbot.conversation_history
    
    # Convert the entire conversation history to a simple format for the response
    history_for_response = []
    for content in chatbot.conversation_history:
        if content.parts and hasattr(content.parts[0], 'text'):
            history_for_response.append({
                "role": content.role,
                "text": content.parts[0].text
            })
    
    return ChatResponse(
        reply=reply,
        session_id=session_id,
        conversation_history=history_for_response
    )

@app.post("/chat/with-file", response_model=ChatResponse)
async def chat_with_file(
    text: str = Form(...),
    image: Optional[UploadFile] = File(None),
    session_id: Optional[str] = Form(None)
):
    """
    Chat endpoint that accepts a file upload using FormData
    Similar to the /chat endpoint but uses multipart/form-data
    """
    # Get or create session ID
    session_id = session_id or str(uuid.uuid4())
    
    # Initialize conversation history
    if session_id in conversation_histories:
        # Retrieve existing history
        conversation_history = conversation_histories[session_id]
    else:
        # Start a new conversation
        conversation_history = []
    
    # Use the chatbot instance with the conversation history
    chatbot.conversation_history = conversation_history
    
    reply = ""
    
    # Process the uploaded image if present
    if image:
        temp_file = None
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp:
                temp_file = temp.name
                # Read and write the contents of the uploaded file
                contents = await image.read()
                temp.write(contents)
            
            # Upload the image to Google Generative AI
            uploaded_file = genai_client.files.upload(file=temp_file)
            
            # Generate content using the uploaded file and text
            result = genai_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    uploaded_file,
                    "\n\n",
                    f"This is a property issue. {text} Analyze the image and tell me: What are the visible property issues? How severe are they? What actions should I take? Keep your response concise and actionable.",
                ],
            )
            
            reply = result.text
            
            # Update conversation history
            chatbot.conversation_history.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=f"{text} [Image attached]")]
                )
            )
            
            # Add model response to conversation history
            chatbot.conversation_history.append(
                types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=reply)]
                )
            )
            
        finally:
            # Clean up the temporary file
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)
    else:
        # Regular text processing
        reply = chatbot.get_response(text)
    
    # Update the stored conversation history
    conversation_histories[session_id] = chatbot.conversation_history
    
    # Convert the entire conversation history to a simple format for the response
    history_for_response = []
    for content in chatbot.conversation_history:
        if content.parts and hasattr(content.parts[0], 'text'):
            history_for_response.append({
                "role": content.role,
                "text": content.parts[0].text
            })
    
    return ChatResponse(
        reply=reply,
        session_id=session_id,
        conversation_history=history_for_response
    )

@app.delete("/chat/{session_id}")
async def clear_conversation(session_id: str):
    if session_id in conversation_histories:
        del conversation_histories[session_id]
        return {"status": "success", "message": f"Conversation {session_id} cleared"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

# Add a simple test endpoint to verify image upload functionality
@app.post("/test-upload")
async def test_upload(image: UploadFile = File(...)):
    return {
        "filename": image.filename, 
        "content_type": image.content_type,
        "size": len(await image.read())
    }

@app.post("/chat-with-image")
async def chat_with_image(
    message: str = Form(...),
    image: Optional[UploadFile] = File(None)
):
    # Process the text message and image
    response = f"Received your message: {message}"
    
    if image:
        # Read and process the image
        image_content = await image.read()
        # Save the image to a file (optional)
        with open(f"uploaded_{image.filename}", "wb") as f:
            f.write(image_content)
        
        response += f" and image: {image.filename}"
    
    return {
        "response": response,
        "received_message": message,
        "image_received": image is not None
    }

@app.post("/analyze-image")
async def analyze_image(image: UploadFile = File(...)):
    # Read and process the image
    image_content = await image.read()
    
    # Save the image to a file (optional)
    with open(f"analysis_{image.filename}", "wb") as f:
        f.write(image_content)
    
    # Simulate analysis response
    analysis_result = {
        "property_type": "Residential",
        "estimated_value": "$450,000",
        "bedrooms": 3,
        "bathrooms": 2,
        "square_feet": 1800,
        "features": ["Large backyard", "Updated kitchen", "Garage"]
    }
    
    return {
        "analysis": analysis_result,
        "image_name": image.filename
    }

@app.get("/image-upload-info")
async def image_upload_info():
    """Helper endpoint to explain how to use the image upload feature"""
    return {
        "message": "To upload an image with your chat message, include a base64-encoded image in the 'image_base64' field.",
        "example_request": {
            "text": "What can you tell me about this property?",
            "image_base64": "base64_encoded_image_string",
            "session_id": "optional_session_id"
        },
        "how_to_encode": "You can encode an image to base64 in JavaScript with: btoa(binaryString) or in Python with: import base64; base64.b64encode(image_bytes).decode('utf-8')"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run"""
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    # Get port from environment variable for cloud deployment compatibility
    # Cloud Run sets PORT=8080 by default
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting server on port {port}")
    # Use 0.0.0.0 to listen on all interfaces
    uvicorn.run(app, host="0.0.0.0", port=port) 