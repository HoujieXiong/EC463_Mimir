import time
import os
import ollama

CHECK_INTERVAL = 5  # seconds between checks

# Path to the image file in your Google Drive folder
IMAGE_PATH = r"C:\Users\14216\Desktop\LLAMA_463\Images\image.jpg"

# Path to the feedback file in the same (or any) Google Drive folder
FEEDBACK_PATH = r"C:\Users\14216\Desktop\LLAMA_463\Feedback\feedback.txt"

# Your question or prompt for Ollama
QUESTION = "What is this file about? Answer within 100 words. Make sure your output can be converted to TTS."



def send_file_to_ollama(file_path, question):
    """
    Sends a file to Ollama for analysis and saves feedback to FEEDBACK_PATH.
    """
    try:
        response = ollama.chat(
            model="llama3.2-vision",
            messages=[
                {
                    "role": "user",
                    "content": question,
                    "images": [file_path]
                }
            ]
        )
        
        # Extract the text response
        content = response.get("message", {}).get("content", "No response")

        # Save feedback to the text file in Google Drive
        with open(FEEDBACK_PATH, "w", encoding="utf-8") as feedback_file:
            feedback_file.write(content)
            print(f"Feedback saved to {FEEDBACK_PATH}")

        return content

    except Exception as e:
        print(f"Error sending file to Ollama: {e}")
        return "Error in Ollama processing."


def monitor_google_drive_image(image_path, question):
    """
    Monitors a file for changes and sends it to Ollama when updated.
    """
    last_mod_time = None

    while True:
        # Only proceed if the file exists
        print(f"1111")
        if os.path.exists(image_path):
            print(f"2222")
            current_mod_time = os.path.getmtime(image_path)

            # First time, just record the mod time
            if last_mod_time is None:
                print(f"3333")
                response = send_file_to_ollama(image_path, question)
                print(f"Ollama analysis result:\n{response}\n")
                last_mod_time = current_mod_time

            # Check if the file has changed
            elif current_mod_time != last_mod_time:
                print(f"4444")
                print("Detected updated file in Google Drive. Processing...")
                response = send_file_to_ollama(image_path, question)
                print(f"Ollama analysis result:\n{response}\n")

                # Update the last known mod time
                last_mod_time = current_mod_time

        else:
            print(f"5555")
            print(f"File not found at {image_path}. Waiting...")

        time.sleep(CHECK_INTERVAL)

# ----------------------------------
# Main Entry Point
# ----------------------------------
if __name__ == "__main__":
    monitor_google_drive_image(IMAGE_PATH, QUESTION)
