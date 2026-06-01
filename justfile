alias gen := generate-website

# Set the image name
export IMAGE_NAME := "electric-toolbox"

# Install the bun-managed CSS toolchain (Tailwind v4).
install:
    bun install

generate-website:
    uv run scripts/generate_site.py
    bun run build:css

watch-tailwind:
    bun run watch:css

local-server:
    python deployment/local/app.py
