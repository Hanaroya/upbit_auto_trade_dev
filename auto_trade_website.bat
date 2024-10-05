@echo off
cd /d C:\Users\ASUS\Documents\GitHub\upbit_auto_trade_dev
python initialize.py
start python -m waitress --port=5000 main_flask_server:app
timeout /t 5
start http://localhost:5000