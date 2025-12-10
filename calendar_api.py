from googleapiclient.discovery import build
import datetime

def get_calendar_service(creds):
    """Builds and returns the Calendar service."""
    return build('calendar', 'v3', credentials=creds)

def get_upcoming_events(service, start_date=None, max_results=10):
    """
    Gets upcoming events.
    If start_date is provided, fetches events for that specific day (local time).
    """
    if start_date:
        # Create datetime range for the selected day in US/Eastern timezone
        # This ensures consistency between Local (EST) and Cloud (UTC) execution
        import datetime as dt
        import pytz
        
        # Define target timezone
        tz = pytz.timezone('America/New_York')
        
        # Create start/end of day in Eastern Time
        start_dt_et = tz.localize(dt.datetime.combine(start_date, dt.time.min))
        end_dt_et = tz.localize(dt.datetime.combine(start_date, dt.time.max))
        
        # Convert to UTC for API query
        timeMin = start_dt_et.astimezone(pytz.UTC).isoformat()
        timeMax = end_dt_et.astimezone(pytz.UTC).isoformat()
        
        print(f"Getting events for {start_date} (Timezone: America/New_York)")
        events_result = service.events().list(calendarId='primary', 
                                            timeMin=timeMin,
                                            timeMax=timeMax,
                                            singleEvents=True,
                                            orderBy='startTime').execute()
    else:
        # Default behavior: 10 upcoming events from now
        now = datetime.datetime.utcnow().isoformat() + 'Z' 
        print(f"Getting the upcoming {max_results} events")
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                            maxResults=max_results, singleEvents=True,
                                            orderBy='startTime').execute()
                                            
    events = events_result.get('items', [])
    return events

def format_event_dt(event):
    """Formats event date/time for display."""
    start = event['start'].get('dateTime', event['start'].get('date'))
    end = event['end'].get('dateTime', event['end'].get('date'))
    
    try:
        # Check if it's a full day event (YYYY-MM-DD pattern)
        if 'T' not in start:
            return f"{start} (All Day)"
            
        # Parse datetime strings
        dt_start = datetime.datetime.fromisoformat(start)
        dt_end = datetime.datetime.fromisoformat(end)
        
        # Format as HH:MM - HH:MM
        # Using %I:%M%p for 12-hour format (e.g. 03:30PM)
        start_str = dt_start.strftime('%I:%M%p')
        end_str = dt_end.strftime('%I:%M%p')
        
        return f"{start_str} - {end_str}"
    except:
        return start
