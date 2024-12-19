"""App to serve the website."""

import os

from flask import Flask, Response, render_template, send_from_directory
from livereload import Server, shell  # type: ignore

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

    # Watch for changes in content and regenerate the website
    server.watch(
        content_dir,
        shell(
            'uv run scripts/generate_site.py',
            output=None,  # No specific output file
        ),
    )

    # Watch for changes in src and regenerate the website
    server.watch(
        src_dir,
        shell(
            'uv run scripts/generate_site.py',
            output=None,  # No specific output file
        ),
    )
    server.serve(host='0.0.0.0', port=8080, debug=True)  # noqa: S104
