#Imports
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from .tools import send_email_tool
from .memory import InMemoryHistory

#Load API Key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file!")

client = genai.Client(api_key=api_key)

#Initialize Memory
history = InMemoryHistory()

#Define The Strict Workflow
SYSTEM_PROMPT = """
You are the 'Civic Helper'. You must follow this strict Logic Flow:

PHASE 1: GATHER INFO
- Check if the user has ALREADY stated the 'Issue' or 'Location'.
- If the 'Issue' is missing, ask: "What is the problem?"
- If the 'Location' is missing, ask: "Where is the location?"
- DO NOT ask for information you already have.

PHASE 2: DRAFT & ACT (Only when you have BOTH Issue and Location)
- Step 1: Write a formal complaint letter addressed to the relevant department (Public Works, Sanitation, etc.).
- Step 2: DISPLAY the full letter to the user in the chat.
- Step 3: CALL the 'send_email_tool' with the destination, subject, and body.
- Step 4: After the tool runs, add a short confirmation message.

Example Output format for Phase 2:
"Here is the drafted letter:
[Subject: ...]
[Body: ...]

(Tool Call happens here hiddenly)

I have sent this mail to the Public Works Department."
"""

#Define the Agent Runner Logic
def run_civic_agent(user_input: str):

    history.add_user_message(user_input)
    
    # Calling Gemini 
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=history.get_history(),
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=[send_email_tool],
            temperature=0.4
        )
    )

    #Handle the Response
    final_output = ""

    if response.text:
        final_output += response.text + "\n\n"

    #If the model called the tool, execute it
    if response.function_calls:
        for call in response.function_calls:
            if call.name == "send_email_tool":
    
                send_email_tool(**call.args)
                
                if "sent" not in final_output.lower():
                    final_output += f"\n(System:Email successfully sent to {call.args.get('destination_dept')}.)"

    #Add to memory and return
    history.add_model_message(final_output)
    return final_output