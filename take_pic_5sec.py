import time
from picamera import PiCamera

# Initialize the camera
camera = PiCamera()

# Set camera resolution (optional)
camera.resolution = (1920, 1080)

# Capture images periodically
try:
    print("Starting periodic image capture. Press Ctrl+C to stop.")
    count = 1  # Image counter for unique filenames
    while True:
        filename = f"/home/pi/images/image_{count:03d}.jpg"  # Store images in /home/pi/images
        camera.capture(filename)
        print(f"Captured {filename}")
        count += 1
        time.sleep(5)  # Wait for 5 seconds
except KeyboardInterrupt:
    print("Stopping image capture...")
finally:
    camera.close()
