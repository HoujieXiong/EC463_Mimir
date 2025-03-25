import openai
import subprocess
# Create an OpenAI client
client = openai.OpenAI(api_key="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")  # Replace with your API key

def text_to_speech(text, voice="alloy", output_file="output.mp3"):
    """Converts text to speech using OpenAI's API and plays it."""
    response = client.audio.speech.create(
        model="tts-1",  # OpenAI's text-to-speech model
        voice=voice,  # Choose from "alloy", "echo", "fable", "onyx", "nova", "shimmer"
        input=text
    )

    # Save the audio file
    with open(output_file, "wb") as f:
        f.write(response.content)

    # Play the audio using ffmpeg
    subprocess.run(["ffplay", "-nodisp", "-autoexit", output_file])


if __name__ == "__main__":
    user_text = input("Enter text to convert to speech: ")
    text_to_speech(user_text)
