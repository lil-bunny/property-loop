import os
import sys
from pathlib import Path
from google import genai

def analyze_property_image(image_path, query="What can you tell me about this property?"):
    """
    Analyze a property image using Google's Gemini API
    
    Args:
        image_path: Path to the image file
        query: Question to ask about the property image
    
    Returns:
        The analysis result from Gemini
    """
    # API key from main.py
    API_KEY = "AIzaSyB5TK4d119fIweLsOjaoVChBV0cEEnVPSg"
    
    # Initialize the client
    client = genai.Client(api_key=API_KEY)
    
    # Check if the file exists
    if not os.path.exists(image_path):
        print(f"Error: File {image_path} not found")
        return None
    
    try:
        # Upload the file to Gemini
        print(f"Uploading file: {image_path}")
        uploaded_file = client.files.upload(file=image_path)
        print(f"File uploaded with ID: {uploaded_file.id}")
        
        # Generate content with the image and query
        print(f"Analyzing image with query: {query}")
        result = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                uploaded_file,
                "\n\n",
                f"{query} Please describe any notable features, condition issues, and potential improvements.",
            ],
        )
        
        # Return the analysis result
        return result.text
    
    except Exception as e:
        print(f"Error during image analysis: {e}")
        return None

def main():
    # Check for command line arguments
    if len(sys.argv) < 2:
        print("Usage: python image_analysis.py <image_path> [query]")
        print("Example: python image_analysis.py house.jpg 'What issues do you see with this property?'")
        return
    
    # Get image path from command line
    image_path = sys.argv[1]
    
    # Get optional query from command line
    query = sys.argv[2] if len(sys.argv) > 2 else "What can you tell me about this property?"
    
    # Analyze the image
    analysis = analyze_property_image(image_path, query)
    
    if analysis:
        print("\nANALYSIS RESULT:")
        print("===============")
        print(analysis)
        print("===============")
    else:
        print("Failed to analyze the image.")

if __name__ == "__main__":
    main() 