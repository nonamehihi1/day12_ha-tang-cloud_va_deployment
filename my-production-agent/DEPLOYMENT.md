# Deployment Information

## Public URL
https://<your-agent-url>.railway.app

## Platform
Railway / Render / Cloud Run

## Test Commands

### Health Check
```bash
curl https://<your-agent-url>.railway.app/health
# Expected: {"status": "ok"}
```

### Readiness Check
```bash
curl https://<your-agent-url>.railway.app/ready
# Expected: {"status": "ready"}
```

### API Test (with authentication)
```bash
curl -X POST https://<your-agent-url>.railway.app/ask \
  -H "X-API-Key: secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'
```

## Environment Variables Set
- PORT
- REDIS_URL
- AGENT_API_KEY
- LOG_LEVEL
- RATE_LIMIT_PER_MINUTE
- MONTHLY_BUDGET_USD

## Screenshots
> Thay thế các file ảnh trong thư mục `screenshots/` bằng ảnh của bạn.

- [Deployment dashboard](image.png)
- [Service running](running.png)
- [Test results](test.png)
