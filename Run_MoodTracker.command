#!/bin/bash

cd "$(dirname "$0")"

if ! python3 -c "import streamlit" >/dev/null 2>&1

then
    echo "Installing dependencies..."
    python3 -m pip install -r requirements.txt

fi

echo "Launching Mood Tracker..."
python3 -m streamlit run app.py