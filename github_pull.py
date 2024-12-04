import requests
import time
import os
import ollama
import subprocess

# Configuration
GITHUB_REPO = "HoujieXiong/EC463_mimir"  # Replace with the repository in 'owner/repo' format
TARGET_FILE_PATH = "image.jpg"  # Replace with the file path in the repo
LOCAL_SAVE_PATH = "image.jpg"  # File to save locally
FEEDBACK_PATH="feedback.txt"
repo_path=r"C:\Users\14216\Desktop\EC463_Mimir\image"
CHECK_INTERVAL = 5  # Interval in seconds
LATEST_COMMIT = None  # Store the latest commit hash



def git_pull(repo_path):
    """
    Performs a `git pull` operation in the specified repository path.
    
    Args:
        repo_path (str): The local path of the Git repository.
    
    Returns:
        str: The output of the `git pull` command.
    """
    try:
        # Change the current working directory to the repo path
        result = subprocess.run(
            ["git", "-C", repo_path, "pull"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            print("Git pull successful!")
            return 1
        else:
            print("Git pull failed!")
            return 0
    except Exception as e:
        print(f"Error running git pull: {e}")
        return str(e)


def send_file_to_ollama(file_path, question):
    """Sends a file to Ollama for analysis."""
    try:
        response = ollama.chat(
            model="llama3.2-vision",
            messages=[{
                "role": "user",
                "content": question,
                "images": [file_path]
            }]
        )
        print(f"Ollama response: {response}")
        return response.get("choices", [{}])[0].get("message", {}).get("content", "No response")
    except Exception as e:
        print(f"Error sending file to Ollama: {e}")
        return "Error in Ollama processing."

def monitor_repository(repo, target_file, local_path, question):
    """Monitors the repository for changes and processes updates."""
    global LATEST_COMMIT
    while True:
        print("Checking for updates...")
        latest_commit = git_pull(repo_path)

        if latest_commit:
            response = send_file_to_ollama("image.jpg", question)
            print(f"Ollama analysis result: {response}")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    QUESTION = "What is this file about? answer within 100 words"  # Replace with your question for Ollama
    monitor_repository(GITHUB_REPO, TARGET_FILE_PATH, LOCAL_SAVE_PATH, QUESTION)
