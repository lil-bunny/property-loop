import requests
import argparse
import os
import json

def chat_with_file_upload(api_url, image_path, text, session_id=None):
    """
    Send a chat request with a file upload using FormData
    
    Args:
        api_url: Base URL of the API
        image_path: Path to the image file
        text: The message text
        session_id: Optional session ID
    
    Returns:
        The API response
    """
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return None
    
    # Prepare form data
    form_data = {
        'text': text
    }
    
    # Add session ID if provided
    if session_id:
        form_data['session_id'] = session_id
    
    # Prepare files
    files = {
        'image': (os.path.basename(image_path), open(image_path, 'rb'), 'image/jpeg')
    }
    
    # Send the request
    print(f"Sending FormData request to {api_url}/chat/with-file")
    print(f"Image: {image_path}")
    print(f"Text: {text}")
    
    try:
        response = requests.post(
            f"{api_url}/chat/with-file",
            data=form_data,
            files=files
        )
        
        # Check if request was successful
        response.raise_for_status()
        
        # Close the file
        files['image'][1].close()
        
        # Return the response
        return response.json()
    
    except Exception as e:
        # Make sure to close the file
        files['image'][1].close()
        
        print(f"Error sending request: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
        return None

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test chat with file upload using FormData')
    parser.add_argument('--image', '-i', required=True, help='Path to the image file')
    parser.add_argument('--text', '-t', default='What can you tell me about this property?', 
                        help='Text message to send with the image')
    parser.add_argument('--api-url', '-a', default='http://localhost:8000', 
                        help='API URL (default: http://localhost:8000)')
    parser.add_argument('--session-id', '-s', help='Session ID (optional)')
    parser.add_argument('--output', '-o', help='Save response to file')
    
    args = parser.parse_args()
    
    # Send the request
    result = chat_with_file_upload(args.api_url, args.image, args.text, args.session_id)
    
    # Save to file if requested
    if args.output and result:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Response saved to {args.output}")
    
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