# Google Calendar MCP Server

A FastMCP 2.0 server that provides Google Calendar integration through the Model Context Protocol (MCP).

## Features

- **List upcoming events**: Get upcoming calendar events with customizable limits
- **Get event details**: Retrieve detailed information about specific events
- **Create events**: Create new calendar events with attendees, location, and description
- **Search events**: Search for events by keyword
- **List calendars**: View all accessible calendars
- **Date range queries**: Get events within specific date ranges

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Google Calendar API**:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Google Calendar API
   - Configure OAuth consent screen
   - Create OAuth 2.0 Client ID credentials for a desktop application
   - Download the credentials and save as `credentials.json` in this directory

3. **First run authentication**:
   ```bash
   python calendar_mcp_server.py
   ```
   This will open a browser for OAuth authentication and save your tokens.

## Running the Server

### Local (stdio transport)
```bash
fastmcp run calendar_mcp_server.py:mcp
```

### HTTP transport
```bash
fastmcp run calendar_mcp_server.py:mcp --transport http --port 8000
```

## Available Tools

### `list_upcoming_events`
List upcoming events from Google Calendar.
- `max_results` (int, optional): Maximum number of events (default: 10)
- `calendar_id` (str, optional): Calendar ID (default: "primary")

### `get_event_details`
Get detailed information about a specific event.
- `event_id` (str): The ID of the event
- `calendar_id` (str, optional): Calendar ID (default: "primary")

### `create_event`
Create a new calendar event.
- `summary` (str): Event title
- `start_datetime` (str): Start time in ISO format
- `end_datetime` (str): End time in ISO format
- `description` (str, optional): Event description
- `location` (str, optional): Event location
- `attendees` (List[str], optional): List of attendee emails
- `calendar_id` (str, optional): Calendar ID (default: "primary")

### `search_events`
Search for events by keyword.
- `query` (str): Search query
- `max_results` (int, optional): Maximum results (default: 10)
- `calendar_id` (str, optional): Calendar ID (default: "primary")

### `list_calendars`
List all accessible calendars.

### `get_events_in_date_range`
Get events within a specific date range.
- `start_date` (str): Start date in ISO format
- `end_date` (str): End date in ISO format
- `calendar_id` (str, optional): Calendar ID (default: "primary")
- `max_results` (int, optional): Maximum results (default: 100)

## Authentication

The server uses OAuth 2.0 for authentication with Google Calendar API. On first API call, it will:
1. Open a browser for user authentication
2. Save access and refresh tokens to `token.json`
3. Automatically refresh tokens as needed

## Required Files

- `credentials.json`: OAuth 2.0 client credentials from Google Cloud Console
- `token.json`: Automatically generated after first authentication

## Client Usage Example

```python
import asyncio
from fastmcp import Client

async def main():
    client = Client("http://localhost:8000/mcp")
    
    async with client:
        # List upcoming events
        events = await client.call_tool("list_upcoming_events", {"max_results": 5})
        print("Upcoming events:", events)
        
        # Create a new event
        new_event = await client.call_tool("create_event", {
            "summary": "Team Meeting",
            "start_datetime": "2024-01-15T14:00:00-08:00",
            "end_datetime": "2024-01-15T15:00:00-08:00",
            "description": "Weekly team sync",
            "location": "Conference Room A"
        })
        print("Created event:", new_event)

asyncio.run(main())
```

## Permissions

The server requests the following Google Calendar scopes:
- `https://www.googleapis.com/auth/calendar.readonly`: Read calendar data
- `https://www.googleapis.com/auth/calendar`: Full calendar access (for creating events)

## Error Handling

All tools include error handling and will return error information in the response if API calls fail.