import base64

from flask import Flask, render_template, request,  render_template_string

app = Flask(__name__)



@app.route('/')
def index():  # put application's code here
    return render_template('index.html')

@app.route('/aut')
def authors():
    import calibre.opds as opds
    opds.gather_catalogs()
    authors_catalog = opds.GLOBAL_DATA["Authors"]
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

@app.route('/author/<string:encoded_id>')
def author_page(encoded_id):
    # Decode the Base64-encoded ID
    decoded_id = base64.b64decode(encoded_id).decode('utf-8')
    # Proceed with using decoded_id to fetch author data
    return render_template('author.html', author_id=decoded_id)


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
