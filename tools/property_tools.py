from google import genai
from google.genai import types
import base64
import requests
from io import BytesIO
import re

class PropertyTools:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.0-flash"

    def issue_detection(self, image_url=None, context=None):
        """Function to handle property issue detection using Gemini API"""
        system_prompt = """You are a helpful, professional real estate assistant specializing in issue detection and troubleshooting. You receive property images and optional textual context from users who want help identifying visible problems in real estate properties and getting actionable advice.
🧠 Your Responsibilities:
Analyze uploaded images of real estate interiors or exteriors.
Identify visible property issues such as:
Water damage
Mold or mildew
Paint peeling
Cracks in walls/floors
Broken fixtures
Poor lighting
Rust or corrosion
Stains or structural wear
If text is provided, use it as additional context to improve issue detection.
Suggest practical next steps or fixes, such as:
Contacting a relevant professional (e.g., plumber, electrician, contractor)
Using specific treatments (e.g., anti-mold paint, waterproof coating)
Performing quick temporary solutions (e.g., applying sealant)
Ask smart follow-up questions to clarify ambiguous scenarios (e.g., "Is there any smell or dampness in that area?" or "Is this near a water source?")
🗣 Your Response Format:
Always respond in a clear, helpful tone. Use this format:

Identified Issue(s):
- Issue 1
- Issue 2 (if any)

Suggested Actions:
- Action 1
- Action 2

Follow-Up Question (if needed):
[Ask a relevant, clarifying question]
"""

        parts = []
        # Add text description if provided
        text_content = f"Property issue description: {context}" if context else "Property issue (no additional description provided)"
        parts.append(types.Part.from_text(text=text_content))
        
        # Handle image if URL is provided
        if image_url:
            try:
                # For remote images (URLs)
                if image_url.startswith('http'):
                    response = requests.get(image_url, stream=True)
                    response.raise_for_status()
                    image_bytes = response.content
                    image_part = types.Part.from_data(
                        data=image_bytes,
                        mime_type="image/jpeg"  # Adjust based on the image type if needed
                    )
                    parts.append(image_part)
                # For base64 encoded images
                elif image_url.startswith('data:image'):
                    # Extract the base64 part
                    base64_data = image_url.split(',')[1]
                    image_bytes = base64.b64decode(base64_data)
                    mime_type = image_url.split(';')[0].split(':')[1]
                    image_part = types.Part.from_data(
                        data=image_bytes,
                        mime_type=mime_type
                    )
                    parts.append(image_part)
            except Exception as e:
                # If image processing fails, add an error message
                parts.append(types.Part.from_text(text=f"Error processing image: {str(e)}. Proceeding with text-only analysis."))
        
        # Configure the generation parameters
        generate_content_config = types.GenerateContentConfig(
            temperature=0.3,
            system_instruction=[types.Part.from_text(text=system_prompt)]
        )
        
        # Make the API call
        response = self.client.models.generate_content(
            model=self.model,
            contents=[types.Content(role="user", parts=parts)],
            config=generate_content_config
        )
        
        return response.text

    def _extract_location_from_history(self, conversation_history):
        """Extract location information from conversation history"""
        # Common location patterns
        city_pattern = r'\b(?:in|from|at|is|am)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        india_cities = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", 
                       "Pune", "Ahmedabad", "Jaipur", "Lucknow", "Kanpur", "Nagpur"]
        us_cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
                    "San Antonio", "San Diego", "Dallas", "San Jose"]
        
        countries = ["India", "USA", "United States", "UK", "United Kingdom", "Canada", "Australia"]
        
        # Look through user messages in reverse order (most recent first)
        if conversation_history:
            for msg in reversed(conversation_history):
                if msg.role == "user":
                    content = ""
                    if msg.parts and hasattr(msg.parts[0], 'text'):
                        content = msg.parts[0].text.strip()
                    
                    # Check for direct mentions
                    for city in india_cities + us_cities:
                        if city.lower() in content.lower():
                            return city
                            
                    for country in countries:
                        if country.lower() in content.lower():
                            return country
                            
                    # Try to extract with regex
                    matches = re.findall(city_pattern, content, re.IGNORECASE)
                    if matches:
                        return matches[0]
        
        return None

    def tenancy_faq(self, prompt, location=None, conversation_history=None):
        """Function to handle tenancy FAQ queries using Gemini API"""
        
        # Try to extract location from history if not provided
        if not location and conversation_history:
            location = self._extract_location_from_history(conversation_history)
        
        system_prompt = """You are a knowledgeable and friendly Tenancy FAQ Assistant named Erica. You answer questions about rental laws and tenant rights.

Important:
1. If the user has already mentioned a location (city/country) in previous messages, use that information
2. Don't ask for location again if it's already been provided
3. Keep answers concise and practical
4. Provide location-specific guidance when possible
5. If truly no location is available, then ask for it politely
"""
        
        # Include extract of conversation with relevant location info
        location_context = ""
        if location:
            location_context = f"\n\nThe user has indicated they are from: {location}"
        
        user_prompt = f"""Question: {prompt}{location_context}"""
        
        generate_content_config = types.GenerateContentConfig(
            temperature=0.5,
            system_instruction=[types.Part.from_text(text=system_prompt)]
        )
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=[types.Content(role="user", parts=[types.Part.from_text(text=user_prompt)])],
            config=generate_content_config
        )
        return response.text 