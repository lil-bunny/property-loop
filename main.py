import os
from chatbot.real_estate_chatbot import RealEstateChatbot

def main():
    # Get API key from environment variable
    api_key = "AIzaSyB5TK4d119fIweLsOjaoVChBV0cEEnVPSg"
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        print("Please set it by running: export GEMINI_API_KEY='your_api_key' (Linux/Mac)")
        print("or: set GEMINI_API_KEY=your_api_key (Windows)")
        return

    # Create and start the chatbot
    chatbot = RealEstateChatbot(api_key)
    chatbot.start_conversation()

if __name__ == "__main__":
    main() 