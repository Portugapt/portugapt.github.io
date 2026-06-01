alias gen := generate-website

# Set the image name
export IMAGE_NAME := "electric-toolbox"

# Install the bun-managed CSS toolchain (Tailwind v4).
install:
    bun install

# Build the CSS first; generate_site.py inlines build/style.css into each page.
generate-website:
    bun run build:css
    uv run scripts/generate_site.py

watch-tailwind:
    bun run watch:css

local-server:
    python deployment/local/app.py
