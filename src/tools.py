def send_email_tool(destination_dept: str, subject: str, body: str):
    """
    Simulates sending an email to a specific government department.
    Args:
        destination_dept: The department to send to (e.g., 'Parks', 'Sanitation').
        subject: The email subject line.
        body: The full email content.
    """
    print(f"\n[SYSTEM] 📧 SENDING EMAIL...")
    print(f"TO: {destination_dept}")
    print(f"SUBJECT: {subject}")
    print(f"BODY:\n{body}\n")
    
    return f"SUCCESS: Email sent to {destination_dept} regarding '{subject}'."