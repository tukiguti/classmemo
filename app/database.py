import os
import json
from datetime import datetime

class Database:
    def __init__(self):
        self.users_file = 'users.json'
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({}, f)
        self.board_file = 'board.json'
        if not os.path.exists(self.board_file):
            with open(self.board_file, 'w') as f:
                json.dump([], f)

    def create_user_directory(self, email):
        user_dir = f"user_data/{email}"
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        
        courses_file = f"{user_dir}/courses.json"
        if not os.path.exists(courses_file):
            with open(courses_file, 'w') as f:
                json.dump([], f)
        
        events_file = f"{user_dir}/events.json"
        if not os.path.exists(events_file):
            with open(events_file, 'w') as f:
                json.dump([], f)

    def get_user_courses(self, email):
        with open(f"user_data/{email}/courses.json", 'r') as f:
            return json.load(f)

    def save_user_courses(self, email, courses):
        with open(f"user_data/{email}/courses.json", 'w') as f:
            json.dump(courses, f)

    def get_user_events(self, email):
        with open(f"user_data/{email}/events.json", 'r') as f:
            return json.load(f)

    def save_user_events(self, email, events):
        with open(f"user_data/{email}/events.json", 'w') as f:
            json.dump(events, f)

    def add_user(self, email, name, password):
        with open(self.users_file, 'r') as f:
            users = json.load(f)
        users[email] = {'name': name, 'password': password}
        with open(self.users_file, 'w') as f:
            json.dump(users, f)

    def get_user(self, email):
        with open(self.users_file, 'r') as f:
            users = json.load(f)
        return users.get(email)

    def verify_user(self, email, password):
        user = self.get_user(email)
        if user and user['password'] == password:
            return True
        return False
    
    def get_board_messages(self):
        with open(self.board_file, 'r') as f:
            return json.load(f)

    def add_board_message(self, user_name, message):
        messages = self.get_board_messages()
        messages.append({'user': user_name, 'message': message, 'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        with open(self.board_file, 'w') as f:
            json.dump(messages, f)