import os
import re
import csv
import base64
from typing import Tuple
from io import BytesIO
from PIL import Image
from PIL.PngImagePlugin import PngInfo
from openai import OpenAI
from dotenv import load_dotenv
import time
from datetime import datetime

# Load environment variables
load_dotenv()

# Set up OpenAI client
client = OpenAI()


'''
This encodes the image in base64 to send to openai api
Also check if a the user wants to save tokens and will cut the image in half
We could make it a feature flag on the size to cut. 
'''
def encode_image(image_path: str, resize: bool = False) -> str:
    with Image.open(image_path) as img:
        original_width, original_height = img.size
        if resize:
            # Check if both dimensions will be at least 512 after resizing
            if original_width * 0.5 >= 512 and original_height * 0.5 >= 512:
                new_width = int(original_width * 0.5)
                new_height = int(original_height * 0.5)
                img = img.resize((new_width, new_height), Image.LANCZOS)
                print(f"Resized image for API: {image_path} from {original_width}x{original_height} to {new_width}x{new_height}")
            else:
                print(f"Image not resized for API: {image_path} (one or both dimensions would be below 512 pixels)")
        
        # Save the image to a BytesIO object
        buffered = BytesIO()
        img.save(buffered, format="PNG")
    
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def get_image_content(image_path: str, resize: bool = False) -> Tuple[str, dict]:
    
    """
    Use OpenAI's vision capabilities to extract content from the image.
    Only using the 4o-mini vision, but you can try whatever model you want.
    There is some speculation Openai is using the same model either way
    Read more here: https://platform.openai.com/docs/guides/vision

    """
    base64_image = encode_image(image_path, resize)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI assistant specialized in analyzing screenshots and generating "
                        "descriptive filenames for archival purposes. Your task is to examine the provided image, describe its "
                        "content concisely"
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this image and provide: 1) A concise description of its content"
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
        max_tokens=3000
    )
    
    content = response.choices[0].message.content.strip()
    usage_info = {
        'prompt_tokens': response.usage.prompt_tokens,
        'completion_tokens': response.usage.completion_tokens,
        'total_tokens': response.usage.total_tokens
    }
    
    return content, usage_info


def get_new_name(image_content: str) ->str:
    """
    Use ChatGPT to generate a new name based on the image content.
    You can tweak the user prompt to be more specific or different tone.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful archival assistant that generates descriptive filenames based on image content. You generate descriptive names to \
             easily understand whats in the file quickly scroll through folders"},
            {"role": "user", "content": f"Generate a concise filename (without extension) for an image with this content: {image_content}"}
        ]
    )
    return response.choices[0].message.content.strip()

def add_metadata(image_path: str, content: str) -> str:
    """
    Add metadata to the image file using Pillow.
    """
    print(content)
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

def process_screenshots(folder_path: str, resize_for_api: bool = False) -> list:
    processed_files = []
    for filename in os.listdir(folder_path):
        if is_screenshot(filename):
            file_path = os.path.join(folder_path, filename)
            
            try:
                content, usage_info = get_image_content(file_path, resize=resize_for_api)
                new_name = get_new_name(content)
                add_metadata(file_path, content)
                new_file_path = os.path.join(folder_path, f"{new_name}.png")
                os.rename(file_path, new_file_path)
                
                processed_files.append({
                    'original_path': file_path,
                    'new_name': f"{new_name}.png",
                    'description': content,
                    'prompt_tokens': usage_info['prompt_tokens'],
                    'total_tokens': usage_info['total_tokens']
                })
                
                print(f"Processed: {filename} -> {new_name}.png")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
    
    return processed_files

"""
Tracking what the old name was, the new name, the content, and the tokens used from openAI
"""
def write_to_csv(processed_files: list, output_folder: str) -> None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = os.path.join(output_folder, f"processed_files_{timestamp}.csv")
    
    with open(csv_filename, 'w', newline='') as csvfile:
        fieldnames = ['original_path', 'new_name', 'description', 'prompt_tokens', 'total_tokens']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for file in processed_files:
            writer.writerow(file)
    
    print(f"CSV file created: {csv_filename}")         


def main():
    folder_path = "/Users/topherjaynes/Desktop/screenshot/testshots"
    output_folder = "/Users/topherjaynes/Desktop/screenshot/output"
    resize_for_api = True  # Set this to False if you don't want to resize images for API
    
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    processed_files = process_screenshots(folder_path, resize_for_api=resize_for_api)
    write_to_csv(processed_files, output_folder)

if __name__ == "__main__":
    main()
