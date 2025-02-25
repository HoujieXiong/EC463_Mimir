import depthai as dai
import cv2
import numpy as np
import mediapipe as mp
import pytesseract
import pyttsx3

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

tts = pyttsx3.init()
tts.setProperty('rate', 150)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

pipeline = dai.Pipeline()

cam_rgb = pipeline.create(dai.node.ColorCamera)
cam_rgb.setPreviewSize(640, 480)
cam_rgb.setInterleaved(False)
cam_rgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)

xout_rgb = pipeline.create(dai.node.XLinkOut)
xout_rgb.setStreamName("rgb")
cam_rgb.preview.link(xout_rgb.input)

def detect_hand(img):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            index_finger_tip = hand_landmarks.landmark[8]  # index finger
            h, w, _ = img.shape
            x, y = int(index_finger_tip.x * w), int(index_finger_tip.y * h)
            return x, y
    return None

def extract_text(image, fingertip):
    x, y = fingertip
    h, w, _ = image.shape

    # isolate area around index finger tip
    x1, y1 = max(0, x-40), max(0, y-20)
    x2, y2 = min(w, x+40), min(h, y+20)
    roi = image[y1:y2, x1:x2]

    # grayscale, faster OCR
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, 11, 2)

    # single word extraction
    text = pytesseract.image_to_string(gray, config='--psm 8 -l eng')

    # filter out random characters
    words = text.split()
    cleaned_text = " ".join([word for word in words if len(word) > 2])

    return cleaned_text.strip()

with dai.Device(pipeline) as device:
    rgb_queue = device.getOutputQueue(name="rgb", maxSize=1, blocking=False)

    while True:
        rgb_frame = rgb_queue.get().getCvFrame()

        fingertip = detect_hand(rgb_frame)

        detected_text = ""
        if fingertip:
            detected_text = extract_text(rgb_frame, fingertip)

        if detected_text:
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
