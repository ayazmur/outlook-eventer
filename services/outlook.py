import json
from typing import List, Dict
from pathlib import Path

class MockOutlookService:
    def __init__(self, db_path: str = "outlook_events.json"):
        self.db_path = Path(db_path)
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        if not self.db_path.exists():
            self.db_path.write_text(json.dumps({"events": []}))

    def add_event(self, event: Dict) -> None:
        data = json.loads(self.db_path.read_text())
        data["events"].append(event)
        self.db_path.write_text(json.dumps(data))

    def get_events(self) -> List[Dict]:
        data = json.loads(self.db_path.read_text())
        return data["events"]