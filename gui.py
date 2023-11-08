import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

def load_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as file:
            chat_log_text.delete('1.0', tk.END)
            chat_log_text.insert(tk.END, file.read())

def grade_chat_log():
    # Parse disallowed phrases
    disallowed = disallowed_phrases_text.get('1.0', tk.END).splitlines()
    
    # Parse keywords
    kw_lines = keywords_text.get('1.0', tk.END).splitlines()
    keywords = {line.split(':')[0].strip(): float(line.split(':')[1].strip()) for line in kw_lines if ':' in line}
    
    # Parse chat log
    chat_log = chat_log_text.get('1.0', tk.END)
    parsed_chat_log = parse_chat_log_text(chat_log)
    
    # Grade the chat log
    host_name = name_entry.get()
    grades = grade_chat_log(parsed_chat_log, known_qs, keywords, disallowed)
    
    # Display the results
    result_text.delete('1.0', tk.END)
    for user, score in grades.items():
        result_text.insert(tk.END, f"{user}: {score}\n")

# Initialize the main window
root = tk.Tk()
root.title("Chat Log Grader")

# Layout configuration
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(1, weight=1)

# Elements
load_button = tk.Button(root, text="Load Chat Log", command=load_file)
load_button.grid(row=0, column=0, sticky='ew')

name_label = tk.Label(root, text="Enter your name:")
name_label.grid(row=0, column=1, sticky='ew')

name_entry = tk.Entry(root)
name_entry.grid(row=0, column=2, sticky='ew')

grade_button = tk.Button(root, text="Grade Chat Log", command=grade_chat_log)
grade_button.grid(row=2, column=0, columnspan=3, sticky='ew')

chat_log_text = ScrolledText(root)
chat_log_text.grid(row=1, column=0, sticky='nsew')

disallowed_phrases_label = tk.Label(root, text="Enter disallowed phrases (one per line):")
disallowed_phrases_label.grid(row=0, column=3, sticky='ew')

disallowed_phrases_text = ScrolledText(root)
disallowed_phrases_text.grid(row=1, column=3, sticky='nsew')

keywords_label = tk.Label(root, text="Enter keywords and points (format: keyword: points):")
keywords_label.grid(row=0, column=4, sticky='ew')

keywords_text = ScrolledText(root)
keywords_text.grid(row=1, column=4, sticky='nsew')

result_label = tk.Label(root, text="Grading Results:")
result_label.grid(row=2, column=3, columnspan=2, sticky='ew')

result_text = ScrolledText(root)
result_text.grid(row=3, column=0, columnspan=5, sticky='nsew')

# Start the application
root.mainloop()