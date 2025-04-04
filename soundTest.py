# Sound Test imports
from vosk import Model, KaldiRecognizer
import pyaudio
import json

# Audio Imports
import os
import subprocess

# Hand tracking imports
import depthai as dai
import cv2
import numpy as np
import mediapipe as mp
import pytesseract
from fuzzywuzzy import process

# OpenAI imports
import base64
import openai
import unicodedata

########################################################################
#            VOICE RECOGNITION SET UP
########################################################################


model = Model("vosk-model-small-en-us-0.15")
#recognizer = KaldiRecognizer(model, 16000, '["analyze", "liquid", "start", "stop", "yes", "no"]')
recognizer = KaldiRecognizer(model, 16000, '["analyze", "liquid", "track", "label", "identify"]')


mic = pyaudio.PyAudio()
stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000,
                  input=True, frames_per_buffer=8000)
stream.start_stream()

########################################################################
#            HAND TRACKING SET UP 
########################################################################


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


pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

with open("kitchen_words.txt", "r") as f:
    kitchen_words = [line.strip().lower() for line in f.readlines()]

pipeline = dai.Pipeline()

cam_rgb = pipeline.create(dai.node.ColorCamera)
cam_rgb.setPreviewSize(640, 480)
cam_rgb.setInterleaved(False)
cam_rgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)

xout_rgb = pipeline.create(dai.node.XLinkOut)
xout_rgb.setStreamName("rgb")
cam_rgb.preview.link(xout_rgb.input)

def detect_fingertips(img):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    fingertips = {}
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            h, w, _ = img.shape
            fingertips["index"] = (int(hand_landmarks.landmark[8].x * w), int(hand_landmarks.landmark[8].y * h))
            return fingertips
    return None

def extract_text(image, fingertip):
    x, y = fingertip
    h, w, _ = image.shape

    x1, y1 = max(0, x - 50), max(0, y - 35)
    x2, y2 = min(w, x + 50), min(h, y ) 

    if x1 >= x2 or y1 >= y2:
        print("Invalid ROI, skipping OCR.")
        return "", (x1, y1, x2, y2)

    roi = image[y1:y2, x1:x2]

    if roi is None or roi.size == 0:
        print("Empty ROI, skipping OCR.")
        return "", (x1, y1, x2, y2)

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    _, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    scale_factor = 2
    gray = cv2.resize(gray, (gray.shape[1] * scale_factor, gray.shape[0] * scale_factor),
                      interpolation=cv2.INTER_LINEAR)

    text = pytesseract.image_to_string(gray, config='--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')

    words = text.lower().split()
    cleaned_text = [word for word in words if len(word) > 1]

    best_word = cleaned_text[0] if cleaned_text else ""

    if best_word:
        best_match = process.extractOne(best_word, kitchen_words, score_cutoff=50)
        if best_match:
            return best_match[0], (x1, y1, x2, y2)

    return "", (x1, y1, x2, y2)

def run_hand_tracking():
    with dai.Device(pipeline) as device:
        rgb_queue = device.getOutputQueue(name="rgb", maxSize=1, blocking=False)

        last_detected_word = None 

        while True:
            rgb_frame = rgb_queue.get().getCvFrame()

            fingertips = detect_fingertips(rgb_frame)

            detected_text = ""
            bbox = None
            if fingertips:
                index_finger = fingertips["index"]
                detected_text, bbox = extract_text(rgb_frame, index_finger)

                cv2.circle(rgb_frame, index_finger, 10, (0, 255, 0), -1)

            if bbox:
                x1, y1, x2, y2 = bbox
                cv2.rectangle(rgb_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            if detected_text and detected_text != last_detected_word:
                last_detected_word = detected_text
                cv2.putText(rgb_frame, detected_text.upper(), (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                print(f"Detected: {detected_text}")
                try:
                    subprocess.run(["espeak", detected_text])
                except Exception as e:
                    print(f"Speech error: {e}")

            cv2.imshow("RGB Camera", rgb_frame)

            if cv2.waitKey(1) == ord('q'): #Exit out by using 'q' key
                break
        
        cv2.destroyAllWindows()


########################################################################
#            OpenAI SETUP 
########################################################################

#Set up api key
client = openai.OpenAI(api_key="")  # Replace with your API key

LOCAL_IMAGE_PATH = "/home/visualAI/Desktop/image.jpg"

#Function to take images
def capture_image(image_path, rgb_queue):
    frame = rgb_queue.get().getCvFrame()
    cv2.imwrite(image_path, frame)

#Helper function that helps encode images to be read by chatgpt properly
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

#Function that makes call to the OpenAI api for image processing 
def process_image_with_gpt(image_path, prompt="Describe the main object in the image while reading any words on it, if possible, in a single concise sentence. Don't say Main Object in your response"):
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
    return response.choices[0].message.content

#Function that makes call to the OpenAI api for TTS
#Note: This has trouble with single words, so use Espeak instead for those cases 
def text_to_speech(text, output_file="output.mp3"):
    try:
        response = client.audio.speech.create(model="tts-1", voice="sage", input=text)
        with open(output_file, "wb") as f:
            f.write(response.content)

        if os.path.exists(output_file):
            print("🔊 Playing audio...")
            subprocess.run(["mpg123", output_file])
        else:
            print("❌ Audio file not found.")
    except Exception as e:
        print(f"TTS Error: {e}")
        
        
def on_api_released(prompt="Describe the main object in the image while reading any words on it, if possible, in a single concise sentence. Don't say Main Object in your response"):
    capture_image(LOCAL_IMAGE_PATH, rgb_queue)
    extracted_text = process_image_with_gpt(LOCAL_IMAGE_PATH, prompt)
    print("\n🖼️ GPT-4o's Response:\n", extracted_text)
    text_to_speech(extracted_text)

########################################################################
#            MAIN
########################################################################

subprocess.run(["espeak", "Voice assistant is ready."])

print("Listening...")

device, rgb_queue = setup_depthai()

while True:
    data = stream.read(4000, exception_on_overflow=False)
    if recognizer.AcceptWaveform(data):
        result = json.loads(recognizer.Result())
        word = result.get("text", "")
        if word:
            print(f"You said: {word}")
            if word == "track":
                run_hand_tracking()
            elif word == "analyze":
                on_api_released()
            elif word == "identify":
                on_api_released("Identify the main object you see in as few words as possible. Ideally three to five words. ")
            elif word == "liquid":
                on_api_released("Describe the water level of this measuring cup")
            else:
                #text_to_speech(word)
                subprocess.run(["espeak", word])


