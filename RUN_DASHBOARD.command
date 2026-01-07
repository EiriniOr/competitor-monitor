#!/bin/bash
# Double-click this file to launch the dashboard

cd "$(dirname "$0")"
source venv/bin/activate
streamlit run dashboard.py
