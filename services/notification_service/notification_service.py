import json
import os
from datetime import time
from typing import Dict
from pydantic import BaseModel

class NotificationSettings(BaseModel):
    chat_id: int
    notify_before_minutes: int = 15
    work_start_time: time = time(9, 0)
    work_end_time: time = time(18, 0)
    enabled: bool = True

class NotificationService:
    def __init__(self, storage_file="notification_settings.json"):
        self.storage_file = storage_file
        self.settings: Dict[int, NotificationSettings] = {}
        self._load_settings()

    def _load_settings(self):
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
                self.settings = {
                    int(chat_id): NotificationSettings(**settings)
                    for chat_id, settings in data.items()
                }

    def _save_settings(self):
        with open(self.storage_file, 'w') as f:
            json.dump({
                chat_id: settings.dict()
                for chat_id, settings in self.settings.items()
            }, f, indent=2)

    def get_settings(self, chat_id: int) -> NotificationSettings:
        return self.settings.get(chat_id, NotificationSettings(chat_id=chat_id))

    def update_settings(self, chat_id: int, **kwargs):
        settings = self.settings.get(chat_id, NotificationSettings(chat_id=chat_id))
        for key, value in kwargs.items():
            setattr(settings, key, value)
        self.settings[chat_id] = settings
        self._save_settings()
        return settings