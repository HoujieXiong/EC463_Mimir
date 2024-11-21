import time
from picamera2 import Picamera2

# Initialize the camera
camera = Picamera2()

# Create a still configuration with the desired resolution
camera_config = camera.create_still_configuration(main={"size": (3280, 2464)})  # Set resolution to 1920x1080
camera.configure(camera_config)

# Start the camera
camera.start()

# Capture images periodically
try:
    print("Starting periodic image capture. Press Ctrl+C to stop.")
    count = 1  # Image counter for unique filenames
    while True:
        filename = f"/home/Visual_AI/Desktop/EC463_Mimir/Images/backpack.jpg"  # Save image with a fixed name

        camera.capture_file(filename)
        print(f"Captured {filename}")
        count += 1
        time.sleep(5)  # Wait for 5 seconds
except KeyboardInterrupt:
    print("Stopping image capture...")
finally:
    camera.stop()  # Stop the camera
    camera.close()  # Close resources
