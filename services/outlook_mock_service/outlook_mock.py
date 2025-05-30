from interfaces.ioutlook import ICalendarService
from datetime import datetime, timedelta
import os
import random
import json
from typing import List, Dict, Optional

from uuid import uuid4


class MockOutlookService(ICalendarService):
    def __init__(self, data_file: str = 'outlook_data.json'):
        self.data_file = data_file
        self._ensure_data_file_exists()

    def _ensure_data_file_exists(self):
        if not os.path.exists(self.data_file):
            self._generate_mock_data()

    def _generate_mock_data(self):
        """Генерация моковых данных для руководителя айти отдела:D"""
        now = datetime.now()
        meetings = []

        # Common meeting types for an IT manager
        meeting_types = [
            "Team Standup", "Sprint Planning", "Architecture Review",
            "Client Demo", "Backlog Grooming", "One-on-One",
            "Leadership Sync", "Retrospective", "Incident Review"
        ]

        participants = [
            "dev1@company.com", "dev2@company.com", "qa@company.com",
            "product@company.com", "design@company.com", "cto@company.com",
            "hr@company.com", "client@client.com"
        ]

        for i in range(30):  # Генерация митов для 30 дней
            meeting_date = now + timedelta(days=i)

            # Не каждый день есть встречи
            if random.random() < 0.7:  # 70% шанс иметь встречу в день
                num_meetings = random.randint(1, 4)
                for _ in range(num_meetings):
                    start_hour = random.randint(9, 17)  # Рабочие часы
                    duration = random.choice([30, 45, 60])  # Средняя продолжительность встреч

                    meeting = {
                        "id": str(uuid4()),
                        "subject": f"{random.choice(meeting_types)} - {random.choice(['Project A', 'Project B', 'Team'])}",
                        "start": {
                            "dateTime": (meeting_date.replace(hour=start_hour, minute=0, second=0)).isoformat(),
                            "timeZone": "UTC"
                        },
                        "end": {
                            "dateTime": (meeting_date.replace(hour=start_hour, minute=0, second=0) + timedelta(
                                minutes=duration)).isoformat(),
                            "timeZone": "UTC"
                        },
                        "location": random.choice(["Teams", "Zoom", "Conference Room 1", "Conference Room 2"]),
                        "organizer": "it_manager@company.com",
                        "attendees": random.sample(participants, random.randint(2, 5)),
                        "body": {
                            "content": f"Discussion about {random.choice(['new features', 'technical debt', 'sprint goals', 'performance issues'])}",
                            "contentType": "text"
                        },
                        "isCancelled": False
                    }
                    meetings.append(meeting)

        data = {
            "meetings": meetings,
            "last_updated": now.isoformat()
        }

        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _load_data(self) -> Dict:
        with open(self.data_file, 'r') as f:
            return json.load(f)

    def _save_data(self, data: Dict):
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)

    def get_meetings(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        data = self._load_data()
        meetings = data['meetings']

        filtered_meetings = []
        for meeting in meetings:
            meeting_start = datetime.fromisoformat(meeting['start']['dateTime'])
            if start_date <= meeting_start <= end_date:
                filtered_meetings.append(meeting)

        return filtered_meetings

    def create_meeting(self, meeting_data: Dict) -> Dict:
        data = self._load_data()

        # Generate required fields if not provided
        if 'id' not in meeting_data:
            meeting_data['id'] = str(uuid4())

        if 'organizer' not in meeting_data:
            meeting_data['organizer'] = "it_manager@company.com"

        if 'isCancelled' not in meeting_data:
            meeting_data['isCancelled'] = False

        data['meetings'].append(meeting_data)
        data['last_updated'] = datetime.now().isoformat()

        self._save_data(data)
        return meeting_data

    def update_meeting(self, meeting_id: str, updates: Dict) -> Dict:
        data = self._load_data()
        updated_meeting = None

        for meeting in data['meetings']:
            if meeting['id'] == meeting_id:
                meeting.update(updates)
                updated_meeting = meeting
                break

        if updated_meeting:
            data['last_updated'] = datetime.now().isoformat()
            self._save_data(data)
            return updated_meeting
        else:
            raise ValueError(f"Meeting with ID {meeting_id} not found")

    def delete_meeting(self, meeting_id: str) -> bool:
        data = self._load_data()
        initial_length = len(data['meetings'])

        data['meetings'] = [m for m in data['meetings'] if m['id'] != meeting_id]

        if len(data['meetings']) < initial_length:
            data['last_updated'] = datetime.now().isoformat()
            self._save_data(data)
            return True
        return False

    def get_meeting(self, meeting_id: str) -> Optional[Dict]:
        data = self._load_data()
        for meeting in data['meetings']:
            if meeting['id'] == meeting_id:
                return meeting
        return None


# Example usage
if __name__ == "__main__":
    outlook_service = MockOutlookService()

    # Get meetings for the next week
    now = datetime.now()
    next_week = now + timedelta(days=7)
    meetings = outlook_service.get_meetings(now, next_week)
    print(f"Found {len(meetings)} meetings in the next week:")
    for meeting in meetings:
        print(f"- {meeting['subject']} at {meeting['start']['dateTime']}")

    # Create a new meeting
    new_meeting = {
        "subject": "Important Project Discussion",
        "start": {
            "dateTime": (now + timedelta(days=1, hours=14)).isoformat(),
            "timeZone": "UTC"
        },
        "end": {
            "dateTime": (now + timedelta(days=1, hours=15)).isoformat(),
            "timeZone": "UTC"
        },
        "location": "Teams",
        "attendees": ["dev1@company.com", "product@company.com"],
        "body": {
            "content": "We need to discuss the upcoming project deadline",
            "contentType": "text"
        }
    }

    created = outlook_service.create_meeting(new_meeting)
    print(f"\nCreated new meeting with ID: {created['id']}")

    # Update the meeting
    updates = {
        "subject": "URGENT: Important Project Discussion",
        "attendees": ["dev1@company.com", "product@company.com", "cto@company.com"]
    }
    updated = outlook_service.update_meeting(created['id'], updates)
    print(f"\nUpdated meeting subject to: {updated['subject']}")

    # Get single meeting
    single = outlook_service.get_meeting(created['id'])
    print(f"\nSingle meeting details: {single}")

    # Delete the meeting
    deleted = outlook_service.delete_meeting(created['id'])
    print(f"\nMeeting deleted: {deleted}")
