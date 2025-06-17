# Kobobo Project Instructions

## Project Structure

- `src/` - Source code for the Flask application
- `docker/` - Docker configuration files
- `bin/` - Helper scripts for building/running (not in src/)
- `docs/` - Project documentation (not in src/)
- `kobobo.yml` - Docker Compose configuration (IGNORED - contains credentials)

## Helper Scripts in bin/

- `bin/build.sh` - Build Docker image
- `bin/run.sh` - Run Docker container with environment variables
- `bin/dev.sh` - Run in development mode locally

## Docker Information

- **Image name**: `kobobo:latest`
- **Port**: 5055 (both container and host)
- **Required environment variables**:
  - `KOBOBO_CALIBRE_URL` - URL to Calibre OPDS server
  - `KOBOBO_USERNAME` - Calibre username
  - `KOBOBO_PASSWORD` - Calibre password

## Build and Run Commands

```bash
# Build Docker image
docker build -f docker/Dockerfile -t kobobo:latest .

# Run Docker container
docker run --rm -p 5055:5055 \
  -e KOBOBO_CALIBRE_URL="http://your-calibre-server:8090" \
  -e KOBOBO_USERNAME="your-username" \
  -e KOBOBO_PASSWORD="your-password" \
  kobobo:latest
```

## Development Setup

The app requires a Calibre server with OPDS enabled. The application will fail to start if it cannot connect to the Calibre server during initialization.

## Configuration

- Configuration template: `src/config/settings.j2`
- Local config: `src/config/settings.ini` (gitignored)
- Example config: `src/config/settings.ini.example`

## Important Files to Remember

- `kobobo.yml` is in .gitignore (contains credentials)
- Helper scripts go in `bin/` directory at project root
- Documentation goes in `docs/` directory at project root
- Never put helper scripts or docs in `src/` directory