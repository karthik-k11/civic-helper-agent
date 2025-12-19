class InMemoryHistory:
    """
    Simple in-memory storage for chat history.
    """
    def __init__(self):
        self.history = []

    def add_user_message(self, content):
    
        self.history.append({"role": "user", "parts": [{"text": content}]})

    def add_model_message(self, content):
    
        self.history.append({"role": "model", "parts": [{"text": content}]})

    def get_history(self):
        return self.history

    def clear(self):
        self.history = []