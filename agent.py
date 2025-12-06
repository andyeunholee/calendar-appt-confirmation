import google.generativeai as genai
import os
import streamlit as st

def configure_genai(api_key):
    """Configures the Gemini API."""
    genai.configure(api_key=api_key)

def generate_email_content(event_details, teacher_name="Teacher", student_name="Student"):
    """
    Generates a confirmation email for the STUDENT using Gemini.
    """
    
    # Extract event info
    summary = event_details.get('summary', 'Appointment')
    
    # Time Parsing Logic
    start_raw = event_details['start'].get('dateTime', event_details['start'].get('date'))
    end_raw = event_details['end'].get('dateTime', event_details['end'].get('date'))
    description = event_details.get('description', '')

    formatted_time_str = start_raw 
    formatted_date_str = start_raw 

    try:
        import datetime
        if 'T' in start_raw:
            dt_start = datetime.datetime.fromisoformat(start_raw)
            dt_end = datetime.datetime.fromisoformat(end_raw)
            
            # Format: 3:30pm - 5:00pm
            start_str = dt_start.strftime('%I:%M%p').lower()
            end_str = dt_end.strftime('%I:%M%p').lower()
            if start_str.startswith('0'): start_str = start_str[1:]
            if end_str.startswith('0'): end_str = end_str[1:]
            
            formatted_time_str = f"{start_str} - {end_str}"
            formatted_date_str = dt_start.strftime('%B, %d, %Y')
        else:
            formatted_time_str = "All Day"
            formatted_date_str = start_raw
    except:
        pass

    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = f"""
    You are an automated email assistant for Elite Prep Suwanee.
    Please generate a confirmation email for a tutoring appointment using the EXACT format below.
    Do not add any extra text or conversational filler.
    
    Event Details:
    - Subject/Topic: {summary}
    - Date: {formatted_date_str}
    - Time Range: {formatted_time_str}
    - Description/Type: {description}
    - Teacher Name: {teacher_name}
    - Student Name: {student_name}
    
    Format Requirements:
    - Date format: 'Month, Day, Year' (e.g. December, 06, 2025)
    - Time format: 'h:mmam - h:mmpm' (e.g. 3:30pm - 5:00pm)
    - [Type] and [Subject] should be extracted from the event details.
    
    Output Format:
    Subject: REMINDER: {student_name}'s tutoring with {teacher_name} Teacher - [Date] at [Time]
    
    Dear {student_name},
    
    This is a reminder that {student_name} has a tutoring session with {teacher_name} Teacher, [Date] at [Time]
    
    Date: [Date]
    Time: [Time]
    Type: [Type]
    Subject: [Subject]
    
    If you cannot attend the tutoring session, please reply with **[N]**, and if you can attend, please reply with **[Y]** as soon as possible.
    
    If you have any questions or need further details, please feel free to contact us anytime.
    
    Best regards,
    
    Andy Lee / Elite Prep Suwanee
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating email: {e}"

def generate_teacher_email_content(event_details, teacher_name="Teacher", student_name="Student"):
    """
    Generates a confirmation email for the TEACHER using Gemini.
    """
    
    # Extract event info
    summary = event_details.get('summary', 'Appointment')
    
    # Time Parsing Logic
    start_raw = event_details['start'].get('dateTime', event_details['start'].get('date'))
    end_raw = event_details['end'].get('dateTime', event_details['end'].get('date'))
    description = event_details.get('description', '')

    formatted_time_str = start_raw 
    formatted_date_str = start_raw 

    try:
        import datetime
        if 'T' in start_raw:
            dt_start = datetime.datetime.fromisoformat(start_raw)
            dt_end = datetime.datetime.fromisoformat(end_raw)
            
            # Format: 3:30pm - 5:00pm
            start_str = dt_start.strftime('%I:%M%p').lower()
            end_str = dt_end.strftime('%I:%M%p').lower()
            if start_str.startswith('0'): start_str = start_str[1:]
            if end_str.startswith('0'): end_str = end_str[1:]
            
            formatted_time_str = f"{start_str} - {end_str}"
            # Teacher format: MM. dd, yyyy
            formatted_date_str = dt_start.strftime('%m. %d, %Y')
        else:
            formatted_time_str = "All Day"
            formatted_date_str = start_raw
    except:
        pass
    
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = f"""
    You are an automated email assistant for Elite Prep Suwanee.
    Please generate a confirmation email for a tutoring appointment using the EXACT format below.
    Do not add any extra text or conversational filler.
    
    Event Details:
    - Subject/Topic: {summary}
    - Date: {formatted_date_str}
    - Time Range: {formatted_time_str}
    - Description/Type: {description}
    - Teacher Name: {teacher_name}
    - Student Name: {student_name}
    
    Format Requirements:
    - Date format: 'MM. dd, yyyy' (e.g. 12. 06, 2025)
    - Time format: 'h:mmam - h:mmpm' (e.g. 3:30pm - 5:00pm)
    - [Type] and [Subject] should be extracted from the event details.
    
    Output Format:
    Subject: REMINDER: {teacher_name} teacher has tutoring with {student_name} - [Date] at [Time]
    
    Dear {teacher_name} teacher,
    
    This is a reminder that {teacher_name} teacher has a tutoring session with {student_name}, [Date] at [Time]
    
    Date: [Date]
    Time: [Time]
    Type: [Type]
    Subject: [Subject]
    
    If you have any questions or need further details, please feel free to contact us.
    
    Best regards,
    
    Andy Lee / Elite Prep Suwanee
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating email: {e}"
