import requests
from picamera import PiCamera
from time import sleep
import os

SERVER_URL = '' # not yet

# Directory to save captured images temporarily
IMAGE_PATH = '/home/pi/captured_image.jpg'

def capture_image():
    camera = PiCamera()
    try:
        camera.start_preview()
        sleep(2)  
        camera.capture(IMAGE_PATH)
        print("Image captured and saved.")
    finally:
        camera.close()

def send_image():
    # Open the image file
    with open(IMAGE_PATH, 'rb') as image_file:
        # Define payload for the POST request
        files = {'image': image_file}
        try:
            # Send the image to the server
            response = requests.post(SERVER_URL, files=files)
            response.raise_for_status()  # Raise an error for bad HTTP responses
            print("Image sent to the server successfully.")
            
            # Process the server response
            result = response.json()  # Assuming the server returns a JSON response
            print("Received response:", result)
            return result
        except requests.exceptions.RequestException as e:
            print("Failed to send image:", e)
            return None

def main():
    # Capture the image
    capture_image()
    
    # Send the image to the server and get the response
    result = send_image()
    
    # Clean up: remove the image file
    if os.path.exists(IMAGE_PATH):
        os.remove(IMAGE_PATH)
    
    # Process result if needed
    if result:
        # Perform any further action based on server response here
        pass

if __name__ == '__main__':
    main()
