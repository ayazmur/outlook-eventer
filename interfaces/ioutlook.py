from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Optional


class ICalendarService(ABC):
    @abstractmethod
    def get_meetings(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        pass

    @abstractmethod
    def create_meeting(self, meeting_data: Dict) -> Dict:
        pass

    @abstractmethod
    def update_meeting(self, meeting_id: str, updates: Dict) -> Dict:
        pass

    @abstractmethod
    def delete_meeting(self, meeting_id: str) -> bool:
        pass

    @abstractmethod
    def get_meeting(self, meeting_id: str) -> Optional[Dict]:
        pass