##Imports
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from .tools import send_email_tool
from .memory import InMemoryHistory

##Load API Key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file!")

client = genai.Client(api_key=api_key)

#Initialize Memory
history = InMemoryHistory()

#System Prompt
SYSTEM_PROMPT = """
You are the 'Civic Helper'. 
PHASE 1: GATHER INFO
- Check if the user has ALREADY stated the 'Issue' or 'Location'.
- If missing, ask for them ONE BY ONE.

PHASE 2: DRAFT & ACT (Only when you have BOTH Issue and Location)
- Call the 'send_email_tool' with the destination, subject, and body.
- You do NOT need to print the letter yourself; the system will show it.
"""

#Define the Agent Runner Logic
def run_civic_agent(user_input: str):
    # Add user message to memory
    history.add_user_message(user_input)
    
    # Call Gemini
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite-preview-02-05", 
        contents=history.get_history(),
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=[send_email_tool],
            temperature=0.3 
        )
    )

    # Handle the Response
    final_output = ""

    #Capture any normal conversation text
    if response.text:
        final_output += response.text + "\n\n"

    #Check if the tool was used (This is where the letter is hiding!)
    if response.function_calls:
        for call in response.function_calls:
            if call.name == "send_email_tool":
                # Get the data the AI sent to the tool
                args = call.args
                dept = args.get('destination_dept', 'Authority')
                subj = args.get('subject', 'No Subject')
                body = args.get('body', 'No Content')

                #
                send_email_tool(**args)

                #Manually appends the letter to the chat
                letter_display = (
                    f"**DRAFTED LETTER**\n"
                    f"**To:** {dept}\n"
                    f"**Subject:** {subj}\n"
                    f"---\n{body}\n---\n"
                    f"*System: Sent successfully.*"
                )
                final_output += letter_display

    # Add to memory and return
    history.add_model_message(final_output)
    return final_output