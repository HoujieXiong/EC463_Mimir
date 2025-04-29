#!/bin/bash
# -------- wrapper for cron/systemd ----------

set -e

# wipe & start logging
exec > /home/visualAI/Desktop/va.log 2>&1


# add any env you need *before* Python starts
export AUDIODEV=pulse
export SDL_AUDIODRIVER=pulse
export HEADLESS=1                              

# give the OS, PulseAudio and Bluetooth a moment to come up
sleep 10

cd /home/visualAI/Desktop/voice_assistant

# run and send all output to a rotating log
source /home/visualAI/Desktop/venv/bin/activate
exec /home/visualAI/Desktop/venv/bin/python \
     /home/visualAI/Desktop/voice_assistant/voice_assistant.py

#>> /home/visualAI/Desktop/va.log 2>&1
