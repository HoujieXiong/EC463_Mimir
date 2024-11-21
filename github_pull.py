import requests
import time
import os
import ollama

# Configuration
GITHUB_REPO = "HoujieXiong/EC463_mimir"  # Replace with the repository in 'owner/repo' format
TARGET_FILE_PATH = "feedback.txt"  # Replace with the file path in the repo
LOCAL_SAVE_PATH = "image.jpg"  # File to save locally
CHECK_INTERVAL = 5  # Interval in seconds
LATEST_COMMIT = None  # Store the latest commit hash

def get_latest_commit(repo):
    """Fetches the latest commit hash from the repository."""
    url = f"https://api.github.com/repos/{repo}/commits"
    headers = {"Accept": "application/vnd.github.v3+json"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        latest_commit = response.json()[0]['sha']  # Get the SHA of the latest commit
        return latest_commit
    except requests.exceptions.RequestException as e:
        print(f"Error fetching latest commit: {e}")
        return None

def download_file(repo, file_path, local_path):
    """Downloads a file from the repository."""
    url = f"https://github.com/{repo}/blob/main/{file_path}"  # Adjust branch if necessary
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(local_path, "wb") as file:
            file.write(response.content)
        print(f"Downloaded file: {file_path}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        return False

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
        latest_commit = get_latest_commit(repo)

        if latest_commit:
            if LATEST_COMMIT is None:
                LATEST_COMMIT = latest_commit
                print(f"Initial commit hash: {LATEST_COMMIT}")
            elif latest_commit != LATEST_COMMIT:
                print(f"New commit detected! Commit hash: {latest_commit}")
                LATEST_COMMIT = latest_commit

                # Step 1: Download the updated file
                if download_file(repo, target_file, local_path):
                    # Step 2: Send the file to Ollama
                    response = send_file_to_ollama(local_path, question)
                    print(f"Ollama analysis result: {response}")
            else:
                print("No new updates.")
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    QUESTION = "What is this file about? answer within 100 words"  # Replace with your question for Ollama
    monitor_repository(GITHUB_REPO, TARGET_FILE_PATH, LOCAL_SAVE_PATH, QUESTION)
