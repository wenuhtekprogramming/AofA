import tkinter as tk
import tkinter.font as tkFont
import chardet
import re

from tkinter import filedialog
from tkinter import scrolledtext
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tkinter import ttk
import pandas

host = ""


def validate_chat_entry(line):
    entry_pattern = re.compile(r'^\d{2}:\d{2}:\d{2} From (.*?):\s*(.*)')
    return entry_pattern.match(line.strip()) is not None

def cosine_similarity_score(user_answer, correct_answer):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([user_answer, correct_answer])
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return cosine_sim[0][0]

def check_disallowed_phrases(message, disallowed_phrases):
    message_lower = message.lower()
    for phrase in disallowed_phrases:
        if phrase.lower() in message_lower:
            if message_lower.strip() == phrase.lower().strip():
                return True
    return False

# Function to match keywords in a message
def match_keywords(message, known_questions, keywords, graded_question):
    score = 0.0
    for question, answer in known_questions.items():
        if(question.lower() in graded_question):
            score = cosine_similarity_score(message.lower(), answer.lower());# Full points for a correct answer
            score = score * 2;
            if(score<2):
                score += sum(keywords[key] for key in keywords if key in message.lower())
            return score
    return score  # No match found, no points


# Function to grade the chat log
def grade_chat_log(content, host_name, known_questions, keywords, disallowed_phrases, triggers):
    scores = {}
    trigger_present=False
    question=""
    for entry in content:
        user = entry['user']
        message = entry['message'].lower()  
        if(user == host_name):
            if(trigger_present==True): # Check for trigger start is still true
                trigger_present = any(key.lower() in message for key in triggers) #check for trigger end
                if(trigger_present==True):
                    trigger_present=False #Sets the it to end trigger question
                    continue
            trigger_present = any(key.lower() in message for key in triggers)#Check if trigger start is true
            if(trigger_present==True):
             question=message.lower() #setting question to trigger
             print("yOOOOOOO "+question)
            continue
        if (trigger_present == True):
            print("yOOOOOOO "+question)
            if check_disallowed_phrases(message, disallowed_phrases):
                continue  # Skip the message if it contains only disallowed phrases
            message_score = match_keywords(message, known_questions, keywords,question)
            if user not in scores:
                scores[user] = 1
            scores[user] += message_score
    return scores


known_qs = {}
#"What is the capital of France?": "Paris",
 #   "Who wrote Macbeth?": "Shakespeare",
#"What is the capital of Italy?" : "Rome",
#"What is the capital of Spain?" : "Madrid",
weighting=0.5
kw = { }
#  "capital":weighting,
#     "Paris":weighting,
#     "wrote":weighting,
#     "Macbeth":weighting,

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
    "Don't care, but",
    "Mi nuh know"
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
# Define the combined function
def add_chat():
    error.config(text=f"Place Keyword File [if necessary]  Before question File for Evaluation")
    global host
    host = host_field.get().strip()
    if host == "":
        error.config(text="You must enter host's name!")
        frame.after(1500, lambda: error.config(text=""))
    else:
        global chat_entries
        filepath = filedialog.askopenfilename()
        if filepath:
            try:
                with open(filepath, 'rb') as f:
                    # Detect the encoding of the file
                    result = chardet.detect(f.read())
                    encoding = result['encoding']
                chat_entries = []
                entry_pattern = re.compile(r'^\d{2}:\d{2}:\d{2} From (.*?):\s*(.*)')
                with open(filepath, 'r', encoding=encoding) as file:
                    for line in file:
                        if not validate_chat_entry(line):
                            error.config(text="Invalid chat log format.")
                            return
                        else:
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
                    #scores = grade_chat_log(chat_entries, host, known_qs, kw, dis_phrases, triggers)
            except Exception as e:
                    error.config(text=f"Error reading file: {e}")
                    return         
def add_keywords():
    global host
    if host == "":
        error.config(text="You must enter host's name!")
        frame.after(1500, lambda: error.config(text=""))
    else:
        filepath = filedialog.askopenfilename()
        if filepath:
            try:
                with open(filepath, 'rb') as f:
                    # or f.read(100) to read the first 100 bytes
                    result = chardet.detect(f.read())
                    encoding = result['encoding']
                with open(filepath, 'r', encoding=encoding) as file:
                    content = file.read()
                    kywrd_text.delete('1.0', tk.END)
                    kywrd_text.insert(tk.END, content)
                    file.seek(0)
                    for line in file:
                        if line.strip() == "":  # Skip empty lines
                                continue
                        kw[line.strip()] = weighting
            except Exception as e:
                error.config(text=f"Error reading file: {e}")
                return
def add_quest():
    global host
    if host == "":
        error.config(text="You must enter host's name!")
        frame.after(1500, lambda: error.config(text=""))
    else:
        filepath = filedialog.askopenfilename()
        if filepath:
            try:
                with open(filepath, 'rb') as f:
                    # or f.read(100) to read the first 100 bytes
                    result = chardet.detect(f.read())
                    encoding = result['encoding']
                with open(filepath, 'r', encoding=encoding) as file:
                    content = file.read()
                    kywrd_text.delete('1.0', tk.END)
                    kywrd_text.insert(tk.END, content)
                    file.seek(0)
                    for line in file:
                        if ":" not in line:
                            error.config(text="Invalid question-answer format.")
                            return
                        if line.strip() == "":  # Skip empty lines
                            continue
                        question, answer = line.strip().split(":")
                            #print("AFFAF"+question)
                            #print("sfsfsf"+answer)
                        known_qs[question.strip()]=answer.strip()
                        scores = grade_chat_log(chat_entries, host,
                                            known_qs, kw, dis_phrases, triggers)
                        update_score_table(scores)
            except Exception as e:
                error.config(text=f"Error reading file: {e}")
                return
                # print(scores)
                # print(known_qs)
                # print(kw)
                # print(chat_entries)
                # print(host)
              

# Create the main frame
frame = tk.Tk()
frame.title("Chat Log Analyzer")
frame.geometry("1000x800")

# Define a font with a specific size
label_font = tkFont.Font(family="Inter", weight="bold", size=18)
label_font1 = tkFont.Font(family="Inter", size=14)

label = tk.Label(frame, text="Chat Log Analyst", font=label_font)
label.grid(row=0, column=0, columnspan=6)

label3 = tk.Label(frame, text="Host's name: ", font=label_font1)
label3.grid(row=1, column=0)

host_field = tk.Entry(frame, width=30)
host_field.grid(row=1, column=1)

text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=60, height=20)
text.grid(row=2, column=0, rowspan=3, columnspan=3, padx=20)

chat_btn = tk.Button(frame, text="Load Chat Log", command=add_chat)
chat_btn.grid(row=5, column=0, columnspan=3, pady=10)

kywrd_text = scrolledtext.ScrolledText(
    frame, wrap=tk.WORD, width=60, height=5)
kywrd_text.grid(row=6, column=0, columnspan=3)

key_btn = tk.Button(frame, text="Add Keywords", command=add_keywords)
key_btn.grid(row=7, column=0, pady=10)

ques_btn = tk.Button(frame, text="Add Questions", command=add_quest)
ques_btn.grid(row=7, column=2)

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