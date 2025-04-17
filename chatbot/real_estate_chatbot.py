from google import genai
from google.genai import types
from tools.property_tools import PropertyTools
from config.chatbot_config import ChatbotConfig
import re

class RealEstateChatbot:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.0-flash"
        self.tools = PropertyTools(api_key)
        self.conversation_history = []
        self.config = ChatbotConfig()

    def _extract_image_url(self, text):
        """Extract image URL from text if present"""
        # Simple pattern to match URLs
        url_pattern = r'https?://\S+'
        urls = re.findall(url_pattern, text)
        
        # Filter for common image extensions
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        for url in urls:
            if any(url.lower().endswith(ext) for ext in image_extensions):
                # Return the URL with image extension
                return url
            
        # Check for data URLs
        if 'data:image' in text:
            data_url_pattern = r'data:image/[^;]+;base64,[a-zA-Z0-9+/]+=*'
            data_urls = re.findall(data_url_pattern, text)
            if data_urls:
                return data_urls[0]
                
        return None

    def get_response(self, user_input):
        """Process user input and return a response"""
        # Check if the input contains an image URL
        image_url = self._extract_image_url(user_input)
        
        # If image URL is present, directly trigger the issue detection tool
        if image_url:
            # Extract text without the URL for context
            context = re.sub(r'https?://\S+', '', user_input).strip()
            if not context:
                context = "Please analyze this property image."
                
            print("\nEric: I see you've shared an image. Let me analyze it for any property issues...")
            
            # Call the issue detection tool directly
            result = self.tools.issue_detection(
                image_url=image_url,
                context=context
            )
            
            # Update conversation history
            self.conversation_history.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=user_input)]
                )
            )
            
            self.conversation_history.append(
                types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=result)]
                )
            )
            
            return result
            
        # Normal text processing
        self.conversation_history.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_input)]
            )
        )

        generate_content_config = types.GenerateContentConfig(
            temperature=0.55,
            tools=self.config.get_tools(),
            response_mime_type="text/plain",
            system_instruction=[types.Part.from_text(text=self.config.get_system_instruction())]
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=self.conversation_history,
            config=generate_content_config
        )

        if response.function_calls:
            function_call = response.function_calls[0]
            tool_name = function_call.name
            args = function_call.args

            if tool_name == "issueDetectionTool":
                result = self.tools.issue_detection(
                    image_url=args.get("image_url"),
                    context=args.get("context")
                )
            elif tool_name == "tenancyFAQAgentTool":
                result = self.tools.tenancy_faq(
                    prompt=args.get("prompt"),
                    location=args.get("location"),
                    conversation_history=self.conversation_history
                )
            else:
                result = "I'm sorry, I couldn't process your request properly."

            self.conversation_history.append(
                types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=result)]
                )
            )
            return result
        else:
            self.conversation_history.append(
                types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=response.text)]
                )
            )
            return response.text

    def start_conversation(self):
        """Start the chatbot conversation"""
        print("Welcome! I'm Eric, your real estate assistant. How can I help you today?")
        print("Type 'quit' to exit the conversation.")
        print("You can also share an image URL to analyze property issues.")

        while True:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == 'quit':
                print("Goodbye! Have a great day!")
                break
            
            response = self.get_response(user_input)
            print(f"\nEric: {response}") 