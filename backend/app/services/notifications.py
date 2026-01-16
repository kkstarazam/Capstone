"""Push notification service using Firebase Cloud Messaging.

This service handles sending push notifications to mobile devices
for weather alerts and proactive suggestions.
"""
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
import httpx

# Firebase Admin SDK (optional, for production)
try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False


class NotificationService:
    """Service for sending push notifications."""

    def __init__(self, firebase_credentials_path: Optional[str] = None):
        """
        Initialize the notification service.

        Args:
            firebase_credentials_path: Path to Firebase service account JSON
        """
        self._initialized = False
        self._device_tokens: Dict[str, str] = {}  # user_id -> device_token

        if FIREBASE_AVAILABLE and firebase_credentials_path:
            try:
                cred = credentials.Certificate(firebase_credentials_path)
                firebase_admin.initialize_app(cred)
                self._initialized = True
            except Exception as e:
                print(f"Firebase initialization failed: {e}")

    @property
    def is_available(self) -> bool:
        """Check if notification service is available."""
        return self._initialized

    def register_device(self, user_id: str, device_token: str) -> bool:
        """
        Register a device token for a user.

        Args:
            user_id: User identifier
            device_token: FCM device token

        Returns:
            True if registration successful.
        """
        self._device_tokens[user_id] = device_token
        return True

    def unregister_device(self, user_id: str) -> bool:
        """
        Unregister a user's device.

        Args:
            user_id: User identifier

        Returns:
            True if unregistration successful.
        """
        if user_id in self._device_tokens:
            del self._device_tokens[user_id]
            return True
        return False

    def get_device_token(self, user_id: str) -> Optional[str]:
        """Get the device token for a user."""
        return self._device_tokens.get(user_id)

    async def send_notification(
        self,
        user_id: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        image_url: Optional[str] = None,
    ) -> bool:
        """
        Send a push notification to a user.

        Args:
            user_id: User identifier
            title: Notification title
            body: Notification body text
            data: Optional data payload
            image_url: Optional image URL

        Returns:
            True if notification sent successfully.
        """
        device_token = self._device_tokens.get(user_id)
        if not device_token:
            print(f"No device token for user {user_id}")
            return False

        if not self._initialized:
            # Log notification for testing/development
            print(f"[NOTIFICATION] To: {user_id}")
            print(f"  Title: {title}")
            print(f"  Body: {body}")
            if data:
                print(f"  Data: {data}")
            return True

        try:
            notification = messaging.Notification(
                title=title,
                body=body,
                image=image_url,
            )

            message = messaging.Message(
                notification=notification,
                data={k: str(v) for k, v in (data or {}).items()},
                token=device_token,
            )

            response = messaging.send(message)
            print(f"Notification sent: {response}")
            return True
        except Exception as e:
            print(f"Failed to send notification: {e}")
            return False

    async def send_weather_alert(
        self,
        user_id: str,
        alert_type: str,
        location: str,
        message: str,
        severity: str = "info",
    ) -> bool:
        """
        Send a weather alert notification.

        Args:
            user_id: User identifier
            alert_type: Type of alert (rain, storm, temperature, etc.)
            location: Location name
            message: Alert message
            severity: Alert severity (info, warning, severe)

        Returns:
            True if notification sent successfully.
        """
        severity_icons = {
            "info": "ℹ️",
            "warning": "⚠️",
            "severe": "🚨",
        }
        icon = severity_icons.get(severity, "🌤️")

        title = f"{icon} Weather Alert - {location}"

        return await self.send_notification(
            user_id=user_id,
            title=title,
            body=message,
            data={
                "type": "weather_alert",
                "alert_type": alert_type,
                "location": location,
                "severity": severity,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    async def send_schedule_reminder(
        self,
        user_id: str,
        event_name: str,
        weather_info: str,
        recommendation: str,
    ) -> bool:
        """
        Send a schedule-based weather reminder.

        Args:
            user_id: User identifier
            event_name: Name of the calendar event
            weather_info: Weather conditions
            recommendation: What to do/bring

        Returns:
            True if notification sent successfully.
        """
        title = f"📅 {event_name} - Weather Update"
        body = f"{weather_info}. {recommendation}"

        return await self.send_notification(
            user_id=user_id,
            title=title,
            body=body,
            data={
                "type": "schedule_reminder",
                "event": event_name,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    async def send_to_multiple(
        self,
        user_ids: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, bool]:
        """
        Send notification to multiple users.

        Args:
            user_ids: List of user identifiers
            title: Notification title
            body: Notification body
            data: Optional data payload

        Returns:
            Dictionary of user_id -> success status.
        """
        results = {}
        for user_id in user_ids:
            results[user_id] = await self.send_notification(
                user_id=user_id,
                title=title,
                body=body,
                data=data,
            )
        return results


# Global notification service instance
_notification_service: Optional[NotificationService] = None


def get_notification_service() -> NotificationService:
    """Get or create the global notification service."""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service
