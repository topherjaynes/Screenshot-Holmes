import os
import base64
from PIL import Image
from PIL.PngImagePlugin import PngInfo
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up OpenAI client
client = OpenAI()

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_image_content(image_path):
    """
    Use OpenAI's vision capabilities to extract content from the image.
    """
    base64_image = encode_image(image_path)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Describe the content of this image concisely."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=300
    )
    
    return response.choices[0].message.content.strip()

def get_new_name(image_content):
    """
    Use ChatGPT to generate a new name based on the image content.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates concise, descriptive filenames based on image content."},
            {"role": "user", "content": f"Generate a concise filename (without extension) for an image with this content: {image_content}"}
        ]
    )
    return response.choices[0].message.content.strip()

def add_metadata(image_path, content):
    """
    Add metadata to the image file using Pillow.
    """
    try:
        with Image.open(image_path) as img:
            metadata = PngInfo()
            metadata.add_text("Description", content)
            img.save(image_path, pnginfo=metadata)
    except Exception as e:
        print(f"Error adding metadata to {image_path}: {str(e)}")

def process_screenshots(folder_path):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.png') and 'screenshot' in filename.lower():
            file_path = os.path.join(folder_path, filename)
            
            try:
                # Get image content using OpenAI's vision capabilities
                content = get_image_content(file_path)
                
                # Get new name from ChatGPT
                new_name = get_new_name(content)
                
                # Add metadata
                add_metadata(file_path, content)
                
                # Rename file
                new_file_path = os.path.join(folder_path, f"{new_name}.png")
                os.rename(file_path, new_file_path)
                
                print(f"Processed: {filename} -> {new_name}.png")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

# Usage
folder_path = "/Users/topherjaynes/Desktop/screenshot/testshots"
process_screenshots(folder_path)