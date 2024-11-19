import time
from picamera2 import Picamera2

# Initialize the camera
camera = Picamera2()

camera.start()
# Set camera resolution (optional)

# Capture images periodically
try:
    print("Starting periodic image capture. Press Ctrl+C to stop.")
    count = 1  # Image counter for unique filenames
    while True:
#        filename = f"/home/Visual_AI/Desktop/EC463_Mimir/Images/image_{count:03d}.jpg"  # Store images in /home/pi/images
        filename = f"/home/Visual_AI/Desktop/EC463_Mimir/Images/image.jpg"  # Store images in /home/pi/images

        camera.capture_file(filename)
        print(f"Captured {filename}")
        count += 1
        time.sleep(5)  # Wait for 5 seconds
except KeyboardInterrupt:
    print("Stopping image capture...")
finally:
    camera.close()
