alias gen := generate-website

# Set the image name
export IMAGE_NAME := "electric-toolbox"

generate-website:
	uv run scripts/generate_site.py
	tailwindcss -i resources/tailwind.css -o website/style.css --minify

runlocal:
    bash -c "python deployment/local/app.py; exec bash"
    bash -c "tailwindcss -i resources/tailwind.css -o website/style.css --minify --watch; exec bash" & \
