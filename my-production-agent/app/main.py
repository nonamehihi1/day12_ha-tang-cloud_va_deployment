import json
import logging
import signal
import sys
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import redis
import uvicorn

from .config import settings
from .auth import verify_api_key
from .rate_limiter import check_rate_limit
from .cost_guard import check_budget
import sys
import os

# Xử lý import utils do thư mục utils nằm ngoài app/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.mock_llm import generate_response

# Setup structured logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger("agent")

def log_event(event_name: str, **kwargs):
    log_data = {"event": event_name}
    log_data.update(kwargs)
    logger.info(json.dumps(log_data))

app = FastAPI(title="Production AI Agent")
r = redis.from_url(settings.REDIS_URL, decode_responses=True)

is_shutting_down = False

def shutdown_handler(signum, frame):
    global is_shutting_down
    logger.info("Received SIGTERM. Initiating graceful shutdown...")
    is_shutting_down = True
    # Đóng kết nối Redis hoặc db connection tại đây nếu cần
    # r.close() # Không dùng được với phiên bản redis-py thấp, nhưng uvicorn sẽ tự drain requests
    sys.exit(0)

# Bắt tín hiệu SIGTERM
signal.signal(signal.SIGTERM, shutdown_handler)


class AskRequest(BaseModel):
    question: str

@app.get("/health")
def health():
    """Liveness probe"""
    return {"status": "ok"}

@app.get("/ready")
def ready():
    """Readiness probe"""
    if is_shutting_down:
        return JSONResponse(status_code=503, content={"status": "shutting down"})
    try:
        r.ping()
        return {"status": "ready"}
    except redis.ConnectionError:
        return JSONResponse(status_code=503, content={"status": "redis not ready"})

@app.post("/ask")
def ask(
    req: AskRequest,
    user_id: str = Depends(verify_api_key)
):
    if is_shutting_down:
        raise HTTPException(status_code=503, detail="Service is shutting down")
        
    # Check rate limit (10 req/min)
    check_rate_limit(user_id)
    
    # Check cost guard (budget $10/tháng, 0.01$/req)
    check_budget(user_id, estimated_cost=0.01)
    
    try:
        # Lấy lịch sử chat từ Redis (Stateless design)
        history_key = f"history:{user_id}"
        history = r.lrange(history_key, 0, -1)
        
        # Gọi Mock LLM
        answer = generate_response(req.question)
        
        # Lưu vào Redis
        r.rpush(history_key, f"Q: {req.question}")
        r.rpush(history_key, f"A: {answer}")
        
        # Giữ lại 20 tin nhắn gần nhất
        r.ltrim(history_key, -20, -1)
        # Set expire 24h
        r.expire(history_key, 24 * 3600)
        
        log_event("request_processed", user_id=user_id, question=req.question)
        return {
            "answer": answer,
            "user_id": user_id,
            "history_length": len(history) // 2
        }
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, log_level=settings.LOG_LEVEL.lower())
