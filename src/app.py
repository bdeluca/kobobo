"""
Kobobo Flask Application
A clean e-reader interface for Calibre OPDS servers
"""
import logging
from waitress import serve
import calibre.opds as opds
from app_factory import create_app
from utils.app_utils import download_kepublify, is_docker

def init():
    """Initialize application dependencies"""
    if is_docker():
        download_kepublify()
        print("Docker server is probably available at http://127.0.0.1:5055")
    opds.gather_catalogs()

# Create Flask app using factory pattern
app = create_app()

# Initialize on module load
init()

if __name__ == '__main__':
    print('Starting server...')
    
    # Configure the Waitress logger
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.DEBUG)
    
    port = 5055
    serve(app, listen=[f"0.0.0.0:{port}"])
    print('Done')