echo "Activating virtual environment..."
.\.venv\Scripts\Activate.ps1
echo "Starting agent..."
python .\app_multifile.py
