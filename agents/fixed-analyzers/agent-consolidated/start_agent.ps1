echo "Activating virtual environment..."
cd ..\..\..\.venv\Scripts\
.\Activate.ps1
echo "Starting agent..."
cd ..\..\agents\fixed-analyzers\agent-consolidated\
python .\app_multifile.py
