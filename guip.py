import tkinter as tk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
import chardet
import re

# Define the parsing and grading functions

def parse_chat_log_text(text):
    chat_entries = []
    entry_pattern = re.compile(r'\[(\d{2}:\d{2})\] ([^:]+): (.+)')
    lines = text.split('\n')
    for line in lines:
        if line.strip() == "":
            continue
        match = entry_pattern.match(line.strip())
        if match:
            timestamp, user, message = match.groups()
            if "(Privately)" in user:
                continue
            chat_entries.append({'timestamp': timestamp, 'user': user.strip(), 'message': message.strip()})
    return chat_entries

def check_disallowed_phrases(message, disallowed_phrases):
    message_lower = message.lower()
    for phrase in disallowed_phrases:
        if phrase.lower() in message_lower:
            if message_lower.strip() == phrase.lower().strip():
                return True
    return False

def match_keywords(message, known_questions, keywords):
    score = 0
    for question, answer in known_questions.items():
        if answer.lower() in message.lower():
            return 1  # Full points for a correct answer
        if question.lower() in message.lower():
            score = sum(keywords[key] for key in keywords if key in message.lower())
            return score
    return score

def grade_chat_log(chat_entries, known_questions, keywords, disallowed_phrases):
    scores = {}
    for entry in chat_entries:
        user = entry['user']
        message = entry['message']
        if check_disallowed_phrases(message, disallowed_phrases):
            continue
        message_score = match_keywords(message, known_questions, keywords)
        if user not in scores:
            scores[user] = 0
        scores[user] += message_score
    return scores

# Define the GUI

class ChatLogGraderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Log Grader")

        # Load button
        self.load_button = tk.Button(root, text="Load Chat Log", command=self.load_file)
        self.load_button.pack()

        # Name entry
        tk.Label(root, text="Enter your name:").pack()
        self.name_entry = tk.Entry(root)
        self.name_entry.pack()

        # Disallowed phrases text area
        tk.Label(root, text="Enter disallowed phrases (one per line):").pack()
        self.disallowed_phrases_text = ScrolledText(root, height=5)
        self.disallowed_phrases_text.pack()

        # Keywords text area
        tk.Label(root, text="Enter keywords and points (format: keyword: points):").pack()
        self.keywords_text = ScrolledText(root, height=5)
        self.keywords_text.pack()

        # Grade button
        self.grade_button = tk.Button(root, text="Grade Chat Log", command=self.grade_chat_log)
        self.grade_button.pack()

        # Results text area
        tk.Label(root, text="Grading Results:").pack()
        self.results_text = ScrolledText(root, height=10)
        self.results_text.pack()

    def load_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
           with open(file_path, 'rb') as f:
                result = chardet.detect(f.read())  # or f.read(100) to read the first 100 bytes
                encoding = result['encoding']
           with open(file_path, 'r', encoding=encoding) as file:
                chat_log = file.read()
                self.chat_log = chat_log

    def grade_chat_log(self):
        known_qs = {}  # This should be populated with the actual known questions and their answers
        chat_entries = parse_chat_log_text(self.chat_log)
        disallowed = self.disallowed_phrases_text.get('1.0', tk.END).splitlines()
        kw_lines = self.keywords_text.get('1.0', tk.END).splitlines()
        keywords = {line.split(':')[0].strip(): float(line.split(':')[1].strip()) for line in kw_lines if ':' in line}
        grades = grade_chat_log(chat_entries, known_qs, keywords, disallowed)
        self.display_results(grades)

    def display_results(self, grades):
        self.results_text.delete('1.0', tk.END)
        for user, score in grades.items():
            self.results_text.insert(tk.END, f"{user}: {score}\n")

# Create and run the GUI application
root = tk.Tk()
app = ChatLogGraderGUI(root)
root.mainloop()