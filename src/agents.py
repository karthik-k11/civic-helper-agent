import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from .tools import send_email_tool
from .memory import InMemoryHistory

#Loading API Key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("❌ GOOGLE_API_KEY not found in .env file!")

client = genai.Client(api_key=api_key)

#Initialize Memory
history = InMemoryHistory()

#Define Personas
ADVOCATE_INSTRUCTIONS = """
You are the 'Civic Advocate', a friendly AI assistant.
Your goal is to interview the citizen to get details about a problem (potholes, trash, etc.).
Ask for:
1. The specific problem.
2. The location.
3. Any other relevant details.

Once you have ALL details, tell the user you are handing them over to the Drafter to write the letter.
DO NOT write the letter yourself. Just gather facts.
"""

DRAFTER_INSTRUCTIONS = """
You are the 'Civic Drafter'. You receive facts from the Advocate.
Your goal is to:
1. Write a formal, professional letter based on the facts.
2. Use the 'send_email_tool' to send it to the correct department.
"""

#Define the Agent Runner Logic
def run_civic_agent(user_input: str):
    """
    Orchestrates the conversation. 
    (In a real complex system, you'd use a router. Here we use a single smart model with tools).
    """
    
    #Add user message to memory
    history.add_user_message(user_input)
    
    # Configuration for the model
    # We give it the combined instructions + the tool
    full_system_instruction = f"""
    SYSTEM INSTRUCTIONS:
    You are a Multi-Agent system composed of an Advocate and a Drafter.
    
    PHASE 1 (Advocate): {ADVOCATE_INSTRUCTIONS}
    PHASE 2 (Drafter): {DRAFTER_INSTRUCTIONS}
    
    If you have enough info, use the 'send_email_tool' immediately.
    """

    #Calling Gemini
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=history.get_history(),
        config=types.GenerateContentConfig(
            system_instruction=full_system_instruction,
            tools=[send_email_tool],
            temperature=0.7
        )
    )

    #Handling Tool Calls
    response_text = ""
    
    if response.function_calls:
        for call in response.function_calls:
            fn_name = call.name
            args = call.args
            
            if fn_name == "send_email_tool":
                result = send_email_tool(**args)
                
                response_text = f"✅ ACTION TAKEN: {result}"
                
                history.add_model_message(response_text)
                return response_text

    #Normal Text Response
    if response.text:
        response_text = response.text
        history.add_model_message(response_text)

    return response_text