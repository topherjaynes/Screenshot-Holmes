import os
import platform
import math
import csv
from PIL import Image  # Ensure Pillow is installed: pip install Pillow

"""
Utility to scan through a specified directory for PNG screenshots,
analyze them, and estimate the cost of processing with 40-mini vision API.

Features:
- Automatically detects the desktop path based on the operating system.
- Analyzes PNG files containing 'screenshot' or 'screen shot' in their names.
- Calculates the number of tiles based on image dimensions (original and halved).
- Estimates tokens and costs for both original and halved image sizes.
- Generates a CSV report with detailed information.
- Provides a summary of total costs and savings.
"""

# Constants for token pricing
PRICE_PER_MILLION_TOKENS = 0.15
BASE_TOKENS_PER_IMAGE = 2833
TILE_TOKENS = 5667
TILE_SIZE_PIXELS = 512  # 512x512 tiles

def analyze_screenshot_pngs(directory):
    """
    Scans the specified directory for PNG files that are screenshots.

    Args:
        directory (str): The directory path to scan.

    Returns:
        list of dict: A list containing information about each screenshot.
    """
    screenshot_data = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.png'):
                name_without_extension = os.path.splitext(file)[0].lower()
                if 'screenshot' in name_without_extension or 'screen shot' in name_without_extension:
                    file_path = os.path.join(root, file)
                    try:
                        with Image.open(file_path) as img:
                            width, height = img.size
                    except Exception as e:
                        print(f"Error opening image {file_path}: {e}")
                        continue
                    size_bytes = os.path.getsize(file_path)
                    screenshot_data.append({
                        'file_path': file_path,
                        'width_px': width,
                        'height_px': height,
                        'size_bytes': size_bytes
                    })
    return screenshot_data

def get_desktop_path():
    """
    Automatically detects the desktop path based on the operating system.

    Returns:
        str: The path to the desktop directory.

    Raises:
        OSError: If the operating system is unsupported.
    """
    system = platform.system()
    if system == 'Windows':
        return os.path.join(os.path.expanduser('~'), 'Desktop')
    elif system in ['Darwin', 'Linux']:  # macOS and Linux
        return os.path.expanduser('~/Desktop')
    else:
        raise OSError(f"Unsupported operating system: {system}")

def determine_tiles(width, height, tile_size=TILE_SIZE_PIXELS):
    """
    Determines the number of 512x512 tiles needed for an image.

    Args:
        width (int): Image width in pixels.
        height (int): Image height in pixels.
        tile_size (int, optional): Size of each tile in pixels. Defaults to 512.

    Returns:
        int: Number of tiles required.
    """
    tiles_x = math.ceil(width / tile_size)
    tiles_y = math.ceil(height / tile_size)
    return tiles_x * tiles_y

def calculate_tokens_per_image(tiles):
    """
    Calculates the total tokens required for an image based on the number of tiles.

    Args:
        tiles (int): Number of tiles for the image.

    Returns:
        int: Total tokens for the image.
    """
    return BASE_TOKENS_PER_IMAGE + (TILE_TOKENS * tiles)

def calculate_cost(total_tokens):
    """
    Calculates the cost based on the total number of tokens.

    Args:
        total_tokens (int): Total tokens consumed.

    Returns:
        float: Estimated cost in USD.
    """
    return (total_tokens / 1_000_000) * PRICE_PER_MILLION_TOKENS

def generate_csv_report(screenshot_data, output_path='screenshot_analysis.csv'):
    """
    Generates a CSV report with detailed information about each screenshot.

    Args:
        screenshot_data (list of dict): List containing image information.
        output_path (str, optional): Path to save the CSV file. Defaults to 'screenshot_analysis.csv'.
    """
    headers = [
        'File Path',
        'Width (px)',
        'Height (px)',
        'Size (KB)',
        'Original Tiles',
        'Original Tokens',
        'Original Cost (USD)',
        'Halved Width (px)',
        'Halved Height (px)',
        'Halved Tiles',
        'Halved Tokens',
        'Halved Cost (USD)',
        'Savings (USD)'
    ]
    with open(output_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        for data in screenshot_data:
            writer.writerow([
                data['file_path'],
                data['width_px'],
                data['height_px'],
                f"{data['size_bytes'] / 1024:.2f}",
                data['original_tiles'],
                data['original_tokens'],
                f"{data['original_cost']:.6f}",
                data['halved_width_px'],
                data['halved_height_px'],
                data['halved_tiles'],
                data['halved_tokens'],
                f"{data['halved_cost']:.6f}",
                f"{data['savings']:.6f}"
            ])
    print(f"CSV report generated at: {output_path}")

def estimate_costs_and_savings(screenshot_data):
    """
    Estimates costs for original and halved image sizes and calculates savings.

    Args:
        screenshot_data (list of dict): List containing image information.

    Returns:
        tuple: Total original cost, total halved cost, total savings.
    """
    total_original_cost = 0
    total_halved_cost = 0

    for data in screenshot_data:
        # Original image calculations
        original_tiles = determine_tiles(data['width_px'], data['height_px'])
        original_tokens = calculate_tokens_per_image(original_tiles)
        original_cost = calculate_cost(original_tokens)

        # Halved image calculations
        halved_width = max(1, data['width_px'] // 2)  # Avoid zero dimension
        halved_height = max(1, data['height_px'] // 2)
        halved_tiles = determine_tiles(halved_width, halved_height)
        halved_tokens = calculate_tokens_per_image(halved_tiles)
        halved_cost = calculate_cost(halved_tokens)

        # Savings calculation
        savings = original_cost - halved_cost

        # Update totals
        total_original_cost += original_cost
        total_halved_cost += halved_cost

        # Update data dictionary with new fields
        data.update({
            'original_tiles': original_tiles,
            'original_tokens': original_tokens,
            'original_cost': original_cost,
            'halved_width_px': halved_width,
            'halved_height_px': halved_height,
            'halved_tiles': halved_tiles,
            'halved_tokens': halved_tokens,
            'halved_cost': halved_cost,
            'savings': savings
        })

    total_savings = total_original_cost - total_halved_cost
    return total_original_cost, total_halved_cost, total_savings

def main():
    """
    Main function to execute the analysis and cost estimation.
    """
    # Get the appropriate desktop path based on the OS
    try:
        desktop_path = get_desktop_path()
        print(f"Detected desktop path: {desktop_path}")
    except OSError as e:
        print(f"Error: {e}")
        desktop_path = input("Please enter the path to your desktop folder manually: ")

    # Analyze screenshots
    screenshot_data = analyze_screenshot_pngs(desktop_path)
    total_screenshots = len(screenshot_data)
    total_size_bytes = sum([data['size_bytes'] for data in screenshot_data])

    if total_screenshots == 0:
        print("No screenshot PNGs found.")
        return

    # Estimate costs and savings
    total_original_cost, total_halved_cost, total_savings = estimate_costs_and_savings(screenshot_data)

    # Generate CSV report
    generate_csv_report(screenshot_data)

    # Print summary
    print(f"\nTotal number of screenshot PNGs found: {total_screenshots}")
    print(f"Total size of screenshot PNGs: {total_size_bytes / (1024 * 1024):.2f} MB")
    print(f"Total original cost to analyze with 40-mini vision: ${total_original_cost:.6f}")
    print(f"Total cost at half size:                      ${total_halved_cost:.6f}")
    print(f"Estimated total savings:                      ${total_savings:.6f}")

if __name__ == "__main__":
    main()
