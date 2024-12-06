import time
import os
import ollama
import subprocess
import git

# Configuration
GITHUB_REPO = "HoujieXiong/EC463_mimir"  # Replace with the repository in 'owner/repo' format
TARGET_FILE_PATH = "image.jpg"  # Replace with the file path in the repo
LOCAL_SAVE_PATH = r"C:\Users\14216\Desktop\EC463_Mimir\Images\image.jpg"  # File to save locally
FEEDBACK_PATH = r"C:\Users\14216\Desktop\EC463_Mimir\feedback.txt"
REPO_PATH = r"C:\Users\14216\Desktop\EC463_Mimir"
CHECK_INTERVAL = 5  # Interval in seconds


def git_pull(repo_path):
    """
    Performs a `git pull` operation in the specified repository path.
    """
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "pull"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            if "Already up to date." in result.stdout:
                print("Repository is already up to date.")
                return False
            else:
                print("Git pull successful with updates!")
                return True

        else:
            print(f"Git pull failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error running git pull: {e}")
        return False


def send_file_to_ollama(file_path, question):
    """Sends a file to Ollama for analysis."""
    try:
        response = ollama.chat(
            model="llava",
            messages=[{
                "role": "user",
                "content": question,
                "images": [file_path]
            }]
        )
        # Extract the content of the response
        content = response.get("message", {}).get("content", "No response")
        
        # Save the feedback to a text file
        with open(FEEDBACK_PATH, "w", encoding="utf-8") as feedback_file:
            feedback_file.write(content)
            print(f"Feedback saved to {FEEDBACK_PATH}")
        
        return content
    except Exception as e:
        print(f"Error sending file to Ollama: {e}")
        return "Error in Ollama processing."


def commit_and_push_changes(repo_path, commit_message):
    """
    Stages, commits, and pushes changes in the specified Git repository.
    """
    try:
        repo = git.Repo(repo_path)
        repo.git.add(A=True)  # Stage all changes
        repo.index.commit(commit_message)  # Commit changes
        origin = repo.remote(name="origin")
        origin.push()  # Push changes
        print("Changes committed and pushed successfully.")
    except Exception as e:
        print(f"Error during git commit/push: {e}")


def monitor_repository(repo, target_file, local_path, question):
    """
    Monitors the repository for changes and processes updates.
    """
    while True:
        print("Checking for updates...")
        if git_pull(REPO_PATH):
            print("New changes detected. Processing the file...")
            response = send_file_to_ollama(local_path, question)
            print(f"Ollama analysis result: {response}")
            
            # Commit and push the feedback
            commit_and_push_changes(REPO_PATH, "Auto-update feedback from Ollama")
        else:
            print("No new changes or failed to pull changes.")
        
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    QUESTION = "What is this file about? Answer within 100 words."  # Customize your question
    monitor_repository(GITHUB_REPO, TARGET_FILE_PATH, LOCAL_SAVE_PATH, QUESTION)
