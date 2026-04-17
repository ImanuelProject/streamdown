# Streamdown

A clean architecture monorepo for a youtube/spotify downloader built with FastAPI, React, and Redis.

## Architecture

- **Backend**: FastAPI + ARQ Worker (Python)
- **Frontend**: React + Vite + Tailwind (TypeScript)
- **Infrastructure**: Docker Compose, Nginx, Redis

## Getting Started

1. Create a `backend/.env` file (if needed).
2. Run `docker-compose up --build`
