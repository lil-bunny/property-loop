from google.genai import types

class ChatbotConfig:
    @staticmethod
    def get_tools():
        """Returns the configured tools for the chatbot"""
        return [
            types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name="issueDetectionTool",
                        description="Detects visible property issues from uploaded images and optional text, and provides troubleshooting suggestions.",
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            required=["image_url"],
                            properties={
                                "image_url": types.Schema(
                                    type=types.Type.STRING,
                                    description="URL of the user-uploaded property image",
                                ),
                                "context": types.Schema(
                                    type=types.Type.STRING,
                                    description="Optional textual description or additional context from the user",
                                ),
                            },
                        ),
                    ),
                    types.FunctionDeclaration(
                        name="tenancyFAQAgentTool",
                        description="Answers frequently asked questions about tenancy laws, rental agreements, and tenant/landlord responsibilities.",
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            properties={
                                "prompt": types.Schema(
                                    type=types.Type.STRING,
                                    description="The user's tenancy-related question",
                                ),
                                "location": types.Schema(
                                    type=types.Type.STRING,
                                    description="The user's city or country to provide relevant legal guidance",
                                ),
                            },
                        ),
                    ),
                ]
            )
        ]

    @staticmethod
    def get_system_instruction():
        """Returns the system instruction for the chatbot"""
        return """You are a Real Estate Agent named Eric responsible for intelligently answering user queries and routing them to appropriate specialized tools when required.
        You have access to two tools:
        1. issueDetectionTool - for property issues
        2. tenancyFAQAgentTool - for tenancy-related questions
        
        Your job is to:
        1. Carefully read the user's input
        2. Identify whether it relates to a property issue or a tenancy question
        3. Call the appropriate tool with the correct parameters
        4. If neither tool is relevant, answer as a real estate agent
        """ 