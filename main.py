import tkinter as tk # Importing tkinter for GUI creation
import tkinter.font as tkFont  # Importing tkinter font module for custom fonts
import chardet # Importing chardet to detect text file encoding
import re # Importing regular expressions for pattern matching in strings

from tkinter import filedialog # Importing filedialog from tkinter for file selection dialogs
from tkinter import scrolledtext # Importing scrolledtext for creating scrollable text areas
from sklearn.feature_extraction.text import TfidfVectorizer # Importing TfidfVectorizer for text vectorization
from sklearn.metrics.pairwise import cosine_similarity # Importing cosine_similarity to calculate similarity between text vectors
from tkinter import ttk # Importing ttk from tkinter for advanced widgets
import pandas # Importing pandas for data manipulation

host = "" # Variable to store the host's name
chat_entries ={}

# Function to calculate cosine similarity score between two text strings
def cosine_similarity_score(user_answer, correct_answer):
    vectorizer = TfidfVectorizer() # Initializing TF-IDF Vectorizer
    tfidf_matrix = vectorizer.fit_transform([user_answer, correct_answer]) # Transforming text to TF-IDF matrix
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2]) # Calculating cosine similarity
    return cosine_sim[0][0] # Returning cosine similarity score

# Function to check if a message contains any disallowed phrases
def check_disallowed_phrases(message, disallowed_phrases):
    message_lower = message.lower() # Converting message to lowercase
    for phrase in disallowed_phrases: # Iterating through disallowed phrases
        if phrase.lower() in message_lower: # Checking if phrase is in message
            if message_lower.strip() == phrase.lower().strip(): # Checking exact match of phrase
                return True
    return False

# Function to match keywords in a message and calculate a score
def match_keywords(message, known_questions, keywords, graded_question):
    score = 0.0 # Initializing score
    for question, answer in known_questions.items(): # Iterating through known questions and answers
        if(question.lower() in graded_question):  # Checking if question is part of the graded question
            score = cosine_similarity_score(message.lower(), answer.lower()); # Calculating similarity score for correct answer
            score = score * 2;  # Doubling the score for correct answer
            if(score<2):  # Adding keyword score if cosine similarity is less than full marks
                score += sum(keywords[key] for key in keywords if key in message.lower())
            return score
    return score  # Returning score


# Function to grade a chat log based on predefined criteria
def grade_chat_log(content, host_name, known_questions, keywords, disallowed_phrases, triggers):
    scores = {} # Dictionary to store scores for each user
    trigger_present=False  # Flag to check if a trigger is present in the chat
    question="" # Variable to store current question
    for entry in content: # Iterating through chat entries
        user = entry['user'] # Extracting user from entry
        message = entry['message'].lower()   # Extracting and converting message to lowercase
        if(user == host_name): # Checking if the user is the host
            # Logic to handle trigger phrases and questions
            if(trigger_present==True):  # If a trigger is already present
                trigger_present = any(key.lower() in message for key in triggers) #check for trigger end
                if(trigger_present==True):
                    trigger_present=False # Resetting trigger
                    continue
            trigger_present = any(key.lower() in message for key in triggers)# Check for new trigger
            if(trigger_present==True):
                question=message.lower() # Setting current question
            continue
        if (trigger_present == True): # If a question is currently active
            if check_disallowed_phrases(message, disallowed_phrases):
                continue  # Skipping message if it contains disallowed phrases
            message_score = match_keywords(message, known_questions, keywords,question)# Calculating score for message
            if user not in scores:
                scores[user] = 1 # Initializing score for user
            scores[user] += message_score # Adding score to user's total
    return scores # Returning scores dictionary

known_qs = {}
weighting=0.5
kw = {}

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

# Function to update the score table in the GUI
def update_score_table():
    global chat_entries
    if len(chat_entries) == 0:
        error.config(text="You must load chat log!") # Displaying error message
        frame.after(1500, lambda: error.config(text="")) # Clearing error message after 1.5 seconds
    else:
        scores = grade_chat_log(chat_entries, host,
                                        known_qs, kw, dis_phrases, triggers)
        # Clear existing data in the table
        for i in scoreTable.get_children(): # Removing existing data in the table
            scoreTable.delete(i)

        # Add new scores to the table
        for user, score in scores.items(): # Adding new scores to the table
            scoreTable.insert("", 'end', values=(user, score))
        
# Define the combined function
def add_chat():
    global host # Accessing the global variable host
    host = host_field.get().strip() # Getting host name from the input field
    if host == "": # If host name is not provided
        error.config(text="You must enter host's name!") # Displaying error message
        frame.after(1500, lambda: error.config(text="")) # Clearing error message after 1.5 seconds
    else:
        global chat_entries # Accessing the global variable chat_entries
        filepath = filedialog.askopenfilename() # Opening file dialog to select chat log file
        if filepath:
            with open(filepath, 'rb') as f:
                result = chardet.detect(f.read())# Detect the encoding of the file
                encoding = result['encoding']
            chat_entries = []   # Initializing list to store chat entries
            entry_pattern = re.compile(r'^\d{2}:\d{2}:\d{2} From (.*?):\s*(.*)') # Regex pattern to parse chat entries
            with open(filepath, 'r', encoding=encoding) as file:
                for line in file:
                    if line.strip() == "":  # Skip empty lines
                        continue
                    match = entry_pattern.match(line.strip()) # Matching line with regex pattern
                    if match:
                        user, message = match.groups() # Extracting user and message
                        if "(Privately)" in user:
                            continue  # Skip private messages
                        chat_entries.append({  # Add the entry to the list
                            'user': user.strip(),
                            'message': message.strip()
                        })

            # Updating the GUI to display chat entries
            text.delete('1.0', tk.END)  # Clearing existing text
            for entry in chat_entries:
                text.insert(tk.END, f"User: {entry['user']}\nMessage: {entry['message']}\n\n") # Adding entries to the text widget

def add_keywords():
    global host
    # Check if host's name is entered, show error if not
    if host == "":
        error.config(text="You must enter host's name!")
        frame.after(1500, lambda: error.config(text=""))
    else:
         # Open file dialog to select a file
        filepath = filedialog.askopenfilename()
        if filepath:
            # Open the file in binary mode and detect its encoding
            with open(filepath, 'rb') as f:
                # or f.read(100) to read the first 100 bytes
                result = chardet.detect(f.read())
                encoding = result['encoding']
            # Open the file with the detected encoding
            with open(filepath, 'r', encoding=encoding) as file:
                # Read the entire content of the file
                content = file.read()
                # Clear the keyword text box and insert the file content
                kywrd_text.delete('1.0', tk.END)
                kywrd_text.insert(tk.END, content)
                # Go back to the start of the file to process each line
                file.seek(0)
                 
                for line in file: # Iterate over each line in the file
                    if line.strip() == "":  # Skip empty lines
                        continue
                    kw[line.strip()] = weighting # Add each keyword from the file to the kw dictionary
def add_quest():
    global host    
    if host == "":# Check if host's name is entered, show error if not
        error.config(text="You must enter host's name!")
        frame.after(1500, lambda: error.config(text=""))
    else:
        filepath = filedialog.askopenfilename() # Open file dialog to select a file
        if filepath:
            with open(filepath, 'rb') as f:  # Detect the encoding of the file
                result = chardet.detect(f.read())
                encoding = result['encoding']
            # Read the file and add questions to the known_qs dictionary
            with open(filepath, 'r', encoding=encoding) as file:
                content = file.read()
                # Update the keyword text box with file content
                kywrd_text.delete('1.0', tk.END)
                kywrd_text.insert(tk.END, content)
                file.seek(0)
                for line in file: # Loop through each line in the file to process questions and answers
                    if line.strip() == "":  # Skip empty lines
                        continue
                    question, answer = line.strip().split(":")
                    known_qs[question.strip()]=answer.strip()
                # Grade the chat log and update the score table
                

# Create the main window for the application
frame = tk.Tk()
frame.title("Chat Log Analyzer") # Set the window title
frame.geometry("1000x800") # Set the window size

# Define fonts for labels
label_font = tkFont.Font(family="Inter", weight="bold", size=18)
label_font1 = tkFont.Font(family="Inter", size=14)
# Create and place the main label
label = tk.Label(frame, text="Chat Log Analyst", font=label_font)
label.grid(row=0, column=0, columnspan=6)
# Create and place the label for host's name
label3 = tk.Label(frame, text="Host's name: ", font=label_font1)
label3.grid(row=1, column=0)
# Create and place the entry field for host's name
host_field = tk.Entry(frame, width=30)
host_field.grid(row=1, column=1)
# Create and place a scrolled text area for displaying chat logs
text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=60, height=20)
text.grid(row=2, column=0, rowspan=3, columnspan=3, padx=20)
# Create and place a button to load chat logs
chat_btn = tk.Button(frame, text="Load Chat Log", command=add_chat)
chat_btn.grid(row=5, column=0, columnspan=3, pady=10)
# Create and place a scrolled text area for displaying keywords
kywrd_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=60, height=5)
kywrd_text.grid(row=6, column=0, columnspan=3)
# Create and place a button to add keywords
key_btn = tk.Button(frame, text="Add Keywords", command=add_keywords)
key_btn.grid(row=7, column=0, pady=10)
# Create and place a button to add questions
ques_btn = tk.Button(frame, text="Add Questions", command=add_quest)
ques_btn.grid(row=7, column=2)
# Create and place a button to submit 
submit_btn = tk.Button(frame, text="Submit", command=update_score_table)
submit_btn.grid(row=8, column=0, columnspan=3)
# Create and set up a Treeview widget for the score table
scoreTable = ttk.Treeview(frame, columns=("Name", "Score"), show="headings")
scoreTable.heading("Name", text="Name")
scoreTable.heading("Score", text="Score")
scoreTable.column("Name", width=120)
scoreTable.column("Score", width=60)
scoreTable.grid(row=2, column=3, columnspan=2)
# Create and place a label for displaying errors
error = tk.Label(frame, text="", fg="red")
error.grid(row=12, column=0, columnspan=10, sticky="ew")

# Run the main loop of the application
frame.mainloop()