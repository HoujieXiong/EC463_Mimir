import time
from picamera2 import Picamera2
import requests
import time
import os
import subprocess

import git

# Initialize the camera
camera = Picamera2()

# Create a still configuration with the desired resolution
camera_config = camera.create_still_configuration(main={"size": (3280, 2464)})  # Set resolution to 1920x1080
camera.configure(camera_config)

# Start the camera
camera.start()

# Capture images periodically
try:
    print("Starting periodic image capture. Press Ctrl+C to stop.")
    count = 1  # Image counter for unique filenames

    filename = f"/home/Visual_AI/Desktop/EC463_Mimir/Images/image.jpg"  # Save image with a fixed name

    camera.capture_file(filename)
    print(f"Captured {filename}")
    count += 1
except KeyboardInterrupt:
    print("Stopping image capture...")
finally:
    camera.stop()  # Stop the camera
    camera.close()  # Close resources

    
   

# Path to your local Git repository
repo_path = "/home/Visual_AI/Desktop/EC463_Mimir"

# Open the repository
repo = git.Repo(repo_path)

# Stage all changes (equivalent to `git add .`)
repo.git.add(A=True)

# Commit the changes
commit_message = "Auto Update"
repo.index.commit(commit_message)

# Push the changes to the remote repository
origin = repo.remote(name="origin")
origin.push()

print("Changes pushed successfully.")




# Configuration
GITHUB_REPO = "HoujieXiong/EC463_mimir"  # Replace with the repository in 'owner/repo' format
TARGET_FILE_PATH = "/home/Visual_AI/Desktop/EC463_Mimir/feedback.txt"  # Replace with the file path in the repo

CHECK_INTERVAL = 5  # Interval in seconds
LATEST_COMMIT = None  # Store the latest commit hash

def git_pull(repo_path):
    """
    Performs a `git pull` operation in the specified repository path.

    Args:
        repo_path (str): The local path of the Git repository.

    Returns:
        bool: True if new changes were pulled, False otherwise.
    """
    try:
        # Run the git pull command
        result = subprocess.run(
            ["git", "-C", repo_path, "pull"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Check if the operation was successful
        if result.returncode == 0:
            if "Already up to date" in result.stdout:
                print("Repository is already up to date.")
                return False  # No new changes
            else:
                print("Git pull successful! Changes were pulled.")
                return True  # New changes were fetched
        else:
            print(f"Git pull failed! Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error running git pull: {e}")
        return False

 
def monitor_repository(repo, target_file):
    """Monitors the repository for changes and processes updates."""
    global LATEST_COMMIT
    while True:
        print("Checking for updates...")
        latest_commit = git_pull(repo_path)

        if latest_commit:
            try:
                # Open the file in read mode
                with open(TARGET_FILE_PATH, "r") as file:
                    # Read the content of the file
                    content = file.read()
                    # Print the content
                    subprocess.run(
                        ["vlc", "feedback.wav"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    print(content)
                    break
            except FileNotFoundError:
                print(f"Error: The file at '{TARGET_FILE_PATH}' was not found.")
            except Exception as e:
                print(f"An error occurred: {e}")

        time.sleep(CHECK_INTERVAL)

monitor_repository(GITHUB_REPO, TARGET_FILE_PATH)

