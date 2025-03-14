import os
import re
import time
import unicodedata
import subprocess
import threading
from time import sleep
from PIL import Image
import pytesseract
from picamera2 import Picamera2
from gpiozero import DigitalInputDevice
import openai
import base64
import subprocess  # For using FFmpeg


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
LOCAL_IMAGE_PATH = "/home/Visual_AI/Desktop/Local_Images/image.jpg"
TEXT_OUTPUT_PATH = "output.txt"
OUTPUT_AUDIO_FILE = "output.mp3"
# Create an OpenAI client
client = openai.OpenAI(api_key="")  # Replace with your API key

# ---------------------------------------------------------
# Camera, and OCRFunctions
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

def clean_text(text):
    """Cleans OCR text by removing non-alphanumeric characters and extra spaces."""
    text = text.strip()
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r'[^a-zA-Z0-9\s.,!?]', '', text)  # Keep only letters, numbers, and common punctuation
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    return text

def perform_ocr(image_path, output_text_path):
    """ Performs OCR on the image and saves extracted text to a file. """
    try:
        if not os.path.exists(image_path):
            print(f"Error: Image {image_path} not found!")
            return ""

        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        text = clean_text(text)  # Clean OCR text

        if not text.strip():
            print("Warning: No text detected in the image!")

        with open(output_text_path, "w") as file:
            file.write(text)

        print(f"OCR complete. Text saved to {output_text_path}")
        return text.strip()
        
    except Exception as e:
        print(f"Error during OCR: {e}")
        return ""
        
        
# ---------------------------------------------------------
# OpenAI Functions
# ---------------------------------------------------------
      
       
def encode_image(image_path):
    """Encodes an image to Base64 format for OpenAI API."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def process_image_with_gpt(image_path, prompt="Describe the main object in the image while reading any words on it, if possible, in a concise sentence. Don't say Main Object in your response"):
    """Sends an image to GPT-4o and gets a response."""
    base64_image = encode_image(image_path)  # Convert image to Base64

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an AI that analyzes images."},
            {"role": "user", "content": prompt},
            {"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}
        ],
        max_tokens=500
    )

    bot_response = response.choices[0].message.content
    return bot_response

def text_to_speech(text, output_file="output.mp3"):
    """Converts text to speech using OpenAI's TTS API and plays the audio using FFmpeg."""
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="sage", # Available voices: "alloy", "echo", "fable", "onyx", "nova", "shimmer"
            input=text
        )

        with open(output_file, "wb") as f:
            f.write(response.content)

        if os.path.exists(output_file):
            print("🔊 Playing generated speech...")
            subprocess.run(["ffplay", "-nodisp", "-autoexit", output_file])
        else:
            print("❌ Error: Audio file was not generated.")

    except Exception as e:
        print(f"❌ Error generating speech: {e}")

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
    
    
    #extracted_text = process_image_with_gpt(LOCAL_IMAGE_PATH)
    #print("\n🖼️ GPT-4o's Response:\n", extracted_text)
    extracted_text = perform_ocr(LOCAL_IMAGE_PATH, TEXT_OUTPUT_PATH)

    # If OCR text is too short, use GPT instead
    if len(extracted_text) < 5:
        print("⚠️ Text is too short. Sending image to OpenAI for analysis instead.")
        extracted_text = process_image_with_gpt(LOCAL_IMAGE_PATH)

    # Convert to Speech
    text_to_speech(extracted_text)
    print("✅ Done!")

def on_send_released():
    """ Captures an image locally, performs OCR, and converts text to audio. """
    print("Send button released. Capturing image and sending to OpenAI")
    
    capture_image(LOCAL_IMAGE_PATH)  # Only saving locally
    
    
    extracted_text = process_image_with_gpt(LOCAL_IMAGE_PATH)
    print("\n🖼️ GPT-4o's Response:\n", extracted_text)

    # Convert to Speech
    text_to_speech(extracted_text)
    print("✅ Done!")


if __name__ == "__main__":
    print("🚀 System Ready! Press the OCR button to capture an image.")

    while True:
        if button_ocr.value:  # When button is pressed
            on_ocr_released()
            time.sleep(1)  # Prevent multiple triggers
        if button_send.value:  # When button is pressed
            on_send_released()
            time.sleep(1)  # Prevent multiple triggers
