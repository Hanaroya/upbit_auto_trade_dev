@echo off
cd /d C:\Users\ASUS\Documents\GitHub\upbit-auto-trade
start python main_flask_server.py
timeout /t 5
start http://localhost:5000