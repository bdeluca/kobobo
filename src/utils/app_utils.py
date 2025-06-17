"""
Application utilities for Kobobo
"""
import os
import requests
import shutil
import stat

def download_kepublify():
    """
    Download kepubify tool for EPUB to KEPUB conversion
    Only runs in Docker environment
    """
    # Define the URL and the destination file path
    url = 'https://github.com/pgaskin/kepubify/releases/latest/download/kepubify-linux-64bit'
    destination_path = '/app/bin/kepubify'

    # Check if the file already exists
    if not os.path.exists(destination_path):
        try:
            # Send a GET request to the URL
            with requests.get(url, stream=True) as response:
                response.raise_for_status()  # Check for HTTP errors
                # Ensure the destination directory exists
                os.makedirs(os.path.dirname(destination_path), exist_ok=True)
                # Open the destination file in write-binary mode and save the content
                with open(destination_path, 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
            print(f'File downloaded and saved to {destination_path}')
        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'An error occurred: {err}')
    else:
        print(f'File already exists at {destination_path}')
    
    # Make the file executable
    st = os.stat(destination_path)
    os.chmod(destination_path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

def is_docker():
    """Check if running inside Docker container"""
    return os.path.exists('/.dockerenv')