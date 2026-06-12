from fastapi import Header, HTTPException
from typing import Optional
from .config import settings

def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API Key header missing")
    if x_api_key != settings.AGENT_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    # Trả về một dummy user_id vì hệ thống đơn giản dựa trên API Key duy nhất. 
    # Có thể lấy user_id từ JWT nếu hệ thống phức tạp hơn.
    return "user_" + x_api_key[:5] 
