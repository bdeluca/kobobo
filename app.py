import base64
from io import BytesIO

import requests
from flask import Flask, render_template, request,  render_template_string, abort, send_file
from requests.auth import HTTPDigestAuth

import calibre.opds as opds
from config import Config

app = Flask(__name__)

@app.route('/')
def index():  # put application's code here
    return render_template('index.html')


@app.route('/authors')
def authors():
    opds.gather_catalogs()
    authors_catalog = opds.GlobalCache().get_catalog("Authors")
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
    authors_catalog = opds.GlobalCache().get_catalog("Authors")
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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
