import os
import pickle


class ChatState:
    def __init__(self):
        self.command_counter = {}
        self.messages_to_del = []
        self.last_command_time = {}

    def load_chat_state(self):
        if os.path.exists("command_count.pickle") and os.stat("command_count.pickle").st_size > 0:
            with open("command_count.pickle", "rb") as f:
                self.command_counter = pickle.load(f)
        else:
            self.command_counter = {}

    def save_chat_state(self):
        with open('command_count.pickle', 'wb') as file:
            pickle.dump(self.command_counter, file)
