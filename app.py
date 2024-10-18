import os
import re
import base64
from PIL import Image
from PIL.PngImagePlugin import PngInfo
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up OpenAI client
client = OpenAI()

def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_image_content(image_path: str) -> str:
    """
    Use OpenAI's vision capabilities to extract content from the image.
    Only using the 4o-mini vision, but you can try whatever model you want.
    There is some speculation Openai is using the same model either way
    Read more here: https://platform.openai.com/docs/guides/vision

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

def get_new_name(image_content: str) ->str:
    """
    Use ChatGPT to generate a new name based on the image content.
    You can tweak the user prompt to be more specific or different tone.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates concise, descriptive filenames based on image content."},
            {"role": "user", "content": f"Generate a concise filename (without extension) for an image with this content: {image_content}"}
        ]
    )
    return response.choices[0].message.content.strip()

def add_metadata(image_path: str, content: str) -> str:
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

def is_screenshot(filename: str) -> bool:
    """
    Check if filename is likely to be a screenshot.
    To research, does the image contain a meta tag if it came from the system screenshot tool?

    Created a method for all the types of formats the screenshot file name apears
    I've seen: Screen shot
        Screenshot
    And I am sure there are many more.
    Windows looks to do Screenshot with their snip tool
    OSX as well.

    Args:
        filename(str): the filename to check
    
    Returns:
        bool: True if the file is likely a screenshot, false if not
    """
    # Convert to lowercase and remove all whitespace
    clean_name = re.sub(r'\s+', '', filename.lower())
    
    # Check if it ends with .png
    if not clean_name.endswith('.png'):
        return False
    
    #list of indicators add what your tool of choice does here
    screenshot_indicators = ['screenshot', 'screen_shot', 'screenclip', 'capture', 'snip']
    
    # Check if any of the indicators are in the cleaned filename
    return any(indicator in clean_name for indicator in screenshot_indicators)

def process_screenshots(folder_path: str) -> str:
    """
    Process all screenshots in the given folder.

    Args:
    folder_path (str): Path to the folder containing screenshots.
    """
    for filename in os.listdir(folder_path):
        if is_screenshot(filename):
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