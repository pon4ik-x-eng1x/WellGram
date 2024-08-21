class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email
        self.chats = []
    
    def add_chat(self, chat):
        self.chats.append(chat)
    
    def remove_chat(self, chat):
        self.chats.remove(chat)
