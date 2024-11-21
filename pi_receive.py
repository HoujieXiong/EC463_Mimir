from google.cloud import pubsub_v1

def receive_processed_text(project_id, subscription_id):
    """Listens for processed text from the desktop."""
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    def callback(message):
        print(f"Received processed text: {message.data.decode('utf-8')}")
        message.ack()  # Acknowledge the message

    subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_id}...")

    # Keep the program running
    import time
    while True:
        time.sleep(60)

# Configuration
PROJECT_ID = "your-project-id"  # Replace with your GCP project ID
SUBSCRIPTION_ID = "desktop-to-raspi"  # Replace with your Pub/Sub subscription ID

# Start listening for processed text
receive_processed_text(PROJECT_ID, SUBSCRIPTION_ID)
