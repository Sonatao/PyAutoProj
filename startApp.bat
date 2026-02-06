@echo off
set STREAMLIT_CONFIG_DIR=%~dp0.streamlit
"%~dp0env\python.exe" -m streamlit run "%~dp0app.py" --server.port 8509