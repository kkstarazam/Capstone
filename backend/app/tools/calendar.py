"""Google Calendar integration tool.

Provides read/write access to Google Calendar for scheduling
weather-aware events and reminders.
"""
from datetime import datetime, timedelta
from typing import Optional, List
import json
import os

# Google API imports (will be used when OAuth is configured)
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False


# OAuth scopes for Google Calendar
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Token storage path
TOKEN_PATH = "token.json"
CREDENTIALS_PATH = "credentials.json"


def _get_calendar_service(user_credentials: Optional[dict] = None):
    """
    Get authenticated Google Calendar service.

    Args:
        user_credentials: Optional user-specific OAuth credentials

    Returns:
        Google Calendar API service object.
    """
    if not GOOGLE_API_AVAILABLE:
        raise RuntimeError(
            "Google API libraries not installed. "
            "Install with: pip install google-auth google-auth-oauthlib google-api-python-client"
        )

    creds = None

    # Try to load existing credentials
    if user_credentials:
        creds = Credentials.from_authorized_user_info(user_credentials, SCOPES)
    elif os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    # Refresh or get new credentials if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif os.path.exists(CREDENTIALS_PATH):
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

            # Save credentials for future use
            with open(TOKEN_PATH, "w") as token:
                token.write(creds.to_json())
        else:
            raise RuntimeError(
                "No valid credentials found. Please set up Google Calendar OAuth. "
                "See: https://developers.google.com/calendar/api/quickstart/python"
            )

    return build("calendar", "v3", credentials=creds)


async def get_calendar_events(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    max_results: int = 10,
    calendar_id: str = "primary",
    user_credentials: Optional[dict] = None
) -> List[dict]:
    """
    Get calendar events within a date range.

    Args:
        start_date: Start of date range (defaults to now)
        end_date: End of date range (defaults to 7 days from now)
        max_results: Maximum number of events to return
        calendar_id: Calendar ID (default is primary calendar)
        user_credentials: Optional user-specific OAuth credentials

    Returns:
        List of calendar events with details.
    """
    service = _get_calendar_service(user_credentials)

    if start_date is None:
        start_date = datetime.utcnow()
    if end_date is None:
        end_date = start_date + timedelta(days=7)

    # Format times for Google Calendar API
    time_min = start_date.isoformat() + "Z"
    time_max = end_date.isoformat() + "Z"

    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=time_min,
        timeMax=time_max,
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = events_result.get("items", [])

    formatted_events = []
    for event in events:
        start = event.get("start", {})
        end = event.get("end", {})

        formatted_events.append({
            "id": event.get("id"),
            "summary": event.get("summary", "Untitled Event"),
            "description": event.get("description"),
            "location": event.get("location"),
            "start": start.get("dateTime") or start.get("date"),
            "end": end.get("dateTime") or end.get("date"),
            "all_day": "date" in start,
            "status": event.get("status"),
            "html_link": event.get("htmlLink"),
        })

    return formatted_events


async def create_calendar_event(
    summary: str,
    start_time: datetime,
    end_time: Optional[datetime] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    reminders: Optional[List[int]] = None,
    calendar_id: str = "primary",
    user_credentials: Optional[dict] = None
) -> dict:
    """
    Create a new calendar event.

    Args:
        summary: Event title
        start_time: Event start time
        end_time: Event end time (defaults to 1 hour after start)
        description: Event description
        location: Event location
        reminders: List of reminder times in minutes before event
        calendar_id: Calendar ID (default is primary calendar)
        user_credentials: Optional user-specific OAuth credentials

    Returns:
        Created event details.
    """
    service = _get_calendar_service(user_credentials)

    if end_time is None:
        end_time = start_time + timedelta(hours=1)

    event = {
        "summary": summary,
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": "UTC",
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": "UTC",
        },
    }

    if description:
        event["description"] = description
    if location:
        event["location"] = location

    if reminders:
        event["reminders"] = {
            "useDefault": False,
            "overrides": [
                {"method": "popup", "minutes": mins} for mins in reminders
            ],
        }

    created_event = service.events().insert(
        calendarId=calendar_id,
        body=event
    ).execute()

    return {
        "id": created_event.get("id"),
        "summary": created_event.get("summary"),
        "start": created_event.get("start", {}).get("dateTime"),
        "end": created_event.get("end", {}).get("dateTime"),
        "html_link": created_event.get("htmlLink"),
        "status": "created",
    }


async def create_weather_reminder(
    title: str,
    event_time: datetime,
    weather_note: str,
    reminder_minutes: int = 60,
    calendar_id: str = "primary",
    user_credentials: Optional[dict] = None
) -> dict:
    """
    Create a weather-related reminder event.

    Args:
        title: Reminder title (e.g., "Bring umbrella")
        event_time: Time for the reminder
        weather_note: Weather-related note/reason
        reminder_minutes: Minutes before to send reminder
        calendar_id: Calendar ID
        user_credentials: Optional user-specific OAuth credentials

    Returns:
        Created reminder event details.
    """
    return await create_calendar_event(
        summary=f"Weather Reminder: {title}",
        start_time=event_time,
        end_time=event_time + timedelta(minutes=15),
        description=f"Weather Advisory: {weather_note}",
        reminders=[reminder_minutes],
        calendar_id=calendar_id,
        user_credentials=user_credentials
    )


async def check_calendar_availability() -> bool:
    """
    Check if Google Calendar API is available and configured.

    Returns:
        True if calendar integration is available.
    """
    if not GOOGLE_API_AVAILABLE:
        return False

    try:
        _get_calendar_service()
        return True
    except Exception:
        return False
