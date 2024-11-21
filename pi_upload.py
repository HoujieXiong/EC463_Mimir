from google.cloud import storage, pubsub_v1

def upload_image_to_gcp(bucket_name, source_file, destination_blob):
    """Uploads an image to Google Cloud Storage."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob)

    blob.upload_from_filename(source_file)
    print(f"Uploaded {source_file} to {destination_blob} in bucket {bucket_name}.")

def send_notification_to_pubsub(project_id, topic_id, message):
    """Sends a Pub/Sub message to notify the desktop."""
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    publisher.publish(topic_path, message.encode("utf-8"))
    print(f"Published message to {topic_id}: {message}")



# Configuration
PROJECT_ID = "strategic-grove-442401-j1"  # Replace with your GCP project ID
BUCKET_NAME = "images_ec463"  # Replace with your GCS bucket name
TOPIC_ID = "image_upload"  # Replace with your Pub/Sub topic
IMAGE_FILE = r"C:\Users\14216\Desktop\EC463_Mimir\Images\image.jpg"# Replace with your image file path
DESTINATION_BLOB = "image.jpg"  # Name of the image in the bucket

# Upload the image and publish metadata
upload_image_to_gcp(BUCKET_NAME, IMAGE_FILE, DESTINATION_BLOB)

# Step 2: Notify the desktop via Pub/Sub
send_notification_to_pubsub(PROJECT_ID, TOPIC_ID, DESTINATION_BLOB)