import time
import redis
from fastapi import HTTPException
from .config import settings

# Kết nối tới Redis chung
r = redis.from_url(settings.REDIS_URL, decode_responses=True)

def check_rate_limit(user_id: str):
    """
    Sử dụng thuật toán Sliding Window cho Rate Limiting với Redis.
    """
    key = f"rate_limit:{user_id}"
    now = time.time()
    limit = settings.RATE_LIMIT_PER_MINUTE
    window_size = 60

    try:
        # Xóa các request cũ hơn 60 giây
        r.zremrangebyscore(key, 0, now - window_size)
        
        # Đếm số request hiện tại trong window
        request_count = r.zcard(key)
        
        if request_count >= limit:
            raise HTTPException(status_code=429, detail="Too Many Requests")
            
        # Thêm request mới
        r.zadd(key, {str(now): now})
        r.expire(key, window_size)
    except redis.ConnectionError:
        # Trong trường hợp Redis sập, có thể cho phép qua hoặc chặn, tùy business logic.
        # Ở đây cho qua tạm để app không sụp hoàn toàn khi redis có vấn đề thoáng qua.
        pass
