"""
Downloads blueprint for book downloads and file serving
"""
import os
import subprocess
import tempfile
from io import BytesIO
from urllib.parse import quote

from flask import Blueprint, abort, send_file
from requests.auth import HTTPDigestAuth
import requests

from calibre.cache import GlobalCache
from config import Config
from utils.file_utils import sanitize_string, create_ebook_filename

downloads_bp = Blueprint('downloads', __name__)

@downloads_bp.route('/download/<string:book_id>', methods=['GET'])
def download_book(book_id):
    """Download and convert book to KEPUB format"""
    book = GlobalCache().get_book(book_id)
    if not book:
        abort(404, description="Book not found")
    
    c = Config()
    url = f'{book.epub_link}'

    try:
        # Fetch the book from Calibre server
        response = requests.get(f'{c.opds_url_root}/{url}', 
                              auth=HTTPDigestAuth(c.username, c.password))
        response.raise_for_status()
    except requests.RequestException as e:
        print(f'Error fetching book: {e}')
        abort(404, description="Book not found on server")
    
    file_data = BytesIO()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        epub_path = os.path.join(temp_dir, 'book.epub')
        output_path = os.path.join(temp_dir, 'book_converted.kepub.epub')

        # Save original EPUB
        with open(epub_path, 'wb') as epub_file:
            epub_file.write(response.content)
        
        # Convert to KEPUB using kepubify
        kepubify_bin = c.kepubify
        cmd_list = [kepubify_bin, "--smarten-punctuation", epub_path]
        
        try:
            subprocess.run(cmd_list, cwd=temp_dir, check=True, 
                         capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f'Error during conversion: {e}')
            print(f'stdout: {e.stdout}')
            print(f'stderr: {e.stderr}')
            abort(500, description="Book conversion failed")

        if not os.path.exists(output_path):
            abort(500, description=f"Converted file not found at {output_path}")
        
        # Read converted file
        with open(output_path, 'rb') as temp_file:
            file_data.write(temp_file.read())

        file_data.seek(0)
        download_name = create_ebook_filename(book.author, book.title, book.year)
        
        response = send_file(file_data,
                           as_attachment=True,
                           mimetype='application/epub+zip',
                           download_name=download_name)
        
        # Set proper headers for download
        headers = response.headers
        encoded_filename = quote(download_name)
        headers["Content-Disposition"] = (
            f"attachment; filename=\"{download_name}\"; "
            f"filename*=UTF-8''{encoded_filename}"
        )
        
        return response

@downloads_bp.route('/cover/<int:cover_id>')
def get_cover(cover_id):
    """Serve book cover images from Calibre server"""
    c = Config()
    url = f'/get/cover/{cover_id}/calibre'

    try:
        response = requests.get(f'{c.opds_url_root}/{url}', 
                              auth=HTTPDigestAuth(c.username, c.password))
        response.raise_for_status()
    except requests.RequestException as e:
        print(f'Error fetching cover: {e}')
        abort(404, description="Cover image not found")

    content_type = response.headers.get('Content-Type', 'image/jpeg')
    image_data = BytesIO(response.content)
    
    return send_file(image_data, mimetype=content_type)