class InMemoryHistory:
    """
    Simple in-memory storage for chat history.
    """
    def __init__(self):
        self.history = []

    def add_user_message(self, content):
        self.history.append({"role": "user", "parts": [content]})

    def add_model_message(self, content):
        self.history.append({"role": "model", "parts": [content]})

    def get_history(self):
        return self.history

    def clear(self):
        self.history = []