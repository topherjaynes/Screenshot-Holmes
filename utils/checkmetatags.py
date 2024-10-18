import os
from PIL import Image

def read_metadata_from_folder(folder_path: str):
    """
    Read metadata from all PNG files in the specified folder.
    Prints the image name and metadata description to the terminal.
    """
    try:
        for filename in os.listdir(folder_path):
            if filename.lower().endswith('.png'):
                file_path = os.path.join(folder_path, filename)
                with Image.open(file_path) as img:
                    metadata = img.info
                    description = metadata.get("Description", "No description found")
                    print(f"Image: {filename}\nDescription: {description}\n")

    except Exception as e:
        print(f"Error reading metadata from images: {str(e)}")


# Example usage:
folder_path = '/Users/username/Desktop/'  # Replace with your folder path
read_metadata_from_folder(folder_path)
