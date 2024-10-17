import os
import re
from PIL import Image
import piexif
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_image_content(image_path):
    """
    This function would typically use OCR to extract text from the image.
    For this example, we'll use a placeholder that returns a description.
    In a real implementation, you'd want to use an actual OCR library or API.
    """
    return f"Content of image: {os.path.basename(image_path)}"

def get_new_name(image_content):
    """
    Use ChatGPT to generate a new name based on the image content.
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates concise, descriptive filenames based on image content."},
            {"role": "user", "content": f"Generate a concise filename (without extension) for an image with this content: {image_content}"}
        ]
    )
    return response.choices[0].message['content'].strip()

def add_metadata(image_path, content):
    """
    Add metadata to the image file.
    """
    exif_dict = piexif.load(image_path)
    exif_dict["0th"][piexif.ImageIFD.ImageDescription] = content.encode('utf-8')
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, image_path)

def process_screenshots(folder_path):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.png') and 'screenshot' in filename.lower():
            file_path = os.path.join(folder_path, filename)
            
            # Get image content (placeholder for OCR)
            content = get_image_content(file_path)
            
            # Get new name from ChatGPT
            new_name = get_new_name(content)
            
            # Add metadata
            add_metadata(file_path, content)
            
            # Rename file
            new_file_path = os.path.join(folder_path, f"{new_name}.png")
            os.rename(file_path, new_file_path)
            
            print(f"Processed: {filename} -> {new_name}.png")

# Usage
folder_path = "/Users/topherjaynes/Desktop/screenshot/testshots"
process_screenshots(folder_path)