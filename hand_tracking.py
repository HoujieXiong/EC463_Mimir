import depthai as dai
import cv2
import numpy as np
import mediapipe as mp
import pytesseract
import pyttsx3
from fuzzywuzzy import process

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

tts = pyttsx3.init()
tts.setProperty('rate', 150)

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
                tts.say(detected_text)
                tts.runAndWait()
            except Exception as e:
                print(f"Speech error: {e}")

        cv2.imshow("RGB Camera", rgb_frame)

        if cv2.waitKey(1) == ord('q'): 
            break

cv2.destroyAllWindows()
