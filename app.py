import requests
import json

# Configuration
API_KEY = "AIzaSyB5TK4d119fIweLsOjaoVChBV0cEEnVPSg"  # Replace with your actual API key
MODEL_ID = "gemini-2.0-flash"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ID}:generateContent?key={API_KEY}"

# Supervisor Agent Prompt and Tool Definitions
SUPERVISOR_PROMPT = """
You are a Supervisor Agent responsible for intelligently routing user queries to the appropriate specialized agent tool. 
You do not answer directly—instead, you respond with a JSON object indicating which tool to call and with what parameters.

Tools:
1. issueDetectionTool: for visible property issues (accepts optional image_url and/or context).
2. tenancyFAQAgentTool: for tenancy questions (accepts question and optional location).
3. initialGreetingTool: greets or clarifies when input is too vague.

Always return a JSON list with one element:
[{"tool_name": "...", "parameters": {...}}]
"""

SUPERVISOR_FUNCTIONS = [
    {
        "name": "issueDetectionTool",
        "description": "Detects visible property issues from text or images and provides troubleshooting suggestions.",
        "parameters": {
            "type": "object",
            "properties": {
                "image_url": {"type": "string"},
                "context": {"type": "string"}
            },
            "required": []
        }
    },
    {
        "name": "tenancyFAQAgentTool",
        "description": "Handles tenancy FAQ with location-specific guidance.",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {"type": "string"},
                "location": {"type": "string"}
            },
            "required": ["question"]
        }
    },
    {
        "name": "initialGreetingTool",
        "description": "Greets the user or asks for missing details.",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            },
            "required": ["message"]
        }
    }
]

def call_supervisor(user_input):
    """Call Gemini to decide which tool to route to."""
    contents = [
        {"role": "user", "parts": [{"text": SUPERVISOR_PROMPT} ]},
        {"role": "user", "parts": [{"text": user_input} ]}
    ]
    payload = {
        "contents": contents,
        "tools": [{"functionDeclarations": SUPERVISOR_FUNCTIONS}],
        "generationConfig": {"temperature": 0.3}
    }
    resp = requests.post(API_URL, json=payload)
    resp.raise_for_status()
    text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    # Extract JSON within markdown
    json_start = text.find("[")
    json_text = text[json_start: text.rfind("]")+1]
    decision = json.loads(json_text)
    return decision[0]["tool_name"], decision[0]["parameters"]

def call_tenancy_agent(question, location=None):
    """Call Gemini as Tenancy FAQ Agent (Erica)."""
    TENANCY_PROMPT = """
You are Erica, a knowledgeable and friendly Tenancy FAQ Assistant. 
Do NOT provide an answer until you know the user's city or country; if missing, ask politely. 
Once known, give short, precise, and location-specific answers.
"""
    user_msg = question
    if location:
        user_msg += f" (Location: {location})"
    contents = [
        {"role": "user", "parts": [{"text": TENANCY_PROMPT} ]},
        {"role": "user", "parts": [{"text": user_msg} ]}
    ]
    resp = requests.post(API_URL, json={
        "contents": contents,
        "generationConfig": {"temperature": 0.5}
    })
    resp.raise_for_status()
    return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

def generate_issue_detection_response(context, image_url=None):
    """Call Gemini for issue detection with a full initial prompt."""
    ISSUE_PROMPT = """
You are a helpful, professional real estate assistant specializing in issue detection and troubleshooting. You receive property images and optional textual context from users who want help identifying visible problems in real estate properties and getting actionable advice.
🧠 Your Responsibilities:
Analyze uploaded images of real estate interiors or exteriors.
Identify visible property issues such as:
- Water damage
- Mold or mildew
- Paint peeling
- Cracks in walls/floors
- Broken fixtures
- Poor lighting
- Rust or corrosion
- Stains or structural wear
If text is provided, use it as additional context to improve issue detection.
Suggest practical next steps or fixes, such as:
- Contacting a relevant professional (e.g., plumber, electrician, contractor)
- Using specific treatments (e.g., anti-mold paint, waterproof coating)
- Performing quick temporary solutions (e.g., applying sealant)
Ask smart follow-up questions to clarify ambiguous scenarios (e.g., “Is there any smell or dampness in that area?” or “Is this near a water source?”)
🗣 Your Response Format:
Always respond in a clear, helpful tone. Use this format:
```markdown
**Identified Issue(s):**
- Issue 1
- Issue 2 (if any)

**Suggested Actions:**
- Action 1
- Action 2

**Follow-Up Question (if needed):**
- [Ask a relevant, clarifying question]
```"""
    user_msg = context
    if image_url:
        user_msg += f"\nImage URL: {image_url}"
    contents = [
        {"role": "user", "parts": [{"text": ISSUE_PROMPT} ]},
        {"role": "user", "parts": [{"text": user_msg} ]}
    ]
    resp = requests.post(API_URL, json={
        "contents": contents,
        "generationConfig": {"temperature": 0.5}
    })
    resp.raise_for_status()
    return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

def issue_detection_tool_handler(params):
    """Handler for the issueDetectionTool function call."""
    context = params.get("context", "")
    image_url = params.get("image_url")
    return generate_issue_detection_response(context, image_url)

def chat_with_tools(user_input):
    """
    Main orchestration: supervisor routes, then specialized agent handles, returning final reply.
    """
    tool_name, params = call_supervisor(user_input)
    if tool_name == "tenancyFAQAgentTool":
        reply = call_tenancy_agent(params["question"], params.get("location"))
    elif tool_name == "issueDetectionTool":
        reply = issue_detection_tool_handler(params)
    elif tool_name == "initialGreetingTool":
        reply = params["message"]
    else:
        reply = "Sorry, I couldn't determine how to help. Could you please clarify?"
    return reply

# Example usage
if __name__ == "__main__":
    print(chat_with_tools("Hello"))  # initialGreetingTool
    print(chat_with_tools("I have a crack in my wall"))  # issueDetectionTool -> detailed response
    print(chat_with_tools("What's the notice period to vacate in Mumbai?"))  # tenancyFAQAgentTool
