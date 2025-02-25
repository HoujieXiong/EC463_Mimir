import cv2
import easyocr
import numpy as np
import pyttsx3
import mediapipe as mp
from picamera import PiCamera
from time import sleep

tts = pyttsx3.init()
tts.setProperty('rate', 150)

reader = easyocr.Reader(['en'])

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30

sleep(2)

camera.capture('captured_image.jpg')

frame = cv2.imread('captured_image.jpg')

def detect_fingertip(image):
    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            index_finger_tip = hand_landmarks.landmark[8] # index finger
            h, w, _ = image.shape
            x, y = int(index_finger_tip.x * w), int(index_finger_tip.y * h)
            return x, y
    return None

def extract_text(image, fingertip):
    x, y = fingertip
    h, w, _ = image.shape

    # region around finger tip
    x1, y1 = max(0, x-50), max(0, y-50)
    x2, y2 = min(w, x+50), min(h, y+50)
    roi = image[y1:y2, x1:x2]

    # grayscale OCR
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, 11, 2)

    text_result = reader.readtext(gray, detail=0)
    return " ".join(text_result) if text_result else ""

fingertip = detect_fingertip(frame)

if fingertip:
    detected_text = extract_text(frame, fingertip)
    if detected_text:
        print(f"Detected Word: {detected_text}")
        tts.say(detected_text)
        tts.runAndWait()
else:
    print("No fingertip detected.")

if fingertip:
    cv2.circle(frame, fingertip, 10, (0, 255, 0), -1)

cv2.imshow("Captured Image", frame)
cv2.waitKey(0)
cv2.destroyAllWindows()
