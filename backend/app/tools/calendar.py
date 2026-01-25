"""Google Calendar integration tool.

Provides read/write access to Google Calendar for scheduling
weather-aware events and reminders.
"""
from datetime import datetime, timedelta
from typing import Optional, List
import json
import os
import asyncio
from functools import partial
import logging

# Google API imports (will be used when OAuth is configured)
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False

logger = logging.getLogger(__name__)

# OAuth scopes for Google Calendar
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Per-user token storage directory (more secure than single shared file)
TOKENS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "tokens")
CREDENTIALS_PATH = "credentials.json"


def _get_user_token_path(user_id: str) -> str:
    """Get the token file path for a specific user."""
    # Sanitize user_id to prevent directory traversal
    safe_user_id = "".join(c for c in user_id if c.isalnum() or c in "-_")
    if not safe_user_id:
        safe_user_id = "default"
    return os.path.join(TOKENS_DIR, f"token_{safe_user_id}.json")


def _ensure_tokens_dir():
    """Ensure the tokens directory exists with proper permissions."""
    if not os.path.exists(TOKENS_DIR):
        os.makedirs(TOKENS_DIR, mode=0o700, exist_ok=True)


def _get_calendar_service_sync(user_id: Optional[str] = None, user_credentials: Optional[dict] = None):
    """
    Get authenticated Google Calendar service (synchronous).

    Args:
        user_id: User ID for per-user token storage
        user_credentials: Optional user-specific OAuth credentials dict

    Returns:
        Google Calendar API service object.
    """
    if not GOOGLE_API_AVAILABLE:
        raise RuntimeError(
            "Google API libraries not installed. "
            "Install with: pip install google-auth google-auth-oauthlib google-api-python-client"
        )

    creds = None
    token_path = _get_user_token_path(user_id or "default")

    # Try to load existing credentials
    if user_credentials:
        creds = Credentials.from_authorized_user_info(user_credentials, SCOPES)
    elif os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # Refresh or get new credentials if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save refreshed credentials
            _ensure_tokens_dir()
            with open(token_path, "w") as token:
                os.chmod(token_path, 0o600)  # Restrict file permissions
                token.write(creds.to_json())
        elif os.path.exists(CREDENTIALS_PATH):
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

            # Save credentials for future use with restricted permissions
            _ensure_tokens_dir()
            with open(token_path, "w") as token:
                token.write(creds.to_json())
            os.chmod(token_path, 0o600)  # Restrict file permissions
        else:
            raise RuntimeError(
                "No valid credentials found. Please set up Google Calendar OAuth. "
                "See: https://developers.google.com/calendar/api/quickstart/python"
            )

    return build("calendar", "v3", credentials=creds)


async def _get_calendar_service(user_id: Optional[str] = None, user_credentials: Optional[dict] = None):
    """
    Get authenticated Google Calendar service (async wrapper).

    Runs the synchronous OAuth flow in a thread pool to avoid blocking.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        partial(_get_calendar_service_sync, user_id, user_credentials)
    )


async def get_calendar_events(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    max_results: int = 10,
    calendar_id: str = "primary",
    user_id: Optional[str] = None,
    user_credentials: Optional[dict] = None
) -> List[dict]:
    """
    Get calendar events within a date range.

    Args:
        start_date: Start of date range (defaults to now)
        end_date: End of date range (defaults to 7 days from now)
        max_results: Maximum number of events to return
        calendar_id: Calendar ID (default is primary calendar)
        user_id: User ID for per-user credential storage
        user_credentials: Optional user-specific OAuth credentials

    Returns:
        List of calendar events with details.
    """
    service = await _get_calendar_service(user_id, user_credentials)

    if start_date is None:
        start_date = datetime.utcnow()
    if end_date is None:
        end_date = start_date + timedelta(days=7)

    # Format times for Google Calendar API
    time_min = start_date.isoformat() + "Z"
    time_max = end_date.isoformat() + "Z"

    # Run blocking API call in thread pool
    loop = asyncio.get_event_loop()
    events_result = await loop.run_in_executor(
        None,
        lambda: service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
    )

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
    user_id: Optional[str] = None,
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
        user_id: User ID for per-user credential storage
        user_credentials: Optional user-specific OAuth credentials

    Returns:
        Created event details.
    """
    service = await _get_calendar_service(user_id, user_credentials)

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

    # Run blocking API call in thread pool
    loop = asyncio.get_event_loop()
    created_event = await loop.run_in_executor(
        None,
        lambda: service.events().insert(
            calendarId=calendar_id,
            body=event
        ).execute()
    )

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
    user_id: Optional[str] = None,
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
        user_id: User ID for per-user credential storage
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
        user_id=user_id,
        user_credentials=user_credentials
    )


async def check_calendar_availability(user_id: Optional[str] = None) -> bool:
    """
    Check if Google Calendar API is available and configured.

    Args:
        user_id: Optional user ID to check specific user's credentials

    Returns:
        True if calendar integration is available.
    """
    if not GOOGLE_API_AVAILABLE:
        return False

    try:
        await _get_calendar_service(user_id)
        return True
    except Exception as e:
        logger.debug(f"Calendar not available: {e}")
        return False


async def delete_user_credentials(user_id: str) -> bool:
    """
    Delete stored credentials for a user.

    Args:
        user_id: User ID whose credentials to delete

    Returns:
        True if credentials were deleted, False if not found.
    """
    token_path = _get_user_token_path(user_id)
    if os.path.exists(token_path):
        os.remove(token_path)
        logger.info(f"Deleted credentials for user {user_id}")
        return True
    return False
