from pydantic import BaseModel
from typing import Optional
from datetime import time

class NotificationSettings(BaseModel):
    chat_id: int
    notify_before_minutes: int = 15
    work_start_time: time = time(9, 0)  # 09:00
    work_end_time: time = time(18, 0)   # 18:00
    enabled: bool = True