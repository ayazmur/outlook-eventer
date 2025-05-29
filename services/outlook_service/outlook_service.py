import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import msal
import requests
from dotenv import load_dotenv
from interfaces.ioutlook import ICalendarService

load_dotenv()

class OutlookCalendarService(ICalendarService):
    def __init__(self):
        self.client_id = os.getenv('OUTLOOK_CLIENT_ID')
        self.client_secret = os.getenv('OUTLOOK_CLIENT_SECRET')
        self.tenant_id = os.getenv('OUTLOOK_TENANT_ID')
        self.user_id = os.getenv('OUTLOOK_USER_ID')
        self.scopes = ['https://graph.microsoft.com/.default']
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.graph_url = 'https://graph.microsoft.com/v1.0'
        self.token = self._get_token()

    def _get_token(self):
        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=self.authority,
            client_credential=self.client_secret
        )
        result = app.acquire_token_for_client(scopes=self.scopes)
        return result['access_token']

    def _make_request(self, method, endpoint, **kwargs):
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        url = f"{self.graph_url}{endpoint}"
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()

    def get_meetings(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        endpoint = f"/users/{self.user_id}/calendarview"
        params = {
            'startDateTime': start_date.isoformat(),
            'endDateTime': end_date.isoformat(),
            '$select': 'subject,start,end,location,id',
            '$orderby': 'start/dateTime'
        }
        data = self._make_request('GET', endpoint, params=params)
        return data.get('value', [])

    def create_meeting(self, meeting_data: Dict) -> Dict:
        endpoint = f"/users/{self.user_id}/events"
        payload = {
            "subject": meeting_data["subject"],
            "start": meeting_data["start"],
            "end": meeting_data["end"],
            "location": {
                "displayName": meeting_data.get("location", "")
            }
        }
        return self._make_request('POST', endpoint, json=payload)

    def update_meeting(self, meeting_id: str, updates: Dict) -> Dict:
        endpoint = f"/users/{self.user_id}/events/{meeting_id}"
        return self._make_request('PATCH', endpoint, json=updates)

    def delete_meeting(self, meeting_id: str) -> bool:
        endpoint = f"/users/{self.user_id}/events/{meeting_id}"
        self._make_request('DELETE', endpoint)
        return True

    def get_meeting(self, meeting_id: str) -> Optional[Dict]:
        endpoint = f"/users/{self.user_id}/events/{meeting_id}"
        return self._make_request('GET', endpoint)

    def setup_notifications(self, notification_url: str):
        """Настраивает вебхук для уведомлений о событиях"""
        endpoint = f"/users/{self.user_id}/subscriptions"
        payload = {
            "changeType": "created,updated,deleted",
            "notificationUrl": notification_url,
            "resource": f"/users/{self.user_id}/events",
            "expirationDateTime": (datetime.utcnow() + timedelta(days=2)).isoformat(),
            "clientState": "secretClientState"
        }
        return self._make_request('POST', endpoint, json=payload)