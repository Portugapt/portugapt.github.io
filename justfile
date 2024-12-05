alias gen := generate

generate:
    uv run scripts/generate_site.py
    tailwindcss -i resources/tailwind.css -o website/style.css --minify