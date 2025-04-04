import openai
import base64
import os

# Create an OpenAI client
client = openai.OpenAI(api_key="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")  # Replace with your API key

def encode_image(image_path):
    """Encodes an image to Base64 format for OpenAI API."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def process_image_with_gpt(image_path, prompt="Describe this image"):
    """Sends an image to GPT-4o and gets a response."""
    base64_image = encode_image(image_path)  # Convert image to Base64

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an AI that analyzes images."},
            {"role": "user", "content": prompt},
            {"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}
        ],
        max_tokens=500
    )

    bot_response = response.choices[0].message.content
    return bot_response

if __name__ == "__main__":
    image_path = input("Enter the path to your image: ").strip()
    
    if not os.path.exists(image_path):
        print("Error: File not found!")
    else:
        description = process_image_with_gpt(image_path)
        print("\nGPT-4o's Response:\n", description)
