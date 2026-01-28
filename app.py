import streamlit as st
import datetime
import auth
import calendar_api
import gmail_api
import agent
# import sms_code.bulk_send  <-- No longer needed directly
import os
import subprocess
import json
import tempfile
import sys

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

# Sidebar - Configuration (Hidden)
# Try to load from secrets or env
default_api_key = ""
try:
    default_api_key = st.secrets["GEMINI_API_KEY"]
except:
    pass

# Automatically use the key from secrets without showing input
gemini_api_key = default_api_key

if gemini_api_key:
    agent.configure_genai(gemini_api_key)
else:
    # Log to console instead of showing UI warning
    print("Warning: Gemini API Key not found in secrets.")

# Authentication
creds = auth.get_credentials()

if not creds:
    st.info("Please log in to continue.")
    st.stop()
    
# Authentication success message hidden

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
        st.write("📧 **Contact Settings**")
        student_email = st.text_input("Student Email (sep by comma)", value=default_emails)
        student_phone = st.text_input("Student Phone (sep by comma)", value="", placeholder="e.g. 404-123-4567, 678-999-8888")
        
        teacher_email = st.text_input("Teacher Email", value="")
        teacher_phone = st.text_input("Teacher Phone (sep by comma)", value="", placeholder="e.g. 404-555-0199")
        
        col_gen_sms, col_gen_email = st.columns(2)
        
        with col_gen_sms:
            if st.button("Generate Text Drafts 📱", use_container_width=True):
                if not gemini_api_key:
                    st.error("Please configure Gemini API Key first.")
                else:
                    with st.spinner("Generating SMS drafts..."):
                        # Generate Student SMS
                        try:
                            student_sms = agent.generate_sms_content(selected_event, teacher_name, student_name)
                            st.session_state.student_sms_draft = student_sms
                        except Exception as e:
                             st.session_state.student_sms_draft = f"Error: {str(e)}"
    
                        # Generate Teacher SMS
                        try:
                            teacher_sms = agent.generate_teacher_sms_content(selected_event, teacher_name, student_name)
                            st.session_state.teacher_sms_draft = teacher_sms
                        except Exception as e:
                             st.session_state.teacher_sms_draft = f"Error: {str(e)}"

        with col_gen_email:
            if st.button("Generate Email 📧", use_container_width=True):
                if not gemini_api_key:
                    st.error("Please configure Gemini API Key first.")
                else:
                    with st.spinner("Generating Email drafts..."):
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
                        time.sleep(1)
                        
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

    # Display Drafts - Reordered Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Student SMS 📱", "Teacher SMS 📱", "Student Email", "Teacher Email"])
    
    with tab1: # Student SMS (Formerly Tab 3)
        if 'student_sms_draft' in st.session_state:
            st.write("#### Student SMS Draft")
            s_sms_input = st.text_area("Message", value=st.session_state.student_sms_draft, height=100, key="s_sms")
            st.info(f"Recipients: {student_phone if student_phone else 'None'}")
            
            if st.button("Send SMS to Student 📱", key="send_sms_student"):
                if not student_phone:
                    st.error("Please enter Student Phone Number(s).")
                else:
                    phones = [p.strip() for p in student_phone.split(',') if p.strip()]
                    st.info(f"Sending to {len(phones)} recipients...")
                    
                    status_box = st.empty()
                    log_box = st.container()
                    
                    def progress_update(msg):
                        status_box.markdown(f"**Status:** {msg}")
                        with log_box:
                            st.text(msg)
                            
                    try:
                        config = {
                            'phone_numbers': phones, 
                            'message_text': s_sms_input,
                            'group_mode': True
                        }
                        
                        tf = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8')
                        json.dump(config, tf)
                        tf.close()
                        tmp_path = tf.name
                        
                        runner_script = os.path.join(os.getcwd(), "sms_code", "sms_runner.py")
                        cmd = [sys.executable, runner_script, tmp_path]
                        
                        process = subprocess.Popen(
                            cmd, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.STDOUT, 
                            text=True, 
                            encoding='utf-8',
                            bufsize=1
                        )
                        
                        while True:
                            line = process.stdout.readline()
                            if not line and process.poll() is not None:
                                break
                            if line:
                                line = line.strip()
                                if line.startswith("PROGRESS:"):
                                    msg = line.replace("PROGRESS:", "", 1)
                                    progress_update(msg)
                                elif line.startswith("ERROR_TRACE:"):
                                    rest = process.stdout.read()
                                    st.error(f"Error in SMS Process:\n{rest}")
                                else:
                                    print(f"[SMS_Runner]: {line}")
                        
                        try:
                            os.remove(tmp_path)
                        except:
                            pass
                            
                        if process.returncode == 0:
                            st.success("✅ SMS Sending Process Completed!")
                        else:
                            st.warning("Process finished with potential issues. Check logs above.")

                    except Exception as e:
                        import traceback
                        st.error(f"Failed to launch SMS process:\n{traceback.format_exc()}")

    with tab2: # Teacher SMS (Formerly Tab 4)
         if 'teacher_sms_draft' in st.session_state:
            st.write("#### Teacher SMS Draft")
            t_sms_input = st.text_area("Message", value=st.session_state.teacher_sms_draft, height=100, key="t_sms")
            st.info(f"Recipients: {teacher_phone if teacher_phone else 'None'}")

            if st.button("Send SMS to Teacher 📱", key="send_sms_teacher"):
                if not teacher_phone:
                    st.error("Please enter Teacher Phone Number(s).")
                else:
                    phones = [p.strip() for p in teacher_phone.split(',') if p.strip()]
                    st.info(f"Sending to {len(phones)} recipients...")
                    
                    status_box = st.empty()
                    log_box = st.container()
                    
                    def progress_update(msg):
                        status_box.markdown(f"**Status:** {msg}")
                        with log_box:
                            st.text(msg)
                            
                    try:
                        config = {
                            'phone_numbers': phones, 
                            'message_text': t_sms_input,
                            'group_mode': True
                        }
                        
                        tf = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8')
                        json.dump(config, tf)
                        tf.close()
                        tmp_path = tf.name
                        
                        runner_script = os.path.join(os.getcwd(), "sms_code", "sms_runner.py")
                        cmd = [sys.executable, runner_script, tmp_path]
                        
                        process = subprocess.Popen(
                            cmd, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.STDOUT, 
                            text=True, 
                            encoding='utf-8',
                            bufsize=1
                        )
                        
                        while True:
                            line = process.stdout.readline()
                            if not line and process.poll() is not None:
                                break
                            if line:
                                line = line.strip()
                                if line.startswith("PROGRESS:"):
                                    msg = line.replace("PROGRESS:", "", 1)
                                    progress_update(msg)
                                elif line.startswith("ERROR_TRACE:"):
                                    rest = process.stdout.read()
                                    st.error(f"Error in SMS Process:\n{rest}")
                                else:
                                    print(f"[SMS_Runner]: {line}")
                        
                        try:
                            os.remove(tmp_path)
                        except:
                            pass

                        if process.returncode == 0:
                            st.success("✅ SMS Sending Process Completed!")
                        else:
                            st.warning("Process finished with potential issues.")

                    except Exception as e:
                        import traceback
                        st.error(f"Failed to launch SMS process:\n{traceback.format_exc()}")

    with tab3: # Student Email (Formerly Tab 1)
        if 'student_draft' in st.session_state:
            st.write("#### Student Email Draft")
            s_subj_input = st.text_input("Student Subject", value=st.session_state.student_draft['subject'], key="s_subj")
            s_body_input = st.text_area("Student Body", value=st.session_state.student_draft['body'], height=300, key="s_body")
            
            if st.button("Send Email to Student 🚀", key="send_student"):
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

    with tab4: # Teacher Email (Formerly Tab 2)
        if 'teacher_draft' in st.session_state:
            st.write("#### Teacher Email Draft")
            t_subj_input = st.text_input("Teacher Subject", value=st.session_state.teacher_draft['subject'], key="t_subj")
            t_body_input = st.text_area("Teacher Body", value=st.session_state.teacher_draft['body'], height=300, key="t_body")
            
            if st.button("Send Email to Teacher 🚀", key="send_teacher"):
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
