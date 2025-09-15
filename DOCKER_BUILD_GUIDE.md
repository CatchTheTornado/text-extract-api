# GitHub Actions Docker Build Guide

This guide explains how to set up automated Docker image building for the text-extract-api project on GitHub.

## Overview

The repository now includes:
- Production-ready Dockerfiles (`Dockerfile` and `Dockerfile.gpu`)
- GitHub Actions workflow for automated building and publishing
- Multi-architecture support (AMD64 and ARM64)
- Automatic tagging and versioning

## What Gets Built

### Docker Images

1. **Standard Image** (`ghcr.io/catchthetornado/text-extract-api:latest`)
   - Built from `Dockerfile`
   - Supports both AMD64 and ARM64 architectures
   - CPU-only processing

2. **GPU Image** (`ghcr.io/catchthetornado/text-extract-api-gpu:latest`)
   - Built from `Dockerfile.gpu`
   - AMD64 architecture only
   - CUDA 11.8 support for GPU processing

### Triggers

The workflow runs on:
- **Push to main branch** → Builds and pushes `latest` images
- **Push to develop branch** → Builds and pushes `develop` images  
- **Git tags** (v*) → Builds and pushes versioned images (e.g., `v1.0.0`)
- **Pull requests** → Builds images for testing (no push)

## Setup Instructions

### 1. Enable GitHub Container Registry

1. Go to your repository settings
2. Navigate to **Actions** → **General**
3. Ensure "Read and write permissions" are enabled for GitHub Token

### 2. Repository Settings

The workflow uses the GitHub Container Registry (ghcr.io) which requires:
- Repository must be public OR
- GitHub Pro/Team account for private repositories

### 3. Environment Variables (Optional)

You can customize the build by setting repository secrets:

```bash
# Optional: Custom registry (defaults to ghcr.io)
REGISTRY=your-registry.com

# Optional: Custom image name (defaults to repository name)
IMAGE_NAME=custom-image-name
```

## Usage Examples

### Pull the Latest Images

```bash
# Standard CPU image
docker pull ghcr.io/catchthetornado/text-extract-api:latest

# GPU-enabled image  
docker pull ghcr.io/catchthetornado/text-extract-api-gpu:latest
```

### Run with Docker Compose

Update your `docker-compose.yml` to use the pre-built images:

```yaml
services:
  fastapi_app:
    image: ghcr.io/catchthetornado/text-extract-api:latest
    # Remove the 'build' section
    ports:
      - "8000:8000"
    # ... rest of your configuration

  celery_worker:
    image: ghcr.io/catchthetornado/text-extract-api:latest
    # Remove the 'build' section  
    # ... rest of your configuration
```

### Run Specific Versions

```bash
# Run a specific version
docker pull ghcr.io/catchthetornado/text-extract-api:v1.0.0

# Run development version
docker pull ghcr.io/catchthetornado/text-extract-api:develop
```

## Image Tags

The workflow creates multiple tags automatically:

| Event | Tags Created | Example |
|-------|-------------|---------|
| Push to main | `latest` | `ghcr.io/catchthetornado/text-extract-api:latest` |
| Push to develop | `develop` | `ghcr.io/catchthetornado/text-extract-api:develop` |
| Git tag `v1.2.3` | `v1.2.3`, `v1.2`, `v1` | `ghcr.io/catchthetornado/text-extract-api:v1.2.3` |
| Pull request | `pr-123` | `ghcr.io/catchthetornado/text-extract-api:pr-123` |

## Architecture Support

| Image | AMD64 | ARM64 | Notes |
|-------|-------|-------|-------|
| Standard | ✅ | ✅ | Works on Intel/AMD and Apple Silicon |
| GPU | ✅ | ❌ | CUDA requires AMD64 architecture |

## Monitoring Build Status

1. Go to your repository's **Actions** tab
2. Click on the latest workflow run
3. Monitor the build progress for both image variants

## Troubleshooting

### Build Failures

Common issues and solutions:

1. **Permission Denied**
   - Check repository permissions in Settings → Actions
   - Ensure "Read and write permissions" are enabled

2. **Out of Disk Space**
   - The workflow includes layer caching to minimize build time
   - Large builds may occasionally fail on GitHub's runners

3. **Architecture Issues**
   - ARM64 builds may take longer due to emulation
   - GPU builds are AMD64-only by design

### Testing Images Locally

```bash
# Test the standard image
docker run --rm -p 8000:8000 ghcr.io/catchthetornado/text-extract-api:latest

# Test the GPU image (requires NVIDIA Docker)
docker run --rm --gpus all -p 8000:8000 ghcr.io/catchthetornado/text-extract-api-gpu:latest
```

## Security Features

- **Non-root user**: Images run as `appuser` for security
- **Minimal base**: Uses slim Python images to reduce attack surface
- **Health checks**: Built-in health monitoring endpoint
- **Layer optimization**: Efficient layer caching reduces build times

## Development Workflow

1. **Local Development**: Use `dev.Dockerfile` and `docker-compose.yml`
2. **Testing**: Push to a feature branch → Creates test images
3. **Staging**: Merge to `develop` → Creates develop images  
4. **Production**: Tag a release → Creates versioned images
5. **Production Deploy**: Use `latest` or specific version tags

This setup provides a complete CI/CD pipeline for containerized deployments of your text-extract-api application.