import base64
import os
import subprocess
import tempfile
from io import BytesIO

import requests
from flask import Flask, render_template, request,  render_template_string, abort, send_file
from requests.auth import HTTPDigestAuth

import calibre.opds
from  calibre.cache import GlobalCache
import calibre.opds as opds
from config import Config

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

def create_ebook_filename(author_name, book_title, year, extension='epub'):
    # Sanitize each component
    sanitized_author = sanitize_string(author_name)
    sanitized_title = sanitize_string(book_title)
    # Format the filename
    filename = f"{sanitized_author}-{sanitized_title}-{year}.{extension}"
    return filename


@app.route('/download/<string:book_id>')
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
        output_path = os.path.join(temp_dir, 'book_converted.kepub')

        with open(epub_path, 'wb') as epub_file:
            epub_file.write(response.content)
        kpubbin = c.kepubify
        cmd_list = [kpubbin,  "--calibre", "--smarten-punctuation", epub_path ]
        print(" ".join(cmd_list))
        try:
            result = subprocess.run(cmd_list, cwd =temp_dir, check=True,capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f'Error during conversion: {e}')
            print(e.stdout)
            print('Standard Error:', e.stderr)
            abort(500, description="Conversion failed")

        if not os.path.exists(output_path):
            abort(500, description="Converted file not found")
        with open(output_path, 'rb') as temp_file:
            file_data.write(temp_file.read())

        # Move the pointer to the beginning of the BytesIO object
        file_data.seek(0)

        return send_file(file_data,
                         as_attachment=True,
                         mimetype='application/x-kepub+zip',
                         download_name=create_ebook_filename(book.author, book.title, book.published_date[:4]))
   
@app.route('/authors')
def authors():
    opds.gather_catalogs()
    authors_catalog = GlobalCache().get_catalog("Authors")
    authors_catalog.gather()
    author_dict  = authors_catalog.authors
    letter_dict = {}
    for author in author_dict.values():
        initial = author.name[0].upper()  # Get the first letter of each name
        if initial not in letter_dict:
            letter_dict[initial] = []
        letter_dict[initial].append(author)
    letters = sorted(letter_dict.keys())

    return render_template('authors.html',  letter_dict=letter_dict, letters=letters)


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


def init():
    calibre.opds.gather_catalogs()

init()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
