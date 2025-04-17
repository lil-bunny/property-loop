import requests
import base64
import json
import argparse
import os

def encode_image_to_base64(image_path):
    """Encode an image file to base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def chat_with_image(api_url, image_path, text, session_id=None):
    """Send a chat request with an image to the API"""
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return None
    
    # Encode the image
    print(f"Encoding image: {image_path}")
    image_base64 = encode_image_to_base64(image_path)
    
    # Prepare the request data
    data = {
        "text": text,
        "image_base64": image_base64
    }
    
    # Add session_id if provided
    if session_id:
        data["session_id"] = session_id
    
    # Send the request
    print(f"Sending request to {api_url}/chat")
    try:
        response = requests.post(
            f"{api_url}/chat",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        # Check if request was successful
        response.raise_for_status()
        
        # Return the response
        return response.json()
    
    except Exception as e:
        print(f"Error sending request: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
        return None

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test chat with image upload')
    parser.add_argument('--image', '-i', required=True, help='Path to the image file')
    parser.add_argument('--text', '-t', default='What can you tell me about this property?', 
                        help='Text message to send with the image')
    parser.add_argument('--api-url', '-a', default='http://localhost:8000', 
                        help='API URL (default: http://localhost:8000)')
    parser.add_argument('--session-id', '-s', help='Session ID (optional)')
    
    args = parser.parse_args()
    
    # Send the request
    result = chat_with_image(args.api_url, args.image, args.text, args.session_id)
    
    # Print the result
    if result:
        print("\nCHAT RESPONSE:")
        print("==============")
        print(f"Reply: {result.get('reply')}")
        print(f"Session ID: {result.get('session_id')}")
        print("\nConversation History:")
        for message in result.get('conversation_history', []):
            role = message.get('role', '').upper()
            text = message.get('text', '')
            print(f"{role}: {text}")

if __name__ == "__main__":
    main() 