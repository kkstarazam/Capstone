"""Push notification service using Firebase Cloud Messaging.

This service handles sending push notifications to mobile devices
for weather alerts and proactive suggestions.
"""
import json
from typing import Optional, List, Dict, Any, NamedTuple
from datetime import datetime, timedelta
import httpx
import logging

logger = logging.getLogger(__name__)

# Firebase Admin SDK (optional, for production)
try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False


class DeviceToken(NamedTuple):
    """Device token with expiration."""
    token: str
    registered_at: datetime
    last_used: datetime


# Token TTL - tokens expire after 30 days of inactivity
TOKEN_TTL_DAYS = 30
# Maximum number of tokens to store (to prevent unbounded growth)
MAX_TOKENS = 10000


class NotificationService:
    """Service for sending push notifications."""

    def __init__(self, firebase_credentials_path: Optional[str] = None):
        """
        Initialize the notification service.

        Args:
            firebase_credentials_path: Path to Firebase service account JSON
        """
        self._initialized = False
        self._device_tokens: Dict[str, DeviceToken] = {}  # user_id -> DeviceToken

        if FIREBASE_AVAILABLE and firebase_credentials_path:
            try:
                cred = credentials.Certificate(firebase_credentials_path)
                firebase_admin.initialize_app(cred)
                self._initialized = True
            except Exception as e:
                logger.warning(f"Firebase initialization failed: {e}")

    @property
    def is_available(self) -> bool:
        """Check if notification service is available."""
        return self._initialized

    def _cleanup_expired_tokens(self) -> int:
        """Remove expired tokens. Returns number of tokens removed."""
        now = datetime.utcnow()
        expired_users = [
            user_id for user_id, token_info in self._device_tokens.items()
            if (now - token_info.last_used).days > TOKEN_TTL_DAYS
        ]
        for user_id in expired_users:
            del self._device_tokens[user_id]
        if expired_users:
            logger.info(f"Cleaned up {len(expired_users)} expired device tokens")
        return len(expired_users)

    def register_device(self, user_id: str, device_token: str) -> bool:
        """
        Register a device token for a user.

        Args:
            user_id: User identifier
            device_token: FCM device token

        Returns:
            True if registration successful.
        """
        # Cleanup old tokens periodically (every 100 registrations or when near limit)
        if len(self._device_tokens) >= MAX_TOKENS - 100:
            self._cleanup_expired_tokens()

        # Enforce maximum token limit
        if len(self._device_tokens) >= MAX_TOKENS and user_id not in self._device_tokens:
            logger.warning(f"Max device tokens ({MAX_TOKENS}) reached, rejecting registration")
            return False

        now = datetime.utcnow()
        self._device_tokens[user_id] = DeviceToken(
            token=device_token,
            registered_at=now,
            last_used=now
        )
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
        """Get the device token for a user (updates last_used time)."""
        token_info = self._device_tokens.get(user_id)
        if token_info:
            # Update last_used time
            self._device_tokens[user_id] = DeviceToken(
                token=token_info.token,
                registered_at=token_info.registered_at,
                last_used=datetime.utcnow()
            )
            return token_info.token
        return None

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
        device_token = self.get_device_token(user_id)
        if not device_token:
            logger.debug(f"No device token for user {user_id}")
            return False

        if not self._initialized:
            # Log notification for testing/development
            logger.info(f"[NOTIFICATION] To: {user_id} | Title: {title} | Body: {body}")
            if data:
                logger.debug(f"  Data: {data}")
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
            logger.info(f"Notification sent to {user_id}: {response}")
            return True
        except Exception as e:
            logger.error(f"Failed to send notification to {user_id}: {e}")
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
