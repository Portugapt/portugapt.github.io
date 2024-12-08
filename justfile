alias gen := generate-website

# Set the image name
export IMAGE_NAME := "electric-toolbox"

generate-website:
	uv run scripts/generate_site.py
	tailwindcss -i resources/tailwind.css -o website/style.css --minify

# Run the Podman container
run:
	podman-compose -f deployment/local/docker-compose.yaml up -d

# Stop the Podman container
stop:
	podman-compose -f deployment/local/docker-compose.yaml down
