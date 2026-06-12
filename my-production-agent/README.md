# Production AI Agent

This is a production-ready AI agent built with FastAPI, Redis, and Docker.

## Features

- **Stateless Design**: Conversation history is stored in Redis.
- **Graceful Shutdown**: Handles `SIGTERM` signals properly.
- **Rate Limiting**: 10 requests per minute per user.
- **Cost Guard**: $10 budget per user per month.
- **Authentication**: API Key required for endpoints.
- **Containerization**: Multi-stage Dockerfile for small image size.
- **Health Checks**: `/health` and `/ready` endpoints.

## Local Development

1. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Start Redis (if not running via Docker):
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

3. Copy the environment file and run:
```bash
cp .env.example .env
uvicorn app.main:app --reload
```

## Running with Docker Compose

```bash
docker compose up --build
```
This will start 1 agent, Redis, and Nginx. To scale the agent:
```bash
docker compose up --scale agent=3
```

## Deployment

Refer to [DEPLOYMENT.md](DEPLOYMENT.md) for public URLs and test commands.
You can deploy this project to [Railway](https://railway.app/) using the provided `railway.json` or to [Render](https://render.com/) using `render.yaml`.
