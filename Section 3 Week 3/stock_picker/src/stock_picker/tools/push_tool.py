from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field


class PushNotificationInput(BaseModel):
    """Input schema for PushNotificationTool."""
    title: str = Field(..., description="Title of the push notification")
    message: str = Field(..., description="The notification message content")


class PushNotificationTool(BaseTool):
    name: str = "Push Notification Tool"
    description: str = (
        "Sends a push notification to alert the user about important stock picks or investment recommendations. "
        "Use this tool to notify the user about the best stock pick and the reasoning behind the selection."
    )
    args_schema: Type[BaseModel] = PushNotificationInput

    def _run(self, title: str, message: str) -> str:
        notification_output = f"""
========================================
PUSH NOTIFICATION SENT
========================================
Title: {title}
----------------------------------------
Message: {message}
========================================
"""
        print(notification_output)
        return f"Push notification sent successfully with title: '{title}'"