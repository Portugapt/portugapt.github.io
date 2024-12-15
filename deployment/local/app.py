"""App to serve the website."""

import os

from flask import Flask, Response, render_template, send_from_directory
from livereload import Server  # type: ignore

# Get the absolute path to the directory containing app.py
base_dir = os.path.abspath(os.path.dirname(__file__))

# Construct the path to the website folder
website_dir = os.path.join(base_dir, '..', '..', 'website')
src_dir = os.path.join(base_dir, '..', '..', 'src')
content_dir = os.path.join(base_dir, '..', '..', 'content')

app = Flask(
    __name__,
    static_url_path='',
    static_folder=website_dir,
    template_folder=website_dir,
)


@app.route('/')
def index() -> str:
    """Render and return the index page."""
    return render_template('index.html')


@app.route('/<path:filename>')
def serve_static(filename: str) -> Response:
    """Serve static files from the configured static folder."""
    return send_from_directory(app.config['STATIC_FOLDER'], filename)


if __name__ == '__main__':
    server = Server(app.wsgi_app)
    server.watch(src_dir, 'just gen')  # Watch for changes in the 'website' directory
    server.watch(content_dir, 'just gen')  # Watch for changes in the 'website' directory
    server.serve(host='0.0.0.0', port=8080)  # noqa: S104
