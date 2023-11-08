# Specify the file path
file_path = r'E:\New folder\OneDrive - The University of Technology,Jamaica\ChatLogAofA.txt'

# Open the file and read its contents
try:
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        print(content)  # Print the content of the file
except FileNotFoundError:
    print(f"The file at {file_path} was not found.")
except Exception as e:
    print(f"An error occurred: {e}")