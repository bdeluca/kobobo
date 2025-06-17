import base64
import logging
import os
import subprocess
import tempfile
from io import BytesIO

import requests
from flask import Flask, render_template, request,  render_template_string, abort, send_file
from waitress import serve
from requests.auth import HTTPDigestAuth

from  calibre.cache import GlobalCache
import calibre.opds as opds
from config import Config
import calibre

app = Flask(__name__)

@app.route('/')
def index():  # put application's code here
    recent_books = GlobalCache().get_catalog("Newest")
    recent_books = recent_books.books
    return render_template('index.html', recent_books= recent_books[:8])

@app.route('/book/<string:book_id>')
def book_detail(book_id):
    book = GlobalCache().get_book(book_id)
    # For now, render an empty page or a placeholder template
    return render_template('book.html', book= book)

import unicodedata
import re

def sanitize_string(input_str):
    # Normalize the string to decompose special characters
    normalized_str = unicodedata.normalize('NFKD', input_str)
    # Encode to ASCII bytes, ignoring errors, then decode back to string
    ascii_str = normalized_str.encode('ASCII', 'ignore').decode('ASCII')
    # Replace any non-alphanumeric characters with underscores
    sanitized_str = re.sub(r'[^a-zA-Z0-9]+', '_', ascii_str)
    # Remove leading and trailing underscores
    sanitized_str = sanitized_str.strip('_')
    return sanitized_str

def create_ebook_filename(author_name, book_title, year):
    # Sanitize each component
    sanitized_author = sanitize_string(author_name)
    sanitized_title = sanitize_string(book_title)
    # Format the filename
    filename = f"{sanitized_author}-{sanitized_title}[{year}].kepub.epub"
    return filename


@app.route('/download/<string:book_id>', methods=['GET'])
def download_book(book_id):
    book = GlobalCache().get_book(book_id)
    c = Config()
    # Construct the URL to fetch the image from the external server
    url = f'{book.epub_link}'

    try:
        # Fetch the image from the external server
        response = requests.get(f'{c.opds_url_root}/{url}', auth=HTTPDigestAuth(c.username, c.password))
        response.raise_for_status()  # Raise an HTTPError for bad responses
    except requests.RequestException as e:
        # Log the error if needed
        print(f'Error fetching image: {e}')
        # Return a 404 error if the image cannot be fetched
        abort(404, description="Cover image not found")
    file_data = BytesIO()
    with tempfile.TemporaryDirectory() as temp_dir:
        epub_path = os.path.join(temp_dir, 'book.epub')
        output_path = os.path.join(temp_dir, 'book_converted.kepub.epub')

        with open(epub_path, 'wb') as epub_file:
            epub_file.write(response.content)
        kpubbin = c.kepubify
        cmd_list = [kpubbin,  "--smarten-punctuation", epub_path ]
        try:
            subprocess.run(cmd_list, cwd =temp_dir, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f'Error during conversion: {e}')
            print(e.stdout)
            print('Standard Error:', e.stderr)
            abort(500, description="Conversion failed")

        if not os.path.exists(output_path):
            abort(500, description=f"Converted file not found {output_path}")
        with open(output_path, 'rb') as temp_file:
            file_data.write(temp_file.read())

        # Move the pointer to the beginning of the BytesIO object
        file_data.seek(0)
        download_name = create_ebook_filename(book.author, book.title, book.year)
        response =  send_file(file_data,
                         as_attachment = True,
                         mimetype='application/epub+zip',
                         download_name  = download_name
                         )
        headers = response.headers
        from urllib.parse import quote
        encoded_filename = quote(download_name)
        headers[
            "Content-Disposition"] = f"attachment; filename=\"{download_name}\"; filename*=UTF-8''{encoded_filename}"

        print(headers)
        return response
   
@app.route('/authors')
def authors():
    authors_catalog = GlobalCache().get_catalog("Authors")
    author_dict  = authors_catalog.authors
    letter_dict = {}
    for author in author_dict.values():
        initial = author.name[0].upper()  # Get the first letter of each name
        if initial not in letter_dict:
            letter_dict[initial] = []
        letter_dict[initial].append(author)
    letters = sorted(letter_dict.keys())

    return render_template('authors.html',  letter_dict=letter_dict, letters=letters)


@app.route('/series')
def series():
    series_dict = GlobalCache().series
    letter_dict = {}
    for series_title in series_dict.keys():
        initial = series_title[0].upper()  # Get the first letter of each name
        if initial not in letter_dict:
            letter_dict[initial] = []
        letter_dict[initial].append(series_title)
    letters = sorted(letter_dict.keys())

    return render_template('series.html',  letter_dict=letter_dict, letters=letters, series=series_dict)


@app.route('/cover/<int:cover_id>')
def get_cover(cover_id):
    c = Config()
    # Construct the URL to fetch the image from the external server
    url = f'/get/cover/{cover_id}/calibre'

    try:
        # Fetch the image from the external server
        response = requests.get(f'{c.opds_url_root}/{url}', auth=HTTPDigestAuth(c.username, c.password))
        response.raise_for_status()  # Raise an HTTPError for bad responses
    except requests.RequestException as e:
        # Log the error if needed
        print(f'Error fetching image: {e}')
        # Return a 404 error if the image cannot be fetched
        abort(404, description="Cover image not found")

    # Determine the content type from the response headers
    content_type = response.headers.get('Content-Type', 'image/jpeg')

    # Create a BytesIO object from the response content
    image_data = BytesIO(response.content)

    # Return the image file
    return send_file(image_data, mimetype=content_type)

@app.route('/author/<string:encoded_id>')
def author_page(encoded_id):
    # Decode the Base64-encoded ID
    decoded_id = base64.b64decode(encoded_id).decode('utf-8')
    # Proceed with using decoded_id to fetch author data

    opds.gather_catalogs()
    authors_catalog = GlobalCache().get_catalog("Authors")
    authors_catalog.gather()
    author_dict = authors_catalog.authors
    author = author_dict.get(decoded_id)
    author.gather()
    c = Config()
    calibre_root = c.opds_url_root
    return render_template('author.html', author=author, calibre_root=calibre_root)


@app.route('/debug/series')
def debug_series():
    series_dict = GlobalCache().series
    debug_info = []
    
    for series_name, books in list(series_dict.items())[:10]:  # Limit to first 10 for readability
        book_info = []
        for position, book in sorted(books.items()):
            book_info.append(f"Position {position}: {book.title}")
        debug_info.append({
            'series_name': series_name,
            'books': book_info
        })
    
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Series Debug</title>
        </head>
        <body>
            <h1>Series Debug Information</h1>
            <p>Total series: {{ total_series }}</p>
            {% for series in debug_info %}
            <h3>{{ series.series_name }}</h3>
            <ul>
            {% for book in series.books %}
                <li>{{ book }}</li>
            {% endfor %}
            </ul>
            {% endfor %}
        </body>
        </html>
    ''', debug_info=debug_info, total_series=len(series_dict))

@app.route('/binfo')
def binfo():
    user_agent = request.headers.get('User-Agent')
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Browser Information</title>
        </head>
        <body>
            <h1>Browser Information</h1>
            <p>User Agent: {{ user_agent }}</p>
        </body>
        </html>
    ''', user_agent=user_agent)


def download_kepublify():
    import os
    import requests
    import shutil
    import stat

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
    st = os.stat(destination_path)
    os.chmod(destination_path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def is_docker():
    return os.path.exists('/.dockerenv')

def init():
    if is_docker():
        download_kepublify()
        print("Docker server is probably available at http://127.0.0.1:5055")
    calibre.opds.gather_catalogs()


init()

if __name__ == '__main__':
    print('Starting server...')
    # Configure the Waitress logger
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.DEBUG)  # Set to DEBUG for detailed output
    port = 5055
    # app.run(host='0.0.0.0', port=5000, debug=True)
    serve(app, listen=[f"0.0.0.0:{port}"])
    print('Done')
