import os


"""
Quick util to be able to scan through your desktop or folder all your screenshots go to to understand how man you have
Just update the desktop folder path for your system.

Future update, give a csv of all the png file paths as well as estimate how much it will cost to use 4o-vision
"""
def count_screenshot_pngs(directory):
    count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.png'):
                name_without_extension = os.path.splitext(file)[0].lower()
                print(name_without_extension)
                if 'screenshot' in name_without_extension or 'screen shot' in name_without_extension:
                    count += 1
    return count

# Replace this with the path to your desktop folder default to just look through your users file
desktop_path = os.path.expanduser("/Users/")
#desktop_path = os.path.expanduser("/Users/{yourusername}/")

#windows machines:


total_screenshots = count_screenshot_pngs(desktop_path)
print(f"Total number of screenshot PNGs found: {total_screenshots}")