import os

# Automatically detect if running headless
import ctypes
from ctypes.util import find_library

# Sound Test imports
from vosk import Model, KaldiRecognizer
import pyaudio
import json
import audioop

# Audio Imports
import subprocess

# Hand tracking imports
import depthai as dai
import cv2
import numpy as np
import mediapipe as mp
import pytesseract
from fuzzywuzzy import process
import queue

# OpenAI imports
import base64
import openai
import unicodedata


#GPIO buttons
from gpiozero import DigitalInputDevice, Device
from gpiozero.pins.lgpio import LGPIOFactory

Device.pin_factory = LGPIOFactory()

import threading
import time
import re
import pexpect
import sys

voiceOn = 0
trackOn = False


########################################################################
#            ALSA ERROR SUPPRESSION & ENV SETUP
########################################################################

os.environ["AUDIODEV"] = "pulse"
os.environ["SDL_AUDIODRIVER"] = "pulse"

def suppress_alsa_errors():
    try:
        asound = ctypes.cdll.LoadLibrary(find_library("asound"))
        def py_error_handler(filename, line, function, err, fmt):
            return
        ERROR_HANDLER_FUNC = ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_int,
                                              ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p)
        c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
        asound.snd_lib_error_set_handler(c_error_handler)
    except Exception as e:
        print("Failed to suppress ALSA errors:", e)

suppress_alsa_errors()


########################################################################
#            VOICE RECOGNITION SET UP
########################################################################

model = Model("/home/visualAI/Desktop/vosk-model-small-en-us-0.15")
#recognizer = KaldiRecognizer(model, 16000, '["analyze", "liquid", "start", "stop", "yes", "no"]')
recognizer = KaldiRecognizer(model, 16000, '["analyze", "liquid", "track", "nutrition", "identify","stop" ,"bluetooth", "echo", "shutdown","dictate"]')

# Initialize PyAudio
p = pyaudio.PyAudio()

# 🔍 Auto-detect working mic
input_index = None
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if info["maxInputChannels"] >= 1 and "USB" in info["name"]:
        input_index = i
        print(f"✅ Selected input device [{i}]: {info['name']}")
        break

if input_index is None:
    print("❌ No suitable input device found.")
    exit(1)

mic = pyaudio.PyAudio()
stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000,
                  input=True, frames_per_buffer=8000)
stream.start_stream()

########################################################################
#            DepthAI 
########################################################################

def setup_depthai():
    pipeline = dai.Pipeline()
    cam_rgb = pipeline.create(dai.node.ColorCamera) #Adds color camera to the pipeline
    cam_rgb.setPreviewSize(480, 480)
    cam_rgb.setInterleaved(False)
    cam_rgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)
    xout = pipeline.create(dai.node.XLinkOut) #USB connection for OAK device
    xout.setStreamName("rgb")
    cam_rgb.preview.link(xout.input)
    device = dai.Device(pipeline)
    rgb_queue = device.getOutputQueue(name="rgb", maxSize=1, blocking=False) #Return queue from which you can pull frames
    return device, rgb_queue


pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

with open("kitchen_words.txt", "r") as f:
    kitchen_words = [line.strip().lower() for line in f.readlines()]

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


########################################################################
#            BLUETOOTH CONNECTION
########################################################################

TARGET_MAC = "20:18:5B:29:BA:B4"
TARGET_NAME = "JBL Flip 5"

connectedFlag = 0;
def remove_ansi_escape(text):
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    text = ansi_escape.sub('', text)
    text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
    return text

def pair_first_available():
	global connectedFlag
	if connectedFlag == 1:
		print("Already Connected.")
		return 
	stream.stop_stream()
	print("Launching bluetoothctl...")
	child = pexpect.spawn('bluetoothctl', encoding='utf-8', timeout=None)
	child.logfile = sys.stdout  # Optional: show live output
	child.sendline('power on')
	child.sendline('agent on')
	child.sendline('default-agent')
	child.sendline('scan on')
	print("Scanning for 30 seconds...")
	discovered_devices = []
	seen_macs = set()
	start_time = time.time()
	child.sendline(f'pair {TARGET_MAC}')
	try:
		child.expect('Pairing successful', timeout=15)
		print(f"✅ Successfully paired with {TARGET_NAME} ({TARGET_MAC})")

		child.sendline(f'trust {TARGET_MAC}')
		child.expect(['trust succeeded', pexpect.EOF, pexpect.TIMEOUT], timeout=5)

		print(f"🔗 Connecting to {TARGET_NAME}...")
		child.sendline(f'connect {TARGET_MAC}')
		try:
			child.expect('Connection successful', timeout=10)
			connectedFlag = 1;
			print(f"✅ Connected to {TARGET_NAME} ({TARGET_MAC})")
		except pexpect.TIMEOUT:
			print(f"⚠️ Paired but failed to connect to {TARGET_NAME}")
	except pexpect.TIMEOUT:
		print(f"❌ Pairing failed with {TARGET_NAME}")

	child.sendline('exit')
	stream.start_stream()
	print("\n🔚 Done.")

########################################################################
#            OpenAI SETUP
########################################################################

# Set up api key
client = openai.OpenAI(api_key="")  # Replace with your API key

LOCAL_IMAGE_PATH = "/home/visualAI/Desktop/image.jpg"

# Function to take images
def capture_image(image_path):
    subprocess.run(["rpicam-jpeg",
    "-n",
    "-t", "1",
    "-r",
    "-o", image_path])
    

# Helper function that helps encode images to be read by chatgpt properly
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Function that makes call to the OpenAI api for image processing
def process_image_with_gpt(image_path, prompt="Describe the main object in the image while reading any words on it, if possible, in a single concise sentence. Don't say Main Object in your response"):
    base64_image = encode_image(image_path)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an AI that analyzes images."},
            {"role": "user", "content": prompt},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
        max_tokens=500
    )
    return response.choices[0].message.content

# Function that makes call to the OpenAI api for TTS
# Note: This has trouble with single words, so use Espeak instead for those cases
def text_to_speech(text, output_file="output.mp3"):
    try:
        response = client.audio.speech.create(model="tts-1", voice="sage", input=text)
        with open(output_file, "wb") as f:
            f.write(response.content)

        if os.path.exists(output_file):
            try:
                if stream.is_active():
                    stream.stop_stream()
                    print("🔊 Playing audio...")
                    subprocess.run(["mpg123", output_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            finally:
                print("Done playing")
                time.sleep(0.5)
                if not stream.is_active():
                    stream.start_stream()
        else:
            print("❌ Audio file not found.")
    except Exception as e:
        print(f"TTS Error: {e}")


def on_api_released(prompt="Describe the main object in the image while reading any words on it, if possible, in a single concise sentence. Don't say Main Object in your response"):
    capture_image(LOCAL_IMAGE_PATH)
    extracted_text = process_image_with_gpt(LOCAL_IMAGE_PATH, prompt)
    print("\n🖼️ GPT-4o's Response:\n", extracted_text)
    text_to_speech(extracted_text)


########################################################################
#            HELPER: Mute/Unmute + Speak
########################################################################

def say_text_espeak(text):
    """
    Helper function to speak using espeak, ensuring the microphone is paused.
    """
    # Stop the mic
    if stream.is_active():
        stream.stop_stream()

    # Now run the TTS command
    try:
        subprocess.run(["espeak", text], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    finally:
        # Resume mic
        time.sleep(0.5)
        if not stream.is_active():
            stream.start_stream()

########################################################################
#            HELPER: Kill Program
########################################################################

def shutdown_assistant():
    print("👋 Shutting down assistant...")
    say_text_espeak("Shutting down the assistant. Goodbye.")
    if stream.is_active():
        stream.stop_stream()
    stream.close()
    p.terminate()
    sys.exit(0)
    


########################################################################
#            HELPER: Voice Functionality
########################################################################

def voice_command_decision(word):
    global trackOn
    """Route a spoken command to the right handler."""
    print(f"You said: {word}")

    if word == "bluetooth":
        pair_first_available()

    elif word == "analyze":
        on_api_released()

    elif word == "shutdown":
        shutdown_assistant()

    elif word == "identify":
        on_api_released(
            "Identify the main object you see in as few words as possible. "
            "Ideally three to five words."
        )

    elif word == "liquid":
        on_api_released(
            "Describe the water level of the container/bottle. "
            "If it's a measuring cup try to read the measurements too, "
            "assume it is in cups."
        )

    elif word == "nutrition":
        on_api_released(
            "Try to read the food label if there is one, "
            "otherwise say 'no label found'"
        )
    elif word == "track":
        trackOn = True
        say_text_espeak("Hand tracking enabled")
    elif word == "stop":
        trackOn = False
        say_text_espeak("Hand tracking disabled")
    else:
        say_text_espeak(word)

########################################################################
#            MAIN
########################################################################

device, rgb_queue = setup_depthai()

say_text_espeak("Voice assistant is ready.")

print("Listening...")

button = DigitalInputDevice(21)
button_buffer=button.value
while True:
    # if button_api.value:
    #    on_api_released()
    #    time.sleep(1)

    # if button_hand_mode.value:
    #    toggle_hand_tracking()
    #    time.sleep(1)

    data = stream.read(4000, exception_on_overflow=False)

    # data_16k = audioop.ratecv(data, 2, 1, 44100, 16000, None)[0]

    



    if recognizer.AcceptWaveform(data):
        result = json.loads(recognizer.Result())
        word = result.get("text", "")
        if word:
            if voiceOn == 0 and (word.lower() == "dictate"):
                voiceOn = 1
                say_text_espeak("Listening")

            elif voiceOn == 1:
                voiceOn = 0
                voice_command_decision(word)
                say_text_espeak("deactivate Listening")
                
    if(button_buffer!=button.value):
        button_buffer=button.value
        if voiceOn == 0 :
            voiceOn = 1
            say_text_espeak("Listening")
            
        elif voiceOn == 1:
            voiceOn = 0
            say_text_espeak("deactivate Listening")
    # 2) Vision (non-blocking)
    if trackOn:
        frame = rgb_queue.tryGet()
        if frame is not None:
            img = frame.getCvFrame()
            fingertips = detect_fingertips(img)
            if fingertips:
                word, bbox = extract_text(img, fingertips['index'])
                if word:
                    print(f"Detected: {word}")
                    say_text_espeak(word)

    time.sleep(0.01)
