from PIL import Image
import pytesseract
import os

# Specify the path to the Tesseract executable if not in PATH (for Windows users)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
GOOGLE_DRIVE_BASE = "/home/Visual_AI/Desktop/GoogleDrive/LLAMA_463"
# Load an image from file
image_path = "images.jpg"

image = Image.open(image_path)

# Perform OCR
text = pytesseract.image_to_string(image)

# Save the extracted text to a file
with open("output.txt", "w") as file:
    file.write(text)

print("Text extracted and saved to output.txt")
