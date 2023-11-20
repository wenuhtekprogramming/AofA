import re
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
# Function to check for disallowed phrases

# Function to calculate cosine similarity
#Complexity O(n)
#https://www.kaggle.com/code/kirankarthikeyan/time-complexity-for-document-similarity-measures#The-Cosine-Similarity
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
            #if answer.lower() in message.lower():
            score = cosine_similarity_score(message.lower(), answer.lower());# Full points for a correct answer
            score *= 2;
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
            if check_disallowed_phrases(message, disallowed_phrases):
                continue  # Skip the message if it contains only disallowed phrases
            message_score = match_keywords(message, known_questions, keywords,question)
            if user not in scores:
                scores[user] = 1
            scores[user] += message_score
    return scores

# Function to parse chat logs in the described format
def parse_chat_log(file_path):
    """
    Parses the chat log from a text file.
    Args: - file_path: path to the text file containing the chat log.
    Returns: - A list of dictionaries with keys 'timestamp', 'user', and 'message' for each chat entry.
    """
    chat_entries = []
    # Regular expression pattern for matching chat log entries
    # This pattern assumes the format: [HH:MM:SS] Username: Message
    entry_pattern = re.compile(r'^\d{2}:\d{2}:\d{2} From (.*?):\s*(.*)')
    # entry_pattern = re.compile(r'^(.*?): \s*(.+)$')

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.strip() == "":  # Skip empty lines
                continue
            match = entry_pattern.match(line.strip()) # Match the line with the pattern to extract data
            if match:
                user, message = match.groups()
                if "(Privately)" in user:
                    continue # Skip private messages
                chat_entries.append({ # Add the entry to the list
                    'user': user.strip(),
                    'message': message.strip()
                })
        return chat_entries
    
#nMain CLI function
def main_cli():
    host_name = input("Enter the host's name: ").strip()
    print("Current working directory:", os.getcwd())
    file_path = r'AofALogFile.txt'

# Read the chat log data from the file
    chat_log_data = parse_chat_log(file_path)
    for entry in chat_log_data:
        # timestamp = entry['timestamp']
        user = entry['user']
        message = entry['message']
        # print(f"{timestamp} - {user}: {message}")
        print(f"{user}: {message}")

    # Here you would get the known questions, keywords, and disallowed phrases
    # from a file or another source. For the example, they are defined as follows:
    known_qs = {
        "What is the Capital of France?": "Paris",
        "Who wrote macbeth?": "Shakespeare",
        "What is the capital of italy?" : "Rome",
        "What is the capital of Spain?" : "Madrid",
    }
    
    kw = {
        "capital": 0.5,
        "wrote": 0.5,
        "macbeth": 0.5,
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

    # Grade the chat log
    grades = grade_chat_log(chat_log_data, host_name,
                            known_qs, kw, dis_phrases, triggers)

    # Display the results
    print("\nGraded participation scores:")
    for user, score in grades.items():
        print(f"{user}: {score}")


main_cli()
# if line.strip().startswith(''):
#     # Remove the leading '-' and whitespace
#     message = line.strip()[2]
#     # Extract user from the previous line
#     user = chat_entries[-1]['user']
#     # Skip private messages
#     if user and "(Privately)" in user:
#         continue
#     # Add the entry to the list
#     chat_entries.append({
#         'user': user.strip(),
#         'message': message.strip()
#     })
