import os
import time
import subprocess
import threading
from time import sleep
from PIL import Image
import pytesseract
from picamera2 import Picamera2
from gpiozero import DigitalInputDevice

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
GOOGLE_DRIVE_BASE = "/home/Visual_AI/Desktop/GoogleDrive/LLAMA_463"
GOOGLE_DRIVE_IMAGE_PATH = os.path.join(GOOGLE_DRIVE_BASE, "Images", "image.jpg")
LOCAL_IMAGE_PATH = "/home/Visual_AI/Desktop/Local_Images/image.jpg"
TEXT_OUTPUT_PATH = "output.txt"
FEEDBACK_PATH = os.path.join(GOOGLE_DRIVE_BASE, "Feedback", "feedback.txt")
ACTION_STATUS_PATH = os.path.join(GOOGLE_DRIVE_BASE, "Status", "action_status.txt")
FEEDBACK_AUDIO = os.path.join(GOOGLE_DRIVE_BASE, "Status", "converted_audio.wav")
CHECK_INTERVAL = 5  # Reduced for faster feedback detection
PIPER_MODEL = "en_US-lessac-medium"

# ---------------------------------------------------------
# Camera, OCR, and TTS Functions
# ---------------------------------------------------------
def capture_image(image_path):
    """ Captures an image using Picamera2 and saves it to the given path. """
    camera = Picamera2()
    camera_config = camera.create_still_configuration(main={"size": (3280, 2464)})
    camera.configure(camera_config)
    camera.start()

    try:
        print(f"Capturing image to {image_path}...")
        camera.capture_file(image_path)
        print(f"Image saved at {image_path}")

        # Ensure the image is fully saved before OCR
        wait_for_image(image_path)

    except Exception as e:
        print(f"Error capturing image: {e}")
    finally:
        camera.stop()
        camera.close()

def wait_for_image(image_path, timeout=5):
    """ Ensures the captured image file is completely written before accessing it. """
    start_time = time.time()
    while time.time() - start_time < timeout:
        if os.path.exists(image_path) and os.path.getsize(image_path) > 0:
            try:
                with Image.open(image_path) as img:
                    img.verify()
                print("Image file is fully written and ready for OCR.")
                return
            except Exception as e:
                print(f"Waiting for image to be fully written: {e}")
        time.sleep(0.5)
    print("Warning: Image might not be fully written!")

def perform_ocr(image_path, output_text_path):
    """ Performs OCR on the image and saves extracted text to a file. """
    try:
        if not os.path.exists(image_path):
            print(f"Error: Image {image_path} not found!")
            return

        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)

        if not text.strip():
            print("Warning: No text detected in the image!")

        with open(output_text_path, "w") as file:
            file.write(text)

        print(f"OCR complete. Text saved to {output_text_path}")
    except Exception as e:
        print(f"Error during OCR: {e}")

def send_image(image_path):
    """ Placeholder function for sending the image. """
    print(f"Image at {image_path} is ready to be sent.")

def update_action_status(action_text):
    """ Updates the action status file with a timestamp. """
    try:
        with open(ACTION_STATUS_PATH, "w") as file:
            file.write(f"{time.ctime()}: {action_text}\n")
        print("Action status updated.")
    except Exception as e:
        print(f"Error updating action status: {e}")

def convert_text_to_audio(text_file, audio_file):
    """ Converts extracted text to audio using Piper TTS and plays it via VLC. """
    try:
        with open(text_file, "r") as f:
            text = f.read().strip()
        if not text:
            print("Text file is empty. Nothing to convert.")
            return
        
        # Convert text to speech using Piper
        command = ["piper", "--model", PIPER_MODEL, "--output_file", audio_file]
        subprocess.run(command, input=text, text=True, check=True)
        print(f"Converted text from {text_file} to audio and saved to {audio_file}")

        # Play the audio file via VLC
        if os.path.exists(audio_file):
            print(f"Playing generated audio: {audio_file}")
            subprocess.run(["vlc", "--play-and-exit", audio_file], 
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        else:
            print(f"Error: Audio file {audio_file} not found!")

    except Exception as e:
        print(f"Error converting text to audio: {e}")

# ---------------------------------------------------------
# Button Setup using DigitalInputDevice
# ---------------------------------------------------------
button_ocr = DigitalInputDevice(4)
button_send = DigitalInputDevice(17)
button_ocr_only = DigitalInputDevice(27)

# ---------------------------------------------------------
# Button Callback Functions
# ---------------------------------------------------------
def on_ocr_released():
    """ Captures an image locally, performs OCR, and converts text to audio. """
    print("OCR button released. Capturing image and performing OCR.")
    
    capture_image(LOCAL_IMAGE_PATH)  # Only saving locally

    perform_ocr(LOCAL_IMAGE_PATH, TEXT_OUTPUT_PATH)
    update_action_status("OCR performed")
    convert_text_to_audio(TEXT_OUTPUT_PATH, FEEDBACK_AUDIO)

def on_send_released():
    """ Captures an image, saves it locally and to Google Drive, and sends it. """
    print("Send button released. Capturing image and sending image.")
    
    capture_image(LOCAL_IMAGE_PATH)  # Save locally first
    capture_image(GOOGLE_DRIVE_IMAGE_PATH)  # Save to Google Drive as well
    
    send_image(GOOGLE_DRIVE_IMAGE_PATH)
    update_action_status("Image sent")  # No audio playback here

def on_ocr_only_released():
    """ Performs OCR on an existing local image and converts the text to audio. """
    print("OCR-Only button released. Performing OCR on existing image.")
    
    if os.path.exists(LOCAL_IMAGE_PATH):
        perform_ocr(LOCAL_IMAGE_PATH, TEXT_OUTPUT_PATH)
        update_action_status("OCR only performed")
        convert_text_to_audio(TEXT_OUTPUT_PATH, FEEDBACK_AUDIO)
    else:
        print("No existing image found. Please capture an image first.")

# Attach the deactivation (release) callbacks.
button_ocr.when_deactivated = on_ocr_released
button_send.when_deactivated = on_send_released
button_ocr_only.when_deactivated = on_ocr_only_released

# ---------------------------------------------------------
# Feedback Monitoring Function
# ---------------------------------------------------------
def monitor_feedback():
    """ Monitors the feedback file and converts updated content into audio. """
    print(f"Monitoring feedback file: {FEEDBACK_PATH}")
    last_mod_time = None
    while True:
        if os.path.exists(FEEDBACK_PATH):
            current_mod_time = os.path.getmtime(FEEDBACK_PATH)
            if last_mod_time is None:
                last_mod_time = current_mod_time
            elif current_mod_time != last_mod_time:
                print("Feedback file has changed! Converting to audio...")
                convert_text_to_audio(FEEDBACK_PATH, FEEDBACK_AUDIO)
                last_mod_time = current_mod_time
        else:
            print(f"Feedback file not found at {FEEDBACK_PATH}. Waiting...")
        sleep(CHECK_INTERVAL)

# ---------------------------------------------------------
# Main Functionality
# ---------------------------------------------------------
def main():
    """ Starts monitoring threads and listens for button presses. """
    threading.Thread(target=monitor_feedback, daemon=True).start()

    print("Waiting for button press:")
    print(" - Press OCR button (GPIO4) to capture image, perform OCR, and convert text to audio")
    print(" - Press Send button (GPIO17) to capture image and send it")
    print(" - Press OCR-Only button (GPIO27) to perform OCR on an existing image and convert text to audio")

    while True:
        sleep(1)

if __name__ == "__main__":
    main()
