alias gen := generate-website

# Set the image name
export IMAGE_NAME := "electric-toolbox"

generate-website:
	uv run scripts/generate_site.py
	tailwindcss -i resources/tailwind.css -o website/style.css --minify
	# chcon -Rt container_file_t website/

# Run the Podman container
run:
	podman-compose -f docker-compose.yaml up -d

# Stop the Podman container
stop:
	docker compose -f deployment/local/docker-compose.yaml down
