@echo off
echo Checking Python installation...
python --version > nul 2>&1
if errorlevel 1 (
    echo Python is not installed! Please install Python 3.8 or higher.
    pause
    exit
)

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Installing requirements...
    call venv\Scripts\activate
    pip install -r requirements.txt
)

if not exist "token.txt" (
    echo Creating token.txt file...
    echo your_token_here> token.txt
    echo Please edit token.txt and add your Discord bot token!
    notepad token.txt
    pause
    exit
)

echo Starting Quiz Bot...
call venv\Scripts\activate
python quiz-bot.py
pause