alias gen := generate-website

# Set the image name
export IMAGE_NAME := "electric-toolbox"

generate-website:
	uv run scripts/generate_site.py
	tailwindcss -i resources/tailwind.css -o website/style.css --minify

watch-tailwind:
    tailwindcss -i resources/main.css -o website/style.css --minify --watch

local-server:
    python deployment/local/app.py
