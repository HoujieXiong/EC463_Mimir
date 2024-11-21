import os
from gpiozero import LED

# Configuration
AUDIO_FILE = "test2.mp3"  # Replace with your .wav file path
SPEAKER_PIN = 18  # GPIO pin connected to the speaker

# Setup GPIO using gpiozero
speaker = LED(SPEAKER_PIN)  # Treat the speaker pin as an output device

try:
    print("Playing audio...")
    # Activate the speaker pin (if needed, depending on your hardware setup)
    speaker.on()

    # Play the .wav file using aplay
    os.system(f"aplay {AUDIO_FILE}")
    print("Audio playback completed.")
finally:
    # Turn off the speaker pin
    speaker.off()
    print("GPIO cleaned up.")
