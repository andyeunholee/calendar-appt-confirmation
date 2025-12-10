import streamlit as st
import datetime
import auth
import calendar_api
import gmail_api
import agent
import os

# Page Config
st.set_page_config(page_title="Calendar Confirmation Agent", page_icon="📅", layout="wide")

st.title("📅 Calendar Appointment Confirmation Agent")
st.markdown("Use AI to confirm your Google Calendar appointments.")

# --- Security Check ---
# Only require password if configured in secrets
if "APP_PASSWORD" in st.secrets:
    password = st.text_input("Enter App Password", type="password")
    if password != st.secrets["APP_PASSWORD"]:
        st.warning("Please enter the correct password to access the application.")
        st.stop()
# ----------------------

# Sidebar - Configuration
st.sidebar.header("Configuration")
# Try to load from secrets or env
default_api_key = ""
try:
    default_api_key = st.secrets["GEMINI_API_KEY"]
except:
    pass

gemini_api_key = st.sidebar.text_input("Gemini API Key", value=default_api_key, type="password", help="Get it from aistudio.google.com")

if not gemini_api_key:
    pass

if gemini_api_key:
    agent.configure_genai(gemini_api_key)
    st.sidebar.success("AI Agent Configured")
else:
    st.sidebar.warning("Please enter Gemini API Key to use AI features.")

# Authentication
creds = auth.get_credentials()

if not creds:
    st.info("Please log in to continue.")
    st.stop()

st.sidebar.success("Authenticated with Google")

# Initialize Services
try:
    calendar_service = calendar_api.get_calendar_service(creds)
    gmail_service = gmail_api.get_gmail_service(creds)
except Exception as e:
    st.error(f"Failed to connect to Google Services: {e}")
    st.stop()

# Main Interface
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Upcoming Appointments")
    
    # Date Filter
    selected_date = st.date_input("Filter by Date", value=datetime.date.today())
    
    if st.button("Refresh Events"):
        st.session_state.events = calendar_api.get_upcoming_events(calendar_service, start_date=selected_date)
        # Clear drafts when refreshing
        if 'student_draft' in st.session_state:
            del st.session_state.student_draft
        if 'teacher_draft' in st.session_state:
            del st.session_state.teacher_draft
        
    if 'events' not in st.session_state:
        st.session_state.events = calendar_api.get_upcoming_events(calendar_service, start_date=selected_date)
        
    events = st.session_state.events
    
    if not events:
        st.info("No upcoming events found.")
    else:
        # Create a selection list
        event_options = {f"{e['summary']} ({calendar_api.format_event_dt(e)})": e for e in events}
        selected_event_label = st.radio("Select an event:", list(event_options.keys()))
        selected_event = event_options[selected_event_label]
        
        # Store selected event in session state
        # Clear drafts if event changed
        if 'selected_event_id' not in st.session_state or st.session_state.selected_event_id != selected_event.get('id'):
            st.session_state.selected_event_id = selected_event.get('id')
            st.session_state.selected_event = selected_event
            # Clear old drafts when selecting a different event
            if 'student_draft' in st.session_state:
                del st.session_state.student_draft
            if 'teacher_draft' in st.session_state:
                del st.session_state.teacher_draft
        
        st.write("---")

with col2:
    st.subheader("2. Draft Confirmation Email")
    
    # Draft Email Section
    if 'selected_event' in st.session_state and st.session_state.selected_event:
        selected_event = st.session_state.selected_event
        teacher_name = st.text_input("Teacher Name", value="Teacher")
        student_name = st.text_input("Student Name", value="Student")
        
        # Get attendees emails if available
        attendees = selected_event.get('attendees', [])
        attendee_emails = [a['email'] for a in attendees]
        default_emails = ", ".join(attendee_emails)
        
        st.write("---")
        st.write("📧 **Email Settings**")
        student_email = st.text_input("Student Email (sep by comma)", value=default_emails)
        teacher_email = st.text_input("Teacher Email", value="")
        
        if st.button("Generate Email Drafts"):
            if not gemini_api_key:
                st.error("Please configure Gemini API Key first.")
            else:
                with st.spinner("Generating emails..."):
                    # Generate Student Email
                    try:
                        student_content = agent.generate_email_content(selected_event, teacher_name, student_name)
                        s_subject = "Appointment Confirmation"
                        s_body = student_content
                        if "Subject:" in student_content:
                            parts = student_content.split("Subject:", 1)
                            if len(parts) > 1:
                                subject_part = parts[1].split("\n", 1)
                                s_subject = subject_part[0].strip()
                                if len(subject_part) > 1:
                                    s_body = subject_part[1].strip()
                        
                        st.session_state.student_draft = {'subject': s_subject, 'body': s_body}
                    except Exception as e:
                        st.error(f"Failed to generate student email: {str(e)}")
                        st.session_state.student_draft = {'subject': 'Error', 'body': f'Error generating email: {str(e)}'}
                    
                    # Add delay to avoid rate limiting
                    import time
                    time.sleep(2)
                    
                    # Generate Teacher Email
                    try:
                        teacher_content = agent.generate_teacher_email_content(selected_event, teacher_name, student_name)
                        t_subject = "Appointment Reminder"
                        t_body = teacher_content
                        if "Subject:" in teacher_content:
                            parts = teacher_content.split("Subject:", 1)
                            if len(parts) > 1:
                                subject_part = parts[1].split("\n", 1)
                                t_subject = subject_part[0].strip()
                                if len(subject_part) > 1:
                                    t_body = subject_part[1].strip()

                        st.session_state.teacher_draft = {'subject': t_subject, 'body': t_body}
                    except Exception as e:
                        st.error(f"Failed to generate teacher email: {str(e)}")
                        st.session_state.teacher_draft = {'subject': 'Error', 'body': f'Error generating email: {str(e)}'}

    # Display Drafts
    tab1, tab2 = st.tabs(["Student Email", "Teacher Email"])
    
    with tab1:
        if 'student_draft' in st.session_state:
            st.write("#### Student Email Draft")
            s_subj_input = st.text_input("Student Subject", value=st.session_state.student_draft['subject'], key="s_subj")
            s_body_input = st.text_area("Student Body", value=st.session_state.student_draft['body'], height=300, key="s_body")
            
            if st.button("Send to Student 🚀", key="send_student"):
                if not student_email:
                    st.error("Please enter Student Email.")
                else:
                    user_profile = gmail_service.users().getProfile(userId='me').execute()
                    user_email = user_profile['emailAddress']
                    
                    msg = gmail_api.create_message(user_email, student_email, s_subj_input, s_body_input)
                    sent_msg = gmail_api.send_message(gmail_service, 'me', msg)
                    
                    if sent_msg:
                        st.success(f"Student email sent! ID: {sent_msg['id']}")
                    else:
                        st.error("Failed to send student email.")

    with tab2:
        if 'teacher_draft' in st.session_state:
            st.write("#### Teacher Email Draft")
            t_subj_input = st.text_input("Teacher Subject", value=st.session_state.teacher_draft['subject'], key="t_subj")
            t_body_input = st.text_area("Teacher Body", value=st.session_state.teacher_draft['body'], height=300, key="t_body")
            
            if st.button("Send to Teacher 🚀", key="send_teacher"):
                if not teacher_email:
                    st.error("Please enter Teacher Email.")
                else:
                    user_profile = gmail_service.users().getProfile(userId='me').execute()
                    user_email = user_profile['emailAddress']
                    
                    msg = gmail_api.create_message(user_email, teacher_email, t_subj_input, t_body_input)
                    sent_msg = gmail_api.send_message(gmail_service, 'me', msg)
                    
                    if sent_msg:
                        st.success(f"Teacher email sent! ID: {sent_msg['id']}")
                    else:
                        st.error("Failed to send teacher email.")
