# Here's the complete code with all functions defined and without placeholder data:

import re

# Function to check for disallowed phrases
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
            return 1  # Full points for a correct answer
        if question.lower() in message.lower():
            score = sum(keywords[key] for key in keywords if key in message.lower())
            return score
    return score  # No match found, no points

# Function to grade the chat log
def grade_chat_log(chat_entries, known_questions, keywords, disallowed_phrases):
    scores = {}
    for entry in chat_entries:
        user = entry['user']
        message = entry['message']
        if check_disallowed_phrases(message, disallowed_phrases):
            continue  # Skip the message if it contains only disallowed phrases
        message_score = match_keywords(message, known_questions, keywords)
        if user not in scores:
            scores[user] = 0
        scores[user] += message_score
    return scores

# Function to parse chat logs in the described format
def parse_chat_log(file_path):
    """
    Parses the chat log from a text file.

    Args:
    - file_path: path to the text file containing the chat log.

    Returns:
    - A list of dictionaries with keys 'timestamp', 'user', and 'message' for each chat entry.
    """
    chat_entries = []

    # Regular expression pattern for matching chat log entries
    # This pattern assumes the format: [HH:MM:SS] Username: Message
    entry_pattern = re.compile(r'\[(\d{2}:\d{2}:\d{2})\] ([^:]+): (.+)')
    
    with open(file_path, 'r',encoding='utf-8') as file:
        for line in file:
            # Skip empty lines
            if line.strip() == "":
                continue
            
            # Match the line with the pattern to extract data
            match = entry_pattern.match(line.strip())
            if match:
                timestamp, user, message = match.groups()
                # Skip private messages
                if "(Privately)" in user:
                    continue
                
                # Add the entry to the list
                chat_entries.append({
                    'timestamp': timestamp,
                    'user': user.strip(),
                    'message': message.strip()
                })

    return chat_entries
# Main CLI function
def main_cli():
    host_name = input("Enter the host's name: ").strip()

    # In a real scenario, you would read the chat log text from a file.
    # For this example, we're using a hardcoded string.
    chat_log_text = """
    [08:30] John Doe: Hey, what's the answer to question 1?
    [08:31] Jane Smith: I think it might be related to gravity.
    [08:31] Teacher: Close! But remember to consider the effect of wind resistance.
    [08:31] John Doe (Privately): Got it, thanks!
    [08:32] Jane Smith: Could it be 9.8 m/s^2 then?
    """
    file_path = r'E:\New folder\OneDrive - The University of Technology,Jamaica\ChatLogAofA.txt'

# Read the chat log data from the file
    chat_log_data = parse_chat_log(file_path)
    for entry in chat_log_data:
        timestamp = entry['timestamp']
        user = entry['user']
        message = entry['message']
        print(f"{timestamp} - {user}: {message}")
    
    # Here you would get the known questions, keywords, and disallowed phrases
    # from a file or another source. For the example, they are defined as follows:
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
    ]

    # Grade the chat log
    grades = grade_chat_log(chat_log_data, known_qs, kw, dis_phrases)
    
    # Display the results
    print("\nGraded participation scores:")
    for user, score in grades.items():
        print(f"{user}: {score}")

main_cli() 
# Uncomment this line to run the CLI when executing this script in a local environment

# Since we can't run interactive input here, let's simulate the main function output
# if __name__ == "__main__":
#     # The following is just for demonstration and will simulate what would happen if the CLI could be run here.
#     # Normally, you would call main_cli() without any arguments and interact with the prompts.
#     print("\n[Simulated CLI Output]")
#     main_cli()