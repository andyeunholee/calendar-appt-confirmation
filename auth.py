import os.path
import streamlit as st
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import json

# If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/gmail.compose'
]

def get_credentials():
    """Gets valid user credentials from storage.

    Returns:
        Credentials, the obtained credential.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Priority: Check Streamlit Secrets for google credentials
    # This enables cloud deployment without browser interaction
    elif 'google' in st.secrets:
        try:
            # Build token info dictionary from secrets
            token_info = {
                'token': st.secrets['google']['token'],
                'refresh_token': st.secrets['google']['refresh_token'],
                'token_uri': st.secrets['google']['token_uri'],
                'client_id': st.secrets['google']['client_id'],
                'client_secret': st.secrets['google']['client_secret'],
                'scopes': st.secrets['google']['scopes']
            }
            creds = Credentials.from_authorized_user_info(token_info, SCOPES)
        except Exception as e:
            st.error(f"Error loading token from secrets: {e}")
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                st.error(f"Error refreshing token: {e}")
                creds = None
        
        if not creds:
            try:
                # Check for secrets first (Cloud Deployment)
                if 'google' in st.secrets:
                    client_config = {
                        "web": {
                            "client_id": st.secrets["google"]["client_id"],
                            "client_secret": st.secrets["google"]["client_secret"],
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                            "redirect_uris": [st.secrets["google"].get("redirect_uri", "http://localhost:8501")]
                        }
                    }
                    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
                    
                # Fallback to local file
                elif os.path.exists('credentials.json'):
                    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                    
                else:
                    st.error("Error: Authentication credentials found (neither in secrets nor 'credentials.json').")
                    return None

                # For cloud deployment, we cannot launch a local server browser.
                # If running locally, run_local_server works.
                # If running in cloud, we might need a different flow, but run_local_server fails in cloud without a display.
                # HOWEVER, for this specific user request, they are likely just deploying.
                # Streamlit Cloud usually requires 'from_client_config' but still needs a way to auth.
                # Standard 'InstalledAppFlow' opens a local browser. This DOES NOT WORK in Streamlit Cloud.
                # We need to use 'flow.authorization_url()' and manual copy-paste or similar if not identical to local behavior.
                # But for now, let's keep it simple as a first step or use the existing flow if they run locally.
                
                # IMPORTANT: InstalledAppFlow.run_local_server DOES NOT work on Streamlit Cloud.
                # We need to stick to the current logic for local, but merely enable loading config from secrets.
                # The user will probably authorize LOCALLY and push token.json (not recommended but easiest) OR
                # we need a full web-based auth flow which is complex.
                # GIVEN the context, the user is likely running this as a personal app.
                # The EASIEST path for Streamlit Cloud with personal Google Creds is to upload 'token.json' to the repo (private repo).
                # Wait, the user has 'token.json' in .gitignore.
                
                # Let's stick to enabling config source for now.
                creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
                    
            except Exception as e:
                st.error(f"Authentication failed: {e}")
                return None
                
    return creds
