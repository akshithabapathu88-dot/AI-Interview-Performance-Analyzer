@echo off
cd /d "%~dp0"
"%~dp0.venv\Scripts\python.exe" -m streamlit run "ai_interview_performance_analyzer\app.py"
