import tkinter as tk
import tkinter.font as tkFont
import chardet
import re

from tkinter import filedialog
from tkinter import scrolledtext
from tkinter import ttk
import pandas

host = ""

def check_disallowed_phrases(message, disallowed_phrases):
    message_lower = message.lower()
    for phrase in disallowed_phrases:
        if phrase.lower() in message_lower:
            if message_lower.strip() == phrase.lower().strip():
                return True
    return False

# Function to match keywords in a message
def match_keywords(message, known_questions, keywords):
    score = 0
    for question, answer in known_questions.items():
        if answer.lower() in message.lower():
            return 2  # Full points for a correct answer
        if question.lower() in message.lower():
            score = sum(keywords[key]
                        for key in keywords if key in message.lower())
            return score
    return score  # No match found, no points

# Function to grade the chat log
def grade_chat_log(content, host_name, known_questions, keywords, disallowed_phrases, triggers):
    scores = {}
    trigger_present = False
    for entry in content:
        user = entry['user']
        message = entry['message'].lower()
        print(f"Processing message from {user}: {message}")  # Debugging line
        if (user == host_name):
            if (trigger_present == True):
                trigger_present = any(
                    key.lower() in message for key in triggers)
                if (trigger_present == True):
                    trigger_present = False
                    continue
            trigger_present = any(key.lower() in message for key in triggers)
            continue
        if (trigger_present == True):
            if check_disallowed_phrases(message, disallowed_phrases):
                continue  # Skip the message if it contains only disallowed phrases
            message_score = match_keywords(message, known_questions, keywords)
            if user not in scores:
                scores[user] = 1
            scores[user] += message_score
    return scores


known_qs = {
    "What is the capital of France?": "Paris",
    "Who wrote Macbeth?": "Shakespeare",
}

kw = {
    "capital": 0.5,
    "Paris": 0.5,
    "wrote": 0.5,
    "Macbeth": 0.5,
}

dis_phrases = [
    "I don't know",
    "Can you repeat the question?",
    "I agree",
    "Sure",
    "Yeah",
    "Okay",
    "Sounds good",
    "That's correct",
    "You're right",
    "I think so",
    "I concur",
    "Makes sense",
    "True",
    "Of course",
    "Absolutely",
    "Definitely",
    "I suppose",
    "Fair enough",
    "I guess",
    "No doubt",
    "It's fine",
    "Agreed",
    "IDK",
    "No clue",
    "No idea",
    "¯_(ツ)_/¯",
    "I'm clueless",
    "I'm stumped",
    "I'm blank",
    "Let me guess",
    "Random guess",
    "Just guessing",
    "Haven't a clue",
    "Not sure, but",
    "I'll try anything",
    "Whatever, it's",
    "Don't care, but"
]

triggers = [
    "what is",
    "Next question, what is",
    "What's the answer for",
    "I think the correct response is",
    "Let's move on to the next question: What is",
    "Your answers are appreciated. The correct response is",
    "Thanks for your responses. The correct solution is",
    "Thank you for your answers. The correct answer is"
]


def update_score_table(scores):
    # Clear existing data in the table
    for i in scoreTable.get_children():
        scoreTable.delete(i)

    # Add new scores to the table
    for user, score in scores.items():
        scoreTable.insert("", 'end', values=(user, score))
        # Manually add test data
    scoreTable.insert("", 'end', values=("Test User", 10))
    scoreTable.insert("", 'end', values=("Another User", 15))

# Define the combined function
def add_chat(host_name= None):
    global chat_entries
    if host_name is None:
        host_name = host
    filepath = filedialog.askopenfilename()
    if filepath:
        with open(filepath, 'rb') as f:
            # Detect the encoding of the file
            result = chardet.detect(f.read())
            encoding = result['encoding']

        chat_entries = []
        entry_pattern = re.compile(r'^\d{2}:\d{2}:\d{2} From (.*?):\s*(.*)')

        with open(filepath, 'r', encoding=encoding) as file:
            for line in file:
                if line.strip() == "":  # Skip empty lines
                    continue
                # Match the line with the pattern to extract data
                match = entry_pattern.match(line.strip())
                if match:
                    user, message = match.groups()
                    if "(Privately)" in user:
                        continue  # Skip private messages
                    chat_entries.append({  # Add the entry to the list
                        'user': user.strip(),
                        'message': message.strip()
                    })

        # Now, you can use the chat_entries data as needed in your GUI application
        # For example, you can display it in a text widget
        text.delete('1.0', tk.END)
        for entry in chat_entries:
            text.insert(tk.END, f"User: {entry['user']}\nMessage: {entry['message']}\n\n")
         # Grade the chat log
        scores = grade_chat_log(chat_entries, host_name,
                                known_qs, kw, dis_phrases, triggers)

        for entry in chat_entries:
            text.insert(tk.END, f"User: {entry['user']}\nMessage: {entry['message']}\n\n")
        print("Chat Entries:", chat_entries)  # Debugging line
        update_score_table(scores)

def toggle_fullscreen(event=None):
    state = not frame.attributes('-fullscreen')
    frame.attributes('-fullscreen', state)
    if state:
        frame.geometry(f"{frame.winfo_screenwidth()}x{frame.winfo_screenheight()}")
    else:
        frame.geometry("1200x800")

def add_keywords():
    filepath = filedialog.askopenfilename()
    if filepath:
        label.config(text=f"Selected File: {filepath}")
        with open(filepath, 'rb') as f:
            # or f.read(100) to read the first 100 bytes
            result = chardet.detect(f.read())
            encoding = result['encoding']
        with open(filepath, 'r', encoding=encoding) as file:
            content = file.read()
            kywrd_text.insert(tk.END, content)
    
def on_submit():
    global host
    host = host_field.get()
    if host == "":
        error.config(text="You must enter host's name!")
        frame.after(1500, lambda: error.config(text=""))
    print(host)

# Create the main frame
frame = tk.Tk()
frame.title("Chat Log Analyzer")
frame.attributes('-fullscreen')
frame.geometry("800x600")

# Bind the F11 key to toggle full screen
frame.bind("<F11>", toggle_fullscreen)
frame.bind("<Escape>", toggle_fullscreen)

# Define a font with a specific size
label_font = tkFont.Font(family="Inter", weight="bold", size=18)
label_font1 = tkFont.Font(family="Inter", size=14)

label = tk.Label(frame, text="Chat Log Analyst", font=label_font)
label.grid(row=0, column=0, columnspan=6)

label3 = tk.Label(frame, text="Host's name: ", font=label_font1)
label3.grid(row=1, column=0)

host_field = tk.Entry(frame, width=30)
host_field.grid(row=1, column=1)

submit_btn = tk.Button(frame, text="Submit", command=on_submit)
submit_btn.grid(row=1, column=2)

text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=60, height=20)
text.grid(row=2, column=0, rowspan=3, columnspan=3, padx=20)

chat_btn = tk.Button(frame, text="Load Chat Log", command=add_chat)
chat_btn.grid(row=5, column=0, columnspan=3, pady=10)

kywrd_text = scrolledtext.ScrolledText(
    frame, wrap=tk.WORD, width=60, height=5)
kywrd_text.grid(row=6, column=0, columnspan=3)

key_btn = tk.Button(frame, text="Add Keywords", command=add_keywords)
key_btn.grid(row=7, column=0, columnspan=3, pady=10)

scoreTable = ttk.Treeview(frame, columns=("Name", "Score"), show="headings")
scoreTable.heading("Name", text="Name")
scoreTable.heading("Score", text="Score")
scoreTable.column("Name", width=120)
scoreTable.column("Score", width=60)
scoreTable.grid(row=2, column=3, columnspan=2)

error = tk.Label(frame, text="", fg="red")
error.grid(row=10, column=0, columnspan=10, sticky="ew")

# Run the application
frame.mainloop()