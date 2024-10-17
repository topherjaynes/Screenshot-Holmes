# Screenshot Holmes

Sometimes you have to be Sherlock Holmes to find that screenshot you just took. Enter Screenshot Holmes, your digital detective for image organization.

## Introduction

Screenshot Holmes is a Python-based tool designed to bring order to the chaos of your screenshot collection. Just as the famous detective could deduce a person's life story from a mere glance, our tool analyzes your images to understand their content, helping you locate and organize your visual information with unprecedented ease.

## What does Screenshot Holmes do?

Our digital detective employs state-of-the-art AI to investigate your screenshots:

1. **Analyze**: Uses advanced image recognition to understand the content of each screenshot.
2. **Rename**: Generates descriptive filenames based on the image content, making it easier to find what you need.
3. **Organize**: Adds relevant metadata to each file, enhancing searchability and organization.
4. **Deduce**: Helps you quickly locate specific screenshots based on their content, not just when they were taken.

Whether you're a professional dealing with numerous screenshots daily or someone who occasionally needs to find that one important capture, Screenshot Holmes is here to streamline your workflow and save you valuable time.

## Features

- Scans a specified folder for PNG screenshots
- Uses OpenAI's GPT-4 Vision API to analyze image content
- Generates descriptive filenames based on image content
- Adds content description as metadata to PNG files
- Renames files with AI-generated names

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.7 or higher
- An OpenAI API key with access to the GPT-4 Vision API

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/screenshot-organizer.git
   cd screenshot-organizer
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install openai python-dotenv Pillow
   ```

## Configuration

1. Create a `.env` file in the project root directory.
2. Add your OpenAI API key to the `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

1. Open the `app.py` file and set the `folder_path` variable to the directory containing your screenshots.

2. Run the script:
   ```
   python app.py
   ```

The script will process all PNG files in the specified folder that have "screenshot" in their filename. It will analyze each image, generate a new name, add metadata, and rename the file.

## Customization

You can modify the `process_screenshots` function in `app.py` to change the file selection criteria or add support for additional file formats.

## Contributing

Contributions to this project are welcome. Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).

## Contact

If you have any questions or feedback, please contac [chris.jaynes@gmail.com] or submit a pr.
