import datetime
import os.path
from typing import List, Dict, Any, Optional
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from fastmcp import FastMCP

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar"
]

mcp = FastMCP("Google Calendar MCP Server")

def get_calendar_service():
    """Get authenticated Google Calendar service."""
    creds = None
    
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    
    return build("calendar", "v3", credentials=creds)

@mcp.tool
def list_upcoming_events(max_results: int = 10, calendar_id: str = "primary") -> List[Dict[str, Any]]:
    """
    List upcoming events from Google Calendar.
    
    Args:
        max_results: Maximum number of events to return (default: 10)
        calendar_id: Calendar ID to query (default: 'primary')
    
    Returns:
        List of event dictionaries with summary, start time, and details
    """
    try:
        service = get_calendar_service()
        
        now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        events_result = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
        
        formatted_events = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            formatted_events.append({
                "id": event.get("id"),
                "summary": event.get("summary", "No title"),
                "start": start,
                "end": event["end"].get("dateTime", event["end"].get("date")),
                "description": event.get("description", ""),
                "location": event.get("location", ""),
                "attendees": [attendee.get("email") for attendee in event.get("attendees", [])],
                "html_link": event.get("htmlLink", ""),
            })
        
        return formatted_events
        
    except HttpError as error:
        return [{"error": f"An error occurred: {error}"}]

@mcp.tool
def get_event_details(event_id: str, calendar_id: str = "primary") -> Dict[str, Any]:
    """
    Get detailed information about a specific calendar event.
    
    Args:
        event_id: The ID of the event to retrieve
        calendar_id: Calendar ID containing the event (default: 'primary')
    
    Returns:
        Dictionary containing detailed event information
    """
    try:
        service = get_calendar_service()
        
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
        
        return {
            "id": event.get("id"),
            "summary": event.get("summary", "No title"),
            "description": event.get("description", ""),
            "location": event.get("location", ""),
            "start": event["start"].get("dateTime", event["start"].get("date")),
            "end": event["end"].get("dateTime", event["end"].get("date")),
            "created": event.get("created"),
            "updated": event.get("updated"),
            "creator": event.get("creator", {}).get("email", ""),
            "organizer": event.get("organizer", {}).get("email", ""),
            "attendees": [
                {
                    "email": attendee.get("email"),
                    "displayName": attendee.get("displayName", ""),
                    "responseStatus": attendee.get("responseStatus", "")
                }
                for attendee in event.get("attendees", [])
            ],
            "html_link": event.get("htmlLink", ""),
            "recurring_event_id": event.get("recurringEventId"),
            "status": event.get("status", ""),
        }
        
    except HttpError as error:
        return {"error": f"An error occurred: {error}"}

@mcp.tool
def create_event(
    summary: str,
    start_datetime: str,
    end_datetime: str,
    description: str = "",
    location: str = "",
    attendees: Optional[List[str]] = None,
    calendar_id: str = "primary"
) -> Dict[str, Any]:
    """
    Create a new calendar event.
    
    Args:
        summary: Event title
        start_datetime: Start time in ISO format (e.g., '2023-12-25T10:00:00-08:00')
        end_datetime: End time in ISO format
        description: Event description (optional)
        location: Event location (optional)
        attendees: List of attendee email addresses (optional)
        calendar_id: Calendar ID to create event in (default: 'primary')
    
    Returns:
        Dictionary containing created event information
    """
    try:
        service = get_calendar_service()
        
        event_body = {
            "summary": summary,
            "description": description,
            "location": location,
            "start": {"dateTime": start_datetime},
            "end": {"dateTime": end_datetime},
        }
        
        if attendees:
            event_body["attendees"] = [{"email": email} for email in attendees]
        
        event = service.events().insert(calendarId=calendar_id, body=event_body).execute()
        
        return {
            "id": event.get("id"),
            "summary": event.get("summary"),
            "start": event["start"].get("dateTime"),
            "end": event["end"].get("dateTime"),
            "html_link": event.get("htmlLink"),
            "status": "created"
        }
        
    except HttpError as error:
        return {"error": f"An error occurred: {error}"}

@mcp.tool
def search_events(
    query: str,
    max_results: int = 10,
    calendar_id: str = "primary"
) -> List[Dict[str, Any]]:
    """
    Search for events in Google Calendar.
    
    Args:
        query: Search query string
        max_results: Maximum number of events to return (default: 10)
        calendar_id: Calendar ID to search (default: 'primary')
    
    Returns:
        List of matching event dictionaries
    """
    try:
        service = get_calendar_service()
        
        events_result = (
            service.events()
            .list(
                calendarId=calendar_id,
                q=query,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
        
        formatted_events = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            formatted_events.append({
                "id": event.get("id"),
                "summary": event.get("summary", "No title"),
                "start": start,
                "end": event["end"].get("dateTime", event["end"].get("date")),
                "description": event.get("description", ""),
                "location": event.get("location", ""),
                "html_link": event.get("htmlLink", ""),
            })
        
        return formatted_events
        
    except HttpError as error:
        return [{"error": f"An error occurred: {error}"}]

@mcp.tool
def list_calendars() -> List[Dict[str, Any]]:
    """
    List all accessible calendars.
    
    Returns:
        List of calendar dictionaries with id, summary, and access role
    """
    try:
        service = get_calendar_service()
        
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get("items", [])
        
        formatted_calendars = []
        for calendar in calendars:
            formatted_calendars.append({
                "id": calendar.get("id"),
                "summary": calendar.get("summary", ""),
                "description": calendar.get("description", ""),
                "primary": calendar.get("primary", False),
                "access_role": calendar.get("accessRole", ""),
                "background_color": calendar.get("backgroundColor", ""),
                "foreground_color": calendar.get("foregroundColor", ""),
            })
        
        return formatted_calendars
        
    except HttpError as error:
        return [{"error": f"An error occurred: {error}"}]

@mcp.tool
def get_events_in_date_range(
    start_date: str,
    end_date: str,
    calendar_id: str = "primary",
    max_results: int = 100
) -> List[Dict[str, Any]]:
    """
    Get events within a specific date range.
    
    Args:
        start_date: Start date in ISO format (e.g., '2023-12-01T00:00:00Z')
        end_date: End date in ISO format
        calendar_id: Calendar ID to query (default: 'primary')
        max_results: Maximum number of events to return (default: 100)
    
    Returns:
        List of event dictionaries within the date range
    """
    try:
        service = get_calendar_service()
        
        events_result = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=start_date,
                timeMax=end_date,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
        
        formatted_events = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            formatted_events.append({
                "id": event.get("id"),
                "summary": event.get("summary", "No title"),
                "start": start,
                "end": event["end"].get("dateTime", event["end"].get("date")),
                "description": event.get("description", ""),
                "location": event.get("location", ""),
                "attendees": [attendee.get("email") for attendee in event.get("attendees", [])],
                "html_link": event.get("htmlLink", ""),
            })
        
        return formatted_events
        
    except HttpError as error:
        return [{"error": f"An error occurred: {error}"}]

if __name__ == "__main__":
    mcp.run()