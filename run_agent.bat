@echo off
cd /d "g:\My Drive\calendar-appt-confirmation"
streamlit run app.py
if errorlevel 1 pause
