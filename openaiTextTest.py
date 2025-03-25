import openai

# Set your OpenAI API key (Use environment variables in production)
client = openai.OpenAI(api_key="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")  # Replace with your actual API key

def chat_with_openai():
    while True:
        user_input = input("You: ")  # Get user input

        if user_input.lower() in ["exit", "quit", "bye"]:  # Exit condition
            print("Chat ended.")
            break

        response = client.chat.completions.create(
            model="gpt-4o",  # Use GPT-4o model
            messages=[{"role": "user", "content": user_input}],  # Send user's input
            temperature=1,  # Control randomness (1 is default)
            max_tokens=200  # Adjust response length
        )

        bot_response = response.choices[0].message.content  # Extract response
        print("ChatGPT:", bot_response)

if __name__ == "__main__":
    chat_with_openai()
