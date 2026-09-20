"""Notification utilities for sending webhooks and alerts."""
import requests
from src.logging_config import logger


def send_webhook_notification(message: str, webhook_url: str) -> None:
    """
    Send a notification to a webhook.
    
    Args:
        message: Message to send
        webhook_url: Webhook URL
    """
    try:
        response = requests.post(
            webhook_url,
            json={"text": message},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        logger.info(f"Webhook notification sent successfully")
    except Exception as e:
        logger.error(f"Failed to send webhook notification: {e}")
