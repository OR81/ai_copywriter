@echo off
REM Step 1: Navigate to Project Directory
@REM cd /d C:\path\to\your\project

REM Step 2: Create Virtual Environment (if not already created)
python -m venv .venv1

REM Step 3: Activate the Virtual Environment
call .venv1\Scripts\activate

REM Step 4: Install Dependencies (if any)
pip install -r ./env/requirements.txt

REM Step 5: Run the App.py File
python app.py

REM Step 6: Deactivate Virtual Environment (optional)
REM deactivate