import os
import re
import time
import unicodedata
import subprocess
import base64
import cv2
from PIL import Image
import pytesseract
import openai
import depthai as dai

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
LOCAL_IMAGE_PATH = "/home/visualAI/Desktop/image.jpg"
TEXT_OUTPUT_PATH = "output.txt"
OUTPUT_AUDIO_FILE = "output.mp3"

# Create an OpenAI client
client = openai.OpenAI(api_key="")

# ---------------------------------------------------------
# DepthAI Camera Functions
# ---------------------------------------------------------
def setup_depthai():
    pipeline = dai.Pipeline()

    cam_rgb = pipeline.create(dai.node.ColorCamera)
    cam_rgb.setPreviewSize(640, 480)
    cam_rgb.setInterleaved(False)
    cam_rgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)

    xout = pipeline.create(dai.node.XLinkOut)
    xout.setStreamName("rgb")
    cam_rgb.preview.link(xout.input)

    device = dai.Device(pipeline)
    rgb_queue = device.getOutputQueue(name="rgb", maxSize=1, blocking=False)

    return device, rgb_queue

def capture_image(image_path, rgb_queue):
    print("\U0001F4F8 Capturing image from DepthAI...")
    frame = rgb_queue.get().getCvFrame()
    cv2.imwrite(image_path, frame)
    print(f"\u2705 Image saved to {image_path}")

# ---------------------------------------------------------
# OCR Functions
# ---------------------------------------------------------
def clean_text(text):
    text = text.strip()
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r'[^a-zA-Z0-9\s.,!?]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text

def perform_ocr(image_path, output_text_path):
    try:
        if not os.path.exists(image_path):
            print(f"Error: Image {image_path} not found!")
            return ""

        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        text = clean_text(text)

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
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def process_image_with_gpt(image_path, prompt="Describe the main object in the image while reading any words on it, if possible, in a concise sentence. Don't say Main Object in your response"):
    base64_image = encode_image(image_path)

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
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="sage",
            input=text
        )

        with open(output_file, "wb") as f:
            f.write(response.content)

        if os.path.exists(output_file):
            print("\U0001F50A Playing generated speech...")
            subprocess.run(["mpg123", output_file])
        else:
            print("\u274C Error: Audio file was not generated.")

    except Exception as e:
        print(f"\u274C Error generating speech: {e}")

# ---------------------------------------------------------
# Keyboard Mode Main Loop
# ---------------------------------------------------------
if __name__ == "__main__":
    device, rgb_queue = setup_depthai()
    print("\U0001F680 System Ready! Press 'o' for OCR or 's' for GPT mode.")

    while True:
        user_input = input("\n[o] OCR | [s] Send to GPT | [q] Quit: ").strip().lower()

        if user_input == 'o':
            capture_image(LOCAL_IMAGE_PATH, rgb_queue)
            extracted_text = perform_ocr(LOCAL_IMAGE_PATH, TEXT_OUTPUT_PATH)
            if len(extracted_text) < 5:
                print("\u26A0\ufe0f Text is too short. Using GPT instead.")
                extracted_text = process_image_with_gpt(LOCAL_IMAGE_PATH)
            text_to_speech(extracted_text)

        elif user_input == 's':
            capture_image(LOCAL_IMAGE_PATH, rgb_queue)
            extracted_text = process_image_with_gpt(LOCAL_IMAGE_PATH)
            print("\n\U0001F5BC GPT-4o's Response:\n", extracted_text)
            text_to_speech(extracted_text)

        elif user_input == 'q':
            print("Exiting...")
            break

        else:
            print("Invalid input. Try again.")
