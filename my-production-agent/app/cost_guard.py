import redis
from datetime import datetime
from fastapi import HTTPException
from .config import settings

# Kết nối Redis
r = redis.from_url(settings.REDIS_URL, decode_responses=True)

def check_budget(user_id: str, estimated_cost: float = 0.01):
    """
    Giới hạn chi phí dựa trên tháng hiện tại. Mỗi request mặc định tốn 0.01$ (giả lập).
    """
    month_key = datetime.now().strftime("%Y-%m")
    key = f"budget:{user_id}:{month_key}"
    
    try:
        current_spending = float(r.get(key) or 0)
        
        if current_spending + estimated_cost > settings.MONTHLY_BUDGET_USD:
            raise HTTPException(status_code=402, detail="Payment Required: Budget Exceeded")
            
        # Tăng spending lên
        r.incrbyfloat(key, estimated_cost)
        # Set expire cho key sau ~32 ngày
        r.expire(key, 32 * 24 * 3600)
    except redis.ConnectionError:
        pass
